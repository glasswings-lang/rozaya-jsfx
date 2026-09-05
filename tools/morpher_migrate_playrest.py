"""Move Drift/Ramp play/rest into their LOGICAL slider positions, in the project files.

2026-09-04. Drift play/rest and Ramp play/rest were first appended at 41-44,
which is the safe-but-ugly option. Rozaya: "Preferably, in a place that makes
sense. No tacking sliders onto the end bullshit." So they went where they
belong -- 35/36 beside the Drift amounts, 41/42 beside Ramp duration -- and
REAPER restores JSFX values by POSITION, so every project saved on the old
layout needs its slider line shifted.

AUTHORED permutation. This script APPLIES a table a human wrote; it never
INFERS one from the files (CLAUDE.md). Everything below 35 is untouched.

    old 35 Drift restart     -> new 37
    old 36 Ramp target       -> new 38
    old 37 Ramp by           -> new 39
    old 38 Ramp duration     -> new 40
    old 39 Ramp engage       -> new 43
    old 40 Ramp start delay  -> new 44
    new 35, 36 (Drift play/rest) and 41, 42 (Ramp play/rest) are seeded to 0,
    which is "off" -- so a migrated project sounds EXACTLY as it did.

IDEMPOTENT. An unmigrated instance has nothing stored above slider 40 (the old
plugin only had 40), so tokens 41-44 read as "-". After migration they hold
real numbers. Any instance with a value at 43 or 44 is therefore already done
and is skipped, not permuted a second time.

Writes MIGRATED COPIES into a folder; it does not touch the originals.
Verify with tools/morpher_verify_playrest.py before putting anything in place.
"""
import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

PERM = {37: 35, 38: 36, 39: 37, 40: 38, 43: 39, 44: 40}   # new slot <- old slot
SEED = (35, 36, 41, 42)                                    # new controls, seeded to 0
N_SLIDERS = 44                                             # the plugin's slider count AFTER the change

ROOTS = [r'E:\reaper\finished', r'E:\reaper\to-play-with-later']
OUT   = os.path.join(os.environ.get('TEMP', '.'), 'morpher-playrest-migrated')


def migrate_file(src, dst):
    raw = io.open(src, encoding='utf-8', newline='').read()
    lines = raw.split('\n')
    n_before = len(lines)
    hdrs = [i for i, l in enumerate(lines) if 'spectral_vowel_morpher' in l]
    changed = skipped = 0
    for i in hdrs:
        j = i + 1
        while not lines[j].strip():
            j += 1
        vals = parse_line(lines[j])
        if vals.get(43) not in (None, '-') or vals.get(44) not in (None, '-'):
            skipped += 1
            continue
        new = dict(vals)
        for dstid, srcid in PERM.items():
            new[dstid] = vals.get(srcid)
        for s in SEED:
            new[s] = '0'
        out = render_line(lines[j], new, N_SLIDERS)
        assert out != lines[j] or not hdrs, "no-op rewrite"
        lines[j] = out
        changed += 1
    assert len(lines) == n_before, "LINE COUNT CHANGED -- refusing to write"
    hdrs_after = [i for i, l in enumerate(lines) if 'spectral_vowel_morpher' in l]
    assert hdrs_after == hdrs, "instance count/positions changed -- refusing to write"
    io.open(dst, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    return len(hdrs), changed, skipped


def main():
    os.makedirs(OUT, exist_ok=True)
    tot_i = tot_c = tot_s = 0
    nfiles = 0
    for root in ROOTS:
        for f in sorted(os.listdir(root)):
            if not f.lower().endswith('.rpp'):
                continue
            src = os.path.join(root, f)
            if 'spectral_vowel_morpher' not in io.open(src, encoding='utf-8', errors='replace').read():
                continue
            dst = os.path.join(OUT, os.path.basename(root) + '__' + f)
            i, c, s = migrate_file(src, dst)
            tot_i += i; tot_c += c; tot_s += s; nfiles += 1
            print("%-52s instances %-3d migrated %-3d skipped %d" % (f[:52], i, c, s))
    print()
    print("files %d   instances %d   migrated %d   already-done %d" % (nfiles, tot_i, tot_c, tot_s))
    print("written to:", OUT)


if __name__ == '__main__':
    main()
