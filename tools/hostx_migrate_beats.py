"""Convert stored Host x MULTIPLIERS into BEATS PER CYCLE.

2026-09-04, for the last two plugins on the old unit: Full_Feature_Tremolo and
full-feature-sweeping-filter (R13-revised). Every other plugin in the suite was
converted with nothing stored on Host x, so this is the only value migration
the whole rule needs.

    beats_per_cycle = 1 / multiplier

A stored 0.5 (half tempo) becomes 2 beats per cycle. A stored 8 (eight cycles
per beat) becomes 0.125.

ONLY instances whose Rate Mode reads Host x are touched. Everything else keeps
its number, because in Hz / Seconds / BPM the number never meant a multiplier
and inverting it would be pure damage. This is the whole reason the migration
is gated on the mode rather than applied to the slider.

AUTHORED table -- plugin name, the rate slider's id, the rate mode's id, and
which mode index is Host x. The script never infers these from source.

IDEMPOTENT? NO, and it cannot be: 1/x applied twice returns x, and there is
nothing in the file that distinguishes a converted value from an unconverted
one. Re-running it over the same project silently undoes it. So it writes
MIGRATED COPIES and refuses to touch the originals; promotion is a separate,
deliberate step after verification.
"""
import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

# plugin token -> (rate slider id, rate mode slider id, Host x index, slider count)
PLUGINS = {
    'Full_Feature_Tremolo':          (1, 2, 3, 40),
    'full-feature-sweeping-filter':  (3, 4, 3, 41),
}

ROOTS = [r'E:\reaper\finished', r'E:\reaper\to-play-with-later', r'E:\reaper\templates',
         r'E:\reaper\claude-experiments', r'E:\reaper\requires midi', r'E:\reaper']
OUT = os.path.join(os.environ.get('TEMP', '.'), 'hostx-beats-migrated')


def migrate_file(src, dst):
    raw = io.open(src, encoding='utf-8', newline='').read()
    lines = raw.split('\n')
    n_before = len(lines)
    touched = 0
    report = []
    for plug, (rv, rm, hostx, nsl) in PLUGINS.items():
        for i, l in enumerate(lines):
            if plug not in l:
                continue
            j = i + 1
            while not lines[j].strip():
                j += 1
            vals = parse_line(lines[j])
            mode = vals.get(rm)
            if mode in (None, '-') or abs(float(mode) - hostx) > 1e-9:
                continue
            old = vals.get(rv)
            assert old not in (None, '-'), "%s: Host x with no rate value stored" % plug
            f = float(old)
            assert f > 0, "%s: non-positive multiplier %r -- refusing to invert" % (plug, old)
            new_val = 1.0 / f
            assert 0.001 <= new_val <= 1000, \
                "%s: %g inverts to %g, outside the slider's range" % (plug, f, new_val)
            newv = dict(vals)
            # keep the token tidy: drop a trailing .0 the way REAPER writes integers
            newv[rv] = ('%g' % new_val)
            lines[j] = render_line(lines[j], newv, nsl)
            touched += 1
            report.append((plug, old, newv[rv]))
    assert len(lines) == n_before, "LINE COUNT CHANGED -- refusing to write"
    if touched:
        io.open(dst, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    return touched, report


def main():
    os.makedirs(OUT, exist_ok=True)
    tot = 0
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
            n, rep = migrate_file(src, dst)
            tot += n
            if n:
                print("%-46s %d converted" % (f[:46], n))
                for plug, a, b in rep:
                    print("      %-32s %s  ->  %s beats per cycle" % (plug, a, b))
    print()
    print("instances converted: %d" % tot)
    print("written to:", OUT)
    print("NOT idempotent -- 1/x twice is x. Do not re-run over a migrated file.")


if __name__ == '__main__':
    main()
