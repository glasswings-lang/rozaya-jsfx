"""Round-trip tools/rpp_sliders.py against every JS value line in the library.

Parse then re-render must reproduce the original line exactly. Any line it
cannot handle is reported rather than skipped -- an unparsed line is exactly the
kind of thing that shifted Melody's sliders.
"""
import glob
import io
import os
import re
import sys

sys.path.insert(0, r"C:\git-src\rozaya-jsfx\tools")
import rpp_sliders as R

roots = [r"E:\reaper\finished", r"E:\reaper\to-play-with-later"]
total = ok = 0
errors = []
mismatches = []
shapes = {}

for root in roots:
    for p in sorted(glob.glob(os.path.join(root, "*.RPP"))):
        lines = io.open(p, encoding="utf-8", errors="surrogateescape",
                        newline="").read().split("\n")
        for i, l in enumerate(lines):
            if "<JS " not in l or i + 1 >= len(lines):
                continue
            m = re.search(r'<JS\s+\S*?([A-Za-z0-9_.\-]+\.jsfx)', l)
            if not m:
                continue
            line = lines[i + 1]
            total += 1
            try:
                slots = R.parse_line(line)
            except R.SliderLineError as e:
                errors.append("%s:%d %s" % (os.path.basename(p), i + 1, e))
                continue
            n = max(slots) if slots else 0
            shapes.setdefault(m.group(1), set()).add(n)
            try:
                out = R.render_line(line, slots, n)
            except R.SliderLineError as e:
                errors.append("%s:%d render: %s" % (os.path.basename(p), i + 1, e))
                continue
            if out.rstrip() != line.rstrip():
                mismatches.append((os.path.basename(p), i + 1,
                                   line.strip()[:110], out.strip()[:110]))
            else:
                ok += 1

print("JS value lines seen      : %d" % total)
print("round-tripped identically: %d" % ok)
print("parse/render errors      : %d" % len(errors))
print("byte mismatches          : %d" % len(mismatches))
print("")
for e in errors[:8]:
    print("  ERROR " + e)
for name, ln, a, b in mismatches[:5]:
    print("  MISMATCH %s:%d\n     was %s\n     got %s" % (name, ln, a, b))
print("")
print("highest slider id seen per plugin:")
for k in sorted(shapes):
    print("   %-34s %s" % (k, sorted(shapes[k])))
sys.exit(1 if (errors or mismatches) else 0)
