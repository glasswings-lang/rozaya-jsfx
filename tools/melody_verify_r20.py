#!/usr/bin/env python3
"""Verify the melody_phase R20/R21 migration by decoding both sides by CONTROL
NAME, independently of the table melody_migrate_r20.py used.

WHY IT IS BUILT THIS WAY. Verifying a migration against the same authored table
that performed it makes the check agree with itself perfectly -- which is how a
Melody migration passed its own verification on 2026-09-02 while writing twelve
instances of nonsense. So this script does not import the mapping. It reads the
OLD slider names out of git and the NEW ones out of the working tree, decodes
every stored value into a {control name: value} dict on each side, and compares
those dicts.

The only differences it accepts are the ones the layout document says to expect,
and each is stated as a rule rather than as a permission to ignore mismatches:

  * three controls disappear      (Sync to host, Host sync target, Every N beats)
  * seven controls appear unset   (Pan rate mode, the drift and ramp units and
                                   their play/rest pairs)
  * a SYNCED instance's Rate value and Rate mode are deliberately overwritten,
    and the new pair must reproduce the OLD cycle length exactly, which is
    recomputed here from first principles rather than assumed.

It also range-checks every migrated value against its slider's declared min/max
-- the fastest proof that a mapping shifted, and it needs no ears.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-melody-r20-20260906'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_REV = 'HEAD'          # the pre-migration source, from git
SRC = 'src/melody_phase.jsfx'

DECL = re.compile(r'^slider(\d+):([^<]*)<([^>]*)>(.*)$')


def declarations(text):
    """{id: (name, default, lo, hi)} straight from the slider lines."""
    out = {}
    for line in text.splitlines():
        m = DECL.match(line)
        if not m:
            continue
        sid, default, rng, name = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        parts = rng.split(',')
        lo, hi = float(parts[0]), float(parts[1].split('{')[0])
        out[sid] = (name.strip(), float(default), lo, hi)
    return out


def by_name(decls, slots):
    out = {}
    for sid, tok in slots.items():
        if tok in (None, '-'):
            continue
        if sid not in decls:
            raise SystemExit('stored value for slider %d, which is not declared' % sid)
        out[decls[sid][0]] = (tok, sid)
    return out


def cycle_seconds(value, mode):
    """Nominal seconds per cycle, transcribed from rate_to_cycle_seconds()."""
    if mode == 0:
        return 60 / max(value, 0.001)
    if mode in (1, 3):
        return max(value, 0.001)
    return 1 / max(value, 0.001)


def instances(path, plugin=r'melody_phase\.jsfx'):
    lines = open(path, encoding='utf-8').read().splitlines()
    for i, line in enumerate(lines):
        if re.search(r'<JS\s+\S*?' + plugin, line):
            yield parse_line(lines[i + 1])


def main():
    old_src = subprocess.check_output(
        ['git', '-C', REPO, 'show', '%s:%s' % (OLD_REV, SRC)]).decode('utf-8')
    old_decl = declarations(old_src)
    new_decl = declarations(open(os.path.join(REPO, SRC), encoding='utf-8').read())
    print('old layout: %d sliders   new layout: %d sliders'
          % (len(old_decl), len(new_decl)))

    old_names = {v[0] for v in old_decl.values()}
    new_names = {v[0] for v in new_decl.values()}
    # Controls that kept their job and changed their label. Listed explicitly so
    # a rename can never be mistaken for a deletion plus an addition -- which is
    # exactly the fingerprint of a mid-list slider insert, and the thing this
    # check exists to catch.
    RENAMED = {'Pan Glide ms (0=instant)': 'Pan glide ms (0 = instant)',
               'Cycle Steps (per-cycle modes)': 'Cycle steps (per-cycle modes)',
               'Ramp duration (minutes)': 'Ramp duration (in ramp time units)',
               'Ramp start delay (minutes)': 'Ramp start delay (in ramp time units)'}
    genuinely_gone = sorted(old_names - new_names - set(RENAMED))
    genuinely_new = sorted(new_names - old_names - set(RENAMED.values()))
    print('renamed in place: %d' % len(RENAMED))
    print('gone : %s' % genuinely_gone)
    print('added: %s' % genuinely_new)
    if len(genuinely_gone) != 3 or len(genuinely_new) != 7:
        raise SystemExit('expected 3 controls gone and 7 added; got %d and %d'
                         % (len(genuinely_gone), len(genuinely_new)))

    checks = comparisons = 0
    problems = []
    n_inst = n_sync = 0

    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        olds = list(instances(os.path.join(SNAP, snapname)))
        news = list(instances(live))
        checks += 1
        if len(olds) != len(news):
            problems.append('%s: %d instances before, %d after'
                            % (base, len(olds), len(news)))
            continue

        for n, (o_slots, n_slots) in enumerate(zip(olds, news)):
            n_inst += 1
            o = by_name(old_decl, o_slots)
            w = by_name(new_decl, n_slots)
            where = '%s #%d' % (base, n + 1)

            # --- range check every stored value against its own control -------
            for name, (tok, sid) in w.items():
                _, _, lo, hi = new_decl[sid]
                v = float(tok)
                checks += 1
                if not (lo - 1e-9 <= v <= hi + 1e-9):
                    problems.append('%s: %s = %s outside [%s, %s]'
                                    % (where, name, tok, lo, hi))

            # --- the seven new controls must be UNSET -------------------------
            for name in genuinely_new:
                checks += 1
                if name in w:
                    problems.append('%s: new control %r carries %r, expected unset'
                                    % (where, name, w[name][0]))

            # --- the sync fold ------------------------------------------------
            sync = float(o['Sync to host'][0]) if 'Sync to host' in o else 0.0
            rate_names = {'Rate value', 'Rate mode'}
            if sync > 0.5:
                n_sync += 1
                beats = float(o['Every N beats (per sync target)'][0])
                old_cyc = beats                      # nominal seconds, at 60 BPM
                new_val = float(w['Rate value'][0])
                new_mode = int(float(w['Rate mode'][0]))
                new_cyc = cycle_seconds(new_val, new_mode)
                comparisons += 1
                checks += 1
                # 2 ppm covers the one instance stored as 0.333333 and rewritten
                # as an exact 3-per-beat; everything else must match to 1e-12.
                tol = 2e-6 * old_cyc if new_mode == 4 else 1e-12
                if abs(new_cyc - old_cyc) > tol:
                    problems.append('%s: synced cycle was %.9f s, now %.9f s'
                                    % (where, old_cyc, new_cyc))
                if new_mode not in (3, 4):
                    problems.append('%s: synced instance came out in mode %d'
                                    % (where, new_mode))
            else:
                # free-running: the rate pair must be untouched, by name
                for name in rate_names:
                    comparisons += 1
                    checks += 1
                    if o.get(name, (None,))[0] != w.get(name, (None,))[0]:
                        problems.append('%s: %s changed %r -> %r on a FREE instance'
                                        % (where, name, o.get(name), w.get(name)))

            # --- every other control must carry the identical token -----------
            for name, (tok, sid) in o.items():
                if name in ('Sync to host', 'Host sync target',
                            'Every N beats (per sync target)'):
                    continue
                if name in rate_names and sync > 0.5:
                    continue          # deliberately overwritten, checked above
                # two controls were RENAMED in place as they moved; match them up
                alias = RENAMED.get(name, name)
                comparisons += 1
                checks += 1
                if alias not in w:
                    problems.append('%s: %r lost its value (was %r)'
                                    % (where, alias, tok))
                elif w[alias][0] != tok:
                    problems.append('%s: %r was %r, now %r'
                                    % (where, alias, tok, w[alias][0]))

    print('\n%d instances, %d of them synced' % (n_inst, n_sync))
    print('%d checks, %d of them name-decoded value comparisons' % (checks, comparisons))
    if problems:
        print('\nFAIL -- %d problem(s):' % len(problems))
        for p in problems[:40]:
            print('  ' + p)
        sys.exit(1)
    print('\nPASS')


if __name__ == '__main__':
    main()
