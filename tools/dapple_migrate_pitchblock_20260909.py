#!/usr/bin/env python3
"""Give Dapple the R22 pitch block, per docs/layouts/dapple.md.

`Pitch (Hz)` at slider 4 becomes six controls in the same place -- mode, note
name, value, fine tune, fine tune unit, tuning reference -- and everything from
old slider 5 up moves up by five. 33 sliders -> 38.

Per instance: the stored frequency moves into `Pitch value`, the mode is written
as Hz (0), which is what that frequency has always meant, and the note name is
seeded to the nearest note so it reads sensibly the moment anyone switches to
Semitones. Nothing changes meaning, and the render has to prove it.

IDEMPOTENCE: slider 6 is `Resonance (noise voice)` before the migration, capped
at 0.97, and `Pitch value` after it, never below 40. So a value above 1 at
slider 6 means the work is already done. Verified against all 14 instances,
which store 0.85 and 0.
"""
import sys, shutil, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

FIRST, LAST, SHIFT = 5, 33, 5
N_NEW = 38
PROJECTS = ["E:/reaper/finished/bubbles.RPP",
            "E:/reaper/to-play-with-later/womb-bubbles-proto.RPP"]


def nearest_note(hz):
    if hz <= 0:
        return 60
    n = 69 + 12 * math.log2(hz / 440.0)
    return max(0, min(127, int(round(n))))


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    done = skipped = 0
    for hi in reversed([i for i, l in enumerate(lines) if "dapple.jsfx" in l]):
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            t = lines[j].strip()
            if t and (t[0].isdigit() or t[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi+1}")

        slots = parse_line(lines[vi])
        s6 = slots.get(6)
        if s6 not in (None, "-") and float(s6) > 1:
            skipped += 1
            continue

        tok = slots.get(4)
        hz = float(tok) if tok not in (None, "-") else 150.0

        for sid in range(LAST, FIRST - 1, -1):
            slots[sid + SHIFT] = slots.get(sid)
        slots[4] = "0"                       # Pitch mode = Hz
        slots[5] = str(nearest_note(hz))     # Note name, seeded
        slots[6] = tok if tok not in (None, "-") else "150"
        slots[7] = "0"                       # Fine tune
        slots[8] = "2"                       # Fine tune unit = Cents
        slots[9] = "440"                     # Tuning reference
        new_line = render_line(lines[vi], slots, n_sliders=N_NEW)
        if apply_it:
            lines[vi] = new_line
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    bak = Path("E:/reaper/finished/backups/snapshots/_pre-dapple-pitch-20260909")
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
