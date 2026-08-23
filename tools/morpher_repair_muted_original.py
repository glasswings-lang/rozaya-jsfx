#!/usr/bin/env python3
"""Repair Morpher instances the muted-Original bug wrote into saved projects.

THE BUG (fixed in the plugin as of commit "the level slider's default muted the
Original on load"): slider33 (Layer) defaults to 6, the Original, and slider35
(Layer level) defaulted to -60.  @slider stamps the visible level straight into
whatever layer the selector names, so any instance whose selector had not been
moved wrote -60 into the Original's slot before the first sample.  base_gain
gates the voice engine AND the wash's base term, so the instance was silent.

Projects opened and SAVED during that window have the -60 baked into their
slider line, so fixing the plugin is not enough for them -- they load, stamp
their saved -60, and stay silent.

WHAT THIS TOUCHES
-----------------
Only instances matching the bug's exact signature:

    slider33 == 6   (the selector is on the Original)
    slider35 == -60 (its level is at the floor)

and it sets slider35 to 0.  Nothing else, in no other instance.  A layer you
deliberately left at -60 has a different selector value and is not touched; a
deliberately-muted Original is indistinguishable from the bug from out here, so
check the report before trusting it.

Fixing the slider line is sufficient even though the blob also holds a muted
Original: @slider re-stamps the visible level into the bank on every call, so
the corrected value overwrites the restored one and the next save is clean.

    python tools/morpher_repair_muted_original.py PROJECT.RPP [...] [--dry-run]

Writes a `.pre-mute-repair-bak` beside each project and refuses to clobber one.
Close the project in REAPER first.
"""

import argparse
import os
import shutil
import sys

PLUGIN = "spectral_vowel_morpher.jsfx"
SEL_SLIDER, LVL_SLIDER = 33, 35
ORIGINAL_INDEX = 6
BACKUP_SUFFIX = ".pre-mute-repair-bak"


def repair(text):
    lines = text.split("\n")
    report = []
    for i, line in enumerate(lines):
        if "<JS" not in line or PLUGIN not in line or "<JS_SER" in line:
            continue
        if i + 1 >= len(lines):
            continue
        vline = lines[i + 1]
        eol = "\r" if vline.endswith("\r") else ""
        body = vline[: len(vline) - len(eol)]
        indent = body[: len(body) - len(body.lstrip())]
        tokens = body.strip().split()
        if len(tokens) < LVL_SLIDER:
            report.append("skipped (only %d sliders)" % len(tokens))
            continue
        sel, lvl = tokens[SEL_SLIDER - 1], tokens[LVL_SLIDER - 1]
        try:
            sel_v, lvl_v = int(float(sel)), float(lvl)
        except ValueError:
            report.append("skipped (non-numeric: %r / %r)" % (sel, lvl))
            continue
        if sel_v == ORIGINAL_INDEX and lvl_v <= -60:
            tokens[LVL_SLIDER - 1] = "0"
            lines[i + 1] = indent + " ".join(tokens) + eol
            report.append("REPAIRED (Original was at -60 -> 0 dB)")
        else:
            report.append("left alone (selector=%d, level=%s -- a real setting)"
                          % (sel_v, lvl))
    return "\n".join(lines), report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projects", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for path in args.projects:
        with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            text = fh.read()
        new_text, report = repair(text)
        print("\n%s" % path)
        if not report:
            print("   no %s instances" % PLUGIN)
            continue
        for n, st in enumerate(report, 1):
            print("   instance %d: %s" % (n, st))
        if args.dry_run or new_text == text:
            continue
        backup = path + BACKUP_SUFFIX
        if os.path.exists(backup):
            print("   REFUSING: %s already exists" % os.path.basename(backup))
            continue
        shutil.copy2(path, backup)
        with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            fh.write(new_text)
        print("   backup: %s" % os.path.basename(backup))
        print("   written: %s" % path)


if __name__ == "__main__":
    sys.exit(main())
