#!/usr/bin/env python3
"""Give Womb v3 the R22 blocks -- four of them, replicated in place.

Rozaya, 2026-09-09: *"womb is 3-layered. just replicate the block where it needs
to be lol"*. S1 and S2 pitch stay in the heartbeat group beside their own decay
and volume; Inhale and Exhale pitch stay in the breath group. One shared
`Tuning reference (Hz)` sits with the master controls. 71 sliders -> 88.

Keeping the blocks in place is what makes this line-only: with a selector the
frequencies would have to live in the blob, and Womb's eight instances carry
three formats between them, one of which the plugin does not even read.

Seven of the eight projects render bit-identical. `to-sleep-within` does not, and
the reason is NOT this change -- see `docs/history/R22.md`. That instance's blob
is magic 5, a format the plugin does not read, so its per-target drift memory
comes up empty at @init and the visible controls are then filled from that empty
memory, wiping the drift the project file still holds. Rozaya, having opened it:
*"The sliders are reporting that there was no drift."* Its drift was already dead
before this work, and whether it survives a load depends on the order @slider and
@serialize happen to run in -- so ANY change to @slider tips it.

Snapshot for reverting: `_pre-womb-pitch-20260909/`.
"""
import sys, shutil, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

N_NEW = 88
PROJECTS = ["E:/reaper/finished/back-to-life.RPP", "E:/reaper/finished/deep-night.RPP",
            "E:/reaper/finished/to-sleep-within.RPP", "E:/reaper/to-play-with-later/micle.RPP",
            "E:/reaper/to-play-with-later/noisescape-august-18-2026.RPP",
            "E:/reaper/to-play-with-later/surges.RPP",
            "E:/reaper/to-play-with-later/womb-and-baby-heartbeats-with-bloodflow.RPP",
            "E:/reaper/to-play-with-later/womb-bubbles-proto.RPP"]

MOVES = ([(n, n) for n in range(1, 6)] +
         [(n, n + 4) for n in (7, 8)] +
         [(n, n + 8) for n in range(10, 22)] +
         [(n, n + 16) for n in range(24, 47)] +
         [(n, n + 17) for n in range(47, 72)])
FREQS = {6: (6, 7, 8, 9, 10, 45.0),
         9: (13, 14, 15, 16, 17, 120.0),
         22: (30, 31, 32, 33, 34, 250.0),
         23: (35, 36, 37, 38, 39, 170.0)}
TUNING_REF_SLIDER = 63


def nearest(hz):
    return max(0, min(127, int(round(69 + 12 * math.log2(hz / 440.0))))) if hz > 0 else 60


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    done = skipped = 0
    for hi in reversed([i for i, l in enumerate(lines) if "womb_sound_generator_v3.jsfx" in l]):
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            t = lines[j].strip()
            if t and (t[0].isdigit() or t[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi+1}")

        old = parse_line(lines[vi])
        s6 = old.get(6)      # `S1 Frequency Hz` (>= 20) before, `S1 pitch mode` (<= 2) after
        if s6 not in (None, "-") and float(s6) <= 2:
            skipped += 1
            continue

        new = {}
        for a, b in MOVES:
            new[b] = old.get(a)
        for src, (m, note, val, fine, fmod, default) in FREQS.items():
            tok = old.get(src)
            hz = float(tok) if tok not in (None, "-") else default
            new[m] = "0"
            new[note] = str(nearest(hz))
            new[val] = tok if tok not in (None, "-") else ("%g" % default)
            new[fine] = "0"
            new[fmod] = "2"
        new[TUNING_REF_SLIDER] = "440"

        new_line = render_line(lines[vi], new, n_sliders=N_NEW)
        if apply_it:
            lines[vi] = new_line
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    bak = Path("E:/reaper/finished/backups/snapshots/_pre-womb-pitch-20260909")
    for ps in PROJECTS:
        p = Path(ps)
        if not p.exists():
            print(f"MISSING {p}")
            continue
        if apply_it and not (bak / (p.parent.name + "__" + p.name)).exists():
            bak.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bak / (p.parent.name + "__" + p.name))
        d, s = migrate(p, apply_it)
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d} (done {s})  {p.name}")


if __name__ == "__main__":
    main()
