#!/usr/bin/env python3
"""Womb's 2026-09-17 turn, measured through jsfx_run rather than read.

Every unit switch keeps the thing and converts the number; every selector switch leaves the
numbers alone; the per-target units stay with their target; the note names work in every unit.

    python tools/womb_checks/unit_switches.py [path/to/womb_sound_generator_v3.jsfx]
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
PLUG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "src", "womb_sound_generator_v3.jsfx")
# jsfx_run runs at 120 BPM: a beat is half a second. Womb's own heart rate is its own control.


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
    # --- the rate and time units keep what they measure ---
    ("heart rate, 60 BPM -> Seconds", [["2=0"], ["1=60"], ["2=1"]], {1: 1}),
    ("heart rate, Seconds 2 -> BPM", [["2=1"], ["1=2"], ["2=0"]], {1: 30}),
    ("systole, 120 ms -> Seconds", [["5=0"], ["4=120"], ["5=1"]], {4: 0.12}),
    ("systole, Seconds 0.5 -> Beats", [["5=1"], ["4=0.5"], ["5=2"]], {4: 1}),
    ("breath, Seconds 4 -> Beats", [["25=0"], ["26=4", "28=4"], ["25=1"]], {26: 8, 28: 8}),
    ("bloodflow offset, 250 ms -> Seconds", [["62=0"], ["61=250"], ["62=1"]], {61: 0.25}),
    ("transport, Beats 8 -> Seconds", [["77=1"], ["78=8"], ["77=0"]], {78: 4}),
    ("drift period, Seconds 10 -> Beats", [["85=0"], ["90=1"], ["89=10"], ["90=2"]], {89: 20}),
    ("ramp time, Seconds 30 -> Minutes", [["95=0"], ["99=1"], ["98=30", "103=6"], ["99=2"]], {98: 0.5, 103: 0.1}),
    # --- the note names, in every unit, both ways ---
    ("S1 note name follows the value in Hz", [["6=0"], ["8=440"]], {7: 69}),
    ("S1 note name sets the value in Hz", [["6=0"], ["7=69"]], {8: 440}),
    ("Breath high-pass name follows its value", [["45=0"], ["47=440"]], {46: 69}),
    ("Breath high-pass, Hz 440 -> Semitones", [["45=0"], ["47=440"], ["45=1"]], {47: 69}),
    ("Bloodflow filter name sets its value in Cents", [["66=2"], ["67=69"]], {68: 6900}),
    # --- selectors leave numbers alone ---
    ("drift target switch leaves the period alone",
     [["85=0"], ["90=2"], ["89=7"], ["85=1"], ["85=0"]], {90: 2, 89: 7}),
    ("ramp target switch leaves the duration alone",
     [["95=0"], ["99=3"], ["98=7"], ["95=1"], ["95=0"]], {99: 3, 98: 7}),
    # --- per target ---
    ("drift amount unit is per target", [["85=3"], ["88=2"], ["85=4"], ["88=5"], ["85=3"]], {88: 2}),
    ("ramp by unit is per target", [["95=3"], ["97=2"], ["95=4"], ["97=5"], ["95=3"]], {97: 2}),
    ("drift period unit is per target",
     [["85=0"], ["90=1"], ["89=10"], ["85=1"], ["90=2"], ["89=3"], ["85=0"]], {90: 1, 89: 10}),
    ("ramp time unit is per target",
     [["95=0"], ["99=1"], ["98=30"], ["95=1"], ["99=3"], ["95=0"]], {99: 1, 98: 30}),
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
