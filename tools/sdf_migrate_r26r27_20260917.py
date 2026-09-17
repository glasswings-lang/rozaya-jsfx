#!/usr/bin/env python3
"""Sweep Dwell's 2026-09-17 turn: 45 controls -> 52, and blob 2500016 -> 2600018.

Authored from docs/layouts/sweep-dwell-filter-r26r27-20260917.md. Every table here is
written from that layout; nothing is inferred from the projects.

What changes in a saved copy, and why it still sounds the same:
  * Resonance, Pan spread and Wet/dry become percents, so they and any drift or ramp
    amount aimed at them are multiplied by 100.
  * The three `(Flipped)` pan choices become their partner plus `Pan direction` Flipped.
  * `Start delay mode` becomes the shared `Transport unit`. Play for and Rest for have
    always counted dwell cycles, so a copy whose Start delay is 0 lands on Cycles with
    every number untouched; see transport_unit() for the other two cases.
  * The new per-target banks are seeded so the plugin does what it did: the one shared
    period unit and ramp time unit go to every target, the amount units to `Target
    default` (which is what an amount meant), and `Drift movement mode` to `On a clock`,
    the live reading this plugin has always used. A NEW instance starts on `With the
    target`, which is the suite's default.

    python tools/sdf_migrate_r26r27_20260917.py            # dry run, prints every change
    python tools/sdf_migrate_r26r27_20260917.py --apply
"""
import base64
import glob
import os
import re
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = "E:/reaper/finished/backups/snapshots/sweep-dwell-r26r27-20260917"
OLD_MAGIC, NEW_MAGIC = 2500016, 2600018
OLD_N, NEW_N = 16, 18          # targets
N_SEG, NEW_SLIDERS = 4, 52

# --- AUTHORED: old slider -> new slider, where the value carries across unchanged ---
MOVE = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 12: 12, 13: 13,
        14: 14, 15: 15, 18: 19, 19: 20, 20: 21, 21: 22, 28: 30, 29: 31,
        30: 32, 31: 33, 32: 34, 33: 36, 34: 37, 35: 39, 36: 40, 37: 41,
        38: 43, 39: 44, 40: 46, 41: 47, 42: 48, 43: 49, 44: 51, 45: 52}
PERCENT = {11: 11, 17: 18, 23: 25}          # old -> new, value x100
PAN = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (6, 0), 4: (6, 1), 5: (7, 0), 6: (8, 0),
       7: (9, 0), 8: (10, 0), 9: (11, 0), 10: (14, 0), 11: (14, 1), 12: (12, 0),
       13: (2, 0), 14: (3, 0), 15: (4, 0)}
PERCENT_TARGETS = (9, 11, 15)               # Resonance, Pan spread, Wet/dry mix
# New controls that are not carried from anything.
NEW_DEFAULTS = {23: "0", 35: "0", 38: "1", 42: "0", 45: "0", 50: "0"}
# Slider defaults, for slots a project stores as '-'.
DEF = {2: 1, 3: 4, 5: 0, 9: 2, 10: 440, 11: 0.7, 17: 1, 20: 2, 21: 0, 22: 1, 23: 1,
       24: 1, 25: 0, 26: 0, 27: 0, 30: 0, 33: 8, 34: 0, 38: 0, 40: 2}


def num(slots, i):
    t = slots.get(i)
    if t in (None, "-"):
        return float(DEF.get(i, 0))
    return float(t)


def fmt(v):
    return "%.10g" % v


def len_secs(mode, v, bpm=120.0):
    """A length in seconds, exactly as the plugin reads it (host tempo 120 unless given)."""
    if mode == 1:
        return v
    if mode == 0:
        return 60 / max(v, 0.001)
    if mode == 2:
        return 1 / max(v, 0.001)
    if mode == 3:
        return v * 60 / bpm
    return 60 / bpm / max(v, 0.001)


def transport_unit(delay, delay_mode, play, rest, cycle_secs, bpm=120.0):
    """The one Transport unit, and the three numbers under it.

    Start delay had its own rate mode; Play for and Rest for counted dwell cycles. One
    unit now covers all three, so the case that keeps the most meaning wins:
      nothing set, or only Play/Rest    -> Cycles, numbers untouched
      only a Start delay               -> Seconds, the delay converted from its rate mode
      both                             -> Seconds; Play/Rest were cycles, so they are
                                          converted with the SAVED cycle length, which is
                                          the length they were counting.
    """
    if delay <= 0:
        return 0, 0.0, play, rest
    delay_sec = len_secs(int(delay_mode), delay, bpm)
    if play <= 0 and rest <= 0:
        return 1, delay_sec, play, rest
    return 1, delay_sec, play * cycle_secs, rest * cycle_secs


def blob_span(lines, i):
    """The <JS_SER block after instance line i: (first line, terminator line, floats)."""
    k = next((k for k in range(i, i + 4) if lines[k].strip().startswith("<JS_SER")), None)
    if k is None:
        return None
    j, b64 = k + 1, ""
    while lines[j].strip() != ">":
        b64 += lines[j].strip()
        j += 1
    raw = base64.b64decode(b64)
    return k, j, list(struct.unpack("<%df" % (len(raw) // 4), raw))


def read_old(vals):
    """The 2500016 blob, in the order the installed plugin's @serialize writes it."""
    if int(round(vals[0])) != OLD_MAGIC:
        raise SystemExit("blob magic %d is not 2500016 -- refusing" % int(round(vals[0])))
    p = [1]

    def take(n):
        r = vals[p[0]:p[0] + n]
        p[0] += n
        return r

    o = {}
    for k in ("up", "down", "per", "shape"):
        o[k] = take(OLD_N)
    o["last_t"] = take(1)[0]
    for k in ("by", "dur", "delay"):
        o[k] = take(OLD_N)
    o["last_sr"] = take(1)[0]
    for k in ("dplay", "drest", "splay", "srest"):
        o[k] = take(OLD_N)
    for k in ("lmode", "len", "sshape", "pmode", "note", "pval", "fine", "funit"):
        o[k] = take(N_SEG)
    o["last_seg"] = take(1)[0]
    if p[0] != len(vals):
        raise SystemExit("blob holds %d floats, decoded %d -- refusing" % (len(vals), p[0]))
    return o


def grow(bank, default, scale_percent=False):
    """16 targets -> 18 (Play for and Rest for appended, so nothing renumbers)."""
    out = list(bank) + [default, default]
    if scale_percent:
        out = [v * 100 if i in PERCENT_TARGETS else v for i, v in enumerate(out)]
    return out


def convert_instance(slots, ob, path, vi):
    """One copy: the new slider dict and the new blob floats."""
    real = {k: t for k, t in slots.items() if t not in (None, "-")}
    if real and max(real) > 45:
        raise SystemExit("%s line %d: a value above slider 45 -- refusing" % (path, vi + 1))
    new = {}
    for o, t in real.items():
        if o in MOVE:
            new[MOVE[o]] = t
    for o, n in PERCENT.items():
        new[n] = fmt(num(slots, o) * 100)
    mode, flip = PAN[int(round(num(slots, 16)))]
    new[16], new[17] = str(mode), str(flip)
    new[24] = fmt(num(slots, 22))                       # Pan sweep every, its mode below
    for k, v in NEW_DEFAULTS.items():
        new[k] = v
    # One Transport unit over the three transport numbers.
    cycle_secs = sum(len_secs(int(ob["lmode"][s]), ob["len"][s]) for s in range(N_SEG))
    unit, delay, play, rest = transport_unit(num(slots, 25), num(slots, 24),
                                             num(slots, 26), num(slots, 27), cycle_secs)
    new[26], new[27], new[28], new[29] = str(unit), fmt(delay), fmt(play), fmt(rest)
    # The shown drift / ramp amounts are the shown target's, so they scale with it.
    shown_d, shown_r = int(round(num(slots, 30))), int(round(num(slots, 38)))
    if shown_d in PERCENT_TARGETS:
        new[33], new[34] = fmt(num(slots, 31) * 100), fmt(num(slots, 32) * 100)
    if shown_r in PERCENT_TARGETS:
        new[44] = fmt(num(slots, 39) * 100)
    # The per-target banks the plugin now keeps, seeded to what it did before.
    shared_punit, shared_tunit = num(slots, 34), num(slots, 40)
    vals = [NEW_MAGIC]
    vals += grow(ob["up"], 0, True) + grow(ob["down"], 0, True)
    vals += grow(ob["per"], 8) + grow(ob["shape"], 0) + [ob["last_t"]]
    vals += grow(ob["by"], 0, True) + grow(ob["dur"], 0) + grow(ob["delay"], 0) + [ob["last_sr"]]
    vals += grow(ob["dplay"], 0) + grow(ob["drest"], 0) + grow(ob["splay"], 0) + grow(ob["srest"], 0)
    for k in ("lmode", "len", "sshape", "pmode", "note", "pval", "fine", "funit"):
        vals += list(ob[k])
    vals += [ob["last_seg"]]
    vals += [0] * NEW_N                      # Drift amount unit: Target default
    vals += [0] * NEW_N                      # Ramp by unit: Target default
    vals += [shared_punit] * NEW_N           # Drift period unit, from the one it shared
    vals += [shared_tunit] * NEW_N           # Ramp time unit, likewise
    vals += [1] * NEW_N                      # Drift movement mode: On a clock, as it read them
    want = 1 + 4 * NEW_N + 1 + 3 * NEW_N + 1 + 4 * NEW_N + 8 * N_SEG + 1 + 5 * NEW_N
    if len(vals) != want:
        raise SystemExit("built %d floats, the plugin reads %d -- refusing" % (len(vals), want))
    return new, vals


def files():
    out = []
    for f in glob.glob("E:/reaper/**/*.RPP", recursive=True):
        f = f.replace("\\", "/")
        if "backups" in f:
            continue
        if re.search(r"<JS\s+glasswings/sweep-dwell-filter\.jsfx", open(f, encoding="utf-8", errors="replace").read()):
            out.append(f)
    return sorted(out)


def convert_file(path):
    text = open(path, "rb").read().decode("utf-8", "replace")
    lines = text.splitlines(keepends=True)
    n_before, count = len(lines), 0
    for i in reversed([i for i, l in enumerate(lines)
                       if re.search(r"<JS\s+glasswings/sweep-dwell-filter\.jsfx", l)]):
        vi = i + 1
        span = blob_span(lines, i + 2)
        if span is None:
            raise SystemExit("%s copy at line %d has no blob -- refusing" % (path, i + 1))
        k, j, vals = span
        ob = read_old(vals)
        new, nvals = convert_instance(parse_line(lines[vi]), ob, path, vi)
        eol = "\r\n" if lines[vi].endswith("\r\n") else "\n"
        indent = lines[vi][:len(lines[vi]) - len(lines[vi].lstrip())]
        lines[vi] = indent + render_line(lines[vi].strip(), new, n_sliders=NEW_SLIDERS).strip() + eol
        b64 = base64.b64encode(struct.pack("<%df" % len(nvals), *nvals)).decode()
        bindent = lines[k + 1][:len(lines[k + 1]) - len(lines[k + 1].lstrip())]
        width = max(16, len(lines[k + 1].strip()))
        lines[k + 1:j] = [bindent + b64[q:q + width] + eol for q in range(0, len(b64), width)]
        count += 1
    return "".join(lines), count


def main():
    apply = "--apply" in sys.argv
    fs = files()
    if not fs:
        raise SystemExit("no project uses sweep-dwell-filter -- nothing to do")
    if apply and os.path.exists(SNAP):
        raise SystemExit("REFUSED: %s exists -- has this already run?" % SNAP)
    if apply:
        os.makedirs(SNAP)
    total = 0
    for f in fs:
        text, n = convert_file(f)
        total += n
        print("%s: %d copies" % (f, n))
        if apply:
            shutil.copy2(f, os.path.join(SNAP, f.replace(":", "").replace("/", "__")))
            data = text.encode("utf-8")
            open(f, "wb").write(data)
            if open(f, "rb").read() != data:
                raise SystemExit("WRITE MISMATCH %s -- restore from %s" % (f, SNAP))
    print("%d files, %d copies%s" % (len(fs), total, "" if apply else " (dry run; --apply writes)"))


if __name__ == "__main__":
    main()
