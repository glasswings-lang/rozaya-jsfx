#!/usr/bin/env python3
"""Resonance Bank: 28 sliders -> 35, per docs/layouts/resonance-bank-r22-r24.md.

Slider line only; the plugin remaps an old blob (1016005 / 2016005 / 3016005)
from 5 targets to 10 itself. New controls are written to what the old plugin
meant: Tuning reference 440, Pitch mode Hz, Note name A4, Fine tune 0 in Cents,
both width units Hz. The two target selectors are remapped 0->2, 1->4, 2->5,
3->6, 4->7.

Idempotent by an exact gate: new slider 3 is Tuning reference (20..2000), old
slider 3 was the Band selector (0..15). A line whose slider 3 is 20 or more is
already done. A line that stores no slider 3 is refused.

Dry run by default; --apply writes. Paths must be given; the scope is authored.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line, as_float, fmt

N_OLD, N_NEW = 28, 35
O2N = {0: 2, 1: 4, 2: 5, 3: 6, 4: 7}
# new id -> old id, for everything that simply moves
MOVE = {1: 1, 2: 2, 4: 3, 7: 4, 10: 5, 12: 6, 14: 7, 15: 8, 16: 9, 17: 10, 18: 11, 19: 12,
        **{20 + k: 13 + k for k in range(8)}, **{28 + k: 21 + k for k in range(8)}}
NEW_VALUES = {3: "440", 5: "0", 6: "69", 8: "0", 9: "2", 11: "0", 13: "0"}
assert sorted(list(MOVE) + list(NEW_VALUES)) == list(range(1, N_NEW + 1))
assert sorted(MOVE.values()) == list(range(1, N_OLD + 1))


def convert_line(line):
    old = parse_line(line)
    if old.get(3) is None:
        raise SystemExit("refusing: a Resonance Bank line with no slider 3")
    if as_float(old[3]) >= 20:
        return None                       # already on the 35 layout
    if any(v is not None for k, v in old.items() if k > N_OLD):
        raise SystemExit("refusing: a value stored above slider 28")
    new = {n: old.get(o) for n, o in MOVE.items()}
    new.update(NEW_VALUES)
    for sel in (20, 28):
        if new[sel] is not None:
            new[sel] = str(O2N[int(as_float(new[sel]))])
    return render_line(line, new, n_sliders=N_NEW)


def convert(path):
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)
    n_lines = len(lines)
    heads = [i for i, l in enumerate(lines) if "<JS" in l and "resonance_bank.jsfx" in l]
    done = skipped = 0
    for hi in heads:
        out = convert_line(lines[hi + 1])
        if out is None:
            skipped += 1
        else:
            lines[hi + 1] = out
            done += 1
    assert len(lines) == n_lines
    return "".join(lines), len(heads), done, skipped


def main():
    apply_it = "--apply" in sys.argv
    paths = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        sys.exit("give the files; the scope is authored, not searched for")
    for p in paths:
        text, n, d, s = convert(p)
        if apply_it and d:
            p.write_text(text, encoding="utf-8", errors="surrogateescape")
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d} of {n} (already done {s})  {p}")


if __name__ == "__main__":
    main()
