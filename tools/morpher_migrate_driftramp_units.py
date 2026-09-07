#!/usr/bin/env python3
"""Migrate Spectral Vowel Morpher projects to the 2026-09-06 unit-control layout.

The permutation is AUTHORED in docs/layouts/spectral-vowel-morpher.md (section
"Second layout change, 2026-09-06"). This script only APPLIES it, and refuses
rather than guessing whenever an instance does not look like the layout the
table describes.

`Drift period unit` (39) and `Ramp time unit` (46) are left ABSENT from the
value line so every instance takes their DECLARED defaults -- Seconds and
Minutes respectively -- which are exactly what those times already meant. No
instance changes what it sounds like.

IDEMPOTENT BY CONSTRUCTION: reads the pre-migration SNAPSHOT and writes the live
project, so re-running reproduces the same result rather than permuting twice.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-morpher-units-20260906/
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-morpher-units-20260906'
PLUG = 'spectral_vowel_morpher'
OLD_N, NEW_N = 49, 51

# ---- AUTHORED ---------------------------------------------------------------
# Everything up to Drift period (38) keeps its place. Drift period unit is new
# at 39, so the drift tail and the whole ramp group shift up one; Ramp time unit
# is new at 46, so Ramp duration onward shift up one more.
REMAP = {i: i for i in range(1, 39)}
REMAP.update({39: 40, 40: 41, 41: 42, 42: 43, 43: 44, 44: 45})
REMAP.update({45: 47, 46: 48, 47: 49, 48: 50, 49: 51})

NEW_SLIDERS = {39: 'Drift period unit', 46: 'Ramp time unit'}

# Sanity on the table itself, before it touches a single file.
assert len(REMAP) == OLD_N, 'remap covers %d of %d old sliders' % (len(REMAP), OLD_N)
assert len(set(REMAP.values())) == OLD_N, 'remap sends two sliders to one place'
assert set(REMAP.values()) | set(NEW_SLIDERS) == set(range(1, NEW_N + 1)), \
    'remap plus the new sliders do not cover 1..%d exactly' % NEW_N


def convert(lines, stats, where):
    """Permute every Morpher instance in `lines`, in place. Returns the count."""
    n_before = len(lines)
    count = 0
    pat = re.compile(r'<JS\s+\S*?' + re.escape(PLUG) + r'\.jsfx')

    for i, line in enumerate(lines):
        if not pat.search(line):
            continue
        vi = i + 1
        orig = lines[vi]
        # The ending is NOT covered by render_line's round-trip check, and a
        # caller using keepends once welded a value line onto the '>' that closes
        # the <JS> block -- 36 lines silently lost. Refuse instead.
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
        if real and max(real) > OLD_N:
            raise SystemExit('%s line %d: real value at slider %d, above the old '
                             'highest id %d -- already migrated, or not the layout '
                             'this table describes' % (where, vi, max(real), OLD_N))

        new = {}
        for o, tok in real.items():
            if o not in REMAP:
                raise SystemExit('%s line %d: slider %d has no authored mapping'
                                 % (where, vi, o))
            new[REMAP[o]] = tok
        for nid, name in NEW_SLIDERS.items():
            if nid in new:
                raise SystemExit('%s line %d: new slider %d (%s) already carries a '
                                 'value -- the permutation is wrong'
                                 % (where, vi, nid, name))

        rendered = render_line(orig, new, NEW_N)
        back = parse_line(rendered)
        for nid, want in new.items():
            if back.get(nid) != want:
                raise SystemExit('%s line %d: slider %d became %r, wanted %r'
                                 % (where, vi, nid, back.get(nid), want))
        for nid in NEW_SLIDERS:
            if back.get(nid) not in (None, '-'):
                raise SystemExit('%s line %d: new slider %d came back as %r -- it '
                                 'must be absent so the declared default applies'
                                 % (where, vi, nid, back.get(nid)))
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
    snaps = sorted(os.listdir(SNAP))
    if not snaps:
        raise SystemExit('no snapshot at %s' % SNAP)
    projects = 0
    for snapname in snaps:
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        if not os.path.exists(live):
            raise SystemExit('live project missing: %s' % live)
        src = os.path.join(SNAP, snapname)
        lines = open(src, 'rb').read().decode('utf-8').splitlines(keepends=True)
        n = convert(lines, stats, src)
        if n and not dry:
            open(live, 'w', encoding='utf-8', newline='').write(''.join(lines))
        if n:
            projects += 1
        print('%-48s %d instance(s)' % (base, n))
    print('\n%s %d instances in %d projects'
          % ('MIGRATED' if not dry else 'WOULD MIGRATE', stats['instances'], projects))
    if dry:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()
