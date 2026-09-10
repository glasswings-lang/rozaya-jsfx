#!/usr/bin/env python3
"""Polyrhythm Phase v3: 56 sliders -> 59, per docs/layouts/polyrhythm-phase-v3-r22-r24.md.

Slider line only. The blob migrates itself inside the plugin (magic 2200024 read
at 24 targets wide, remapped to 88, each voice's note + 36).

Per instance: every slider moves to its new number; Pitch mode (16) is written as
Semitones and Fine tune unit (20) as Cents; the visible voice's note index k
(C2..C6) becomes MIDI note k + 36 in both Note name (17) and Pitch value (18),
or stays unstored if it was unstored (the new default 60 is the old default
24 + 36); Fine tune moves 17 -> 19 unchanged; the Drift and Ramp target
selectors are remapped through the target table.

IDEMPOTENCE: a migrated line stores slider 57+; an old line has 56 sliders.
Lines storing anything above 56 are skipped.

Dry run by default; --apply writes. Paths may be given; otherwise every
non-backup project under E:/reaper holding polyrhythm_phase_v3.jsfx.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line, fmt, as_float

N_OLD, N_NEW = 56, 59


def old_to_new_slider(n):
    if 1 <= n <= 15: return n
    if n == 16: return 17
    if n == 17: return 19
    if 18 <= n <= 56: return n + 3
    raise ValueError(n)


def old_to_new_target(t):
    if t == 0: return 0
    if 1 <= t <= 8: return 27 + t
    if t == 9: return 82
    if t == 10: return 83
    if t == 11: return 3
    if t == 12: return 45
    if 13 <= t <= 20: return 60 + t
    return {21: 36, 22: 54, 23: 63}[t]


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    n_lines = len(lines)
    done = skipped = 0
    for hi in [i for i, l in enumerate(lines) if "polyrhythm_phase_v3.jsfx" in l and "<JS" in l]:
        vi = hi + 1
        if not lines[vi].strip() or not (lines[vi].strip()[0].isdigit() or lines[vi].strip()[0] in '-"'):
            raise RuntimeError(f"{path}: no value line directly under <JS> at line {hi + 1}")
        old = parse_line(lines[vi])
        if any(k > N_OLD and v is not None for k, v in old.items()):
            skipped += 1
            continue
        new = {}
        for n in range(1, N_OLD + 1):
            if old.get(n) is not None:
                new[old_to_new_slider(n)] = old[n]
        new[16] = "1"
        new[20] = "2"
        tok = old.get(16)
        if tok is not None:
            midi = as_float(tok, "Note") + 36
            assert 36 <= midi <= 84, (path, midi)
            new[17] = fmt(midi)
            new[18] = fmt(midi)
        for old_sel, new_sel in ((41, 44), (49, 52)):
            tok = old.get(old_sel)
            if tok is not None:
                new[new_sel] = str(old_to_new_target(int(as_float(tok, "target"))))
        assert all(1 <= k <= N_NEW for k in new)
        new_line = render_line(lines[vi], new, n_sliders=N_NEW)
        if apply_it:
            lines[vi] = new_line
        done += 1
    assert len(lines) == n_lines
    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        paths = [str(p) for p in Path("E:/reaper").rglob("*.RPP")
                 if "backups" not in p.parts
                 and "polyrhythm_phase_v3.jsfx" in p.read_text(encoding="utf-8", errors="replace")]
    total = 0
    for ps in sorted(paths):
        d, s = migrate(Path(ps), apply_it)
        total += d
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d:>2} (already done {s})  {ps}")
    print(f"total instances: {total}")


if __name__ == "__main__":
    main()
