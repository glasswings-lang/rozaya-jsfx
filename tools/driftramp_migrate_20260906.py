#!/usr/bin/env python3
"""Migrate projects to the 2026-09-06 Drift/Ramp completion layouts.

Each plugin's permutation is AUTHORED below, transcribed from the layout the
source was built to. This script only APPLIES it, and refuses rather than
guessing whenever an instance does not look like the layout the table describes.

New sliders are left ABSENT from the value line so every instance takes their
declared defaults, which are the off/neutral values by design.

IDEMPOTENT BY CONSTRUCTION: reads the pre-migration SNAPSHOT and writes the live
project, so re-running reproduces the same result rather than permuting twice.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-driftramp-20260906/
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-driftramp-20260906'

# ---- AUTHORED, one entry per plugin -----------------------------------------
# heartbeat gen: 28 declared sliders with ids up to 35 and gaps at 17-20/26-28.
# Rate Mode moves 34 -> 2 (R20: the rate pair is adjacent; it was 33 places
# away). The drift block moves to 18-25 and the ramp block to 26-33, both
# gaining their new controls in canonical positions.
HEARTBEAT = {1: 1, 34: 2}
HEARTBEAT.update({o: o + 1 for o in range(2, 17)})
HEARTBEAT.update({21: 18, 22: 19, 23: 20, 24: 21, 25: 23})
HEARTBEAT.update({29: 26, 30: 27, 31: 29, 32: 32, 33: 33, 35: 34})

# sweep-dwell-filter: the ramp block was scattered and out of order (target 26,
# duration 27, engage 28, `by` 29, and start delay stranded at 37). It becomes
# contiguous 26-33 in canonical order; drift moves to 34-41; the five controls
# that sat above the drift block shift up by four.
SWEEPDWELL = {i: i for i in range(1, 27)}
SWEEPDWELL.update({29: 27, 27: 29, 28: 32, 37: 33})
SWEEPDWELL.update({30: 34, 31: 35, 32: 36, 33: 37, 34: 39})
SWEEPDWELL.update({38: 42, 39: 43, 40: 44, 41: 45, 42: 46})

PLUGINS = {
    'sweep-dwell-filter': dict(remap=SWEEPDWELL, old_n=42, new_n=46,
                               new_sliders={28: 'Ramp time unit',
                                            30: 'Ramp play for',
                                            31: 'Ramp rest for',
                                            38: 'Drift period unit',
                                            40: 'Drift play for',
                                            41: 'Drift rest for'}),
    'heartbeat gen': dict(remap=HEARTBEAT, old_n=35, new_n=34,
                          new_sliders={22: 'Drift period unit',
                                       24: 'Drift play for',
                                       25: 'Drift rest for',
                                       28: 'Ramp time unit',
                                       30: 'Ramp play for',
                                       31: 'Ramp rest for'}),
}


def convert(lines, plug, cfg, stats, where):
    """Permute every instance of `plug` in `lines`, in place, and return the
    count. Takes the lines rather than a path so that a project containing TWO
    migrated plugins accumulates both edits -- reading the snapshot per plugin
    would have made the second pass silently discard the first's work. No project
    in the library has two of these today; the shape was wrong anyway."""
    n_before = len(lines)
    count = 0
    pat = re.compile(r'<JS\s+\S*?' + re.escape(plug) + r'\.jsfx')

    for i, line in enumerate(lines):
        if not pat.search(line):
            continue
        vi = i + 1
        orig = lines[vi]
        if not orig.endswith(('\r\n', '\n', '\r')):
            raise SystemExit('%s line %d: value line has no ending -- refusing'
                             % (where, vi))
        old = parse_line(orig)
        real = {k: v for k, v in old.items() if v not in (None, '-')}
        for k, v in real.items():
            if v.startswith('"'):
                raise SystemExit('%s line %d: slider %d holds a quoted token %r -- '
                                 'this plugin has no file selector, refusing'
                                 % (where, vi, k, v))
        if real and max(real) > cfg['old_n']:
            raise SystemExit('%s line %d: real value at slider %d, above the old '
                             'highest id %d -- not the layout this table describes'
                             % (where, vi, max(real), cfg['old_n']))

        new = {}
        for o, tok in real.items():
            if o not in cfg['remap']:
                raise SystemExit('%s line %d: slider %d has no authored mapping'
                                 % (where, vi, o))
            new[cfg['remap'][o]] = tok
        for nid, name in cfg['new_sliders'].items():
            if nid in new:
                raise SystemExit('%s line %d: new slider %d (%s) already carries a '
                                 'value -- the permutation is wrong'
                                 % (where, vi, nid, name))

        rendered = render_line(orig, new, cfg['new_n'])
        back = parse_line(rendered)
        for nid, want in new.items():
            if back.get(nid) != want:
                raise SystemExit('%s line %d: slider %d became %r, wanted %r'
                                 % (where, vi, nid, back.get(nid), want))
        lines[vi] = rendered
        count += 1
        stats['instances'] += 1

    if len(lines) != n_before:
        raise SystemExit('%s: line count changed %d -> %d -- refusing'
                         % (where, n_before, len(lines)))
    return count


def main():
    dry = '--apply' not in sys.argv
    stats = {'instances': 0}
    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        if not os.path.exists(live):
            raise SystemExit('live project missing: %s' % live)
        src = os.path.join(SNAP, snapname)
        lines = open(src, 'rb').read().decode('utf-8').splitlines(keepends=True)
        total = 0
        for plug, cfg in PLUGINS.items():
            total += convert(lines, plug, cfg, stats, src)
        if total and not dry:
            open(live, 'w', encoding='utf-8', newline='').write(''.join(lines))
        print('%-44s %d instance(s)' % (base, total))
    print('\n%s %d instances' % ('MIGRATED' if not dry else 'WOULD MIGRATE',
                                 stats['instances']))
    if dry:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()
