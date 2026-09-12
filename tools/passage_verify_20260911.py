#!/usr/bin/env python3
"""Spectral Vowel Passage's 2026-09-11 layout, measured, stage by stage.
docs/layouts/spectral-vowel-passage.md, "THE LAYOUT".

Renders run TEST COPIES with the per-load rand() scramble pinned (as the Morpher's
tools do); the shipped plugin keeps its scramble.

current   every live instance: the pre-layout build (PRE) on the project as it is ==
          the new build on a temp copy converted by passage_migrate_20260911.convert,
          8 s of noise in, not silent. Live files are never written.

    python tools/passage_verify_20260911.py [section ...] [--jobs N]
"""
import concurrent.futures as cf, os, re, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import passage_migrate_20260911 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "spectral_vowel_passage"
PRE = "d5adcaf"      # the last commit before the layout work began
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 6
fails = 0
tmp = tempfile.mkdtemp()


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def pinned(text, name):
    if text.count("_tp = time_precise();") != 1:
        raise SystemExit("the load-time scramble line is not there exactly once")
    p = os.path.join(tmp, name)
    open(p, "w", encoding="utf-8", newline="").write(text.replace("_tp = time_precise();", "_tp = 0.25;"))
    return p


OLD = pinned(subprocess.run(["git", "show", f"{PRE}:src/{FX}.jsfx"], cwd=ROOT, capture_output=True,
                            check=True).stdout.decode("utf-8"), "old.jsfx")
NEW = pinned(open(os.path.join(ROOT, "src", f"{FX}.jsfx"), encoding="utf-8").read(), "new.jsfx")


def run(plugin, seconds, rpp, inst, extra=("--input", "noise")):
    out = os.path.join(tmp, f"o{os.getpid()}_{abs(hash((plugin, rpp, inst)))}.csv")
    cmd = [EXE, plugin, "--seconds", str(seconds), "--csv", out, "--quiet", "--rpp", rpp,
           "--fx", FX, "--instance", str(inst), *extra]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    a = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))
    os.remove(out)
    return a


def current():
    jobs = []
    for live in mig.files():
        text, n = mig.convert(live)
        conv = os.path.join(tmp, "m-" + re.sub(r"[/\\: ']", "_", live))
        open(conv, "w", encoding="utf-8", errors="surrogateescape", newline="").write(text)
        jobs += [(live, conv, i) for i in range(1, n + 1)]

    def one(j):
        live, conv, i = j
        a = run(OLD, 8, live, i)
        b = run(NEW, 8, conv, i)
        return live, i, np.array_equal(a, b), float(np.abs(b).max())

    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(one, jobs))
    for live, i, eq, mx in res:
        if not eq:
            report(False, f"{live} #{i}: differs")
    same = sum(r[2] for r in res)
    sounding = sum(r[3] > 0 for r in res)
    report(same == len(res) and sounding == len(res) and len(res) == 49,
           f"current: {same} of {len(res)} instances bit-identical, {sounding} not silent")


# --- All slots (stage 3). Fresh instances, a tone in, blocks of ~0.74 s so a capture
# hears real audio. The HEARD slot never changes inside a comparison (a slot change
# hands the voice phases over, which alone moves the render): Audition = Morph with
# Morph parked at 0 (Slot 1) or 100 (Slot 8), and Capture slot, which Morph audition
# ignores, is free to move. Slider numbers are the 2026-09-11 layout's.
BLOCK = 32768
TONE = ("--input", "sine", "--input-hz", "220", "--input-db", "-6", "--block", str(BLOCK))
CAP_SLOT, CAPTURE, POINT, TEXTURE, AUDITION, MORPH = 1, 2, 3, 13, 36, 34
DRIFT_TARGET, DRIFT_UP, DRIFT_PERIOD = 44, 45, 48
WAIT = [[]] * 5


def fresh_run(morph, steps, seconds=16, first_slot=0):
    stages = [[(AUDITION, 1), (MORPH, morph), (CAP_SLOT, first_slot)], [(CAPTURE, 1)]] + [list(s) for s in steps]
    out = os.path.join(tmp, f"f{os.getpid()}_{abs(hash((morph, str(steps))))}.csv")
    cmd = [EXE, NEW, "--seconds", str(seconds), "--csv", out, "--quiet", *TONE]
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    a = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))
    os.remove(out)
    return a[(len(stages) + 2) * BLOCK:]


def allslots():
    # Every comparison below has the same number of stages on both sides, and a
    # selector is always set one stage BEFORE the value it governs (jsfx_run README).
    # Capture on All == an ordinary capture into that slot, heard through Slot 8.
    on_all = fresh_run(100, [[], [], *WAIT])
    ordinary = fresh_run(100, [[], [], *WAIT], first_slot=8)
    report(np.array_equal(on_all, ordinary) and np.abs(on_all).max() > 0,
           "all: a capture on All, heard in Slot 8, == an ordinary capture into Slot 8")
    # Texture moved on All reaches Slot 8, which All does not show...
    moved = fresh_run(100, [[], [(TEXTURE, 90)], *WAIT])
    report(not np.array_equal(moved, on_all), "all: Texture moved on All changed Slot 8")
    # ...exactly as moving it by hand on Slot 8 at the same moment does.
    by_hand = fresh_run(100, [[(CAP_SLOT, 8)], [(TEXTURE, 90)], *WAIT])
    report(np.array_equal(moved, by_hand), "all: Texture on All == Texture moved by hand on Slot 8")
    # Passing through All keeps Slot 8's own Texture.
    via_all = fresh_run(100, [[(CAP_SLOT, 8)], [(TEXTURE, 90)], [(CAP_SLOT, 0)], [], [(CAP_SLOT, 8)], *WAIT])
    direct = fresh_run(100, [[(CAP_SLOT, 8)], [(TEXTURE, 90)], [], [], [], *WAIT])
    report(np.array_equal(via_all, direct), "all: passing through All kept Slot 8's own Texture")
    # A Texture drift set on All moves Slot 8 (target 0 is Texture, the default).
    drift = fresh_run(100, [[], [(DRIFT_UP, 40), (DRIFT_PERIOD, 1.3)], *WAIT])
    report(not np.array_equal(drift, on_all), "all: a Texture drift set on All moves Slot 8")
    # ...exactly as setting it by hand on Slot 8 does.
    drift_hand = fresh_run(100, [[(CAP_SLOT, 8)], [(DRIFT_UP, 40), (DRIFT_PERIOD, 1.3)], *WAIT])
    report(np.array_equal(drift, drift_hand), "all: that drift == the same drift set by hand on Slot 8")


SRC, SRC_FINE, TARGET, TRANSPOSE, T_UNIT, FINE, TUNING = 5, 6, 8, 9, 10, 11, 30


def pitch():
    # Heard: Slot 1 (Morph parked at 0), captured into Slot 1. Equal stage counts.
    def one(steps):
        return fresh_run(0, [*steps, *WAIT], first_slot=1)
    base12 = one([[], [(TRANSPOSE, 12)]])
    untouched = one([[], []])
    report(not np.array_equal(base12, untouched) and np.abs(base12).max() > 0,
           "pitch: Transpose 12 changes the sound (the check can fail)")
    for label, steps in (("1200 cents", [[(T_UNIT, 2)], [(TRANSPOSE, 1200)]]),
                         ("440 Hz from a 440 reference", [[(T_UNIT, 0)], [(TRANSPOSE, 440)]]),
                         ("880 Hz from an 880 reference", [[(T_UNIT, 0), (TUNING, 880)], [(TRANSPOSE, 880)]]),
                         # Same stage: a fine tune set a block earlier sounds +1 for that
                         # block and moves the voice phases for good (jsfx_run README).
                         ("11 semitones + Fine tune 100 cents", [[], [(FINE, 100), (TRANSPOSE, 11)]])):
        report(np.array_equal(one(steps), base12), f"pitch: {label} == Transpose 12 semitones")
    by_note = one([[(SRC, 61)], [(TARGET, 64)]])
    report(np.array_equal(by_note, one([[(SRC, 61)], [(TRANSPOSE, 4)]])),
           "pitch: Source C4, Target E4 == Transpose 4")
    flat = one([[(SRC, 61), (SRC_FINE, -50)], [(TARGET, 64)]])
    report(np.array_equal(flat, one([[(SRC, 61), (SRC_FINE, -50)], [(TRANSPOSE, 4.5)]])),
           "pitch: Source C4 50 cents flat, Target E4 == Transpose 4.5")
    on_all = fresh_run(100, [[], [(TRANSPOSE, 7)], *WAIT])
    report(np.array_equal(on_all, fresh_run(100, [[(CAP_SLOT, 8)], [(TRANSPOSE, 7)], *WAIT])),
           "pitch: Transpose 7 on All == by hand on Slot 8")


GRAIN, HICUT, INPUT_LEVEL = 14, 18, 37


def rms(a):
    return float(np.sqrt((a ** 2).mean()))


def grainhc():
    def one(morph, steps, first_slot=0):
        return fresh_run(morph, [*steps, *WAIT], first_slot=first_slot)
    # High cut at its lowest, 200 Hz, below the 220 Hz tone: the dry input is turned
    # down so only Passage's own sound is measured.
    for tex, label in ((100, "wash"), (0, "voice")):
        open_ = one(0, [[(TEXTURE, tex), (INPUT_LEVEL, -60)], []], first_slot=1)
        cut = one(0, [[(TEXTURE, tex), (INPUT_LEVEL, -60)], [(HICUT, 200)]], first_slot=1)
        report(rms(open_) > 0 and rms(cut) < 0.1 * rms(open_),
               f"highcut: 200 Hz silences the {label} of a 220 Hz tone (rms {rms(open_):.4f} -> {rms(cut):.4f})")
    report(np.array_equal(one(100, [[], [(HICUT, 2000)]]), one(100, [[(CAP_SLOT, 8)], [(HICUT, 2000)]])),
           "highcut: 2000 on All == by hand on Slot 8")
    # Wash grain is per slot: 40 ms on Slot 8 changes Slot 8 and leaves Slot 1 alone.
    for morph, heard, should in ((100, "Slot 8", True), (0, "Slot 1", False)):
        base = one(morph, [[(TEXTURE, 100)], [(CAP_SLOT, 8)], []])
        g = one(morph, [[(TEXTURE, 100)], [(CAP_SLOT, 8)], [(GRAIN, 40)]])
        changed = not np.array_equal(base, g)
        report(changed == should, f"grain: 40 ms on Slot 8 {'changes' if changed else 'leaves'} {heard}"
                                  f" ({'right' if changed == should else 'WRONG'})")
    report(np.array_equal(one(100, [[(TEXTURE, 100)], [], [(GRAIN, 40)]]),
                          one(100, [[(TEXTURE, 100)], [(CAP_SLOT, 8)], [(GRAIN, 40)]])),
           "grain: 40 ms on All == by hand on Slot 8")


if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()] or ["current"]
    for w in want:
        globals()[w]()
    print(f"--- {fails} failure(s)")
    sys.exit(1 if fails else 0)
