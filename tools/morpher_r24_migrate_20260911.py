#!/usr/bin/env python3
"""The Morpher's fifty-five targets: every project line's two selectors.

docs/layouts/spectral-vowel-morpher-r24-20260911.md. No slider moves and the plugin
remaps its own blob; this remaps the LINE's Drift target (35) and Ramp target (44)
from the 24-target list to the 55, in all 123 instances, so a line and its blob
agree before the plugin ever loads them. A selector is floored, as the plugin reads
it, and written back whole.

Reads the snapshot and writes the live file (the authored scope is the snapshot's
39 projects). A live file equal to the result is already done; one equal to the
snapshot is written; anything else is refused. Dry run by default; --apply writes.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line, as_float

SNAP = "E:/reaper/finished/backups/snapshots/_pre-morpher-r24-20260911"
LIVE = "E:/reaper"
O2N = {0: 2, 1: 4, 2: 5, 3: 6, 4: 8, 5: 52, 6: 10, 7: 9, **{8 + i: 14 + i for i in range(16)}}


def refuse(where, why):
    raise SystemExit(f"REFUSED {where}: {why}")


def files():
    out = []
    for top, _, names in os.walk(SNAP):
        for n in names:
            p = os.path.join(top, n).replace("\\", "/")
            out.append((p[len(SNAP) + 1:], f"{LIVE}/{p[len(SNAP) + 1:]}"))
    return sorted(out)


def heads(lines):
    return [i for i, l in enumerate(lines) if "<JS " in l and "<JS_SER" not in l and "spectral_vowel_morpher.jsfx" in l]


def remap_line(line, where):
    s = parse_line(line)
    n = max(k for k, v in s.items() if v is not None)
    for sid in (35, 44):
        if s.get(sid) is not None:
            o = int(math.floor(as_float(s[sid], f"slider {sid}")))
            if o not in O2N:
                refuse(where, f"slider {sid} = {s[sid]} is not a 24-target index")
            s[sid] = str(O2N[o])
    return render_line(line, s, n_sliders=n)


def convert(snap_path):
    text = open(snap_path, encoding="utf-8", errors="surrogateescape", newline="").read()
    lines = text.splitlines(keepends=True)
    n_lines, hs = len(lines), heads(lines)
    if not hs:
        refuse(snap_path, "no Morpher instance")
    for hi in hs:
        lines[hi + 1] = remap_line(lines[hi + 1], snap_path)
    if len(lines) != n_lines or len(heads(lines)) != len(hs):
        refuse(snap_path, "line or instance count changed")
    return "".join(lines), len(hs)


def main():
    apply_it = "--apply" in sys.argv
    total = 0
    for rel, live in files():
        snap = f"{SNAP}/{rel}"
        want, n = convert(snap)
        total += n
        have = open(live, encoding="utf-8", errors="surrogateescape", newline="").read()
        orig = open(snap, encoding="utf-8", errors="surrogateescape", newline="").read()
        if have == want:
            state = "already done"
        elif have != orig:
            refuse(live, "changed since the snapshot")
        elif apply_it:
            open(live, "w", encoding="utf-8", errors="surrogateescape", newline="").write(want)
            state = "WRITTEN"
        else:
            state = "would write"
        print(f"{state:13} {n} instance(s)  {rel}")
    print(f"TOTAL {total} instances")


if __name__ == "__main__":
    main()
