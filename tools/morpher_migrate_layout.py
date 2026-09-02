#!/usr/bin/env python3
"""Migrate REAPER projects across Spectral Vowel Morpher's 2026-09 layout reorder.

WHY THIS EXISTS
---------------
The Morpher's controls were reordered so that things that belong together sit
together: Capture average rejoined the Capture group it had been twenty-four
sliders away from, High cut rejoined Low cut, Drift and Ramp stopped splitting
the sound controls in half, and the two global levels moved to the end of the
sound section where a global level belongs.  Two controls were added in their
proper places rather than bolted on the end -- `Sync to host` beside the
Auto-morph time it governs, and `Layer overtone harmonic` with the other layer
controls.  38 sliders became 40.

REAPER restores plugin values by slider POSITION, so a reorder moves every value
above the first change onto the wrong control.  The `@serialize` blob has no
notion of slider numbering, so captures, per-layer banks and every Drift/Ramp
bank cross untouched -- the whole break lives in one plain-text line per
instance, which is what this rewrites.

WHAT IT DOES TO EACH INSTANCE
-----------------------------
  * permutes the values into the new order (the table below)
  * `Capture slot` gains 1: the slider is 1-8 now, matching how slots are
    spoken about, where the engine stays 0-7 underneath
  * seeds `Sync to host` to Off and `Layer overtone harmonic` to -1
    (follow the global) -- the values that reproduce the OLD sound exactly

Sliders the instance never stored (it was saved by an older build with fewer
controls) are filled with the OLD plugin's declared defaults, which is precisely
what REAPER was handing them.  Five different slider counts are in the live
library and all of them migrate.

THE CAPTURE-SLOT SUBTLETY, WHICH IS REAL
----------------------------------------
`Capture slot` has been re-indexed once before: it was 1-8, and commit da04aac
(2026-07-09) made it 0-7.  Blob magic 7700002 arrived 2026-07-28, so anything at
7700002 or later is certainly 0-based.  Magic 7700001 straddles the change and
cannot be dated from its contents, so the rule is evidence-first:

    slider1 == 0            -> 0-based   (0 is not a legal 1-based value)
    magic >= 7700002        -> 0-based   (that magic postdates the change)
    file mtime >= 2026-07-09 -> 0-based
    otherwise               -> already 1-based, left alone

Instances taking that last branch are NAMED in the report, so the guess is
inspectable rather than silent.  If it is wrong for one, the consequence is that
its Capture-slot CURSOR points one slot along -- which control the Capture
group is aimed at, not what anything sounds like.  Nothing audible rides on it.

RUNNING IT TWICE IS SAFE
------------------------
The value count is the gate, and unusually for this suite it is a reliable one:
every old layout wrote 38 values or fewer, every migrated one has 40.  An
instance with 39 or more is reported as already migrated and skipped.

USAGE
-----
    python tools/morpher_migrate_layout.py PROJECT.RPP [MORE.RPP ...] --dry-run
    python tools/morpher_migrate_layout.py PROJECT.RPP [MORE.RPP ...]
    python tools/morpher_migrate_layout.py PROJECT.RPP --out MIGRATED.RPP

Close the project in REAPER before migrating in place -- REAPER holds its own
copy in memory and writes it back over yours on the next save.
"""

import argparse
import base64
import datetime
import os
import shutil
import struct
import sys

PLUGIN = "spectral_vowel_morpher.jsfx"
BACKUP_SUFFIX = ".pre-layout-bak"

OLD_COUNT = 38
NEW_COUNT = 40

# The authored permutation, from docs/layouts/spectral-vowel-morpher.md.
# OLD slider id -> NEW slider id.  Kept as a literal table, deliberately: it has
# to agree entry for entry with the declaration block in the plugin.
OLD_TO_NEW = {
    1: 1, 2: 2, 3: 3, 28: 4, 13: 5, 14: 6, 15: 7, 16: 9,
    6: 10, 7: 11, 8: 12, 9: 13, 10: 14, 12: 15, 11: 16, 32: 17,
    29: 18, 30: 19, 31: 20,
    33: 21, 34: 22, 35: 23, 36: 24, 37: 25, 38: 26,
    4: 28, 5: 29,
    17: 30, 18: 31, 19: 32, 20: 33, 21: 34, 22: 35,
    23: 36, 24: 37, 25: 38, 27: 39, 26: 40,
}

# New controls, seeded to whatever reproduces the old behaviour.
NEW_SLIDERS = {
    8: "0",    # Sync to host = Off, so the time stays in seconds
    27: "-1",  # Layer overtone harmonic = follow the global, as it always did
}

# The OLD plugin's declared defaults -- what REAPER supplied for any slider an
# older save did not store.  Read from the pre-reorder source, not typed by hand.
OLD_DEFAULTS = {
    1: "0", 2: "0", 3: "0", 4: "0", 5: "0", 6: "50", 7: "150", 8: "0",
    9: "0", 10: "50", 11: "0", 12: "0", 13: "1", 14: "0", 15: "0", 16: "20",
    17: "0", 18: "0", 19: "0", 20: "30", 21: "0", 22: "0", 23: "0", 24: "0",
    25: "0", 26: "0", 27: "0", 28: "1", 29: "0", 30: "24", 31: "1", 32: "20000",
    33: "6", 34: "1", 35: "0", 36: "0", 37: "-12", 38: "0",
}

ZERO_INDEXED_FROM = 7700002
REINDEX_DATE = datetime.datetime(2026, 7, 9)

assert sorted(OLD_TO_NEW) == list(range(1, OLD_COUNT + 1))
assert sorted(list(OLD_TO_NEW.values()) + list(NEW_SLIDERS)) == list(range(1, NEW_COUNT + 1))
assert sorted(OLD_DEFAULTS) == list(range(1, OLD_COUNT + 1))


def read_magic(b64):
    """First float32 of the @serialize stream, or None if it cannot be read."""
    try:
        raw = base64.b64decode("".join(b64), validate=False)
    except Exception:
        return None
    if len(raw) < 4:
        return None
    return int(round(struct.unpack("<f", raw[:4])[0]))


def capture_slot_is_zero_based(value, magic, mtime):
    """See THE CAPTURE-SLOT SUBTLETY above. Returns (bool, why)."""
    if value == "0":
        return True, "value 0"
    if magic is not None and magic >= ZERO_INDEXED_FROM:
        return True, "blob %d" % magic
    if mtime >= REINDEX_DATE:
        return True, "saved %s" % mtime.date()
    return False, "blob %s, saved %s -- treated as already 1-based" % (magic, mtime.date())


def rewrite_values(line, magic, mtime):
    eol = "\r" if line.endswith("\r") else ""
    line = line[: len(line) - len(eol)]
    indent = line[: len(line) - len(line.lstrip())]
    tokens = line.strip().split()
    values = [t for t in tokens if t != "-"]

    # Index by TOKEN position: a '-' between real values would shift every
    # slider after it, so refuse rather than rewrite the wrong controls.
    if values != tokens[: len(values)]:
        return line + eol, "SKIPPED (a '-' sits among the values)", None
    # ...and the same for the `""` marker REAPER writes after slider 64. The
    # Morpher has 40 sliders so it never appears here, and all 122 instances in
    # the library were checked for it on 2026-09-02. But a plugin that grows
    # past 64 gets one, and reading it as a value shifts every slider after it
    # -- which is exactly what happened to Melody Phase that day. If one ever
    # turns up, stop: tools/rpp_sliders.py is the code that knows the format,
    # and this tool should be rebuilt on it rather than guessing.
    if any(t.startswith('"') for t in tokens):
        return line + eol, ("SKIPPED (quoted token on the line -- use "
                            "tools/rpp_sliders.py, see its docstring)"), None
    if len(values) >= OLD_COUNT + 1:
        return line + eol, "already migrated (%d values)" % len(values), None
    if not values:
        return line + eol, "SKIPPED (no values on the line)", None

    # Fill anything this save predates with what REAPER was giving it.
    old = [values[i] if i < len(values) else OLD_DEFAULTS[i + 1]
           for i in range(OLD_COUNT)]
    filled = OLD_COUNT - len(values)

    new = [None] * NEW_COUNT
    for o, n in OLD_TO_NEW.items():
        new[n - 1] = old[o - 1]
    for n, v in NEW_SLIDERS.items():
        new[n - 1] = v
    assert all(v is not None for v in new)

    note = None
    zero_based, why = capture_slot_is_zero_based(old[0], magic, mtime)
    if zero_based:
        try:
            new[0] = str(int(float(old[0])) + 1)
        except ValueError:
            return line + eol, "SKIPPED (Capture slot %r is not a number)" % old[0], None
    else:
        note = why

    pad = max(0, len(tokens) - NEW_COUNT)
    status = "migrated (%d values%s)" % (
        len(values), ", %d filled from defaults" % filled if filled else "")
    return indent + " ".join(new + ["-"] * pad) + eol, status, note


def migrate(text, mtime):
    lines = text.split("\n")
    report, notes = [], []
    for i, line in enumerate(lines):
        if "<JS " not in line or PLUGIN not in line:
            continue
        if i + 1 >= len(lines):
            continue
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
        lines[i + 1], status, note = rewrite_values(lines[i + 1], magic, mtime)
        report.append("%s [blob %s]" % (status, magic))
        if note:
            notes.append("instance %d: Capture slot NOT shifted -- %s" % (len(report), note))
    return "\n".join(lines), report, notes


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
    migrated = 0
    all_notes = []
    for path in args.projects:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            text = fh.read()
        new_text, report, notes = migrate(text, mtime)
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
            all_notes.append("%s: %s" % (os.path.basename(path), note))
        if args.dry_run or new_text == text:
            continue
        target = args.out or path
        if not args.out:
            backup = path + BACKUP_SUFFIX
            if os.path.exists(backup):
                print("   REFUSED to write: %s already exists" % backup)
                problems += 1
                continue
            shutil.copy2(path, backup)
        with open(target, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
            fh.write(new_text)

    print("\n%d instance(s) migrated, %d problem(s)." % (migrated, problems))
    if all_notes:
        print("\n%d instance(s) had Capture slot left alone as already 1-based:" % len(all_notes))
        for n in all_notes:
            print("   %s" % n)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
