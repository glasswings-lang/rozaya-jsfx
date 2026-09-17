#!/usr/bin/env python3
"""Womb's mechanical half, 2026-09-17: 88 controls -> 103, and every saved blob normalised to
2700049.

Authored from docs/layouts/womb-mechanical-half-20260917.md.

What changes in a saved copy, and why it sounds the same:
  * R9. The five volumes become dB (-60 is off), so a saved 0..1 gain becomes 20*log10(gain) and
    a drift or ramp amount aimed at one becomes the dB step that amount used to make at that
    control's own value. Everything else that counted in fractions becomes a percent, x100, and
    so do its amounts.
  * Three frequencies gained a pitch block, so each keeps its Hz in the block's value with the
    block on Hz -- exactly what the old single control held.
  * Start delay gains a Transport unit, set to Beats, which is what it counted.
  * The new per-target banks are seeded to what the plugin did: the one shared period unit and
    ramp time unit go to every target, and the amount units to `Target default`.

The blob: six formats exist in the library (2600049, 2400011, 2100010 and an UNVERSIONED one the
plugin never read, which is why those copies load with drift and ramp at defaults today). Each is
read the way the plugin reads it, remapped to the 49 targets, and written out as 2700049.

    python tools/womb_migrate_mechanical_20260917.py            # dry run
    python tools/womb_migrate_mechanical_20260917.py --apply
"""
import base64
import glob
import math
import os
import re
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

FX = "womb_sound_generator_v3"
SNAP = "E:/reaper/finished/backups/snapshots/womb-mechanical-20260917"
NEW_MAGIC, N, NEW_SLIDERS = 2700049, 49, 103

# --- AUTHORED: old slider -> new slider (the layout doc's table) ---
MOVE = {n: n for n in range(1, 45)}
MOVE.update({45: 47, 46: 52, 47: 55, 48: 56, 49: 57, 50: 58, 51: 59, 52: 60, 53: 61, 54: 62,
             55: 63, 56: 64, 57: 65, 58: 68, 59: 71, 60: 72, 61: 73, 62: 74, 63: 75, 64: 76,
             65: 78, 66: 79, 67: 80, 68: 81, 69: 82, 70: 83, 71: 84,
             72: 85, 73: 86, 74: 87, 75: 89, 76: 90, 77: 91, 78: 92, 79: 93, 80: 94,
             81: 95, 82: 96, 83: 99, 84: 98, 85: 100, 86: 101, 87: 102, 88: 103})
# R9: old slider -> new slider, and how the value converts.
VOL_DB = {12: 12, 19: 19, 22: 22, 51: 59, 61: 73}        # 0..1 gain -> dB
PERCENT = {20: 20, 40: 40, 41: 41, 42: 42, 43: 43, 50: 58, 55: 63, 56: 64, 57: 65, 59: 71, 60: 72}
# The targets those controls are, for the drift and ramp banks.
VOL_TARGETS = {6: 12, 10: 19, 13: 22, 33: 51, 41: 61}    # target -> the OLD slider it reads
PCT_TARGETS = (11, 23, 24, 25, 26, 32, 35, 36, 37, 39, 40)
# New controls that are not carried from anything: the three pitch blocks (mode, name, fine,
# fine unit), the Transport unit, and the two amount units.
NEW_DEFAULTS = {45: "0", 46: "31", 48: "0", 49: "2", 50: "0", 51: "71", 53: "0", 54: "2",
                66: "0", 67: "59", 69: "0", 70: "2", 77: "1", 88: "0", 97: "0"}
DEF = {12: 1.0, 19: 0.7, 20: 0.3, 22: 1.0, 40: 0.3, 41: 0.2, 42: 0.2, 43: 0.3, 45: 80, 46: 500,
       50: 0.5, 51: 0.5, 55: 0.15, 56: 0.85, 57: 0.1, 58: 250, 59: 0.2, 60: 0.5, 61: 0.7,
       63: 440, 65: 0, 76: 0, 83: 2}
# The old ten/eleven targets -> the forty-nine, as the plugin's wb_o2n does it.
O2N = {0: 0, 1: 2, 2: 15, 3: 16, 4: 17, 5: 18, 6: 1, 7: 14, 8: 19, 9: 21, 10: 34}


def num(slots, i):
    t = slots.get(i)
    return float(DEF.get(i, 0)) if t in (None, "-") else float(t)


def fmt(v):
    return "%.10g" % v


def to_db(gain):
    """A 0..1 gain as dB, with silence landing on the control's own -60 rather than -inf."""
    return -60.0 if gain <= 0.001 else max(-60.0, min(24.0, 20 * math.log10(gain)))


def amt_db(amount, base):
    """A drift/ramp amount that used to ADD to a 0..1 gain, as the dB step it made at `base`."""
    if amount == 0:
        return 0.0
    b = max(base, 0.0001)
    return max(-60.0, min(24.0, 20 * math.log10(max(b + amount, 0.0001) / b)))


def blob_span(lines, i):
    k = next((k for k in range(i, i + 5) if lines[k].strip().startswith("<JS_SER")), None)
    if k is None:
        return None
    j, b64 = k + 1, ""
    while lines[j].strip() != ">":
        b64 += lines[j].strip()
        j += 1
    raw = base64.b64decode(b64)
    return k, j, list(struct.unpack("<%df" % (len(raw) // 4), raw))


BANKS = ("up", "down", "per", "shape", "by", "dur", "delay", "dplay", "drest", "rplay", "rrest", "moves")
DEFAULTS = {"up": 0, "down": 0, "per": 8, "shape": 0, "by": 0, "dur": 0, "delay": 0,
            "dplay": 0, "drest": 0, "rplay": 0, "rrest": 0, "moves": 0}


def read_blob(vals):
    """Every format the plugin reads, in its own width, remapped onto the 49 targets."""
    magic = int(round(vals[0]))
    out = {k: [DEFAULTS[k]] * N for k in BANKS}
    out["last_t"] = out["last_sr"] = 0
    if magic not in (2600049, 2500011, 2400011, 2300010, 2200010, 2100010):
        return out, magic            # unversioned: the plugin ignores it, so this does too
    w = N if magic == 2600049 else 11 if magic >= 2400000 else 10
    p = [1]

    def take(n):
        r = vals[p[0]:p[0] + n]
        p[0] += n
        return r

    raw = {}
    for k in ("up", "down", "per", "shape"):
        raw[k] = take(w)
    last_t = take(1)[0]
    for k in ("by", "dur", "delay"):
        raw[k] = take(w)
    last_sr = take(1)[0]
    if magic == 2300010:
        take(2 + 1)                  # the retired host-sync bank and its selector
    if magic >= 2400000:
        for k in ("dplay", "drest", "rplay", "rrest"):
            raw[k] = take(w)
    if magic >= 2500000:
        raw["moves"] = take(w)
    for k, v in raw.items():
        if w == N:
            out[k] = list(v)
        else:
            out[k] = [DEFAULTS[k]] * N
            for o in range(w):
                out[k][O2N[o]] = v[o]
    out["last_t"] = O2N.get(int(round(last_t)), int(round(last_t))) if w != N else int(round(last_t))
    out["last_sr"] = O2N.get(int(round(last_sr)), int(round(last_sr))) if w != N else int(round(last_sr))
    return out, magic


def seed_from_line(ob, slots):
    """A copy whose blob the plugin never read (unversioned, or none at all).

    What the old build does with one, measured on deep-night and to-sleep-within rather than
    assumed: the blob is skipped entirely, so the banks start empty and the FIRST @slider pass
    sees the saved selector as a switch away from target 0. It saves the visible values into
    target 0's slot and loads the selected target's -- which is empty. So a copy showing target 0
    keeps its saved drift or ramp, and a copy showing any other target has already lost it, every
    time it has ever loaded. This carries across exactly that, per selector."""
    d = int(round(num(slots, 72)))
    r = int(round(num(slots, 81)))
    if d == 0:
        ob["up"][0], ob["down"][0] = num(slots, 73), num(slots, 74)
        ob["per"][0], ob["shape"][0] = num(slots, 75), num(slots, 78)
        ob["dplay"][0], ob["drest"][0] = num(slots, 79), num(slots, 80)
        ob["moves"][0] = num(slots, 77)
    if r == 0:
        ob["by"][0], ob["dur"][0], ob["delay"][0] = num(slots, 82), num(slots, 84), num(slots, 88)
        ob["rplay"][0], ob["rrest"][0] = num(slots, 85), num(slots, 86)
    ob["last_t"], ob["last_sr"] = d, r
    return ob


def convert_instance(slots, ob, path, vi):
    real = {k: t for k, t in slots.items() if t not in (None, "-")}
    if real and max(real) > 88:
        raise SystemExit("%s line %d: a value above slider 88 -- refusing" % (path, vi + 1))
    new = {}
    for o, t in real.items():
        if o in MOVE and o not in VOL_DB and o not in PERCENT:
            new[MOVE[o]] = t
    for o, n in VOL_DB.items():
        new[n] = fmt(to_db(num(slots, o)))
    for o, n in PERCENT.items():
        new[n] = fmt(num(slots, o) * 100)
    for k, v in NEW_DEFAULTS.items():
        new[k] = v
    # The shown drift and ramp amounts belong to the shown target, so they convert with it.
    shown_d, shown_r = int(round(num(slots, 72))), int(round(num(slots, 81)))
    for tgt, sl, ids in ((shown_d, (73, 74), (86, 87)), (shown_r, (82,), (96,))):
        for o, nid in zip(sl, ids):
            v = num(slots, o)
            if tgt in VOL_TARGETS:
                new[nid] = fmt(amt_db(v, num(slots, VOL_TARGETS[tgt])))
            elif tgt in PCT_TARGETS:
                new[nid] = fmt(v * 100)
    # The banks convert the same way, per target.
    for k in ("up", "down", "by"):
        for tgt in range(N):
            if tgt in VOL_TARGETS:
                ob[k][tgt] = amt_db(ob[k][tgt], num(slots, VOL_TARGETS[tgt]))
            elif tgt in PCT_TARGETS:
                ob[k][tgt] = ob[k][tgt] * 100
    vals = [NEW_MAGIC]
    for k in ("up", "down", "per", "shape"):
        vals += ob[k]
    vals += [ob["last_t"]]
    for k in ("by", "dur", "delay"):
        vals += ob[k]
    vals += [ob["last_sr"]]
    for k in ("dplay", "drest", "rplay", "rrest"):
        vals += ob[k]
    vals += ob["moves"]
    vals += [0] * N          # Drift amount unit: Target default
    vals += [0] * N          # Ramp by unit
    vals += [num(slots, 76)] * N     # Drift period unit, from the one they shared
    vals += [num(slots, 83)] * N     # Ramp time unit, likewise
    want = 1 + 4 * N + 1 + 3 * N + 1 + 5 * N + 4 * N
    if len(vals) != want:
        raise SystemExit("built %d floats, the plugin reads %d -- refusing" % (len(vals), want))
    return new, vals


def files():
    out = []
    for f in glob.glob("E:/reaper/**/*.[rR][pP][pP]", recursive=True):
        f = f.replace(os.sep, "/")
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
        slots = parse_line(lines[vi])
        if span is None:
            k = j = None
            ob, magic = read_blob([0])
        else:
            k, j, vals = span
            ob, magic = read_blob(vals)
        if magic not in (2600049, 2500011, 2400011, 2300010, 2200010, 2100010):
            ob = seed_from_line(ob, slots)
        new, nvals = convert_instance(slots, ob, path, vi)
        eol = "\r\n" if lines[vi].endswith("\r\n") else "\n"
        indent = lines[vi][:len(lines[vi]) - len(lines[vi].lstrip())]
        lines[vi] = indent + render_line(lines[vi].strip(), new, n_sliders=NEW_SLIDERS).strip() + eol
        b64 = base64.b64encode(struct.pack("<%df" % len(nvals), *nvals)).decode()
        if k is None:
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
