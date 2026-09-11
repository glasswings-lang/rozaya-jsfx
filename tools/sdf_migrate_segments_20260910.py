#!/usr/bin/env python3
"""Sweep Dwell: the installed 46-control layout -> segments behind a selector (45),
per docs/layouts/sweep-dwell.md.

Reads the SNAPSHOT, writes the live project, so it is idempotent. Rewrites the
slider line AND replaces the blob: the segments' lengths, shapes and pitches are
no longer sliders, so they can only arrive in the blob (magic 2500016), which is
written here in exactly the order the plugin's @serialize reads it.

Every table below is authored from the layout doc.

Tensor's two Sweep Dwell instances are NOT here: they point at
`filters/sweep-dwell-filter.jsfx`, which does not exist in the Effects folder, so
REAPER has never loaded them. They are left untouched.

    python tools/sdf_migrate_segments_20260910.py            # dry run
    python tools/sdf_migrate_segments_20260910.py --apply
"""
import base64, os, re, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = "E:/reaper/finished/backups/snapshots/_pre-sdf-segments-20260910"
LIVE = {"to-play-with-later__surges.RPP": "E:/reaper/to-play-with-later/surges.RPP"}
NEW_N, N_T, N_SEG, MAGIC = 45, 16, 4, 2500016

# --- AUTHORED: installed (46) slider -> new slider, for the plain moves -------
MOVE = {9: 11, 10: 23, 11: 13, 12: 14, 13: 15, 14: 16, 15: 17, 16: 18, 17: 19,
        18: 20, 19: 21, 21: 25, 22: 26, 23: 27, 24: 28, 25: 29,
        26: 38, 27: 39, 28: 40, 29: 41, 30: 42, 31: 43, 32: 44, 33: 45,
        34: 30, 35: 31, 36: 32, 37: 33, 38: 34, 39: 35, 40: 36, 41: 37, 46: 12}
RETIRED = {42: "Cycle mode", 43: "Cycle length (beats)", 44: "Cycle length mode",
           45: "Pan speed (Linked Sweep)"}
TARGET_SLIDERS = (30, 38)                       # new ids of Drift / Ramp target
OLD_TO_NEW_TARGET = {0: 0, 1: 1, 2: 2, 3: 3, 4: 13, 5: 9}
# Installed defaults, for slots stored as '-'.
DEF46 = {1: 500, 2: 5000, 3: 4, 4: 6, 5: 1, 6: 1, 7: 1, 8: 1, 20: 1, 42: 0, 43: 12, 44: 0}


def num(slots, i):
    t = slots.get(i)
    return float(t) if t not in (None, "-") else float(DEF46[i])


def fmt(v):
    return ("%.10g" % v)


def old_blob(lines, vi):
    """The installed plugin's blob, decoded by ITS @serialize order."""
    k = next((k for k in range(vi + 1, vi + 4) if lines[k].strip().startswith("<JS_SER")), None)
    if k is None:
        return None, None, None
    j, b64 = k + 1, ""
    while lines[j].strip() != ">":
        b64 += lines[j].strip()
        j += 1
    raw = base64.b64decode(b64)
    v = list(struct.unpack("<%df" % (len(raw) // 4), raw))
    magic = v[0]
    if magic not in (2200006, 2300006):
        raise SystemExit(f"blob magic {magic} is not a format this script was written for")
    p = [1]
    def take(n):
        r = v[p[0]:p[0] + n]; p[0] += n; return r
    out = {"by": take(6), "dur": take(6), "delay": take(6), "last_sr": take(1)[0]}
    if magic == 2300006:
        out.update(dplay=take(6), drest=take(6), splay=take(6), srest=take(6))
    else:
        out.update(dplay=[0] * 6, drest=[0] * 6, splay=[0] * 6, srest=[0] * 6)
    out.update(up=take(6), down=take(6), per=take(6), shape=take(6), last_t=take(1)[0])
    if p[0] != len(v):
        raise SystemExit(f"blob has {len(v)} floats; decoded {p[0]} -- refusing")
    return out, k, j


def remap(bank6, default):
    new = [default] * N_T
    for o, n in OLD_TO_NEW_TARGET.items():
        new[n] = bank6[o]
    return new


def convert(path_in):
    text = open(path_in, "rb").read().decode("utf-8")
    lines = text.splitlines(keepends=True)
    n_before, count = len(lines), 0
    for i in reversed([i for i, l in enumerate(lines)
                       if re.search(r"<JS\s+glasswings/sweep-dwell-filter\.jsfx", l)]):
        vi = i + 1
        slots = parse_line(lines[vi])
        real = {k: t for k, t in slots.items() if t not in (None, "-")}
        if max(real) > 46:
            raise SystemExit(f"{path_in} line {vi + 1}: value above slider 46 -- refusing")

        # Segments: 0 High dwell, 1 Fade down, 2 Low dwell, 3 Fade up.
        lens = [num(slots, 3), num(slots, 5), num(slots, 4), num(slots, 7)]
        lmode = [1, 1, 1, 1]                               # Seconds
        if num(slots, 42) == 1:                            # Host x: lengths in beats
            lmode = [3, 3, 3, 3]
            if num(slots, 44) == 1:                        # Set in beats: scale to fit
                total = sum(lens)
                lens = [x * num(slots, 43) / total for x in lens]
        shape = [1, num(slots, 6), 1, num(slots, 8)]
        pmode = [0, 0, 0, 0]
        note = [111, 111, 71, 71]
        pval = [num(slots, 2), num(slots, 2), num(slots, 1), num(slots, 1)]
        fine, funit = [0] * 4, [2] * 4

        new = {}
        for o, t in real.items():
            if o in RETIRED or o in range(1, 9) or o == 20:
                continue
            if o not in MOVE:
                raise SystemExit(f"{path_in}: slider {o} has no authored mapping")
            new[MOVE[o]] = t
        new[22] = fmt(1 / max(num(slots, 20), 0.001))     # multiplier -> every N cycles
        new[24] = "1"                                      # Start delay mode = Seconds
        for s in TARGET_SLIDERS:
            if s in new:
                new[s] = str(OLD_TO_NEW_TARGET[int(float(new[s]))])
        # The segment block, showing High dwell -- what @serialize shows too.
        new.update({1: "1", 2: fmt(lmode[0]), 3: fmt(lens[0]), 4: fmt(shape[0]),
                    5: fmt(pmode[0]), 6: fmt(note[0]), 7: fmt(pval[0]), 8: "0", 9: "2",
                    10: "440"})

        ob, k, j = old_blob(lines, i + 2)
        if ob is None:
            ob = {"by": [0] * 6, "dur": [0] * 6, "delay": [0] * 6, "last_sr": 0,
                  "dplay": [0] * 6, "drest": [0] * 6, "splay": [0] * 6, "srest": [0] * 6,
                  "up": [0] * 6, "down": [0] * 6, "per": [8] * 6, "shape": [0] * 6, "last_t": 0}
        vals = ([MAGIC] + remap(ob["up"], 0) + remap(ob["down"], 0) + remap(ob["per"], 8)
                + remap(ob["shape"], 0) + [OLD_TO_NEW_TARGET[int(ob["last_t"])]]
                + remap(ob["by"], 0) + remap(ob["dur"], 0) + remap(ob["delay"], 0)
                + [OLD_TO_NEW_TARGET[int(ob["last_sr"])]]
                + remap(ob["dplay"], 0) + remap(ob["drest"], 0) + remap(ob["splay"], 0)
                + remap(ob["srest"], 0)
                + lmode + lens + shape + pmode + note + pval + fine + funit + [1])
        assert len(vals) == 1 + 4 * N_T + 1 + 3 * N_T + 1 + 4 * N_T + 8 * N_SEG + 1
        b64 = base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode("ascii")
        vl = lines[vi]
        eol = "\r\n" if vl.endswith("\r\n") else "\n"
        ind = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        blob = ([ind + "<JS_SER" + eol] + [ind + "  " + b64[x:x + 112] + eol
                                            for x in range(0, len(b64), 112)] + [ind + ">" + eol])
        close = next(c for c in range(vi + 1, vi + 3) if lines[c].strip() == ">")
        if k is not None:
            lines[k:j + 1] = blob
        else:
            lines[close + 1:close + 1] = blob
        lines[vi] = render_line(vl, new, NEW_N)
        count += 1
    return "".join(lines), count


def main():
    apply_it = "--apply" in sys.argv
    for name, live in LIVE.items():
        out, n = convert(os.path.join(SNAP, name))
        print(f"{live}: {n} instance(s) {'MIGRATED' if apply_it else 'would migrate'}")
        if apply_it:
            open(live, "w", encoding="utf-8", newline="").write(out)
    if not apply_it:
        print("re-run with --apply to write")


if __name__ == "__main__":
    main()
