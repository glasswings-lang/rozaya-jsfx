#!/usr/bin/env python3
"""Sustain Looper: 8 sliders -> 30, per docs/layouts/sustain-looper.md.

Per instance: 1-4 unchanged; old 5 (Pitch, semitones) -> 7 with 8 = Semitones;
old 6 (Output) -> 14; old 7 (Voices) -> 12; old 8 (Spread) -> 13. Everything
else is left unstored, so it takes its default.

IDEMPOTENCE: a migrated line stores slider 8 (Transpose unit) as 1 and slider 14
(Output); an old line stores nothing past slider 8, and its slider 8 is Spread
(0-100). A line that already stores slider 14 is skipped.

Dry run by default; --apply writes. Asserts line and instance counts.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

PROJECTS = ["E:/reaper/finished/energy healing vol. 2.RPP"]
N_NEW = 30


def migrate(path, apply_it):
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)
    n_lines = len(lines)
    done = skipped = 0
    for hi in [i for i, l in enumerate(lines) if "sustain_looper.jsfx" in l and "<JS" in l]:
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            t = lines[j].strip()
            if t and (t[0].isdigit() or t[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi + 1}")
        old = parse_line(lines[vi])
        if old.get(14) is not None:
            skipped += 1
            continue
        new = {1: old.get(1), 2: old.get(2), 3: old.get(3), 4: old.get(4),
               7: old.get(5) if old.get(5) is not None else "0", 8: "1",
               12: old.get(7), 13: old.get(8), 14: old.get(6)}
        new_line = render_line(lines[vi], new, n_sliders=N_NEW)
        print(f"  line {vi + 1}: {lines[vi].strip()[:60]}")
        print(f"       -> {new_line.strip()[:60]}")
        if apply_it:
            lines[vi] = new_line
        done += 1
    assert len(lines) == n_lines
    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("--")] or PROJECTS
    for ps in paths:
        p = Path(ps)
        d, s = migrate(p, apply_it)
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d} (already done {s})  {p.name}")


if __name__ == "__main__":
    main()
