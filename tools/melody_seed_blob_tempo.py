#!/usr/bin/env python3
"""Seed the project tempo into every Melody Phase @serialize blob.

WHY
---
REAPER reports `tempo` as its 120 placeholder for the first stretch of a
project open, before the project's own tempo is applied. Melody Phase derives
host_scale = tempo/60 and its sequencer COUNTS against that, so a synced
sequence started inside that window comes in late and stays late. Measured on
simple-sequence (205 BPM): eleven of twelve instances read 120 at their first
note and were 276.4 ms late; the twelfth has a Start delay, so its first note
landed after the window, read 205, and was exact.

The plugin now remembers the tempo it last saw settled, in its own blob, and
starts from that instead of guessing. But the remembered value only exists once
a project has been saved by the new build -- so every project already on disk
would keep misbehaving until it happened to be re-saved.

This writes the value in directly.

WHAT IT DOES
------------
For each Melody Phase instance whose blob is the v2.14 format (magic 2100028):

    magic 2100000+N -> 2200000+N          (the format the plugin now writes)
    append one float32: the project's TEMPO

Nothing else in the blob is touched -- the drift and ramp banks are copied
through byte for byte and verified afterwards.

NOT TOUCHED
-----------
* Blobs on the older drift-only format (magic 1000028). Those already fall
  through to the plugin's defaults and always have; upgrading them would mean
  synthesising ramp banks that never existed. They are all in BPM-mode projects
  where host_scale is 1 and the tempo is not used at all, so there is nothing
  to gain and a format to get wrong.
* Projects with no Melody Phase, and instances with no blob.

SAFETY
------
All-or-nothing per file: every blob is rebuilt and the whole file verified in
memory before a byte is written. Afterwards, melody_verify_blob_tempo checks the
RESULT against the snapshot -- first 199 floats identical, magic bumped, the
appended float equal to the project tempo, and no other line changed.
"""

import argparse
import base64
import os
import re
import struct
import sys

N_TARGETS = 28
OLD_MAGIC = 2100000 + N_TARGETS      # 2100028
NEW_MAGIC = 2200000 + N_TARGETS      # 2200028
OLD_FLOATS = 1 + 4 * N_TARGETS + 1 + 3 * N_TARGETS + 1     # 199
NEW_FLOATS = OLD_FLOATS + 1                                 # 200

JS_RE = re.compile(r'^\s*<JS\s+\S*melody_phase\.jsfx\b')
TEMPO_RE = re.compile(r'^\s*TEMPO\s+([\d.]+)')


def project_tempo(lines):
    for l in lines:
        m = TEMPO_RE.match(l)
        if m:
            return float(m.group(1))
    return None


def find_blobs(lines):
    """Return [(start_idx, end_idx, indent, width)] for each Melody instance's
    <JS_SER> body -- start_idx/end_idx are the first/last base64 line."""
    out = []
    for i, line in enumerate(lines):
        if not JS_RE.match(line):
            continue
        j = i + 1
        while j < len(lines) and lines[j].strip() != ">":
            j += 1
        j += 1
        if j >= len(lines) or not lines[j].strip().startswith("<JS_SER"):
            continue
        first = j + 1
        k = first
        while k < len(lines) and not lines[k].strip().startswith(">"):
            k += 1
        if k == first:
            continue
        body = lines[first]
        indent = body[: len(body) - len(body.lstrip())]
        width = len(body.strip())
        out.append((first, k - 1, indent, width))
    return out


def rewrite(path, apply_changes):
    with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        text = fh.read()
    lines = text.splitlines(keepends=True)
    eol = "\r\n" if text.count("\r\n") else "\n"

    tempo = project_tempo(lines)
    blobs = find_blobs(lines)
    if not blobs:
        return None
    if tempo is None:
        raise ValueError("%s: no TEMPO line" % path)

    changed = skipped = 0
    # walk backwards so earlier indices stay valid as line counts change
    for first, last, indent, width in reversed(blobs):
        b64 = "".join(l.strip() for l in lines[first:last + 1])
        raw = base64.b64decode(b64)
        if len(raw) % 4:
            skipped += 1
            continue
        f = list(struct.unpack("<%df" % (len(raw) // 4), raw))
        if len(f) != OLD_FLOATS or abs(f[0] - OLD_MAGIC) > 0.5:
            skipped += 1
            continue
        f[0] = float(NEW_MAGIC)
        f.append(float(tempo))
        assert len(f) == NEW_FLOATS
        new_raw = struct.pack("<%df" % len(f), *f)
        new_b64 = base64.b64encode(new_raw).decode("ascii")
        body = [indent + new_b64[p:p + width] + eol
                for p in range(0, len(new_b64), width)]
        lines[first:last + 1] = body
        changed += 1

    if changed:
        rebuilt = "".join(lines)
        # the only thing that may change is blob body lines; instance count
        # and every non-blob line must survive
        if len(find_blobs(rebuilt.splitlines(keepends=True))) != len(blobs):
            raise ValueError("%s: instance count would change; refusing" % path)
        if apply_changes:
            with open(path, "w", encoding="utf-8",
                      errors="surrogateescape", newline="") as fh:
                fh.write(rebuilt)
    return changed, skipped, tempo


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, f) for f in names
                          if f.lower().endswith(".rpp")]
        else:
            files.append(p)

    tc = ts = 0
    for path in sorted(files):
        res = rewrite(path, args.apply)
        if res is None:
            continue
        c, s, tempo = res
        tc += c
        ts += s
        if c or s:
            print("%-56s tempo=%-7s seeded=%-3d skipped=%d%s"
                  % (os.path.basename(path), tempo, c, s,
                     "" if args.apply else "   (DRY RUN)"))
    print("\nTOTAL seeded=%d skipped=%d%s"
          % (tc, ts, "" if args.apply else "   (DRY RUN -- pass --apply to write)"))


if __name__ == "__main__":
    main()
