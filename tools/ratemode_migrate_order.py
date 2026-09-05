"""Remap stored Rate Mode indices for the {Hz,Seconds,BPM,Host x} -> {BPM,Seconds,Hz,Host x} reorder.

2026-09-04. Full_Feature_Tremolo and full-feature-sweeping-filter ran the
suite's four rate modes in a different order from everybody else. The order is
now canonical, which moves the stored INDEX for two of the four:

    Hz       0 -> 2
    Seconds  1 -> 1
    BPM      2 -> 0
    Host x   3 -> 3

An enum option is an index stored inside the slider's value, so without this
every saved project would come back in the wrong unit -- a project in BPM would
read as Hz, and vice versa.

AUTHORED table. The script applies it; it never infers it from source.

NOT IDEMPOTENT, and it cannot be: 0<->2 is an involution, so a second run puts
everything back. There is nothing in the file that distinguishes a migrated
instance from an unmigrated one. So it writes MIGRATED COPIES and never touches
the originals; promotion is a separate, deliberate step after verification.
"""
import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

# plugin -> (rate mode slider id, slider count)
PLUGINS = {
    'Full_Feature_Tremolo':         (2, 40),
    'full-feature-sweeping-filter': (4, 41),
}
REMAP = {0: 2, 1: 1, 2: 0, 3: 3}

ROOTS = [r'E:\reaper\finished', r'E:\reaper\to-play-with-later', r'E:\reaper\templates',
         r'E:\reaper\claude-experiments', r'E:\reaper\requires midi', r'E:\reaper']
OUT = os.path.join(os.environ.get('TEMP', '.'), 'ratemode-order-migrated')


def migrate_file(src, dst):
    lines = io.open(src, encoding='utf-8', newline='').read().split('\n')
    n_before = len(lines)
    hdrs = [(i, p) for i, l in enumerate(lines) for p in PLUGINS if p in l]
    changed = 0
    for i, plug in hdrs:
        sid, nsl = PLUGINS[plug]
        j = i + 1
        while not lines[j].strip():
            j += 1
        vals = parse_line(lines[j])
        cur = vals.get(sid)
        if cur in (None, '-'):
            continue                      # nothing stored: takes the new default
        old = int(float(cur))
        assert old in REMAP, "%s: rate mode %r is not one of the four" % (plug, cur)
        new = dict(vals)
        new[sid] = str(REMAP[old])
        lines[j] = render_line(lines[j], new, nsl)
        changed += 1
    assert len(lines) == n_before, "LINE COUNT CHANGED -- refusing to write"
    if changed:
        io.open(dst, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    return changed


def main():
    os.makedirs(OUT, exist_ok=True)
    tot = nf = 0
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for f in sorted(os.listdir(root)):
            if not f.lower().endswith('.rpp'):
                continue
            src = os.path.join(root, f)
            txt = io.open(src, encoding='utf-8', errors='replace').read()
            if not any(p in txt for p in PLUGINS):
                continue
            dst = os.path.join(OUT, os.path.basename(root) + '__' + f)
            n = migrate_file(src, dst)
            if n:
                tot += n; nf += 1
                print("%-48s %d remapped" % (f[:48], n))
    print()
    print("files %d   instances remapped %d" % (nf, tot))
    print("written to:", OUT)
    print("NOT idempotent -- 0<->2 is an involution. Do not re-run over a migrated file.")


if __name__ == '__main__':
    main()
