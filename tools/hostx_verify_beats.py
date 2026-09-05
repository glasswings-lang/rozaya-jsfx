"""Verify the Host x multiplier -> beats-per-cycle value migration.

Checks the thing that actually matters, which is not "was 1/x applied" but
"does the sweep still run at the same speed". For every migrated instance it
recomputes the resulting rate in Hz under BOTH the old code path and the new
one, using THAT PROJECT'S OWN TEMPO read out of the .RPP, and asserts they
agree:

    old:  actual Hz = multiplier      * tempo / 60
    new:  actual Hz = (1 / beats)     * tempo / 60

It also asserts that the ONLY token that moved on each line is the rate
slider's -- the check that catches a migration which got the right answer and
disturbed something else on the way.
"""
import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

PLUGINS = {
    'Full_Feature_Tremolo':         (1, 2, 3),
    'full-feature-sweeping-filter': (3, 4, 3),
}
SNAP = r'E:\reaper\finished\backups\snapshots\_pre-hostx-beats-20260904'
MIG = os.path.join(os.environ.get('TEMP', '.'), 'hostx-beats-migrated')


def project_tempo(text):
    for line in text.split('\n'):
        t = line.strip()
        if t.startswith('TEMPO '):
            return float(t.split()[1])
    return 120.0


def instances(path):
    lines = io.open(path, encoding='utf-8', newline='').read().split('\n')
    out = []
    for i, l in enumerate(lines):
        for plug in PLUGINS:
            if plug in l:
                j = i + 1
                while not lines[j].strip():
                    j += 1
                out.append((plug, j, parse_line(lines[j]), lines[j]))
    return out, lines


def main():
    files = sorted(f for f in os.listdir(MIG) if f.lower().endswith('.rpp'))
    checked = bad = other = 0
    print("%-40s %-30s %10s %10s %12s" % ("project", "plugin", "old", "new", "Hz (both)"))
    print("-" * 106)
    for f in files:
        a_inst, a_lines = instances(os.path.join(SNAP, f))
        b_inst, b_lines = instances(os.path.join(MIG, f))
        assert len(a_lines) == len(b_lines), "line count differs in " + f
        assert len(a_inst) == len(b_inst), "instance count differs in " + f
        tempo = project_tempo('\n'.join(a_lines))
        for (pa, ja, va, ra), (pb, jb, vb, rb) in zip(a_inst, b_inst):
            assert pa == pb and ja == jb, "instances do not line up in " + f
            rv, rm, hostx = PLUGINS[pa]
            mode = va.get(rm)
            synced = mode not in (None, '-') and abs(float(mode) - hostx) < 1e-9
            # every token except the rate slider must be untouched
            for k in set(list(va.keys()) + list(vb.keys())):
                if k == rv and synced:
                    continue
                if va.get(k) != vb.get(k):
                    other += 1
                    print("  UNEXPECTED CHANGE %s slider%d: %r -> %r" % (f[:30], k, va.get(k), vb.get(k)))
            if not synced:
                assert ra == rb, "a non-Host-x instance was rewritten in " + f
                continue
            checked += 1
            old = float(va[rv]); new = float(vb[rv])
            hz_old = old * tempo / 60.0
            hz_new = (1.0 / new) * tempo / 60.0
            ok = abs(hz_old - hz_new) < 1e-9
            if not ok:
                bad += 1
            print("%-40s %-30s %10g %10g %12.6f %s"
                  % (f[:40], pa, old, new, hz_old, "" if ok else "  <-- RATE CHANGED"))
    print()
    print("Host x instances checked: %d   rate mismatches: %d   unexpected token changes: %d"
          % (checked, bad, other))


if __name__ == '__main__':
    main()
