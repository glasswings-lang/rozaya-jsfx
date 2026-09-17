#!/usr/bin/env python3
"""What Sweep Dwell's new controls DO, measured from the rendered samples.

A control that saves and reloads but changes nothing is the failure this catches.

    python tools/sweep_dwell_checks/sound_checks.py [path/to/sweep-dwell-filter.jsfx]
"""
import ctypes
import math
import os
import subprocess
import sys

ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
PLUG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "src", "sweep-dwell-filter.jsfx")
WORK = os.environ.get("TEMP", ".")
CSV = os.path.join(WORK, "sdf_sound.csv")


def render(sets, secs=12.0, stages=None):
    if os.path.exists(CSV):
        os.remove(CSV)
    a = [EXE, PLUG, "--input", "noise", "--seconds", str(secs), "--quiet", "--csv", CSV]
    for s in sets:
        a += ["--set-after", s]
    for st in (stages or []):
        a.append("--stage")
        for s in st:
            a += ["--set-after", s]
    subprocess.run(a, capture_output=True)
    if not os.path.exists(CSV):
        return None
    return np.loadtxt(CSV, delimiter=",", skiprows=1)[:, 2:]


def balance(x):
    """Mean left-minus-right, as a share of the whole: -1 hard left, +1 hard right."""
    l = np.sqrt((x[:, 0] ** 2).reshape(-1, 4410).mean(axis=1))
    r = np.sqrt((x[:, 1] ** 2).reshape(-1, 4410).mean(axis=1))
    return (r - l) / np.maximum(l + r, 1e-9)


def db(x):
    return 20 * math.log10(math.sqrt((x ** 2).mean()) + 1e-12)


def differ(a, b):
    m = min(len(a), len(b))
    d = a[:m] - b[:m]
    return 20 * math.log10(math.sqrt((d ** 2).mean()) / max(math.sqrt((a[:m] ** 2).mean()), 1e-12) + 1e-30)


CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, ok, detail))
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def main():
    # --- every pan choice moves the sound somewhere, and none is silent ---
    names = ["Mono", "Alternating", "Alternating every 2", "Alternating every 4", "Alternating every 8",
             "Accent L / Weak R", "Distributed", "Distributed (Ping-pong)", "Converging",
             "Converging (Ping-pong)", "Diverging", "Diverging (Ping-pong)", "Linked Sweep", "Sway", "Pan Sweep"]
    swings = {}
    for m, nm in enumerate(names):
        x = render(["15=1", "16=%d" % m, "18=100", "19=0", "20=4", "21=1", "24=1", "23=1", "3=1"], secs=12)
        b = balance(x)
        swings[m] = b
        moved = b.max() - b.min()
        if m == 0:
            check("Mono stays centred", abs(b).max() < 0.05, "|balance| %.3f" % abs(b).max())
        else:
            check("%s moves between the sides" % nm, moved > 0.2 and db(x) > -60, "swing %.2f" % moved)
    # --- Pan direction mirrors any choice ---
    for m in (1, 6, 14):
        a = render(["15=1", "16=%d" % m, "17=0", "18=100", "19=0", "20=4", "21=1", "3=1"], secs=8)
        f = render(["15=1", "16=%d" % m, "17=1", "18=100", "19=0", "20=4", "21=1", "3=1"], secs=8)
        ba, bf = balance(a), balance(f)
        n = min(len(ba), len(bf))
        err = np.sort(np.abs(ba[:n] + bf[:n]))[int(n * 0.9)]   # the windows that straddle a switch are half each
        check("Pan direction mirrors %s" % names[m], err < 0.02, "%.3f from a perfect mirror" % err)
    # --- Sway is smooth where Pan Sweep jumps back ---
    sway = swings[13]
    sweep = swings[14]
    check("Sway turns around instead of jumping back",
          np.abs(np.diff(sway)).max() < np.abs(np.diff(sweep)).max() * 0.6,
          "biggest step: Sway %.2f, Pan Sweep %.2f" % (np.abs(np.diff(sway)).max(), np.abs(np.diff(sweep)).max()))
    # --- Pan sweep every: N per cycle is faster than Every N cycles ---
    slow = balance(render(["15=1", "16=12", "18=100", "19=0", "23=0", "24=4", "3=1"], secs=12))
    fast = balance(render(["15=1", "16=12", "18=100", "19=0", "23=1", "24=4", "3=1"], secs=12))
    zc = lambda b: int(np.sum(np.diff(np.sign(b)) != 0))
    check("Pan sweep every: N per cycle is the faster one", zc(fast) > zc(slow) * 3,
          "turns: every 4 cycles %d, 4 per cycle %d" % (zc(slow), zc(fast)))
    # --- a drift amount in semitones is not the same as one in Hz ---
    pre = ["1=1", "5=0", "7=2000"]
    base = [["32=4"], ["33=12", "34=12", "36=2", "37=1"]]
    dflt = render(pre, secs=10, stages=base + [["35=0"]])
    semi = render(pre, secs=10, stages=base + [["35=2"]])
    check("Drift amount unit changes what the amount means", differ(dflt, semi) > -40,
          "difference %.1f dB under the signal" % differ(dflt, semi))
    # --- movement mode: a length drift latched per cycle is not the live reading ---
    lenb = [["1=1", "2=1", "3=2", "32=0"], ["33=1", "34=1", "36=3", "37=1"]]
    with_t = render([], secs=14, stages=lenb + [["38=0"]])
    clock = render([], secs=14, stages=lenb + [["38=1"]])
    check("Drift movement mode changes when a length drift lands", differ(with_t, clock) > -40,
          "difference %.1f dB under the signal" % differ(with_t, clock))
    # --- Play for / Rest for in seconds, with Output at rest on Silence ---
    x = render(["26=1", "28=2", "29=2", "31=1", "3=1"], secs=12)
    sec = np.array([db(x[i:i + 22050]) for i in range(0, len(x) - 22049, 22050)])
    check("Play for / Rest for in Seconds gates the output", sec.max() - sec.min() > 40,
          "loudest %.0f dB, quietest %.0f dB" % (sec.max(), sec.min()))
    # --- the two rest switches ---
    g = [["26=1", "28=2", "29=2", "11=50", "32=9"], ["33=50", "34=50", "36=1", "37=1"]]
    walk = render([], secs=14, stages=g + [["42=0"]])
    freeze = render([], secs=14, stages=g + [["42=1"]])
    check("Drift rest mode changes the sound", differ(walk, freeze) > -40,
          "difference %.1f dB under the signal" % differ(walk, freeze))
    r = [["26=1", "28=2", "29=2", "11=50", "43=9"], ["44=50", "46=1", "47=4", "51=1"]]
    walk = render([], secs=14, stages=r + [["50=0"]])
    freeze = render([], secs=14, stages=r + [["50=1"]])
    check("Ramp rest mode changes the sound", differ(walk, freeze) > -40,
          "difference %.1f dB under the signal" % differ(walk, freeze))
    # --- Play for and Rest for as drift targets (R24) ---
    p = ["26=1", "28=2", "29=2", "31=1", "3=1"]
    still = render(p, secs=14)
    drifted = render(p, secs=14, stages=[["32=16"], ["33=1.5", "34=1.5", "36=4", "37=1"]])
    check("Play for is a drift target", differ(still, drifted) > -40,
          "difference %.1f dB under the signal" % differ(still, drifted))
    fails = sum(1 for _, ok, _ in CHECKS if not ok)
    print("%d sound checks, %d failed" % (len(CHECKS), fails))
    return fails


sys.exit(1 if main() else 0)
