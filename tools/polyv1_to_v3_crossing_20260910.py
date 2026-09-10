#!/usr/bin/env python3
"""Polyrhythm Phase v1 -> v3, per docs/layouts/polyrhythm-v1-to-v3-crossing.md.

Rewrites each `<JS .../polyrhythm_phase.jsfx` instance as a v3 instance: the JS
line's filename, a 59-slider value line, and a native 2300088 `<JS_SER>` blob
(created where the instance had none).

Refuses rather than guessing: a fractional semitone, a quoted token, a blob that
is neither absent nor 2100024 x 171, an unrecognised line shape, or a line-count
change other than the blob lines it added.

Dry run by default; --apply writes. Paths must be given (the scope is authored in
the layout doc, not inferred here).
"""
import sys, base64, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line, fmt, SliderLineError, is_quoted

N = 88
V1_DEFAULTS = {1: 0, 2: 0, 3: 60, 4: 4, 5: 100, 6: 0, 7: 100, 8: 1, 9: 1, 10: -6, 11: 440,
               12: 0, 13: 4, 14: 0, 15: 0, 16: 0, 17: 100, 18: 60, 19: 0,
               60: 0, 61: 0, 62: 0, 63: 0, 64: 0, 69: 0, 70: 0, 71: 0, 72: 0, 73: 25,
               74: 0, 75: 0, 76: 0, 77: 8, 78: 0, 79: 0, 80: 0, 81: 0, 82: 0, 83: 0, 84: 0,
               85: 10, 86: 8}
for _v in range(8):
    V1_DEFAULTS.update({20 + 5 * _v: -6, 21 + 5 * _v: 0, 22 + 5 * _v: 0, 23 + 5 * _v: 0,
                        24 + 5 * _v: 1 if _v == 0 else 0})
# Slider values that end up in a float32 bank in v3 (used by the verifier too).
BANK_BOUND = [5, 6, 7, 10, 14] + list(range(20, 60)) + [75, 76, 77, 78, 80, 81, 83]


def old_to_new_target(t):
    t = int(t)
    if t == 0: return 0
    if 1 <= t <= 8: return 27 + t
    if t == 9: return 82
    if t == 10: return 83
    if t == 11: return 3
    if t == 12: return 45
    if 13 <= t <= 20: return 60 + t
    return {21: 36, 22: 54, 23: 63}[t]


def is_all(t): return 9 <= t <= 72 and (t - 9) % 9 == 0
def read_slot(t): return t + 1 if is_all(t) else t


def tgt_write(bank, t, val):
    if is_all(t):
        for k in range(1, 9): bank[t + k] = val
    else:
        bank[t] = val


def parse_v1_line(line):
    try:
        return parse_line(line)
    except SliderLineError:
        toks = line.split()
        # Tensor's hand-written line: 59 values then more dashes than REAPER writes.
        if len(toks) > 64 and all(t == "-" for t in toks[59:]):
            return {i + 1: (None if t == "-" else t) for i, t in enumerate(toks[:59])}
        raise


def v1_value(slots, k):
    tok = slots.get(k)
    if tok is None:
        return float(V1_DEFAULTS[k]), None
    if is_quoted(tok):
        raise SliderLineError(f"slider{k} is quoted: {tok!r}")
    return float(tok), tok


def convert_instance(slots, blob):
    val = lambda k: v1_value(slots, k)[0]
    tok = lambda k: v1_value(slots, k)[1] or fmt(V1_DEFAULTS[k])

    up, down, per, shape = [0.0] * N, [0.0] * N, [8.0] * N, [0.0] * N
    by, dur, delay = [0.0] * N, [0.0] * N, [0.0] * N
    zero = [0.0] * N
    if blob is not None:
        fl = struct.unpack("<%df" % (len(blob) // 4), blob)
        if not (len(fl) == 171 and fl[0] == 2100024):
            raise ValueError(f"unrecognised blob: {len(fl)} floats, first {fl[0]}")
        o = 1
        o_up, o_down, o_per, o_shape = fl[o:o + 24], fl[o + 24:o + 48], fl[o + 48:o + 72], fl[o + 72:o + 96]
        last_t = fl[97]
        o_by, o_dur, o_delay = fl[98:122], fl[122:146], fl[146:170]
        last_s = fl[170]
        for t in range(24):
            n = old_to_new_target(t)
            for bank, src in ((up, o_up), (down, o_down), (per, o_per), (shape, o_shape),
                              (by, o_by), (dur, o_dur), (delay, o_delay)):
                tgt_write(bank, n, src[t])
        sel_d, sel_r = old_to_new_target(last_t), old_to_new_target(last_s)
    else:
        # v1 on load with no blob: last selector 0, so the first @slider saves the
        # visible values into target 0 and then loads the saved target's defaults.
        up[0], down[0], per[0], shape[0] = val(75), val(76), val(77), val(78)
        by[0], dur[0], delay[0] = val(80), val(81), val(83)
        sel_d, sel_r = old_to_new_target(val(74)), old_to_new_target(val(79))

    b, c = val(12), val(13)
    vm = {k: [0.0] * 8 for k in ("note", "fine", "dr", "phoff", "wave", "depth", "ondur",
                                 "att", "rel", "gain", "active", "solo", "pmode", "pval", "funit")}
    flagged = []
    for v in range(8):
        semi = val(21 + 5 * v)
        # A voice between notes becomes the nearest note plus the rest in cents --
        # the way v3 says a microtonal pitch. Whole-number voices get 0 cents and
        # stay bit-exact; a between-notes voice differs only by float rounding.
        exact = 60 + (c - 4) * 12 + b + semi
        pval = float(round(exact))
        cents = round((exact - pval) * 100, 6)
        if cents != 0:
            flagged.append(f"V{v+1} between notes: {exact:g} -> note {pval:g} {cents:+g} cents")
        vm["fine"][v] = cents
        active = val(24 + 5 * v)
        if pval < 0:
            if active:
                raise ValueError(f"active V{v+1} lands below MIDI 0 ({pval})")
            flagged.append(f"inactive V{v+1} pitch {pval} held at 0")
            pval = 0.0
        vm["pval"][v] = pval
        vm["note"][v] = float(min(127, max(0, round(pval))))
        vm["pmode"][v] = 1.0
        vm["funit"][v] = 2.0
        vm["gain"][v] = val(20 + 5 * v)
        vm["dr"][v] = val(22 + 5 * v)
        vm["phoff"][v] = val(23 + 5 * v)
        vm["active"][v] = active
        vm["wave"][v] = val(14)
        vm["depth"][v] = val(10)
        vm["ondur"][v] = val(5)
        vm["att"][v] = val(6)
        vm["rel"][v] = val(7)

    ds, rs = read_slot(sel_d), read_slot(sel_r)
    new = {
        1: tok(1), 2: tok(3), 3: tok(2), 4: tok(8), 5: tok(9), 6: tok(11), 7: "0", 8: "0",
        9: tok(4), 10: tok(73), 11: tok(69), 12: tok(70), 13: tok(71), 14: tok(72), 15: "1",
        16: "1", 17: fmt(vm["note"][0]), 18: fmt(vm["pval"][0]), 19: fmt(vm["fine"][0]), 20: "2",
        21: tok(22), 22: tok(23), 23: tok(14), 24: tok(10), 25: tok(5), 26: tok(6), 27: tok(7),
        28: tok(20), 29: tok(24), 30: "0",
        31: tok(15), 32: tok(16), 33: tok(17), 34: tok(18), 35: tok(2), 36: tok(19),
        37: tok(86), 38: tok(85), 39: tok(60), 40: tok(61), 41: tok(62), 42: tok(63), 43: tok(64),
        44: str(sel_d), 45: fmt(up[ds]), 46: fmt(down[ds]), 47: fmt(per[ds]), 48: "0",
        49: fmt(shape[ds]), 50: "0", 51: "0",
        52: str(sel_r), 53: fmt(by[rs]), 54: "2", 55: fmt(dur[rs]), 56: "0", 57: "0",
        58: tok(82), 59: fmt(delay[rs]),
    }
    floats = [2300088.0] + up + down + per + shape + [float(sel_d)] + by + dur + delay + \
             [float(sel_r)] + zero + zero + zero + zero
    for k in ("note", "fine", "dr", "phoff", "wave", "depth", "ondur", "att", "rel", "gain", "active", "solo"):
        floats += vm[k]
    floats += [1.0] + vm["pmode"] + vm["pval"] + vm["funit"]
    assert len(floats) == 1092
    return new, struct.pack("<1092f", *floats), flagged


def convert_file(path, apply_it):
    raw = path.read_bytes().decode("utf-8", errors="surrogateescape")
    lines = raw.splitlines(keepends=True)
    n_before = len(lines)
    eol = "\r\n" if lines[0].endswith("\r\n") else "\n"
    out, i, count, added, notes = [], 0, 0, 0, []
    while i < len(lines):
        l = lines[i]
        if "<JS " in l and "polyrhythm_phase.jsfx" in l:
            count += 1
            assert l.count("polyrhythm_phase.jsfx") == 1
            indent = l[:len(l) - len(l.lstrip())]
            slots = parse_v1_line(lines[i + 1])
            if lines[i + 2].strip() != ">":
                raise RuntimeError(f"{path}:{i+3}: expected '>' closing the JS block")
            j = i + 3
            blob, old_ser_lines = None, 0
            if j < len(lines) and lines[j].strip() == "<JS_SER":
                b64, k = "", j + 1
                while lines[k].strip() != ">": b64 += lines[k].strip(); k += 1
                blob = base64.b64decode(b64)
                old_ser_lines = k - j + 1
            new, newblob, flagged = convert_instance(slots, blob)
            notes += [f"#{count}: {f}" for f in flagged]
            out.append(l.replace("polyrhythm_phase.jsfx", "polyrhythm_phase_v3.jsfx"))
            out.append(render_line(lines[i + 1], new, n_sliders=59))
            out.append(lines[i + 2])
            enc = base64.b64encode(newblob).decode()
            ser = [indent + "<JS_SER" + eol] + [indent + "  " + enc[p:p + 128] + eol for p in range(0, len(enc), 128)] \
                  + [indent + ">" + eol]
            out += ser
            added += len(ser) - old_ser_lines
            i = j + old_ser_lines
            continue
        out.append(l)
        i += 1
    assert len(out) == n_before + added, (len(out), n_before, added)
    if apply_it and count:
        path.write_bytes("".join(out).encode("utf-8", errors="surrogateescape"))
    return count, notes


def main():
    apply_it = "--apply" in sys.argv
    paths = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        sys.exit("give the files to convert; the scope is authored, not searched for")
    total = 0
    for p in paths:
        c, notes = convert_file(p, apply_it)
        total += c
        print(f"{'CONVERTED' if apply_it else 'would convert'} {c:>2}  {p}" + ("".join("\n    " + n for n in notes)))
    print(f"total instances: {total}")


if __name__ == "__main__":
    main()
