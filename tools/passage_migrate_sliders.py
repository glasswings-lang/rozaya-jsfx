#!/usr/bin/env python3
"""Migrate REAPER projects across Spectral Vowel Passage's slider-layout changes.

WHY THIS EXISTS
---------------
REAPER restores plugin values by slider POSITION, so inserting a control in the
middle of the list shifts every value above it.  A project saved against an older
Passage build therefore opens with its controls off by however many sliders were
inserted below them -- Wash grain's 150 arriving as Voice level dB (clamped to
+12), Auto-morph landing on Audition, and so on up the list.

What is NOT affected: the captures.  Those live in the <JS_SER ...> blob, which
is a raw @serialize memory dump with no notion of slider numbering at all.  It
survives any renumber untouched, which is what makes a text migration possible
instead of a re-capture or a compensating renumber of the plugin.  Each of these
changes lives entirely in one plain-text line per plugin instance.

New sliders are seeded to whatever reproduces the OLD behaviour, never to the
plugin's own default -- the point of a migration is that the project still sounds
like itself.  Change them afterwards if you want the new default; that is a
choice, not a correction.

THE HOPS, oldest first
----------------------
32 -> 34  Fade in shape / Fade out shape inserted at 10-11.
          Seeded to 0 (Linear): the pre-shape build had no curve control and
          ramped straight, so Linear is what those fades literally were.
          Everything from Input level up shifts by two.

34 -> 35  Capture average inserted at 4, beside the other capture-analysis
          controls.  Seeded to 1 (a single analysis frame), which is exactly what
          those projects were analysed with.  Everything from Slot fade in up
          shifts by one.

A project gets whichever hops it still needs, in order, so a 32-slider project
migrates straight through to 35 in one run.

USAGE
-----
    python tools/passage_migrate_sliders.py PROJECT.RPP [PROJECT2.RPP ...]
    python tools/passage_migrate_sliders.py PROJECT.RPP --out MIGRATED.RPP
    python tools/passage_migrate_sliders.py PROJECT.RPP --dry-run

In-place edits write a `.pre-slider-migrate-bak` copy alongside first (and refuse
to clobber an existing one).  Close the project in REAPER before migrating in
place -- REAPER holds its own copy in memory and writes it back over yours on the
next save.

Idempotent: an instance already at the current count is left alone, so re-running
over a folder is safe.
"""

import argparse
import os
import shutil
import sys

PLUGIN = "spectral_vowel_passage.jsfx"

# (slider count this hop applies to, how many sliders keep their place, values to
# insert).  A "keep" of 9 means the new values land at slider 10, straight after
# Slot mute.  Ordered oldest hop first; a project is walked through every hop it
# still needs, so the chain composes.
HOPS = [
    (32, 9, ["0", "0"]),   # Fade in shape / Fade out shape -> Linear
    (34, 3, ["1"]),        # Capture average -> 1 frame
]
CURRENT = 35   # slider count of the build this script targets

BACKUP_SUFFIX = ".pre-slider-migrate-bak"


def shift_slider_line(line):
    """Rewrite one JSFX slider-value line.  Returns (new_line, status)."""
    # REAPER writes CRLF.  The file is read with newline='' so those survive as
    # literal characters, which means the split leaves a '\r' on the end of
    # every line -- carry it back onto the rewritten one rather than leaving a
    # single LF line in the middle of a CRLF file.
    eol = "\r" if line.endswith("\r") else ""
    line = line[: len(line) - len(eol)]

    stripped = line.strip()
    if not stripped:
        return line + eol, "skipped (blank)"

    indent = line[: len(line) - len(line.lstrip())]
    tokens = stripped.split()

    # REAPER pads the line out to a fixed number of slots with '-'.  Count only
    # the real values; the padding is regenerated to keep the line's width.
    values = [t for t in tokens if t != "-"]
    width = len(tokens)

    # A '-' interleaved among the values would mean this is not the simple
    # "N values then padding" shape this migration assumes.  Bail rather than
    # guess -- a wrong guess here silently rewrites someone's mix.
    if values != tokens[: len(values)]:
        return line + eol, "SKIPPED (unexpected layout: '-' among the values)"

    if len(values) == CURRENT:
        return line + eol, "already current"

    applied = []
    for count, keep, inserted in HOPS:
        if len(values) == count:
            values = values[:keep] + list(inserted) + values[keep:]
            applied.append("%d->%d" % (count, len(values)))

    if not applied:
        known = sorted({h[0] for h in HOPS} | {CURRENT})
        return line + eol, ("SKIPPED (unrecognised layout: %d values, expected one "
                            "of %s)" % (len(values), known))
    if len(values) != CURRENT:
        return line + eol, ("SKIPPED (hop chain ended at %d, not %d -- HOPS is "
                            "incomplete)" % (len(values), CURRENT))

    # Give back the slots the new values took, so the line keeps the width
    # REAPER wrote.  It re-pads on its own next save either way.
    pad = max(0, width - len(values))
    return (indent + " ".join(values + ["-"] * pad) + eol,
            "migrated (%s)" % ", ".join(applied))


def migrate(text):
    """Rewrite every Passage instance in a project.  Returns (text, report)."""
    lines = text.split("\n")
    report = []
    for i, line in enumerate(lines):
        if PLUGIN not in line or "<JS" not in line:
            continue
        # The slider values are always the line immediately after the <JS ...>
        # header.
        if i + 1 >= len(lines):
            report.append(("SKIPPED", "instance at line %d: truncated file" % (i + 1)))
            continue
        new_line, status = shift_slider_line(lines[i + 1])
        lines[i + 1] = new_line
        report.append((status, "instance at line %d: %s" % (i + 1, status)))
    return "\n".join(lines), report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+", help="REAPER .RPP project files")
    ap.add_argument("--out", help="write to this path instead of editing in place "
                                  "(single project only)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change, write nothing")
    args = ap.parse_args()

    if args.out and len(args.projects) != 1:
        ap.error("--out takes a single project")

    failures = 0
    for path in args.projects:
        print("== %s" % path)
        try:
            with open(path, "r", encoding="utf-8", errors="surrogateescape",
                      newline="") as fh:
                text = fh.read()
        except OSError as exc:
            print("   ERROR: %s" % exc)
            failures += 1
            continue

        new_text, report = migrate(text)
        if not report:
            print("   no %s instances found" % PLUGIN)
            continue
        for status, line in report:
            print("   %s" % line)
            if status.startswith("SKIPPED"):
                failures += 1

        changed = sum(1 for status, _ in report if status.startswith("migrated"))
        if args.dry_run:
            print("   dry run -- nothing written (%d would change)" % changed)
            continue
        if not changed:
            print("   nothing to write")
            continue

        dest = args.out or path
        if not args.out:
            backup = path + BACKUP_SUFFIX
            if os.path.exists(backup):
                print("   ERROR: %s already exists; move it aside first" % backup)
                failures += 1
                continue
            shutil.copy2(path, backup)
            print("   backed up -> %s" % backup)
        with open(dest, "w", encoding="utf-8", errors="surrogateescape",
                  newline="") as fh:
            fh.write(new_text)
        print("   wrote %s (%d instance(s) migrated)" % (dest, changed))

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
