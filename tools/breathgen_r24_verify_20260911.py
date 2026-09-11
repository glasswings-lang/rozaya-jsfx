#!/usr/bin/env python3
"""Breath Generator's eighteen targets, measured. docs/layouts/breath-gen-r24-20260911.md.

current  Rozaya's four and the bridge copy: the pre-change build (f24f083) ==
         the new build, bit for bit, not silent.
saves    synthetic 2500007, 2400007 and 2300005 saves with drift and ramp on all
         the older targets, random shapes and play/rest included: old == new, and
         the drift and ramp must matter.
targets  each of the eleven new targets, by drift, changes the sound.
tensor   Tensor's seven, migrated: the last build that read their line as saved
         (0ae0c75) on the snapshot == the new build on the migrated file; the 13
         stored values decoded by name, the exhale frequency from the blob; and
         breathscapes and organic-movement equal, value for value and in sound,
         to Rozaya's own copies migrated from the same lines on 2026-09-09.

    python tools/breathgen_r24_verify_20260911.py [current|saves|targets|tensor]
"""
import base64, os, re, struct, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import breathgen_tensor_migrate_20260911 as mig
from rpp_sliders import parse_line

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
NEW = os.path.join(ROOT, "src", "breath_gen.jsfx")
SNAP = "E:/reaper/finished/backups/snapshots/_pre-breathgen-r24-20260911"
FX = "breath_gen"
fails = 0
tmp = tempfile.mkdtemp()


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def build(commit):
    p = os.path.join(tmp, f"breath_gen-{commit}.jsfx")
    if not os.path.exists(p):
        open(p, "wb").write(subprocess.run(["git", "show", f"{commit}:src/breath_gen.jsfx"], cwd=ROOT,
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


def listing(plugin, rpp, inst=1):
    r = subprocess.run([EXE, plugin, "--rpp", rpp, "--fx", FX, "--instance", str(inst), "--list"],
                       capture_output=True, text=True, check=True)
    return {m.group(2): float(m.group(3)) for m in
            (re.match(r"\s*slider(\d+)\s+(.*?)\s+\[.*\] = (\S+)", l) for l in r.stdout.splitlines()) if m}


def blobs(path):
    L = open(path, encoding="utf-8", errors="replace").read().split("\n")
    out = []
    for i, l in enumerate(L):
        if "<JS" in l and "<JS_SER" not in l and "/breath_gen.jsfx" in l:
            vals = None
            if i + 3 < len(L) and L[i + 3].strip().startswith("<JS_SER"):
                j, b = i + 4, ""
                while L[j].strip() != ">":
                    b += L[j].strip()
                    j += 1
                raw = base64.b64decode(b)
                vals = struct.unpack("<%df" % (len(raw) // 4), raw)
            out.append((L[i + 1], vals))
    return out


def current():
    for rel, live, n in (("templates/breathscapes.RPP", "E:/reaper/templates/breathscapes.RPP", 1),
                         ("to-play-with-later/micle.RPP", "E:/reaper/to-play-with-later/micle.RPP", 1),
                         ("to-play-with-later/organic-movement.RPP", "E:/reaper/to-play-with-later/organic-movement.RPP", 2),
                         ("test-projects/claude-testing002-bridge.RPP", None, 1)):
        for k in range(1, n + 1):
            a = run(build("f24f083"), 40, f"{SNAP}/{rel}", k)
            b = run(NEW, 40, live or f"{SNAP}/{rel}", k)
            report(np.array_equal(a, b) and np.abs(a).max() > 0,
                   f"{rel} #{k}: old == new over 40 s {np.array_equal(a, b)}, peak {np.abs(a).max():.3f}")
    a, b = run(build("f24f083"), 12), run(NEW, 12)
    report(np.array_equal(a, b), "a fresh instance renders identically")


# old index: (up, down, period, shape, play, rest) and (by, duration, delay, play, rest)
DRIFT = {0: (3, 3, 2, 0, 0, 0), 1: (0.5, 0.5, 3, 2, 0, 0), 2: (0.2, 0.1, 2, 1, 0, 0),
         3: (0.6, 0.4, 2, 2, 1.25, 0.5), 4: (0.2, 0.2, 3, 0, 0, 0),
         5: (150, 100, 1.3, 0, 0, 0), 6: (100, 100, 0.7, 2, 0, 0)}
RAMP = {0: (4, 15, 0, 0, 0), 1: (1, 20, 0, 0, 0), 5: (300, 10, 0, 0, 0), 6: (-200, 8, 0, 1, 0.5)}


def old_blob(magic, mod):
    n = 7 if magic in (2500007, 2400007) else 5
    d = lambda k, dflt: [(DRIFT[t][k] if mod and t in DRIFT else dflt) for t in range(n)]
    r = lambda k: [(RAMP[t][k] if mod and t in RAMP else 0) for t in range(n)]
    v = [magic] + r(0) + r(1) + r(2) + [1] + d(0, 0) + d(1, 0) + d(2, 8) + d(3, 0) + [3]
    v += d(4, 0) + d(5, 0) + r(3) + r(4)
    v += [62, 62, 55] + [300, 300, 200] + [0, 0, 0] + [0, 0, 0] + [2, 2, 2] + [0]
    if magic == 2500007:
        v += [0, 0, 0, 0, 0, 1, 1]
    return base64.b64encode(struct.pack("<%df" % len(v), *v)).decode()


def project(path, blob):
    line = {1: 11.764706, 2: 0, 3: 2, 4: 0.3, 5: 2.5, 6: 0.3, 7: 0, 8: 0, 9: 62, 10: 300, 11: 0, 12: 2,
            13: 440, 14: 0.3, 15: 0.2, 16: 0.2, 17: 0.3, 18: 2, 19: 0.5, 20: 0, 21: 0, 25: 3, 29: 1,
            30: 0, 34: 1, 36: 1, 40: 1}
    vals = " ".join(str(line.get(i, "-")) for i in range(1, 65))
    body = "\n".join("        " + blob[i:i + 128] for i in range(0, len(blob), 128))
    open(path, "w", newline="").write(
        "<REAPER_PROJECT 0.1 \"7.0\" 0\n  <TRACK\n    <FXCHAIN\n      <JS glasswings/breath_gen.jsfx \"\"\n"
        f"        {vals}\n      >\n      <JS_SER\n{body}\n      >\n    >\n  >\n>\n")


def saves():
    for magic in (2500007, 2400007, 2300005):
        pa, pc = os.path.join(tmp, "a.RPP"), os.path.join(tmp, "c.RPP")
        project(pa, old_blob(magic, True))
        project(pc, old_blob(magic, False))
        a, b, c = run(build("f24f083"), 30, pa), run(NEW, 30, pa), run(build("f24f083"), 30, pc)
        same, matters = np.array_equal(a, b), not np.array_equal(a, c)
        report(same and matters, f"old save {magic}: loads bit-identical {same}; its drift and ramp matter {matters}")


BASE = [(3, 1), (4, 0.1), (5, 1), (6, 0.1)]
TARGETS = [(7, "Inhale fine tune", [], 300), (8, "Exhale fine tune", [], 300),
           (9, "Tuning reference", [(8, 1), (9, 60), (10, 60)], 150),
           (10, "Inhale fade in", [], 0.3), (11, "Inhale fade out", [], 0.3),
           (12, "Exhale fade in", [], 0.3), (13, "Exhale fade out", [], 0.3),
           (14, "Stereo width", [], 0.4), (15, "Output", [], 6),
           (16, "Play for", [(23, 2), (24, 1)], 1.5), (17, "Rest for", [(23, 2), (24, 1)], 1.5)]


def targets():
    for t, name, extra, amt in TARGETS:
        r = [run(NEW, 12, stages=[BASE + extra, [(25, t)], [(29, 1), (28, 1), (30, 1), (26, a), (27, a)]])
             for a in (0, amt)]
        moved = not np.array_equal(*r)
        report(moved and all(np.isfinite(x).all() for x in r), f"new target {t} {name}: changes the sound {moved}")


OLD_NAMES = {"Inhale Duration (sec)": "Inhale (in breath units)", "Top pause (sec)": "Top pause (in breath units)",
             "Exhale Duration (sec)": "Exhale (in breath units)", "Bottom pause (sec)": "Bottom pause (in breath units)",
             "Inhale Frequency Hz": "Pitch value (Hz / semitones / cents)", "Inhale Fade In": "Inhale fade in",
             "Inhale Fade Out": "Inhale fade out", "Exhale Fade In": "Exhale fade in",
             "Exhale Fade Out": "Exhale fade out", "Fade Mode": "Fade mode", "Stereo Width": "Stereo width",
             "Stereo Flip": "Stereo flip"}


def tensor():
    for name in mig.FILES:
        snap, live = f"{mig.SNAP}/{name}", f"{mig.LIVE}/{name}"
        olds, news = blobs(snap), blobs(live)
        for k in range(1, len(olds) + 1):
            a, b = run(build("0ae0c75"), 40, snap, k), run(NEW, 40, live, k)
            ol, nl = listing(build("0ae0c75"), snap, k), listing(NEW, live, k)
            # An old declaration can carry a trailing comment in its name, so match
            # the old name by its start.
            old = lambda o: next(v for key, v in ol.items() if key.startswith(o))
            bad = [f"{o} {old(o)} -> {nl.get(n)}" for o, n in OLD_NAMES.items()
                   if abs(nl.get(n, 1e9) - old(o)) > 1e-6]
            # 2500007: magic, 11 banks of 7 and two selectors (80 floats), then
            # pitch note[3], pitch value[3] -- so Exhale's value is float 85.
            ex = news[k - 1][1][1 + 11 * 7 + 2 + 3 + 2] if news[k - 1][1] else None
            if ex is None or abs(ex - old("Exhale Frequency Hz")) > 1e-3:
                bad.append(f"exhale frequency in the blob {ex}, stored {old('Exhale Frequency Hz')}")
            same = np.array_equal(a, b)
            report(same and not bad and np.abs(a).max() > 0,
                   f"Tensor {name} #{k}: 0ae0c75 on snapshot == new on migrated {same}; by name"
                   + ("" if not bad else " -- " + "; ".join(bad)))
    for name, mine, n in (("breathscapes.RPP", "E:/reaper/templates/breathscapes.RPP", 1),
                          ("organic-movement.RPP", "E:/reaper/to-play-with-later/organic-movement.RPP", 2)):
        t_b, m_b = blobs(f"{mig.LIVE}/{name}"), blobs(mine)
        for k in range(n):
            tl, ml = parse_line(t_b[k][0]), parse_line(m_b[k][0])
            vals_eq = all(abs(float(tl[s]) - float(ml[s])) < 1e-9 for s in range(1, 42))
            blob_eq = t_b[k][1] == m_b[k][1]
            sound_eq = np.array_equal(run(NEW, 40, f"{mig.LIVE}/{name}", k + 1), run(NEW, 40, mine, k + 1))
            report(vals_eq and blob_eq and sound_eq,
                   f"Tensor {name} #{k+1} against Rozaya's copy: 41 values equal {vals_eq}, "
                   f"blob equal {blob_eq}, sound identical {sound_eq}")


def main():
    parts = sys.argv[1:] or ["current", "saves", "targets", "tensor"]
    for p in parts:
        globals()[p]()
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
