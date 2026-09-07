#!/usr/bin/env python3
"""Migrate Polyrhythm Phase v3 projects to the 2026-09-07 authored layout.

The permutation and every value rule below is AUTHORED in
docs/layouts/polyrhythm-phase-v3.md. This script only APPLIES them, and refuses
rather than guessing whenever an instance does not look like what the table
describes.

Two things happen, and only the first is a plain move:

  1. 90 sliders become 56. Most of that is a reorder, but 42 of the removed
     sliders are V2-V8's per-voice controls, which stop being sliders at all --
     the voices now live behind a Voice selector.

  2. THE BLOB IS REWRITTEN, which no migration in this repo has had to do
     before. V2-V8's forty-two values move OFF the slider line and INTO twelve
     new @serialize banks, alongside the four new drift/ramp play-rest banks.
     An instance whose blob is not rewritten would come up with one voice.

VALUES THAT CHANGE MEANING, and what is written so the project still sounds
like itself:

  * Waveform, Depth dB, On Duration, Attack % and Release % were GLOBAL and are
    now per-voice. Each one's old global value is written to ALL EIGHT voices,
    which is exactly what the plugin was doing before.
  * `Pan rate mode` is new and its declared default (0 = BPM) is a LIVE VALUE
    for any instance that never touches it. The pan used to borrow the tremolo
    Rate Mode, so this instance's actual Rate Mode is written into it. Relying
    on the default would silently re-time every host-synced pan.
  * `Voice` is seeded to 1, NOT to its declared default of 0 (All). A fresh
    instance has eight identical voices, so All is harmless there; a migrated
    one has eight configured voices, and parking the selector on All would mean
    one stray nudge writes across all of them. The declared default is right
    for a new instance and wrong for this one.
  * The six new drift/ramp controls take their declared defaults, which are the
    off/no-change values (Drift period unit = Cycles, Ramp time unit = Minutes,
    all four play/rest = 0).

IDEMPOTENT BY CONSTRUCTION: reads the pre-migration SNAPSHOT and writes the
live project, so re-running reproduces the same result rather than converting
twice.

Snapshot: E:/reaper/finished/backups/snapshots/_pre-polyv3-layout-20260907/
"""
import base64
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-polyv3-layout-20260907'
PLUG = 'polyrhythm_phase_v3'
OLD_N, NEW_N = 90, 56
N_TARGETS = 24
OLD_MAGIC = 2100000 + N_TARGETS      # 2100024
NEW_MAGIC = 2200000 + N_TARGETS      # 2200024

# ---- AUTHORED: old slider -> new slider (globals and voice 1) ---------------
# Voice 1's five own controls become the selector's editing slots; the five
# controls that went per-voice land in the voice block at their new positions.
REMAP = {
    1: 1, 3: 2, 2: 3, 8: 4, 9: 5,
    11: 6, 12: 7, 13: 8, 4: 9, 15: 10,
    16: 11, 17: 12, 18: 13, 19: 14,
    26: 16, 27: 17, 28: 18, 29: 19,      # V1 note / fine / drift / phase
    14: 20,                              # Waveform      (was global)
    10: 21,                              # Depth dB      (was global)
    5: 22,                               # On Duration   (was global)
    6: 23,                               # Attack %      (was global)
    7: 24,                               # Release %     (was global)
    25: 25, 30: 26,                      # V1 gain / active
    20: 28, 21: 29, 22: 30, 23: 31, 24: 33,
    90: 34, 89: 35,
    73: 36, 74: 37, 75: 38, 76: 39, 77: 40,
    41: 41, 42: 42, 43: 43, 44: 44, 46: 46,   # placeholder, overwritten below
}
# The drift/ramp block, written out rather than left to a pattern.
REMAP.update({78: 41, 79: 42, 80: 43, 81: 44, 82: 46,
              83: 49, 84: 50, 85: 52, 86: 55, 87: 56})
for stale in (41, 42, 43, 44, 46):
    if REMAP.get(stale) == stale:
        del REMAP[stale]

RETIRED = {88: 'Host ratio picker (already inert since 2026-09-02)'}
# V2-V8's per-voice sliders leave the line entirely and become bank values.
TO_BLOB = set(range(31, 73))
NEW_SLIDERS = {15: 'Voice', 27: 'Solo this voice', 32: 'Pan rate mode',
               45: 'Drift period unit', 47: 'Drift play for',
               48: 'Drift rest for', 51: 'Ramp time unit',
               53: 'Ramp play for', 54: 'Ramp rest for'}

OLD_RATE_MODE = 2
NEW_VOICE_SEL, NEW_PAN_RATE_MODE = 15, 32

# Per-voice sources on the OLD line. Order matches the @serialize stream.
#   name          -> per-voice old slider ids, or a single global id for all 8
VOICE_SRC = [
    ('note',   [26, 32, 38, 44, 50, 56, 62, 68]),
    ('fine',   [27, 33, 39, 45, 51, 57, 63, 69]),
    ('dr',     [28, 34, 40, 46, 52, 58, 64, 70]),
    ('phoff',  [29, 35, 41, 47, 53, 59, 65, 71]),
    ('wave',   14),
    ('depth',  10),
    ('ondur',   5),
    ('att',     6),
    ('rel',     7),
    ('gain',   [25, 31, 37, 43, 49, 55, 61, 67]),
    ('active', [30, 36, 42, 48, 54, 60, 66, 72]),
    ('solo',   0.0),
]
# Declared defaults, used when a slot holds '-' (nothing stored).
VOICE_DEFAULT = {'note': 24, 'fine': 0, 'dr': 0, 'phoff': 0, 'wave': 0,
                 'depth': -6, 'ondur': 100, 'att': 0, 'rel': 100,
                 'gain': -6, 'active': None, 'solo': 0}

assert set(REMAP) | set(RETIRED) | TO_BLOB == set(range(1, OLD_N + 1)), \
    'map does not cover every old slider'
assert len(set(REMAP.values())) == len(REMAP), 'two old sliders share a new id'
assert set(REMAP.values()) | set(NEW_SLIDERS) == set(range(1, NEW_N + 1)), \
    'result is not 1..%d' % NEW_N


def fmt(v):
    """Match REAPER's own token style: no trailing zeros, no exponent."""
    s = ('%.6f' % v).rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def num(vals, sid, default):
    v = vals.get(sid)
    if v in (None, '-'):
        return float(default)
    return float(v)


def find_blob(lines, at):
    """Return (start_index, end_index, floats) for the <JS_SER> after `at`."""
    for j in range(at, min(at + 8, len(lines))):
        if lines[j].strip() == '<JS_SER':
            body = []
            for k in range(j + 1, len(lines)):
                t = lines[k].strip()
                if t == '>':
                    raw = base64.b64decode(''.join(body))
                    return j, k, list(struct.unpack('<%df' % (len(raw) // 4), raw))
                body.append(t)
            raise SystemExit('unterminated <JS_SER> at line %d' % j)
        if lines[j].strip().startswith('<JS '):
            continue
    return None, None, None


def render_blob(indent, floats):
    raw = struct.pack('<%df' % len(floats), *floats)
    b64 = base64.b64encode(raw).decode('ascii')
    return [indent + b64[i:i + 128] for i in range(0, len(b64), 128)]


def build_blob(old, real, where, vi):
    """The new @serialize stream, in the order the plugin reads it."""
    # Drift/ramp config carries across only if the old blob was the format this
    # build's predecessor wrote. Anything else falls through to the plugin's own
    # defaults -- which is the accepted policy, and safer than reinterpreting an
    # unknown stream.
    ok = old is not None and len(old) >= 171 and round(old[0]) == OLD_MAGIC
    if ok:
        carried = old[1:171]
    else:
        # up/down = 0, per = 8, shape = 0, last_target = 0, by/dur/delay = 0
        carried = ([0.0] * N_TARGETS + [0.0] * N_TARGETS + [8.0] * N_TARGETS +
                   [0.0] * N_TARGETS + [0.0] +
                   [0.0] * N_TARGETS * 3 + [0.0])
    assert len(carried) == 170, len(carried)

    out = [float(NEW_MAGIC)] + carried
    out += [0.0] * (N_TARGETS * 4)          # drift play/rest, ramp play/rest

    for name, src in VOICE_SRC:
        if isinstance(src, list):
            for v, sid in enumerate(src):
                d = VOICE_DEFAULT[name]
                if d is None:               # Active: V1 defaults on, V2-V8 off
                    d = 1 if v == 0 else 0
                out.append(num(real, sid, d))
        elif isinstance(src, (int,)) and src != 0:
            out += [num(real, src, VOICE_DEFAULT[name])] * 8
        else:
            out += [0.0] * 8
    out.append(1.0)                          # last_voice_sel = Voice 1
    expect = 1 + 170 + N_TARGETS * 4 + 12 * 8 + 1
    assert len(out) == expect, (len(out), expect)
    return out, ok


def convert(lines, stats, where):
    n_before = len(lines)
    count = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if ('<JS ' not in line) or (PLUG + '.jsfx' not in line):
            i += 1
            continue
        vi = i + 1
        orig = lines[vi]
        if not orig.endswith(('\r\n', '\n', '\r')):
            raise SystemExit('%s line %d: value line has no ending -- refusing'
                             % (where, vi))
        old_vals = parse_line(orig)
        real = {k: v for k, v in old_vals.items() if v not in (None, '-')}
        for k, v in real.items():
            if v.startswith('"'):
                raise SystemExit('%s line %d: slider %d holds a quoted token %r'
                                 ' -- refusing' % (where, vi, k, v))
        if real and max(real) > OLD_N:
            raise SystemExit('%s line %d: value at slider %d, above the old '
                             'highest id %d -- already migrated, or not this '
                             'layout' % (where, vi, max(real), OLD_N))
        if real and max(real) <= NEW_N and 73 not in real:
            raise SystemExit('%s line %d: no value above %d -- this looks '
                             'already migrated' % (where, vi, NEW_N))

        # --- the blob, built from the OLD line before it is rewritten -------
        b0, b1, oldblob = find_blob(lines, vi + 1)
        if b0 is None:
            raise SystemExit('%s line %d: no <JS_SER> block -- refusing, the '
                             'voices have nowhere to go' % (where, vi))
        newblob, carried_cfg = build_blob(oldblob, real, where, vi)

        # --- the plain positional move -------------------------------------
        new = {}
        for o, tok in real.items():
            if o in RETIRED or o in TO_BLOB:
                continue
            if o not in REMAP:
                raise SystemExit('%s line %d: slider %d has no authored mapping'
                                 % (where, vi, o))
            new[REMAP[o]] = tok

        # --- value rules ----------------------------------------------------
        new[NEW_PAN_RATE_MODE] = fmt(num(real, OLD_RATE_MODE, 0))
        new[NEW_VOICE_SEL] = '1'

        rendered = render_line(orig, new, NEW_N)
        back = parse_line(rendered)
        for nid, want in new.items():
            if back.get(nid) != want:
                raise SystemExit('%s line %d: slider %d became %r, wanted %r'
                                 % (where, vi, nid, back.get(nid), want))
        lines[vi] = rendered

        indent = lines[b0 + 1][:len(lines[b0 + 1]) - len(lines[b0 + 1].lstrip())]
        ending = '\r\n' if lines[b0].endswith('\r\n') else '\n'
        body = [l + ending for l in render_blob(indent, newblob)]
        lines[b0 + 1:b1] = body

        count += 1
        stats['instances'] += 1
        stats['notes'].append(
            '%-42s ratemode=%-2d oldblob=%-8s drift/ramp %s  voices=%s'
            % (os.path.basename(where), int(num(real, OLD_RATE_MODE, 0)),
               round(oldblob[0]) if oldblob else 'none',
               'carried' if carried_cfg else 'RESET to defaults',
               ''.join('1' if num(real, s, 1 if n == 0 else 0) else '.'
                       for n, s in enumerate([30, 36, 42, 48, 54, 60, 66, 72]))))
        i = b0 + 1 + len(body)
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
        src = os.path.join(SNAP, snapname)
        lines = open(src, 'rb').read().decode('utf-8').splitlines(keepends=True)
        before_js = sum(1 for l in lines if PLUG + '.jsfx' in l)
        n = convert(lines, stats, src)
        if n != before_js:
            raise SystemExit('%s: found %d JS blocks but converted %d'
                             % (src, before_js, n))
        if n and not dry:
            open(live, 'w', encoding='utf-8', newline='').write(''.join(lines))
        if n:
            projects += 1
    print('\n'.join(stats['notes']))
    print('\n%s: %d instances across %d projects'
          % ('DRY RUN' if dry else 'APPLIED', stats['instances'], projects))
    if stats['instances'] != 8:
        raise SystemExit('expected 8 instances, found %d -- refusing'
                         % stats['instances'])
    if dry:
        print('re-run with --apply to write')


if __name__ == '__main__':
    main()
