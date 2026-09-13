#!/usr/bin/env python3
"""Spectral Vowel Morpher, the pitch layout: 51 sliders -> 64, in ONE migration.
docs/layouts/spectral-vowel-morpher.md, "THE PITCH LAYOUT".

The slider line only. Old positions move by the AUTHORED map below (the same map
tools/jsfx_renumber.py applied to the source); every new control is seeded to what
reproduces the old sound. The blob is not touched: the plugin remaps its own.

Built in stages; the live projects are migrated ONCE, when every stage is in.
  stage 1  renumber, seed the 13 new controls, Capture average 1-6     (built)

    python tools/morpher_migrate_20260913.py inventory
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line, render_line, as_float

FX = "spectral_vowel_morpher.jsfx"
LIVE = "E:/reaper"
# Scope, 2026-09-13: every saved copy outside a backup. One project lives outside E:/reaper.
EXTRA = ["C:/Users/solst/Dropbox/quick one.RPP"]
N_OLD, N_NEW = 51, 64

# old id -> new id, the layout doc's table, and the map jsfx_renumber applied to src.
MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 9, 9: 8, 10: 10, 11: 11, 12: 12,
       13: 17, 14: 22, 15: 23, 16: 24, 17: 25, 18: 26, 19: 27, 20: 28, 21: 29, 22: 30,
       23: 35, 24: 36, 25: 31, 26: 37, 27: 38, 28: 39, 29: 40, 30: 41, 31: 42, 32: 43,
       33: 44, 34: 45, 35: 46, 36: 47, 37: 48, 38: 50, 39: 51, 40: 52, 41: 53, 42: 54,
       43: 55, 44: 56, 45: 57, 46: 59, 47: 60, 48: 61, 49: 62, 50: 63, 51: 64}

# new id -> the value that reproduces the old sound.
SEEDS = {13: "0",           # Source note None: nothing is measured from it
         14: "0", 15: "2",  # Source fine tune 0, in Cents
         16: "60",          # Target note, inert while Source note is None
         18: "1",           # Transpose unit Semitones: what Pitch (semitones) meant
         19: "0", 20: "2",  # Fine tune 0, in Cents
         21: "440",         # Tuning reference
         32: "1",           # Layer pitch unit Semitones: what Layer pitch (semitones) meant
         33: "0", 34: "2",  # Layer fine tune 0, in Cents
         49: "0",           # Drift amount unit: Target default
         58: "0"}           # Ramp by unit: Target default


# The old Layer selector's pitch ladder, by index: 4 octaves down ... 4 octaves up, the
# Original at 6, then Custom 1-3 at 13-15.
LADDER_SEMIS = [-48, -36, -24, -12, -7, -5, 0, 5, 7, 12, 24, 36, 48]
# Ladder index -> the new selector value (0 is All): the Original is Layer 1, the six below
# it Layers 2-7, the six above it Layers 8-13, Custom 1-3 Layers 14-16.
LADDER_TO_LAYER = {i: (1 if i == 6 else i + 2 if i < 6 else i + 1) for i in range(16)}


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
    return sorted(out) + EXTRA


def heads(lines):
    return [i for i, l in enumerate(lines) if "<JS " in l and "<JS_SER" not in l and FX in l]


def stored_ids(line):
    return sorted(k for k, v in parse_line(line).items() if v is not None)


# Drift period unit (39) and Ramp time unit (46) were left ABSENT by the 2026-09-06
# migration, so REAPER supplies their declared defaults, Seconds and Minutes -- read
# 2026-09-13 on purr.RPP. An absent value moves as absent (to 51 and 59), and those two
# declarations keep their defaults, so each goes on meaning what it meant.
MAY_BE_ABSENT = {39, 46}


def is_51(line):
    s = stored_ids(line)
    return max(s, default=0) == N_OLD and set(range(1, N_OLD + 1)) - set(s) <= MAY_BE_ABSENT


def remap_line(line, where):
    slots = parse_line(line)
    if not is_51(line):
        refuse(where, f"not a whole {N_OLD}-slider line")
    new = {MAP[k]: slots[k] for k in range(1, N_OLD + 1)}
    # Capture average: the control becomes 1-6, which is all the analysis ever used.
    ca = as_float(new[4], "Capture average")
    if not 1 <= ca <= 6:
        refuse(where, f"Capture average {new[4]!r} is outside 1-6")
    # Stage 3, sixteen pitched layers: Layer held an index into the old pitch ladder; it is
    # {All, Layer 1 ... Layer 16} now, Layer 1 the Original. The pitch shown is the chosen
    # layer's own: a Custom layer's saved value, otherwise the ladder interval it played.
    old_lay = as_float(new[29], "Layer")
    if old_lay != int(old_lay) or not 0 <= old_lay <= 15:
        refuse(where, f"Layer {new[29]!r} is not a whole ladder index 0-15")
    new[29] = str(LADDER_TO_LAYER[int(old_lay)])
    if int(old_lay) < 13:
        new[31] = str(LADDER_SEMIS[int(old_lay)])
    for k, v in SEEDS.items():
        if k in new:
            refuse(where, f"seed {k} collides with a moved value")
        new[k] = v
    if sorted(new) != list(range(1, N_NEW + 1)):
        refuse(where, f"the new line does not cover 1..{N_NEW} exactly")
    return render_line(line, new, N_NEW)


def convert(path):
    text = open(path, encoding="utf-8", errors="surrogateescape", newline="").read()
    lines = text.splitlines(keepends=True)
    n_lines, hs = len(lines), heads(lines)
    if not hs:
        refuse(path, "no Morpher instance")
    for hi in hs:
        lines[hi + 1] = remap_line(lines[hi + 1], f"{path} line {hi + 2}")
    if len(lines) != n_lines or len(heads(lines)) != len(hs):
        refuse(path, "line or instance count changed")
    return "".join(lines), len(hs)


def is_current_layout(path):
    """True when every Morpher line in the file holds the 51-slider layout."""
    lines = open(path, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    return all(is_51(lines[h + 1]) for h in heads(lines))


if __name__ == "__main__":
    if sys.argv[1:2] == ["inventory"]:
        total = 0
        for p in files():
            if not is_current_layout(p):
                print(f"  - {p}: NOT the 51-slider layout (handled in the live-migration stage)")
                continue
            _, n = convert(p)
            total += n
            print(f"{n:3} {p}")
        print(f"{total} instances convert cleanly (nothing written)")
    else:
        raise SystemExit(__doc__)
