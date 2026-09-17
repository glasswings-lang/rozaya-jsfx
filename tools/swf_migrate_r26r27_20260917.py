#!/usr/bin/env python3
"""The Sweeping Filter's 2026-09-17 turn: 54 controls -> 62, and blob 2300017 -> 2400019.

Authored from docs/layouts/sweeping-filter-r26r27-20260917.md; every table here is written from
that layout, never inferred from the projects.

What changes in a saved copy, and why it still sounds the same:
  * Resonance, Pan spread and Wet/dry mix become percents, so they and any drift or ramp amount
    aimed at them are multiplied by 100.
  * The three `(Flipped)` pan choices become their partner plus `Pan direction` Flipped.
  * `Ramp time unit` moves under `Ramp duration` (Rozaya: "That sounds right yeah"), which swaps
    two slider positions; both values are carried to their new places.
  * Start delay counted in the Rate mode's units and Play for / Rest for counted LFO cycles. They
    share one `Transport unit` now: see transport_unit() for the three cases.
  * The new per-target banks are seeded so the plugin does what it did: the one shared period unit
    and ramp time unit go to every target, the amount units to `Target default` (what an amount
    meant), and `Drift movement mode` to `On a clock`, the live reading it has always used.

    python tools/swf_migrate_r26r27_20260917.py            # dry run
    python tools/swf_migrate_r26r27_20260917.py --apply
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

FX = "full-feature-sweeping-filter"
SNAP = "E:/reaper/finished/backups/snapshots/sweeping-filter-r26r27-20260917"
OLD_MAGIC, NEW_MAGIC = 2300017, 2400019
OLD_N, NEW_N, NEW_SLIDERS = 17, 19, 62

# --- AUTHORED: old slider -> new slider, where the value carries across unchanged ---
MOVE = {n: n for n in range(1, 27)}
MOVE.update({28: 29, 29: 30, 30: 31, 31: 32, 32: 34, 34: 37, 35: 38, 36: 39, 37: 40, 38: 41,
             39: 42, 40: 43, 41: 44, 42: 46, 43: 47, 44: 49, 45: 50, 46: 51, 47: 53, 48: 54,
             49: 57, 50: 56, 51: 58, 52: 59, 53: 61, 54: 62})
del MOVE[12]                                  # Resonance is a percent now
del MOVE[26]                                  # Pan mode is remapped, and gains Pan direction
PERCENT = {12: 12, 27: 28, 33: 35}            # old -> new, value x100
PAN = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (6, 0), 4: (6, 1), 5: (7, 0), 6: (8, 0), 7: (9, 0),
       8: (10, 0), 9: (11, 0), 10: (14, 0), 11: (14, 1), 12: (12, 0), 13: (2, 0), 14: (3, 0),
       15: (4, 0)}
PERCENT_TARGETS = (5, 12, 16)                 # Resonance, Pan spread, Wet/dry mix
NEW_DEFAULTS = {27: "0", 33: "0", 45: "0", 48: "1", 52: "0", 55: "0", 60: "0"}
DEF = {1: 0, 3: 500, 6: 0, 8: 5000, 11: 440, 12: 0.7, 14: 2, 15: 0, 17: 50, 18: 100,
       26: 0, 27: 1, 32: 1, 33: 1, 34: 0, 35: 0, 36: 0, 39: 0, 43: 0, 47: 0, 49: 2}


def num(slots, i):
    t = slots.get(i)
    return float(DEF.get(i, 0)) if t in (None, "-") else float(t)


def fmt(v):
    return "%.10g" % v


def rate_secs(mode, v, bpm=120.0):
    """One LFO cycle in seconds, exactly as the plugin reads the rate pair."""
    mode = int(mode)
    if mode == 1:
        return v
    if mode == 0:
        return 60 / max(v, 0.001)
    if mode == 2:
        return 1 / max(v, 0.001)
    if mode == 3:
        return v * 60 / bpm
    return 60 / bpm / max(v, 0.001)


def transport_unit(delay, rate_mode, rate_val, play, rest, bpm=120.0):
    """One Transport unit over Start delay, Play for and Rest for.

    Start delay counted in the RATE's units (seconds in Seconds mode, LFO cycles otherwise) and
    Play/Rest counted cycles, so:
      no delay                 -> Cycles, every number untouched
      a delay, no play/rest    -> Seconds if the rate was in Seconds (the delay was literal
                                  seconds), else Cycles, where the delay already counted cycles
      both                     -> the same unit, with the delay converted into it when it was
                                  seconds and the cycle length is known
    """
    cyc = rate_secs(rate_mode, rate_val, bpm)
    if delay <= 0:
        return 0, 0.0, play, rest
    if int(rate_mode) == 1:                  # the delay was in seconds
        if play <= 0 and rest <= 0:
            return 1, delay, play, rest
        return 1, delay, play * cyc, rest * cyc
    return 0, delay, play, rest              # it counted cycles, and so do play/rest


def blob_span(lines, i):
    k = next((k for k in range(i, i + 4) if lines[k].strip().startswith("<JS_SER")), None)
    if k is None:
        return None
    j, b64 = k + 1, ""
    while lines[j].strip() != ">":
        b64 += lines[j].strip()
        j += 1
    return k, j, list(struct.unpack("<%df" % (len(base64.b64decode(b64)) // 4), base64.b64decode(b64)))


# Blobs from before 2026-09-10 hold SIX targets in the old order; the plugin read them and
# remapped, so this does the same rather than dropping a saved drift on the floor.
# {Sweep Rate, Frequency Low, Frequency High, Pan Sweep Rate, Resonance, Wet/Dry} ->
OLD6 = {0: 6, 1: 0, 2: 2, 3: 14, 4: 5, 5: 16}


def remap6(bank6, default):
    out = [default] * OLD_N
    for o, n in OLD6.items():
        out[n] = bank6[o]
    return out


def read_old(vals, path):
    """The saved blob, in the order the installed plugin's @serialize reads it: 2300017, or one of
    the two six-target formats it still accepted (2100006 without play/rest, 2200006 with)."""
    m = int(round(vals[0]))
    if m not in (OLD_MAGIC, 2100006, 2200006):
        raise SystemExit("%s: blob magic %d is not one the plugin reads -- refusing" % (path, m))
    p = [1]

    def take(n):
        r = vals[p[0]:p[0] + n]
        p[0] += n
        return r

    n = OLD_N if m == OLD_MAGIC else 6
    o = {}
    for k in ("up", "down", "per", "shape"):
        o[k] = take(n)
    o["last_t"] = take(1)[0]
    for k in ("by", "dur", "delay"):
        o[k] = take(n)
    if m == 2100006:                      # play/rest did not exist yet: both gates off
        for k in ("dplay", "drest", "splay", "srest"):
            o[k] = [0] * n
    else:
        for k in ("dplay", "drest", "splay", "srest"):
            o[k] = take(n)
    o["last_sr"] = take(1)[0]
    if p[0] != len(vals):
        raise SystemExit("%s: blob holds %d floats, decoded %d -- refusing" % (path, len(vals), p[0]))
    if n == 6:                            # the six old targets, moved to their places in the 17
        for k, dflt in (("up", 0), ("down", 0), ("per", 8), ("shape", 0), ("by", 0), ("dur", 0),
                        ("delay", 0), ("dplay", 0), ("drest", 0), ("splay", 0), ("srest", 0)):
            o[k] = remap6(o[k], dflt)
        o["last_t"] = OLD6.get(int(round(o["last_t"])), 0)
        o["last_sr"] = OLD6.get(int(round(o["last_sr"])), 0)
    return o


def grow(bank, default, scale_percent=False):
    out = list(bank) + [default, default]
    if scale_percent:
        out = [v * 100 if i in PERCENT_TARGETS else v for i, v in enumerate(out)]
    return out


def convert_instance(slots, ob, path, vi):
    real = {k: t for k, t in slots.items() if t not in (None, "-")}
    if real and max(real) > 54:
        raise SystemExit("%s line %d: a value above slider 54 -- refusing" % (path, vi + 1))
    new = {}
    for o, t in real.items():
        if o in MOVE:
            new[MOVE[o]] = t
    for o, n in PERCENT.items():
        new[n] = fmt(num(slots, o) * 100)
    mode, flip = PAN[int(round(num(slots, 26)))]
    new[26], new[27] = str(mode), str(flip)
    for k, v in NEW_DEFAULTS.items():
        new[k] = v
    unit, delay, play, rest = transport_unit(num(slots, 34), num(slots, 15), num(slots, 14),
                                             num(slots, 35), num(slots, 36))
    new[36], new[37], new[38], new[39] = str(unit), fmt(delay), fmt(play), fmt(rest)
    shown_d, shown_r = int(round(num(slots, 39))), int(round(num(slots, 47)))
    if shown_d in PERCENT_TARGETS:
        new[43], new[44] = fmt(num(slots, 40) * 100), fmt(num(slots, 41) * 100)
    if shown_r in PERCENT_TARGETS:
        new[54] = fmt(num(slots, 48) * 100)
    shared_punit, shared_tunit = num(slots, 43), num(slots, 49)
    vals = [NEW_MAGIC]
    vals += grow(ob["up"], 0, True) + grow(ob["down"], 0, True)
    vals += grow(ob["per"], 8) + grow(ob["shape"], 0) + [ob["last_t"]]
    vals += grow(ob["by"], 0, True) + grow(ob["dur"], 0) + grow(ob["delay"], 0)
    vals += grow(ob["dplay"], 0) + grow(ob["drest"], 0) + grow(ob["splay"], 0) + grow(ob["srest"], 0)
    vals += [ob["last_sr"]]
    vals += [0] * NEW_N                      # Drift amount unit: Target default
    vals += [0] * NEW_N                      # Ramp by unit: Target default
    vals += [shared_punit] * NEW_N           # Drift period unit, from the one they shared
    vals += [shared_tunit] * NEW_N           # Ramp time unit, likewise
    vals += [1] * NEW_N                      # Drift movement mode: On a clock, as it read them
    want = 1 + 4 * NEW_N + 1 + 7 * NEW_N + 1 + 5 * NEW_N
    if len(vals) != want:
        raise SystemExit("built %d floats, the plugin reads %d -- refusing" % (len(vals), want))
    return new, vals


def files():
    out = []
    for f in glob.glob("E:/reaper/**/*.RPP", recursive=True):
        f = f.replace("\\", "/")
        if "backups" in f:
            continue
        if re.search(r"<JS\s+glasswings/%s\.jsfx" % FX, open(f, encoding="utf-8", errors="replace").read()):
            out.append(f)
    return sorted(out)


def convert_file(path):
    lines = open(path, "rb").read().decode("utf-8", "replace").splitlines(keepends=True)
    count = 0
    for i in reversed([i for i, l in enumerate(lines) if re.search(r"<JS\s+glasswings/%s\.jsfx" % FX, l)]):
        vi = i + 1
        span = blob_span(lines, i + 2)
        if span is None:
            # A copy that was never saved with state of its own: the plugin runs on @init's
            # defaults, so the new blob is written from those.
            k = j = None
            ob = {k2: [d] * OLD_N for k2, d in (("up", 0), ("down", 0), ("per", 8), ("shape", 0),
                                                ("by", 0), ("dur", 0), ("delay", 0), ("dplay", 0),
                                                ("drest", 0), ("splay", 0), ("srest", 0))}
            ob["last_t"] = ob["last_sr"] = 0
        else:
            k, j, vals = span
            ob = read_old(vals, path)
        new, nvals = convert_instance(parse_line(lines[vi]), ob, path, vi)
        eol = "\r\n" if lines[vi].endswith("\r\n") else "\n"
        indent = lines[vi][:len(lines[vi]) - len(lines[vi].lstrip())]
        lines[vi] = indent + render_line(lines[vi].strip(), new, n_sliders=NEW_SLIDERS).strip() + eol
        b64 = base64.b64encode(struct.pack("<%df" % len(nvals), *nvals)).decode()
        if k is None:
            # No blob to replace: write one, in the <JS_SER block REAPER expects after the line.
            lines[vi + 1:vi + 1] = ([indent + "<JS_SER" + eol]
                                    + [indent + "  " + b64[q:q + 128] + eol for q in range(0, len(b64), 128)]
                                    + [indent + ">" + eol])
        else:
            bindent = lines[k + 1][:len(lines[k + 1]) - len(lines[k + 1].lstrip())]
            width = max(16, len(lines[k + 1].strip()))
            lines[k + 1:j] = [bindent + b64[q:q + width] + eol for q in range(0, len(b64), width)]
        count += 1
    return "".join(lines), count


def main():
    apply = "--apply" in sys.argv
    fs = files()
    if not fs:
        raise SystemExit("no project uses %s -- nothing to do" % FX)
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
