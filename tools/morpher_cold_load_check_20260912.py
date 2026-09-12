#!/usr/bin/env python3
"""The Morpher sounds on project load with the transport STOPPED (2026-09-12).

Rozaya: "I'd expect there to be a little stutter at play, but on project load, to walk
into silence? cmmon". A copy saved on Capture point 0 and Capture average 1 never had
its captures analysed until the first play; measured silent in `breathing` #1.

Every live instance (backups skipped), old build (PRE) against new, rand scramble pinned:
  playing   old == new, bit-identical (the play edge analysed first in both)
  stopped   new is not silent wherever the same instance sounds when playing
  can-fail  old stopped is silent for the copies on both defaults

    python tools/morpher_cold_load_check_20260912.py [--jobs N] [--pre REV]
"""
import concurrent.futures as cf, glob, os, re, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "spectral_vowel_morpher"
PRE = sys.argv[sys.argv.index("--pre") + 1] if "--pre" in sys.argv else "caa6e29"
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 6
tmp = tempfile.mkdtemp()


def pinned(text, name):
    if text.count("_tp = time_precise();") != 1:
        raise SystemExit("the load-time scramble line is not there exactly once")
    p = os.path.join(tmp, name)
    open(p, "w", encoding="utf-8", newline="").write(text.replace("_tp = time_precise();", "_tp = 0.25;"))
    return p


OLD = pinned(subprocess.run(["git", "show", f"{PRE}:src/{FX}.jsfx"], cwd=ROOT, capture_output=True,
                            check=True).stdout.decode("utf-8"), "old.jsfx")
NEW = pinned(open(os.path.join(ROOT, "src", f"{FX}.jsfx"), encoding="utf-8").read(), "new.jsfx")


def render(plugin, rpp, inst, extra):
    out = os.path.join(tmp, f"r{abs(hash((plugin, rpp, inst, str(extra))))}.csv")
    r = subprocess.run([EXE, plugin, "--rpp", rpp, "--fx", FX, "--instance", str(inst), "--seconds", "6",
                        "--csv", out, "--quiet", *extra],   # SILENT input: the Morpher passes its input
                                                            # through, and a -60 dB noise in counted as
                                                            # "sounds stopped" on the old build (2026-09-12)
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{rpp} #{inst}: {r.stderr[-400:]}")
    a = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))
    os.remove(out)
    return a


def settings(rpp, inst):
    r = subprocess.run([EXE, NEW, "--list", "--rpp", rpp, "--fx", FX, "--instance", str(inst)],
                       capture_output=True, text=True)
    v = {m[0]: float(m[1]) for m in re.findall(r"^\s*slider(\d+)\s.*=\s*(-?[\d.e+]+)", r.stdout, re.M)}
    return v.get("3"), v.get("4")


def one(job):
    rpp, inst = job
    cp, ca = settings(rpp, inst)
    op, np_ = render(OLD, rpp, inst, ["--transport"]), render(NEW, rpp, inst, ["--transport"])
    os_, ns = render(OLD, rpp, inst, ["--stopped"]), render(NEW, rpp, inst, ["--stopped"])
    # The last 4 s: past the load settle in both.
    tail = slice(2 * 44100, None)
    rms = lambda a: float(np.sqrt((a[tail] ** 2).mean()))
    return rpp, inst, cp, ca, np.array_equal(op, np_), rms(np_), rms(os_), rms(ns)


jobs = []
for f in glob.glob(r"E:\reaper\**\*.RPP", recursive=True):
    if "backups" in f.lower():
        continue
    n = len(re.findall(rf"<JS glasswings/{FX}\.jsfx", open(f, encoding="utf-8", errors="replace").read()))
    jobs += [(f, i) for i in range(1, n + 1)]

with cf.ThreadPoolExecutor(JOBS) as ex:
    res = list(ex.map(one, jobs))

fails = 0
same = sum(r[4] for r in res)
if same != len(res):
    fails += 1
for rpp, inst, cp, ca, eq, play, old_stop, new_stop in res:
    tag = os.path.relpath(rpp, "E:/reaper")
    if not eq:
        print(f"FAIL playing differs old vs new: {tag} #{inst}")
    if play > 1e-6 and new_stop <= 1e-6:
        fails += 1
        print(f"FAIL silent stopped though it sounds playing: {tag} #{inst} (point {cp}, average {ca})")
defaults = [r for r in res if r[2] == 0 and r[3] == 1 and r[5] > 1e-6]
old_silent = sum(r[6] <= 1e-6 for r in defaults)
sounding = sum(r[5] > 1e-6 for r in res)
print(f"{'ok  ' if same == len(res) else 'FAIL'} playing: {same} of {len(res)} instances bit-identical old vs new")
print(f"ok   stopped: every one of {sounding} instances that sound playing also sounds stopped" if not fails else
      f"FAIL stopped: see above")
print(f"{'ok  ' if defaults and old_silent == len(defaults) else 'FAIL'} can-fail: the old build was silent stopped "
      f"in {old_silent} of {len(defaults)} sounding copies on Capture point 0 and Capture average 1")
if not defaults or old_silent != len(defaults):
    fails += 1
print(f"--- {fails} failure(s)")
sys.exit(1 if fails else 0)
