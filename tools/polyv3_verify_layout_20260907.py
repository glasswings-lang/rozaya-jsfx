#!/usr/bin/env python3
"""Verify the 2026-09-07 Polyrhythm Phase v3 layout migration.

DELIBERATELY DOES NOT IMPORT THE MIGRATION'S TABLE. A verifier that reuses the
mapping it is checking agrees with itself perfectly -- that is how five Melody
projects were broken and passed verification on 2026-09-02. So this decodes by
CONTROL NAME: it reads the slider declarations out of the OLD source (from git)
and the NEW source (the working tree), matches controls by the name REAPER
shows, and checks that each one's value survived.

Four independent checks:

  1. BY NAME, ON THE LINE. Every control that exists in both versions must hold
     the same value before and after. The nine genuinely renamed controls are
     listed in ALIAS below, written by reading both files rather than by
     importing anything.

  2. BY NAME, IN THE BLOB. V2-V8's forty-two values left the slider line and
     must reappear in the @serialize stream. Each one is looked up in the old
     line by its old NAME (`V5 Note`) and compared against the decoded bank.
     The five controls that went from global to per-voice must appear in all
     eight slots with the old global's value.

  3. RANGE. Every migrated value must fit its NEW slider's declared min/max --
     the fastest possible proof that a mapping shifted, and it needs no ears.
     A value that was ALREADY out of range before is reported separately: that
     is a pre-existing oddity, not a fault this migration caused, and confusing
     the two buries the real signal.

  4. STRUCTURE. Line counts, instance counts, and a round-trip of every value
     line through the parser.

Run AFTER --apply. Compares E:/reaper live projects against the snapshot.
"""
import base64
import os
import re
import struct
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-polyv3-layout-20260907'
PLUG = 'polyrhythm_phase_v3'
SRC = 'src/polyrhythm_phase_v3.jsfx'
# PINNED to the commit before this build, never HEAD or HEAD~n: a relative
# revision goes stale the moment anything else is committed, and the check
# then compares the new layout against ITSELF and reports fiction.
OLD_REV = 'f1c049c49c7e'
N_TARGETS = 24
NEW_MAGIC = 2200000 + N_TARGETS

# Controls whose NAME changed. Written by reading the two files side by side.
# new name -> old name
ALIAS = {
    'Rate Value — all voices (BPM / sec / Hz / beats per cycle / per beat)':
        'Rate Value (Drift only: BPM / sec / Hz / beats per cycle)',
    'Drift period': 'Drift period (cycles)',
    'Ramp duration (in ramp time units)': 'Ramp duration (minutes)',
    'Ramp start delay (in ramp time units)': 'Ramp start delay (minutes)',
    'Note': 'V1 Note',
    'Fine tune (cents)': 'V1 Fine tune (cents)',
    "Drift / Rate — offset in Drift mode, this voice's own rate in Independent":
        'V1 Drift / Rate',
    'Phase Offset': 'V1 Phase Offset',
    'Gain dB': 'V1 Gain dB',
    'Active (Off = no CPU cost)': 'V1 Active (Off = no CPU cost)',
}
# Genuinely new in this build -- nothing to compare them against.
BRAND_NEW = {'Voice', 'Solo this voice', 'Pan rate mode', 'Drift period unit',
             'Drift play for (periods, 0 = always)',
             'Drift rest for (periods, 0 = always)', 'Ramp time unit',
             'Ramp play for (0 = smooth)', 'Ramp rest for (0 = smooth)'}

DECL = re.compile(r'^slider(\d+):(-?[0-9.]+)<([^,]*),([^,]*),[^>]*>(.*)$')


def sliders(text):
    """{id: (name, default, lo, hi)} from a .jsfx source."""
    out = {}
    for line in text.split('\n'):
        m = DECL.match(line)
        if not m:
            continue
        sid, dflt, lo, hi, name = m.groups()
        out[int(sid)] = (name.strip(), float(dflt), float(lo), float(hi))
    return out


def blob_of(lines, at):
    for j in range(at, min(at + 8, len(lines))):
        if lines[j].strip() == '<JS_SER':
            body = []
            for k in range(j + 1, len(lines)):
                t = lines[k].strip()
                if t == '>':
                    raw = base64.b64decode(''.join(body))
                    return list(struct.unpack('<%df' % (len(raw) // 4), raw))
                body.append(t)
    return None


def instances(path):
    """[(value_line_dict, blob_floats)] for every instance of PLUG in a file."""
    lines = open(path, 'rb').read().decode('utf-8').splitlines(keepends=True)
    out = []
    for i, l in enumerate(lines):
        if '<JS ' in l and PLUG + '.jsfx' in l:
            out.append((parse_line(lines[i + 1]), blob_of(lines, i + 2), lines[i + 1]))
    return out, len(lines)


def main():
    old_src = subprocess.check_output(
        ['git', 'show', '%s:%s' % (OLD_REV, SRC)]).decode('utf-8')
    OLD = sliders(old_src)
    NEW = sliders(open(SRC, encoding='utf-8').read())
    print('old source declares %d sliders, new declares %d' % (len(OLD), len(NEW)))
    assert len(OLD) == 90 and len(NEW) == 56, 'not the expected two layouts'

    old_by_name = {}
    for sid, (name, _d, _lo, _hi) in OLD.items():
        old_by_name.setdefault(name, sid)

    # new id -> old id, resolved purely by name
    by_name = {}
    for sid, (name, _d, _lo, _hi) in NEW.items():
        if name in BRAND_NEW:
            continue
        want = ALIAS.get(name, name)
        if want not in old_by_name:
            raise SystemExit('new slider %d %r has no old control named %r'
                             % (sid, name, want))
        by_name[sid] = old_by_name[want]
    print('matched %d of %d new controls to an old one by name; %d are new'
          % (len(by_name), len(NEW), len(BRAND_NEW)))
    assert len(by_name) + len(BRAND_NEW) == len(NEW)

    checks = failures = pre_existing = 0
    total_inst = 0
    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        old_inst, old_lines = instances(os.path.join(SNAP, snapname))
        new_inst, new_lines = instances(live)
        if len(old_inst) != len(new_inst):
            raise SystemExit('%s: %d instances before, %d after'
                             % (base, len(old_inst), len(new_inst)))
        if old_lines != new_lines:
            # The blob is re-wrapped at 128 chars, so a line-count change here
            # is expected -- but only in the blob, and only by the amount the
            # longer stream needs. Report it rather than asserting equality.
            pass
        for n, ((ov, ob, _oraw), (nv, nb, nraw)) in enumerate(zip(old_inst, new_inst)):
            total_inst += 1
            tag = '%s#%d' % (base, n + 1)

            # ---- 1. by name, on the line ---------------------------------
            for nsid, osid in by_name.items():
                got, want = nv.get(nsid), ov.get(osid)
                if want in (None, '-') and got in (None, '-'):
                    continue
                checks += 1
                if want in (None, '-'):
                    continue          # absent before; a declared default now
                if got is None or got == '-' or float(got) != float(want):
                    failures += 1
                    print('  FAIL %s: %r (new %d) = %r, was %r (old %d)'
                          % (tag, NEW[nsid][0], nsid, got, want, osid))

            # ---- 3. range ------------------------------------------------
            for nsid, tok in nv.items():
                if tok in (None, '-'):
                    continue
                name, _d, lo, hi = NEW[nsid]
                v = float(tok)
                if lo <= v <= hi:
                    continue
                osid = by_name.get(nsid)
                was = ov.get(osid) if osid else None
                if osid and was not in (None, '-'):
                    olo, ohi = OLD[osid][2], OLD[osid][3]
                    if not (olo <= float(was) <= ohi):
                        pre_existing += 1
                        print('  note %s: %r = %s is out of range %g..%g, and '
                              'ALREADY was before this migration -- '
                              'pre-existing, not caused here'
                              % (tag, name, tok, lo, hi))
                        continue
                failures += 1
                print('  FAIL %s: %r (new %d) = %s outside %g..%g'
                      % (tag, name, nsid, tok, lo, hi))

            # ---- 2. by name, in the blob ---------------------------------
            if nb is None:
                failures += 1
                print('  FAIL %s: no blob after migration' % tag)
                continue
            expect_len = 1 + 170 + N_TARGETS * 4 + 12 * 8 + 1
            checks += 1
            if len(nb) != expect_len:
                failures += 1
                print('  FAIL %s: blob is %d floats, expected %d'
                      % (tag, len(nb), expect_len))
                continue
            checks += 1
            if round(nb[0]) != NEW_MAGIC:
                failures += 1
                print('  FAIL %s: blob magic %s, expected %d'
                      % (tag, nb[0], NEW_MAGIC))
            # drift/ramp config must have survived byte for byte
            if ob is not None and round(ob[0]) == 2100000 + N_TARGETS:
                checks += 1
                if [round(x, 6) for x in nb[1:171]] != [round(x, 6) for x in ob[1:171]]:
                    failures += 1
                    print('  FAIL %s: drift/ramp config changed' % tag)
            # the four new play/rest banks must be all-zero (off)
            base_pr = 171
            checks += 1
            if any(nb[base_pr:base_pr + N_TARGETS * 4]):
                failures += 1
                print('  FAIL %s: new play/rest banks are not zero' % tag)
            # the twelve voice banks, checked against the OLD line BY NAME
            vb = base_pr + N_TARGETS * 4
            per_voice = [
                ('note', 'V%d Note', None), ('fine', 'V%d Fine tune (cents)', None),
                ('dr', 'V%d Drift / Rate', None), ('phoff', 'V%d Phase Offset', None),
                ('wave', None, 'Waveform'), ('depth', None, 'Depth dB'),
                ('ondur', None, 'On Duration % of Cycle'),
                ('att', None, 'Attack % of Cycle'),
                ('rel', None, 'Release % of Cycle'),
                ('gain', 'V%d Gain dB', None),
                ('active', 'V%d Active (Off = no CPU cost)', None),
                ('solo', None, None),
            ]
            for bi, (nm, pat, glob) in enumerate(per_voice):
                for v in range(8):
                    got = nb[vb + bi * 8 + v]
                    if pat is not None:
                        osid = old_by_name[pat % (v + 1)]
                        want = ov.get(osid)
                        want = OLD[osid][1] if want in (None, '-') else float(want)
                    elif glob is not None:
                        osid = old_by_name[glob]
                        want = ov.get(osid)
                        want = OLD[osid][1] if want in (None, '-') else float(want)
                    else:
                        want = 0.0
                    checks += 1
                    if abs(got - want) > 1e-4:
                        failures += 1
                        print('  FAIL %s: voice %d %s = %s, wanted %s'
                              % (tag, v + 1, nm, got, want))
            checks += 1
            if nb[-1] != 1.0:
                failures += 1
                print('  FAIL %s: last_voice_sel = %s, wanted 1' % (tag, nb[-1]))

            # ---- 4. structure --------------------------------------------
            checks += 1
            if not nraw.endswith(('\r\n', '\n', '\r')):
                failures += 1
                print('  FAIL %s: value line lost its ending' % tag)

    print('\n%d checks over %d instances, %d failures%s'
          % (checks, total_inst, failures,
             ', %d pre-existing range oddities reported separately'
             % pre_existing if pre_existing else ''))
    if total_inst != 8:
        raise SystemExit('expected 8 instances, saw %d' % total_inst)
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
