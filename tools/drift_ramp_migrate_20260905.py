#!/usr/bin/env python3
"""Migrate bubbler / dapple / resonance_bank project files to the 2026-09-05
canonical layouts (Part 2 order + transport + full Drift and Ramp).

The permutations below are AUTHORED BY HAND from the layout change, not inferred
from the source. This script only APPLIES them -- see the tooling boundary in
docs/suite-consistency-plan.md, and the reason: a scripted edit spreads one wrong
assumption across every file instantly, and every structural check still passes.

IDEMPOTENT BY CONSTRUCTION: it reads the PRE-MIGRATION SNAPSHOT and writes the
live project, so re-running reproduces the same result rather than permuting an
already-permuted line. That matters here because these plugins' old and new
layouts overlap in range -- a "has it already been done?" test on the line itself
would be guesswork, and guesswork is what ate a line per instance on 2026-09-02.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-drift-ramp-20260905/
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-drift-ramp-20260905'

# --- AUTHORED: old slider id -> new slider id. Anything absent is DROPPED. ---
PLUGINS = {
    'bubbler': dict(
        old_n=11, new_n=30,
        remap={1: 1, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 2},
        dropped={11: 'Host ratio (retired)'},
        value_remap={},
    ),
    'dapple': dict(
        old_n=13, new_n=32,
        remap={1: 1, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 11, 9: 12,
               10: 9, 11: 10, 12: 2},
        dropped={13: 'Host ratio (retired)'},
        value_remap={},
    ),
    'resonance_bank': dict(
        old_n=17, new_n=27,
        remap={1: 1, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9,
               9: 12, 10: 13, 11: 14, 12: 15, 13: 16, 14: 17,
               15: 2, 16: 10, 17: 11},
        dropped={},
        # Drift period mode: the enum went {BPM,Hz,Seconds,Host x} ->
        # {BPM,Seconds,Hz,Host x}, so the two middle entries swap. Keyed by the
        # NEW slider id, applied after the position remap. The @serialize blob
        # carries the same swap for the per-band bank; this is the visible one.
        value_remap={16: {'1': '2', '2': '1'}},
    ),
}

# live path -> snapshot filename, and the instance count this file MUST contain
FILES = [
    ('E:/reaper/finished/birdsong-2.RPP', 'finished__birdsong-2.RPP', {'bubbler': 3}),
    ('E:/reaper/finished/birdsong.RPP', 'finished__birdsong.RPP', {'bubbler': 2}),
    ('E:/reaper/finished/the-sound-of-a-drain.RPP', 'finished__the-sound-of-a-drain.RPP', {'bubbler': 5}),
    ('E:/reaper/finished/bubbles.RPP', 'finished__bubbles.RPP', {'dapple': 11}),
    ('E:/reaper/to-play-with-later/womb-bubbles-proto.RPP', 'to-play-with-later__womb-bubbles-proto.RPP', {'dapple': 3}),
    ('E:/reaper/to-play-with-later/wind.RPP', 'to-play-with-later__wind.RPP', {'resonance_bank': 1}),
]

JS_RE = re.compile(r'<JS\s+\S*?([A-Za-z0-9_\- ]+?)\.jsfx')


def migrate(src, dst, expect, dry):
    raw = open(src, 'rb').read()
    lines = raw.decode('utf-8').splitlines(keepends=True)
    n_before = len(lines)
    counts = {}

    for i, line in enumerate(lines):
        m = JS_RE.search(line)
        if not m or m.group(1) not in PLUGINS:
            continue
        name = m.group(1)
        cfg = PLUGINS[name]
        vi = i + 1
        orig = lines[vi]
        if not orig.endswith(('\r\n', '\n', '\r')):
            raise SystemExit('%s line %d: value line has no ending -- refusing' % (src, vi))

        old = parse_line(orig)
        real = {k: v for k, v in old.items() if v not in (None, '-')}
        if real and max(real) > cfg['old_n']:
            raise SystemExit('%s line %d: %s has a real value at slider %d, above the '
                             'old count of %d -- this is not the layout this table '
                             'describes. Refusing.' % (src, vi, name, max(real), cfg['old_n']))

        new = {}
        for o, tok in old.items():
            if o in cfg['dropped'] or tok in (None, '-'):
                continue
            if o not in cfg['remap']:
                raise SystemExit('%s line %d: slider %d has no authored mapping' % (src, vi, o))
            new[cfg['remap'][o]] = tok
        for sid, table in cfg['value_remap'].items():
            if sid in new and new[sid] in table:
                new[sid] = table[new[sid]]

        rendered = render_line(orig, new, cfg['new_n'])
        back = parse_line(rendered)
        for o, tok in real.items():
            if o in cfg['dropped']:
                continue
            n = cfg['remap'][o]
            want = cfg['value_remap'].get(n, {}).get(tok, tok)
            if back.get(n) != want:
                raise SystemExit('%s line %d: slider %d -> %d became %r, wanted %r'
                                 % (src, vi, o, n, back.get(n), want))
        lines[vi] = rendered
        counts[name] = counts.get(name, 0) + 1

    if counts != expect:
        raise SystemExit('%s: found %r instances, authored table says %r -- refusing'
                         % (src, counts, expect))
    if len(lines) != n_before:
        raise SystemExit('%s: line count changed -- refusing' % src)
    if not dry:
        open(dst, 'w', encoding='utf-8', newline='').write(''.join(lines))
    return counts


def main():
    dry = '--apply' not in sys.argv
    total = 0
    for live, snapname, expect in FILES:
        src = os.path.join(SNAP, snapname)
        if not os.path.exists(src):
            raise SystemExit('missing snapshot: %s' % src)
        counts = migrate(src, live, expect, dry)
        total += sum(counts.values())
        print('%-42s %s' % (os.path.basename(live),
                            ', '.join('%d x %s' % (v, k) for k, v in sorted(counts.items()))))
    print('\n%s %d instances across %d projects' %
          ('WOULD MIGRATE' if dry else 'MIGRATED', total, len(FILES)))
    if dry:
        print('re-run with --apply to write')


if __name__ == '__main__':
    main()
