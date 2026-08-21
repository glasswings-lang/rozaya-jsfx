#!/usr/bin/env python3
"""Migrate REAPER projects across Spectral Vowel Morpher's layer-order change.

WHY THIS EXISTS
---------------
The Layer selector used to list the Original LAST, after all fifteen
pitch-shifted layers.  It now lists it FIRST, where it belongs by meaning: it is
the thing the other fifteen are measured against, and having to arrow past all of
them to reach it was more to hold in your head than the position was worth.

That shifts every index in two lists:

    Layer selector (slider33)        old Original 15 -> new 0, old 0..14 -> 1..15
    Drift / Ramp target (17, 23)     old Original 23 -> new 8, old 8..22 -> 9..23
                                     targets 0..7 are not layers and do not move

The plugin migrates its own @serialize blob -- the per-layer levels, mutes,
solos and every Drift/Ramp bank rotate themselves on load.  What it CANNOT reach
is the slider line: slider33, slider17 and slider23 hold indices into these same
lists and live in the project file.  Without this script the banks are correct
but the selector and the two target pickers point one entry low.

WHICH INSTANCES ARE TOUCHED
---------------------------
Only those whose blob magic is 7700005 or 7700006 -- the two layouts that had a
Layer selector with the Original at the end.  The magic is the first float32 of
the <JS_SER> block, so this is read from the project rather than guessed from
the slider count, which cannot tell a migrated project from an un-migrated one
(the count did not change).

Anything older has no layer selector at all: those sliders did not exist, REAPER
gives the missing trailing ones their defaults, and there is nothing to move.
Anything at 7700007 is already current.

RUN IT ONCE PER PROJECT.  Opening a migrated project in REAPER re-saves the blob
at 7700007, after which this script correctly skips it -- but if you re-run it
BEFORE opening the project, it would shift a second time.  In-place edits write a
`.pre-layer-order-bak` copy first and refuse to clobber an existing one, so the
backup is also the record of what has already been done.

USAGE
-----
    python tools/morpher_migrate_layer_order.py PROJECT.RPP [MORE.RPP ...]
    python tools/morpher_migrate_layer_order.py PROJECT.RPP --dry-run
    python tools/morpher_migrate_layer_order.py PROJECT.RPP --out MIGRATED.RPP

Close the project in REAPER before migrating in place -- REAPER holds its own
copy in memory and writes it back over yours on the next save.
"""

import argparse
import base64
import os
import shutil
import struct
import sys

PLUGIN = "spectral_vowel_morpher.jsfx"
BACKUP_SUFFIX = ".pre-layer-order-bak"

# 1-indexed slider -> which list its value indexes into
SEL_SLIDER = 33          # Layer selector
TARGET_SLIDERS = (17, 23)  # Drift target, Ramp target
LAY_T0 = 8               # first layer entry in the target list

# CANON is the order every layout up to 7700006 used:
#   0..2  Custom 1..3
#   3..14 the twelve intervals, low to high
#   15    the Original (absent in 7700005, which had only 15 slots)
# The list is now a PITCH LADDER, and CANON_TO_LADDER[canon_index] is where that
# entry sits in it.  Kept deliberately as a literal table rather than computed:
# it has to agree, entry for entry, with lay_perm in the plugin's @init.
CANON_TO_LADDER = {
    0: 13, 1: 14, 2: 15,        # Custom 1..3 trail the ladder
    3: 0,  4: 1,  5: 2,  6: 3,  # 4,3,2,1 octaves down
    7: 4,  8: 5,                # a fifth down, a fourth down
    9: 7,  10: 8,               # a fourth up, a fifth up
    11: 9, 12: 10, 13: 11, 14: 12,   # 1,2,3,4 octaves up
    15: 6,                      # the Original, at unison, mid-ladder
}
# 7700007 briefly put the Original FIRST; shift back by one to reach CANON.
ROTATED = {7700007}
MIGRATABLE = {7700005, 7700006, 7700007}
CURRENT = 7700008


def read_magic(b64):
    """First float32 of the @serialize stream, or None if it can't be read."""
    try:
        raw = base64.b64decode("".join(b64), validate=False)
    except Exception:
        return None
    if len(raw) < 4:
        return None
    return int(round(struct.unpack("<f", raw[:4])[0]))


def shift(value, magic, is_target):
    """Move one index from an old list into the pitch ladder."""
    base = LAY_T0 if is_target else 0
    if is_target and value < LAY_T0:
        return value                      # Texture..High cut: not layers
    canon = value - base
    if magic in ROTATED:                  # Original-first: undo that rotate
        canon = (canon - 1) % 16
    if canon not in CANON_TO_LADDER:
        return None                       # out of range for this layout
    return base + CANON_TO_LADDER[canon]


def rewrite_values(line, magic):
    eol = "\r" if line.endswith("\r") else ""
    line = line[: len(line) - len(eol)]
    indent = line[: len(line) - len(line.lstrip())]
    tokens = line.strip().split()
    values = [t for t in tokens if t != "-"]
    if values != tokens[: len(values)]:
        return line + eol, "SKIPPED (unexpected layout: '-' among the values)"
    need = max(SEL_SLIDER, max(TARGET_SLIDERS))
    if len(values) < need:
        return line + eol, ("SKIPPED (%d values, need at least %d -- blob says %d "
                            "but the slider line disagrees)" % (len(values), need, magic))

    moved = []
    for sl in (SEL_SLIDER,) + TARGET_SLIDERS:
        i = sl - 1
        try:
            v = int(float(values[i]))
        except ValueError:
            return line + eol, "SKIPPED (slider%d is not a number: %r)" % (sl, values[i])
        nv = shift(v, magic, sl in TARGET_SLIDERS)
        if nv is None:
            return line + eol, "SKIPPED (slider%d = %d is outside the old list)" % (sl, v)
        if nv != v:
            values[i] = str(nv)
            moved.append("slider%d %d->%d" % (sl, v, nv))

    pad = max(0, len(tokens) - len(values))
    status = "migrated (%s)" % ", ".join(moved) if moved else "no change needed"
    return indent + " ".join(values + ["-"] * pad) + eol, status


def migrate(text):
    lines = text.split("\n")
    report = []
    for i, line in enumerate(lines):
        if "<JS" not in line or PLUGIN not in line or "<JS_SER" in line:
            continue
        if i + 1 >= len(lines):
            continue
        # The blob for this instance is the <JS_SER> block that follows, a couple
        # of lines down past this <JS> block's own closing '>'. Stop at the next
        # <JS so a plugin with no blob can never borrow the next plugin's.
        b64, j = [], i + 1
        while j < len(lines) and "<JS_SER" not in lines[j]:
            if j > i + 1 and lines[j].lstrip().startswith("<JS "):
                break
            j += 1
        if j < len(lines) and "<JS_SER" in lines[j]:
            k = j + 1
            while k < len(lines) and lines[k].strip() not in (">", ""):
                b64.append(lines[k].strip())
                k += 1
        magic = read_magic(b64) if b64 else None
        if magic == CURRENT:
            report.append("already current (blob %s)" % magic)
            continue
        if magic not in MIGRATABLE:
            report.append("skipped (blob %s -- no layer selector to move)" % magic)
            continue
        lines[i + 1], status = rewrite_values(lines[i + 1], magic)
        report.append("%s [blob %s]" % (status, magic))
    return "\n".join(lines), report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+")
    ap.add_argument("--out", help="write here instead of in place (single project only)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.out and len(args.projects) > 1:
        ap.error("--out takes a single project")

    problems = 0
    for path in args.projects:
        with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            text = fh.read()
        new_text, report = migrate(text)
        print("\n%s" % path)
        if not report:
            print("   no %s instances" % PLUGIN)
            continue
        for n, status in enumerate(report, 1):
            print("   instance %d: %s" % (n, status))
            if status.startswith("SKIPPED"):
                problems += 1
        if args.dry_run or new_text == text:
            continue
        dest = args.out or path
        if not args.out:
            backup = path + BACKUP_SUFFIX
            if os.path.exists(backup):
                print("   REFUSING: %s already exists -- this project looks migrated"
                      % os.path.basename(backup))
                problems += 1
                continue
            shutil.copy2(path, backup)
            print("   backup: %s" % os.path.basename(backup))
        with open(dest, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            fh.write(new_text)
        print("   written: %s" % dest)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
