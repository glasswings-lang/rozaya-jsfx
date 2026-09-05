#!/usr/bin/env python3
"""Migrate Full_Feature_Tremolo projects to the 2026-09-05 approved
layout (docs/layouts/full-feature-tremolo.md, reading order approved by Rozaya).

The permutation is AUTHORED, transcribed from that document's "The order"
section. This script only APPLIES it.

IDEMPOTENT BY CONSTRUCTION: reads the pre-migration SNAPSHOT and writes the live
project, so re-running reproduces the same result rather than permuting an
already-permuted line.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-tremolo-reorder-20260905/
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-tremolo-reorder-20260905'
OLD_N, NEW_N = 40, 39

# --- AUTHORED: old slider id -> new slider id ------------------------------
REMAP = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 7: 6, 6: 7, 8: 8, 9: 9, 10: 10,
    11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18,
    19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
    29: 24, 30: 25, 31: 26, 32: 27, 33: 29, 36: 30, 37: 31,
    24: 32, 25: 33, 38: 34, 26: 35, 39: 36, 40: 37, 27: 38, 28: 39,
}
DELETED = {34: 'Host ratio (retired)', 35: 'Pan speed picker (Linked Sweep)'}

# Pan sweep rate mode: {Hz,Seconds,BPM} -> {BPM,Seconds,Hz,Host x}.
# Hz 0 -> 2, Seconds 1 -> 1, BPM 2 -> 0. Keyed by the NEW slider id.
ENUM = {17: {'0': '2', '1': '1', '2': '0'}}

# Filter speed multiplier -> Pan sweep every (cycles): the reciprocal.
# Measured before running: all 11 instances store 1, so this is 1 -> 1 for every
# one of them. Implemented properly anyway, because "it happens to be free right
# now" is not a reason to write a wrong transform.
RECIPROCAL = {18}


def convert(path_in, path_out, dry):
    raw = open(path_in, 'rb').read()
    lines = raw.decode('utf-8').splitlines(keepends=True)
    n_before = len(lines)
    count = 0

    for i, line in enumerate(lines):
        if not re.search(r'<JS\s+\S*?Full_Feature_Tremolo\.jsfx', line):
            continue
        vi = i + 1
        orig = lines[vi]
        if not orig.endswith(('\r\n', '\n', '\r')):
            raise SystemExit('%s line %d: value line has no ending -- refusing'
                             % (path_in, vi))
        old = parse_line(orig)
        real = {k: v for k, v in old.items() if v not in (None, '-')}
        if real and max(real) > OLD_N:
            raise SystemExit('%s line %d: real value at slider %d, above the old '
                             'count of %d -- not the layout this table describes'
                             % (path_in, vi, max(real), OLD_N))

        new = {}
        for o, tok in real.items():
            if o in DELETED:
                continue
            if o not in REMAP:
                raise SystemExit('%s line %d: slider %d has no authored mapping'
                                 % (path_in, vi, o))
            n = REMAP[o]
            if n in ENUM:
                if tok not in ENUM[n]:
                    raise SystemExit('%s line %d: slider %d value %r is not in the '
                                     'enum map -- refusing' % (path_in, vi, o, tok))
                tok = ENUM[n][tok]
            elif n in RECIPROCAL:
                v = float(tok)
                if v <= 0:
                    raise SystemExit('%s line %d: slider %d is %r; the reciprocal '
                                     'is undefined -- refusing' % (path_in, vi, o, tok))
                inv = 1.0 / v
                tok = ('%g' % inv)
            new[n] = tok

        rendered = render_line(orig, new, NEW_N)
        back = parse_line(rendered)
        for o, tok in real.items():
            if o in DELETED:
                continue
            n = REMAP[o]
            want = new[n]
            if back.get(n) != want:
                raise SystemExit('%s line %d: slider %d -> %d became %r, wanted %r'
                                 % (path_in, vi, o, n, back.get(n), want))
        lines[vi] = rendered
        count += 1

    if len(lines) != n_before:
        raise SystemExit('%s: line count changed -- refusing' % path_in)
    if count and not dry:
        open(path_out, 'w', encoding='utf-8', newline='').write(''.join(lines))
    return count


def main():
    dry = '--apply' not in sys.argv
    total = 0
    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        if not os.path.exists(live):
            raise SystemExit('live project missing: %s' % live)
        n = convert(os.path.join(SNAP, snapname), live, dry)
        total += n
        print('%-56s %d instance(s)' % (base, n))
    print('\n%s %d instances across %d projects'
          % ('WOULD MIGRATE' if dry else 'MIGRATED', total, len(os.listdir(SNAP))))
    if dry:
        print('re-run with --apply to write')


if __name__ == '__main__':
    main()
