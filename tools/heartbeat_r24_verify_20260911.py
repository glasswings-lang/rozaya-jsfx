#!/usr/bin/env python3
"""Heartbeat's eighteen targets, measured. docs/layouts/heartbeat-r24-20260911.md.

current  the bridge copy and Rozaya's transformation: the pre-change build
         (af7479a) on the snapshot == the new build on the live file and on the
         unchanged snapshot; transformation's moved blob is byte-identical to the
         nested one, and still holds S2 at 75 Hz.
saves    synthetic 2400004, 2300004, 2200004 and 2100004 saves with drift and ramp
         on all four old targets: old == new, and the drift and ramp must matter.
targets  each of the fourteen new targets, by drift, changes the sound.
tensor   Tensor's transformation: the last build that read the first-release line
         as saved (9d33c5b) on the snapshot == the new build on the migrated file,
         the 13 values by name, and value for value, blob for blob and in sound
         against Rozaya's own copy.

    python tools/heartbeat_r24_verify_20260911.py [current|saves|targets|tensor]
"""
import base64, os, re, struct, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import heartbeat_r24_migrate_20260911 as mig
from rpp_sliders import parse_line

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
NEW = os.path.join(ROOT, "src", "heartbeat gen.jsfx")
FX = "heartbeat"
PRE = "af7479a"
fails = 0
tmp = tempfile.mkdtemp()


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def build(commit):
    p = os.path.join(tmp, f"heartbeat-{commit}.jsfx")
    if not os.path.exists(p):
        open(p, "wb").write(subprocess.run(["git", "show", f"{commit}:src/heartbeat gen.jsfx"], cwd=ROOT,
                                           capture_output=True, check=True).stdout)
    return p


def run(plugin, seconds, rpp=None, inst=1, stages=()):
    out = os.path.join(tmp, "o.csv")
    cmd = [EXE, plugin, "--seconds", str(seconds), "--csv", out, "--quiet"]
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
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))


def listing(plugin, rpp):
    r = subprocess.run([EXE, plugin, "--rpp", rpp, "--fx", FX, "--list"], capture_output=True, text=True, check=True)
    return {m.group(2): float(m.group(3)) for m in
            (re.match(r"\s*slider(\d+)\s+(.*?)\s+\[.*\] = (\S+)", l) for l in r.stdout.splitlines()) if m}


def block(path):
    """(value line, blob floats) of the first Heartbeat, wherever its <JS_SER> sits."""
    L = open(path, encoding="utf-8", errors="replace").read().split("\n")
    i = next(k for k, l in enumerate(L) if "<JS " in l and "heartbeat gen.jsfx" in l)
    j = next(k for k in range(i + 1, i + 5) if L[k].strip().startswith("<JS_SER"))
    b, k = "", j + 1
    while L[k].strip() != ">":
        b += L[k].strip()
        k += 1
    raw = base64.b64decode(b)
    return L[i + 1], struct.unpack("<%df" % (len(raw) // 4), raw)


def current():
    snap_t, live_t = f"{mig.SNAP}/finished/transformation.RPP", "E:/reaper/finished/transformation.RPP"
    for name, snap, live in (("transformation", snap_t, live_t),
                             ("bridge", f"{mig.SNAP}/test-projects/claude-testing002-bridge.RPP", None)):
        a = run(build(PRE), 30, snap)
        b = run(NEW, 30, live or snap)
        c = run(NEW, 30, snap)
        ok = np.array_equal(a, b) and np.array_equal(a, c) and np.abs(a).max() > 0
        report(ok, f"{name}: old on snapshot == new on live {np.array_equal(a, b)}, "
                   f"== new on the unchanged snapshot {np.array_equal(a, c)}, peak {np.abs(a).max():.3f}")
    s_blob, l_blob = block(snap_t)[1], block(live_t)[1]
    # The pitch banks close the stream: note[3], value[3], mode[3], fine[3], unit[3],
    # last target -- so S1's value is float -12 and S2's is -11.
    report(s_blob == l_blob and abs(l_blob[-11] - 75) < 1e-6,
           f"transformation's saved data moved unchanged {s_blob == l_blob}; S2 pitch in it {l_blob[-11]}")
    a, b = run(build(PRE), 8), run(NEW, 8)
    report(np.array_equal(a, b), "a fresh instance renders identically")


DRIFT = {0: (6, 6, 3, 0, 0, 0), 1: (30, 30, 2, 2, 0, 0), 2: (0.05, 0.05, 1.5, 1, 1.25, 0.5), 3: (0.02, 0.02, 2, 2, 0, 0)}
RAMP = {0: (-10, 20, 0, 0, 0), 2: (0.1, 10, 0, 0, 0), 3: (0.03, 8, 0, 1, 0.5)}


def old_blob(magic, mod):
    d = lambda k, dflt: [(DRIFT[t][k] if mod else dflt) for t in range(4)]
    r = lambda k: [(RAMP[t][k] if mod and t in RAMP else 0) for t in range(4)]
    v = [magic] + r(0) + r(1) + r(2) + [3] + d(0, 0) + d(1, 0) + d(2, 8) + d(3, 0) + [2]
    if magic >= 2200000:
        v += d(4, 0) + d(5, 0) + r(3) + r(4)
    if magic >= 2300000:
        v += [0, 0, 1, 1]
    if magic >= 2400000:
        v += [34, 34, 46] + [45, 45, 110] + [0, 0, 0] + [0, 0, 0] + [2, 2, 2] + [0]
    return base64.b64encode(struct.pack("<%df" % len(v), *v)).decode()


def project(path, blob):
    line = {1: 72, 2: 0, 3: 120, 4: 1, 5: 0.7, 6: 0.3, 7: 60, 8: 25, 9: 0, 10: 0, 11: 34, 12: 45, 13: 0,
            14: 2, 15: 440, 16: 3, 17: 6, 18: 0.08, 19: 0.02, 23: 2, 27: 1, 28: 1, 32: 3, 34: 1, 38: 1}
    vals = " ".join(str(line.get(i, "-")) for i in range(1, 65))
    body = "\n".join("        " + blob[i:i + 128] for i in range(0, len(blob), 128))
    open(path, "w", newline="").write(
        "<REAPER_PROJECT 0.1 \"7.0\" 0\n  <TRACK\n    <FXCHAIN\n      <JS \"glasswings/heartbeat gen.jsfx\" \"\"\n"
        f"        {vals}\n      >\n      <JS_SER\n{body}\n      >\n    >\n  >\n>\n")


def saves():
    for magic in (2400004, 2300004, 2200004, 2100004):
        pa, pc = os.path.join(tmp, "a.RPP"), os.path.join(tmp, "c.RPP")
        project(pa, old_blob(magic, True))
        project(pc, old_blob(magic, False))
        a, b, c = run(build(PRE), 30, pa), run(NEW, 30, pa), run(build(PRE), 30, pc)
        same, matters = np.array_equal(a, b), not np.array_equal(a, c)
        report(same and matters, f"old save {magic}: loads bit-identical {same}; its drift and ramp matter {matters}")


BASE = [(1, 120)]
TARGETS = [(2, "S1 volume", [], 0.5), (3, "S2 volume", [], 0.5), (4, "Brightness", [], 0.5),
           (5, "S1 decay", [], 40), (6, "S2 decay", [], 20), (7, "S1 pitch", [], 20), (8, "S2 pitch", [], 40),
           (9, "S1 fine tune", [], 300), (10, "S2 fine tune", [], 300),
           (11, "Tuning reference", [(10, 1), (11, 40), (12, 40)], 150), (12, "Stereo width", [], 2),
           (13, "Breath cycle", [(18, 0.25)], 4), (16, "Play for", [(21, 2), (22, 1)], 1.5),
           (17, "Rest for", [(21, 2), (22, 1)], 1.5)]


def targets():
    for t, name, extra, amt in TARGETS:
        r = [run(NEW, 8, stages=[BASE + extra, [(23, t)], [(27, 1), (26, 1), (28, 1), (24, a), (25, a)]])
             for a in (0, amt)]
        moved = not np.array_equal(*r)
        report(moved and all(np.isfinite(x).all() for x in r), f"new target {t} {name}: changes the sound {moved}")


OLD_NAMES = {"Heart rate": "Heart rate (BPM", "Systole ms": "Systole ms", "S1 Volume": "S1 Volume",
             "S2 Volume": "S2 Volume", "Brightness": "Brightness", "S1 Decay": "S1 Decay", "S2 Decay": "S2 Decay",
             "Stereo Width": "Stereo Width", "Breath Cycle": "Breath Cycle", "Breath HRV": "Breath HRV",
             "Random HRV": "Random HRV"}


def tensor():
    snap, live = f"{mig.SNAP}/tensor/transformation.RPP", "E:/tensor's-rpp-projects/transformation.RPP"
    a, b = run(build("9d33c5b"), 30, snap), run(NEW, 30, live)
    ol, nl = listing(build("9d33c5b"), snap), listing(NEW, live)
    find = lambda d, start: next(v for k, v in d.items() if k.startswith(start))
    bad = [f"{o} {find(ol, o)} -> {find(nl, n)}" for o, n in OLD_NAMES.items() if abs(find(ol, o) - find(nl, n)) > 1e-6]
    blob = block(live)[1]
    if abs(blob[-12] - find(ol, "S1 Frequency")) > 1e-6 or abs(blob[-11] - find(ol, "S2 Frequency")) > 1e-6:
        bad.append(f"pitches in the blob {blob[-12]}, {blob[-11]}")
    same = np.array_equal(a, b)
    report(same and not bad and np.abs(a).max() > 0,
           f"Tensor transformation: 9d33c5b on snapshot == new on migrated {same}; by name"
           + ("" if not bad else " -- " + "; ".join(bad)))
    mine = "E:/reaper/finished/transformation.RPP"
    tl, ml = parse_line(block(live)[0]), parse_line(block(mine)[0])
    # A slot one file leaves unstored and the other stores as 0 is the same value.
    vals_eq = all(float(tl.get(s) or 0) == float(ml.get(s) or 0) for s in range(1, 41))
    blob_eq = block(live)[1] == block(mine)[1]
    sound_eq = np.array_equal(b, run(NEW, 30, mine))
    report(vals_eq and blob_eq and sound_eq,
           f"Tensor transformation against Rozaya's copy: values equal {vals_eq}, blob equal {blob_eq}, "
           f"sound identical {sound_eq}")


def main():
    for p in (sys.argv[1:] or ["current", "saves", "targets", "tensor"]):
        globals()[p]()
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
