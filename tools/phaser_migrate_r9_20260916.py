#!/usr/bin/env python3
"""Stereo Phaser, R9: scale saved Feedback and Wet/dry from fractions to percent.

Rozaya, 2026-09-14, on no control counting in fractions of one: "That'd be fine by
me". Asked for on 2026-09-16: "Fix the controls, yeah."

Two things move, and both are handled here so the project on disk is wholly on the
newest format:

  1. The SLIDER LINE. Feedback (slider 8) and Wet/dry mix (slider 13) are plain
     sliders, not banked behind a picker, so their saved values live here. x100.
  2. The BLOB, transcoded 3400013 -> 3600013: the per-target period and time units
     appended (seeded from sliders 23 and 32, which is what every target used), and
     the drift and ramp amounts aimed at Feedback (target 7) and Wet/dry (target 10)
     scaled x100 -- every drift amount, and every ramp amount not already typed as
     Percent. This is exactly what the plugin's own @serialize does to an old blob;
     doing it here as well means the idempotency check can be the blob's MAGIC.

The idempotency check is the magic, never the slider values: a value test would
mistake a real small percentage for an unmigrated fraction. (The same class of
mistake as the slot-count check that nearly re-migrated strangeness.RPP.)

Dry run by default; --apply writes.
"""
import base64, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

JS = "glasswings/stereo-phaser.jsfx"
FILES = ["E:/reaper/finished/strangeness.RPP",
         "E:/reaper/finished/test-projects/claude-testing002-bridge.RPP"]
N = 13
OLD, NEW = 3400013, 3600013
PCT = (7, 10)            # Feedback, Wet/dry mix

def unpack(b64):
    raw = base64.b64decode(b64)
    return list(struct.unpack("<%df" % (len(raw) // 4), raw))

def pack(vals):
    return base64.b64encode(b"".join(struct.pack("<f", v) for v in vals)).decode("ascii")

def transcode(v, punit, tunit):
    """3400013 -> 3600013. Offsets follow @serialize's write order exactly."""
    assert int(round(v[0])) == OLD, v[0]
    rb, rd, rdl, rp, rr = 1, 1+N, 1+2*N, 1+3*N, 1+4*N
    last_speed = 1+5*N
    du, dd = last_speed+1, last_speed+1+N
    last_target = last_speed+1+6*N
    dunit, runit = last_target+1, last_target+1+N
    for k in PCT:
        v[du+k] *= 100
        v[dd+k] *= 100
        if int(round(v[runit+k])) != 11:
            v[rb+k] *= 100
    v[0] = NEW
    return v + [punit] * N + [tunit] * N

def blob_span(lines, i):
    """Index range of the base64 lines of the <JS_SER> block after slider line i."""
    j = i + 1
    while j < len(lines) and j < i + 6 and "<JS_SER" not in lines[j]:
        j += 1
    if j >= len(lines) or "<JS_SER" not in lines[j]:
        return None
    a = j + 1
    b = a
    while b < len(lines) and lines[b].strip() != ">":
        b += 1
    return a, b

def main():
    apply = "--apply" in sys.argv
    total = 0
    for path in FILES:
        if not os.path.exists(path):
            print("MISSING %s" % path); continue
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        changed = 0
        i = 0
        while i < len(lines):
            if JS in lines[i] and "<JS" in lines[i]:
                sl = i + 1
                span = blob_span(lines, sl)
                if span is None:
                    print("  SKIP (no blob -- run phaser_migrate_r26r27 first)")
                    i += 1; continue
                a, b = span
                vals = unpack("".join(x.strip() for x in lines[a:b]))
                magic = int(round(vals[0]))
                if magic == NEW:
                    print("  SKIP (already %d)" % NEW); i = b; continue
                if magic != OLD:
                    print("  REFUSED: blob %d is neither %d nor %d" % (magic, OLD, NEW))
                    i = b; continue
                slots = parse_line(lines[sl])
                fb = float(slots[8]) if slots.get(8) not in (None, "-") else 0.6
                wet = float(slots[13]) if slots.get(13) not in (None, "-") else 0.5
                punit = float(slots[23]) if slots.get(23) not in (None, "-") else 0.0
                tunit = float(slots[32]) if slots.get(32) not in (None, "-") else 2.0
                slots[8] = "%g" % (fb * 100)
                slots[13] = "%g" % (wet * 100)
                lines[sl] = render_line(lines[sl], slots, n_sliders=38)
                indent = lines[a][:len(lines[a]) - len(lines[a].lstrip())]
                b64 = pack(transcode(vals, punit, tunit))
                lines[a:b] = [indent + b64[k:k+128] for k in range(0, len(b64), 128)]
                print("  Feedback %g -> %g, Wet/dry %g -> %g, blob %d -> %d"
                      % (fb, fb*100, wet, wet*100, OLD, NEW))
                changed += 1
            i += 1
        total += changed
        print("%s: %d instance(s)" % (path, changed))
        if apply and changed:
            open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("APPLIED" if apply else "DRY RUN -- pass --apply to write")
    return 0

if __name__ == "__main__":
    sys.exit(main())
