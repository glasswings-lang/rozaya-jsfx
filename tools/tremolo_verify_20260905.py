#!/usr/bin/env python3
"""Verify the Full Feature Tremolo's 2026-09-05 reorder by decoding control NAMES.

Deliberately does NOT use the migration's permutation table -- that would agree
with itself perfectly. It reads the OLD plugin build (backed up out of the
Effects folder before installing) and the NEW source, maps every stored value to
the control name it belongs to on each side, and compares name-for-name.

Also range-checks every migrated value against its new slider's declared min/max.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-tremolo-reorder-20260905'
OLDSRC = ('C:/Users/solst/jsfx-backups/effects-folder-baks/'
          'pre-tremolo-reorder-20260905/Full_Feature_Tremolo.jsfx')
NEWSRC = 'src/Full_Feature_Tremolo.jsfx'

RENAMED = {
    'Pan Sweep Rate Unit': 'Pan sweep rate mode',
    'Filter Speed Multiplier (Linked Sweep)': 'Pan sweep every (cycles)',
}
RETIRED = {'Host ratio (retired)', 'Pan speed (Linked Sweep)'}
# name -> function turning the OLD stored token into what the NEW one must be
TRANSFORM = {
    'Pan sweep rate mode': lambda t: {'0': '2', '1': '1', '2': '0'}[t],
    'Pan sweep every (cycles)': lambda t: '%g' % (1.0 / float(t)),
}

DECL = re.compile(r'^slider(\d+):([^<]*)<([^,]*),([^,]*),([^>]*)>(.*)$')
JS = re.compile(r'<JS\s+\S*?Full_Feature_Tremolo\.jsfx')


def decls(path):
    out = {}
    for line in open(path, encoding='utf-8'):
        m = DECL.match(line)
        if m:
            try:
                lo, hi = float(m.group(3)), float(m.group(4))
            except ValueError:
                lo = hi = None
            out[int(m.group(1))] = (m.group(6).strip(), lo, hi)
    return out


def rows(path):
    lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
    return [parse_line(lines[i + 1]) for i, l in enumerate(lines) if JS.search(l)]


def main():
    old_d, new_d = decls(OLDSRC), decls(NEWSRC)
    checks = bad = oor = 0
    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        before = rows(os.path.join(SNAP, snapname))
        after = rows('E:/reaper/%s/%s' % (folder, base))
        assert len(before) == len(after), (base, len(before), len(after))
        for vb, va in zip(before, after):
            bn = {old_d[s][0]: t for s, t in vb.items()
                  if t not in (None, '-') and s in old_d}
            an = {}
            for s, t in va.items():
                if t in (None, '-') or s not in new_d:
                    continue
                name, lo, hi = new_d[s]
                an[name] = t
                if lo is not None and not (lo <= float(t) <= hi):
                    print('  OUT OF RANGE  %-40s = %s (declared %s..%s)'
                          % (name, t, lo, hi))
                    oor += 1
            for name, tok in bn.items():
                if name in RETIRED:
                    continue
                want_name = RENAMED.get(name, name)
                want = TRANSFORM[want_name](tok) if want_name in TRANSFORM else tok
                got = an.get(want_name)
                checks += 1
                if got != want:
                    print('  MISMATCH  %-28s %-40s before=%r after=%r'
                          % (base, want_name, want, got))
                    bad += 1
    print('\n%d value comparisons by control NAME across %d projects'
          % (checks, len(os.listdir(SNAP))))
    print('%d mismatches, %d values outside their declared range' % (bad, oor))
    print('RESULT:', 'PASS' if bad == 0 and oor == 0 else 'FAIL')


if __name__ == '__main__':
    main()
