#!/usr/bin/env python3
"""Migrate Womb v3 projects across the 2026-09-06 (evening) breath follow-up.

VALUES ONLY -- no slider moves, no count change, still 70. Three controls change
meaning, and every rule below is AUTHORED in docs/layouts/womb.md.

  16  `Breaths per minute` -> `Set breath rate`, a ONE-SHOT that zeroes itself.
      A stored value is meaningless now, so it is zeroed. Safe, and measured:
      every instance holding a non-zero rate already has segments summing to
      exactly the cycle it asks for, so nothing it would have done is lost.

  17  `Breath rate mode` {BPM,Seconds,Hz,Every N beats,N per beat}
      -> `Breath unit` {Seconds,Beats}. Either host mode meant the segments read
      as BEATS, so 3 and 4 become Beats(1); everything else becomes Seconds(0).

  33  `Sigh depth multiplier` (x) -> `Sigh extra length` (+, in breath units).
      extra = total * (multiplier - 1), where total is the four segments' sum.
      A 1.5x sigh on a 12-unit breath is a breath 6 units longer: same sound.

IDEMPOTENT BY CONSTRUCTION: reads the pre-change SNAPSHOT, writes the live file.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-womb-breath-20260906b/
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-womb-breath-20260906b'
PLUG = 'womb_sound_generator_v3'
N = 70
SET_RATE, BREATH_UNIT, SIGH = 16, 17, 33
SEGS = (18, 19, 20, 21)
SEG_DEFAULTS = {18: 4.0, 19: 0.3, 20: 4.0, 21: 0.3}


def fmt(v):
    s = ('%.6f' % v).rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def num(vals, sid, default):
    v = vals.get(sid)
    return float(default) if v in (None, '-') else float(v)


def convert(lines, stats, where):
    n_before = len(lines)
    pat = re.compile(r'<JS\s+\S*?' + re.escape(PLUG) + r'\.jsfx')
    count = 0
    for i, line in enumerate(lines):
        if not pat.search(line):
            continue
        vi = i + 1
        orig = lines[vi]
        if not orig.endswith(('\r\n', '\n', '\r')):
            raise SystemExit('%s line %d: value line has no ending -- refusing' % (where, vi))
        vals = parse_line(orig)
        real = {k: v for k, v in vals.items() if v not in (None, '-')}
        for k, v in real.items():
            if v.startswith('"'):
                raise SystemExit('%s line %d: slider %d holds a quoted token' % (where, vi, k))
        if real and max(real) > N:
            raise SystemExit('%s line %d: value at slider %d, above %d -- not this layout'
                             % (where, vi, max(real), N))
        if BREATH_UNIT not in real:
            raise SystemExit('%s line %d: no breath rate mode stored -- this project has not '
                             'had the first 2026-09-06 migration' % (where, vi))

        new = dict(real)
        old_rate = num(real, SET_RATE, 0)
        old_mode = num(real, BREATH_UNIT, 0)
        segs = [num(real, s, SEG_DEFAULTS[s]) for s in SEGS]
        total = sum(segs)

        # 16: a stored rate is meaningless for a one-shot. Assert first that it
        # was a no-op, so a project where it WOULD have rescaled cannot be
        # silently flattened.
        if old_rate > 0 and old_mode < 3:
            want = 60.0 / old_rate
            if abs(total - want) > 1e-3:
                raise SystemExit('%s line %d: stored breath rate %g wants a cycle of %.4f but '
                                 'the segments sum to %.4f -- zeroing it WOULD change the sound. '
                                 'Refusing; this needs a decision, not a script.'
                                 % (where, vi, old_rate, want, total))
        new[SET_RATE] = '0'

        # 17: five rate modes collapse to two units. >= 3 is either host mode.
        new[BREATH_UNIT] = '1' if old_mode >= 3 else '0'

        # 33: multiplier -> additive extra, same resulting sigh length.
        old_mult = num(real, SIGH, 1.5)
        new[SIGH] = fmt(max(0.0, min(1000.0, total * (old_mult - 1.0))))

        rendered = render_line(orig, new, N)
        back = parse_line(rendered)
        for sid, want in new.items():
            if back.get(sid) != want:
                raise SystemExit('%s line %d: slider %d became %r wanted %r'
                                 % (where, vi, sid, back.get(sid), want))
        lines[vi] = rendered
        count += 1
        stats['instances'] += 1
        stats['notes'].append('%-44s rate %-6s mode %s->%s   sigh %sx -> +%s (total %.3f)'
                              % (os.path.basename(where).split('__', 1)[1],
                                 old_rate, int(old_mode), new[BREATH_UNIT],
                                 old_mult, new[SIGH], total))
    if len(lines) != n_before:
        raise SystemExit('%s: line count changed -- refusing' % where)
    return count


def main():
    dry = '--apply' not in sys.argv
    stats = {'instances': 0, 'notes': []}
    snaps = sorted(os.listdir(SNAP))
    if not snaps:
        raise SystemExit('no snapshot at %s' % SNAP)
    projects = 0
    for snapname in snaps:
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        if not os.path.exists(live):
            raise SystemExit('live project missing: %s' % live)
        lines = open(os.path.join(SNAP, snapname), 'rb').read().decode('utf-8').splitlines(keepends=True)
        n = convert(lines, stats, os.path.join(SNAP, snapname))
        if n and not dry:
            open(live, 'w', encoding='utf-8', newline='').write(''.join(lines))
        if n:
            projects += 1
    for note in stats['notes']:
        print('   ', note)
    print()
    print('%s %d instances in %d projects'
          % ('MIGRATED' if not dry else 'WOULD MIGRATE', stats['instances'], projects))
    if dry:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()
