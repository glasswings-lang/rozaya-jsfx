#!/usr/bin/env python3
"""Repair Melody Phase projects saved before the 2026-07-02 slider insert.

WHAT WENT WRONG
---------------
Commit ac7f125 (2026-07-02, "Speed Ramp reaches all 28 targets") inserted a new
slider -- `Ramp target` -- at position 67, in the MIDDLE of the list. The slider
count went 75 -> 76 and every control from 67 up moved one place:

    old 67 Speed ramp by          -> new 68 Ramp by
    old 68 Speed ramp duration    -> new 69 Ramp duration
    old 69 Speed ramp engage      -> new 70 Ramp engage
    old 70 Speed ramp start delay -> new 71 Ramp start delay
    old 71 Drift target           -> new 72 Drift target
    old 72 Drift up               -> new 73 Drift up
    old 73 Drift down             -> new 74 Drift down
    old 74 Drift period (dflt 8)  -> new 75 Drift period
    old 75 Drift shape            -> new 76 Drift shape

REAPER restores by POSITION, so a project saved before that commit now feeds the
default Drift period of 8 into `Drift down`, and Drift shape (0) into `Drift
period`. `(up > 0 || down > 0)` therefore goes TRUE on a plugin the user never
configured drift on, and `max(per, 1)` makes the period ONE cycle -- the rate is
swung down by up to 8 units every single cycle. Audibly: every note a different
length, with the fault landing at the passage from one note to the next.

THE GATE
--------
The same commit bumped the @serialize magic from 1000000+N to 2100000+N, so the
blob's leading float32 is an exact discriminator and nothing has to be guessed:

    magic 1000028 -> saved on the OLD 75-slider layout  -> migrate
    magic 2100028 -> saved on the CURRENT layout        -> leave alone

The blob itself is NOT touched. Its drift banks are all at their @init defaults
(up 0, down 0, per 8, shape 0) -- drift was never configured -- and because the
magic mismatches, the plugin ignores the blob and reads the slider line, which is
exactly the line this script repairs. REAPER rewrites the blob in the current
format the next time the project is saved.

SEEDING
-------
The new slider 67 (`Ramp target`) is seeded to 0 = Rate Value. The old Speed Ramp
was single-target and always acted on Rate Value, so 0 reproduces the OLD
behaviour rather than the plugin's default -- the project still sounds like
itself.

SAFETY
------
- Indexing goes through tools/rpp_sliders.py, which knows about the marker token
  at index 64 and about dash padding that can sit between real values.
- All-or-nothing per project file: every instance is rebuilt in memory and the
  whole file verified before a single byte is written.
- Verify the OUTPUT, not the run: melody_verify_drift_shift.py re-reads the files
  from disk afterwards and checks them against the pre-migration snapshot.
"""

import argparse
import base64
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line, SliderLineError  # noqa: E402

OLD_MAGIC = 1000028          # v2.9 drift-only, 28 targets -- the pre-insert format
NEW_MAGIC = 2100028          # v2.14 -- the format ac7f125 introduced
INSERT_AT = 67               # `Ramp target` was inserted here
OLD_MAX = 75                 # highest slider the old layout had
NEW_MAX = 76                 # highest slider this migration writes
SEED = {INSERT_AT: "0"}      # Ramp target = Rate Value: reproduces old behaviour

JS_RE = re.compile(r'^\s*<JS\s+\S*melody_phase\.jsfx\b')


def find_instances(lines):
    """Return [(values_line_index, magic_or_None)] for each Melody Phase instance.

    The block shape REAPER writes is:
        <JS glasswings/melody_phase.jsfx ""
          <values line>
        >
        <JS_SER
          <base64...>
        >
    The JS_SER sibling is optional -- older saves may lack one.
    """
    out = []
    for i, line in enumerate(lines):
        if not JS_RE.match(line):
            continue
        values_index = i + 1
        magic = None
        j = values_index
        while j < len(lines) and lines[j].strip() != ">":
            j += 1
        j += 1
        if j < len(lines) and lines[j].strip().startswith("<JS_SER"):
            b64, k = "", j + 1
            while k < len(lines) and not lines[k].strip().startswith(">"):
                b64 += lines[k].strip()
                k += 1
            try:
                raw = base64.b64decode(b64)
                if len(raw) >= 4:
                    magic = struct.unpack("<f", raw[:4])[0]
            except Exception:
                magic = None
        out.append((values_index, magic))
    return out


def shift(slots):
    """old slider N -> new slider N (N < 67), or N+1 (67 <= N <= 75)."""
    new = {}
    for sid, tok in slots.items():
        if sid > OLD_MAX:
            raise SliderLineError(
                "slider %d is above the old layout's maximum of %d -- this instance "
                "is not on the old layout, refusing to shift" % (sid, OLD_MAX))
        new[sid + 1 if sid >= INSERT_AT else sid] = tok
    new.update(SEED)
    return new


def migrate_file(path, apply_changes):
    with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        text = fh.read()
    lines = text.splitlines(keepends=True)

    instances = find_instances(lines)
    if not instances:
        return None

    changed = skipped = 0
    report = []
    for n, (vi, magic) in enumerate(instances, 1):
        original = lines[vi]
        if magic is None or abs(magic - OLD_MAGIC) > 0.5:
            skipped += 1
            report.append((n, "skip", "magic=%s" % magic, original.strip(), original.strip()))
            continue
        slots = parse_line(original)
        top = max((s for s, t in slots.items() if t is not None), default=0)
        if top < INSERT_AT:
            skipped += 1
            report.append((n, "skip", "nothing stored at or above slider %d" % INSERT_AT,
                           original.strip(), original.strip()))
            continue
        # rpp_sliders._split only preserves a trailing '\r', not '\n' -- it was
        # written for lines already stripped of their ending. Hand it a bare
        # body and put the ORIGINAL ending back, or every rewritten line welds
        # itself onto the '>' that closes the block. (Caught by the verifier on
        # the first run of this script: 17 lines lost in upswing, 19 in
        # outcoming -- one per migrated instance.)
        body = original.rstrip("\r\n")
        eol = original[len(body):]
        rebuilt = render_line(body, shift(slots), n_sliders=NEW_MAX)
        lines[vi] = rebuilt + eol
        changed += 1
        report.append((n, "MIGRATE", "magic=%d top=%d" % (OLD_MAGIC, top),
                       original.strip(), rebuilt.strip()))

    # All-or-nothing: prove the rebuilt file still has the same shape before a
    # single byte is written. A rewritten line that lost its ending would weld
    # itself onto the block's closing '>' and silently drop a line -- so count
    # them, and re-locate every instance in the rebuilt text.
    if changed:
        rebuilt_text = "".join(lines)
        rebuilt_lines = rebuilt_text.splitlines(keepends=True)
        if len(rebuilt_lines) != len(text.splitlines(keepends=True)):
            raise SliderLineError(
                "%s: line count would change %d -> %d; refusing to write"
                % (path, len(text.splitlines(keepends=True)), len(rebuilt_lines)))
        if len(find_instances(rebuilt_lines)) != len(instances):
            raise SliderLineError(
                "%s: instance count would change; refusing to write" % path)

    if changed and apply_changes:
        with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            fh.write("".join(lines))
    return changed, skipped, report


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help=".RPP files or folders")
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    ap.add_argument("--show", action="store_true", help="print every before/after line")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, f) for f in names if f.lower().endswith(".rpp")]
        else:
            files.append(p)

    total_c = total_s = 0
    for path in sorted(files):
        res = migrate_file(path, args.apply)
        if res is None:
            continue
        c, s, report = res
        total_c += c
        total_s += s
        print("%s  migrated=%d skipped=%d%s"
              % (path, c, s, "" if args.apply else "   (DRY RUN)"))
        for n, verdict, why, before, after in report:
            if verdict == "skip" and not args.show:
                continue
            print("   #%-2d %-8s %s" % (n, verdict, why))
            if args.show:
                print("       before: %s" % before)
                print("       after : %s" % after)
    print("\nTOTAL migrated=%d skipped=%d%s"
          % (total_c, total_s, "" if args.apply else "   (DRY RUN -- pass --apply to write)"))


if __name__ == "__main__":
    main()
