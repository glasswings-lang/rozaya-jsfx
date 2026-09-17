#!/usr/bin/env python3
"""Womb's migration, measured on every live copy BEFORE anything is written.

The migrated text is built into --out (live files are only READ). Then, per copy:

  sound     the OLD build on the original project against the NEW build on the migrated copy,
            30 s each. Everything in this turn but the Breath high-pass is meant to leave a saved
            sound alone, so the difference is reported and checked against --tol (default 0.5 dB
            on the overall level): the new filter is a real change and Rozaya asked for the size
            of it, not for it to be asserted away.
  controls  every old control's value in its new slot, with the changes made on purpose: the five
            volumes in dB, the percents, the three pitch blocks holding their old Hz, the
            transport unit on Beats.
  format    the migrated blob is 2700049.

    python tools/womb_checks/verify_live.py --out DIR [--old PATH] [--tol dB]
"""
import ctypes
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile

ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import womb_migrate_mechanical_20260917 as mig
from rpp_sliders import parse_line

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "womb_sound_generator_v3"
OUT = sys.argv[sys.argv.index("--out") + 1]
TOL = float(sys.argv[sys.argv.index("--tol") + 1]) if "--tol" in sys.argv else 0.5
os.makedirs(OUT, exist_ok=True)
work = tempfile.mkdtemp(dir=OUT)

if "--old" in sys.argv:
    OLD = sys.argv[sys.argv.index("--old") + 1]
else:
    OLD = os.path.join(work, "old.jsfx")
    open(OLD, "wb").write(subprocess.run(["git", "show", "HEAD:src/%s.jsfx" % FX], cwd=ROOT,
                                         capture_output=True).stdout)
NEW = os.path.join(ROOT, "src", "%s.jsfx" % FX)


def render(plug, rpp, inst, secs=30):
    csv = os.path.join(work, "r.csv")
    if os.path.exists(csv):
        os.remove(csv)
    subprocess.run([EXE, plug, "--rpp", rpp, "--fx", FX, "--instance", str(inst),
                    "--seconds", str(secs), "--quiet", "--csv", csv], capture_output=True)
    return np.loadtxt(csv, delimiter=",", skiprows=1)[:, 2:] if os.path.exists(csv) else None


def db(x):
    return 20 * math.log10(math.sqrt((x ** 2).mean()) + 1e-12)


def loaded_line(plug, rpp, inst):
    out = os.path.join(work, "loaded.RPP")
    if os.path.exists(out):
        os.remove(out)
    subprocess.run([EXE, plug, "--rpp", rpp, "--fx", FX, "--instance", str(inst), "--seconds", "0.05",
                    "--quiet", "--save-rpp", out], capture_output=True)
    L = open(out, encoding="utf-8").read().split("\n")
    return L[[i for i, l in enumerate(L) if "<JS" in l and "<JS_SER" not in l][0] + 1]


def controls(old_line, new_line):
    o, n = parse_line(old_line), parse_line(new_line)
    bad = []
    for oid, nid in mig.MOVE.items():
        if o.get(oid) in (None, "-") or oid in mig.VOL_DB or oid in mig.PERCENT:
            continue
        want, got = mig.num(o, oid), mig.num(n, nid)
        if abs(want - got) > 0.002:
            bad.append(("moved", oid, nid, want, got))
    for oid, nid in mig.VOL_DB.items():
        want, got = mig.to_db(mig.num(o, oid)), mig.num(n, nid)
        if abs(want - got) > 0.01:
            bad.append(("dB", oid, nid, want, got))
    for oid, nid in mig.PERCENT.items():
        want, got = mig.num(o, oid) * 100, mig.num(n, nid)
        if abs(want - got) > 0.01:
            bad.append(("percent", oid, nid, want, got))
    # The three new pitch blocks hold the old control's Hz, on Hz.
    for oid, mode_id, val_id in ((45, 45, 47), (46, 50, 52), (58, 66, 68)):
        if int(round(mig.num(n, mode_id))) != 0 or abs(mig.num(n, val_id) - mig.num(o, oid)) > 0.01:
            bad.append(("pitch block", oid, val_id, mig.num(o, oid),
                        (mig.num(n, mode_id), mig.num(n, val_id))))
    if int(round(mig.num(n, 77))) != 1:
        bad.append(("transport unit", None, 77, 1, mig.num(n, 77)))
    return bad


def main():
    manifest = {"files": [], "copies": 0, "fails": 0}
    for path in mig.files():
        text, count = mig.convert_file(path)
        migrated = os.path.join(OUT, os.path.basename(path))
        open(migrated, "wb").write(text.encode("utf-8"))
        for k in range(1, count + 1):
            manifest["copies"] += 1
            bad = controls(loaded_line(OLD, path, k), loaded_line(NEW, migrated, k))
            ml = open(migrated, encoding="utf-8").read().split("\n")
            mh = [i for i, l in enumerate(ml) if re.search(r"<JS\s+glasswings/%s\.jsfx" % FX, l)]
            fmt = int(round(mig.blob_span(ml, mh[k - 1] + 2)[2][0]))
            a, b = render(OLD, path, k), render(NEW, migrated, k)
            if a is None or b is None:
                lvl, same = 99, False
            else:
                m = min(len(a), len(b))
                lvl = db(b[:m]) - db(a[:m])
                same = abs(lvl) <= TOL
            ok = same and not bad and fmt == mig.NEW_MAGIC
            manifest["fails"] += 0 if ok else 1
            print("%s %s copy %d: level %+.2f dB; controls %s; blob %d" % (
                "PASS" if ok else "FAIL", os.path.basename(path), k, lvl,
                "all in place" if not bad else "WRONG %s" % bad[:3], fmt), flush=True)
        manifest["files"].append({"live": path, "migrated": migrated,
                                  "live_sha1": hashlib.sha1(open(path, "rb").read()).hexdigest()})
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print("%d copies, %d failed" % (manifest["copies"], manifest["fails"]))


main()
