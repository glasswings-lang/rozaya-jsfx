"""Verify the Morpher play/rest slider migration -- by NAME, against a snapshot.

Deliberately does NOT use the permutation table the migration used: a check
against the same table would agree with itself perfectly (CLAUDE.md, and the
Melody break that this rule came from). It decodes both the pre-migration
snapshot and the migrated copy by CONTROL NAME, from the two versions of the
plugin source, and compares.

Also range-checks every migrated value against its control's declared min/max,
which is the fastest possible proof that a mapping shifted and needs no ears.
"""
import sys, io, os, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line

SNAP = r'E:\reaper\finished\backups\snapshots\_pre-morpher-playrest-20260904'
MIG  = os.path.join(os.environ.get('TEMP', '.'), 'morpher-playrest-migrated')
OLD_REV = '0ad893d^:src/spectral_vowel_morpher.jsfx'
NEW_SRC = 'src/spectral_vowel_morpher.jsfx'

DECL = re.compile(r'^slider(\d+):([^<]*)<([^,]*),([^,]*),([^>]*)>(.*)')


def decls(text):
    out = {}
    for line in text.splitlines():
        m = DECL.match(line.strip())
        if m:
            out[int(m.group(1))] = (m.group(6).strip(), float(m.group(3)), float(m.group(4)))
    return out


def instances(path):
    lines = io.open(path, encoding='utf-8', newline='').read().split('\n')
    out = []
    for i, l in enumerate(lines):
        if 'spectral_vowel_morpher' in l:
            j = i + 1
            while not lines[j].strip():
                j += 1
            out.append(parse_line(lines[j]))
    return out


def main():
    old = decls(subprocess.check_output(['git', 'show', OLD_REV]).decode('utf-8', 'replace'))
    new = decls(io.open(NEW_SRC, encoding='utf-8', errors='replace').read())
    print("old layout: %d sliders   new layout: %d sliders" % (len(old), len(new)))

    old_by_name = {}
    for i, (n, _, _) in old.items():
        old_by_name.setdefault(n, []).append(i)
    new_by_name = {}
    for i, (n, _, _) in new.items():
        new_by_name.setdefault(n, []).append(i)

    shared = [n for n in old_by_name if n in new_by_name]
    for n in shared:
        assert len(old_by_name[n]) == 1 and len(new_by_name[n]) == 1, "ambiguous name: " + n
    added = sorted(set(new_by_name) - set(old_by_name))
    dropped = sorted(set(old_by_name) - set(new_by_name))
    print("names carried over: %d   added: %s   dropped: %s"
          % (len(shared), added or 'none', dropped or 'none'))

    files = sorted(f for f in os.listdir(SNAP) if f.lower().endswith('.rpp'))
    checked = mism = oor = seeded = 0
    ninst = 0
    for f in files:
        a = instances(os.path.join(SNAP, f))
        b = instances(os.path.join(MIG, f))
        assert len(a) == len(b), "instance count differs in " + f
        ninst += len(a)
        for va, vb in zip(a, b):
            for n in shared:
                oi, ni = old_by_name[n][0], new_by_name[n][0]
                x, y = va.get(oi), vb.get(ni)
                checked += 1
                if x != y:
                    mism += 1
                    print("MISMATCH %-40s %-28s old=%r new=%r" % (f[:40], n, x, y))
            for n in added:
                ni = new_by_name[n][0]
                seeded += 1
                if vb.get(ni) != '0':
                    mism += 1
                    print("SEED WRONG %-38s %-28s = %r" % (f[:38], n, vb.get(ni)))
            for i, (n, lo, hi) in new.items():
                t = vb.get(i)
                if t in (None, '-') or str(t).startswith('"'):
                    continue
                v = float(t)
                if v < lo - 1e-9 or v > hi + 1e-9:
                    oor += 1
                    print("OUT OF RANGE %-34s %-28s %s not in [%s, %s]" % (f[:34], n, v, lo, hi))

    print()
    print("files %d   instances %d" % (len(files), ninst))
    print("name comparisons %d   mismatches %d" % (checked, mism))
    print("new controls seeded %d" % seeded)
    print("values out of range %d" % oor)


if __name__ == '__main__':
    main()
