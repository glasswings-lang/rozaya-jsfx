#!/usr/bin/env python3
"""Migrate REAPER projects across the sweeping filters' honest-Hz change.

WHY THIS EXISTS
---------------
Resonant Sweeping Filter and Sweep Dwell Filter used to share a fixed two-pole
Kellett core -- two one-pole sections with a resonance feedback path -- whose
cutoff coefficient was `cut = 2*fc/srate`.  That is the standard musicdsp idiom
and it is approximately right at low frequencies, but measured, the real -3 dB
corner landed at 0.21x to 0.77x the number on the slider, DEPENDING ON THE
RESONANCE SETTING:

    set 500 Hz, Resonance 0.0  ->  real corner  103 Hz
    set 500 Hz, Resonance 0.7  ->  real corner  232 Hz
    set 500 Hz, Resonance 1.0  ->  real corner  247 Hz

So "Frequency Hz" was never Hz, and Resonance was quietly a second frequency
control.  Both plugins now use a Butterworth cascade whose corner sits exactly
on the number at any slope.

That fixes the label and would move the sound, so this script moves the numbers
to compensate: for each instance it works out where the OLD filter actually
cornered, given that instance's own Frequency and Resonance, and writes that
frequency into the slider.  The value on screen changes a lot.  What you hear
does not.

WHAT IT CANNOT PRESERVE
-----------------------
The corner, exactly.  Not the whole curve: the old filter has a droopier
passband and a softer knee than Butterworth, so material near the corner will
sit slightly differently.  It is a character shift, not a tuning shift.

Also, if a project SWEEPS Resonance (Drift or Speed Ramp aimed at it), the old
filter's corner moved with it and the new one's will not -- one fixed
correction cannot stand in for that.  The script warns when it sees this.  At
the time of writing no project in the library did it.

USAGE
-----
    python tools/sweepfilter_migrate_hz.py PROJECT.RPP [MORE.RPP ...]
    python tools/sweepfilter_migrate_hz.py PROJECT.RPP --dry-run

In-place edits write a `.pre-hz-migrate-bak` copy first and refuse to clobber an
existing one.  Close the project in REAPER before migrating in place.
"""

import argparse
import cmath
import math
import os
import shutil
import sys

SR = 48000.0   # the correction is very nearly sample-rate independent

# plugin -> (freq-low slider, freq-high slider, resonance slider,
#            speed-ramp target slider, drift target slider, resonance target index,
#            defaults for low/high/resonance when the slot holds '-')
PLUGINS = {
    "full-feature-sweeping-filter.jsfx": (1, 2, 12, 29, 34, 4, (500.0, 5000.0, 0.7)),
    "sweep-dwell-filter.jsfx":           (1, 2,  9, 26, 30, 4, (500.0, 5000.0, 0.7)),
}
BACKUP_SUFFIX = ".pre-hz-migrate-bak"


def old_response_db(fc, res, f):
    """The retired Kellett core's magnitude response, analytically.

        n3 += cut*(x - n3 + fb*(n3 - n4))
        n4 += cut*(n3 - n4)

    n4 uses the freshly updated n3, so the state update is sequential; folding
    that in gives the 2x2 system below.  Evaluated on the unit circle rather
    than simulated, so a whole library migrates in a second.
    """
    a = fc * 2 / SR
    if a >= 1:
        return -999.0
    fb = res + res / (1 - a)
    # s1' = A11*s1 + A12*s2 + B1*x ; s2' = a*s1' + (1-a)*s2
    A11, A12, B1 = (1 - a + a * fb), (-a * fb), a
    A21, A22, B2 = a * A11, a * A12 + (1 - a), a * B1
    z = cmath.exp(2j * math.pi * f / SR)
    # (zI - A)^-1 B, then take the second state as the output
    det = (z - A11) * (z - A22) - A12 * A21
    if det == 0:
        return -999.0
    s2 = (A21 * B1 + (z - A11) * B2) / det
    m = abs(s2)
    return 20 * math.log10(m) if m > 0 else -999.0


def old_corner(fc, res):
    """Where the retired core's -3 dB point actually was.

    A forward log scan for the FIRST crossing, not a bisection.  At high
    Resonance that response is not monotonic, and bisection then returns
    whichever crossing its bracket happened to straddle -- the two answers
    differed by half an octave at Resonance 1.0, which would have been silently
    wrong in exactly the projects that lean on the filter hardest.  The first
    downward crossing is the corner as heard.
    """
    ref = old_response_db(fc, res, 0.01)
    lo, hi = fc * 0.005, min(fc * 6, SR * 0.49)
    steps = 4000
    ratio = (hi / lo) ** (1.0 / steps)
    f, prev_f, prev_d = lo, lo, old_response_db(fc, res, lo)
    for _ in range(steps):
        f *= ratio
        d = old_response_db(fc, res, f)
        if d <= ref - 3:
            # linear interpolation in log-f between the bracketing samples
            span = d - prev_d
            t = 0.0 if span == 0 else ((ref - 3) - prev_d) / span
            return math.exp(math.log(prev_f) + t * (math.log(f) - math.log(prev_f)))
        prev_f, prev_d = f, d
    return hi


def fmt(v):
    return str(int(round(v)))


def rewrite(line, spec):
    lo_s, hi_s, res_s, sr_t, dr_t, res_idx, defaults = spec
    eol = "\r" if line.endswith("\r") else ""
    line = line[: len(line) - len(eol)]
    indent = line[: len(line) - len(line.lstrip())]
    tokens = line.strip().split()

    # Index by TOKEN position, never by "the values with the '-' padding
    # stripped out".  REAPER writes '-' for a slot it has nothing to say about,
    # and those slots can appear BETWEEN real values, not only as trailing
    # padding -- one project in the library does exactly that.  Filtering them
    # first silently shifts every slider after the gap, which would have
    # rewritten the wrong controls.
    def get(slot, default):
        if slot > len(tokens):
            return default, False
        t = tokens[slot - 1]
        if t == "-":
            return default, False
        try:
            return float(t), True
        except ValueError:
            return default, False

    d_lo, d_hi, d_res = defaults
    lo, lo_set = get(lo_s, d_lo)
    hi, hi_set = get(hi_s, d_hi)
    res, _ = get(res_s, d_res)

    if not lo_set and not hi_set:
        return line + eol, "no change needed (both frequencies at default)", False

    # Target sliders only exist on layouts that have the Drift/Ramp sweep; an
    # older project simply has no such slot, and that is not an error.
    swept = False
    for slot in (sr_t, dr_t):
        v, present = get(slot, -1)
        if present and int(v) == res_idx:
            swept = True

    new_lo, new_hi = old_corner(lo, res), old_corner(hi, res)
    if lo_set:
        tokens[lo_s - 1] = fmt(new_lo)
    if hi_set:
        tokens[hi_s - 1] = fmt(new_hi)
    status = ("migrated (res %.2f: low %s->%s Hz, high %s->%s Hz)"
              % (res, fmt(lo), fmt(new_lo), fmt(hi), fmt(new_hi)))
    return indent + " ".join(tokens) + eol, status, swept


def migrate(text):
    lines = text.split("\n")
    report, warned = [], False
    for i, line in enumerate(lines):
        if "<JS" not in line or "<JS_SER" in line:
            continue
        spec = next((v for k, v in PLUGINS.items() if k in line), None)
        if spec is None or i + 1 >= len(lines):
            continue
        lines[i + 1], status, swept = rewrite(lines[i + 1], spec)
        if swept:
            status += "  ** WARNING: this instance sweeps Resonance; the old " \
                      "corner moved with it and one fixed correction cannot " \
                      "reproduce that **"
            warned = True
        report.append(status)
    return "\n".join(lines), report, warned


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    problems = 0
    for path in args.projects:
        with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            text = fh.read()
        new_text, report, warned = migrate(text)
        print("\n%s" % path)
        if not report:
            print("   no sweeping-filter instances")
            continue
        for n, status in enumerate(report, 1):
            print("   instance %d: %s" % (n, status))
            if status.startswith("SKIPPED"):
                problems += 1
        if warned:
            problems += 1
        if args.dry_run or new_text == text:
            continue
        backup = path + BACKUP_SUFFIX
        if os.path.exists(backup):
            print("   REFUSING: %s already exists" % os.path.basename(backup))
            problems += 1
            continue
        shutil.copy2(path, backup)
        with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            fh.write(new_text)
        print("   backup: %s" % os.path.basename(backup))
        print("   written: %s" % path)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
