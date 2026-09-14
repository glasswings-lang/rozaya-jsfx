#!/usr/bin/env python3
"""Spectral Vowel Morpher, the pitch layout: 51 sliders -> 64, in ONE migration.
docs/history/layouts/spectral-vowel-morpher.md, "THE PITCH LAYOUT".

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
MAY_STAY_ABSENT = {51, 59}   # the same two, where they sit now


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
    # Stage 4, the 87-target list: Drift target (46) and Ramp target (56) held an index into
    # the 55-target list of 2026-09-11; each moves to where that target sits now. The plugin's
    # t55_o2n() is the same table.
    def t55(o):
        if o <= 5:
            return o                                    # Morph .. Pitch, now Transpose
        if o <= 12:
            return o + 2                                # Stereo width .. Overtone width
        if o == 13:
            return 49                                   # Layer level (all layers)
        if o <= 29:
            return 50 + LADDER_TO_LAYER[o - 14] - 1     # a ladder layer's level
        if o == 30:
            return 15                                   # Layer pitch (all Custom layers) -> (all layers)
        if o <= 33:
            return 16 + 13 + (o - 31)                   # Custom 1-3 pitch -> Layer 14-16 pitch
        if o == 34:
            return 66                                   # Layer overtone harmonic (all layers)
        if o <= 50:
            return 67 + LADDER_TO_LAYER[o - 35] - 1     # a ladder layer's overtone harmonic
        return o + 32                                   # Input level .. Rest for
    for k in (46, 56):
        old_t = as_float(new[k], f"slider {k}")
        if old_t != int(old_t) or not 0 <= old_t <= 54:
            refuse(where, f"slider {k} {new[k]!r} is not a whole target 0-54")
        new[k] = str(t55(int(old_t)))
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
        where = f"{path} line {hi + 2}"
        lines[hi + 1] = remap_31(lines[hi + 1], where) if is_31(lines[hi + 1]) else remap_line(lines[hi + 1], where)
    if len(lines) != n_lines or len(heads(lines)) != len(hs):
        refuse(path, "line or instance count changed")
    return "".join(lines), len(hs)


# --- quick one.RPP: 12 copies saved 2026-08-14 on the layout of 409b1ba (2026-08-11), 31
# sliders and a 7700002 blob, never carried through a migration since. Mapped straight to the
# new layout BY NAME from 409b1ba's declarations; every control added since takes the value it
# was given when it arrived (its declared default then, which is what these copies would have
# read), and each of those is also this layout's seed. Verified by reading every control back.
N_31 = 31
Q31 = {1: 1,     # Capture slot (0-7 then; +1 below, for All)
       2: 2,     # Capture spectrum -> Capture now
       3: 3,     # Capture point
       4: 39,    # Input level (dry, dB)
       5: 40,    # Voice level (dB) -> Output level
       6: 10,    # Texture
       7: 11,    # Wash grain (ms)
       8: 12,    # Spread (Hz)
       9: 17,    # Pitch (semitones) -> Transpose value, Semitones
       10: 22,   # Stereo width
       11: 24,   # Low cut (Hz)
       12: 23,   # Denoise
       13: 5,    # Audition
       14: 6,    # Morph
       15: 7,    # Auto-morph
       16: 8,    # Auto-morph time (sec) -> Auto-morph time, Rate mode Seconds
       17: 46,   # Drift target (7-target list, remapped below)
       18: 47,   # Drift up amount
       19: 48,   # Drift down amount
       20: 50,   # Drift period (seconds) -> Drift period, unit Seconds
       21: 52,   # Drift shape
       22: 55,   # Drift restart
       23: 56,   # Ramp target (7-target list, remapped below)
       24: 57,   # Ramp by
       25: 60,   # Ramp duration (minutes) -> Ramp duration, unit Minutes
       26: 64,   # Ramp start delay (minutes)
       27: 63,   # Ramp engage
       28: 4,    # Capture average
       29: 26,   # Overtone harmonic
       30: 27,   # Overtone lift
       31: 28}   # Overtone width
# 409b1ba's 7-target list {Texture, Spread, Pitch, Stereo width, Low cut, Voice level, Overtone
# harmonic} -> the 87-target list.
T7 = {0: 2, 1: 4, 2: 5, 3: 8, 4: 10, 5: 84, 6: 12}
Q31_SEEDS = dict(SEEDS)
Q31_SEEDS.update({9: "1",       # Rate mode Seconds: what Auto-morph time (sec) meant
                  25: "20000",  # High cut off
                  29: "1",      # Layer 1, the Original, where the selector arrived
                  30: "1", 31: "0", 35: "0", 36: "0", 37: "0", 38: "-1",   # Layer 1 as it arrived
                  41: "0", 42: "0", 43: "0", 44: "0", 45: "0",             # transport off
                  51: "1",      # Drift period unit Seconds: what Drift period (seconds) meant
                  53: "0", 54: "0",
                  59: "2",      # Ramp time unit Minutes: what Ramp duration (minutes) meant
                  61: "0", 62: "0"})


def is_31(line):
    return stored_ids(line) == list(range(1, N_31 + 1))


def remap_31(line, where):
    slots = parse_line(line)
    if not is_31(line):
        refuse(where, f"not a whole {N_31}-slider line")
    new = {Q31[k]: slots[k] for k in range(1, N_31 + 1)}
    cs = as_float(new[1], "Capture slot")
    if cs != int(cs) or not 0 <= cs <= 7:
        refuse(where, f"Capture slot {new[1]!r} is not a whole slot 0-7")
    new[1] = str(int(cs) + 1)
    ca = as_float(new[4], "Capture average")
    if not 1 <= ca <= 6:
        refuse(where, f"Capture average {new[4]!r} is outside 1-6")
    for k in (46, 56):
        old_t = as_float(new[k], f"slider {k}")
        if old_t != int(old_t) or int(old_t) not in T7:
            refuse(where, f"slider {k} {new[k]!r} is not a whole 7-target index")
        new[k] = str(T7[int(old_t)])
    for k, v in Q31_SEEDS.items():
        if k in new:
            refuse(where, f"seed {k} collides with a moved value")
        new[k] = v
    if sorted(new) != list(range(1, N_NEW + 1)):
        refuse(where, f"the new line does not cover 1..{N_NEW} exactly ({sorted(set(range(1, N_NEW + 1)) - set(new))} missing)")
    return render_line(line, new, N_NEW)


# The live write. Every file converts in memory first, so a refusal anywhere writes nothing.
# Each file is copied to the snapshot and compared byte for byte before any file is written.
# After writing, each file is read back: the only lines that changed are the Morpher value
# lines, each now holding exactly 64 values. Any failure puts every file back from the snapshot.
SNAP = "E:/reaper/finished/backups/snapshots/_pre-morpher-pitch-layout-20260913"
EXPECT_FILES, EXPECT_INSTANCES = 40, 135   # counted 2026-09-13


def snap_path(p):
    if p.startswith(LIVE + "/"):
        return f"{SNAP}/{p[len(LIVE) + 1:]}"
    return f"{SNAP}/_outside-E-reaper/{os.path.basename(p)}"


def write_all():
    import shutil
    if os.path.exists(SNAP):
        refuse(SNAP, "the snapshot already exists -- this migration has been run")
    plans = [(p, *convert(p)) for p in files()]
    n_inst = sum(n for _, _, n in plans)
    if (len(plans), n_inst) != (EXPECT_FILES, EXPECT_INSTANCES):
        refuse("inventory", f"{len(plans)} files and {n_inst} instances, expected {EXPECT_FILES} and {EXPECT_INSTANCES}")
    snaps = {}
    for p, _, _ in plans:
        dst = snap_path(p)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        if open(dst, "rb").read() != open(p, "rb").read():
            refuse(dst, "the snapshot copy does not match its project")
        snaps[p] = dst
    try:
        for p, text, _ in plans:
            open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(text)
        for p, text, n in plans:
            new = open(p, encoding="utf-8", errors="surrogateescape", newline="").read()
            old = open(snaps[p], encoding="utf-8", errors="surrogateescape", newline="").read()
            ol, nl = old.splitlines(keepends=True), new.splitlines(keepends=True)
            if new != text or len(ol) != len(nl):
                refuse(p, "read back differently from what was written")
            changed = [i for i in range(len(ol)) if ol[i] != nl[i]]
            if changed != [h + 1 for h in heads(ol)] or len(changed) != n:
                refuse(p, f"changed lines {changed[:5]} are not exactly its {n} Morpher value lines")
            for i in changed:
                s = stored_ids(nl[i])
                # Drift period unit (51) and Ramp time unit (59) may stay absent, as they were.
                if max(s) != N_NEW or set(range(1, N_NEW + 1)) - set(s) - MAY_STAY_ABSENT:
                    refuse(p, f"line {i + 1} does not hold sliders 1..{N_NEW}")
            print(f"{n:3} written and read back  {p}")
    except BaseException:
        for p, dst in snaps.items():
            shutil.copy2(dst, p)
        print("FAILED -- every project put back from the snapshot")
        raise
    print(f"{n_inst} instances in {len(plans)} files migrated; snapshot {SNAP}")


def is_current_layout(path):
    """True when every Morpher line in the file holds the 51-slider layout."""
    lines = open(path, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    return all(is_51(lines[h + 1]) for h in heads(lines))


if __name__ == "__main__":
    if sys.argv[1:2] == ["inventory"]:
        total = files_n = 0
        for p in files():
            _, n = convert(p)
            total += n
            files_n += 1
            print(f"{n:3} {p}{'' if is_current_layout(p) else '   (the 31-slider layout of 2026-08-11)'}")
        print(f"{total} instances in {files_n} files convert cleanly (nothing written)")
    elif sys.argv[1:2] == ["write"]:
        write_all()
    else:
        raise SystemExit(__doc__)
