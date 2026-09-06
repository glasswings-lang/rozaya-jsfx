#!/usr/bin/env python3
"""Verify the 2026-09-06 Drift/Ramp migrations by decoding both sides by CONTROL
NAME, independently of the table driftramp_migrate_20260906.py used.

It does NOT import the migration's mapping. It reads the OLD slider declarations
out of git and the NEW ones out of the working tree, turns each instance's stored
values into a {control name: value} dict on each side, and compares those.

Verifying a migration against the table that performed it makes the check agree
with itself perfectly -- which is how a Melody migration passed its own
verification on 2026-09-02 while writing twelve instances of nonsense.

Run BEFORE committing the source changes: it reads the pre-migration layout from
the given git revision, which defaults to HEAD.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-driftramp-20260906'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECL = re.compile(r'^slider(\d+):([^<]*)<([^>]*)>(.*)$')

# plugin -> (source path, git revision holding the PRE-migration layout)
PLUGINS = {
    # heartbeat's build was committed before this verifier existed, so its
    # PRE-migration layout is two commits back, not one. Pinned explicitly and
    # checked by slider count below rather than assumed -- pointing at the wrong
    # revision makes the check compare the new layout against ITSELF, which looks
    # like a catastrophic value shift and is nothing of the kind.
    'heartbeat gen':      ('src/heartbeat gen.jsfx',      'HEAD~2'),
    'sweep-dwell-filter': ('src/sweep-dwell-filter.jsfx', 'HEAD'),
}

# Controls that kept their job and changed their label. Declared explicitly so a
# rename can never read as a deletion plus an addition -- which is the
# fingerprint of a mid-list slider insert, the thing this check exists to catch.
RENAMED = {
    'Ramp duration (minutes)':    'Ramp duration (in ramp time units)',
    'Ramp start delay (minutes)': 'Ramp start delay (in ramp time units)',
    'Drift period (beats)':       'Drift period',
    'Drift period (cycles)':      'Drift period',
    'Drift period (heartbeats)':  'Drift period',
}


def declarations(text):
    out = {}
    for line in text.splitlines():
        m = DECL.match(line)
        if not m:
            continue
        rng = m.group(3).split(',')
        out[int(m.group(1))] = (m.group(4).strip(),
                                float(rng[0]), float(rng[1].split('{')[0]))
    return out


def instances(path, plug):
    lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
    pat = re.compile(r'<JS\s+\S*?' + re.escape(plug) + r'\.jsfx')
    for i, l in enumerate(lines):
        if pat.search(l):
            yield parse_line(lines[i + 1])


def by_name(decls, slots):
    out = {}
    for sid, tok in slots.items():
        if tok in (None, '-') or sid not in decls:
            continue
        out[decls[sid][0]] = (tok, sid)
    return out


def main():
    problems = []
    checks = comparisons = n_inst = 0

    for plug, (src, rev) in PLUGINS.items():
        old = declarations(subprocess.check_output(
            ['git', '-C', REPO, 'show', '%s:%s' % (rev, src)]).decode('utf-8'))
        new = declarations(open(os.path.join(REPO, src), encoding='utf-8').read())
        old_names = {v[0] for v in old.values()}
        new_names = {v[0] for v in new.values()}
        gone = sorted(old_names - new_names - set(RENAMED))
        added = sorted(new_names - old_names - set(RENAMED.values()))
        print("%-20s %d -> %d sliders   gone %s   added %d"
              % (plug, len(old), len(new), gone or 'none', len(added)))
        if len(old) == len(new):
            problems.append('%s: the OLD and NEW layouts have the same slider '
                            'count -- revision %r is almost certainly not the '
                            'pre-migration one' % (plug, rev))
        if gone:
            problems.append('%s: controls disappeared: %s' % (plug, gone))
        if len(added) != 6:
            problems.append('%s: expected 6 new controls, got %d: %s'
                            % (plug, len(added), added))

        for snapname in sorted(os.listdir(SNAP)):
            folder, base = snapname.split('__', 1)
            live = 'E:/reaper/%s/%s' % (folder, base)
            olds = list(instances(os.path.join(SNAP, snapname), plug))
            news = list(instances(live, plug))
            if not olds and not news:
                continue
            checks += 1
            if len(olds) != len(news):
                problems.append('%s/%s: %d instances before, %d after'
                                % (plug, base, len(olds), len(news)))
                continue
            for n, (o_s, n_s) in enumerate(zip(olds, news)):
                n_inst += 1
                O, W = by_name(old, o_s), by_name(new, n_s)
                where = '%s %s #%d' % (plug, base, n + 1)

                for name, (tok, sid) in W.items():
                    _, lo, hi = new[sid]
                    checks += 1
                    if not (lo - 1e-9 <= float(tok) <= hi + 1e-9):
                        problems.append('%s: %s = %s outside [%s, %s]'
                                        % (where, name, tok, lo, hi))
                for name in added:
                    checks += 1
                    if name in W:
                        problems.append('%s: new control %r carries %r, expected unset'
                                        % (where, name, W[name][0]))
                for name, (tok, sid) in O.items():
                    alias = RENAMED.get(name, name)
                    comparisons += 1
                    checks += 1
                    if alias not in W:
                        problems.append('%s: %r lost its value (was %r)'
                                        % (where, alias, tok))
                    elif W[alias][0] != tok:
                        problems.append('%s: %r was %r, now %r'
                                        % (where, alias, tok, W[alias][0]))

    print("\n%d instances, %d checks, %d name-decoded value comparisons"
          % (n_inst, checks, comparisons))
    if problems:
        print("\nFAIL -- %d problem(s):" % len(problems))
        for p in problems[:40]:
            print('  ' + p)
        sys.exit(1)
    print("\nPASS")


if __name__ == '__main__':
    main()
