#!/usr/bin/env python3
"""Spectral Vowel Morpher's pitch layout, measured, stage by stage.
docs/layouts/spectral-vowel-morpher.md, "THE PITCH LAYOUT".

Renders run TEST COPIES with the per-load rand() scramble pinned (as every Morpher and
Passage tool does); the shipped plugin keeps its scramble.

current   every live instance on the 51-slider layout: the pre-layout build (PRE) on the
          project as it is == the new build on a temp copy converted by
          morpher_migrate_20260913.convert, 8 s of SILENCE in, so what sounds is the
          plugin's own voice and wash (the Morpher passes its input through, and a noise
          input once made silent copies read as sounding). Live files are never written.

    python tools/morpher_verify_20260913.py [section ...] [--jobs N]
"""
import concurrent.futures as cf, os, re, subprocess, sys, tempfile
import numpy as np

# Idle priority, inherited by every render it starts: parallel renders at normal priority
# made NVDA lag (memory, "Heavy renders at Idle priority").
if os.name == "nt":
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_migrate_20260913 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "spectral_vowel_morpher"
PRE = "693c3ad"      # the last commit before the layout work began
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
_n = 0


def run(plugin, seconds, rpp=None, inst=1, stages=(), extra=()):
    global _n
    _n += 1
    out = os.path.join(tmp, f"o{_n}_{os.getpid()}_{abs(hash((plugin, rpp, inst, str(stages))))}.csv")
    cmd = [EXE, plugin, "--seconds", str(seconds), "--csv", out, "--quiet", *extra]
    if rpp:
        cmd += ["--rpp", rpp, "--fx", FX, "--instance", str(inst)]
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


def current():
    jobs = []
    for live in mig.files():
        if not mig.is_current_layout(live):
            continue
        text, n = mig.convert(live)
        conv = os.path.join(tmp, "m-" + re.sub(r"[/\\: ']", "_", live))
        open(conv, "w", encoding="utf-8", errors="surrogateescape", newline="").write(text)
        jobs += [(live, conv, i) for i in range(1, n + 1)]

    def one(j):
        live, conv, i = j
        a = run(OLD, 8, live, i)
        b = run(NEW, 8, conv, i)
        return live, i, np.array_equal(a, b), float(np.abs(a).max())

    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(one, jobs))
    for live, i, eq, mx in res:
        if not eq:
            report(False, f"{live} #{i}: differs")
    same = sum(r[2] for r in res)
    sounding = sum(r[3] > 0 for r in res)
    report(same == len(res) and len(res) == 123,
           f"current: {same} of {len(res)} instances bit-identical; {sounding} sound with silence in")


# --- Fresh instances. A tone in, blocks of ~0.74 s so a capture hears real audio; the heard
# slot never changes inside a comparison (a slot change hands the voice phases over, which
# alone moves the render). A selector is set one stage BEFORE the value it governs, and both
# sides of a comparison run the same number of stages (jsfx_run README). Slider numbers are
# the 2026-09-13 layout's.
BLOCK = 32768
TONE = ("--input", "sine", "--input-hz", "220", "--input-db", "-6", "--block", str(BLOCK))
CAP_SLOT, CAPTURE, AUDITION, MORPH, TEXTURE = 1, 2, 5, 6, 10
SRC, SRC_FINE, SRC_FUNIT, TARGET, TRANSPOSE, T_UNIT, FINE, F_UNIT, TUNING = 13, 14, 15, 16, 17, 18, 19, 20, 21
WAIT = [[]] * 5


def fresh(steps, seconds=16, first=((AUDITION, 0), (CAP_SLOT, 1))):
    stages = [list(first), [(CAPTURE, 1)]] + [list(s) for s in steps] + list(WAIT)
    a = run(NEW, seconds, stages=stages, extra=TONE)
    return a[(len(stages) + 2) * BLOCK:]


def pitch():
    # Heard: Slot 1 on Focused slot, captured into Slot 1.
    base12 = fresh([[], [(TRANSPOSE, 12)]])
    untouched = fresh([[], []])
    report(not np.array_equal(base12, untouched) and np.abs(base12).max() > 0,
           "pitch: Transpose 12 changes the sound (the check can fail)")
    for label, steps in (("1200 cents", [[(T_UNIT, 2)], [(TRANSPOSE, 1200)]]),
                         ("440 Hz from a 440 reference", [[(T_UNIT, 0)], [(TRANSPOSE, 440)]]),
                         ("880 Hz from an 880 reference", [[(T_UNIT, 0), (TUNING, 880)], [(TRANSPOSE, 880)]]),
                         ("11 semitones + Fine tune 100 cents", [[], [(FINE, 100), (TRANSPOSE, 11)]]),
                         ("11 semitones + Fine tune 1 semitone", [[(F_UNIT, 1)], [(FINE, 1), (TRANSPOSE, 11)]])):
        report(np.array_equal(fresh(steps), base12), f"pitch: {label} == Transpose 12 semitones")
    by_note = fresh([[(SRC, 61)], [(TARGET, 64)]])
    report(np.array_equal(by_note, fresh([[(SRC, 61)], [(TRANSPOSE, 4)]])),
           "pitch: Source C4, Target E4 == Transpose 4")
    report(not np.array_equal(by_note, untouched), "pitch: Source C4, Target E4 changes the sound")
    flat = fresh([[(SRC, 61), (SRC_FINE, -50)], [(TARGET, 64)]])
    report(np.array_equal(flat, fresh([[(SRC, 61), (SRC_FINE, -50)], [(TRANSPOSE, 4.5)]])),
           "pitch: Source C4 50 cents flat, Target E4 == Transpose 4.5")
    # Moving Source note never changes the sound; it re-reads Target note.
    moved_src = fresh([[(TRANSPOSE, 4)], [(SRC, 63)]])
    report(np.array_equal(moved_src, fresh([[(TRANSPOSE, 4)], []])),
           "pitch: moving Source note with Transpose 4 set leaves the sound alone")
    # Tuning reference alone, in Semitones, is not heard.
    report(np.array_equal(fresh([[], [(TUNING, 432)]]), untouched),
           "pitch: Tuning reference 432 in Semitones changes nothing")


LAYER, L_ACTIVE, L_PITCH, L_PUNIT, L_FINE, L_FUNIT, L_LEVEL, L_SOLO = 29, 30, 31, 32, 33, 34, 35, 36
WASH = ((AUDITION, 0), (CAP_SLOT, 1), (TEXTURE, 100))


def layers():
    # Wash only where two DIFFERENT layers are compared: each layer's voice has its own
    # random starting phases, the wash does not.
    untouched = fresh([[], []])
    l1 = fresh([[(LAYER, 1)], [(L_PITCH, 12)]])
    report(np.array_equal(l1, fresh([[(LAYER, 1)], [(TRANSPOSE, 12)]])) and not np.array_equal(l1, untouched),
           "layers: Layer 1 (the Original) pitch 12 == Transpose 12, and changes the sound")
    wash = fresh([[], []], first=WASH)
    l2 = fresh([[(LAYER, 2)], [(L_LEVEL, 0)]], first=WASH)
    report(np.array_equal(l2, fresh([[(LAYER, 14)], [(L_PITCH, -48), (L_LEVEL, 0)]], first=WASH))
           and not np.array_equal(l2, wash),
           "layers: Layer 2 raised (starts 4 octaves down) == Layer 14 pitched -48, and is heard")
    # The authored order: Layer 2 -48, 3 -36, 4 -24, 5 -12, 6 -7, 7 -5, 8 +5, 9 +7, 10 +12.
    six = fresh([[(LAYER, 6)], [], [(L_LEVEL, 0)]], first=WASH)
    report(np.array_equal(fresh([[(LAYER, 6)], [(L_PUNIT, 2)], [(L_PITCH, -700), (L_LEVEL, 0)]], first=WASH), six)
           and not np.array_equal(six, fresh([[(LAYER, 5)], [], [(L_LEVEL, 0)]], first=WASH)),
           "layers: Layer 6 at -700 cents == Layer 6 as it starts (a fifth down), which is not Layer 5")
    fourteen12 = fresh([[(LAYER, 14)], [], [(L_PITCH, 12), (L_LEVEL, 0)]], first=WASH)
    report(np.array_equal(fresh([[(LAYER, 14)], [], [(L_FINE, 100), (L_PITCH, 11), (L_LEVEL, 0)]], first=WASH), fourteen12),
           "layers: Layer 14 at 11 semitones + fine tune 100 cents == 12 semitones")
    report(np.array_equal(fresh([[(LAYER, 14)], [(L_PUNIT, 0)], [(L_PITCH, 440), (L_LEVEL, 0)]], first=WASH), fourteen12),
           "layers: Layer 14 at 440 Hz from a 440 reference == 12 semitones")
    on_all = fresh([[(LAYER, 0)], [(L_PITCH, 7)]])
    report(np.array_equal(on_all, fresh([[(LAYER, 0)], [(TRANSPOSE, 7)]])),
           "layers: Layer pitch 7 on All (only Layer 1 sounds) == Transpose 7")
    # On All the level shows Layer 1's 0 dB, so it must MOVE to be written: -1, then 0.
    all_up = fresh([[(LAYER, 0)], [(L_LEVEL, -1)], [(L_LEVEL, 0)]], first=WASH)
    two_up = fresh([[(LAYER, 2)], [(L_LEVEL, -1)], [(L_LEVEL, 0)]], first=WASH)
    report(not np.array_equal(all_up, two_up) and not np.array_equal(all_up, fresh([[], [], []], first=WASH)),
           "layers: Layer level to 0 dB on All is more than Layer 1, and more than Layers 1 and 2")
    v = listed([[(LAYER, 0)], [(L_LEVEL, -1)], [(L_LEVEL, 0)], [(LAYER, 16)]])
    report(v[35] == 0 and v[31] == -24, f"layers: after All, Layer 16 reads level 0 and its own pitch -24 (read {v[35]}, {v[31]})")
    via = fresh([[(LAYER, 14)], [(L_PITCH, 5), (L_LEVEL, 0)], [(LAYER, 0)], [], [(LAYER, 14)]], first=WASH)
    direct = fresh([[(LAYER, 14)], [(L_PITCH, 5), (L_LEVEL, 0)], [], [], []], first=WASH)
    report(np.array_equal(via, direct), "layers: passing through All keeps Layer 14's own pitch and level")
    # Read back, not heard: on All a moved fine tune reaches every layer and nothing else does.
    v = listed([[(LAYER, 14)], [(L_PITCH, 5), (L_LEVEL, -6)], [(LAYER, 0)], [(L_FINE, 30)], [(LAYER, 14)]])
    report(v[31] == 5 and v[35] == -6 and v[33] == 30,
           f"layers: on All, Fine tune 30 reached Layer 14 and left its pitch and level (read {v[31]}, {v[35]}, {v[33]})")
    v = listed([[(LAYER, 0)], [(L_FINE, 30)], [(LAYER, 10)]])
    report(v[31] == 12 and v[33] == 30,
           f"layers: Layer 10 starts an octave up and took All's fine tune (read {v[31]}, {v[33]})")
    starts = [listed([[(LAYER, k)]])[31] for k in range(1, 17)]
    report(starts == [0, -48, -36, -24, -12, -7, -5, 5, 7, 12, 24, 36, 48, -12, 12, -24],
           f"layers: Layers 1-16 start at the authored pitches (read {starts})")


def listed(stages):
    """Every control's value at the end of a staged run on a fresh instance."""
    cmd = [EXE, NEW, "--seconds", "1", "--list"]
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    out = {}
    for line in r.stdout.splitlines():
        m = re.match(r"\s*slider(\d+)\s.*\]\s*=\s*(-?[\d.]+)", line)
        if m:
            out[int(m.group(1))] = float(m.group(2))
    return out


if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()] or ["current"]
    for name in want:
        globals()[name]()
    print(f"{fails} failures")
    sys.exit(1 if fails else 0)
