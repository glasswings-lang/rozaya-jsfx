#!/usr/bin/env python3
"""Spectral Vowel Passage, the 2026-09-11 layout: 38 sliders -> 62, in ONE migration.
docs/layouts/spectral-vowel-passage.md, "THE LAYOUT".

The slider line only. Old positions move by the AUTHORED map below (the same map
tools/jsfx_renumber.py applied to the source); every new control is seeded to what
reproduces the old sound. The blob is not touched: the plugin remaps its own.

Built in stages; the live projects are migrated ONCE, when every stage is in.
  stage 1  renumber, and seed the 24 new controls              (built)
  later    Capture slot +1 for All at 0

    python tools/passage_migrate_20260911.py inventory
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line, render_line

FX = "spectral_vowel_passage.jsfx"
LIVE = "E:/reaper"
N_OLD, N_NEW = 38, 62

# old id -> new id, copied from the renumber stage (docs/layouts/spectral-vowel-passage.md).
MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 21, 6: 22, 7: 23, 8: 24, 9: 26, 10: 27, 11: 31, 12: 32,
       13: 37, 14: 29, 15: 13, 16: 14, 17: 15, 18: 9, 19: 28, 20: 17, 21: 16, 22: 36, 23: 34,
       24: 35, 25: 44, 26: 45, 27: 46, 28: 48, 29: 50, 30: 53, 31: 54, 32: 55, 33: 58, 34: 62,
       35: 61, 36: 19, 37: 20, 38: 33}

# new id -> the value that reproduces the old sound.
SEEDS = {5: "0",        # Source note None: nothing measured from it
         6: "0", 7: "2",  # Source fine tune 0, in Cents
         8: "60",       # Target note, inert while Source note is None
         10: "1",       # Transpose unit Semitones: what Pitch (semitones) meant
         11: "0", 12: "2",  # Fine tune 0, in Cents
         18: "20000",   # High cut off
         25: "0",       # Slot timing unit Seconds: what the timings meant
         30: "440",     # Tuning reference
         38: "0", 39: "0", 40: "0", 41: "0", 42: "0", 43: "0",  # transport off
         47: "0",       # Drift amount unit: Target default
         49: "1",       # Drift period unit Seconds: what Drift period (seconds) meant
         51: "0", 52: "0",
         56: "0",       # Ramp by unit: Target default
         57: "2",       # Ramp time unit Minutes: what Ramp duration (minutes) meant
         59: "0", 60: "0"}


def refuse(where, why):
    raise SystemExit(f"REFUSED {where}: {why}")


def files():
    out = []
    for top, dirs, names in os.walk(LIVE):
        dirs[:] = [d for d in dirs if d.lower() != "backups"]
        for n in names:
            if n.lower().endswith(".rpp"):
                p = os.path.join(top, n).replace("\\", "/")
                if FX in open(p, encoding="utf-8", errors="surrogateescape").read():
                    out.append(p)
    return sorted(out)


def heads(lines):
    return [i for i, l in enumerate(lines) if "<JS " in l and "<JS_SER" not in l and FX in l]


# A line saved before 2026-07-27 (c962cf9) holds 35 values: Overtone harmonic, depth
# and width were APPENDED as 36-38 that day, 1-35 unmoved (declarations diffed). REAPER
# has been supplying their declared defaults on every load, unchanged since -- so those
# are the values these instances have always played with. 5 instances, all nightfall.RPP.
PRE_OVERTONE_FILL = {36: "0", 37: "24", 38: "1"}


def remap_line(line, where):
    slots = parse_line(line)
    stored = [k for k, v in slots.items() if v is not None]
    last = max(stored) if stored else 0
    if last == 35 and len(stored) == 35:
        slots.update(PRE_OVERTONE_FILL)
        stored = [k for k, v in slots.items() if v is not None]
    if not stored or max(stored) != N_OLD or len([k for k in stored if k <= N_OLD]) != N_OLD:
        refuse(where, f"not a whole {N_OLD}- or 35-slider line (stored ids end at {last})")
    new = {MAP[k]: slots[k] for k in range(1, N_OLD + 1)}
    # Stage 3, All slots: Capture slot was 0-7 and becomes {All, Slot 1 ... Slot 8},
    # so every saved slot moves up one and 0 is left for All.
    old_slot = float(new[1])
    if old_slot != int(old_slot) or not 0 <= old_slot <= 7:
        refuse(where, f"Capture slot {new[1]!r} is not a whole slot 0-7")
    new[1] = str(int(old_slot) + 1)
    for k, v in SEEDS.items():
        if k in new:
            refuse(where, f"seed {k} collides with a moved value")
        new[k] = v
    if sorted(new) != list(range(1, N_NEW + 1)):
        refuse(where, "the new line does not cover 1..62 exactly")
    return render_line(line, new, N_NEW)


def convert(path):
    text = open(path, encoding="utf-8", errors="surrogateescape", newline="").read()
    lines = text.splitlines(keepends=True)
    n_lines, hs = len(lines), heads(lines)
    if not hs:
        refuse(path, "no Passage instance")
    for hi in hs:
        lines[hi + 1] = remap_line(lines[hi + 1], f"{path} line {hi + 2}")
    if len(lines) != n_lines or len(heads(lines)) != len(hs):
        refuse(path, "line or instance count changed")
    return "".join(lines), len(hs)


if __name__ == "__main__":
    if sys.argv[1:2] == ["inventory"]:
        total = 0
        for p in files():
            _, n = convert(p)
            total += n
            print(f"{n:3} {p}")
        print(f"{total} instances convert cleanly (nothing written)")
    else:
        raise SystemExit(__doc__)
