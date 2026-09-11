#!/usr/bin/env python3
"""Heartbeat's eighteen targets: the two files that need writing, and why.

docs/layouts/heartbeat-r24-20260911.md. The plugin remaps an old four-target save
itself, so a current copy needs no change for the targets. What this writes:

  finished/transformation.RPP  its <JS_SER> sits INSIDE the <JS> block, before the
      block's closing '>', where heartbeat_migrate_pitchblock_20260909.py put it.
      REAPER writes it AFTER that '>' (every REAPER-saved project checked), and
      whether REAPER reads it inside is not known. Moved, content byte-identical.
      The only nested one in any live project (scanned 2026-09-11).
  Tensor's transformation.RPP  the first release's 13 values, never carried over
      ("Yes, sync all the broken things"). Given the line and blob Rozaya's own copy
      got from the same line: positions 1-13 by name, the two thump frequencies
      into the pitch banks through heartbeat_migrate_pitchblock_20260909.build_blob.

NOT touched: Tensor's tensor-heartbeat-pulse, whose plugin path has a space and no
quotes, so REAPER never loaded it; its line is sixty hand-typed zeros.

IDEMPOTENT BY CONSTRUCTION: snapshot in, live out; a live file equal to the result
is done, one equal to the snapshot is written, anything else is refused.
Dry run by default; --apply writes.
"""
import base64, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import render_line, as_float
import heartbeat_migrate_pitchblock_20260909 as pitchblock

SNAP = "E:/reaper/finished/backups/snapshots/_pre-heartbeat-r24-20260911"
FILES = [("finished/transformation.RPP", "E:/reaper/finished/transformation.RPP", "unnest"),
         ("tensor/transformation.RPP", "E:/tensor's-rpp-projects/transformation.RPP", "april")]


def refuse(where, why):
    raise SystemExit(f"REFUSED {where}: {why}")


def unnest(lines, where):
    """<JS>, values, <JS_SER ... >, >  ->  <JS>, values, >, <JS_SER ... >"""
    n = 0
    for i, l in enumerate(lines):
        if "<JS " in l and "heartbeat gen.jsfx" in l and lines[i + 2].strip().startswith("<JS_SER"):
            end = i + 3
            while lines[end].strip() != ">":
                end += 1
            close = end + 1
            if lines[close].strip() != ">":
                refuse(where, f"line {close+1}: expected the <JS> block's closing '>'")
            ind = l[: len(l) - len(l.lstrip())]
            ser = lines[i + 2:end + 1]
            # Re-indent to the JS block's own level, as REAPER writes it.
            shift = len(lines[i + 2]) - len(lines[i + 2].lstrip()) - len(ind)
            ser = [s[shift:] if s[:shift].strip() == "" else s for s in ser]
            lines[i + 2:close + 1] = [lines[close]] + ser
            n += 1
    return n


def april(lines, where):
    out, n, i = [], 0, 0
    while i < len(lines):
        l = lines[i]
        out.append(l)
        if "<JS" in l and "<JS_SER" not in l and "heartbeat gen.jsfx" in l:
            vl, close = lines[i + 1], lines[i + 2]
            toks = vl.split()
            if len(toks) < 13 or any(t != "-" for t in toks[13:]) or close.strip() != ">":
                refuse(where, f"line {i+2}: not a 13-value first-release line")
            if i + 3 < len(lines) and lines[i + 3].strip().startswith("<JS_SER"):
                refuse(where, f"line {i+2}: already has a blob")
            v = [as_float(t) for t in toks[:13]]
            new = {1: toks[0], 2: "0", 3: toks[1], 4: toks[2], 5: toks[3], 6: toks[4], 7: toks[5],
                   8: toks[6], 9: "0", 10: "0", 11: str(pitchblock.nearest_note(v[7])), 12: toks[7],
                   13: "0", 14: "2", 15: "440", 16: toks[9], 17: toks[10], 18: toks[11], 19: toks[12],
                   28: "0"}
            out.append(render_line(vl, new, n_sliders=40))
            out.append(close)
            ind = close[: len(close) - len(close.lstrip())]
            eol = "\r\n" if close.endswith("\r\n") else "\n"
            vals = pitchblock.build_blob(v[7], v[8])
            b64 = base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode("ascii")
            out.append(ind + "<JS_SER" + eol)
            out += [ind + "  " + b64[k:k + 128] + eol for k in range(0, len(b64), 128)]
            out.append(ind + ">" + eol)
            n += 1
            i += 3
            continue
        i += 1
    lines[:] = out
    return n


def main():
    apply_it = "--apply" in sys.argv
    for rel, live, kind in FILES:
        snap = f"{SNAP}/{rel}"
        orig = open(snap, encoding="utf-8", errors="surrogateescape", newline="").read()
        lines = orig.splitlines(keepends=True)
        n = {"unnest": unnest, "april": april}[kind](lines, snap)
        want = "".join(lines)
        have = open(live, encoding="utf-8", errors="surrogateescape", newline="").read()
        if have == want:
            state = "already done"
        elif have != orig:
            refuse(live, "changed since the snapshot")
        elif apply_it:
            open(live, "w", encoding="utf-8", errors="surrogateescape", newline="").write(want)
            state = "WRITTEN"
        else:
            state = "would write"
        print(f"{state:13} {n} instance(s)  {kind:7} {live}")


if __name__ == "__main__":
    main()
