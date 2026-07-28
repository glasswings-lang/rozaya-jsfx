#!/usr/bin/env python3
"""Migrate REAPER projects across the Spectral Vowel Passage fade-shape renumber.

WHY THIS EXISTS
---------------
"Fade in shape" and "Fade out shape" were added to Spectral Vowel Passage as
sliders 10 and 11, which pushed every control from "Input level" upward along by
two.  Slider IDs are REAPER's primary key for plugin state: it restores values by
POSITION, so a project saved against the 32-slider build opens on the 34-slider
build with everything above slider 9 off by two -- Wash grain 150 arriving as
Voice level dB (clamped to +12), Auto-morph landing on Audition, and so on.

What is NOT affected: the captures.  Those live in the <JS_SER ...> blob, which
is a raw @serialize memory dump with no notion of slider numbering at all.  It
survives the renumber untouched, which is what makes a text migration possible
instead of a re-capture or a second renumber of the plugin.

So this rewrites only the plugin's slider VALUE line:

    old 1-9   ->  new 1-9    (Capture slot .. Slot mute -- unchanged)
    (new)     ->  new 10, 11 (Fade in / out shape, seeded to 0 = Linear)
    old 10-32 ->  new 12-34  (Input level .. Ramp engage -- shifted by two)

Linear, not the plugin's Cosine default, because a straight ramp is what the
fades in these projects literally were: the old build had no shape control and
ramped linearly.  Migrating to Cosine would quietly re-voice every fade in the
project.  Set them to Cosine afterwards if you prefer it -- it is a house-style
choice, not a correctness one.

USAGE
-----
    python tools/passage_shift_fade_shapes.py PROJECT.RPP [PROJECT2.RPP ...]
    python tools/passage_shift_fade_shapes.py PROJECT.RPP --out MIGRATED.RPP
    python tools/passage_shift_fade_shapes.py PROJECT.RPP --dry-run

In-place edits write a `.pre-fadeshape-bak` copy alongside first (and refuse to
clobber an existing one).  Close the project in REAPER before migrating in
place -- REAPER holds its own copy in memory and will write it back over yours
on the next save.

Idempotent: an instance already carrying 34 values is left alone, so re-running
over a folder is safe.
"""

import argparse
import os
import shutil
import sys

PLUGIN = "spectral_vowel_passage.jsfx"

OLD_COUNT = 32   # slider count of the pre-fade-shape build
NEW_COUNT = 34   # slider count once Fade in / Fade out shape exist
KEEP = 9         # sliders 1-9 keep their position
FADE_IN_SHAPE = "0"    # 0 = Linear, matching how the old build actually faded
FADE_OUT_SHAPE = "0"


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
    # the real values; the padding is regenerated to keep the total width.
    values = [t for t in tokens if t != "-"]
    dashes = len(tokens) - len(values)

    # A '-' interleaved among the values would mean this is not the simple
    # "N values then padding" shape this migration assumes.  Bail rather than
    # guess -- a wrong guess here silently rewrites someone's mix.
    if values != tokens[: len(values)]:
        return line + eol, "SKIPPED (unexpected layout: '-' among the values)"

    if len(values) == NEW_COUNT:
        return line + eol, "already migrated"
    if len(values) != OLD_COUNT:
        return line + eol, "SKIPPED (expected %d values, found %d)" % (OLD_COUNT, len(values))

    new_values = (
        values[:KEEP]
        + [FADE_IN_SHAPE, FADE_OUT_SHAPE]
        + values[KEEP:]
    )
    # Give back the two slots the new values took, so the line keeps the width
    # REAPER wrote.  It re-pads on its own next save either way.
    new_dashes = max(0, dashes - (NEW_COUNT - OLD_COUNT))
    return indent + " ".join(new_values + ["-"] * new_dashes) + eol, "migrated"


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
            report.append("instance at line %d: SKIPPED (truncated file)" % (i + 1))
            continue
        new_line, status = shift_slider_line(lines[i + 1])
        lines[i + 1] = new_line
        report.append("instance at line %d: %s" % (i + 1, status))
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
        for line in report:
            print("   %s" % line)

        changed = sum(1 for r in report if r.endswith("migrated")
                      and "already" not in r)
        if args.dry_run:
            print("   dry run -- nothing written (%d would change)" % changed)
            continue
        if not changed:
            print("   nothing to write")
            continue

        dest = args.out or path
        if not args.out:
            backup = path + ".pre-fadeshape-bak"
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
