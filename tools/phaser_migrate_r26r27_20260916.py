#!/usr/bin/env python3
"""Move the Stereo Phaser's saved state from the 25-control layout to the 38-control one.

docs/layouts/stereo-phaser.md holds the layout this applies. Four live instances,
counted 2026-09-16 across all of E:/reaper and E:/tensor's-rpp-projects plus
REAPER's ProjectTemplates and TrackTemplates, ignoring backup snapshots.

THE MAP IS AUTHORED, one line per control; nothing is inferred.

The hard part, and why this writes a BLOB as well as a slider line: the sweep's
two ends no longer have a slider each -- they are per-end banks reached through
the Range end picker, and banks live in @serialize. strangeness.RPP's three
instances are pre-2026-09-05 saves with NO blob at all and a sweep of 40-200 Hz,
nothing like the 300/1500 defaults, so carrying only the midpoint would throw
their sound away. So a fresh new-format blob is written for every instance, with
the two ends in it and every other bank at exactly the @init default the plugin
would have used anyway (drift period 20, everything else 0) -- which is what "no
blob" meant.

Dry run by default; --apply writes. Idempotent: a 38-wide line is left alone.
"""
import base64, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

JS = "glasswings/stereo-phaser.jsfx"
FILES = ["E:/reaper/finished/strangeness.RPP",
         "E:/reaper/finished/test-projects/claude-testing002-bridge.RPP"]

N = 13                      # new target count
OLD_N = 6
TGT = {0: 8, 1: 1, 2: 2, 3: 7, 4: 9, 5: 10}     # old target -> new
MOVE = {11: 1, 10: 2, 8: 6, 9: 7, 12: 8, 13: 9,  # new <- old
        21: 11, 22: 12, 23: 14, 24: 13, 25: 15, 26: 16, 27: 17,
        31: 19, 32: 20, 33: 21, 34: 22, 35: 23, 37: 24, 38: 25}
NEW = {1: "0", 2: "0", 5: "2", 6: "0", 7: "440",
       14: "0", 15: "0", 16: "0", 17: "0", 18: "0",
       20: "0", 28: "0", 30: "0", 36: "0"}

def num(tok, dflt=0.0):
    try:
        return float(tok)
    except (TypeError, ValueError):
        return dflt

def note_for(hz, ref=440.0):
    import math
    return max(0, min(127, int(round(69 + 12 * math.log(max(hz, 0.0001) / ref, 2)))))

def blob(lo, hi):
    """A fresh new-format @serialize blob: the two ends, everything else at @init.

    Layout is exactly what @serialize writes, in order, as little-endian float32 --
    the same 4-byte width the old 232-byte Veil blob proved (58 values x 4)."""
    v = [3400000 + N]                       # magic
    for _ in range(5):                      # ramp by / dur / delay / play / rest
        v += [0.0] * N
    v += [0.0]                              # last_speed_target
    v += [0.0] * N                          # drift up
    v += [0.0] * N                          # drift down
    v += [20.0] * N                         # drift period -- the @init default
    v += [0.0] * N                          # drift shape
    v += [0.0] * N                          # drift play
    v += [0.0] * N                          # drift rest
    v += [0.0]                              # last_target_select
    v += [0.0] * N                          # drift amount unit  = Target default
    v += [0.0] * N                          # ramp by unit       = Target default
    v += [0.0, 0.0]                         # end_pmode  = Hz
    v += [note_for(lo), note_for(hi)]       # end_note
    v += [lo, hi]                           # end_freq
    v += [2.0, 2.0]                         # end_funit  = Cents
    v += [0.0, 0.0]                         # end_fine
    v += [0.0]                              # last_end   = Both
    raw = b"".join(struct.pack("<f", x) for x in v)
    return base64.b64encode(raw).decode("ascii")

def already_done(lines, i):
    """True if this instance already carries a NEW-format blob.

    Counting slider slots does NOT work as an idempotency check and nearly cost a
    project: strangeness.RPP's migrated lines still hold `-` at slots 26 and 38, so
    a width test passed a second time and would have re-migrated an already-migrated
    line, reading the new slot 4 and 5 as if they were the old two ends. The blob's
    magic is unambiguous, so that is what is checked."""
    j = i
    while j < len(lines) and j < i + 6 and "<JS_SER" not in lines[j]:
        j += 1
    if j >= len(lines) or "<JS_SER" not in lines[j]:
        return False
    b = ""
    j += 1
    while j < len(lines) and lines[j].strip() != ">":
        b += lines[j].strip(); j += 1
    try:
        raw = base64.b64decode(b)
        return struct.unpack("<f", raw[:4])[0] == 3400000 + N
    except Exception:
        return False

def migrate(line):
    old = parse_line(line)
    lo = num(old.get(4), 300.0)
    hi = num(old.get(5), 1500.0)
    new = dict(NEW)
    for dst, src in MOVE.items():
        new[dst] = old.get(src)
    new[3] = str(note_for((lo + hi) / 2))
    new[4] = "%g" % ((lo + hi) / 2)          # the picker opens on Both = the midpoint
    new[19] = str(TGT.get(int(num(old.get(10))), 0))
    new[29] = str(TGT.get(int(num(old.get(18))), 0))
    return render_line(line, new, n_sliders=38), lo, hi, None

def main():
    apply = "--apply" in sys.argv
    total = 0
    for path in FILES:
        if not os.path.exists(path):
            print("MISSING %s" % path); continue
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        out, i, changed = [], 0, 0
        while i < len(lines):
            ln = lines[i]
            out.append(ln)
            if JS in ln and "<JS" in ln:
                i += 1
                if already_done(lines, i):
                    print("  SKIP (already carries a %d blob)" % (3400000 + N))
                    out.append(lines[i]); i += 1; continue
                newline, lo, hi, why = migrate(lines[i])
                if newline is None:
                    print("  SKIP (%s)" % why); out.append(lines[i])
                else:
                    changed += 1
                    print("  sweep %g-%g Hz -> midpoint %g, carried in a fresh blob"
                          % (lo, hi, (lo + hi) / 2))
                    out.append(newline)
                    # drop any old blob, then write the new one
                    j = i + 1
                    while j < len(lines) and "<JS_SER" not in lines[j] and lines[j].strip() != ">":
                        out.append(lines[j]); j += 1
                    if j < len(lines) and "<JS_SER" in lines[j]:
                        while j < len(lines) and lines[j].strip() != ">":
                            j += 1
                        j += 1
                    indent = " " * (len(ln) - len(ln.lstrip()))
                    b = blob(lo, hi)
                    out.append("%s<JS_SER" % indent)
                    for k in range(0, len(b), 128):
                        out.append("%s  %s" % (indent, b[k:k+128]))
                    out.append("%s>" % indent)
                    i = j - 1
            i += 1
        total += changed
        print("%s: %d instance(s)" % (path, changed))
        if apply and changed:
            open(path, "w", encoding="utf-8", newline="").write("\n".join(out))
    print("APPLIED" if apply else "DRY RUN -- pass --apply to write")
    return 0 if total else 1

if __name__ == "__main__":
    sys.exit(main())
