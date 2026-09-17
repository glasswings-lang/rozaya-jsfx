#!/usr/bin/env python3
"""What the Sweeping Filter's new controls DO, measured from the rendered samples.

A control that saves and reloads but changes nothing is the failure this catches.

    python tools/sweeping_filter_checks/sound_checks.py [path/to/full-feature-sweeping-filter.jsfx]
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
PLUG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "src", "full-feature-sweeping-filter.jsfx")
CSV = os.path.join(os.environ.get("TEMP", "."), "swf_sound.csv")
# A one-second cycle throughout, so twelve seconds is twelve cycles. The MODE goes in its own
# stage: switching it converts the value, so mode and value in one step would overwrite the value.
RATE = []
RATE_STAGES = [["15=1"], ["14=1"]]


def render(sets, secs=12.0, stages=None):
    if os.path.exists(CSV):
        os.remove(CSV)
    a = [EXE, PLUG, "--input", "noise", "--seconds", str(secs), "--quiet", "--csv", CSV]
    sets = list(sets)
    for st in (RATE_STAGES + [sets] + (stages or [])):
        if not st:
            continue
        a.append("--stage")
        for s in st:
            a += ["--set-after", s]
    subprocess.run(a, capture_output=True)
    return np.loadtxt(CSV, delimiter=",", skiprows=1)[:, 2:] if os.path.exists(CSV) else None


def balance(x):
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
    CHECKS.append((name, ok))
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def main():
    names = ["Mono", "Alternating", "Alternating every 2", "Alternating every 4", "Alternating every 8",
             "Accent L / Weak R", "Distributed", "Distributed (Ping-pong)", "Converging",
             "Converging (Ping-pong)", "Diverging", "Diverging (Ping-pong)", "Linked Sweep", "Sway", "Pan Sweep"]
    swings = {}
    for m, nm in enumerate(names):
        x = render(RATE + ["25=1", "26=%d" % m, "28=100", "29=0", "30=4", "31=1", "32=1", "33=0", "34=1"])
        b = balance(x)
        swings[m] = b
        moved = b.max() - b.min()
        if m == 0:
            check("Mono stays centred", abs(b).max() < 0.05, "|balance| %.3f" % abs(b).max())
        else:
            check("%s moves between the sides" % nm, moved > 0.2 and db(x) > -60, "swing %.2f" % moved)
    for m in (1, 6, 14):
        a = render(RATE + ["25=1", "26=%d" % m, "27=0", "28=100", "29=0", "30=4", "31=1", "32=1"], secs=8)
        f = render(RATE + ["25=1", "26=%d" % m, "27=1", "28=100", "29=0", "30=4", "31=1", "32=1"], secs=8)
        ba, bf = balance(a), balance(f)
        n = min(len(ba), len(bf))
        err = np.sort(np.abs(ba[:n] + bf[:n]))[int(n * 0.9)]
        check("Pan direction mirrors %s" % names[m], err < 0.02, "%.3f from a perfect mirror" % err)
    sway, sweep = swings[13], swings[14]
    check("Sway turns around instead of jumping back",
          np.abs(np.diff(sway)).max() < np.abs(np.diff(sweep)).max() * 0.6,
          "biggest step: Sway %.2f, Pan Sweep %.2f" % (np.abs(np.diff(sway)).max(), np.abs(np.diff(sweep)).max()))
    zc = lambda b: int(np.sum(np.diff(np.sign(b)) != 0))
    slow = balance(render(RATE + ["25=1", "26=12", "28=100", "29=0", "33=0", "34=4"]))
    fast = balance(render(RATE + ["25=1", "26=12", "28=100", "29=0", "33=1", "34=4"]))
    check("Pan sweep every: N per cycle is the faster one", zc(fast) > zc(slow) * 3,
          "turns: every 4 cycles %d, 4 per cycle %d" % (zc(slow), zc(fast)))
    # --- a drift amount in semitones is not the same as one in Hz (High frequency, target 2) ---
    base = [["42=2"], ["43=12", "44=12", "46=2", "47=1"]]
    dflt = render(RATE, secs=10, stages=base + [["45=0"]])
    semi = render(RATE, secs=10, stages=base + [["45=2"]])
    check("Drift amount unit changes what the amount means", differ(dflt, semi) > -40,
          "difference %.1f dB under the signal" % differ(dflt, semi))
    # --- movement mode on On duration (target 7): latched per cycle, or read live ---
    lat = [["42=7"], ["43=30", "44=30", "46=3", "47=1"]]
    with_t = render(RATE, secs=14, stages=lat + [["48=0"]])
    clock = render(RATE, secs=14, stages=lat + [["48=1"]])
    check("Drift movement mode changes when an On duration drift lands", differ(with_t, clock) > -40,
          "difference %.1f dB under the signal" % differ(with_t, clock))
    # --- Play for / Rest for in seconds, with Output at rest on Silence ---
    x = render(RATE + ["36=1", "38=2", "39=2", "41=1"])
    sec = np.array([db(x[i:i + 22050]) for i in range(0, len(x) - 22049, 22050)])
    check("Play for / Rest for in Seconds gates the output", sec.max() - sec.min() > 40,
          "loudest %.0f dB, quietest %.0f dB" % (sec.max(), sec.min()))
    # --- the two rest switches (a drift on Resonance, target 5) ---
    # The period is deliberately NOT a whole number of rests: at 1 s with a 2 s rest, a drift that
    # kept walking would land back where a frozen one stopped, and the test would prove nothing.
    g = [["36=1", "38=2", "39=2", "12=50", "42=5"], ["43=50", "44=50", "46=0.7", "47=1"]]
    walk = render(RATE, secs=14, stages=g + [["52=0"]])
    freeze = render(RATE, secs=14, stages=g + [["52=1"]])
    check("Drift rest mode changes the sound", differ(walk, freeze) > -40,
          "difference %.1f dB under the signal" % differ(walk, freeze))
    r = [["36=1", "38=2", "39=2", "12=50", "53=5"], ["54=50", "57=1", "56=4", "61=1"]]
    walk = render(RATE, secs=14, stages=r + [["60=0"]])
    freeze = render(RATE, secs=14, stages=r + [["60=1"]])
    check("Ramp rest mode changes the sound", differ(walk, freeze) > -40,
          "difference %.1f dB under the signal" % differ(walk, freeze))
    # --- Play for as a drift target (R24), target 17 ---
    p = RATE + ["36=1", "38=2", "39=2", "41=1"]
    still = render(p, secs=14)
    drifted = render(p, secs=14, stages=[["42=17"], ["43=1.5", "44=1.5", "46=4", "47=1"]])
    check("Play for is a drift target", differ(still, drifted) > -40,
          "difference %.1f dB under the signal" % differ(still, drifted))
    fails = sum(1 for _, ok in CHECKS if not ok)
    print("%d sound checks, %d failed" % (len(CHECKS), fails))
    return fails


sys.exit(1 if main() else 0)
