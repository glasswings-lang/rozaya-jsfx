#!/usr/bin/env python3
"""Tensor's seven Breath Generators: the first-release line to the current layout.

docs/layouts/breath-gen-r24-20260911.md. Rozaya: "Yes, sync all the broken things".

Each was saved with 13 values and no blob -- Inhale, Top pause, Exhale, Bottom
pause (seconds), Inhale and Exhale frequency (Hz), the four fades, Fade mode,
Stereo width, Stereo flip -- positions that meant the same until the 40-slider
layout of 2026-09-08. Rozaya's own breathscapes and organic-movement were
carried from these very lines by breathgen_promote_20260909.py and
breathgen_migrate_driftmoves_20260909.py; this applies the same rule:

  slider line (41): Breath rate = 60 / the four segments, unit Seconds; the
    segments; Pitch target All, mode Hz, note = the nearest note at or below the
    inhale frequency, value = that frequency, fine tune 0 Cents, reference 440;
    fades, fade mode, width, flip as stored; everything else @init's default.
  blob (2500007): drift and ramp off, the two frequencies in the pitch banks,
    Drift movement as the old rule hardcoded. The plugin reads it like Rozaya's.

IDEMPOTENT BY CONSTRUCTION: reads the snapshot, writes the live file; a live file
equal to the result is done, one equal to the snapshot is written, anything else
is refused. Dry run by default; --apply writes.
"""
import base64, math, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import render_line, as_float, fmt

SNAP = "E:/reaper/finished/backups/snapshots/_pre-breathgen-r24-20260911/tensor"
LIVE = "E:/tensor's-rpp-projects"
FILES = ["breathscapes.RPP", "organic-movement.RPP", "tensor-first-project-20260507-021600.RPP",
         "tensor-three-layer-drift-20260507-023500.RPP", "tensor-two-track-20260507-022000.RPP",
         "tensor-two-track-drift-fixed-20260507-024500.RPP"]
N, N_PITCH = 7, 3


def note_at_or_below(hz):
    return max(0, min(127, int(math.floor(69 + 12 * math.log2(hz / 440.0) + 1e-9))))


def blob(in_hz, ex_hz):
    ni, ne = note_at_or_below(in_hz), note_at_or_below(ex_hz)
    f = [2500007.0] + [0.0] * (3 * N) + [0.0]            # ramp by, dur, delay, last
    f += [0.0] * N + [0.0] * N + [8.0] * N + [0.0] * N + [0.0]   # drift, last
    f += [0.0] * (4 * N)                                  # drift / ramp play, rest
    f += [ni, ni, ne] + [in_hz, in_hz, ex_hz] + [0.0] * N_PITCH + [0.0] * N_PITCH + [2.0] * N_PITCH
    f += [0.0]                                            # last pitch target: All
    f += [0.0] * 5 + [1.0] * 2                            # Drift movement, old rule
    assert len(f) == 103
    return f


def convert(text, where):
    lines = text.splitlines(keepends=True)
    out, i, n = [], 0, 0
    while i < len(lines):
        l = lines[i]
        out.append(l)
        if "<JS" in l and "<JS_SER" not in l and "/breath_gen.jsfx" in l:
            vl, close = lines[i + 1], lines[i + 2]
            toks = vl.split()
            if len(toks) < 13 or any(t != "-" for t in toks[13:]) or close.strip() != ">":
                raise SystemExit(f"REFUSED {where} line {i+2}: not a 13-value first-release line")
            if i + 3 < len(lines) and lines[i + 3].strip().startswith("<JS_SER"):
                raise SystemExit(f"REFUSED {where} line {i+2}: already has a blob")
            v = [as_float(t) for t in toks[:13]]
            new = {1: fmt(round(60.0 / (v[0] + v[1] + v[2] + v[3]), 6)), 2: "0",
                   3: toks[0], 4: toks[1], 5: toks[2], 6: toks[3],
                   7: "0", 8: "0", 9: str(note_at_or_below(v[4])), 10: toks[4],
                   11: "0", 12: "2", 13: "440",
                   14: toks[6], 15: toks[7], 16: toks[8], 17: toks[9], 18: toks[10],
                   19: toks[11], 20: toks[12], 21: "0", 22: "0", 23: "0", 24: "0",
                   25: "0", 26: "0", 27: "0", 28: "8", 29: "0", 30: "0", 31: "0", 32: "0", 33: "0",
                   34: "0", 35: "0", 36: "2", 37: "0", 38: "0", 39: "0", 40: "0", 41: "0"}
            out.append(render_line(vl, new, n_sliders=41))
            out.append(close)
            ind = close[: len(close) - len(close.lstrip())]
            eol = "\r\n" if close.endswith("\r\n") else "\n"
            b64 = base64.b64encode(struct.pack("<103f", *blob(v[4], v[5]))).decode("ascii")
            out.append(ind + "<JS_SER" + eol)
            out += [ind + "  " + b64[k:k + 128] + eol for k in range(0, len(b64), 128)]
            out.append(ind + ">" + eol)
            n += 1
            i += 3
            continue
        i += 1
    return "".join(out), n


def main():
    apply_it = "--apply" in sys.argv
    for name in FILES:
        snap, live = f"{SNAP}/{name}", f"{LIVE}/{name}"
        orig = open(snap, encoding="utf-8", errors="surrogateescape", newline="").read()
        want, n = convert(orig, snap)
        have = open(live, encoding="utf-8", errors="surrogateescape", newline="").read()
        if have == want:
            state = "already done"
        elif have != orig:
            raise SystemExit(f"REFUSED {live}: changed since the snapshot")
        elif apply_it:
            open(live, "w", encoding="utf-8", errors="surrogateescape", newline="").write(want)
            state = "WRITTEN"
        else:
            state = "would write"
        print(f"{state:13} {n} instance(s)  {live}")


if __name__ == "__main__":
    main()
