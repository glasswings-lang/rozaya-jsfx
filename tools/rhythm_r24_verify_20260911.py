#!/usr/bin/env python3
"""Rhythm Track's sixteen targets and Drift movement, measured.
docs/layouts/rhythm-track-r24-20260911.md.

current   the bridge copy: the pre-change build (912d95f) on the snapshot == the
          new build on the migrated file, not silent; its selectors read Swing
          (2) and Drift movement On a clock; a fresh instance renders identically.
saves     synthetic 2400002 / 2300002 / 2200002 / 2100002 saves with drift and
          ramp on both old targets, Random shape on Swing: old build on the old
          line == new build on the migrated line with the SAME blob, and the drift
          and ramp must matter.
targets   each of the fourteen new targets, by drift, changes the sound, finite.
movement  With the target and On a clock differ, on a click target and on the bar.
bar       a Beats per bar edit mid-bar waits for the downbeat: accents S W W W S W
          S W on the new build, and the OLD build must not do that (the test can fail).
fresh     under a pitch drift the clicks differ from each other; without, they match.
tensor    Tensor's two first-release copies: e09eec7 (the last build with the first
          release's positions 1-13) on the snapshot == the new build on the migrated
          file; every value by name, the weak frequency from the blob.

    python tools/rhythm_r24_verify_20260911.py [current|saves|targets|movement|bar|fresh|tensor]
"""
import base64, os, re, struct, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import rhythm_r24_migrate_20260911 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
NEW = os.path.join(ROOT, "src", "rhythm-track.jsfx")
FX = "rhythm-track"
PRE = "912d95f"
fails = 0
tmp = tempfile.mkdtemp()


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def build(commit):
    p = os.path.join(tmp, f"rhythm-{commit}.jsfx")
    if not os.path.exists(p):
        open(p, "wb").write(subprocess.run(["git", "show", f"{commit}:src/rhythm-track.jsfx"], cwd=ROOT,
                                           capture_output=True, check=True).stdout)
    return p


def run(plugin, seconds, rpp=None, stages=()):
    out = os.path.join(tmp, "o.csv")
    cmd = [EXE, plugin, "--seconds", str(seconds), "--csv", out, "--quiet"]
    if rpp:
        cmd += ["--rpp", rpp, "--fx", FX, "--instance", "1"]
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))


def listing(plugin, rpp):
    r = subprocess.run([EXE, plugin, "--rpp", rpp, "--fx", FX, "--list"], capture_output=True, text=True, check=True)
    return {m.group(2): float(m.group(3)) for m in
            (re.match(r"\s*slider(\d+)\s+(.*?)\s+\[.*\] = (\S+)", l) for l in r.stdout.splitlines()) if m}


def blob(path):
    L = open(path, encoding="utf-8", errors="replace").read().split("\n")
    i = next(k for k, l in enumerate(L) if "<JS " in l and "rhythm-track.jsfx" in l)
    j = next(k for k in range(i + 1, i + 5) if L[k].strip().startswith("<JS_SER"))
    b, k = "", j + 1
    while L[k].strip() != ">":
        b += L[k].strip()
        k += 1
    raw = base64.b64decode(b)
    return struct.unpack("<%df" % (len(raw) // 4), raw)


def current():
    rel, live, _ = mig.FILES[0]
    snap = f"{mig.SNAP}/{rel}"
    a, b = run(build(PRE), 30, snap), run(NEW, 30, live)
    same = np.array_equal(a, b)
    report(same and np.abs(a).max() > 0, f"bridge: old on snapshot == new on migrated {same}, peak {np.abs(a).max():.3f}")
    nl = listing(NEW, live)
    got = (nl.get("Drift target"), nl.get("Ramp target"), nl.get("Drift movement"))
    report(got == (2, 2, 1), f"bridge reads Drift target, Ramp target, Drift movement = {got}, want (2, 2, 1)")
    a, b = run(build(PRE), 8), run(NEW, 8)
    report(np.array_equal(a, b) and np.abs(a).max() > 0, "a fresh instance renders identically")


def old_blob(magic, mod):
    #            up     down   period shape  play   rest
    D = {0: (20, 30, 3, 0, 1.25, 0.5), 1: (0.4, 0.3, 2, 2, 0, 0)}
    #            by    dur  delay play rest
    R = {0: (-40, 6, 1, 0, 0), 1: (0.5, 5, 0, 1, 0.5)}
    d = lambda k, dflt: [(D[t][k] if mod else dflt) for t in range(2)]
    r = lambda k: [(R[t][k] if mod else 0) for t in range(2)]
    v = [magic] + d(0, 0) + d(1, 0) + d(2, 8) + d(3, 0) + [1] + r(0) + r(1) + r(2) + [1]
    if magic in (2200002, 2400002):
        v += d(4, 0) + d(5, 0) + r(3) + r(4)
    if magic >= 2300000:
        v += [81, 81, 69] + [880, 880, 440] + [0, 0, 0] + [0, 0, 0] + [2, 2, 2] + [0]
    return base64.b64encode(struct.pack("<%df" % len(v), *v)).decode()


def project(path, line, b64):
    body = "\n".join("        " + b64[i:i + 128] for i in range(0, len(b64), 128))
    open(path, "w", newline="").write(
        "<REAPER_PROJECT 0.1 \"7.0\" 0\n  <TRACK\n    <FXCHAIN\n      <JS glasswings/rhythm-track.jsfx \"\"\n"
        f"{line}      >\n      <JS_SER\n{body}\n      >\n    >\n  >\n>\n")


def saves():
    base = {1: 120, 2: 0, 3: 4, 4: 0.2, 5: 0, 6: 0, 7: 81, 8: 880, 9: 0, 10: 2, 11: 440, 12: 1.5, 13: 0.75,
            14: 0.5, 15: 0.04, 16: 0.02, 17: 1, 18: 3, 19: 0, 20: 0, 21: 0, 22: 0, 23: 1, 24: 0.5, 25: 1,
            26: 5, 27: 1, 28: 0.5, 29: 1, 30: 0, 31: 1, 32: 0.4, 33: 0.3, 34: 2, 35: 0, 36: 2, 37: 0, 38: 0, 39: 0}
    old_line = "        " + " ".join(str(base.get(i, "-")) for i in range(1, 65)) + "\n"
    new_line = mig.current_line(old_line, "synthetic")
    for magic in (2400002, 2300002, 2200002, 2100002):
        po, pn, pc = (os.path.join(tmp, f"{x}.RPP") for x in "onc")
        project(po, old_line, old_blob(magic, True))
        project(pn, new_line, old_blob(magic, True))
        project(pc, old_line, old_blob(magic, False))
        a, b, c = run(build(PRE), 30, po), run(NEW, 30, pn), run(build(PRE), 30, pc)
        same, matters = np.array_equal(a, b), not np.array_equal(a, c)
        report(same and matters and np.abs(a).max() > 0,
               f"old save {magic}: loads bit-identical {same}; its drift and ramp matter {matters}")


BASE = [(1, 120)]
SEMI = [(6, 1), (7, 69), (8, 69)]
TARGETS = [(1, "Beats per bar", [(18, 3)], 2), (3, "Strong pitch", [], 200), (4, "Weak pitch", [], 100),
           (5, "Strong fine tune", [], 300), (6, "Weak fine tune", [], 300), (7, "Tuning reference", SEMI, 150),
           (8, "Tone resonance", [], 3), (9, "Strong volume", [], 0.3), (10, "Weak volume", [], 0.3),
           (11, "Strong decay", [], 0.1), (12, "Weak decay", [], 0.1), (13, "Pan spread", [(18, 2)], 0.5),
           (14, "Play for", [(21, 2), (22, 1)], 2.5), (15, "Rest for", [(21, 2), (22, 1)], 2.5)]
# Play for and Rest for render 12 s. A rest length is only read at a rest check,
# once per play+rest cycle, and with a 1.3 s wave the checks in the first 8 s all
# fell at or below zero, where Rest for 1 stays 1: two false FAILs on 2026-09-11.
# Measured: the renders first differ at exactly 8.0 s, the first check above zero.


# A period of 1.3 s, never a whole second: at 120 BPM a beat is 0.5 s and a bar
# 2 s, so a 1 s sine is read at its zero crossings on every click and every
# downbeat, and drift changes nothing. That false FAIL happened on the first run.
def drifted(t, amt, extra=(), moves=1, unit=1, per=1.3, seconds=8):
    return run(NEW, seconds, stages=[BASE + list(extra), [(31, t)],
                                     [(35, unit), (34, per), (36, moves), (32, amt), (33, amt)]])


def targets():
    for t, name, extra, amt in TARGETS:
        r = [drifted(t, a, extra, seconds=12 if t >= 14 else 8) for a in (0, amt)]
        moved = not np.array_equal(*r)
        report(moved and all(np.isfinite(x).all() for x in r), f"new target {t} {name}: changes the sound {moved}")


def movement():
    for t, name, extra, amt, per in ((3, "Strong pitch", [(3, 1)], 300, 3), (1, "Beats per bar", [(18, 3)], 2, 3)):
        a = drifted(t, amt, extra, moves=0, unit=0, per=per, seconds=12)
        b = drifted(t, amt, extra, moves=1, unit=0, per=per, seconds=12)
        report(not np.array_equal(a, b), f"Drift movement on {name}: With the target differs from On a clock")


def clicks(x):
    """Peak of each click, in order (mono pan, so both channels are the same)."""
    m = np.abs(x[:, 0])
    on = np.flatnonzero(m > 0.01)
    starts = [on[0]] + [on[k] for k in range(1, len(on)) if on[k] - on[k - 1] > 2000]
    ends = starts[1:] + [len(m)]
    return [float(m[s:e].max()) for s, e in zip(starts, ends)]


def bar():
    seq = lambda x: "".join("S" if p > 0.45 else "W" for p in clicks(x))
    # Stage 1 sets the bar to 4; one block later, inside the first beat, it becomes 2.
    st = [[(1, 120), (3, 4)], [(3, 2)]]
    new, old = seq(run(NEW, 6, stages=st)), seq(run(build(PRE), 6, stages=st))
    report(new.startswith("SWWWSWSWSW"), f"a mid-bar edit waits for the downbeat: new {new[:12]}")
    report(old.startswith("SWSW"), f"and the old build changed at once, so the test can fail: old {old[:12]}")


def fresh():
    def peaks(x):
        m = np.abs(x[:, 0])
        on = np.flatnonzero(m > 0.01)
        starts = [on[0]] + [on[k] for k in range(1, len(on)) if on[k] - on[k - 1] > 2000]
        # Clicks 4-11: the edit to Beats per bar waits for the downbeat, so the first
        # bar still has its three weak clicks. Reading them was the first run's false FAIL.
        return [tuple(np.round(x[s:s + 400, 0], 9)) for s in starts[4:12]]
    extra = [(3, 1)]                    # every beat a strong click, so every click is comparable
    flat = peaks(drifted(3, 0, extra, seconds=10))
    moving = peaks(drifted(3, 300, extra, seconds=10))
    report(len(set(flat)) == 1, f"no drift: the first 8 clicks are identical ({len(set(flat))} distinct)")
    report(len(set(moving)) >= 6, f"pitch drift: the clicks differ ({len(set(moving))} distinct of 8)")


FIRST = {"Tempo": "Tempo", "Beats per bar": "Beats per bar", "Swing amount": "Swing amount",
         "Strong beat frequency": "Pitch value", "Tone resonance": "Tone resonance",
         "Strong beat volume": "Strong beat volume", "Weak beat volume": "Weak beat volume",
         "Strong beat decay": "Strong beat decay", "Weak beat decay": "Weak beat decay",
         "Pan spread": "Pan spread", "Pan mode": "Pan mode", "Pan direction": "Pan direction"}


def tensor():
    for rel, live, kind in mig.FILES[1:]:
        snap = f"{mig.SNAP}/{rel}"
        a, b = run(build("e09eec7"), 30, snap), run(NEW, 30, live)
        same = np.array_equal(a, b)
        silent = np.abs(a).max() == 0
        ol, nl = listing(build("d19873f"), snap), listing(NEW, live)
        find = lambda d, start: next(v for k, v in d.items() if k.startswith(start))
        bad = [f"{o} {find(ol, o)} -> {find(nl, n)}" for o, n in FIRST.items()
               if abs(find(ol, o) - find(nl, n)) > 1e-4]
        weak = blob(live)[1 + 16 * 4 + 1 + 16 * 3 + 1 + 16 * 4 + 3 + 2]
        if abs(weak - find(ol, "Weak beat frequency")) > 1e-4:
            bad.append(f"weak frequency in the blob {weak}")
        report(same and not bad, f"Tensor {rel.split('/')[-1][:32]}: e09eec7 on snapshot == new on migrated {same}"
               f" ({'silent in both, as typed' if silent else f'peak {np.abs(a).max():.3f}'}); by name"
               + ("" if not bad else " -- " + "; ".join(bad)))


def main():
    for p in (sys.argv[1:] or ["current", "saves", "targets", "movement", "bar", "fresh", "tensor"]):
        globals()[p]()
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
