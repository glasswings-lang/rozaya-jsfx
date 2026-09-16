#!/usr/bin/env python3
"""Veil and the Stereo Phaser: make room for `Drift movement`, blob included.

docs/layouts/veil-phaser-drift-movement.md is the layout this applies. One new control
right after `Drift period`: Veil's slider 22 (old 22-35 -> 23-36), the Phaser's slider 25
(old 25-38 -> 26-39). Rozaya, 2026-09-16: "Yes pls".

Two things move, both here, so the project on disk is wholly on the newest format:

  1. The SLIDER LINE: the new slot gets 0 (With the target) and everything after it
     moves down one. The map is authored, not inferred.
  2. The BLOB, 3600013 -> 3700013: one bank of 13 zeros appended -- every target on
     With the target, exactly what the plugin's own @serialize gives an older blob.

The idempotency check is the blob's MAGIC, never the slider count or values.

Dry run by default; --apply writes.
"""
import base64, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

N = 13
OLD, NEW = 3600013, 3700013
PLUGINS = {
    "glasswings/veil.jsfx": dict(insert=22, old_width=35,
        files=["E:/reaper/finished/test-projects/claude-testing002-bridge.RPP"]),
    "glasswings/stereo-phaser.jsfx": dict(insert=25, old_width=38,
        files=["E:/reaper/finished/strangeness.RPP",
               "E:/reaper/finished/test-projects/claude-testing002-bridge.RPP"]),
}

def unpack(b64):
    raw = base64.b64decode(b64)
    return list(struct.unpack("<%df" % (len(raw) // 4), raw))

def pack(vals):
    return base64.b64encode(b"".join(struct.pack("<f", v) for v in vals)).decode("ascii")

def blob_span(lines, i):
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
    by_file = {}
    for js, p in PLUGINS.items():
        for f in p["files"]:
            by_file.setdefault(f, []).append(js)
    for path, plugins in by_file.items():
        if not os.path.exists(path):
            print("MISSING %s" % path); continue
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        changed = 0
        i = 0
        while i < len(lines):
            js = next((j for j in plugins if j in lines[i] and "<JS" in lines[i]), None)
            if js is None:
                i += 1; continue
            p = PLUGINS[js]
            sl = i + 1
            span = blob_span(lines, sl)
            if span is None:
                print("  REFUSED %s line %d: no blob" % (js, sl + 1)); i += 1; continue
            a, b = span
            vals = unpack("".join(x.strip() for x in lines[a:b]))
            magic = int(round(vals[0]))
            if magic == NEW:
                print("  SKIP %s line %d (already %d)" % (js, sl + 1, NEW)); i = b; continue
            if magic != OLD:
                print("  REFUSED %s line %d: blob %d is neither %d nor %d"
                      % (js, sl + 1, magic, OLD, NEW)); i = b; continue
            old = parse_line(lines[sl])
            new = {}
            k = p["insert"]
            for s in range(1, p["old_width"] + 1):
                new[s if s < k else s + 1] = old.get(s)
            new[k] = "0"
            lines[sl] = render_line(lines[sl], new, n_sliders=p["old_width"] + 1)
            vals[0] = NEW
            indent = lines[a][:len(lines[a]) - len(lines[a].lstrip())]
            b64 = pack(vals + [0.0] * N)
            lines[a:b] = [indent + b64[q:q+128] for q in range(0, len(b64), 128)]
            print("  %s line %d: slider %d inserted, blob %d -> %d" % (js, sl + 1, k, OLD, NEW))
            changed += 1
            i += 1
        print("%s: %d instance(s)" % (path, changed))
        if apply and changed:
            open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("APPLIED" if apply else "DRY RUN -- pass --apply to write")
    return 0

if __name__ == "__main__":
    sys.exit(main())
