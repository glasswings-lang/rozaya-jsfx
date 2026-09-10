#!/usr/bin/env python3
"""Melody Phase: 96 sliders -> 105, per docs/layouts/melody-phase-r22-r24.md.

Slider line only. The blob migrates itself inside the plugin (old magic read at
28 targets wide, remapped to 55).

Per instance: every slider moves to its new number; Pitch mode (5) is written
as Semitones; each voice's note index k (C2..C6) becomes MIDI note k + 36 in
both its Note and its Pitch slider, or stays unstored if it was unstored (the
new defaults are the old defaults + 36); the Drift and Ramp target selectors are
remapped through the target table.

IDEMPOTENCE: a migrated line stores slider 105; an old line has 96 sliders at
most. Lines storing anything above 96 are skipped.

Dry run by default; --apply writes. Paths may be given; otherwise every
non-backup project under E:/reaper holding melody_phase.jsfx.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line, fmt, as_float

N_NEW = 105


def old_to_new_slider(n):
    if n <= 4: return n
    if n == 5: return 7
    if n == 6: return 6
    if 7 <= n <= 26: return n + 1
    if 27 <= n <= 74:
        v, k = divmod(n - 27, 6)
        return 28 + 7 * v + {0: 0, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6}[k]
    if 75 <= n <= 96: return n + 9
    raise ValueError(n)


def old_to_new_target(i):
    if i == 0: return 0
    if 1 <= i <= 8: return 14 + 5 * (i - 1)
    if i == 9: return 10
    if 10 <= i <= 17: return 16 + 5 * (i - 10)
    if 18 <= i <= 25: return 15 + 5 * (i - 18)
    return {26: 5, 27: 6}[i]


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    n_lines = len(lines)
    done = skipped = 0
    for hi in [i for i, l in enumerate(lines) if "melody_phase.jsfx" in l and "<JS" in l]:
        vi = next((j for j in range(hi + 1, min(hi + 6, len(lines)))
                   if lines[j].strip() and (lines[j].strip()[0].isdigit() or lines[j].strip()[0] in '-"')), None)
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi + 1}")
        old = parse_line(lines[vi])
        if any(k > 96 and v is not None for k, v in old.items()):
            skipped += 1
            continue
        new = {}
        for n in range(1, 97):
            if old.get(n) is not None:
                new[old_to_new_slider(n)] = old[n]
        new[5] = "1"
        for v in range(8):
            tok = old.get(27 + 6 * v)
            if tok is not None:
                midi = fmt(as_float(tok, f"V{v+1} Note") + 36)
                new[28 + 7 * v] = midi
                new[29 + 7 * v] = midi
        for old_sel, new_sel in ((80, 89), (89, 98)):
            tok = old.get(old_sel)
            if tok is not None:
                new[new_sel] = str(old_to_new_target(int(as_float(tok, "target"))))
        # Range check every numeric token against nothing wider than the plugin allows.
        for k, tok in new.items():
            assert 1 <= k <= N_NEW
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
                 if "backups" not in p.parts and "melody_phase.jsfx" in p.read_text(encoding="utf-8", errors="replace")]
    for ps in sorted(paths):
        d, s = migrate(Path(ps), apply_it)
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d:>2} (already done {s})  {ps}")


if __name__ == "__main__":
    main()
