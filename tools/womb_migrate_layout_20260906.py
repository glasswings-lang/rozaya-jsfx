#!/usr/bin/env python3
"""Migrate Womb v3 projects to the 2026-09-06 authored layout.

The permutation and every value rule below is AUTHORED in docs/layouts/womb.md.
This script only APPLIES them, and refuses rather than guessing whenever an
instance does not look like what the table describes.

Three things happen, and only the first is a plain move:

  1. 60 controls change position; two retire; ten are new. 64 sliders -> 70,
     which crosses the point where a REAPER value line grows a quoted marker at
     token index 64. rpp_sliders.py handles that and is not re-derived here.

  2. R20 conversion for host-mode instances. `Rate Mode = Host x` becomes
     `Heart rate mode = Every N beats`, and the rate VALUE becomes the beat
     count that used to live in the separate `Every N beats` slider. The stored
     Heart rate in host mode was a derived READOUT, not a setting, so carrying
     it across as BPM would be wrong twice over.

  3. The one instance that relied on a LOAD-TIME conversion. Six of the nine
     instances carry the oldest blob (2100010); the plugin's seeding block --
     gated on host mode, so it fired for exactly one of them -- converted heart
     rate, the four breath segments and Systole on every open. That block is
     removed by this change, so the conversion is done ONCE here instead, with
     the same arithmetic and against the project's own tempo.

IDEMPOTENT BY CONSTRUCTION: reads the pre-migration SNAPSHOT and writes the live
project, so re-running reproduces the same result rather than converting twice.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-womb-layout-20260906/
"""
import base64
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-womb-layout-20260906'
PLUG = 'womb_sound_generator_v3'
OLD_N, NEW_N = 64, 70

# ---- AUTHORED: old slider -> new slider -------------------------------------
REMAP = {
    1: 1, 62: 2, 59: 3, 5: 4,
    11: 6, 9: 7, 6: 8, 12: 9, 10: 10, 7: 11, 8: 12, 13: 13, 3: 14, 4: 15,
    53: 16,
    16: 18, 17: 19, 18: 20, 19: 21, 20: 22, 21: 23,
    23: 24, 24: 25, 25: 26, 26: 27, 27: 28,
    22: 29, 39: 30, 40: 31, 60: 32, 61: 33, 28: 34, 14: 35, 15: 36,
    34: 39, 35: 40, 32: 41, 31: 42, 33: 43, 36: 44, 29: 45, 30: 46,
    2: 47, 41: 48, 42: 49, 43: 50, 44: 51, 45: 52, 46: 53, 47: 54,
    54: 55, 55: 56, 56: 57, 57: 58, 58: 60,
    48: 63, 49: 64, 50: 66, 51: 69, 52: 70,
}
RETIRED = {63: 'Host sync target', 64: 'Every N beats'}
NEW_SLIDERS = {5: 'Systole unit', 17: 'Breath rate mode', 37: 'Bloodflow offset',
               38: 'Bloodflow offset unit', 59: 'Drift period unit',
               61: 'Drift play for', 62: 'Drift rest for', 65: 'Ramp time unit',
               67: 'Ramp play for', 68: 'Ramp rest for'}

OLD_RATE_MODE, OLD_BEATS, OLD_HEART = 62, 64, 1
OLD_SEGS = (16, 17, 18, 19)
OLD_SYSTOLE, OLD_BPM = 5, 53

NEW_HEART, NEW_HEART_MODE, NEW_SYS, NEW_SYS_UNIT = 1, 2, 4, 5
NEW_BPM, NEW_BREATH_MODE = 16, 17
NEW_SEGS = (18, 19, 20, 21)

MODE_EVERY_N_BEATS = 3
SYS_UNIT_MS, SYS_UNIT_BEATS = 0, 2

# blob magics whose instances were converted on LOAD by the seeding block
SEEDING_MAGICS = (2100010, 2200010)

assert set(REMAP) | set(RETIRED) == set(range(1, 37)) | set(range(39, 65)), 'map does not cover the old sliders'
assert len(set(REMAP.values())) == len(REMAP), 'two old sliders share a new id'
assert set(REMAP.values()) | set(NEW_SLIDERS) == set(range(1, NEW_N + 1)), 'result is not 1..%d' % NEW_N


def project_tempo(lines):
    for l in lines:
        m = re.match(r'\s*TEMPO\s+([0-9.]+)', l)
        if m:
            return float(m.group(1))
    return 120.0


def blob_magic(lines, at):
    started = False
    b = []
    for j in range(at, min(at + 60, len(lines))):
        t = lines[j].strip()
        if t == '<JS_SER':
            started = True
            continue
        if started:
            if t == '>':
                break
            b.append(t)
    if not b:
        return None
    try:
        return round(struct.unpack('<f', base64.b64decode(''.join(b))[:4])[0])
    except Exception:
        return None


def num(vals, sid, default):
    v = vals.get(sid)
    if v in (None, '-'):
        return float(default)
    return float(v)


def convert(lines, stats, where):
    n_before = len(lines)
    tempo = project_tempo(lines)
    pat = re.compile(r'<JS\s+\S*?' + re.escape(PLUG) + r'\.jsfx')
    count = 0

    for i, line in enumerate(lines):
        if not pat.search(line):
            continue
        vi = i + 1
        orig = lines[vi]
        if not orig.endswith(('\r\n', '\n', '\r')):
            raise SystemExit('%s line %d: value line has no ending -- refusing' % (where, vi))
        old = parse_line(orig)
        real = {k: v for k, v in old.items() if v not in (None, '-')}
        for k, v in real.items():
            if v.startswith('"'):
                raise SystemExit('%s line %d: slider %d holds a quoted token %r -- refusing'
                                 % (where, vi, k, v))
        if real and max(real) > OLD_N:
            raise SystemExit('%s line %d: value at slider %d, above the old highest id %d -- '
                             'already migrated, or not this layout' % (where, vi, max(real), OLD_N))

        magic = blob_magic(lines, vi)
        host = num(real, OLD_RATE_MODE, 0) == 1
        seeded = host and magic in SEEDING_MAGICS

        # --- plain positional move ------------------------------------------
        new = {}
        for o, tok in real.items():
            if o in RETIRED:
                continue
            if o not in REMAP:
                raise SystemExit('%s line %d: slider %d has no authored mapping' % (where, vi, o))
            new[REMAP[o]] = tok

        # --- value rules -----------------------------------------------------
        note = 'plain'
        if host:
            # R20: the rate VALUE carries the beat count; the stored Heart rate
            # was a readout of it, not a setting.
            beats = num(real, OLD_BEATS, 1)
            if seeded:
                # The load-time conversion this migration replaces, verbatim:
                #   host_beats = clamp(1 / heart_rate, 0.25, 64)   [2100000 blobs]
                #   segments  *= tempo/60 ; systole *= tempo/60 * 0.001
                beats = max(0.25, min(64, 1.0 / max(num(real, OLD_HEART, 1), 0.0001)))
                br_u = tempo / 60.0
                for o, nn in zip(OLD_SEGS, NEW_SEGS):
                    lo = 0.02 if o in (16, 18) else 0.0
                    new[nn] = fmt(min(64, max(lo, num(real, o, 0) * br_u)))
                new[NEW_SYS] = fmt(min(1000, max(0.01, num(real, OLD_SYSTOLE, 120) * br_u * 0.001)))
                note = 'seeded+R20'
            else:
                note = 'R20'
            new[NEW_HEART] = fmt(beats)
            new[NEW_HEART_MODE] = str(MODE_EVERY_N_BEATS)
            new[NEW_BREATH_MODE] = str(MODE_EVERY_N_BEATS)
            new[NEW_SYS_UNIT] = str(SYS_UNIT_BEATS)
            # `Breaths per minute` was HIDDEN in host mode and inert (its rescale
            # only fired on a change). Under the new layout it is a live rate, so
            # a leftover value would suddenly mean something. Zero it: 0 is
            # "the segments decide", which is exactly what was happening.
            new[NEW_BPM] = '0'
        else:
            new[NEW_HEART_MODE] = '0'      # BPM, which is what it already was
            new[NEW_BREATH_MODE] = '0'
            new[NEW_SYS_UNIT] = str(SYS_UNIT_MS)

        for nid in NEW_SLIDERS:
            if nid not in new:
                continue   # left absent on purpose -> declared default

        rendered = render_line(orig, new, NEW_N)
        back = parse_line(rendered)
        for nid, want in new.items():
            if back.get(nid) != want:
                raise SystemExit('%s line %d: slider %d became %r, wanted %r'
                                 % (where, vi, nid, back.get(nid), want))
        lines[vi] = rendered
        count += 1
        stats['instances'] += 1
        stats['notes'].append('%-46s tempo=%-5g blob=%-8s %s'
                              % (os.path.basename(where), tempo, magic, note))

    if len(lines) != n_before:
        raise SystemExit('%s: line count changed %d -> %d -- refusing' % (where, n_before, len(lines)))
    return count


def fmt(v):
    """Match REAPER's own token style: no trailing zeros, no exponent."""
    s = ('%.6f' % v).rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


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
        src = os.path.join(SNAP, snapname)
        lines = open(src, 'rb').read().decode('utf-8').splitlines(keepends=True)
        n = convert(lines, stats, src)
        if n and not dry:
            open(live, 'w', encoding='utf-8', newline='').write(''.join(lines))
        if n:
            projects += 1
        print('%-48s %d instance(s)' % (base, n))
    print()
    for note in stats['notes']:
        print('   ', note)
    print()
    print('%s %d instances in %d projects'
          % ('MIGRATED' if not dry else 'WOULD MIGRATE', stats['instances'], projects))
    if dry:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()
