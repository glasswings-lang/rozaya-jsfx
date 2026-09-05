#!/usr/bin/env python3
"""Verify the 2026-09-05 drift/ramp migration by decoding control NAMES.

Deliberately does NOT use the migration's permutation table -- that would agree
with itself perfectly, which is how the 2026-09-02 Melody break slipped through.
Instead it reads the OLD plugin sources (the builds backed up out of the Effects
folder before installing) and the NEW ones from src/, maps each stored value to
the control NAME it belongs to on each side, and compares name-for-name.

Also range-checks every migrated value against its new slider's declared min/max,
which is the cheapest possible proof that a mapping shifted and needs no ears.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-drift-ramp-20260905'
OLDSRC = 'C:/Users/solst/jsfx-backups/effects-folder-baks/pre-drift-ramp-20260905'
NEWSRC = 'src'

# Controls whose NAME changed in the same pass. Old label -> new label.
RENAMED = {
    'Timing randomness %': 'Timing randomness (%)',
    'Stereo width %': 'Stereo width (%)',
    'Dry/Wet %': 'Dry/wet (%)',
    'Pitch spread %': 'Pitch spread (%)',
    'Rise %': 'Rise (%)',
    'Tone vs Noise % (0=noise, 100=tone plink)': 'Tone vs noise (%, 0 = noise, 100 = tone plink)',
    'Excite from input % (0=internal noise, 100=input)': 'Excite from input (%, 0 = internal noise, 100 = input)',
    'Rate Mode': 'Rate mode',
    'Input Gain (dB)': 'Input gain (dB)',
    'Wet/Dry mix': 'Wet/dry mix',
    'Output Volume': 'Output volume',
    'Drift period (BPM / Hz / sec / beats per cycle by mode; 0 = off)':
        'Drift period (BPM / sec / Hz / beats per cycle by mode; 0 = off)',
}
# Controls that are GONE on purpose, and must therefore not be compared.
RETIRED = {'Host ratio (writes Bubble rate)'}

DECL = re.compile(r'^slider(\d+):([^<]*)<([^,]*),([^,]*),([^>]*)>(.*)$')
JS_RE = re.compile(r'<JS\s+\S*?([A-Za-z0-9_\- ]+?)\.jsfx')

FILES = [
    ('E:/reaper/finished/birdsong-2.RPP', 'finished__birdsong-2.RPP'),
    ('E:/reaper/finished/birdsong.RPP', 'finished__birdsong.RPP'),
    ('E:/reaper/finished/the-sound-of-a-drain.RPP', 'finished__the-sound-of-a-drain.RPP'),
    ('E:/reaper/finished/bubbles.RPP', 'finished__bubbles.RPP'),
    ('E:/reaper/to-play-with-later/womb-bubbles-proto.RPP', 'to-play-with-later__womb-bubbles-proto.RPP'),
    ('E:/reaper/to-play-with-later/wind.RPP', 'to-play-with-later__wind.RPP'),
]
PLUGINS = ('bubbler', 'dapple', 'resonance_bank')

# Values that legitimately change: the Drift period mode enum was reordered.
ENUM_MOVED = {('resonance_bank', 'Drift period mode'): {'1': '2', '2': '1'}}


def decl_map(path):
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


def instances(path):
    lines = open(path, encoding='utf-8').read().splitlines()
    for i, l in enumerate(lines):
        m = JS_RE.search(l)
        if m and m.group(1) in PLUGINS:
            yield m.group(1), parse_line(lines[i + 1])


def main():
    old_d = {p: decl_map(os.path.join(OLDSRC, p + '.jsfx')) for p in PLUGINS}
    new_d = {p: decl_map(os.path.join(NEWSRC, p + '.jsfx')) for p in PLUGINS}

    checks = mismatches = oor = 0
    for live, snapname in FILES:
        before = list(instances(os.path.join(SNAP, snapname)))
        after = list(instances(live))
        assert len(before) == len(after), (live, len(before), len(after))
        for (pb, vb), (pa, va) in zip(before, after):
            assert pb == pa, (live, pb, pa)
            byname_before = {}
            for sid, tok in vb.items():
                if tok in (None, '-') or sid not in old_d[pb]:
                    continue
                byname_before[old_d[pb][sid][0]] = tok
            byname_after = {}
            for sid, tok in va.items():
                if tok in (None, '-') or sid not in new_d[pa]:
                    continue
                name, lo, hi = new_d[pa][sid]
                byname_after[name] = tok
                if lo is not None and not (lo <= float(tok) <= hi):
                    print('  OUT OF RANGE  %s  %s = %s (declared %s..%s)'
                          % (pa, name, tok, lo, hi))
                    oor += 1
            for name, tok in byname_before.items():
                if name in RETIRED:
                    continue
                want_name = RENAMED.get(name, name)
                want = ENUM_MOVED.get((pb, want_name), {}).get(tok, tok)
                got = byname_after.get(want_name)
                checks += 1
                if got != want:
                    print('  MISMATCH  %s  %-45s before=%r after=%r'
                          % (os.path.basename(live), want_name, want, got))
                    mismatches += 1

    print('\n%d value comparisons by control NAME across %d projects'
          % (checks, len(FILES)))
    print('%d mismatches, %d values outside their declared range' % (mismatches, oor))
    print('RESULT:', 'PASS' if mismatches == 0 and oor == 0 else 'FAIL')


if __name__ == '__main__':
    main()
