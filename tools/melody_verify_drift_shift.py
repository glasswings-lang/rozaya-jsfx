#!/usr/bin/env python3
"""Verify melody_migrate_drift_shift.py by reading the RESULT, not the run.

A clean script exit is the weakest available evidence. This re-reads both the
pre-migration snapshot and the migrated file from disk and checks, per instance:

  1. Sliders 1-66 are byte-identical to the snapshot. The insert was at 67, so
     nothing below it may have moved -- and the per-voice note/step durations
     live at 22-61, which is the thing that must not be touched.
  2. Every old slider N (67..75) now sits at N+1, token for token.
  3. Slider 67 (Ramp target) is the seeded 0.
  4. Every value sits inside its slider's declared range, read out of the plugin
     source rather than hand-typed. An out-of-range value is what exposed the
     original fault and is the cheapest possible detector of a shifted map.
  5. The drift block agrees with the instance's OWN @serialize blob. The blob
     was never touched by the migration, so it is an independent witness: its
     banks say up/down/per/shape for the selected target, and sliders 73/74/75/76
     must now match. This is the check that proves the repair is correct rather
     than merely self-consistent.
  6. Outside the melody value lines the two files are identical.

Usage:
    python tools/melody_verify_drift_shift.py <snapshot_dir> <live_file> [...]
    python tools/melody_verify_drift_shift.py --pairs SNAP=LIVE [SNAP=LIVE ...]
"""

import base64
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line  # noqa: E402

from melody_migrate_drift_shift import find_instances, OLD_MAGIC, INSERT_AT  # noqa: E402

DECL = re.compile(r'^slider(\d+):([^<]*)<([^,]*),([^,]*),([^>]*)>(.*)$')


def read_layout(src):
    lay = {}
    with open(src, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = DECL.match(ln.strip())
            if not m:
                continue
            lay[int(m.group(1))] = dict(
                lo=float(m.group(3)), hi=float(m.group(4)),
                name=m.group(6).split("}")[-1].strip())
    return lay


def load(path):
    with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        return fh.read().splitlines(keepends=True)


def blob_banks(lines, values_index, n_targets=28):
    """Read the @serialize blob that follows this instance. Returns dict or None."""
    j = values_index
    while j < len(lines) and lines[j].strip() != ">":
        j += 1
    j += 1
    if j >= len(lines) or not lines[j].strip().startswith("<JS_SER"):
        return None
    b64, k = "", j + 1
    while k < len(lines) and not lines[k].strip().startswith(">"):
        b64 += lines[k].strip()
        k += 1
    raw = base64.b64decode(b64)
    f = struct.unpack("<%df" % (len(raw) // 4), raw[:len(raw) // 4 * 4])
    N = n_targets
    if len(f) < 1 + 4 * N + 1:
        return None
    return dict(magic=f[0],
                up=f[1:1 + N], down=f[1 + N:1 + 2 * N],
                per=f[1 + 2 * N:1 + 3 * N], shape=f[1 + 3 * N:1 + 4 * N],
                sel=f[1 + 4 * N])


def verify(snap_path, live_path, layout):
    fails, checks = [], 0
    s_lines, l_lines = load(snap_path), load(live_path)
    s_inst, l_inst = find_instances(s_lines), find_instances(l_lines)

    if len(s_inst) != len(l_inst):
        return ["instance count changed: %d -> %d" % (len(s_inst), len(l_inst))], 0

    changed_lines = set()
    for n, ((svi, smagic), (lvi, _)) in enumerate(zip(s_inst, l_inst), 1):
        before, after = parse_line(s_lines[svi]), parse_line(l_lines[lvi])
        migrated = abs((smagic or 0) - OLD_MAGIC) <= 0.5 and \
            max((s for s, t in before.items() if t is not None), default=0) >= INSERT_AT
        if s_lines[svi] != l_lines[lvi]:
            changed_lines.add(lvi)

        if not migrated:
            checks += 1
            if s_lines[svi] != l_lines[lvi]:
                fails.append("#%d should NOT have been touched but the line changed" % n)
            continue

        # 1. nothing below the insert point moved
        for sid in range(1, INSERT_AT):
            checks += 1
            if before.get(sid) != after.get(sid):
                fails.append("#%d slider %d (%s) moved: %r -> %r"
                             % (n, sid, layout.get(sid, {}).get("name", "?"),
                                before.get(sid), after.get(sid)))
        # 2. old N -> new N+1
        for sid in range(INSERT_AT, 76):
            checks += 1
            if before.get(sid) != after.get(sid + 1):
                fails.append("#%d old slider %d = %r did not land at %d (found %r)"
                             % (n, sid, before.get(sid), sid + 1, after.get(sid + 1)))
        # 3. seed
        checks += 1
        if after.get(INSERT_AT) != "0":
            fails.append("#%d slider %d (Ramp target) seed is %r, expected '0'"
                         % (n, INSERT_AT, after.get(INSERT_AT)))
        # 4. range check
        for sid, tok in after.items():
            if tok is None or sid not in layout:
                continue
            checks += 1
            try:
                v = float(tok)
            except ValueError:
                fails.append("#%d slider %d is non-numeric %r" % (n, sid, tok))
                continue
            lo, hi = layout[sid]["lo"], layout[sid]["hi"]
            if not (lo - 1e-9 <= v <= hi + 1e-9):
                fails.append("#%d slider %d (%s) = %s OUT OF [%s,%s]"
                             % (n, sid, layout[sid]["name"], tok, lo, hi))
        # 5. agree with the untouched blob
        b = blob_banks(l_lines, lvi)
        if b:
            sel = int(round(b["sel"]))
            for sid, key in ((73, "up"), (74, "down"), (75, "per"), (76, "shape")):
                checks += 1
                want = b[key][sel]
                got = float(after.get(sid) or 0)
                if abs(want - got) > 1e-6:
                    fails.append("#%d slider %d (%s) = %s but blob target %d says %s"
                                 % (n, sid, layout[sid]["name"], got, sel, want))

    # 6. nothing else in the file changed
    checks += 1
    if len(s_lines) != len(l_lines):
        fails.append("line count changed: %d -> %d" % (len(s_lines), len(l_lines)))
    else:
        for i, (a, b) in enumerate(zip(s_lines, l_lines)):
            if a != b and i not in changed_lines:
                fails.append("line %d changed but is not a melody value line" % (i + 1))
    return fails, checks


def main():
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "src", "melody_phase.jsfx")
    layout_src = os.environ.get("MELODY_SRC", src)
    layout = read_layout(layout_src)
    print("layout from %s: %d sliders, max id %d\n"
          % (layout_src, len(layout), max(layout)))

    pairs = [a.split("=", 1) for a in sys.argv[1:]]
    total_f = total_c = 0
    for snap, live in pairs:
        fails, checks = verify(snap, live, layout)
        total_f += len(fails)
        total_c += checks
        status = "PASS" if not fails else "FAIL (%d)" % len(fails)
        print("%-46s %6d checks  %s" % (os.path.basename(live), checks, status))
        for f in fails[:25]:
            print("     - %s" % f)
    print("\nTOTAL %d checks, %d failures" % (total_c, total_f))
    sys.exit(1 if total_f else 0)


if __name__ == "__main__":
    main()
