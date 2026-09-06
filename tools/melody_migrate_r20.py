#!/usr/bin/env python3
"""Migrate melody_phase projects to the 2026-09-06 R20/R21 layout
(docs/layouts/melody-phase-r20.md).

The permutation and the enum handling are AUTHORED, transcribed from that
document's "The order" and "The migration" sections. This script only APPLIES
them -- it never infers a mapping, and it refuses rather than guessing whenever
an instance does not look like the layout the table describes.

WHAT MOVES
  * Sliders 3, 4, 5 (`Sync to host`, `Host sync target`, `Every N beats`) are
    DELETED, and a synced instance's beat count is folded into Rate value with
    Rate mode set to 3 (`Every N beats`).
  * `Pan glide` and `Cycle steps` come back from 81/82 into the pan block.
  * Seven new sliders are left ABSENT from the value line so every instance takes
    their declared defaults, which are the off/neutral values by design.

IDEMPOTENT BY CONSTRUCTION: reads the pre-migration SNAPSHOT and writes the live
project, so re-running reproduces the same result rather than permuting an
already-permuted line.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-melody-r20-20260906/
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-melody-r20-20260906'
OLD_N, NEW_N = 82, 86

# --- AUTHORED: old slider id -> new slider id ------------------------------
REMAP = {1: 1, 2: 2}
REMAP.update({o: o - 3 for o in range(6, 18)})     # 6..17  -> 3..14
REMAP.update({18: 15, 19: 16, 20: 17})
REMAP.update({81: 18, 82: 19})                     # pan glide / cycle steps
REMAP.update({21: 20})                             # pan base rate; 21 is NEW
REMAP.update({o: o for o in range(22, 75)})        # 22..74 stand still
REMAP.update({75: 76})                             # drift shape; 75 is NEW
REMAP.update({76: 79, 77: 80})                     # ramp target / by; 81 NEW
REMAP.update({78: 82})                             # ramp duration; 83/84 NEW
REMAP.update({79: 85, 80: 86})                     # ramp engage / start delay

DELETED = {3: 'Sync to host', 4: 'Host sync target', 5: 'Every N beats'}

# Sliders that exist in the new layout but never in the old one. Left ABSENT
# from the value line so REAPER hands each instance the declared default.
NEW_SLIDERS = {21: 'Pan rate mode', 75: 'Drift period unit',
               77: 'Drift play for', 78: 'Drift rest for',
               81: 'Ramp time unit', 83: 'Ramp play for', 84: 'Ramp rest for'}

# The one instance whose beat count reads badly as a beat count. AUTHORED, one
# entry, matched on the exact stored token -- not on a range, not on a rounding
# rule, so nothing else can fall into it by accident.
PER_BEAT = {'0.333333': '3'}


def near(tok, want, tol=1e-9):
    try:
        return abs(float(tok) - want) <= tol
    except (TypeError, ValueError):
        return False


def convert(path_in, path_out, dry, stats):
    raw = open(path_in, 'rb').read()
    lines = raw.decode('utf-8').splitlines(keepends=True)
    n_before = len(lines)
    count = 0

    for i, line in enumerate(lines):
        if not re.search(r'<JS\s+\S*?melody_phase\.jsfx', line):
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
        for k, v in real.items():
            if v.startswith('"'):
                raise SystemExit('%s line %d: slider %d holds a quoted token %r; '
                                 'melody_phase has no file selector -- refusing'
                                 % (path_in, vi, k, v))

        # --- the sync fold, done BEFORE the permutation so it reads in old ids
        sync_tok = real.get(3, '0')
        synced = not near(sync_tok, 0.0) and sync_tok != '-'
        if synced:
            target = real.get(4, '0')
            if not near(target, 0.0):
                # Authored for target 0 only, because all 27 synced instances in
                # the library are on it. A pan-synced instance would need the
                # beat count folded into Pan base rate and its own new Pan rate
                # mode instead -- a different edit, so refuse rather than guess.
                raise SystemExit('%s line %d: synced instance targets the PAN '
                                 '(slider4=%r). The authored migration covers '
                                 'target 0 only -- refusing' % (path_in, vi, target))
            beats = real.get(5)
            if beats is None:
                raise SystemExit('%s line %d: Sync to host is on but no `Every N '
                                 'beats` is stored -- refusing' % (path_in, vi))
            if beats in PER_BEAT:
                real[1], real[2] = PER_BEAT[beats], '4'      # N per beat
                stats['per_beat'] += 1
            else:
                real[1], real[2] = beats, '3'                # Every N beats
                stats['every_n'] += 1
        else:
            stats['free'] += 1
            mode = real.get(2)
            if mode is not None and not near(mode, 0) and not near(mode, 1) \
                                and not near(mode, 2):
                raise SystemExit('%s line %d: free-running instance has Rate mode '
                                 '%r, which is not one of the three old modes -- '
                                 'refusing' % (path_in, vi, mode))

        new = {}
        for o, tok in real.items():
            if o in DELETED:
                continue
            if o not in REMAP:
                raise SystemExit('%s line %d: slider %d has no authored mapping'
                                 % (path_in, vi, o))
            new[REMAP[o]] = tok

        for nid in NEW_SLIDERS:
            if nid in new:
                raise SystemExit('%s line %d: new slider %d (%s) already carries '
                                 'a value -- the permutation is wrong'
                                 % (path_in, vi, nid, NEW_SLIDERS[nid]))

        rendered = render_line(orig, new, NEW_N)
        back = parse_line(rendered)
        for nid, want in new.items():
            if back.get(nid) != want:
                raise SystemExit('%s line %d: slider %d became %r, wanted %r'
                                 % (path_in, vi, nid, back.get(nid), want))
        lines[vi] = rendered
        count += 1
        stats['instances'] += 1

    if len(lines) != n_before:
        raise SystemExit('%s: line count changed %d -> %d -- refusing'
                         % (path_in, n_before, len(lines)))
    if count and not dry:
        open(path_out, 'w', encoding='utf-8', newline='').write(''.join(lines))
    return count


def main():
    dry = '--apply' not in sys.argv
    stats = {'instances': 0, 'free': 0, 'every_n': 0, 'per_beat': 0}
    total = 0
    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        if not os.path.exists(live):
            raise SystemExit('live project missing: %s' % live)
        n = convert(os.path.join(SNAP, snapname), live, dry, stats)
        total += n
        print('%-46s %2d instance(s)' % (base, n))
    print('\n%s %d instances across %d projects'
          % ('WOULD MIGRATE' if dry else 'MIGRATED', total, len(os.listdir(SNAP))))
    print('  free-running, rate block untouched : %d' % stats['free'])
    print('  synced -> Every N beats (mode 3)   : %d' % stats['every_n'])
    print('  synced -> N per beat    (mode 4)   : %d' % stats['per_beat'])
    if dry:
        print('\n(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()
