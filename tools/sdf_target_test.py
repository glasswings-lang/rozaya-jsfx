#!/usr/bin/env python3
"""Every Sweep Dwell drift target must move the sound, and stay stable.

Same method as swf_target_test.py: a render with drift amount 0 against one with
amount N, each with whatever makes that target audible. The cycle is shortened
(All segments, length 0.5 s) so both dwells and both fades pass many times in 8
seconds -- a Low-end target is inaudible if the render never leaves High dwell.

    python tools/sdf_target_test.py
"""
import os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
SRC = os.path.join(ROOT, "src", "sweep-dwell-filter.jsfx")
SHORT = [(3, 0.5)]                                    # on All segments
NOTES = [(5, 1), (6, 60), (7, 60)]                    # both dwells in Semitones
TARGETS = [
    (0, "High dwell length", SHORT, 0.4), (1, "Fade down length", SHORT, 0.4),
    (2, "Low dwell length", SHORT, 0.4), (3, "Fade up length", SHORT, 0.4),
    (4, "High dwell frequency", SHORT, 2000), (5, "High dwell fine tune", SHORT, 300),
    (6, "Low dwell frequency", SHORT, 400), (7, "Low dwell fine tune", SHORT, 300),
    (8, "Tuning reference", SHORT + NOTES, 150), (9, "Resonance", SHORT, 0.4),
    (10, "Stereo phase offset", SHORT + [(14, 1)], 120),
    (11, "Pan spread", SHORT + [(15, 1), (16, 1)], 0.8),
    (12, "Pan glide", SHORT + [(15, 1), (16, 1)], 400),
    (13, "Pan sweep rate", SHORT + [(15, 1), (16, 10)], 60),
    (14, "Pan sweep every", SHORT + [(15, 1), (16, 12)], 3),
    (15, "Wet/dry", SHORT, 0.6),
]

def render(t, enable, amount, tmp):
    out = os.path.join(tmp, f"t{t}_{amount}.csv")
    cmd = [EXE, SRC, "--input", "noise", "--seconds", "8", "--csv", out, "--quiet",
           "--slider", "1=0", "--slider", f"30={t}"]
    for s, v in enable:
        cmd += ["--set-after", f"{s}={v}"]
    cmd += ["--set-after", "34=1", "--set-after", "33=1",
            "--set-after", f"31={amount}", "--set-after", f"32={amount}"]
    subprocess.run(cmd, check=True, capture_output=True)
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))

def main():
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        for t, name, enable, amount in TARGETS:
            a, b = render(t, enable, 0, tmp), render(t, enable, amount, tmp)
            stable = bool(np.isfinite(a).all() and np.isfinite(b).all())
            moved = not np.array_equal(a, b)
            ok = stable and moved and bool(np.abs(a).max() > 0)
            fails += not ok
            print(f"{'ok  ' if ok else 'FAIL'} target {t:2} {name:22} changes the sound: {moved}, "
                  f"largest gap {float(np.abs(a - b).max()) if stable else float('nan'):.3f}, stable: {stable}",
                  flush=True)
    print("all 16 pass" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
