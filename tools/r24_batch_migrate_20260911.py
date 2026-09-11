#!/usr/bin/env python3
"""The 2026-09-11 small R24 batch: the files that need writing, and why.

docs/layouts/r24-small-batch-20260911.md. Bubbler, Dapple and Tremolo put their
targets in control order; the PLUGINS remap an old save themselves, so a copy on
the current layout with nothing selected past target 0 needs no file change.
What this writes:

  tremolo_april   Tensor's six and the custom-polyrhythm track template, saved
                  on the FIRST RELEASE layout (d19873f, 18 controls) and never
                  carried over. Taken through every step since, by control:
                  Rate mode and Pan sweep rate unit {Hz, Seconds, BPM} ->
                  canonical (0->2, 1->1, 2->0); Release % and Attack shape swap
                  places (6 <-> 7); Filter speed multiplier becomes Pan sweep
                  every, its reciprocal. Nothing above 18 is stored, so no later
                  insert touches them. Rozaya: "Yes, sync all the broken things".
  tremolo_current knocking.RPP: its Drift target is 1 (Tremolo amount), which is
                  2 now. The line's selector is remapped and the blob rewritten
                  in the new 2300012 format, so the file is current either way.
  dapple_32       scattered.rpp's two, saved on the 32-control layout of
                  2026-09-06 and never carried over: Drift movement inserted
                  (430ff37), the pitch block (78bfc59), and the selectors
                  remapped. The 3500011 blob is left for the plugin to remap.

IDEMPOTENT BY CONSTRUCTION: reads the snapshot and writes the live file. A live
file equal to the result is already done; a live file equal to the snapshot is
written; anything else is refused, because it changed since the snapshot.
Dry run by default; --apply writes. --bridge adds the bridge test project, which
must be closed in REAPER first.
"""
import base64, math, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line, as_float, fmt

SNAP = "E:/reaper/finished/backups/snapshots/_pre-r24-batch-20260911"
TENSOR = "E:/tensor's-rpp-projects"
FILES = [
    ("tensor/playing-around.RPP", f"{TENSOR}/playing-around.RPP", "tremolo_april"),
    ("tensor/shepard.RPP", f"{TENSOR}/shepard.RPP", "tremolo_april"),
    ("tensor/singing-bowl.RPP", f"{TENSOR}/singing-bowl.RPP", "tremolo_april"),
    ("tensor/tensor-heartbeat-pulse-20260507-024000.RPP",
     f"{TENSOR}/tensor-heartbeat-pulse-20260507-024000.RPP", "tremolo_april"),
    ("tensor/tensor-three-layer-drift-20260507-023500.RPP",
     f"{TENSOR}/tensor-three-layer-drift-20260507-023500.RPP", "tremolo_april"),
    ("TrackTemplates/custom-polyrhythm.RTrackTemplate",
     "C:/Users/solst/AppData/Roaming/REAPER/TrackTemplates/custom-polyrhythm.RTrackTemplate",
     "tremolo_april"),
    ("to-play-with-later/knocking.RPP", "E:/reaper/to-play-with-later/knocking.RPP", "tremolo_current"),
    ("to-play-with-later/scattered.rpp", "E:/reaper/to-play-with-later/scattered.rpp", "dapple_32"),
]
BRIDGE = ("test-projects/claude-testing002-bridge.RPP",
          "E:/reaper/finished/test-projects/claude-testing002-bridge.RPP", "tremolo_current")

TR_O2N = {0: 0, 1: 2, 2: 8, 3: 1, 4: 3, 5: 4}
DP_O2N = {o: (o if o <= 2 else o + 2) for o in range(11)}
HZ_SEC_BPM = {0: 2, 1: 1, 2: 0}     # {Hz, Seconds, BPM} -> {BPM, Seconds, Hz, ...}


def refuse(where, why):
    raise SystemExit(f"REFUSED {where}: {why}")


def blocks(lines, fx):
    """(value line index, blob start, blob end) for every <JS ...fx.jsfx>."""
    out = []
    for i, l in enumerate(lines):
        if "<JS" in l and "<JS_SER" not in l and f"/{fx}.jsfx" in l:
            vi = i + 1
            bs = be = None
            k = vi + 1
            while k < len(lines) and lines[k].strip() == ">":
                k += 1
                break
            if k < len(lines) and lines[k].strip().startswith("<JS_SER"):
                bs = k + 1
                be = bs
                while lines[be].strip() != ">":
                    be += 1
            out.append((vi, bs, be))
    return out


def read_blob(lines, bs, be):
    raw = base64.b64decode("".join(l.strip() for l in lines[bs:be]))
    return list(struct.unpack("<%df" % (len(raw) // 4), raw))


def blob_lines(vals, like):
    b64 = base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode("ascii")
    indent = like[: len(like) - len(like.lstrip())]
    eol = "\r\n" if like.endswith("\r\n") else "\n"
    return [indent + b64[x:x + 128] + eol for x in range(0, len(b64), 128)]


def tremolo_april(lines, where):
    n = 0
    for vi, bs, be in blocks(lines, "Full_Feature_Tremolo"):
        old = {k: v for k, v in parse_line(lines[vi]).items() if v is not None}
        if not old or max(old) > 18:
            refuse(where, f"line {vi+1}: stores slider {max(old)}, not the 18-control layout")
        if bs is not None:
            refuse(where, f"line {vi+1}: has a blob; the first release never wrote one")
        new = {}
        for k, v in old.items():
            f = as_float(v, f"slider {k}")
            if k in (2, 17):
                if int(f) not in HZ_SEC_BPM or f != int(f):
                    refuse(where, f"line {vi+1}: slider {k} = {v} is not Hz/Seconds/BPM")
                new[k] = str(HZ_SEC_BPM[int(f)])
            elif k == 18:
                if f <= 0:
                    refuse(where, f"line {vi+1}: Filter speed multiplier {v}")
                new[18] = fmt(1.0 / f)
            elif k == 6:
                new[7] = v
            elif k == 7:
                new[6] = v
            else:
                new[k] = v
        lines[vi] = render_line(lines[vi], new, n_sliders=39)
        n += 1
    return n


def tremolo_current(lines, where):
    n = 0
    for vi, bs, be in reversed(blocks(lines, "Full_Feature_Tremolo")):
        line = parse_line(lines[vi])
        vals = read_blob(lines, bs, be) if bs is not None else None
        if vals is None or vals[0] not in (2100006.0, 2200006.0):
            continue          # nothing a file change is needed for
        m = vals[0]
        up, dn, per, shp = vals[1:7], vals[7:13], vals[13:19], vals[19:25]
        last_d = vals[25]
        by, dur, dly = vals[26:32], vals[32:38], vals[38:44]
        last_r = vals[44]
        if m == 2200006.0:
            if len(vals) != 69:
                refuse(where, f"blob of {len(vals)} floats for 2200006")
            dpl, drs, spl, srs = vals[45:51], vals[51:57], vals[57:63], vals[63:69]
        else:
            if len(vals) != 45:
                refuse(where, f"blob of {len(vals)} floats for 2100006")
            dpl = drs = spl = srs = [0.0] * 6

        def bank(old6, dflt):
            b = [dflt] * 12
            for o in range(6):
                b[TR_O2N[o]] = old6[o]
            return b
        d_sel = TR_O2N[int(last_d)]
        r_sel = TR_O2N[int(last_r)]
        new_vals = ([2300012.0] + bank(up, 0) + bank(dn, 0) + bank(per, 8) + bank(shp, 0) + [d_sel]
                    + bank(by, 0) + bank(dur, 0) + bank(dly, 0) + [r_sel]
                    + bank(dpl, 0) + bank(drs, 0) + bank(spl, 0) + bank(srs, 0))
        for sid in (24, 32):
            if line.get(sid) is not None:
                line[sid] = str(TR_O2N[int(as_float(line[sid]))])
        lines[vi] = render_line(lines[vi], line, n_sliders=39)
        lines[bs:be] = blob_lines(new_vals, lines[bs])
        n += 1
    return n


def nearest_note(hz):
    return 60 if hz <= 0 else max(0, min(127, int(round(69 + 12 * math.log2(hz / 440.0)))))


def dapple_32(lines, where):
    n = 0
    for vi, bs, be in blocks(lines, "dapple"):
        old = {k: v for k, v in parse_line(lines[vi]).items() if v is not None}
        if not old or max(old) > 32:
            refuse(where, f"line {vi+1}: stores slider {max(old)}, not the 32-control layout")
        if bs is not None and read_blob(lines, bs, be)[0] != 3500011.0:
            refuse(where, f"line {vi+1}: blob is not 3500011")
        new = {}
        for k, v in old.items():
            if k <= 3:
                new[k] = v
            elif k == 4:
                pass
            elif k <= 16:
                new[k + 5] = v
            elif k == 17:
                new[22] = str(DP_O2N[int(as_float(v))])
            elif k <= 21:
                new[k + 5] = v
            elif k == 25:
                new[31] = str(DP_O2N[int(as_float(v))])
            else:
                new[k + 6] = v
        hz = as_float(old[4]) if 4 in old else 150.0
        new.update({4: "0", 5: str(nearest_note(hz)), 6: old.get(4, "150"),
                    7: "0", 8: "2", 9: "440"})
        sel = int(as_float(old[17])) if 17 in old else 0
        new[27] = "0" if 1 <= sel <= 3 else "1"   # what drift_is_stepped() hardcoded
        lines[vi] = render_line(lines[vi], new, n_sliders=38)
        n += 1
    return n


def convert(snap_path, kind):
    text = open(snap_path, encoding="utf-8", errors="surrogateescape", newline="").read()
    lines = text.splitlines(keepends=True)
    n_lines = len(lines)
    count = {"tremolo_april": tremolo_april, "tremolo_current": tremolo_current,
             "dapple_32": dapple_32}[kind](lines, snap_path)
    if kind != "tremolo_current" and len(lines) != n_lines:
        refuse(snap_path, "line count changed")
    return "".join(lines), count


def main():
    apply_it = "--apply" in sys.argv
    files = FILES + ([BRIDGE] if "--bridge" in sys.argv else [])
    for rel, live, kind in files:
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
        print(f"{state:13} {count} instance(s)  {kind:16} {live}")


if __name__ == "__main__":
    main()
