#!/usr/bin/env python3
"""Shepard Tone: 89 sliders -> 97, per docs/layouts/solo-propagation-20260910.md.

Slider line only; the blob format is unchanged (its magic moved 2300040 -> 2400040
as the layout witness, and the plugin still reads the old one). Each voice block
grows from seven to eight: Vn Solo, written Off, sits after Vn Active.

RE-RUNNING IS NOT SAFE ON EVERY LINE. The "already done" test looks for a value
stored above the old slider count, and a line saved by an older build that
stopped at 64 has none even after migrating -- so a second run shifts it again
(it happened to Tensor's shepard.RPP on 2026-09-10). Run once; to redo, restore
the file from its snapshot first.

Dry run by default; --apply writes. Paths must be given (the scope is authored).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line, SliderLineError

N_OLD, N_NEW = 89, 97


def old_to_new(n):
    if n <= 13: return n
    if 14 <= n <= 69:
        v, k = divmod(n - 14, 7)
        return 14 + 8 * v + k
    if 70 <= n <= 89: return n + 8
    raise ValueError(n)


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    n_lines = len(lines)
    done = skipped = 0
    for hi in [i for i, l in enumerate(lines) if "shepard-tone.jsfx" in l and "<JS" in l]:
        try:
            old = parse_line(lines[hi + 1])
        except SliderLineError:
            # Tensor's hand-written lines: more dashes than REAPER writes and no
            # marker. Accepted only when every token past the last real value is
            # a dash and that value sits at or below slider 64, so the ids are
            # unambiguous.
            toks = lines[hi + 1].split()
            last = max((k + 1 for k, t in enumerate(toks) if t != "-"), default=0)
            if not (len(toks) > 64 and last <= 64):
                raise
            old = {k + 1: (None if t == "-" else t) for k, t in enumerate(toks[:last])}
        if any(k > N_OLD and v is not None for k, v in old.items()):
            skipped += 1
            continue
        new = {old_to_new(k): v for k, v in old.items() if v is not None and k <= N_OLD}
        for v in range(8):
            new[21 + 8 * v] = "0"
        assert all(1 <= k <= N_NEW for k in new)
        if apply_it:
            lines[hi + 1] = render_line(lines[hi + 1], new, n_sliders=N_NEW)
        else:
            render_line(lines[hi + 1], new, n_sliders=N_NEW)
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
