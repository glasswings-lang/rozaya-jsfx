#!/usr/bin/env python3
"""Verify the 2026-09-06 Morpher unit-control migration INDEPENDENTLY.

Deliberately does not import the migration's table. It reads the slider NAMES
out of both versions of the source and checks that every named control holds the
same token before and after -- so a wrong permutation disagrees with itself
rather than agreeing with the map that produced it.

Checks, in order:
  1. line count and instance count per project (a shifted line ending once ate a
     line per instance, and the token round-trip passed the whole time);
  2. every control, matched BY NAME, carries its old token;
  3. the two new sliders are absent, so their declared defaults apply;
  4. every value fits its slider's declared min/max -- reporting values that were
     ALREADY out of range separately, since only a NEW violation is a failure.

PRE is pinned to a commit HASH, never HEAD~n: a relative revision goes stale the
moment anything else is committed, and the check then compares a layout against
itself and reports fiction.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = 'E:/reaper/finished/backups/snapshots/_pre-morpher-units-20260906'
SRC = 'src/spectral_vowel_morpher.jsfx'
PRE = '33a5119'          # the commit immediately before the unit controls
PLUG = 'spectral_vowel_morpher'

DECL = re.compile(r'^slider(\d+):([^<]*)<([^>]*)>(.*)$')

# AUTHORED. Three controls kept their identity and changed their LABEL, because
# the label used to state the unit and a control now states it. Matching by name
# has to be told about a rename or it reports the control as vanished -- which is
# the verifier being wrong, not the data, and is exactly the kind of false alarm
# that makes a checker worth ignoring. Nothing else was renamed.
RENAMED = {
    'Drift period (sec, or beats in Host x)': 'Drift period (in drift period units)',
    'Ramp duration (minutes)':                'Ramp duration (in ramp time units)',
    'Ramp start delay (minutes)':             'Ramp start delay (in ramp time units)',
}


def sliders(text):
    """{id: (name, lo, hi)} from a .jsfx source. Enums declare their range too."""
    out = {}
    for line in text.splitlines():
        m = DECL.match(line)
        if not m:
            continue
        sid, _default, rng, name = m.groups()
        parts = rng.split(',')
        try:
            lo, hi = float(parts[0]), float(parts[1])
        except (ValueError, IndexError):
            lo = hi = None
        out[int(sid)] = (name.strip(), lo, hi)
    return out


def show(rev, path):
    return subprocess.run(['git', 'show', '%s:%s' % (rev, path)],
                          capture_output=True, text=True, check=True).stdout


def instances(lines):
    """(value_line_index, parsed) for every Morpher instance, in file order."""
    pat = re.compile(r'<JS\s+\S*?' + re.escape(PLUG) + r'\.jsfx')
    return [(i + 1, parse_line(lines[i + 1]))
            for i, l in enumerate(lines) if pat.search(l)]


def main():
    old_s = sliders(show(PRE, SRC))
    new_s = sliders(open(SRC, encoding='utf-8').read())
    print('sliders: %d before, %d after' % (len(old_s), len(new_s)))

    new_by_name = {}
    for sid, (name, _lo, _hi) in new_s.items():
        new_by_name.setdefault(name, []).append(sid)
    dupes = {n: v for n, v in new_by_name.items() if len(v) > 1}
    if dupes:
        raise SystemExit('duplicate control names, cannot match by name: %s' % dupes)

    added = set(new_s) - set(REV(old_s, new_s))
    assert added == {39, 46}, 'expected exactly sliders 39 and 46 to be new, got %s' % sorted(added)
    checks = 0
    fails = []
    pre_bad = 0
    new_bad = []
    n_inst = 0
    n_proj = 0

    for snapname in sorted(os.listdir(SNAP)):
        folder, base = snapname.split('__', 1)
        live = 'E:/reaper/%s/%s' % (folder, base)
        old_lines = open(os.path.join(SNAP, snapname), 'rb').read().decode('utf-8').splitlines()
        new_lines = open(live, 'rb').read().decode('utf-8').splitlines()

        if len(old_lines) != len(new_lines):
            fails.append('%s: %d lines -> %d' % (base, len(old_lines), len(new_lines)))
            continue

        oi, ni = instances(old_lines), instances(new_lines)
        if len(oi) != len(ni):
            fails.append('%s: %d instances -> %d' % (base, len(oi), len(ni)))
            continue
        n_proj += 1

        for (o_at, o_vals), (n_at, n_vals) in zip(oi, ni):
            n_inst += 1
            if o_at != n_at:
                fails.append('%s: instance moved line %d -> %d' % (base, o_at, n_at))
                continue

            # 2. every OLD control, by name, still holds its token.
            for sid, tok in o_vals.items():
                if tok in (None, '-'):
                    continue
                if sid not in old_s:
                    fails.append('%s line %d: value at undeclared old slider %d'
                                 % (base, o_at, sid))
                    continue
                name = RENAMED.get(old_s[sid][0], old_s[sid][0])
                if name not in new_by_name:
                    fails.append('%s line %d: control %r vanished' % (base, o_at, name))
                    continue
                dest = new_by_name[name][0]
                got = n_vals.get(dest)
                checks += 1
                if got != tok:
                    fails.append('%s line %d: %r was %r, now %r (slider %d -> %d)'
                                 % (base, o_at, name, tok, got, sid, dest))

            # 3. the new controls must be ABSENT.
            for sid in added:
                checks += 1
                if n_vals.get(sid) not in (None, '-'):
                    fails.append('%s line %d: new slider %d (%s) carries %r, must be '
                                 'absent' % (base, o_at, sid, new_s[sid][0],
                                             n_vals.get(sid)))

            # 4. range check, old violations separated from new ones.
            was_bad = set()
            for sid, tok in o_vals.items():
                if tok in (None, '-') or sid not in old_s:
                    continue
                _n, lo, hi = old_s[sid]
                try:
                    v = float(tok)
                except ValueError:
                    continue
                if lo is not None and not (lo <= v <= hi):
                    was_bad.add(old_s[sid][0])
                    pre_bad += 1
            for sid, tok in n_vals.items():
                if tok in (None, '-') or sid not in new_s:
                    continue
                name, lo, hi = new_s[sid]
                try:
                    v = float(tok)
                except ValueError:
                    continue
                checks += 1
                if lo is not None and not (lo <= v <= hi) and name not in was_bad:
                    new_bad.append('%s line %d: %r = %s, outside %g..%g'
                                   % (base, n_at, name, tok, lo, hi))

    print('projects           :', n_proj)
    print('instances          :', n_inst)
    print('checks             :', checks)
    print('already out of range before (not a fault):', pre_bad)
    print('NEWLY out of range :', len(new_bad))
    for b in new_bad[:10]:
        print('   ', b)
    print('failures           :', len(fails))
    for f in fails[:20]:
        print('   ', f)
    print()
    print('RESULT:', 'PASS' if not fails and not new_bad else 'FAIL')
    return 0 if not fails and not new_bad else 1


def REV(old_s, new_s):
    """Old ids that still exist under the same name -- i.e. everything but the
    genuinely new sliders."""
    old_names = {RENAMED.get(n, n) for n, _l, _h in old_s.values()}
    return {sid for sid, (n, _l, _h) in new_s.items() if n in old_names}


if __name__ == '__main__':
    sys.exit(main())
