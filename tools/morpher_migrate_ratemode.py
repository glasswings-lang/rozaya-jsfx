"""Morpher: move every saved Rate Mode from the old enum's Seconds to the new one's.

2026-09-04. The Morpher's mode slider (8) has been three different things in one
day, and this migration exists because the LAST of those changes moved which
INDEX means Seconds:

    was  {Off, On}                      -- a Sync to host switch;   Off = 0
    then {Seconds, Beats}               -- a relabel, 0 still meant seconds
    then {Seconds, Minutes, Beats}      -- Minutes inserted, 0 still seconds
    now  {BPM, Seconds, Hz, Host x}     -- the suite's four. SECONDS IS 1.

Every saved instance stores 0. Under the new enum 0 is BPM, so an untouched
project would read its 20-second Auto-morph time as 20 BPM -- a three-second
period instead of twenty. Loud, wrong, and silent about it.

So: 0 -> 1, and ONLY 0. Anything else is refused rather than guessed at, because
nothing should have anything else and a surprise here means an assumption is
wrong.

IDEMPOTENT: a migrated instance holds 1, which is not 0, so a second run skips
it. Writes MIGRATED COPIES; does not touch originals.
"""
import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

PLUG = 'spectral_vowel_morpher'
MODE_ID = 8
OLD_SECONDS = '0'
NEW_SECONDS = '1'
N_SLIDERS = 49

ROOTS = [r'E:\reaper\finished', r'E:\reaper\to-play-with-later']
OUT = os.path.join(os.environ.get('TEMP', '.'), 'morpher-ratemode-migrated')


def migrate_file(src, dst):
    lines = io.open(src, encoding='utf-8', newline='').read().split('\n')
    n_before = len(lines)
    hdrs = [i for i, l in enumerate(lines) if PLUG in l]
    changed = skipped = 0
    for i in hdrs:
        j = i + 1
        while not lines[j].strip():
            j += 1
        vals = parse_line(lines[j])
        cur = vals.get(MODE_ID)
        if cur == NEW_SECONDS:
            skipped += 1
            continue
        assert cur == OLD_SECONDS, \
            "unexpected Rate Mode %r -- expected %r; refusing to guess" % (cur, OLD_SECONDS)
        new = dict(vals)
        new[MODE_ID] = NEW_SECONDS
        lines[j] = render_line(lines[j], new, N_SLIDERS)
        changed += 1
    assert len(lines) == n_before, "LINE COUNT CHANGED -- refusing to write"
    assert [i for i, l in enumerate(lines) if PLUG in l] == hdrs, \
        "instance count/positions changed -- refusing to write"
    io.open(dst, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    return len(hdrs), changed, skipped


def main():
    os.makedirs(OUT, exist_ok=True)
    ti = tc = ts = nf = 0
    for root in ROOTS:
        for f in sorted(os.listdir(root)):
            if not f.lower().endswith('.rpp'):
                continue
            src = os.path.join(root, f)
            if PLUG not in io.open(src, encoding='utf-8', errors='replace').read():
                continue
            dst = os.path.join(OUT, os.path.basename(root) + '__' + f)
            i, c, s = migrate_file(src, dst)
            ti += i; tc += c; ts += s; nf += 1
    print("files %d   instances %d   set to Seconds %d   already done %d" % (nf, ti, tc, ts))
    print("written to:", OUT)


if __name__ == '__main__':
    main()
