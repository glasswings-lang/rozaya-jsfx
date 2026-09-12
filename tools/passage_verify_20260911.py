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


FADE_IN, HOLD, FADE_OUT, GAP, T_UNIT_SLOT, XFADE_ON, AUTOMORPH = 21, 22, 23, 24, 25, 26, 35


def timing():
    # Auto-morph Sweep walks the eight slots a capture on All filled, so the legs are
    # heard. Unit and the four timings land on ONE stage (the unit is not a selector,
    # and a unit a stage early would play one leg in the wrong unit). 120 BPM: ysfx's.
    # Crossfade into next OFF: with it on (the default) a leg blends straight into the
    # next slot and IGNORES the gap, and eight identical captures blend inaudibly -- the
    # first version of this check could not fail for exactly that reason (2026-09-11).
    # Off, each leg is fade in, hold, fade out to silence, gap: all four shape the level.
    def legs(unit, fi, h, fo, g):
        return fresh_run(0, [[(AUTOMORPH, 1), (XFADE_ON, 0), (T_UNIT_SLOT, unit), (FADE_IN, fi), (HOLD, h),
                              (FADE_OUT, fo), (GAP, g)], *WAIT, [], []], seconds=18)
    sec = legs(0, 0.5, 1, 0.5, 1)
    report(np.abs(sec).max() > 0 and not np.array_equal(sec, legs(0, 0.5, 1, 0.5, 1.5)),
           "timing: a gap of 1.5 s instead of 1 changes the sound (the check can fail)")
    report(np.array_equal(sec, legs(2, 1, 2, 1, 2)), "timing: Beats 1, 2, 1, 2 at 120 BPM == Seconds 0.5, 1, 0.5, 1")
    report(np.array_equal(sec, legs(1, 2, 1, 2, 1)), "timing: Hz 2, 1, 2, 1 == Seconds 0.5, 1, 0.5, 1")
    report(np.array_equal(legs(0, 0.5, 1, 0.5, 0), legs(1, 2, 1, 2, 0)),
           "timing: a gap of 0 in Hz == a gap of 0 in Seconds (0 still means none)")


START_DELAY, PLAY_FOR, REST_FOR, TR_UNIT, OUT_AT_REST = 38, 39, 40, 41, 43


def transport():
    # Set once, two stages after the capture; the tail starts near 8.9 s and runs to
    # 22 s, so a 16 s delay (counted from when it is set) ends inside it.
    def tr(sets):
        return fresh_run(0, [list(sets), *WAIT, [], []], seconds=22)
    sec = tr([(START_DELAY, 16)])
    report(np.abs(sec).max() > 0 and not np.array_equal(sec, tr([(START_DELAY, 17)])),
           "transport: a start delay of 17 s instead of 16 changes the sound (the check can fail)")
    report(np.array_equal(sec, tr([(TR_UNIT, 2), (START_DELAY, 32)])), "transport: Start delay 32 beats at 120 BPM == 16 s")
    report(np.array_equal(sec, tr([(TR_UNIT, 1), (START_DELAY, 0.0625)])), "transport: Start delay 0.0625 Hz == 16 s")
    pr = tr([(PLAY_FOR, 1), (REST_FOR, 1)])
    report(not np.array_equal(pr, tr([])), "transport: Play for 1 s, Rest for 1 s changes the sound")
    report(np.array_equal(pr, tr([(TR_UNIT, 2), (PLAY_FOR, 2), (REST_FOR, 2)])),
           "transport: Play for and Rest for 2 beats at 120 BPM == 1 s")
    report(not np.array_equal(pr, tr([(PLAY_FOR, 1), (REST_FOR, 1), (OUT_AT_REST, 1)])),
           "transport: Output at rest Silence differs from Pass-through")


DRIFT_PUNIT, DRIFT_PLAY, DRIFT_REST = 49, 51, 52
RAMP_TARGET, RAMP_BY, RAMP_TUNIT, RAMP_DUR, RAMP_PLAY, RAMP_REST, RAMP_ENGAGE = 54, 55, 57, 58, 59, 60, 61


def driftramp():
    # Heard: Slot 1; everything set on All in ONE stage. Target 0 is Texture for both.
    def dr(sets):
        return fresh_run(0, [list(sets), *WAIT, [], []], seconds=22)
    d2 = dr([(DRIFT_UP, 40), (DRIFT_PERIOD, 2)])
    report(np.abs(d2).max() > 0 and not np.array_equal(d2, dr([(DRIFT_UP, 40), (DRIFT_PERIOD, 3)])),
           "drift: a period of 3 s instead of 2 changes the sound (the check can fail)")
    report(np.array_equal(d2, dr([(DRIFT_PUNIT, 2), (DRIFT_UP, 40), (DRIFT_PERIOD, 4)])),
           "drift: period 4 beats at 120 BPM == 2 s")
    report(not np.array_equal(d2, dr([(DRIFT_UP, 40), (DRIFT_PERIOD, 2), (DRIFT_PLAY, 1.3), (DRIFT_REST, 0.7)])),
           "drift: Play for 1.3 / Rest for 0.7 periods changes the sound")
    r15 = dr([(RAMP_BY, -40), (RAMP_DUR, 0.25), (RAMP_ENGAGE, 1)])
    report(np.abs(r15).max() > 0 and not np.array_equal(r15, dr([(RAMP_BY, -40), (RAMP_DUR, 0.5), (RAMP_ENGAGE, 1)])),
           "ramp: half a minute instead of a quarter changes the sound (the check can fail)")
    report(np.array_equal(r15, dr([(RAMP_TUNIT, 1), (RAMP_BY, -40), (RAMP_DUR, 15), (RAMP_ENGAGE, 1)])),
           "ramp: 15 seconds == a quarter of a minute")
    report(np.array_equal(r15, dr([(RAMP_TUNIT, 3), (RAMP_BY, -40), (RAMP_DUR, 30), (RAMP_ENGAGE, 1)])),
           "ramp: 30 beats at 120 BPM == a quarter of a minute")
    report(not np.array_equal(dr([(RAMP_TUNIT, 1), (RAMP_BY, -40), (RAMP_DUR, 15), (RAMP_ENGAGE, 1)]),
                              dr([(RAMP_TUNIT, 1), (RAMP_BY, -40), (RAMP_DUR, 15), (RAMP_PLAY, 1), (RAMP_REST, 1), (RAMP_ENGAGE, 1)])),
           "ramp: Play for 1 / Rest for 1 second changes the sound")


def cycles():
    # Rozaya kept Cycles: one walk through the active slots' legs. After a capture on All
    # every slot has the default fade in 1 + hold 4 + fade out 1 with crossfade on (the
    # gap is not part of a crossfading leg), so one walk is 8 x 6 = 48 s exactly, and
    # 0.0625 cycles is 3 s.
    def dr(sets):
        return fresh_run(0, [list(sets), *WAIT, [], []], seconds=22)
    in_seconds = dr([(DRIFT_UP, 40), (DRIFT_PERIOD, 3)])
    report(np.abs(in_seconds).max() > 0 and
           np.array_equal(in_seconds, dr([(DRIFT_PUNIT, 0), (DRIFT_UP, 40), (DRIFT_PERIOD, 0.0625)])),
           "cycles: a drift period of 0.0625 cycles (a 48 s walk) == 3 s")
    report(not np.array_equal(in_seconds, dr([(DRIFT_PUNIT, 0), (DRIFT_UP, 40), (DRIFT_PERIOD, 0.125)])),
           "cycles: 0.125 cycles (6 s) differs from 3 s (the check can fail)")


# --- A tempo change lands at once, mid-slot (2026-09-11). Rozaya: "a tempo change is
# meant to be a tempo change, not a delayed tempo change." The runner changes tempo at a
# block boundary (0.743 s here), so the change moment B is known exactly. Crossfade into
# next OFF, all eight slots captured alike, the walk on Sweep; edges found in 10 ms windows.
TSR, PRE_TEMPO = 44100, "45350c6"   # the last build before the fix
BLK_S = BLOCK / TSR


def tempo_run(plugin, settings, extra, seconds=30):
    stages = [[(AUDITION, 1), (MORPH, 0), (CAP_SLOT, 0)], [(CAPTURE, 1)], list(settings)]
    out = os.path.join(tmp, f"t{os.getpid()}_{abs(hash((plugin, str(settings), str(extra))))}.csv")
    cmd = [EXE, plugin, "--seconds", str(seconds), "--csv", out, "--quiet", *TONE, *extra]
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
    return a


def win(a, n=441):
    x = a[:len(a) // n * n, 0].reshape(-1, n)
    return np.abs(x).max(1), np.sqrt((x ** 2).mean(1))


def edges(a):
    on = win(a)[0] > 1e-4
    rise = [i * 0.01 for i in range(1, len(on)) if on[i] and not on[i - 1]]
    fall = [i * 0.01 for i in range(1, len(on)) if on[i - 1] and not on[i]]
    return rise, fall


def block_in(lo, hi):
    b = np.ceil(lo / BLK_S) * BLK_S
    if b > hi:
        raise RuntimeError("no block boundary in the window")
    return b


def tempo():
    old = pinned(subprocess.run(["git", "show", f"{PRE_TEMPO}:src/{FX}.jsfx"], cwd=ROOT, capture_output=True,
                                check=True).stdout.decode("utf-8"), "pre_tempo.jsfx")
    steady = ["--tempo", "120"]
    # Hold 8 beats, gap 4: at 120 BPM 4 s of sound, 2 s of silence.
    held = [(INPUT_LEVEL, -60), (AUTOMORPH, 1), (XFADE_ON, 0), (T_UNIT_SLOT,2), (FADE_IN, 0), (HOLD, 8), (FADE_OUT, 0), (GAP, 4)]
    ctl = tempo_run(NEW, held, steady)
    rise, _ = edges(ctl)
    r = next(t for t in rise if t > 8)
    b = block_in(r + 1.0, r + 3.0)
    change = steady + ["--tempo-at", f"{b - 0.000001:.6f}=60"]
    want_fall = b + 8 - 2 * (b - r)          # the beats left of the hold, at one beat a second
    for label, plugin, expect in (("fixed", NEW, want_fall), ("pre-fix", old, r + 8)):
        a = tempo_run(plugin, held, change)
        _, fall = edges(a)
        f = next(t for t in fall if t > b)
        nxt = next(t for t in edges(a)[0] if t > f)
        ok = abs(f - expect) < 0.02 and abs(nxt - (f + 4)) < 0.02
        report(ok if label == "fixed" else ok and abs(f - want_fall) > 0.5,
               f"tempo ({label}): 120 -> 60 BPM {b - r:.3f} s into an 8-beat hold ends it at {f:.2f} s "
               f"(beats say {want_fall:.2f}), and the 4-beat gap lasts {nxt - f:.2f} s")
    # A fade crossing the change: hold 2 beats, fade out 8, gap 4. No jump in level at B.
    # Texture 0: the wash flickers by up to 0.75 of full in 20 ms while merely holding,
    # which hid the jump entirely (measured 2026-09-11); the voice holds within 0.016.
    faded = [(TEXTURE, 0), (INPUT_LEVEL, -60), (AUTOMORPH, 1), (XFADE_ON, 0), (T_UNIT_SLOT,2), (FADE_IN, 0), (HOLD, 2), (FADE_OUT, 8), (GAP, 4)]
    ctl = tempo_run(NEW, faded, steady)
    r = next(t for t in edges(ctl)[0] if t > 8)
    b = block_in(r + 2.2, r + 3.8)
    change = steady + ["--tempo-at", f"{b - 0.000001:.6f}=60"]
    jumps = {}
    for label, plugin, extra in (("steady", NEW, steady), ("fixed", NEW, change), ("pre-fix", old, change)):
        rms = win(tempo_run(plugin, faded, extra), 882)[1]
        full = np.median(rms[int((r + 0.2) / 0.02):int((r + 0.9) / 0.02)])
        k = int(round(b / 0.02))
        jumps[label] = np.abs(np.diff(rms[k - 5:k + 6])).max() / full
    report(jumps["fixed"] < 0.05 and jumps["pre-fix"] > 0.15,
           f"tempo: the biggest level step (20 ms) where the tempo changes mid-fade: fixed "
           f"{jumps['fixed']:.3f}, steady tempo {jumps['steady']:.3f}, pre-fix {jumps['pre-fix']:.3f} of full")
    # Seconds ignores the tempo entirely.
    secs = [(INPUT_LEVEL, -60), (AUTOMORPH, 1), (XFADE_ON, 0), (T_UNIT_SLOT,0), (FADE_IN, 0.3), (HOLD, 4), (FADE_OUT, 0.7), (GAP, 2)]
    report(np.array_equal(tempo_run(NEW, secs, steady), tempo_run(NEW, secs, change)),
           "tempo: slots in Seconds are bit-identical through the same tempo change")


# --- The other Beats timings through the same tempo change (2026-09-11). A stage lands
# after block k and a --tempo-at lands before block k+1, so a Seconds length changed at
# stage K and a Beats length with the tempo changed at block K+1 meet on the same sample.
RAMP_DELAY = 62


def staged_run(plugin, settings, later, extra, seconds):
    stages = [[(AUDITION, 1), (MORPH, 0), (CAP_SLOT, 0)], [(CAPTURE, 1)], list(settings)] + [list(s) for s in later]
    out = os.path.join(tmp, f"s{os.getpid()}_{abs(hash((plugin, str(settings), str(later), str(extra))))}.csv")
    cmd = [EXE, plugin, "--seconds", str(seconds), "--csv", out, "--quiet", *TONE, *extra]
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
    return a


def beats():
    K = 6                        # the change lands with stage K: the start of block K+1
    B, t0 = (K + 1) * BLK_S, 3 * BLK_S   # settings land with stage 2
    steady = ["--tempo", "120"]
    change = steady + ["--tempo-at", f"{B - 0.000001:.6f}=60"]
    base = [(TEXTURE, 0), (INPUT_LEVEL, -60)]

    def later(at=()):
        return [[]] * (K - 3) + [list(at)] + [[]] * 3

    def first(times, after):
        return next((t for t in times if t > after), float("nan"))

    def edge_case(label, settings, which, beats_len, seconds):
        # 120 -> 60 BPM: the beats done before B, at two a second; the rest at one a second.
        say = B + (beats_len - 2 * (B - t0))
        ctl = first(edges(staged_run(NEW, settings, later(), steady, seconds))[which], t0 + 0.1)
        got = first(edges(staged_run(NEW, settings, later(), change, seconds))[which], t0 + 0.1)
        report(abs(ctl - (t0 + beats_len / 2)) < 0.02 and abs(got - say) < 0.02,
               f"beats: {label} -- steady ends {ctl:.2f} s (beats say {t0 + beats_len / 2:.2f}); through "
               f"120 -> 60 at {B:.2f} s it ends {got:.2f} s (beats say {say:.2f}; counted in seconds {t0 + beats_len:.2f})")

    rest_silent = base + [(OUT_AT_REST, 1), (TR_UNIT, 2)]
    edge_case("Start delay 16 beats", rest_silent + [(START_DELAY, 16)], 0, 16, 22)
    edge_case("Play for 8 beats (Rest 4)", rest_silent + [(PLAY_FOR, 8), (REST_FOR, 4)], 1, 8, 16)

    # Ramp start delay: when the render first differs from the same ramp left disengaged.
    ramp = base + [(RAMP_TUNIT, 3), (RAMP_BY, 80), (RAMP_DUR, 4), (RAMP_DELAY, 16)]

    def diverge(extra):
        a = staged_run(NEW, ramp + [(RAMP_ENGAGE, 1)], later(), extra, 22)
        z = staged_run(NEW, ramp, later(), extra, 22)
        d = np.nonzero(np.abs(a - z).max(1) > 1e-7)[0]
        return d[0] / TSR if len(d) else float("nan")
    say = B + (16 - 2 * (B - t0))
    ctl, got = diverge(steady), diverge(change)
    report(abs(ctl - (t0 + 8)) < 0.02 and abs(got - say) < 0.02,
           f"beats: Ramp start delay 16 beats -- steady starts {ctl:.2f} s (beats say {t0 + 8:.2f}); through "
           f"120 -> 60 at {B:.2f} s it starts {got:.2f} s (beats say {say:.2f}; counted in seconds {t0 + 16:.2f})")

    # Drift period and Ramp duration accumulate, so they can be held to bit-identity.
    drift_b = staged_run(NEW, base + [(DRIFT_PUNIT, 2), (DRIFT_UP, 40), (DRIFT_PERIOD, 4)], later(), change, 16)
    drift_s = staged_run(NEW, base + [(DRIFT_PUNIT, 1), (DRIFT_UP, 40), (DRIFT_PERIOD, 2)], later([(DRIFT_PERIOD, 4)]), steady, 16)
    drift_f = staged_run(NEW, base + [(DRIFT_PUNIT, 1), (DRIFT_UP, 40), (DRIFT_PERIOD, 2)], later(), steady, 16)
    report(np.array_equal(drift_b, drift_s) and not np.array_equal(drift_s, drift_f) and np.abs(drift_b).max() > 0,
           "beats: Drift period 4 beats through 120 -> 60 == 2 s changed to 4 s at that moment (and != staying at 2 s)")
    rb = base + [(RAMP_BY, 80), (RAMP_ENGAGE, 1)]
    ramp_b = staged_run(NEW, rb + [(RAMP_TUNIT, 3), (RAMP_DUR, 24)], later(), change, 16)
    ramp_s = staged_run(NEW, rb + [(RAMP_TUNIT, 1), (RAMP_DUR, 12)], later([(RAMP_DUR, 24)]), steady, 16)
    ramp_f = staged_run(NEW, rb + [(RAMP_TUNIT, 1), (RAMP_DUR, 12)], later(), steady, 16)
    report(np.array_equal(ramp_b, ramp_s) and not np.array_equal(ramp_s, ramp_f) and np.abs(ramp_b).max() > 0,
           "beats: Ramp duration 24 beats through 120 -> 60 == 12 s changed to 24 s at that moment (and != staying at 12 s)")


# --- Cold load with the transport STOPPED (2026-09-12). The Morpher stayed silent until the
# first play when saved on the starting Capture point and Capture average; Passage has the
# same code. Every live instance: the pre-layout build (PRE) on the project, stopped, against
# the new build on its temp conversion, stopped -- the new must sound wherever the same
# instance sounds playing. Rozaya: "on project load, to walk into silence? cmmon".
def coldload():
    jobs = []
    for live in mig.files():
        text, n = mig.convert(live)
        conv = os.path.join(tmp, "c-" + re.sub(r"[/\\: ']", "_", live))
        open(conv, "w", encoding="utf-8", errors="surrogateescape", newline="").write(text)
        jobs += [(live, conv, i) for i in range(1, n + 1)]
    tail = slice(3 * 44100, None)
    rms = lambda a: float(np.sqrt((a[tail] ** 2).mean()))

    def one(j):
        live, conv, i = j
        quiet_in = ()   # SILENT input: a noise in passes through and reads as "sounds stopped"
        play = rms(run(NEW, 8, conv, i, quiet_in))
        old_stop = rms(run(OLD, 8, live, i, quiet_in + ("--stopped",)))
        new_stop = rms(run(NEW, 8, conv, i, quiet_in + ("--stopped",)))
        return live, i, play, old_stop, new_stop

    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(one, jobs))
    sounding = [r for r in res if r[2] > 1e-6]
    silent_new = [r for r in sounding if r[4] <= 1e-6]
    silent_old = [r for r in sounding if r[3] <= 1e-6]
    for live, i, *_ in silent_new:
        report(False, f"coldload: {live} #{i} is silent stopped though it sounds playing")
    report(len(sounding) > 0 and not silent_new,
           f"coldload: all {len(sounding)} of {len(res)} instances that sound playing also sound stopped (new build)")
    print(f"     (the pre-layout build was silent stopped in {len(silent_old)} of them)")


if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()] or ["current"]
    for w in want:
        globals()[w]()
    print(f"--- {fails} failure(s)")
    sys.exit(1 if fails else 0)
