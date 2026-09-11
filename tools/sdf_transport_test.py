#!/usr/bin/env python3
"""Sweep Dwell's beat modes with a MOVING transport -- the bar lock and live tempo.

Every earlier test ran with jsfx_run's old default time info: playing, 120 BPM,
and a beat position that never moved. Under that, a tempo-locked phase is frozen,
so "old and new agree" proved only that both shared a formula. This uses the
runner's --transport / --beat-start / --tempo-at (added 2026-09-10).

1. LOCK. All segments in Every N beats (4+1+6+1 = a 12-beat cycle, 6 s at 120).
   A render starting at beat 6 must match a render starting at beat 0 shifted by
   those 6 beats (3 s). The input is a sine with a whole number of cycles in 3 s,
   so the input lines up too. The same comparison in Seconds -- no lock -- must
   NOT match, or the test cannot fail.
2. OLD PARITY. The old plugin's Host x cycle (Fit to durations) against the new
   All-segments-in-beats, same moving transport, starting at beat 6.
3. LIVE TEMPO. The same pair with the tempo dropping from 120 to 60 at 4 s; and
   the tempo change must audibly matter.
4. ONE SEGMENT IN BEATS (unlocked) at 60 BPM must equal its seconds on the old
   plugin, bit for bit.

    python tools/sdf_transport_test.py
"""
import os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
NEW = os.path.join(ROOT, "src", "sweep-dwell-filter.jsfx")
SR = 44100
SHIFT = 3 * SR                     # 6 beats at 120 BPM

def old_build():
    p = os.path.join(tempfile.gettempdir(), "sdf_oracle_8bde9c5.jsfx")
    open(p, "w", encoding="utf-8", newline="").write(subprocess.run(
        ["git", "show", "8bde9c5:src/sweep-dwell-filter.jsfx"], cwd=ROOT,
        capture_output=True, text=True, check=True).stdout)
    return p

def render(plugin, args, pre, after, tmp, tag, seconds):
    out = os.path.join(tmp, tag + ".csv")
    cmd = [EXE, plugin, "--input", "sine", "--input-hz", "220", "--input-db", "-6",
           "--seconds", str(seconds), "--csv", out, "--quiet"] + args
    for s, v in pre:
        cmd += ["--slider", f"{s}={v}"]
    for s, v in after:
        cmd += ["--set-after", f"{s}={v}"]
    subprocess.run(cmd, check=True, capture_output=True)
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))

def main():
    old = old_build()
    fails = 0
    BEATS = ([(1, 0)], [(2, 3)])          # All segments, Length mode = Every N beats
    SECS = ([(1, 0)], [])                 # the same, left in Seconds
    with tempfile.TemporaryDirectory() as tmp:
        # 1. lock
        gaps = {}
        for name, (pre, after) in (("beats", BEATS), ("seconds", SECS)):
            a = render(NEW, ["--transport"], pre, after, tmp, "a", 12)
            b = render(NEW, ["--beat-start", "6"], pre, after, tmp, "b", 9)
            lo, hi = SR, 8 * SR
            gaps[name] = float(np.abs(b[lo:hi] - a[lo + SHIFT:hi + SHIFT]).max())
        ok = gaps["beats"] < 1e-3 and gaps["seconds"] > 1e-2
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} 1. bar lock: starting at beat 6 lines up with beat 0 shifted 3 s -- "
              f"largest gap {gaps['beats']:.2e} in beats; {gaps['seconds']:.2e} in Seconds (must NOT line up)")

        # 2. old parity, moving transport
        n = render(NEW, ["--beat-start", "6"], *BEATS, tmp, "n", 12)
        o = render(old, ["--beat-start", "6"], [], [(51, 1), (53, 0)], tmp, "o", 12)
        g = float(np.abs(n[SR:] - o[SR:]).max())
        ok = g < 1e-4
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} 2. new beats vs old Host x, moving transport from beat 6: "
              f"{'bit-identical' if np.array_equal(n, o) else 'largest gap after 1 s %.2e' % g}")

        # 3. live tempo change
        args = ["--beat-start", "6", "--tempo-at", "4=60"]
        n2 = render(NEW, args, *BEATS, tmp, "n2", 14)
        o2 = render(old, args, [], [(51, 1), (53, 0)], tmp, "o2", 14)
        n3 = render(NEW, ["--beat-start", "6"], *BEATS, tmp, "n3", 14)
        g2 = float(np.abs(n2[SR:] - o2[SR:]).max())
        matters = float(np.abs(n2[5 * SR:] - n3[5 * SR:]).max()) > 1e-2
        ok = g2 < 1e-4 and matters
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} 3. tempo 120 -> 60 at 4 s, new vs old: "
              f"{'bit-identical' if np.array_equal(n2, o2) else 'largest gap %.2e' % g2}; the change matters: {matters}")

        # 4. one segment in beats, unlocked, at 60 BPM = its seconds
        n4 = render(NEW, ["--tempo", "60"], [(1, 1)], [(2, 3), (3, 4)], tmp, "n4", 20)
        o4 = render(old, ["--tempo", "60"], [], [(12, 4)], tmp, "o4", 20)
        ok = np.array_equal(n4, o4)
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} 4. High dwell 4 beats at 60 BPM vs old High Dwell 4 s: "
              f"{'bit-identical' if ok else 'largest gap %.2e' % float(np.abs(n4 - o4).max())}")
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
