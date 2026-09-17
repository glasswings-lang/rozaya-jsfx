#!/usr/bin/env python3
"""The Sweeping Filter's 2026-09-17 turn, measured through jsfx_run rather than read.

Every unit switch keeps the thing and converts the number; every SELECTOR switch leaves the
numbers alone; the per-target settings stay with their target.

    python tools/sweeping_filter_checks/unit_switches.py [path/to/full-feature-sweeping-filter.jsfx]
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
PLUG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "src", "full-feature-sweeping-filter.jsfx")
# jsfx_run runs at 120 BPM, so a beat is half a second.


def run(stages, want):
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
    ("rate, Seconds 20 -> BPM", [["15=1"], ["14=20"], ["15=0"]], {14: 3}),
    ("rate, Seconds 20 -> Every N beats", [["15=1"], ["14=20"], ["15=3"]], {14: 40}),
    ("rate, Hz 0.5 -> Seconds", [["15=2"], ["14=0.5"], ["15=1"]], {14: 2}),
    ("pan sweep rate, Seconds 2 -> BPM", [["32=1"], ["31=2"], ["32=0"]], {31: 30}),
    ("Low pitch, Hz 440 -> Semitones", [["1=0"], ["3=440"], ["1=1"]], {3: 69, 2: 69}),
    ("High pitch, Semitones 69 -> Cents", [["6=1"], ["8=69"], ["6=2"]], {8: 6900}),
    ("transport, Seconds 10 -> Beats", [["36=1"], ["37=10", "38=4"], ["36=2"]], {37: 20, 38: 8}),
    ("transport, to Cycles keeps the number", [["36=1"], ["37=10"], ["36=0"]], {37: 10}),
    ("drift period, Seconds 10 -> Beats", [["42=0"], ["47=1"], ["46=10"], ["47=2"]], {46: 20}),
    ("ramp time, Seconds 30 -> Minutes", [["53=0"], ["57=1"], ["56=30", "62=6"], ["57=2"]], {56: 0.5, 62: 0.1}),
    ("ramp time, Minutes -> Beats", [["53=0"], ["57=1"], ["56=30"], ["57=2"], ["57=3"]], {56: 60}),
    # --- the note name works in every unit, both ways ---
    ("Low note name follows the value in Hz", [["1=0"], ["3=880"]], {2: 81}),
    ("Low note name sets the value in Hz", [["1=0"], ["2=69"]], {3: 440}),
    ("High note name sets the value in Cents", [["6=2"], ["7=69"]], {8: 6900}),
    # --- selector switches leave numbers alone ---
    ("drift target switch leaves the period alone",
     [["42=0"], ["47=2"], ["46=7"], ["42=1"], ["42=0"]], {47: 2, 46: 7}),
    ("ramp target switch leaves the duration alone",
     [["53=0"], ["57=3"], ["56=7"], ["53=1"], ["53=0"]], {57: 3, 56: 7}),
    # --- per target, not shared ---
    ("drift period unit is per target",
     [["42=0"], ["47=1"], ["46=10"], ["42=1"], ["47=2"], ["46=3"], ["42=0"]], {47: 1, 46: 10}),
    ("drift amount unit is per target", [["42=4"], ["45=2"], ["42=5"], ["45=5"], ["42=4"]], {45: 2}),
    ("ramp by unit is per target", [["53=4"], ["55=2"], ["53=5"], ["55=5"], ["53=4"]], {55: 2}),
    ("drift movement mode is per target", [["42=7"], ["48=1"], ["42=8"], ["48=0"], ["42=7"]], {48: 1}),
    ("ramp time unit is per target",
     [["53=0"], ["57=1"], ["56=30"], ["53=1"], ["57=3"], ["53=0"]], {57: 1, 56: 30}),
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
