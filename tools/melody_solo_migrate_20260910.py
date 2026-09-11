#!/usr/bin/env python3
"""Melody Phase: 105 sliders -> 113, per docs/layouts/solo-propagation-20260910.md.

Slider line only; the blob format is unchanged (magic 2500055 -> 2600055 as the
layout witness, the old one still read). Each voice block grows from seven to
eight: Vn Solo, written Off, sits after Vn Active. Over 64 sliders before and
after, so rpp_sliders handles the "" marker at both ends.

RE-RUNNING IS NOT SAFE ON EVERY LINE. The "already done" test looks for a value
stored above the old slider count, and a line saved by an older build that
stopped at 64 has none even after migrating -- so a second run shifts it again
(it happened to Tensor's shepard.RPP on 2026-09-10). Run once; to redo, restore
the file from its snapshot first.
Dry run by default; --apply writes. Paths must be given.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

N_OLD, N_NEW = 105, 113


def old_to_new(n):
    if n <= 27: return n
    if 28 <= n <= 83:
        v, k = divmod(n - 28, 7)
        return 28 + 8 * v + k
    if 84 <= n <= 105: return n + 8
    raise ValueError(n)


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    n_lines = len(lines)
    done = skipped = 0
    for hi in [i for i, l in enumerate(lines) if "melody_phase.jsfx" in l and "<JS" in l]:
        old = parse_line(lines[hi + 1])
        if any(k > N_OLD and v is not None for k, v in old.items()):
            skipped += 1
            continue
        new = {old_to_new(k): v for k, v in old.items() if v is not None and k <= N_OLD}
        for v in range(8):
            new[35 + 8 * v] = "0"
        out = render_line(lines[hi + 1], new, n_sliders=N_NEW)
        if apply_it:
            lines[hi + 1] = out
        done += 1
    assert len(lines) == n_lines
    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    paths = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        sys.exit("give the files; the scope is authored, not searched for")
    total = 0
    for p in paths:
        d, s = migrate(p, apply_it)
        total += d
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d:>2} (already done {s})  {p}")
    print(f"total instances: {total}")


if __name__ == "__main__":
    main()
