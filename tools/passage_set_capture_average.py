#!/usr/bin/env python3
"""Set Capture average across every Passage / Morpher instance in a project.

    python tools/passage_set_capture_average.py PROJECT.RPP --value 6
    python tools/passage_set_capture_average.py *.RPP --value 6 --in-place

Capture average is the wash's multi-frame analysis: 1 reads a single instant and
freezes its per-bin scatter (the wobble on re-spectralised material), higher
averages several overlapping frames so the scatter cancels. Turning it up on a
finished project is a one-control change, but doing it by hand means opening
every project, finding the control on every instance, and saving again.

WHAT IT TOUCHES
---------------
Only the plugin's slider line -- one line of plain text per instance. It does not
go near the saved captures.

That works because of how both plugins restore the setting. Capture average is
stored per slot, but a project saved before the control existed has no such field,
and on load the plugin seeds every slot from the visible slider (the same
migration the per-slot Capture point uses). So writing the slider is enough: all
eight slots follow it. Projects saved SINCE the control existed carry their own
per-slot values, and those win -- as they should, since somebody chose them.

Old projects may not have the slider at all: Morpher's Capture average is slider
28, and a project from its 16-slider days stops long before that. The missing
positions in between are filled with each slider's real default, read live out of
the .jsfx file rather than guessed, so nothing else moves.

Run it on a copy first if that's more comfortable -- `--in-place` keeps a
`.pre-capavg-bak` beside each project, and close the project in REAPER before
running, or REAPER writes its own copy back over yours on the next save.
"""

import argparse
import glob
import os
import re
import shutil
import sys

# plugin filename -> (slider number carrying Capture average, source file)
TARGETS = {
    "spectral_vowel_passage.jsfx": (4, "spectral_vowel_passage.jsfx"),
    "spectral_vowel_morpher.jsfx": (28, "spectral_vowel_morpher.jsfx"),
}
BACKUP_SUFFIX = ".pre-capavg-bak"


def slider_defaults(jsfx_path):
    """Every slider's default value, straight out of the plugin source."""
    out = {}
    with open(jsfx_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r"slider(\d+):([^<]*)<", line)
            if m:
                out[int(m.group(1))] = m.group(2).strip() or "0"
    return out


def set_value(line, slot, value, defaults):
    """Put `value` at 1-based slider position `slot` on a REAPER slider line."""
    eol = "\r" if line.endswith("\r") else ""
    line = line[: len(line) - len(eol)]
    indent = line[: len(line) - len(line.lstrip())]
    tokens = line.strip().split()
    values = [t for t in tokens if t != "-"]
    if values != tokens[: len(values)]:
        return line + eol, "SKIPPED (unexpected layout)"

    width = len(tokens)
    if len(values) >= slot and values[slot - 1] == str(value):
        return line + eol, "already %s" % value

    grew = 0
    while len(values) < slot:
        # Fill the gap with what the plugin itself would use, so turning this one
        # control on cannot quietly move anything else.
        values.append(defaults.get(len(values) + 1, "0"))
        grew += 1
    values[slot - 1] = str(value)
    pad = max(0, width - len(values))
    note = " (+%d default slider(s) filled in)" % grew if grew else ""
    return indent + " ".join(values + ["-"] * pad) + eol, "set to %s%s" % (value, note)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+")
    ap.add_argument("--value", type=int, default=6, help="1-6 (default 6)")
    ap.add_argument("--src", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "..", "src"),
                    help="folder holding the .jsfx sources (for slider defaults)")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not 1 <= args.value <= 6:
        ap.error("--value must be 1-6")

    defaults = {name: slider_defaults(os.path.join(args.src, src))
                for name, (_, src) in TARGETS.items()}

    paths = []
    for pat in args.projects:
        paths += sorted(glob.glob(pat)) or [pat]

    total = 0
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="surrogateescape",
                      newline="") as fh:
                text = fh.read()
        except OSError as exc:
            print("%-40s ERROR: %s" % (os.path.basename(path), exc))
            continue
        nl = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(nl)

        changed, notes = 0, []
        for i, line in enumerate(lines):
            if "<JS" not in line:
                continue
            hit = next((n for n in TARGETS if re.search(r"/%s\b" % re.escape(n), line)), None)
            if hit is None or i + 1 >= len(lines):
                continue
            new_line, status = set_value(lines[i + 1], TARGETS[hit][0],
                                         args.value, defaults[hit])
            lines[i + 1] = new_line
            notes.append(status)
            if status.startswith("set to"):
                changed += 1

        if not notes:
            print("%-40s no Passage / Morpher instances" % os.path.basename(path))
            continue
        extra = ""
        if any("filled in" in n for n in notes):
            extra = "  [older layout extended]"
        print("%-40s %d/%d instance(s) set%s" % (os.path.basename(path), changed, len(notes), extra))
        skipped = [n for n in notes if n.startswith("SKIPPED")]
        for n in skipped:
            print("      %s" % n)

        if args.dry_run or not changed:
            continue
        if args.in_place:
            backup = path + BACKUP_SUFFIX
            if not os.path.exists(backup):
                shutil.copy2(path, backup)
        with open(path, "w", encoding="utf-8", errors="surrogateescape",
                  newline="") as fh:
            fh.write(nl.join(lines))
        total += changed

    print("\n%d instance(s) %s" % (total, "would change" if args.dry_run else "written"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
