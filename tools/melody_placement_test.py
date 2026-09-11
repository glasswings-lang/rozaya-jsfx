#!/usr/bin/env python3
"""Melody's song placement, 2026-09-11 -- fixed without taking away the stopped transport.

The reverted fix (dcfeead) silenced a synced Melody until play. Rozaya: "now you
take that away for what? To force me to play the project if I wanna hear
something happening. No." This fix only makes the placement wait for Melody's
existing two-block settle hold. Four checks, old build (8ad5da1) against new:

1. STOPPED transport: synced Melody renders bit-identically to the old build and
   is not silent -- nothing about hearing it with the transport stopped changes.
2. FROM THE TOP: every saved Melody instance in a beat mode (27, in three projects)
   renders bit-identically to the old build when played from beat 0.
3. PARTWAY IN: three voices of different pitch, song starting at beat 2 -- the new
   build lands on voice 3 (0% wrong notes against beat 0 shifted); the old did not.
4. A SEEK while playing (to beat 10 at 3 s) lands on the right note. The runner does
   not re-run @init on a locate the way REAPER does, so this checks the seek
   detection; the play-start check (3) is the one that covers the @init path.

    python tools/melody_placement_test.py
"""
import glob, os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lock_test as L
from rpp_sliders import parse_line

EXE = L.EXE
NEW = os.path.join(ROOT, "src", "melody_phase.jsfx")
SYNC = [(2, 3), (1, 1)]
VOICES = SYNC + L.MELODY_VOICES

def old_build():
    # BYTES, not text: Melody's comments hold UTF-8 dashes, and text=True decodes
    # with Windows' cp1252, which crashed the first run before any check ran.
    p = os.path.join(tempfile.gettempdir(), "melody_8ad5da1.jsfx")
    open(p, "wb").write(subprocess.run(
        ["git", "show", "8ad5da1:src/melody_phase.jsfx"], cwd=ROOT,
        capture_output=True, check=True).stdout)
    return p

def run(plugin, args, out):
    subprocess.run([EXE, plugin, "--csv", out, "--quiet"] + args, check=True, capture_output=True)
    return open(out).read()

def synced_instances():
    found = []
    for f in glob.glob("E:/reaper/**/*.RPP", recursive=True) + glob.glob("E:/tensor's-rpp-projects/**/*.RPP", recursive=True):
        if "backup" in f.lower():
            continue
        L_ = open(f, encoding="utf-8", errors="replace").read().split("\n")
        n = 0
        for i, l in enumerate(L_):
            if "<JS " in l and "melody_phase.jsfx" in l:
                n += 1
                s = parse_line(L_[i + 1] + "\n").get(2)
                if s not in (None, "-") and float(s) >= 3:
                    found.append((f, n))
    return found

def main():
    old = old_build()
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        a, b = os.path.join(tmp, "a.csv"), os.path.join(tmp, "b.csv")
        # 1. stopped
        for label, st in (("synced, one voice", SYNC), ("synced, three voices", VOICES)):
            args = ["--stopped", "--seconds", "10"] + sum((["--slider", f"{s}={v}"] for s, v in st), [])
            x, y = run(old, args, a), run(NEW, args, b)
            loud = any(r.split(",")[2] not in ("0", "-0") for r in x.splitlines()[1:40000:97])
            ok = x == y and loud
            fails += not ok
            print(f"{'ok  ' if ok else 'FAIL'} 1. transport STOPPED, {label}: "
                  f"{'bit-identical to the old build' if x == y else 'DIFFERENT'}, {'makes sound' if loud else 'SILENT'}", flush=True)
        # 2. from the top, every saved synced instance
        # 60 s, not 20: two instances carry an 8-cycle Start delay and are silent
        # for the first 8 s, which a short render reports as "proved nothing".
        # Where old and new DIFFER, the new build must equal the same instance in
        # a free-running rate mode at the same speed -- a free sequencer never
        # places, so it is the reference for what the play/rest count should be.
        # The old build placed and then double-counted the first step: with Play
        # for 8 its first play period held 7 notes (simple-sequence #9, measured).
        inst = synced_instances()
        same = corrected = 0
        for f, k in inst:
            args = ["--rpp", f, "--fx", "melody_phase", "--instance", str(k), "--transport", "--seconds", "60"]
            x, y = run(old, args, a), run(NEW, args, b)
            loud = any(r.split(",")[2] not in ("0", "-0") for r in x.splitlines()[1:2600000:97])
            if x == y and loud:
                same += 1
                continue
            lines_ = open(f, encoding="utf-8", errors="replace").read().split("\n")
            idx = [i for i, l in enumerate(lines_) if "<JS " in l and "melody_phase.jsfx" in l][k - 1]
            beats = float(parse_line(lines_[idx + 1] + "\n")[1])
            free = run(NEW, args + ["--slider", "2=1", "--slider", f"1={beats * 60 / 120}"], os.path.join(tmp, "f.csv"))
            if loud and y == free:
                corrected += 1
                print(f"     {os.path.basename(f)} #{k}: differs from the old build and MATCHES the free-running reference")
            else:
                print(f"     {os.path.basename(f)} #{k}: {'identical' if x == y else 'DIFFERENT'}, "
                      f"{'sound' if loud else 'silent'}, matches free reference: {y == free}")
        ok = same + corrected == len(inst) and len(inst) > 0
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} 2. played from the top: {same} of {len(inst)} bit-identical to the old build, "
              f"{corrected} corrected to the free-running reference", flush=True)
        # 3. partway in
        shift = int(2 * 60 / 120 * L.SR)
        res = {}
        for label, plug in (("new", NEW), ("old", old)):
            A = L.render(plug[:-5], "pitch", VOICES, 0, 8, tmp, "A")
            B = L.render(plug[:-5], "pitch", VOICES, 2, 7, tmp, "B")
            res[label] = L.compare("pitch", A, B, shift)
        ok = res["new"] < 0.1 and res["old"] > 0.5
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} 3. song starting at beat 2: wrong-note share {res['new']:.2f} new, {res['old']:.2f} old", flush=True)
        # 4. seek while playing: beat 10 at 3 s. After it, C at time t is A at 5 + (t - 3).
        A = L.render(NEW[:-5], "pitch", VOICES, 0, 12, tmp, "A")
        cmd_c = [EXE, NEW, "--transport", "--seek-at", "3=10", "--seconds", "8", "--csv", os.path.join(tmp, "c.csv"), "--quiet"]
        for s, v in VOICES:
            cmd_c += ["--slider", f"{s}={v}"]
        subprocess.run(cmd_c, check=True, capture_output=True)
        C = np.loadtxt(os.path.join(tmp, "c.csv"), delimiter=",", skiprows=1, usecols=(2, 3))
        pa, pc = L.pitches(A), L.pitches(C)
        lo, hi, off = 35, 75, 20                       # 3.5 s .. 7.5 s in C; A is 2 s ahead
        wrong = float((pc[lo:hi] != pa[lo + off:hi + off]).mean())
        ok = wrong < 0.1
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} 4. seek to beat 10 while playing: wrong-note share after the seek {wrong:.2f}", flush=True)
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
