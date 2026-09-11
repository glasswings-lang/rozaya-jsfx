#!/usr/bin/env python3
"""Resonance Bank: 27 sliders -> 28, per docs/layouts/solo-propagation-20260910.md.

Slider line only. `Band solo` is inserted at 10, written Off; 10..27 move to
11..28. The blob gains a band_solo bank under magic 3016005, and the plugin reads
an older 2016005 / 1016005 save with every band unsoloed, so the blob needs no
rewrite.

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

N_OLD, N_NEW = 27, 28


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    n_lines = len(lines)
    done = skipped = 0
    for hi in [i for i, l in enumerate(lines) if "resonance_bank.jsfx" in l and "<JS" in l]:
        old = parse_line(lines[hi + 1])
        if old.get(28) is not None:
            skipped += 1
            continue
        new = {(k + 1 if k >= 10 else k): v for k, v in old.items() if v is not None and k <= N_OLD}
        new[10] = "0"
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
