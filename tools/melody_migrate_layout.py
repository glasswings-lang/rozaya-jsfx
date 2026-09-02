#!/usr/bin/env python3
"""Migrate REAPER projects across Melody Phase's 2026-09 layout reorder.

WHAT CHANGED
------------
Positions: `Host ratio` sat sixty sliders from the Rate Mode that gave it
meaning; `Direction` split the transport block; the envelope shapes were four
sliders from the stages they shape; `Master Gain` sat in the middle of the sound
controls. All of that is reordered, and 78 sliders become 80.

Values, and these are the reason this is more than a permutation:

  * `Vn Semitones from root` becomes `Vn Note`, an absolute note name.
    Index 24 is C4, which is where "0 semitones" landed, so the conversion is
    `note = semitones + 24`. Exact.

  * `Root note` and `Center octave` become `Transpose (half steps)` and
    `Octave shift`, the pair Polyrhythm v3 already uses. They feed the same
    pitch conversion, so the values carry across exactly:
        Transpose    = old Root note        (a root of D = +2 half steps)
        Octave shift = old Center octave - 4
    Nothing moves in pitch.

  * `Rate Mode`'s fourth entry `Host x` is gone (R13: sync is not a unit).
    An instance that was in Host x becomes `Sync to host = On` with:
        Every N beats = 1 / old Rate Value      (the multiplier inverted)
        Rate value    = project tempo x old Rate Value, in BPM
    The first line is what it actually runs at; the second is what the rate
    slider hands back if sync is ever switched off, so it does not jump.
    THIS IS VISIBLE: those instances stop showing a multiplier and start
    showing a real BPM. They sound the same.

WHAT IS NOT TOUCHED
-------------------
The `@serialize` blob -- Drift and Ramp banks -- has no notion of slider
numbering and crosses untouched. The new tempo-sync bank is APPENDED to that
stream, so an old blob simply runs out and the beat counts take their defaults.

RUNNING IT TWICE IS SAFE
------------------------
The value count gates it: every old layout wrote 78 values or fewer, every
migrated one has 80. An instance with 79 or more is reported and skipped.

USAGE
-----
    python tools/melody_migrate_layout.py PROJECT.RPP [MORE.RPP ...] --dry-run
    python tools/melody_migrate_layout.py PROJECT.RPP [MORE.RPP ...]

Close the project in REAPER first -- REAPER holds its own copy in memory and
writes it back over yours on the next save.
"""

import argparse
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rpp_sliders as R

PLUGIN = "melody_phase.jsfx"
BACKUP_SUFFIX = ".pre-layout-bak"
OLD_COUNT = 78
NEW_COUNT = 80

# OLD slider -> NEW slider. Authored in docs/layouts/melody-phase.md; this only
# applies it. Old 77 (Host ratio) is deleted and deliberately absent.
OLD_TO_NEW = {
    2: 1, 1: 2, 3: 6, 78: 7, 4: 8, 5: 9, 6: 10, 9: 11,
    10: 12, 12: 13, 11: 14, 13: 15,
    20: 16, 21: 17,
    15: 18, 16: 19, 17: 20, 18: 21, 19: 22,
    14: 23, 63: 24, 7: 25,
    8: 66, 62: 67, 64: 68, 65: 69, 66: 70,
    72: 71, 73: 72, 74: 73, 75: 74, 76: 75,
    67: 76, 68: 77, 69: 78, 70: 79, 71: 80,
}
for _o in range(22, 62):
    OLD_TO_NEW[_o] = _o + 4

NEW_SLIDERS = {3, 4, 5}          # Sync to host, Host sync target, Every N beats
NOTE_SLIDERS_OLD = (22, 27, 32, 37, 42, 47, 52, 57)   # Vn Semitones from root
RATE_MODE_OLD = 1
RATE_VALUE_OLD = 2
ROOT_NOTE_OLD = 5
CENTER_OCT_OLD = 6
HOST_X = 3

# The OLD plugin's declared defaults, for any slider an older save predates.
OLD_DEFAULTS = {
    1: "1", 2: "1", 3: "0", 4: "440", 5: "0", 6: "4", 7: "1", 8: "-6",
    9: "0", 10: "10", 11: "30", 12: "1", 13: "1", 14: "0",
    15: "0", 16: "2", 17: "100", 18: "1", 19: "0", 20: "0", 21: "0",
    62: "0", 63: "0", 64: "0", 65: "0", 66: "0",
    67: "0", 68: "0", 69: "0", 70: "0", 71: "0",
    72: "0", 73: "0", 74: "0", 75: "8", 76: "0", 77: "0", 78: "25",
}
_VOICE_DEFAULTS = ["0", "1", "1", "-6", "1"]
_SEMIS = ["0", "2", "4", "5", "7", "9", "11", "12"]
_ACTIVE = ["1", "1", "1", "1", "0", "0", "0", "0"]
for _v in range(8):
    _b = 22 + _v * 5
    OLD_DEFAULTS[_b] = _SEMIS[_v]
    OLD_DEFAULTS[_b + 1] = _VOICE_DEFAULTS[1]
    OLD_DEFAULTS[_b + 2] = _VOICE_DEFAULTS[2]
    OLD_DEFAULTS[_b + 3] = _VOICE_DEFAULTS[3]
    OLD_DEFAULTS[_b + 4] = _ACTIVE[_v]

assert sorted(list(OLD_TO_NEW) + [77]) == list(range(1, OLD_COUNT + 1))
assert sorted(list(OLD_TO_NEW.values()) + list(NEW_SLIDERS)) == list(range(1, NEW_COUNT + 1))
assert sorted(OLD_DEFAULTS) == list(range(1, OLD_COUNT + 1))


fmt = R.fmt


def project_tempo(text):
    m = re.search(r'^\s*TEMPO\s+([0-9.]+)', text, re.M)
    return float(m.group(1)) if m else 120.0


def rewrite_values(line, tempo):
    """Permute one instance's slider line into the new layout.

    Slider ids come from rpp_sliders, which knows that REAPER puts a `""` marker
    after slider 64 -- indexing the raw tokens instead is what shifted every
    slider from 65 upward on 2026-09-02.
    """
    try:
        slots = R.parse_line(line)
    except R.SliderLineError as e:
        return line, "SKIPPED (%s)" % e, None

    if max(slots) > OLD_COUNT:
        return line, "already migrated (slider %d present)" % max(slots), None

    # Anything this save predates gets what REAPER was handing it.
    old = {}
    filled = 0
    for i in range(1, OLD_COUNT + 1):
        v = slots.get(i)
        if v is None:
            v = OLD_DEFAULTS[i]
            filled += 1
        old[i] = v

    def num(i, what):
        return R.as_float(old[i], what)

    try:
        new = {}
        for o, n in OLD_TO_NEW.items():
            new[n] = old[o]

        # Vn Semitones -> Vn Note (index 24 == C4 == the old zero)
        for o in NOTE_SLIDERS_OLD:
            v = num(o, "V-note slider%d" % o)
            new[OLD_TO_NEW[o]] = fmt(max(0, min(48, v + 24)))

        # Root note -> Transpose, Center octave -> Octave shift
        root = num(ROOT_NOTE_OLD, "Root note")
        cent = num(CENTER_OCT_OLD, "Center octave")
        new[OLD_TO_NEW[ROOT_NOTE_OLD]] = fmt(max(-12, min(12, root)))
        new[OLD_TO_NEW[CENTER_OCT_OLD]] = fmt(max(-4, min(4, cent - 4)))

        # Host x -> Sync to host
        note = None
        mode = num(RATE_MODE_OLD, "Rate mode")
        rate = num(RATE_VALUE_OLD, "Rate value")
        if int(mode) == HOST_X:
            rate = rate if rate > 0 else 1.0
            beats = max(0.25, min(1000, 1.0 / rate))
            bpm = max(0.001, min(1000, tempo * rate))
            new[2] = "0"                 # Rate mode -> BPM
            new[1] = fmt(bpm)            # Rate value -> a real BPM
            new[3] = "1"                 # Sync to host = On
            new[4] = "0"                 # target = Rate value
            new[5] = fmt(beats)
            note = ("Host x -> synced: every %s beats, rate reads %s BPM "
                    "(was x%s at %g BPM)" % (fmt(beats), fmt(bpm), fmt(rate), tempo))
        else:
            new[3] = "0"
            new[4] = "0"
            new[5] = "4"

        missing = [i for i in range(1, NEW_COUNT + 1) if i not in new]
        assert not missing, "unfilled new sliders: %s" % missing
        out = R.render_line(line, new, NEW_COUNT)
    except (R.SliderLineError, AssertionError) as e:
        return line, "SKIPPED (%s)" % e, None

    status = "migrated (%d stored%s)" % (
        OLD_COUNT - filled, ", %d filled from defaults" % filled if filled else "")
    return out, status, note


def migrate(text):
    tempo = project_tempo(text)
    lines = text.split("\n")
    report, notes = [], []
    for i, line in enumerate(lines):
        if "<JS " not in line or PLUGIN not in line or "melody_phase_v2" in line:
            continue
        if i + 1 >= len(lines):
            continue
        lines[i + 1], status, note = rewrite_values(lines[i + 1], tempo)
        report.append(status)
        if note:
            notes.append("instance %d: %s" % (len(report), note))
    return "\n".join(lines), report, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    problems = migrated = 0
    for path in args.projects:
        with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            text = fh.read()
        new_text, report, notes = migrate(text)
        if not report:
            continue
        print("\n%s" % path)
        for n, status in enumerate(report, 1):
            print("   instance %d: %s" % (n, status))
            if status.startswith("SKIPPED"):
                problems += 1
            elif status.startswith("migrated"):
                migrated += 1
        for note in notes:
            print("   ! %s" % note)
        if args.dry_run or new_text == text:
            continue
        backup = path + BACKUP_SUFFIX
        if os.path.exists(backup):
            print("   REFUSED to write: %s already exists" % backup)
            problems += 1
            continue
        shutil.copy2(path, backup)
        with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            fh.write(new_text)

    print("\n%d instance(s) migrated, %d problem(s)." % (migrated, problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
