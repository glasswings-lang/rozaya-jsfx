#!/usr/bin/env python3
"""Migrate every Sweeping Filter to the 54-control layout of
docs/layouts/sweeping-filter-r22-r24.md: two pitch blocks, Tuning reference at
11, and 17 drift/ramp targets.

EVERY TABLE HERE IS AUTHORED, transcribed from that document. Which layout each
file holds is authored too, per file -- never inferred from a value count,
because Rozaya's migrated copy of organic-movement and Tensor's original both
hold 23-ish values and mean different things.

IDEMPOTENT BY CONSTRUCTION: reads the SNAPSHOT, writes the live project.
    python tools/swf_migrate_r22_20260910.py            # dry run
    python tools/swf_migrate_r22_20260910.py --apply
"""
import cmath, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = "E:/reaper/finished/backups/snapshots/_pre-swf-r22-20260910"
NEW_N = 54

# --- AUTHORED: which layout each snapshot file holds -----------------------
L45, AE4A655, D19873F = "45 (2026-09-05)", "23 (ae4a655, April)", "22 (d19873f, first release)"
FILE_LAYOUT = {
    "reaper__finished__bilateral-healing-1.RPP": L45,
    "reaper__finished__bilateral-support.RPP": L45,
    "reaper__finished__bilateral-with-binaurals.RPP": L45,
    "reaper__finished__infantile.RPP": L45,
    "reaper__finished__life-is-worth-it.RPP": L45,
    "reaper__finished__strangeness.RPP": L45,
    "reaper__finished__the-sound-of-a-drain.RPP": L45,
    "reaper__to-play-with-later__as-things-are.RPP": L45,
    "reaper__to-play-with-later__noisescape-august-18-2026.RPP": L45,
    "reaper__to-play-with-later__organic-movement.RPP": L45,
    "reaper__to-play-with-later__womb-and-baby-heartbeats-with-bloodflow.RPP": L45,
    "tensors-rpp-projects__organic-movement.RPP": AE4A655,
    "tensors-rpp-projects__shepard.RPP": D19873F,
    "tensors-rpp-projects__singing-bowl.RPP": D19873F,
}
LIVE_DIR = {"reaper": "E:/reaper", "tensors-rpp-projects": "E:/tensor's-rpp-projects"}

# --- AUTHORED: Tensor's old layouts -> the 45 layout, by control -----------
TO45 = {
    AE4A655: {1: 1, 2: 2, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9, 8: 10, 9: 12, 10: 11, 11: 13,
              12: 3, 13: 14, 14: 15, 15: 24, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20,
              21: 21, 22: 22, 23: 23},
    D19873F: {1: 1, 2: 2, 3: 5, 4: 6, 5: 8, 6: 9, 7: 10, 8: 12, 9: 11, 10: 13,
              11: 3, 12: 14, 13: 15, 14: 24, 15: 16, 16: 17, 17: 18, 18: 19, 19: 20,
              20: 21, 21: 22, 22: 23},
}
# Old declared ranges, keyed by 45-layout id, for refusing a value that does not
# belong to the layout claimed.
OLD_RANGE = {1: (20, 20000), 2: (20, 20000), 3: (0, 1), 5: (0.001, 1000), 6: (0, 2),
             7: (-180, 180), 8: (0, 100), 9: (0, 100), 10: (0, 100), 11: (0, 3),
             12: (0, 100), 13: (0, 3), 14: (-180, 180), 15: (0, 1), 16: (0, 1),
             17: (0, 12), 18: (0, 1), 19: (0, 100), 20: (2, 32), 21: (0.001, 1000),
             22: (0, 2), 23: (0.125, 8), 24: (0, 1)}
INTEGER_45 = {6, 11, 13, 15, 16, 17, 20, 22}
# {Hz, Seconds, BPM} -> {BPM, Seconds, Hz, ...}: rate mode (6) and pan unit (22).
UNIT_REORDER = {"0": "2", "1": "1", "2": "0"}

# --- AUTHORED: the 45 layout -> the 54 layout ------------------------------
def to54(o):
    return {1: 3, 2: 8}.get(o, o + 9 if 3 <= o <= 45 else None)

TARGET_REMAP = {"0": "6", "1": "0", "2": "2", "3": "14", "4": "5", "5": "16"}
TARGET_SLIDERS_54 = (39, 47)
NEW_DEFAULTS = {1: "0", 2: "71", 4: "0", 5: "2", 6: "0", 7: "111", 9: "0", 10: "2", 11: "440"}

# --- The retired Kellett core, matched by its PEAK: the FINAL version of
#     sweepfilter_migrate_hz.py (bf81d1d), which rewrote every E:/reaper project
#     on 2026-08-22 -- frequencies AND Resonance. Loaded from git rather than
#     retyped, so the maths is the maths that ran. The first version (ce3f391)
#     matched the corner and kept Resonance; using it here gave Tensor's second
#     organic-movement filter 466 Hz where Rozaya's migrated copy of the same
#     project holds 291 Hz and Resonance 0.223. That copy is the reference.
import subprocess
_hz = {}
exec(subprocess.run(["git", "show", "bf81d1d:tools/sweepfilter_migrate_hz.py"],
                    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    capture_output=True, text=True, check=True).stdout.replace(
                    'if __name__ == "__main__":', "if False:"), _hz)
hz_match = _hz["match"]      # (fc, res) -> (new fc, new resonance)


def refuse(where, why):
    raise SystemExit(f"{where}: {why} -- refusing")


def tensor_to45(real, layout, where):
    table = TO45[layout]
    if max(real) > max(table):
        refuse(where, f"real value at slider {max(real)}, beyond the {layout} layout")
    out = {}
    for o, tok in real.items():
        n = table[o]
        v = float(tok)
        lo, hi = OLD_RANGE[n]
        if not lo <= v <= hi or (n in INTEGER_45 and v != int(v)):
            refuse(where, f"old slider {o} holds {tok}, outside {layout} slider's range")
        out[n] = tok
    for n in (6, 22):
        out[n] = UNIT_REORDER[str(int(float(out[n])))]
    out[23] = "%g" % (1.0 / float(out[23]))
    # Exactly as bf81d1d's rewrite(): both ends matched at the OLD Resonance, the
    # new Resonance taken from the low end, formatted the way it formatted them.
    res = float(out[3])
    new_lo, new_res = hz_match(float(out[1]), res)
    new_hi, _ = hz_match(float(out[2]), res)
    out[1], out[2] = str(int(round(new_lo))), str(int(round(new_hi)))
    out[3] = "%.3f" % new_res
    return out


def convert(path_in, layout, dry):
    text = open(path_in, "rb").read().decode("utf-8")
    lines = text.splitlines(keepends=True)
    n_before, count, notes = len(lines), 0, []
    for i, line in enumerate(lines):
        if not re.search(r"<JS\s+\S*?full-feature-sweeping-filter\.jsfx", line, re.I):
            continue
        vi, where = i + 1, f"{os.path.basename(path_in)} line {i + 2}"
        orig = lines[vi]
        real = {k: v for k, v in parse_line(orig).items() if v not in (None, "-")}
        if not real:
            refuse(where, "no values at all")
        if any(t.startswith('"') for t in real.values()):
            refuse(where, "a quoted token")
        if layout == L45:
            if max(real) > 45:
                refuse(where, f"real value at slider {max(real)}, above 45")
            s45 = real
        else:
            s45 = tensor_to45(real, layout, where)
        new = {to54(o): tok for o, tok in s45.items()}
        for s in TARGET_SLIDERS_54:
            if s in new:
                if new[s] not in TARGET_REMAP and str(int(float(new[s]))) not in TARGET_REMAP:
                    refuse(where, f"target selector {s} holds {new[s]}")
                new[s] = TARGET_REMAP[str(int(float(new[s])))]
        for s, tok in NEW_DEFAULTS.items():
            if s in new:
                refuse(where, f"new slot {s} already occupied")
            new[s] = tok
        rendered = render_line(orig, new, NEW_N)
        back = parse_line(rendered)
        for s, tok in new.items():
            if back.get(s) != tok:
                refuse(where, f"slider {s} rendered as {back.get(s)!r}, wanted {tok!r}")
        lines[vi] = rendered
        count += 1
        notes.append(f"   {where}: {layout}, {len(real)} values -> Low {new[3]} Hz, High {new[8]} Hz")
    if len(lines) != n_before:
        refuse(path_in, "line count changed")
    return "".join(lines), count, notes


def main():
    dry = "--apply" not in sys.argv
    snaps = sorted(os.listdir(SNAP))
    if set(snaps) != set(FILE_LAYOUT):
        raise SystemExit(f"snapshot holds {sorted(set(snaps) ^ set(FILE_LAYOUT))} "
                         "that the authored list does not -- refusing")
    total = 0
    for name in snaps:
        parts = name.split("__")
        live = "/".join([LIVE_DIR[parts[0]]] + parts[1:])
        if not os.path.exists(live):
            raise SystemExit(f"live project missing: {live}")
        out, n, notes = convert(os.path.join(SNAP, name), FILE_LAYOUT[name], dry)
        total += n
        print(f"{live}  {n} instance(s)")
        print("\n".join(notes))
        if not dry:
            open(live, "w", encoding="utf-8", newline="").write(out)
    print(f"\n{'WOULD MIGRATE' if dry else 'MIGRATED'} {total} instances in {len(snaps)} projects")
    if dry:
        print("re-run with --apply to write")


if __name__ == "__main__":
    main()
