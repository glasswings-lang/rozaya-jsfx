#!/usr/bin/env python3
"""The Sweep Dwell segment migration, proven on what surges.RPP does not use.

surges has no drift, no ramp and no host sync, so its bit-identical render says
nothing about those branches of the migration. This builds synthetic OLD
projects that do use them -- surges' snapshot with its Sweep Dwell line and blob
replaced -- migrates each with the real convert(), and renders the installed
(46-control) build on the synthetic project against the new src on its
migration.

Drift and ramp cases must be bit-identical AND differ from the same project with
nothing set. The two host-sync cases convert the old "Host x" cycle into beat
lengths; there the fade fractions are recomputed from beat lengths instead of raw
slider values, so rounding in the last bits is expected -- they report the
largest sample gap and pass under 1e-4.

    python tools/sdf_migrate_test.py
"""
import base64, os, struct, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sdf_migrate_segments_20260910 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
NEW = os.path.join(ROOT, "src", "sweep-dwell-filter.jsfx")
OLD = os.path.join(os.environ["APPDATA"], "REAPER", "Effects", "glasswings", "sweep-dwell-filter.jsfx")
BASE = os.path.join(mig.SNAP, "to-play-with-later__surges.RPP")
FX = "sweep-dwell-filter"

def line46(v):
    d = {1: 300, 2: 3000, 3: 2, 4: 3, 5: 1, 6: 1, 7: 1.5, 8: 2, 9: 0.5, 10: 0.8, 11: 0,
         12: 0, 13: 1, 14: 10, 15: 1, 16: 5, 17: 8, 18: 20, 19: 0, 20: 1, 21: 0,
         22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 1, 29: 0, 30: 0, 31: 0, 32: 0,
         33: 0, 34: 0, 35: 0, 36: 0, 37: 1, 38: 1, 39: 0, 40: 0, 41: 0, 42: 0, 43: 12,
         44: 0, 45: 0, 46: 0}
    d.update(v)
    return " ".join(("%g" % d[i]) if i in d else "-" for i in range(1, 65))

def blob46(magic, cfg, last_t, last_sr):
    g = lambda k, t: cfg.get(t, {}).get(k, 0)
    vals = [magic] + [g("by", t) for t in range(6)] + [g("dur", t) for t in range(6)] \
         + [0] * 6 + [last_sr]
    if magic == 2300006:
        vals += [0] * 24
    vals += [g("up", t) for t in range(6)] + [g("down", t) for t in range(6)] \
          + [1] * 6 + [t % 2 for t in range(6)] + [last_t]
    return base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode()

def synth(path, sliders, magic, cfg, last_t, last_sr):
    L = open(BASE, encoding="utf-8", newline="").read().split("\n")
    i = next(i for i, l in enumerate(L) if "<JS " in l and FX in l)
    ind = L[i + 1][: len(L[i + 1]) - len(L[i + 1].lstrip())]
    cr = "\r" if L[i + 1].endswith("\r") else ""
    s = dict(sliders)
    s.update({34: last_t, 26: last_sr})
    L[i + 1] = ind + line46(s) + cr
    k = next(k for k in range(i + 2, i + 6) if "<JS_SER" in L[k])
    j = k + 1
    while L[j].strip() != ">":
        j += 1
    L[k + 1:j] = [ind + "  " + blob46(magic, cfg, last_t, last_sr) + cr]
    open(path, "w", encoding="utf-8", newline="").write("\n".join(L))

CASES = [  # name, sliders, magic, cfg, drift target, ramp target, exact?
    ("high dwell length drift, 2200006", {}, 2200006, {0: {"up": 1, "down": 0.5}}, 0, 0, True),
    ("low dwell length ramp", {32: 1}, 2300006, {2: {"by": 3, "dur": 0.05}}, 0, 2, True),
    ("fade up length drift", {}, 2300006, {3: {"up": 1, "down": 1}}, 3, 0, True),
    ("pan sweep rate drift (old 4)", {}, 2200006, {4: {"up": 15, "down": 15}}, 4, 0, True),
    ("resonance drift (old 5)", {}, 2300006, {5: {"up": 0.4, "down": 0.4}}, 5, 0, True),
    ("resonance ramp (old 5)", {32: 1}, 2200006, {5: {"by": 0.45, "dur": 0.05}}, 0, 5, True),
    ("linked sweep every 0.5 cycles", {14: 12, 20: 2}, 2300006, {}, 0, 0, True),
    ("host x, fit to durations", {42: 1, 44: 0}, 2300006, {}, 0, 0, False),
    ("host x, set in beats (6)", {42: 1, 44: 1, 43: 6}, 2300006, {}, 0, 0, False),
]

def render(plugin, proj, out):
    subprocess.run([EXE, plugin, "--rpp", proj, "--fx", FX, "--input", "noise",
                    "--seconds", "20", "--csv", out, "--quiet"], check=True, capture_output=True)
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))

def main():
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        o, n, c = (os.path.join(tmp, x) for x in ("old.RPP", "new.RPP", "base.RPP"))
        for name, sl, magic, cfg, lt, lsr, exact in CASES:
            synth(o, sl, magic, cfg, lt, lsr)
            text, count = mig.convert(o)
            open(n, "w", encoding="utf-8", newline="").write(text)
            a = render(OLD, o, os.path.join(tmp, "a.csv"))
            b = render(NEW, n, os.path.join(tmp, "b.csv"))
            synth(c, {}, magic, {}, 0, 0)
            base = render(OLD, c, os.path.join(tmp, "c.csv"))
            gap = float(np.abs(a - b).max())
            matters = not np.array_equal(a, base)
            ok = matters and (np.array_equal(a, b) if exact else gap < 1e-4)
            fails += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name:34} "
                  f"{'bit-identical' if np.array_equal(a, b) else 'largest gap %.2e' % gap}; "
                  f"the setting audibly matters: {matters}", flush=True)
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
