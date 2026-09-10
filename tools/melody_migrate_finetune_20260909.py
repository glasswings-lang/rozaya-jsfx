#!/usr/bin/env python3
"""Give Melody Phase a per-voice fine tune, and one unit control for all eight.

Rozaya, 2026-09-09, on being told the plan required a voice selector first:
*"Why would a voice need a block each?"* It doesn't. A voice needs its NOTE,
which it already has, plus a fine offset. Mode and tuning reference are
properties of the PLUGIN, not of a voice.

So: `Fine tune unit` {Hz, Semitones, Cents} at slider 6 beside the tuning
reference, and `Vn Fine tune` after each `Vn Note`. Nine controls added, not
thirty-two, and **no voice selector**. 87 sliders -> 96.

Cents is the default because it is what microtonal music speaks: 100 cents is a
semitone at every pitch, a quarter tone is 50, the syntonic comma is 21.5, and a
trained ear resolves about 5. Measured: 1200 cents renders bit-identical to
raising the note by 12.

Every fine tune defaults to 0, so a migrated project sounds exactly as it did.
"""
import sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

MAX_OLD, N_NEW = 87, 96
INSERTED = {6, 28, 34, 40, 46, 52, 58, 64, 70}      # in the NEW numbering
PROJECTS = ["E:/reaper/finished/melodic.RPP", "E:/reaper/finished/outcoming.RPP",
            "E:/reaper/finished/slow-summer.RPP", "E:/reaper/finished/upswing.RPP",
            "E:/reaper/to-play-with-later/simple-sequence-check.RPP",
            "E:/reaper/to-play-with-later/simple-sequence.RPP",
            "E:/reaper/to-play-with-later/testing-proof of concept.RPP"]

# old -> new, derived by walking the new list and skipping what was inserted
MAP, nxt = {}, 1
for old in range(1, MAX_OLD + 1):
    while nxt in INSERTED:
        nxt += 1
    MAP[old] = nxt
    nxt += 1
assert MAP[26] == 27 and MAP[31] == 33 and MAP[61] == 69 and MAP[MAX_OLD] == N_NEW, MAP


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    done = skipped = 0
    for hi in reversed([i for i, l in enumerate(lines) if "melody_phase.jsfx" in l]):
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            t = lines[j].strip()
            if t and (t[0].isdigit() or t[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi+1}")

        # Melody declares more than 64 sliders, so the line carries the `""`
        # marker and its token count tracks the slider count exactly.
        n = len(lines[vi].strip().split())
        expected_old = 64 + 1 + (MAX_OLD - 64)
        if n == expected_old + (N_NEW - MAX_OLD):
            skipped += 1
            continue
        if n != expected_old:
            raise RuntimeError(f"{path}: value line has {n} tokens, expected {expected_old}")

        old = parse_line(lines[vi])
        new = {MAP[o]: old.get(o) for o in range(1, MAX_OLD + 1)}
        new[6] = "2"                       # Fine tune unit = Cents
        for sid in (28, 34, 40, 46, 52, 58, 64, 70):
            new[sid] = "0"                 # every fine tune starts at no change
        new_line = render_line(lines[vi], new, n_sliders=N_NEW)
        if apply_it:
            lines[vi] = new_line
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    bak = Path("E:/reaper/finished/backups/snapshots/_pre-melody-finetune-20260909")
    for ps in PROJECTS:
        p = Path(ps)
        if not p.exists():
            print(f"MISSING {p}")
            continue
        if apply_it:
            bak.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bak / (p.parent.name + "__" + p.name))
        d, s = migrate(p, apply_it)
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d:>2} (done {s})  {p.name}")


if __name__ == "__main__":
    main()
