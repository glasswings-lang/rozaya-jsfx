#!/usr/bin/env python3
"""Does each tempo-synced plugin really lock to the SONG, not to when play was pressed?

Needs jsfx_run's moving transport (--beat-start, 2026-09-10). Before that the beat
position never moved in the runner, so no lock anywhere in the suite had been
tested -- only that old and new builds shared a formula.

For each plugin, in a beat mode: render A starting at beat 0, render B starting a
few beats into the song. Locked, B lines up with A shifted by those beats. The
CONTROL is the same plugin at the same speed in a free mode (Seconds or BPM); it
starts fresh on play, so it must NOT line up. A test whose control also lines up
proves nothing, and says so.

Three ways of comparing, because the plugins lock differently:
- Effects (Sweeping Filter, Tremolo, Stereo Phaser) set their sweep from the song
  position every sample. Fed a 220 Hz sine that is whole cycles over the shift,
  the SAMPLES line up. Start at beat 1.5, mid-cycle.
- Rhythm Track and Shepard Scale place their sequence at play and count on; their
  oscillators restart every render, so the LOUDNESS ENVELOPE (10 ms RMS) is
  compared -- where the beats land. Start at beat 1.5.
- Melody places the RIGHT NOTE and restarts it from its attack, by design ("You
  land on the RIGHT note; it just begins again"). With one voice every note is the
  same and nothing can be seen -- the first run of this test proved exactly that.
  So three voices of different pitch are switched on, the song starts on a WHOLE
  beat (2), and the PITCH playing in each 100 ms window is compared.

    python tools/lock_test.py [name ...]
"""
import os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
SR = 44100
WIN = 441
PWIN = 4410
MELODY_VOICES = [(42, 1), (50, 1)]        # V2 and V3 Active (D4 and E4 beside V1's C4)

# name, file, kind, start beat, locked settings, control settings (same speed, free)
CASES = [
    ("Sweeping Filter", "full-feature-sweeping-filter", "fx", 1.5, [(15, 3), (14, 4)], [(15, 1), (14, 2)]),
    ("Tremolo", "Full_Feature_Tremolo", "fx", 1.5, [(2, 3), (1, 4)], [(2, 1), (1, 2)]),
    ("Stereo Phaser", "stereo-phaser", "fx", 1.5, [(2, 3), (1, 4)], [(2, 1), (1, 2)]),
    ("Melody", "melody_phase", "pitch", 2, [(2, 3), (1, 1)] + MELODY_VOICES, [(2, 1), (1, 0.5)] + MELODY_VOICES),
    ("Rhythm Track", "rhythm-track", "env", 1.5, [(2, 3), (1, 1)], [(2, 0), (1, 120)]),
    ("Shepard Scale", "shepard-scale", "env", 1.5, [(2, 3), (1, 1)], [(2, 0), (1, 120)]),
]

def render(plugin, kind, settings, beat_start, seconds, tmp, tag):
    out = os.path.join(tmp, tag + ".csv")
    cmd = [EXE, os.path.join(ROOT, "src", plugin + ".jsfx"), "--beat-start", str(beat_start),
           "--seconds", str(seconds), "--csv", out, "--quiet"]
    if kind == "fx":
        cmd += ["--input", "sine", "--input-hz", "220", "--input-db", "-6"]
    for s, v in settings:
        cmd += ["--slider", f"{s}={v}"]
    subprocess.run(cmd, check=True, capture_output=True)
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))

def env(x):
    m = x.mean(axis=1)
    n = len(m) // WIN
    return np.sqrt((m[: n * WIN].reshape(n, WIN) ** 2).mean(axis=1))

def pitches(x):
    m = x.mean(axis=1)
    n = len(m) // PWIN
    w = np.hanning(PWIN)
    out = []
    for k in range(n):
        seg = m[k * PWIN:(k + 1) * PWIN]
        spec = np.abs(np.fft.rfft(seg * w))
        out.append(int(np.argmax(spec[5:])) + 5 if seg.any() else -1)
    return np.array(out)

def compare(kind, a, b, shift):
    lo, hi = SR, 6 * SR
    if kind == "fx":
        return float(np.abs(b[lo:hi] - a[lo + shift:hi + shift]).max())
    if kind == "env":
        ea, eb = env(a), env(b)
        k, l0, l1 = shift // WIN, lo // WIN, hi // WIN
        return float(np.abs(eb[l0:l1] - ea[l0 + k:l1 + k]).mean() / max(ea[l0 + k:l1 + k].mean(), 1e-9))
    pa, pb = pitches(a), pitches(b)
    k, l0, l1 = shift // PWIN, lo // PWIN, hi // PWIN
    sounding = (pb[l0:l1] >= 0) & (pa[l0 + k:l1 + k] >= 0)
    mismatch = (pb[l0:l1] != pa[l0 + k:l1 + k]) & sounding
    return float(mismatch.sum() / max(sounding.sum(), 1))       # share of windows on the wrong note

def main():
    pick = sys.argv[1:]
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, plugin, kind, start, locked, control in CASES:
            if pick and not any(p.lower() in name.lower() for p in pick):
                continue
            shift = int(start * 60 / 120 * SR)
            gaps = {}
            for label, st in (("locked", locked), ("control", control)):
                a = render(plugin, kind, st, 0, 8, tmp, "a")
                b = render(plugin, kind, st, start, 7, tmp, "b")
                gaps[label] = compare(kind, a, b, shift) if np.abs(a).max() else None
            if gaps["locked"] is None or gaps["control"] is None:
                fails += 1
                print(f"FAIL {name:16} SILENT output -- nothing measured")
                continue
            unit, limit = {"fx": ("largest sample gap", 1e-3), "env": ("envelope gap", 0.1),
                           "pitch": ("share of windows on the wrong note", 0.1)}[kind]
            can_fail = gaps["control"] > max(10 * gaps["locked"], limit)
            ok = gaps["locked"] < limit and can_fail
            fails += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name:16} starting {start} beats in lines up with beat 0 shifted: "
                  f"{unit} {gaps['locked']:.2e} locked, {gaps['control']:.2e} in the free control"
                  + ("" if can_fail else "  (the control lined up too -- this test cannot tell)"), flush=True)
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
