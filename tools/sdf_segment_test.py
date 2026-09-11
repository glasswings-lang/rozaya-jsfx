#!/usr/bin/env python3
"""Sweep Dwell's Segment selector, checked against the OLD plugins as the oracle.

Every case sets something through the new selector, and the same thing the old
way on a pre-segment build, with the same staging, and requires the two renders
to be bit-identical. So "picking Fade down and typing 3" must sound exactly like
the old Fade Down sec = 3; "All segments, length 2" exactly like all four old
times at 2; a length in BPM, Hz, Every N beats or N per beat exactly like the
seconds it means.

Oracles: the pre-segment src (git 8bde9c5, which has pitch modes) for pitch
cases, and the same file for everything else -- its first ten sliders are the
two pitch blocks, 12-17 the four times and shapes.

    python tools/sdf_segment_test.py
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
NEW = os.path.join(ROOT, "src", "sweep-dwell-filter.jsfx")

# old (8bde9c5) ids: 1 low mode, 2 low note, 3 low value, 6 high mode, 7 high note,
# 8 high value, 12 High Dwell sec, 13 Low Dwell sec, 14 Fade Down sec,
# 15 Fade Down Shape, 16 Fade Up sec, 17 Fade Up Shape, 30 Start delay (seconds)
# new ids: 1 Segment {All, High, Fade down, Low, Fade up}, 2 Length mode,
# 3 Length, 4 Fade shape, 5 Pitch mode, 6 Note, 7 Frequency, 24/25 Start delay
CASES = [
    ("Fade down length 3 s",          [(1, 2)], [(3, 3)],                    [], [(14, 3)]),
    ("Low dwell length 2 s",          [(1, 3)], [(3, 2)],                    [], [(13, 2)]),
    ("Fade up shape Exponential",     [(1, 4)], [(4, 3)],                    [], [(17, 3)]),
    ("Low dwell frequency 300 Hz",    [(1, 3)], [(7, 300)],                  [], [(3, 300)]),
    ("High dwell frequency 2000 Hz",  [(1, 1)], [(7, 2000)],                 [], [(8, 2000)]),
    ("All segments, length 2 s",      [(1, 0)], [(3, 2)],                    [], [(12, 2), (13, 2), (14, 2), (16, 2)]),
    ("All segments, fade shape Linear", [(1, 0)], [(4, 0)],                  [], [(15, 0), (17, 0)]),
    ("All segments, frequency 1000",  [(1, 0)], [(7, 1000)],                 [], [(3, 1000), (8, 1000)]),
    ("High dwell in BPM 30 = 2 s",    [(1, 1)], [(2, 0), (3, 30)],           [], [(12, 2)]),
    ("High dwell in Hz 0.5 = 2 s",    [(1, 1)], [(2, 2), (3, 0.5)],          [], [(12, 2)]),
    ("High dwell semitones, note 81", [(1, 1)], [(5, 1), (6, 81)],           [], [(6, 1), (7, 81), (8, 81)]),
    ("Low dwell cents 5700",          [(1, 3)], [(5, 2), (7, 5700)],         [], [(1, 2), (3, 5700)]),
]
# Beat modes need the runner's tempo; measured from a 4-beat start delay below.

def render(plugin, pre, after, tmp, tag):
    out = os.path.join(tmp, tag + ".csv")
    cmd = [EXE, plugin, "--input", "noise", "--seconds", "20", "--csv", out, "--quiet"]
    for s, v in pre:
        cmd += ["--slider", f"{s}={v}"]
    for s, v in after:
        cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-400:])
    return open(out).read()

def main():
    old = os.path.join(tempfile.gettempdir(), "sdf_oracle_8bde9c5.jsfx")
    open(old, "w", encoding="utf-8", newline="").write(subprocess.run(
        ["git", "show", "8bde9c5:src/sweep-dwell-filter.jsfx"], cwd=ROOT,
        capture_output=True, text=True, check=True).stdout)
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = render(old, [], [], tmp, "base")
        for name, npre, nafter, opre, oafter in CASES:
            a = render(NEW, npre, nafter, tmp, "n")
            b = render(old, opre, oafter, tmp, "o")
            ok = a == b and b != base
            fails += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name:34} identical to the old controls: {a == b}; "
                  f"differs from defaults: {b != base}", flush=True)
        # Beat modes: find the runner's tempo from the plugin itself -- a 4-beat
        # start delay must equal SOME whole-number-of-ms seconds delay.
        for beats_name, nafter, secs_for in (
            ("High dwell Every N beats 4", [(2, 3), (3, 4)], lambda bpm: [(12, 4 * 60 / bpm)]),
            ("High dwell N per beat 0.25", [(2, 4), (3, 0.25)], lambda bpm: [(12, 60 / bpm / 0.25)]),
            ("Start delay Every N beats 4", [(24, 3), (25, 4)], lambda bpm: [(30, 4 * 60 / bpm)]),
        ):
            a = render(NEW, [(1, 1)], nafter, tmp, "n")
            match = next((bpm for bpm in (120, 60, 100, 90, 140) if a == render(old, [], secs_for(bpm), tmp, "o")), None)
            fails += match is None
            print(f"{'ok  ' if match else 'FAIL'} {beats_name:34} identical to its seconds: "
                  f"{'yes, at the runner tempo of %d BPM' % match if match else 'no tempo matched'}", flush=True)
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
