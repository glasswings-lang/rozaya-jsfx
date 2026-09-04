"""Move stereo-phaser's rate triple contiguous, in the PROJECT FILE.

The 2026-09-04 reorder put Rate / Rate Mode / Host ratio together (they were at
1, 8 and 9). REAPER restores JSFX values by POSITION and knows nothing about
which slider a number belongs to, so the repair belongs here, in the numbers,
where it can be verified before anyone opens the project.

Rozaya, 2026-09-04, on an earlier attempt to do this at runtime inside the
plugin: "reaper only reads the numbers. It doesn't know what sliders they
correspond to." That runtime version was also a double-permute hazard -- a
correctly migrated project has no @serialize blob either, so the plugin could
not tell "old layout" from "already fixed".

Writes a MIGRATED COPY. It does not touch the original.
Verified by decoding both files control-by-control by NAME -- see the run log in
the 2026-09-04 commit: 27 controls, 0 mismatches, 0 values out of range, and 3
changed lines out of 192 with the rest byte-identical.
"""
import sys, io, os
sys.path.insert(0,'tools')
from rpp_sliders import parse_line, render_line

SRC = r'E:\reaper\finished\strangeness.RPP'
OUT = os.path.join(os.environ.get('TEMP','.'), 'strangeness.MIGRATED.RPP')
PERM = {1:1, 2:8, 3:9, 4:2, 5:3, 6:4, 7:5, 8:6, 9:7}   # new slot <- old slot

raw = io.open(SRC, encoding='utf-8', newline='').read()
lines = raw.split('\n')
n_before = len(lines)
hdrs = [i for i,l in enumerate(lines) if 'stereo-phaser.jsfx' in l]
assert len(hdrs) == 3, "expected 3 instances, found %d" % len(hdrs)

changed = 0
for i in hdrs:
    j = i + 1
    while not lines[j].strip(): j += 1
    orig = lines[j]
    vals = parse_line(orig)
    new  = dict(vals)
    for dst, src in PERM.items():
        new[dst] = vals.get(src)
    lines[j] = render_line(orig, new, 9)
    changed += 1

assert changed == 3, changed
assert len(lines) == n_before, "LINE COUNT CHANGED %d -> %d" % (n_before, len(lines))
io.open(OUT,'w',encoding='utf-8',newline='').write('\n'.join(lines))
print("instances rewritten: %d   line count %d -> %d (unchanged)" % (changed, n_before, len(lines)))
print("written: %s" % OUT)
