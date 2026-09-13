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
    # The handle types must be declared: left to ctypes' default int, the 64-bit pseudo-handle
    # was passed wrongly and the call silently did nothing (2026-09-13, renders seen at Normal).
    _k32 = ctypes.windll.kernel32
    _k32.GetCurrentProcess.restype = ctypes.c_void_p
    _k32.SetPriorityClass.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    if not _k32.SetPriorityClass(_k32.GetCurrentProcess(), 0x40):
        print("warning: could not set Idle priority; renders will run at Normal", flush=True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_migrate_20260913 as mig
from rpp_sliders import parse_line, render_line

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


# --- The 87-target list (stage 4).
LADDER = ["4 octaves down", "3 octaves down", "2 octaves down", "1 octave down", "a fifth down", "a fourth down",
          "Original (unison)", "a fourth up", "a fifth up", "1 octave up", "2 octaves up", "3 octaves up",
          "4 octaves up", "Custom 1", "Custom 2", "Custom 3"]
OLD55 = (["Morph", "Auto-morph time", "Texture", "Wash grain", "Spread", "Pitch", "Stereo width", "Denoise",
          "Low cut", "High cut", "Overtone harmonic", "Overtone lift", "Overtone width", "Layer level (all layers)"]
         + [f"{x} level" for x in LADDER] + ["Layer pitch (all Custom layers)", "Custom 1 pitch", "Custom 2 pitch",
                                             "Custom 3 pitch", "Layer overtone harmonic (all layers)"]
         + [f"{x} overtone harmonic" for x in LADDER] + ["Input level", "Output level", "Play for", "Rest for"])
# The authored layer order: the Original is Layer 1, the six below it 2-7, the six above 8-13, Custom 14-16.
LAYER_OF = {x: (1 if i == 6 else i + 2 if i < 6 else i + 1) for i, x in enumerate(LADDER)}
AUTH87 = (["Morph", "Auto-morph time", "Texture", "Wash grain", "Spread", "Transpose", "Fine tune", "Tuning reference",
           "Stereo width", "Denoise", "Low cut", "High cut", "Overtone harmonic", "Overtone lift", "Overtone width",
           "Layer pitch (all layers)"] + [f"Layer {k} pitch" for k in range(1, 17)]
          + ["Layer fine tune (all layers)"] + [f"Layer {k} fine tune" for k in range(1, 17)]
          + ["Layer level (all layers)"] + [f"Layer {k} level" for k in range(1, 17)]
          + ["Layer overtone harmonic (all layers)"] + [f"Layer {k} overtone harmonic" for k in range(1, 17)]
          + ["Input level", "Output level", "Play for", "Rest for"])


def renamed(old):
    """What an old target is called now -- written from the layout doc, not from the tools."""
    if old == "Pitch":
        return "Transpose"
    if old == "Layer pitch (all Custom layers)":
        return "Layer pitch (all layers)"
    if old.startswith("Custom ") and old.endswith(" pitch"):
        return f"Layer {13 + int(old.split()[1])} pitch"
    for x in LADDER:
        for kind in ("level", "overtone harmonic"):
            if old == f"{x} {kind}":
                return f"Layer {LAYER_OF[x]} {kind}"
    return old


def names():
    src = open(os.path.join(ROOT, "src", f"{FX}.jsfx"), encoding="utf-8").read()
    for sid in (46, 56):
        m = re.search(rf"^slider{sid}:0<0,86,1{{(.*?)}}>", src, re.M)
        report(bool(m) and m.group(1).split(",") == AUTH87, f"names: slider {sid}'s 87 names are the authored list")
    # The migration's selector remap, read through a converted line: every old target lands on its own name.
    live = next(p for p in mig.files() if mig.is_current_layout(p))
    L = open(live, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    base = L[mig.heads(L)[0] + 1]
    bad = []
    for o, name in enumerate(OLD55):
        s = parse_line(base)
        s[35], s[44] = str(o), str(o)
        new = parse_line(mig.remap_line(render_line(base, s, 51), "synthetic"))
        got = {AUTH87[int(new[46])], AUTH87[int(new[56])]}
        if got != {renamed(name)}:
            bad.append(f"{name} -> {got}")
    report(not bad, f"names: all 55 old targets keep their name through the line migration {bad[:3]}")


DT, DUP, DPER, RT = 46, 47, 50, 56
# Defined here, before the module-level lists below (SAVE_STAGES, SCOPE) that use them.
DDOWN, DUNIT, RBY, RUNIT, RDUR, RENG = 48, 49, 57, 58, 60, 63
LOW_CUT, SPREAD = 24, 12


def targets():
    # Each new target, by drift, changes the sound and stays finite. A layer is raised first
    # (-1 then 0 dB, since it must MOVE to be written) so its pitch can be heard.
    cases = [(6, "Fine tune", 60, [], []),
             (7, "Tuning reference", 100, [(T_UNIT, 0)], [(TRANSPOSE, 50)]),
             (8, "Stereo width (moved from 6)", 40, [], []),
             (84, "Output level (moved from 52)", 6, [], []),
             (15, "Layer pitch (all layers)", 3, [], []),
             (16, "Layer 1 pitch", 3, [], []),
             (18, "Layer 3 pitch", 3, [(LAYER, 3)], [(L_LEVEL, -1)]),
             (31, "Layer 16 pitch", 3, [(LAYER, 16)], [(L_LEVEL, -1)]),
             (32, "Layer fine tune (all layers)", 60, [], []),
             (33, "Layer 1 fine tune", 60, [], []),
             (40, "Layer 8 fine tune", 60, [(LAYER, 8)], [(L_LEVEL, -1)])]

    def one(c):
        tg, label, amt, first, second = c
        raise_lvl = [(L_LEVEL, 0)] if any(s == LAYER for s, _ in first) else []
        steps_off = [first + [(DT, tg)], second, raise_lvl]
        steps_on = [first + [(DT, tg)], second, raise_lvl + [(DUP, amt), (DPER, 1.3)]]
        a, b = fresh(steps_off), fresh(steps_on)
        return label, not np.array_equal(a, b) and np.isfinite(b).all() and np.abs(b).max() > 0
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for label, ok in ex.map(one, cases):
            report(ok, f"targets: a drift on {label} changes the sound, finite")
    # An "all layers" entry reaches more than Layer 1: Layers 1 and 3 up, pitch drifting.
    base = [[(LAYER, 3)], [(L_LEVEL, -1)], [(L_LEVEL, 0)]]
    all_p = fresh([[(LAYER, 3), (DT, 15)], [(L_LEVEL, -1)], [(L_LEVEL, 0), (DUP, 3), (DPER, 1.3)]])
    one_p = fresh([[(LAYER, 3), (DT, 16)], [(L_LEVEL, -1)], [(L_LEVEL, 0), (DUP, 3), (DPER, 1.3)]])
    report(not np.array_equal(all_p, one_p) and not np.array_equal(all_p, fresh(base)),
           "targets: Layer pitch (all layers) moves Layer 3 as well as Layer 1")


def blob_of(path, inst=1):
    import base64, struct
    L = open(path, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    hi = mig.heads(L)[inst - 1]
    j = hi + 1
    while "<JS_SER" not in L[j]:
        j += 1
    k = j + 1
    while L[k].strip() != ">":
        k += 1
    raw = base64.b64decode("".join(x.strip() for x in L[j + 1:k]))
    return L, hi, j, k, list(struct.unpack("<%df" % (len(raw) // 4), raw))


def write_project(path, L, hi, j, k, vals, line_fn):
    import base64, struct
    b = base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode()
    ind = L[j + 1][: len(L[j + 1]) - len(L[j + 1].lstrip())]
    eol = "\r\n" if L[j + 1].endswith("\r\n") else "\n"
    L2 = list(L)
    L2[hi + 1] = line_fn(L[hi + 1])
    L2[j + 1:k] = [ind + b[x:x + 128] + eol for x in range(0, len(b), 128)]
    open(path, "w", encoding="utf-8", errors="surrogateescape", newline="").write("".join(L2))


def fmt(x):
    return str(int(x)) if float(x) == int(x) else repr(round(float(x), 6))


def blobs():
    # Every live copy's blob is an older format (7700008-7700011) holding the 24-target list:
    # the line was moved to 55 on 2026-09-11 and the blob is remapped as it loads. So a real one
    # with two or more captures gets drift and ramp written into all 24 targets (every shape,
    # Random included), and the whole chain is walked: 24 -> 55 in both builds, then 55 -> 87
    # and the ladder -> Layer 1-16 in the new one. Pre-layout build on the project == new build
    # on the migrated line. Wide amounts, so every target is really moving.
    found = None
    for p in mig.files():
        if not mig.is_current_layout(p):
            continue
        L = open(p, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
        for n in range(1, len(mig.heads(L)) + 1):
            v = blob_of(p, n)[4]
            if v[0] in (7700011.0, 7700010.0, 7700008.0) and v[2] >= 2:
                found = (p, n, v[0])
                break
        if found:
            break
    report(bool(found), f"blobs: a 24-target instance with two captures to craft from: {found}")
    if not found:
        return
    p, n, magic = found
    L, hi, j, k, v = blob_of(p, n)
    W = 24
    off = 3 + int(v[2]) * 32768
    mod = list(v)
    for tt in range(W):
        mod[off + tt] = 0.4 + 0.1 * (tt % 7)             # up
        mod[off + W + tt] = 0.3 + 0.05 * (tt % 5)        # down
        mod[off + 2 * W + tt] = 1.3 + 0.2 * (tt % 5)     # period, seconds
        mod[off + 3 * W + tt] = tt % 3                   # Sine, Triangle, Random
    mod[off + 4 * W] = 23                                # remembered drift target: Custom 3 level (24-list)
    r0 = off + 4 * W + 1
    for tt in range(0, W, 3):
        mod[r0 + tt] = 2.0                               # ramp by
        mod[r0 + W + tt] = 4.0                           # duration, seconds (below)
    mod[r0 + 3 * W] = 2                                  # remembered ramp target: Pitch (24-list)

    def old_line(line):
        s = parse_line(line)
        s[35], s[44] = "29", "5"                         # the same two, in the 55-list the line holds
        s[36], s[37], s[38], s[40] = fmt(mod[off + 23]), fmt(mod[off + W + 23]), fmt(mod[off + 2 * W + 23]), fmt(mod[off + 3 * W + 23])
        s[45], s[47] = fmt(mod[r0 + 2]), fmt(mod[r0 + W + 2])
        s[39], s[46], s[50], s[10] = "1", "1", "1", "60"
        return render_line(line, s, 51)
    po, pn, pc = (os.path.join(tmp, f"b24{x}.RPP") for x in "onc")
    write_project(po, L, hi, j, k, mod, old_line)
    write_project(pn, L, hi, j, k, mod, lambda ln: mig.remap_line(old_line(ln), "synthetic"))
    write_project(pc, L, hi, j, k, v, old_line)
    a, b, c = run(OLD, 12, po, n), run(NEW, 12, pn, n), run(OLD, 12, pc, n)
    same, matters = np.array_equal(a, b), not np.array_equal(a, c)
    report(same and matters and np.abs(a).max() > 0,
           f"blobs: {os.path.basename(p)} #{n} ({magic:.0f}), drift and ramp on all 24 old targets: "
           f"loads bit-identical {same}; they matter {matters}")
    got = listed_rpp(pn, n)
    report(got[46] == 65 and got[56] == 5,
           f"blobs: the migrated copy shows Drift target Layer 16 level and Ramp target Transpose (read {got[46]}, {got[56]})")
    CRAFT.update(old=po, inst=n)


CRAFT = {}

# --- The save format, magic 7700087 (stage 6). A view is the stages that bring a layer or target
# onto the controls; a view reached after a save and reopen must list every control exactly as
# the same view reached in one sitting. The build before the save format (git HEAD while stage 6
# is uncommitted) reads none of it: the check can fail.
PRE_SAVE = os.environ.get("MORPHER_PRE_SAVE", "HEAD")
SAVE_STAGES = [
    [(LAYER, 14)],
    [(L_PUNIT, 2), (L_FINE, 30), (L_FUNIT, 0), (L_LEVEL, -6)],
    [(L_PITCH, 70)],
    [(LAYER, 3)],
    [(L_PITCH, -20), (L_FUNIT, 1), (L_FINE, 0.5)],
    [(DT, 16)],
    [(DUNIT, 3), (DUP, 25), (DPER, 2)],
    [(RT, 33)],
    [(RUNIT, 1), (RBY, 4), (RDUR, 1)],
    [(SRC, 61), (FINE, 12), (F_UNIT, 2), (TUNING, 432)],
    [(TARGET, 64)],
]
VIEWS = {"as saved": [],
         "Layer 14": [[(LAYER, 14)]],
         "Layer 3, Drift Layer 1 pitch, Ramp Layer 1 fine tune": [[(LAYER, 3)], [(DT, 16)], [(RT, 33)]],
         "Layer 16": [[(LAYER, 16)]]}


def listing(plugin, stages, rpp=None, inst=1):
    cmd = [EXE, plugin, "--list", "--seconds", "0.2"] + (["--rpp", rpp, "--fx", FX, "--instance", str(inst)] if rpp else [])
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    return {int(m[1]): float(m[2]) for m in re.finditer(r"^\s*slider(\d+)\s.*= (\S+)", r.stdout, re.M)}


def saveformat():
    pre = pinned(subprocess.run(["git", "show", f"{PRE_SAVE}:src/{FX}.jsfx"], cwd=ROOT, capture_output=True,
                                check=True).stdout.decode("utf-8"), "pre_save.jsfx")
    for end, tail in (("Layer 3", []), ("All", [[(LAYER, 0)]])):
        stages = SAVE_STAGES + tail
        s = os.path.join(tmp, f"sv-{end.replace(' ', '')}.RPP")
        save(NEW, stages, s)
        report(blob_of(s, 1)[4][0] == 7700087.0, f"save: saved on {end}, the blob is 7700087")
        for vname, view in VIEWS.items():
            want = listing(NEW, stages + view)
            got = listing(NEW, view, rpp=s)
            diff = sorted(k for k in want if k != CAPTURE and want[k] != got.get(k))
            report(not diff and len(want) == mig.N_NEW,
                   f"save: saved on {end}, reopened, {vname}: {len(want) - 1} controls as before the save"
                   + (f" -- DIFFER at sliders {diff}" if diff else ""))
        view = VIEWS["Layer 14"]
        want = listing(NEW, stages + view)
        old = listing(pre, view, rpp=s)
        report(any(want[k] != old.get(k) for k in (L_PITCH, L_PUNIT, L_FINE, L_FUNIT)),
               f"save: saved on {end}, the build before the save format reopens Layer 14 without its pitch (the check can fail)")
        s2 = os.path.join(tmp, f"sv2-{end.replace(' ', '')}.RPP")
        save(NEW, [], s2, rpp=s)
        report(open(s, "rb").read() == open(s2, "rb").read(),
               f"save: saved on {end}, reopened and saved again: the second save is byte-identical to the first")


def savedlive():
    # Every live copy, converted, then saved once in 7700087: it must render exactly as the
    # converted project does. The old-save path (every remap) meeting the new one.
    jobs = []
    for live in mig.files():
        text, n = mig.convert(live)
        conv = os.path.join(tmp, "sl-" + re.sub(r"[/\\: ']", "_", live))
        open(conv, "w", encoding="utf-8", errors="surrogateescape", newline="").write(text)
        jobs += [(live, conv, i) for i in range(1, n + 1)]

    def one(j):
        live, conv, i = j
        sv = os.path.join(tmp, f"sl{i}-" + os.path.basename(conv))
        save(NEW, [], sv, rpp=conv, inst=i, seconds=0.05)
        a = run(NEW, 8, conv, i)
        b = run(NEW, 8, sv, 1)
        return live, i, np.array_equal(a, b), float(np.abs(b).max())

    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(one, jobs))
    for live, i, eq, _ in res:
        if not eq:
            report(False, f"savedlive: {live} #{i}: differs after a save")
    same = sum(r[2] for r in res)
    report(same == len(res) == 135 and all(r[3] > 0 for r in res),
           f"savedlive: {same} of {len(res)} converted copies render bit-identical after one save in 7700087")


# --- Which kind each control is (R25), measured through jsfx_run the way
# tools/selector_scope_probe.py does it live: set a value on one option, switch, read; switch
# back, read. PER = it read something else on the other option and its own value back; ALL = it
# read its own value on the other option too. Never read off a label. Options compared are real
# ones on both sides (a selector with All at 0 cannot be measured against 0: session-log
# 2026-09-13). control -> (a value unlike its default, selector, option a, option b, the kind named)
DRIFT_PLAY, DRIFT_REST, DSHAPE, DPUNIT, DRESTART = 53, 54, 52, 51, 55
RPLAY, RREST, RTUNIT, RDELAY = 61, 62, 59, 64
SCOPE = {3: (40, CAP_SLOT, 1, 2, "per slot"), 4: (3, CAP_SLOT, 1, 2, "all slots"),
         30: (0, LAYER, 1, 2, "per layer"), 31: (7, LAYER, 1, 2, "per layer"), 32: (2, LAYER, 1, 2, "per layer"),
         33: (25, LAYER, 1, 2, "per layer"), 34: (1, LAYER, 1, 2, "per layer"), 35: (-9, LAYER, 1, 2, "per layer"),
         36: (1, LAYER, 1, 2, "per layer"), 37: (5, LAYER, 1, 2, "per layer"), 38: (4, LAYER, 1, 2, "per layer"),
         DUP: (5, DT, 2, 3, "per target"), DDOWN: (6, DT, 2, 3, "per target"), DUNIT: (3, DT, 2, 3, "per target"),
         DPER: (12, DT, 2, 3, "per target"), DPUNIT: (2, DT, 2, 3, "all targets"), DSHAPE: (2, DT, 2, 3, "per target"),
         DRIFT_PLAY: (3, DT, 2, 3, "per target"), DRIFT_REST: (1, DT, 2, 3, "per target"),
         DRESTART: (1, DT, 2, 3, "all targets"),
         RBY: (3, RT, 2, 3, "per target"), RUNIT: (1, RT, 2, 3, "per target"), RTUNIT: (1, RT, 2, 3, "all targets"),
         RDUR: (4, RT, 2, 3, "per target"), RPLAY: (2, RT, 2, 3, "per target"), RREST: (3, RT, 2, 3, "per target"),
         RENG: (1, RT, 2, 3, "all targets"), RDELAY: (1.5, RT, 2, 3, "per target")}


def scope():
    def one(item):
        ctl, (a, sel, o0, o1, kind) = item
        on_other = listing(NEW, [[(sel, o0)], [(ctl, a)], [(sel, o1)]])[ctl]
        back = listing(NEW, [[(sel, o0)], [(ctl, a)], [(sel, o1)], [(sel, o0)]])[ctl]
        got = "PER" if on_other != a and back == a else "ALL" if on_other == a and back == a else "?"
        want = "ALL" if kind.startswith("all") else "PER"
        return ctl, kind, got, got == want

    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(one, SCOPE.items()))
    for ctl, kind, got, ok in res:
        if not ok:
            report(False, f"scope: slider {ctl} is named {kind} but measured {got}")
    report(all(r[3] for r in res), f"scope: {sum(r[3] for r in res)} of {len(res)} controls measured as the kind their name says")


QUICK = "C:/Users/solst/Dropbox/quick one.RPP"
Q31_BUILD = "409b1ba"   # the Morpher these copies were saved on (31 sliders, 2026-08-11)


def quick31():
    conv = os.path.join(tmp, "quick-one-migrated.RPP")
    text, n = mig.convert(QUICK)
    open(conv, "w", encoding="utf-8", errors="surrogateescape", newline="").write(text)
    quick_readback(QUICK, conv, n, "quick31")


# --- After the live write: every migrated project against its snapshot. The pre-layout build
# on the snapshot == the new build on the project as it now is on disk; quick one, whose
# snapshot the pre-layout build cannot read, is read back by name against 409b1ba instead.
def migrated():
    jobs, quick = [], None
    for live in mig.files():
        snap = mig.snap_path(live)
        n = len(mig.heads(open(live, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(True)))
        if live == QUICK:
            quick = (snap, live, n)
            continue
        jobs += [(live, snap, i) for i in range(1, n + 1)]

    def one(j):
        live, snap, i = j
        a = run(OLD, 8, snap, i)
        b = run(NEW, 8, live, i)
        return live, i, np.array_equal(a, b), float(np.abs(b).max())

    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(one, jobs))
    for live, i, eq, _ in res:
        if not eq:
            report(False, f"migrated: {live} #{i} differs from its snapshot")
    same = sum(r[2] for r in res)
    report(same == len(res) == 123 and all(r[3] > 0 for r in res),
           f"migrated: {same} of {len(res)} instances on disk render bit-identical to their snapshots")
    report(quick is not None, "migrated: quick one.RPP is in the scope")
    if quick:
        quick_readback(*quick, "migrated quick one")


def quick_readback(orig, conv, n, label):
    # Read every control back, by name, on the build the copies were saved on and on the new
    # build after migration. A render cannot be compared: a month of engine work lies between.
    old_src = subprocess.run(["git", "show", f"{Q31_BUILD}:src/{FX}.jsfx"], cwd=ROOT, capture_output=True,
                             check=True).stdout.decode("utf-8")
    oldp = os.path.join(tmp, "q31.jsfx")
    open(oldp, "w", encoding="utf-8", newline="").write(old_src)
    QUICK_SRC = orig

    def read(plugin, rpp, i):
        r = subprocess.run([EXE, plugin, "--rpp", rpp, "--fx", FX, "--instance", str(i), "--list"],
                           capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr[-600:])
        return {int(m[1]): float(m[2]) for m in re.finditer(r"^\s*slider(\d+)\s.*= (\S+)", r.stdout, re.M)}
    # What each added control must read, the value it was given when it arrived.
    arrived = {9: 1, 13: 0, 14: 0, 15: 2, 16: 60, 18: 1, 19: 0, 20: 2, 21: 440, 25: 20000, 29: 1, 30: 1,
               31: 0, 32: 1, 33: 0, 34: 2, 35: 0, 36: 0, 37: 0, 38: -1, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0,
               49: 0, 51: 1, 53: 0, 54: 0, 58: 0, 59: 2, 61: 0, 62: 0}
    bad = []
    for i in range(1, n + 1):
        o, w = read(oldp, QUICK_SRC, i), read(NEW, conv, i)
        for k in range(1, 32):
            want = o[k] + 1 if k == 1 else mig.T7[int(o[k])] if k in (17, 23) else o[k]
            if abs(w[mig.Q31[k]] - want) > 1e-6:
                bad.append(f"#{i} old {k}={o[k]} -> new {mig.Q31[k]}={w[mig.Q31[k]]}")
        for k, v in arrived.items():
            if abs(w[k] - v) > 1e-6:
                bad.append(f"#{i} new {k}={w[k]}, arrived as {v}")
        if len(w) != mig.N_NEW:
            bad.append(f"#{i} lists {len(w)} controls")
    report(n == 12 and not bad, f"{label}: {n} copies, 31 old controls and 33 added ones each read back as authored {bad[:4]}")
    loud = [float(np.abs(run(NEW, 8, conv, i)).max()) for i in range(1, n + 1)]
    report(all(x > 0 for x in loud), f"{label}: all {n} migrated copies sound with silence in (peaks {min(loud):.3f}..{max(loud):.3f})")


def save(plugin, stages, path, rpp=None, inst=1, seconds=0.3):
    cmd = [EXE, plugin, "--seconds", str(seconds), "--quiet", "--save-rpp", path]
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
    # The runner names the plugin by the file it ran (a pinned temp copy); name it as a project does.
    text = open(path, encoding="utf-8").read()
    head = next(l for l in text.splitlines() if l.strip().startswith("<JS "))
    open(path, "w", encoding="utf-8", newline="").write(text.replace(head, f'    <JS "{FX}.jsfx" ""', 1))


def blobs55():
    # The same crafted copy SAVED by the pre-layout build, so its blob is 7700055 -- what REAPER
    # writes for any Morpher saved since 2026-09-11. Old build on that save == new build on it
    # migrated: the 55 -> 87 path on its own, without the 24 -> 55 step.
    if not CRAFT:
        blobs()
    s = os.path.join(tmp, "b55-saved.RPP")
    save(OLD, [], s, rpp=CRAFT["old"], inst=CRAFT["inst"], seconds=0.05)
    magic = blob_of(s, 1)[4][0]
    conv = os.path.join(tmp, "b55-migrated.RPP")
    open(conv, "w", encoding="utf-8", errors="surrogateescape", newline="").write(mig.convert(s)[0])
    a, b = run(OLD, 12, s, 1), run(NEW, 12, conv, 1)
    plain = run(OLD, 12, CRAFT["old"].replace("b24o", "b24c"), CRAFT["inst"])
    report(magic == 7700055.0 and np.array_equal(a, b) and not np.array_equal(a, plain) and np.abs(a).max() > 0,
           f"blobs55: saved by the old build (magic {magic:.0f}), drift and ramp on every target: "
           f"old == new migrated {np.array_equal(a, b)}; they matter {not np.array_equal(a, plain)}")
    got = listed_rpp(conv, 1)
    report(got[46] == 65 and got[56] == 5, f"blobs55: shows Drift target Layer 16 level and Ramp target Transpose (read {got[46]}, {got[56]})")


def listed_rpp(rpp, inst):
    r = subprocess.run([EXE, NEW, "--rpp", rpp, "--fx", FX, "--instance", str(inst), "--seconds", "0.1", "--list"],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    out = {}
    for line in r.stdout.splitlines():
        m = re.match(r"\s*slider(\d+)\s.*\]\s*=\s*(-?[\d.]+)", line)
        if m:
            out[int(m.group(1))] = float(m.group(2))
    return out


# --- The amount units (stage 5).
DDOWN, DUNIT, RBY, RUNIT, RDUR, RENG = 48, 49, 57, 58, 60, 63
LOW_CUT, SPREAD = 24, 12


def units():
    near = lambda x, y, tol=1e-6: x.shape == y.shape and float(np.abs(x - y).max()) < tol
    ramp = [(RDUR, 0.001), (RENG, 1)]
    none_ = fresh([[(RT, 5)], [], []])
    cents = fresh([[(RT, 5)], [], [(RUNIT, 3), (RBY, 1200), *ramp]])
    semis = fresh([[(RT, 5)], [], [(RBY, 12), *ramp]])
    report(near(cents, semis) and not near(cents, none_),
           f"units: a Transpose ramp of 1200 cents == 12 semitones (largest difference {np.abs(cents - semis).max():.2e})")
    away = fresh([[(RT, 5)], [(RUNIT, 3)], [(RT, 2)], [(RT, 5)], [(RBY, 1200), *ramp]])
    stay = fresh([[(RT, 5)], [(RUNIT, 3)], [], [], [(RBY, 1200), *ramp]])
    report(np.array_equal(away, stay) and not near(away, fresh([[(RT, 5)], [], [], [], []])),
           "units: the Ramp by unit stays with its target through a target switch")
    l1c = fresh([[(RT, 16)], [], [(RUNIT, 3), (RBY, 1200), *ramp]])
    l1s = fresh([[(RT, 16)], [], [(RBY, 12), *ramp]])
    report(near(l1c, l1s) and not near(l1c, none_),
           f"units: a Layer 1 pitch ramp of 1200 cents == 12 semitones ({np.abs(l1c - l1s).max():.2e})")
    allc = fresh([[(RT, 15)], [], [(RUNIT, 3), (RBY, 1200), *ramp]])
    report(near(allc, l1c), f"units: the same set on Layer pitch (all layers) == on Layer 1 ({np.abs(allc - l1c).max():.2e})")
    dr = [(DUP, 300), (DDOWN, 300), (DPER, 1.3)]
    db_ = fresh([[(DT, 10)], [], [(DUNIT, 10), *dr]])
    hz = fresh([[(DT, 10)], [], dr])
    report(np.array_equal(db_, hz) and not np.array_equal(hz, fresh([[(DT, 10)], [], []])),
           "units: dB on Low cut falls back to its own unit, Hz")
    st0 = fresh([[(DT, 10)], [], [(DUNIT, 2), (DUP, 48), (DDOWN, 48), (DPER, 1.3)]])
    report(not np.array_equal(st0, fresh([[(DT, 10)], [], []])), "units: semitones on a Low cut at 0 move it (counted from 20 Hz)")
    sp0 = fresh([[(DT, 4)], [], []], first=WASH)
    sps = fresh([[(DT, 4)], [], [(DUNIT, 2), (DUP, 60), (DDOWN, 60), (DPER, 1.3)]], first=WASH)
    report(not np.array_equal(sps, sp0), "units: semitones on a Spread at 0 move it (counted from one bin)")


# The conversions themselves, read out of a debug copy: @sample ends by writing case i into
# spl0 on sample i. Expectations are worked out here by hand-written arithmetic, not by
# calling the plugin's own formulas. (off, unit, base, nu-or-mode or floor, expected, label)
CONV = [
    ("au_pitch", 1200, 3, 0, 1, 12, "1200 cents on a Semitones value"),
    ("au_pitch", 700, 3, 5, 1, 7, "700 cents on Semitones at 5"),
    ("au_pitch", 2, 2, 100, 2, 200, "2 semitones on a Cents value"),
    ("au_pitch", 12, 2, 0, 0, 440, "12 semitones on an Hz value at 0, reference 440"),
    ("au_pitch", 440, 1, 0, 1, 12, "440 Hz on a Semitones value at 0, reference 440"),
    ("au_pitch", 3, 10, 0, 1, 3, "dB on a pitch falls back"),
    ("au_freq", 12, 2, 100, 20, 100, "12 semitones on 100 Hz"),
    ("au_freq", 1200, 3, 0, 20, 40, "1200 cents on a cutoff at 0 counts from 20 Hz"),
    ("au_freq", 30, 1, 500, 20, 30, "Hz on Hz"),
    ("au_time", 0.5, 5, 200, 3, 500, "0.5 s on 200 ms"),
    ("au_time", 250, 4, 1, 0, 0.25, "250 ms on a length in seconds"),
    ("au_time", 2, 8, 1, 0, None, "2 beats on seconds (tempo-dependent)"),
    ("au_time", 1, 1, 1, 0, -0.5, "1 Hz on a 1 s length: 2 Hz is 0.5 s"),
    ("au_time", 60, 7, 1, 0, -0.5, "60 BPM on a 1 s length"),
    ("au_time", 1, 9, 1, 0, 20, "1 Cycle on seconds, a 20 s traversal"),
    ("au_rate", 2, 5, 20, 1, 2, "2 s on Auto-morph time in Seconds passes through"),
    ("au_rate", 2000, 4, 20, 1, 2, "2000 ms on Seconds"),
    ("au_rate", 0.05, 1, 20, 1, -10, "0.05 Hz on a 20 s period: 0.1 Hz is 10 s"),
    ("au_rate", 10, 5, 6, 0, -3, "10 s on 6 BPM: 20 s is 3 BPM"),
    ("au_rate", 6, 7, 6, 0, 6, "BPM on BPM passes through"),
    ("au_rate", 1, 8, 4, 3, 1, "beats on Every N beats passes through"),
    ("au_rate", 2, 2, 20, 1, 2, "semitones on Auto-morph time falls back"),
    ("au_rate", 1, 9, 20, 1, 20, "1 Cycle on a 20 s traversal"),
]


def convert():
    src = open(os.path.join(ROOT, "src", f"{FX}.jsfx"), encoding="utf-8", newline="").read()
    cut = src.index("\r\n@serialize\r\n")
    cases = ["tempo"] + [f"{fn}({off}, {u}, {base}, {nu})" for fn, off, u, base, nu, _, _ in CONV]
    chain = "".join(f"cv_i == {i} ? {c} : " for i, c in enumerate(cases)) + "0"
    dbg = src[:cut] + ("\r\ntuning_ref = 440; au_cyc = 20;\r\n"
                       f"spl0 = {chain};\r\nspl1 = 0; cv_i += 1;\r\n") + src[cut:]
    p = pinned(dbg, "convert.jsfx")
    out = os.path.join(tmp, "convert.csv")
    r = subprocess.run([EXE, p, "--seconds", "0.01", "--csv", out, "--quiet"], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    vals = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2,))[:len(cases)]
    tempo = float(vals[0])
    bad = 0
    for (fn, off, u, base, nu, want, label), got in zip(CONV, vals[1:]):
        if want is None:
            want = (base + off * 60 / tempo) - base   # beats at the run's tempo, added to seconds
        ok = abs(got - want) < 1e-4
        bad += not ok
        if not ok:
            report(False, f"convert: {label}: got {got}, want {want}")
    report(bad == 0 and tempo > 0, f"convert: {len(CONV) - bad} of {len(CONV)} conversions equal the worked answers (tempo {tempo})")


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
