#!/usr/bin/env python3
"""Verify the 2026-09-06 Womb layout migration INDEPENDENTLY.

Deliberately does not import the migration's table. Two separate checks:

  A. BY NAME. Every control that survived is looked up by its LABEL in the old
     source and the new one, and must carry the same token -- so a wrong
     permutation disagrees with itself rather than agreeing with whatever
     produced it. Controls whose VALUE was deliberately transformed are excluded
     here by name and checked in B instead.

  B. BY BEHAVIOUR, which is the one that actually matters. For each instance it
     computes what the plugin DOES -- heart rate in BPM, systole in seconds, the
     four breath segment lengths in seconds -- under the OLD code and under the
     NEW code, and asserts they agree. This is model-against-model rather than
     table-against-table, and it is the only check that would notice a
     permutation that is perfectly self-consistent and still silent-changes the
     sound.

     The old model INCLUDES the load-time seeding, because that is what the
     plugin really did on open for an old-blob host-mode instance. Comparing
     against the stored numbers instead would have been comparing against
     something nobody ever heard.

PRE is pinned to a commit HASH, never HEAD~n.
"""
import base64
import math
import os
import re
import struct
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-womb-layout-20260906'
SRC = 'src/womb_sound_generator_v3.jsfx'
PRE = '0235fd3'
PLUG = 'womb_sound_generator_v3'
DECL = re.compile(r'^slider(\d+):([^<]*)<([^>]*)>(.*)$')

# AUTHORED. Controls that kept their identity and changed their LABEL.
RENAMED = {
    'Heart rate (BPM)': 'Heart rate (in heart rate mode units)',
    'Rate Mode': 'Heart rate mode',
    'Systole (ms / beats in Host x)': 'Systole (in systole units)',
    'Inhale (sec / beats in Host x)': 'Inhale (seconds, or beats when synced)',
    'Top pause (sec / beats in Host x)': 'Top pause (seconds, or beats when synced)',
    'Exhale (sec / beats in Host x)': 'Exhale (seconds, or beats when synced)',
    'Bottom pause (sec / beats in Host x)': 'Bottom pause (seconds, or beats when synced)',
    'Breaths per minute (Own BPM only; 0=off, rewrites the durations)':
        'Breaths per minute (0 = the segments below decide)',
    'Drift period (heartbeats or breath cycles)': 'Drift period (in drift period units)',
    'Ramp duration (minutes)': 'Ramp duration (in ramp time units)',
    'Ramp start delay (minutes)': 'Ramp start delay (in ramp time units)',
}
# Controls whose VALUE is deliberately transformed -- check B covers these.
TRANSFORMED = {'Heart rate (BPM)', 'Rate Mode', 'Systole (ms / beats in Host x)',
               'Inhale (sec / beats in Host x)', 'Top pause (sec / beats in Host x)',
               'Exhale (sec / beats in Host x)', 'Bottom pause (sec / beats in Host x)',
               'Breaths per minute (Own BPM only; 0=off, rewrites the durations)'}
RETIRED_NAMES = {'Host sync target', 'Every N beats (Host x)'}
SEEDING_MAGICS = (2100010, 2200010)


def sliders(text):
    out = {}
    for line in text.splitlines():
        m = DECL.match(line)
        if not m:
            continue
        sid, _d, rng, name = m.groups()
        p = rng.split(',')
        try:
            lo, hi = float(p[0]), float(p[1])
        except (ValueError, IndexError):
            lo = hi = None
        out[int(sid)] = (name.strip(), lo, hi)
    return out


def show(rev, path):
    return subprocess.run(['git', 'show', '%s:%s' % (rev, path)],
                          capture_output=True, text=True, check=True).stdout


def tempo_of(lines):
    for l in lines:
        m = re.match(r'\s*TEMPO\s+([0-9.]+)', l)
        if m:
            return float(m.group(1))
    return 120.0


def magic_at(lines, at):
    started, b = False, []
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


def g(vals, sid, default):
    v = vals.get(sid)
    return float(default) if v in (None, '-') else float(v)


def old_behaviour(v, tempo, magic):
    """What the OLD plugin produced on open, seeding included."""
    heart = g(v, 1, 70)
    systole = g(v, 5, 120)
    segs = [g(v, 16, 4.0), g(v, 17, 0.3), g(v, 18, 4.0), g(v, 19, 0.3)]
    host = g(v, 62, 0) == 1
    beats = g(v, 64, 1)
    if host and magic in SEEDING_MAGICS:
        beats = max(0.25, min(64, 1.0 / max(heart, 0.0001)))
        br_u = tempo / 60.0
        segs = [min(64, max(0.02 if i in (0, 2) else 0.0, s * br_u)) for i, s in enumerate(segs)]
        systole = min(1000, max(0.01, systole * br_u * 0.001))
    if host:
        bpm = max(tempo, 0.001) / max(beats, 0.25)
        sys_sec = systole * 60.0 / tempo
        seg_sec = [s * 60.0 / tempo for s in segs]
    else:
        bpm = heart
        sys_sec = systole * 0.001
        seg_sec = segs[:]
    return bpm, sys_sec, seg_sec


def new_behaviour(v, tempo):
    """What the NEW plugin produces, transcribed from @block."""
    beat = 60.0 / tempo
    mode = g(v, 2, 0)
    raw = max(g(v, 1, 70), 0.001)
    bpm = (raw if mode == 0 else 60 / raw if mode == 1 else raw * 60 if mode == 2
           else 60 / (raw * beat) if mode == 3 else 60 * raw / beat)
    bpm = max(0.01, min(1000, bpm))

    su = g(v, 5, 0)
    sysv = g(v, 4, 120)
    unit = 0.001 if su == 0 else 1 if su == 1 else beat if su == 2 else 60 / max(bpm, 0.01)
    sys_sec = sysv * (0.01 if su == 3 else 1) * unit
    sys_sec = max(1 / 48000.0, min(sys_sec, max(60.0 / bpm, 2 / 48000.0) - 1 / 48000.0))

    bmode = g(v, 17, 0)
    braw = g(v, 16, 0)
    cyc = (0 if braw <= 0 else
           60 / max(braw, .001) if bmode == 0 else
           max(braw, .001) if bmode == 1 else
           1 / max(braw, .001) if bmode == 2 else
           max(braw, .001) * beat if bmode == 3 else
           beat / max(braw, .001))
    host_scale = tempo / 60.0 if bmode >= 3 else 1.0
    segs = [g(v, 18, 4.0), g(v, 19, 0.3), g(v, 20, 4.0), g(v, 21, 0.3)]
    natural = max(sum(segs), 0.001) / max(host_scale, 0.0001)
    host_scale *= (natural / cyc) if cyc > 0 else 1.0
    seg_sec = [s / host_scale for s in segs]
    return bpm, sys_sec, seg_sec


def main():
    old_s, new_s = sliders(show(PRE, SRC)), sliders(open(SRC, encoding='utf-8').read())
    print('sliders: %d before, %d after' % (len(old_s), len(new_s)))
    new_by_name = {}
    for sid, (name, _l, _h) in new_s.items():
        new_by_name.setdefault(name, []).append(sid)
    dupes = {n: v for n, v in new_by_name.items() if len(v) > 1}
    if dupes:
        raise SystemExit('duplicate control names: %s' % dupes)

    fails, new_bad = [], []
    checks = pre_bad = n_inst = n_proj = 0
    pat = re.compile(r'<JS\s+\S*?' + re.escape(PLUG) + r'\.jsfx')

    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        o_lines = open(os.path.join(SNAP, snapname), 'rb').read().decode('utf-8').splitlines()
        n_lines = open(live, 'rb').read().decode('utf-8').splitlines()
        if len(o_lines) != len(n_lines):
            fails.append('%s: %d lines -> %d' % (base, len(o_lines), len(n_lines)))
            continue
        tempo = tempo_of(o_lines)
        oi = [i for i, l in enumerate(o_lines) if pat.search(l)]
        ni = [i for i, l in enumerate(n_lines) if pat.search(l)]
        if oi != ni:
            fails.append('%s: instances moved %s -> %s' % (base, oi, ni))
            continue
        n_proj += 1

        for at in oi:
            n_inst += 1
            ov, nv = parse_line(o_lines[at + 1]), parse_line(n_lines[at + 1])
            magic = magic_at(o_lines, at + 1)

            # --- A. by name -------------------------------------------------
            for sid, tok in ov.items():
                if tok in (None, '-') or sid not in old_s:
                    continue
                oname = old_s[sid][0]
                if oname in RETIRED_NAMES or oname in TRANSFORMED:
                    continue
                name = RENAMED.get(oname, oname)
                if name not in new_by_name:
                    fails.append('%s @%d: control %r vanished' % (base, at, name))
                    continue
                dest = new_by_name[name][0]
                checks += 1
                if nv.get(dest) != tok:
                    fails.append('%s @%d: %r was %r now %r (%d -> %d)'
                                 % (base, at, name, tok, nv.get(dest), sid, dest))

            # --- B. by behaviour ---------------------------------------------
            ob = old_behaviour(ov, tempo, magic)
            nb = new_behaviour(nv, tempo)
            checks += 6
            if abs(ob[0] - nb[0]) > 1e-4 * max(1, ob[0]):
                fails.append('%s @%d: heart rate %.4f BPM -> %.4f' % (base, at, ob[0], nb[0]))
            if abs(ob[1] - nb[1]) > 1e-4 * max(1e-3, ob[1]):
                fails.append('%s @%d: systole %.6f s -> %.6f' % (base, at, ob[1], nb[1]))
            for k, (a, b) in enumerate(zip(ob[2], nb[2])):
                if abs(a - b) > 1e-4 * max(1e-3, a):
                    fails.append('%s @%d: breath segment %d %.6f s -> %.6f' % (base, at, k, a, b))

            # --- range check --------------------------------------------------
            was_bad = set()
            for sid, tok in ov.items():
                if tok in (None, '-') or sid not in old_s:
                    continue
                _n, lo, hi = old_s[sid]
                try:
                    val = float(tok)
                except ValueError:
                    continue
                if lo is not None and not (lo <= val <= hi):
                    was_bad.add(old_s[sid][0])
                    pre_bad += 1
            for sid, tok in nv.items():
                if tok in (None, '-') or sid not in new_s:
                    continue
                name, lo, hi = new_s[sid]
                try:
                    val = float(tok)
                except ValueError:
                    continue
                checks += 1
                if lo is not None and not (lo <= val <= hi) and name not in was_bad:
                    new_bad.append('%s @%d: %r = %s outside %g..%g' % (base, at, name, tok, lo, hi))

    print('projects           :', n_proj)
    print('instances          :', n_inst)
    print('checks             :', checks)
    print('already out of range before (not a fault):', pre_bad)
    print('NEWLY out of range :', len(new_bad))
    for b in new_bad[:10]:
        print('   ', b)
    print('failures           :', len(fails))
    for f in fails[:25]:
        print('   ', f)
    print()
    print('RESULT:', 'PASS' if not fails and not new_bad else 'FAIL')
    return 0 if not fails and not new_bad else 1


if __name__ == '__main__':
    sys.exit(main())
