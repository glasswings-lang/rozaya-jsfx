#!/usr/bin/env python3
"""Give Bubbler the R22 block, in the SHIFT form Rozaya designed 2026-09-09.

`Transpose (semitones)` at slider 4 becomes seven controls in the same place --
Source note, Target note, value, unit, fine tune, fine tune unit, tuning
reference -- and everything from old slider 5 up moves up by six. 31 -> 37.

Rozaya's design, and the part that matters: **Source note defaults to `None`,
which is what every saved project gets.** With it at None the semitone value is
the control and behaves exactly as the old slider did. The note names only come
alive once you tell the plugin where zero is, because a plugin that did not make
the audio cannot know that by itself.

Per instance: the stored semitone number moves into `Transpose value`, the unit
is written as Semitones, and everything else takes its default. Nothing changes
meaning, and the render has to prove it.

IDEMPOTENCE: slider 7 is `Bubble length (ms)`, minimum 5, before the migration,
and `Transpose unit`, maximum 2, after it. So a value of 2 or less at slider 7
means the work is done. Verified against all 10 instances, which hold 1000 and 50.
"""
import sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

FIRST, LAST, SHIFT, N_NEW = 5, 31, 6, 37
PROJECTS = ["E:/reaper/finished/birdsong-2.RPP",
            "E:/reaper/finished/birdsong.RPP",
            "E:/reaper/finished/the-sound-of-a-drain.RPP"]


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    done = skipped = 0
    for hi in reversed([i for i, l in enumerate(lines) if "bubbler.jsfx" in l]):
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            t = lines[j].strip()
            if t and (t[0].isdigit() or t[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi+1}")

        slots = parse_line(lines[vi])
        s7 = slots.get(7)
        if s7 not in (None, "-") and float(s7) <= 2:
            skipped += 1
            continue

        tok = slots.get(4)
        for sid in range(LAST, FIRST - 1, -1):
            slots[sid + SHIFT] = slots.get(sid)
        slots[4] = "0"                                   # Source note = None
        slots[5] = "60"                                  # Target note, inert
        slots[6] = tok if tok not in (None, "-") else "12"   # the semitone shift
        slots[7] = "1"                                   # unit = Semitones
        slots[8] = "0"                                   # Fine tune
        slots[9] = "2"                                   # Fine tune unit = Cents
        slots[10] = "440"                                # Tuning reference
        new_line = render_line(lines[vi], slots, n_sliders=N_NEW)
        if apply_it:
            lines[vi] = new_line
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    bak = Path("E:/reaper/finished/backups/snapshots/_pre-bubbler-transpose-20260909")
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
