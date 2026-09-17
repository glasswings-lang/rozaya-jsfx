#!/usr/bin/env python3
"""Sweep Dwell's 2026-09-17 turn, measured through jsfx_run rather than read.

Every unit switch must keep the thing and convert the number; every SELECTOR switch must
leave the numbers alone; the per-target settings must stay with their target; and each new
control must actually change the sound.

    python tools/sweep_dwell_checks/unit_switches.py [path/to/sweep-dwell-filter.jsfx]
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
PLUG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "src", "sweep-dwell-filter.jsfx")
# 120 BPM is jsfx_run's tempo, so a beat is half a second.


def run(stages, want):
    """Apply each stage a block apart, then read the slider values back."""
    a = [EXE, PLUG, "--seconds", "0.5", "--list"]
    for i, st in enumerate(stages):
        if i:
            a.append("--stage")
        for s in st:
            a += ["--set-after", s]
    txt = subprocess.run(a, capture_output=True, text=True).stdout
    got = {int(m.group(1)): float(m.group(2)) for m in re.finditer(r"slider(\d+)\s.*?= (-?[\d.]+)", txt)}
    return {k: got.get(k) for k in want}


TESTS = [
    # --- the unit switches keep the thing ---
    ("segment length, Seconds 4 -> BPM", [["1=1"], ["2=1"], ["3=4"], ["2=0"]], {3: 15}),
    ("segment length, Seconds 4 -> Every N beats", [["1=1"], ["2=1"], ["3=4"], ["2=3"]], {3: 8}),
    ("segment length, Hz 0.5 -> Seconds", [["1=1"], ["2=2"], ["3=0.5"], ["2=1"]], {3: 2}),
    ("segment pitch, Hz 440 -> Semitones", [["1=1"], ["5=0"], ["7=440"], ["5=1"]], {7: 69, 6: 69}),
    ("segment pitch, Semitones 69 -> Cents", [["1=1"], ["5=0"], ["7=440"], ["5=1"], ["5=2"]], {7: 6900}),
    ("pan sweep rate, Seconds 2 -> BPM", [["22=1"], ["21=2"], ["22=0"]], {21: 30}),
    ("transport, Seconds 10 -> Beats", [["26=1"], ["27=10", "28=4"], ["26=2"]], {27: 20, 28: 8}),
    ("transport, to Cycles keeps the number", [["26=1"], ["27=10"], ["26=0"]], {27: 10}),
    ("drift period, Seconds 10 -> Beats", [["32=0"], ["37=1"], ["36=10"], ["37=2"]], {36: 20}),
    ("ramp time, Seconds 30 -> Minutes", [["43=0"], ["46=1"], ["47=30", "52=6"], ["46=2"]], {47: 0.5, 52: 0.1}),
    ("ramp time, Minutes -> Beats", [["43=0"], ["46=1"], ["47=30"], ["46=2"], ["46=3"]], {47: 60}),
    # --- the note name works in every unit, both ways ---
    ("note name follows the value in Hz", [["1=1"], ["5=0"], ["7=880"]], {6: 81}),
    ("note name sets the value in Hz", [["1=1"], ["5=0"], ["6=69"]], {7: 440}),
    ("note name sets the value in Cents", [["1=1"], ["5=2"], ["6=69"]], {7: 6900}),
    # --- selector switches leave numbers alone ---
    ("segment switch leaves lengths alone", [["1=1"], ["2=3"], ["3=7"], ["1=2"], ["1=1"]], {2: 3, 3: 7}),
    ("drift target switch leaves the period alone",
     [["32=0"], ["37=2"], ["36=7"], ["32=1"], ["32=0"]], {37: 2, 36: 7}),
    ("ramp target switch leaves the duration alone",
     [["43=0"], ["46=3"], ["47=7"], ["43=1"], ["43=0"]], {46: 3, 47: 7}),
    # --- per target, not shared ---
    ("drift period unit is per target",
     [["32=0"], ["37=1"], ["36=10"], ["32=1"], ["37=2"], ["36=3"], ["32=0"]], {37: 1, 36: 10}),
    ("drift amount unit is per target",
     [["32=4"], ["35=2"], ["32=5"], ["35=5"], ["32=4"]], {35: 2}),
    ("ramp by unit is per target",
     [["43=4"], ["45=2"], ["43=5"], ["45=5"], ["43=4"]], {45: 2}),
    ("drift movement mode is per target",
     [["32=0"], ["38=1"], ["32=1"], ["38=0"], ["32=0"]], {38: 1}),
    ("ramp time unit is per target",
     [["43=0"], ["46=1"], ["47=30"], ["43=1"], ["46=3"], ["43=0"]], {46: 1, 47: 30}),
]


def main():
    fails = 0
    for name, stages, want in TESTS:
        got = run(stages, want)
        ok = all(got[k] is not None and abs(got[k] - v) < 0.02 for k, v in want.items())
        fails += not ok
        print("%s %s %s" % ("PASS" if ok else "FAIL", name, "" if ok else got))
    print("%d switch tests, %d failed" % (len(TESTS), fails))
    return fails


sys.exit(1 if main() else 0)
