#!/usr/bin/env python3
"""Repair projects saved before the 2026-07-02 mid-list `Speed ramp target` insert.

WHAT WENT WRONG
---------------
On 2026-07-02 the per-target Speed Ramp work added a `Speed ramp target` selector
to six plugins -- and added it in the MIDDLE of each slider list, not at the end.
REAPER restores plugin values by POSITION, so every project saved before that day
now has each stored value read as the control one place DOWN the list:

    ... Speed ramp by       -> Speed ramp target
        Speed ramp duration -> Speed ramp by
        Speed ramp engage   -> Speed ramp duration
        Speed ramp delay    -> Speed ramp engage
        Drift target        -> Speed ramp start delay
        Drift up            -> Drift target
        Drift down          -> Drift up
        Drift period (8)    -> Drift down          <-- the damage
        Drift shape  (0)    -> Drift period        <-- and this

The last two are what bite. `Drift period` defaults to 8, so that 8 lands on
`Drift down`; the drift gate is `(up > 0 || down > 0)`, which goes **TRUE on a
plugin nobody ever configured drift on**. And `Drift shape`'s 0 lands on
`Drift period`, which is then `max(per, 1)` = ONE cycle. The result is a rate
swung downward by up to 8 units every single cycle -- audibly, every note a
different length, with the fault landing at the passage from one note to the
next.

Found 2026-09-02 from a single out-of-range value: `Drift period = 0` against a
declared minimum of 1. Range-check your migrations.

WHICH PLUGINS
-------------
Six plugins took the insert on the same day. `melody_phase` is handled by its own
already-applied script (`melody_migrate_drift_shift.py`) and is listed here only
so a re-run is provably a no-op. `rhythm-track`, `shepard-scale` and
`shepard-tone` took the same insert but appear in ZERO projects, so they are
listed for completeness and cost nothing to scan.

THE GATE
--------
Each of those commits also introduced (or bumped) the `@serialize` magic, so an
instance whose blob is missing or whose leading float32 is below the plugin's
current magic was saved on the old layout. Two further conditions make the whole
thing idempotent and safe to re-run over a folder:

  * nothing is stored at or above the insert point   -> nothing to move
  * something is stored ABOVE the old maximum slider -> already migrated

The blob is not touched. Its banks are at their @init defaults, and REAPER
rewrites it in the current format on the next save from inside REAPER.
"""

import argparse
import base64
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line, SliderLineError  # noqa: E402

# plugin basename -> (insert position, old max slider, current @serialize magic)
# The seeded value for the new selector is always 0 -- the old Speed Ramp was
# single-target and always acted on target 0 (Rate Value), so 0 reproduces the
# OLD behaviour rather than the plugin's default.
PLUGINS = {
    "Full_Feature_Tremolo.jsfx":         (24, 32, 2100000),
    "full-feature-sweeping-filter.jsfx": (29, 37, 2100000),
    "rhythm-track.jsfx":                 (18, 25, 2000000),
    "shepard-scale.jsfx":                (53, 60, 2000000),
    "shepard-tone.jsfx":                 (65, 72, 2000000),
    "melody_phase.jsfx":                 (67, 75, 2100000),
}

JS_RE = re.compile(r'^\s*<JS\s+(\S+)')


def read_blob_magic(lines, values_index):
    j = values_index
    while j < len(lines) and lines[j].strip() != ">":
        j += 1
    j += 1
    if j >= len(lines) or not lines[j].strip().startswith("<JS_SER"):
        return None
    b64, k = "", j + 1
    while k < len(lines) and not lines[k].strip().startswith(">"):
        b64 += lines[k].strip()
        k += 1
    try:
        raw = base64.b64decode(b64)
        return struct.unpack("<f", raw[:4])[0] if len(raw) >= 4 else None
    except Exception:
        return None


def instances(lines):
    out = []
    for i, line in enumerate(lines):
        m = JS_RE.match(line)
        if not m:
            continue
        base = os.path.basename(m.group(1).strip('"'))
        if base in PLUGINS:
            out.append((i + 1, base, read_blob_magic(lines, i + 1)))
    return out


def shift(slots, insert_at, old_max):
    # A plugin with <= 64 sliders has its line PADDED to 64 dash tokens, so
    # `slots` carries empty keys well above the plugin's real slider count.
    # Those are padding and are dropped; only a REAL value above the old maximum
    # means this instance is not on the old layout, and that must stop the run.
    new = {}
    for sid, tok in slots.items():
        if sid > old_max:
            if tok is not None:
                raise SliderLineError(
                    "slider %d holds %r, above the old layout's maximum of %d -- "
                    "this instance is not on the old layout" % (sid, tok, old_max))
            continue
        new[sid + 1 if sid >= insert_at else sid] = tok
    new[insert_at] = "0"
    return new


def migrate_file(path, apply_changes):
    with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        text = fh.read()
    lines = text.splitlines(keepends=True)
    found = instances(lines)
    if not found:
        return None

    changed, report = 0, []
    for vi, base, magic in found:
        insert_at, old_max, want_magic = PLUGINS[base]
        original = lines[vi]
        slots = parse_line(original)
        top = max((s for s, t in slots.items() if t is not None), default=0)

        if magic is not None and magic >= want_magic:
            report.append((base, "skip", "current layout (magic %g)" % magic)); continue
        if top > old_max:
            report.append((base, "skip", "already migrated (stores slider %d)" % top)); continue
        if top < insert_at:
            report.append((base, "skip", "nothing stored at/above %d" % insert_at)); continue

        body = original.rstrip("\r\n")
        eol = original[len(body):]
        rebuilt = render_line(body, shift(slots, insert_at, old_max),
                              n_sliders=old_max + 1) + eol

        # Verify this line before accepting it: nothing below the insert point may
        # move, every old N must land at N+1, and the seed must be present.
        after = parse_line(rebuilt)
        for sid in range(1, insert_at):
            if slots.get(sid) != after.get(sid):
                raise SliderLineError("%s: slider %d moved" % (base, sid))
        for sid in range(insert_at, old_max + 1):
            if slots.get(sid) != after.get(sid + 1):
                raise SliderLineError("%s: old slider %d did not land at %d"
                                      % (base, sid, sid + 1))
        if after.get(insert_at) != "0":
            raise SliderLineError("%s: seed missing at %d" % (base, insert_at))

        lines[vi] = rebuilt
        changed += 1
        report.append((base, "MIGRATE", "insert@%d  old_max=%d  top=%d"
                       % (insert_at, old_max, top)))

    if changed:
        rebuilt_lines = "".join(lines).splitlines(keepends=True)
        if len(rebuilt_lines) != len(text.splitlines(keepends=True)):
            raise SliderLineError("%s: line count would change; refusing to write" % path)
        if len(instances(rebuilt_lines)) != len(found):
            raise SliderLineError("%s: instance count would change; refusing" % path)
        if apply_changes:
            with open(path, "w", encoding="utf-8",
                      errors="surrogateescape", newline="") as fh:
                fh.write("".join(lines))
    return changed, report


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show-skips", action="store_true")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, f) for f in names if f.lower().endswith(".rpp")]
        else:
            files.append(p)

    total = 0
    for path in sorted(files):
        res = migrate_file(path, args.apply)
        if res is None:
            continue
        c, report = res
        total += c
        shown = [r for r in report if r[1] != "skip" or args.show_skips]
        if c or args.show_skips:
            print("%s  migrated=%d%s" % (path, c, "" if args.apply else "  (DRY RUN)"))
            for base, verdict, why in shown:
                print("   %-36s %-8s %s" % (base, verdict, why))
    print("\nTOTAL migrated=%d%s"
          % (total, "" if args.apply else "   (DRY RUN -- pass --apply to write)"))


if __name__ == "__main__":
    main()
