"""Shift the Morpher's Drift and Ramp blocks up by five, for the transport block.

2026-09-04. The Morpher gained Start delay, Play for, Rest for, Modulation at
rest and Output at rest -- the canonical transport block -- and they went into
their LOGICAL position at sliders 30-34 rather than being appended. Rozaya:
"put them in, in a logical place, not scattered through the list or appended to
the end, we can afford not to append."

REAPER restores JSFX values by POSITION, so every project saved before this
needs its slider line shifted.

AUTHORED permutation. This script APPLIES a table a human wrote; it never
INFERS one from the source (CLAUDE.md).

    old 30..44  ->  new 35..49      (Drift target .. Ramp start delay, +5)
    new 30..34  ->  seeded to 0

    0 is the OFF value for all five: no start delay, gate disabled, Walk
    through, Pass-through. So a migrated project behaves EXACTLY as it did.

IDEMPOTENT. An unmigrated instance has nothing stored above slider 44 -- the
plugin only had 44 -- so tokens 45-49 read as "-". After migration they hold
real numbers. Any instance with a value at 48 or 49 is already done and is
skipped rather than shifted a second time.

Writes MIGRATED COPIES into a folder; it does not touch the originals. Verify
with tools/morpher_verify_transport.py before putting anything in place.
"""
import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SHIFT_FROM, SHIFT_TO, SHIFT_BY = 30, 44, 5
SEED = (30, 31, 32, 33, 34)
N_SLIDERS = 49                    # the plugin's slider count AFTER the change
N_SLIDERS_BEFORE = 44

ROOTS = [r'E:\reaper\finished', r'E:\reaper\to-play-with-later']
OUT = os.path.join(os.environ.get('TEMP', '.'), 'morpher-transport-migrated')


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
        already = any(vals.get(k) not in (None, '-') for k in (48, 49))
        if already:
            skipped += 1
            continue
        new = dict(vals)
        # walk DOWNWARD so a destination is never written before it is read
        for old_id in range(SHIFT_TO, SHIFT_FROM - 1, -1):
            new[old_id + SHIFT_BY] = vals.get(old_id)
        for k in SEED:
            new[k] = '0'
        out = render_line(lines[j], new, N_SLIDERS)
        lines[j] = out
        changed += 1
    assert len(lines) == n_before, "LINE COUNT CHANGED -- refusing to write"
    hdrs_after = [i for i, l in enumerate(lines) if 'spectral_vowel_morpher' in l]
    assert hdrs_after == hdrs, "instance count/positions changed -- refusing to write"
    io.open(dst, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    return len(hdrs), changed, skipped


def main():
    os.makedirs(OUT, exist_ok=True)
    tot_i = tot_c = tot_s = nfiles = 0
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
