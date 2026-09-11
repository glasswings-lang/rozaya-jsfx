#!/usr/bin/env python3
"""Every Sweeping Filter drift target must move the sound, and stay stable.

For each of the 17 targets: the same render twice, drift amount 0 and drift
amount N, both with whatever that target needs to be audible (pan on for pan
targets, Offset-from-L for the phase offset, note mode for the Tuning
reference). They must differ, and neither may contain a broken sample.

THE SWEEP RUNS AT 120 BPM (one cycle every half second). At the default 2 BPM an
8-second render sits at the TOP of its sweep throughout, so nothing done to the
Low end is ever heard -- the first version of this test failed both Low targets
for exactly that reason on 2026-09-10.

    python tools/swf_target_test.py
"""
import os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
SRC = os.path.join(ROOT, "src", "full-feature-sweeping-filter.jsfx")
FAST = [(14, 120)]          # Rate value 120 in BPM mode
NOTES = [(1, 1), (2, 57), (3, 57), (6, 1), (7, 81), (8, 81)]
TARGETS = [
    (0, "Low frequency", FAST, 300), (1, "Low fine tune", FAST, 300),
    (2, "High frequency", FAST, 2000), (3, "High fine tune", FAST, 300),
    (4, "Tuning reference", FAST + NOTES, 150), (5, "Resonance", FAST, 0.4),
    (6, "Rate value", [], 60), (7, "On duration", FAST, 30), (8, "Depth", FAST, 60),
    (9, "Attack", FAST, 30), (10, "Release", FAST, 30),
    (11, "R channel phase offset", FAST + [(24, 1)], 120),
    (12, "Pan spread", FAST + [(25, 1), (26, 1)], 0.8),
    (13, "Pan glide", FAST + [(25, 1), (26, 1)], 400),
    (14, "Pan sweep rate", FAST + [(25, 1), (26, 10)], 60),
    (15, "Pan sweep every", FAST + [(25, 1), (26, 12)], 3),
    (16, "Wet/dry", FAST, 0.6),
]

def render(t, enable, amount, tmp):
    out = os.path.join(tmp, f"t{t}_{amount}.csv")
    cmd = [EXE, SRC, "--input", "noise", "--seconds", "8", "--csv", out, "--quiet",
           "--slider", f"39={t}"]
    for s, v in enable:
        cmd += ["--set-after", f"{s}={v}"]
    # period 1 second (unit Seconds), then the amounts: selector first, values after
    cmd += ["--set-after", "43=1", "--set-after", "42=1",
            "--set-after", f"40={amount}", "--set-after", f"41={amount}"]
    subprocess.run(cmd, check=True, capture_output=True)
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))

def main():
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        for t, name, enable, amount in TARGETS:
            a, b = render(t, enable, 0, tmp), render(t, enable, amount, tmp)
            stable = bool(np.isfinite(a).all() and np.isfinite(b).all())
            moved = not np.array_equal(a, b)
            loud = bool(np.abs(a).max() > 0)
            ok = stable and moved and loud
            fails += not ok
            gap = float(np.abs(a - b).max()) if stable else float("nan")
            print(f"{'ok  ' if ok else 'FAIL'} target {t:2} {name:24} changes the sound: {moved}, "
                  f"largest gap {gap:.3f}, stable: {stable}", flush=True)
    print("all 17 pass" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
