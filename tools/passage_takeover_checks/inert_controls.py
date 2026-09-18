#!/usr/bin/env python3
"""Which of Passage's controls actually do something, in a given setup, measured.

Rozaya, 2026-09-17, after a gap typed on All slots was silent: *"there's more stuff in here that
feels like it should apply but doesn't, or at least, isn't labled like it doesn't apply."* This
answers that by moving each control in turn and listening, rather than by reading the source.

Each control is nudged from what the project saved, twice: once with the copy as it stands, and
once with Auto-morph timing mode on Slot timings and Slot crossfade into next Off. A control that
changes nothing in either is inert in this project, and the pair says whether the walk is why.

    python tools/passage_takeover_checks/inert_controls.py [--rpp PROJECT] [--instance N]
"""
import ctypes
import math
import os
import re
import subprocess
import sys

ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
# The grain phases are scrambled per load, so two renders of the SAME settings never match. Pin
# that first, or every control looks like it did something (measured the hard way, 2026-09-17).
_src = open(os.path.join(ROOT, "src", "spectral_vowel_passage.jsfx"), encoding="utf-8", newline="").read()
assert _src.count("_tp = time_precise();") == 1
_dir = os.path.join(os.environ.get("TEMP", "."), "passage_inert_pin")
os.makedirs(_dir, exist_ok=True)
PLUG = os.path.join(_dir, "spectral_vowel_passage.jsfx")
open(PLUG, "w", encoding="utf-8", newline="").write(_src.replace("_tp = time_precise();", "_tp = 0.25;"))
RPP = sys.argv[sys.argv.index("--rpp") + 1] if "--rpp" in sys.argv else "E:/reaper/finished/held.RPP"
INST = sys.argv[sys.argv.index("--instance") + 1] if "--instance" in sys.argv else "1"
CSV = os.path.join(os.environ.get("TEMP", "."), "passage_inert.csv")
SECS = 8
# Selectors and one-shots: moving these changes what is SHOWN or captures afresh, so they are not
# what this is asking about.
SKIP = {1, 2, 50, 68, 80}


def decls():
    src = _src
    out = {}
    for m in re.finditer(r"^slider(\d+):([-\d.]+)<([^>]*)>(.*)$", src, re.M):
        n = int(m.group(1))
        rng = m.group(3).split("{")[0].split(",")
        out[n] = (float(m.group(2)), float(rng[0]), float(rng[1]), m.group(4).strip())
    return out


def render(stages):
    if os.path.exists(CSV):
        os.remove(CSV)
    a = [EXE, PLUG, "--rpp", RPP, "--fx", "spectral_vowel_passage", "--instance", INST,
         "--seconds", str(SECS), "--quiet", "--csv", CSV]
    for st in stages:
        a.append("--stage")
        for s in st:
            a += ["--set-after", s]
    subprocess.run(a, capture_output=True)
    return np.loadtxt(CSV, delimiter=",", skiprows=1)[:, 2:] if os.path.exists(CSV) else None


def differ(a, b):
    if a is None or b is None:
        return 99
    m = min(len(a), len(b))
    return 20 * math.log10(math.sqrt(((a[:m] - b[:m]) ** 2).mean())
                           / max(math.sqrt((a[:m] ** 2).mean()), 1e-12) + 1e-30)


def main():
    D = decls()
    # the two setups: the copy as it stands, and the per-slot walk with the crossfade off
    SETUPS = (("as the project sits", []), ("Slot timings, crossfade Off", ["8=0", "18=0"]))
    base = {}
    for name, pre in SETUPS:
        base[name] = render([pre] if pre else [])
    rows = []
    for n in sorted(D):
        if n in SKIP:
            continue
        dflt, lo, hi, label = D[n]
        moved = {}
        for name, pre in SETUPS:
            v = dflt + (hi - dflt) * 0.6 if hi > dflt else dflt - (dflt - lo) * 0.6
            if abs(v - dflt) < 1e-9:
                v = hi if hi != dflt else lo
            stages = ([pre] if pre else []) + [["1=0"], ["%d=%g" % (n, v)]]
            moved[name] = differ(base[name], render(stages))
        rows.append((n, label, moved))
        flags = " ".join("%s %+.0f dB" % (k.split(",")[0], v) for k, v in moved.items())
        print("slider%-3d %-52s %s" % (n, label[:52], flags), flush=True)
    print()
    dead = [r for r in rows if all(v < -60 for v in r[2].values())]
    walk = [r for r in rows if r[2]["as the project sits"] < -60 > -1e9
            and r[2]["Slot timings, crossfade Off"] >= -60]
    print("DOES NOTHING EITHER WAY (%d):" % len(dead))
    for n, label, _ in dead:
        print("   slider%-3d %s" % (n, label))
    print("DOES NOTHING ON THE CONTINUOUS WALK, BUT WORKS ON SLOT TIMINGS (%d):" % len(walk))
    for n, label, _ in walk:
        print("   slider%-3d %s" % (n, label))


main()
