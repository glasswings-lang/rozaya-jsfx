#!/usr/bin/env python3
"""The Morpher's All slots, measured. docs/layouts/spectral-vowel-morpher-all-slots-20260911.md.

Renders run TEST COPIES with the per-load rand() scramble pinned (see
morpher_r24_verify_20260911.py); the shipped plugin keeps its scramble.

current   every saved instance: the previous build on the live project == the new
          build on the same project (no slider moves), 8 s of noise in, not silent.
fresh     a fresh instance renders identically in both builds.
eight     one capture on All: all eight slots sound identical, and not silent.
single    that capture sounds exactly like an ordinary capture into Slot 1.
canfail   a slot an ordinary Slot 1 capture never reached sounds different.
point     Capture point moved on All reaches all eight, and changes the sound.
park      passing through All leaves Slot 3's own Capture point alone.

    python tools/morpher_all_slots_verify_20260911.py [section ...] [--jobs N]
"""
import concurrent.futures as cf, os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_r24_migrate_20260911 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "spectral_vowel_morpher"
PRE = "e9ca736"      # the build before All slots
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 6
BLOCK = 32768        # one stage is ~0.74 s: a capture sees real audio, a settle is 4 stages
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


def run(plugin, seconds, rpp=None, inst=1, stages=(), extra=()):
    out = os.path.join(tmp, f"o{os.getpid()}_{abs(hash((plugin, rpp, inst, str(stages), extra)))}.csv")
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
    for rel, live in mig.files():
        if not os.path.exists(live):
            report(False, f"{rel}: live project missing")
            continue
        n = len(mig.heads(open(live, encoding="utf-8", errors="surrogateescape").read().splitlines()))
        jobs += [(rel, live, i) for i in range(1, n + 1)]

    def one(j):
        rel, live, i = j
        a = run(OLD, 8, live, i, extra=("--input", "noise"))
        b = run(NEW, 8, live, i, extra=("--input", "noise"))
        return rel, i, np.array_equal(a, b), float(np.abs(b).max())

    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(one, jobs))
    same = sum(r[2] for r in res)
    sounding = sum(r[3] > 0 for r in res)
    for rel, i, eq, mx in res:
        if not eq:
            report(False, f"{rel} #{i}: new build differs from the previous one")
    report(same == len(res) and len(res) > 0,
           f"current: {same} of {len(res)} instances bit-identical, {sounding} not silent")


def fresh():
    a = run(OLD, 6, extra=("--input", "sine", "--input-hz", "220"))
    b = run(NEW, 6, extra=("--input", "sine", "--input-hz", "220"))
    report(np.array_equal(a, b), "fresh: a fresh instance renders identically in both builds")


# A capture scenario. Stage 0 lands after block 1; stage j after block j+1.
SINE = ("--input", "sine", "--input-hz", "220", "--input-db", "-6", "--block", str(BLOCK))


def scenario(steps, seconds=12):
    """steps: list of stages, each a list of (slider, value). Audition = Focused slot
    throughout. Returns the render and the sample where the LAST stage landed."""
    stages = [[(5, 0)] + list(steps[0])] + [list(s) for s in steps[1:]]
    a = run(NEW, seconds, stages=stages, extra=SINE)
    return a, (len(stages) + 1) * BLOCK


def tail(a, start):
    return a[start + BLOCK:]


def eight():
    # NOT "the eight slots sound identical to each other": two ordinary captures of
    # one moment into two different slots already differ by ~5% as heard (measured
    # 2026-09-11, before All existed in the scenario). The claim is that All fills
    # every slot exactly as an ordinary capture into that slot would.
    outs, same, peak = {}, [], 0.0
    for k in range(1, 9):
        a, s = scenario([[(1, 0)], [(2, 1)], [(1, k)]])
        o, s2 = scenario([[(1, k)], [(2, 1)], [(1, k)]])
        outs[k] = tail(a, s)
        peak = max(peak, float(np.abs(outs[k]).max()))
        if np.array_equal(outs[k], tail(o, s2)):
            same.append(k)
    report(len(same) == 8 and peak > 0,
           f"eight: one capture on All == an ordinary capture, slot by slot, in {len(same)} of 8, peak {peak:.3f}")
    return outs


def single(outs):
    a, s = scenario([[(1, 1)], [(2, 1)], [(1, 1)]])
    report(np.array_equal(tail(a, s), outs[1]), "single: All's Slot 1 == an ordinary Slot 1 capture")


def canfail(outs):
    a, s = scenario([[(1, 1)], [(2, 1)], [(1, 5)]])
    report(not np.array_equal(tail(a, s), outs[5]),
           "canfail: Slot 5 after an ordinary Slot 1 capture differs from Slot 5 after All")


# The HEARD slot must not change inside a comparison: changing it hands the oscillator
# phases over (the anti-click swap), which alone makes two renders differ. So these two
# hear through Audition = Morph with Morph parked where it lands exactly -- 0 is Slot 1,
# 100 is Slot 8, 50 is Slots 4 and 5 at half each -- and Capture slot, which Morph
# audition ignores, is free to move.
WAIT = [[]] * 5      # a settle is 4 stages; the re-derive lands inside this


def morph_run(morph, steps, seconds):
    stages = [[(5, 1), (6, morph), (1, 0)], [(2, 1)]] + [list(s) for s in steps]
    a = run(NEW, seconds, stages=stages, extra=SINE)
    return tail(a, (len(stages) + 1) * BLOCK)


def point():
    # The move must land on the SAME stage in both runs: a point moved one block
    # earlier re-analyses one block earlier, which alone changes the render (the
    # first version of this check did that, 2026-09-11). So the All run spends the
    # by-hand run's "select the slot" stage doing nothing.
    secs = 14
    steps_after = [*WAIT, [], []]
    for morph, slot in ((0, 1), (100, 8)):
        on_all = morph_run(morph, [[], [(3, 60)], *steps_after], secs)
        by_hand = morph_run(morph, [[(1, slot)], [(3, 60)], *steps_after], secs)
        untouched = morph_run(morph, [[], [], *steps_after], secs)
        same = np.array_equal(on_all, by_hand)
        moved = not np.array_equal(on_all, untouched)
        report(same and moved and np.abs(on_all).max() > 0,
               f"point: Capture point on All == moving it by hand on Slot {slot} ({same}), "
               f"and it changed the sound ({moved})")
    # Slots 4 and 5 heard at half each: neither is the slot All shows, so only a
    # re-analysis of EVERY slot can change them. Timing cannot be matched by hand
    # for two slots, so this one is the can-fail half alone.
    on_all = morph_run(50, [[], [(3, 60)], *steps_after], secs)
    untouched = morph_run(50, [[], [], *steps_after], secs)
    report(not np.array_equal(on_all, untouched) and np.abs(on_all).max() > 0,
           "point: Capture point on All changed Slots 4 and 5, which All does not show")


def park():
    secs = 20
    via_all = morph_run(100, [[(1, 8)], [(3, 70)], *WAIT, [(1, 0)], [], [(1, 8)], []], secs)
    direct = morph_run(100, [[(1, 8)], [(3, 70)], *WAIT, [], [], [], []], secs)
    no_point = morph_run(100, [[(1, 8)], [], *WAIT, [], [], [], []], secs)
    kept = np.array_equal(via_all, direct)
    took = not np.array_equal(direct, no_point)
    report(kept and took, f"park: passing through All kept Slot 8's own point ({kept}); "
                          f"and that point changes Slot 8 ({took})")


if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()] or \
           ["fresh", "eight", "point", "park", "current"]
    outs = None
    for w in want:
        if w in ("eight", "single", "canfail"):
            outs = outs or eight()
            if w == "eight":
                single(outs); canfail(outs)
            continue
        globals()[w]()
    print(f"--- {fails} failure(s)")
    sys.exit(1 if fails else 0)
