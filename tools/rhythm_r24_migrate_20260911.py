#!/usr/bin/env python3
"""Rhythm Track's sixteen targets and Drift movement: the three files, and why.

docs/layouts/rhythm-track-r24-20260911.md. The plugin remaps an old two-target
blob itself; the slider LINE cannot be, because Drift movement is inserted at 36.

  current  the bridge copy, on the 39-control layout: 1-35 stay, 36 becomes Drift
           movement = On a clock (what both old targets always did), 36-39 move
           to 37-40, and the two target selectors (23, 31) are remapped 1 -> 2.
  first    Tensor's two, saved on the FIRST RELEASE (d19873f, 13 controls, no
           blob) and never carried over ("Yes, sync all the broken things").
           By name to the 40-control line, and a new 2500016 blob holding the
           line's two frequencies as pitches in Hz. Only the first 13 tokens are
           read: the first release declares 13, and tensor-two-track's later
           tokens are hand-typed zeros REAPER never gave to any control.

IDEMPOTENT BY CONSTRUCTION: reads the snapshot and writes the live file. A live
file equal to the result is already done; one equal to the snapshot is written;
anything else is refused. Dry run by default; --apply writes.
"""
import base64, math, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line, as_float

SNAP = "E:/reaper/finished/backups/snapshots/_pre-rhythm-r24-20260911"
TENSOR = "E:/tensor's-rpp-projects"
FILES = [
    ("test-projects/claude-testing002-bridge.RPP",
     "E:/reaper/finished/test-projects/claude-testing002-bridge.RPP", "current"),
    ("tensor/tensor-two-track-drift-fixed-20260507-024500.RPP",
     f"{TENSOR}/tensor-two-track-drift-fixed-20260507-024500.RPP", "first"),
    ("tensor/tensor-two-track-20260507-022000.RPP",
     f"{TENSOR}/tensor-two-track-20260507-022000.RPP", "first"),
]
N_OLD, N_NEW, N_T = 39, 40, 16
O2N = {0: 0, 1: 2}


def refuse(where, why):
    raise SystemExit(f"REFUSED {where}: {why}")


def heads(lines):
    return [i for i, l in enumerate(lines) if "<JS " in l and "<JS_SER" not in l and "/rhythm-track.jsfx" in l]


def current_line(line, where):
    old = parse_line(line)
    if any(v is not None for k, v in old.items() if k > N_OLD):
        refuse(where, "a value stored above slider 39 -- already on the new layout, or unknown")
    if old.get(36) is None:
        refuse(where, "no slider 36 stored; cannot tell the layout")
    new = {k: old.get(k) for k in range(1, 36)}
    new[36] = "1"
    for k in range(36, 40):
        new[k + 1] = old.get(k)
    for sid in (23, 31):
        if new[sid] is not None:
            v = as_float(new[sid], f"slider {sid}")
            if v not in O2N:
                refuse(where, f"slider {sid} = {new[sid]} is not a two-target index")
            new[sid] = str(O2N[int(v)])
    return render_line(line, new, n_sliders=N_NEW)


def nearest_note(hz):
    return 60 if hz <= 0 else max(0, min(127, int(round(69 + 12 * math.log2(hz / 440.0)))))


def first_blob(strong_hz, weak_hz):
    ns, nw = nearest_note(strong_hz), nearest_note(weak_hz)
    z = [0.0] * N_T
    v = ([2500016.0] + z + z + [8.0] * N_T + z + [0.0]      # drift up, down, period, shape, last target
         + z + z + z + [0.0]                                 # ramp by, duration, delay, last target
         + z + z + z + z                                     # drift play/rest, ramp play/rest
         + [ns, ns, nw] + [strong_hz, strong_hz, weak_hz]    # note, value (All, Strong, Weak)
         + [0.0] * 3 + [0.0] * 3 + [2.0] * 3 + [0.0]         # mode Hz, fine 0, unit Cents, last pitch target
         + [1.0] * N_T)                                      # Drift movement: On a clock
    return base64.b64encode(struct.pack("<%df" % len(v), *v)).decode("ascii"), ns


def first(lines, where):
    n = 0
    for hi in reversed(heads(lines)):
        vi = hi + 1
        body = lines[vi]
        eol = "\r\n" if body.endswith("\r\n") else "\n"
        indent = body[: len(body) - len(body.lstrip())]
        toks = body.split()
        if len(toks) < 13 or any(t == "-" or t.startswith('"') for t in toks[:13]):
            refuse(where, f"line {vi+1}: not 13 plain first-release values")
        if lines[vi + 1].strip() != ">":
            refuse(where, f"line {vi+2}: expected the <JS> block's closing '>'")
        if lines[vi + 2].strip().startswith("<JS_SER"):
            refuse(where, f"line {vi+3}: already has a blob; the first release never wrote one")
        t = {k + 1: toks[k] for k in range(13)}
        for k in t:
            as_float(t[k], f"first-release slider {k}")
        blob, ns = first_blob(float(t[4]), float(t[5]))
        new = {1: t[1], 2: "0", 3: t[2], 4: t[3], 5: "0", 6: "0", 7: str(ns), 8: t[4], 9: "0", 10: "2",
               11: "440", 12: t[6], 13: t[7], 14: t[8], 15: t[9], 16: t[10], 17: t[11], 18: t[12],
               19: t[13], 20: "0", 21: "0", 22: "0", 23: "0", 24: "0", 25: "2", 26: "0", 27: "0", 28: "0",
               29: "0", 30: "0", 31: "0", 32: "0", 33: "0", 34: "8", 35: "0", 36: "1", 37: "0", 38: "0",
               39: "0", 40: "0"}
        lines[vi] = render_line(indent + "x" + eol, new, n_sliders=N_NEW)
        js_ind = lines[hi][: len(lines[hi]) - len(lines[hi].lstrip())]
        ser = ([js_ind + "<JS_SER" + eol]
               + [js_ind + "  " + blob[x:x + 128] + eol for x in range(0, len(blob), 128)]
               + [js_ind + ">" + eol])
        lines[vi + 2:vi + 2] = ser
        n += 1
    return n


def convert(snap_path, kind):
    text = open(snap_path, encoding="utf-8", errors="surrogateescape", newline="").read()
    lines = text.splitlines(keepends=True)
    n_lines, n_heads = len(lines), len(heads(lines))
    if kind == "current":
        for hi in heads(lines):
            lines[hi + 1] = current_line(lines[hi + 1], snap_path)
        count = n_heads
        if len(lines) != n_lines:
            refuse(snap_path, "line count changed")
    else:
        count = first(lines, snap_path)
    if len(heads(lines)) != n_heads or count != n_heads or n_heads != 1:
        refuse(snap_path, f"instance count {n_heads} -> {len(heads(lines))}, converted {count}")
    return "".join(lines), count


def main():
    apply_it = "--apply" in sys.argv
    for rel, live, kind in FILES:
        snap = f"{SNAP}/{rel}"
        want, count = convert(snap, kind)
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
        print(f"{state:13} {count} instance(s)  {kind:8} {live}")


if __name__ == "__main__":
    main()
