#!/usr/bin/env python3
"""Sweep Dwell's migration, measured on every live copy BEFORE anything is written.

The migrated text is built into --out (live files are only READ). Then, per copy:

  sound     the OLD build on the original project against the NEW build on the migrated
            copy, 30 s. Nothing in this turn is meant to change a saved sound, so the two
            must be bit-identical.
  controls  every old control's value in its new slot, with the four changes the migration
            makes on purpose (the three percents, the pan choice and its direction, the
            transport unit, the per-target banks).
  format    the migrated blob is 2600018, and the plugin loads it without losing anything:
            the values it SHOWS after loading are the ones the migration wrote.

    python tools/sweep_dwell_checks/verify_live.py --out DIR
"""
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sdf_migrate_r26r27_20260917 as mig
from rpp_sliders import parse_line

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "sweep-dwell-filter"
OUT = sys.argv[sys.argv.index("--out") + 1]
os.makedirs(OUT, exist_ok=True)
work = tempfile.mkdtemp(dir=OUT)

OLD = os.path.join(work, "old.jsfx")
open(OLD, "wb").write(subprocess.run(["git", "show", "HEAD:src/%s.jsfx" % FX], cwd=ROOT,
                                     capture_output=True).stdout)
NEW = os.path.join(ROOT, "src", "%s.jsfx" % FX)


def render(plug, rpp, inst, secs=30):
    csv = os.path.join(work, "r.csv")
    if os.path.exists(csv):
        os.remove(csv)
    subprocess.run([EXE, plug, "--rpp", rpp, "--fx", FX, "--instance", str(inst), "--input", "noise",
                    "--seconds", str(secs), "--quiet", "--csv", csv], capture_output=True)
    return open(csv, "rb").read() if os.path.exists(csv) else b""


def loaded_line(plug, rpp, inst):
    """What the plugin SHOWS once the project has loaded -- the blob can overwrite the line."""
    out = os.path.join(work, "loaded.RPP")
    if os.path.exists(out):
        os.remove(out)
    subprocess.run([EXE, plug, "--rpp", rpp, "--fx", FX, "--instance", str(inst), "--seconds", "0.05",
                    "--quiet", "--save-rpp", out], capture_output=True)
    L = open(out, encoding="utf-8").read().split("\n")
    return L[[i for i, l in enumerate(L) if "<JS" in l and "<JS_SER" not in l][0] + 1]


def controls(old_line, new_line, ob):
    """Every old control in its new slot, with the changes the migration makes on purpose."""
    o, n = parse_line(old_line), parse_line(new_line)
    bad = []
    for oid, nid in mig.MOVE.items():
        if o.get(oid) in (None, "-"):
            continue
        want, got = mig.num(o, oid), mig.num(n, nid)
        if abs(want - got) > 0.002:
            bad.append(("moved", oid, nid, want, got))
    for oid, nid in mig.PERCENT.items():
        want, got = mig.num(o, oid) * 100, mig.num(n, nid)
        if abs(want - got) > 0.002:
            bad.append(("percent", oid, nid, want, got))
    mode, flip = mig.PAN[int(round(mig.num(o, 16)))]
    if int(round(mig.num(n, 16))) != mode or int(round(mig.num(n, 17))) != flip:
        bad.append(("pan", 16, 16, (mode, flip), (mig.num(n, 16), mig.num(n, 17))))
    cyc = sum(mig.len_secs(int(ob["lmode"][s]), ob["len"][s]) for s in range(mig.N_SEG))
    unit, delay, play, rest = mig.transport_unit(mig.num(o, 25), mig.num(o, 24),
                                                 mig.num(o, 26), mig.num(o, 27), cyc)
    for nid, want in ((26, unit), (27, delay), (28, play), (29, rest)):
        if abs(mig.num(n, nid) - want) > 0.002:
            bad.append(("transport", None, nid, want, mig.num(n, nid)))
    # The per-target units the migration seeded: what the plugin shows for the shown target.
    if abs(mig.num(n, 37) - mig.num(o, 34)) > 0.002:
        bad.append(("drift period unit", 34, 37, mig.num(o, 34), mig.num(n, 37)))
    if abs(mig.num(n, 46) - mig.num(o, 40)) > 0.002:
        bad.append(("ramp time unit", 40, 46, mig.num(o, 40), mig.num(n, 46)))
    if int(round(mig.num(n, 38))) != 1:
        bad.append(("movement mode", None, 38, 1, mig.num(n, 38)))
    return bad


def main():
    manifest = {"files": [], "copies": 0, "fails": 0}
    for path in mig.files():
        text, count = mig.convert_file(path)
        migrated = os.path.join(OUT, os.path.basename(path))
        open(migrated, "wb").write(text.encode("utf-8"))
        src = open(path, encoding="utf-8", errors="replace").read().split("\n")
        heads = [i for i, l in enumerate(src) if re.search(r"<JS\s+glasswings/%s\.jsfx" % FX, l)]
        for k in range(1, count + 1):
            manifest["copies"] += 1
            ob = mig.read_old(mig.blob_span(src, heads[k - 1] + 2)[2])
            bad = controls(loaded_line(OLD, path, k), loaded_line(NEW, migrated, k), ob)
            ml = open(migrated, encoding="utf-8").read().split("\n")
            mh = [i for i, l in enumerate(ml) if re.search(r"<JS\s+glasswings/%s\.jsfx" % FX, l)]
            fmt = int(round(mig.blob_span(ml, mh[k - 1] + 2)[2][0]))
            a, b = render(OLD, path, k), render(NEW, migrated, k)
            same = a == b and len(a) > 100
            ok = same and not bad and fmt == mig.NEW_MAGIC
            manifest["fails"] += 0 if ok else 1
            print("%s %s copy %d: %s; controls %s; blob %d" % (
                "PASS" if ok else "FAIL", os.path.basename(path), k,
                "bit-identical" if same else ("SOUNDS DIFFERENT" if len(a) > 100 and len(b) > 100 else "a render failed"),
                "all in place" if not bad else "WRONG %s" % bad[:4], fmt), flush=True)
        manifest["files"].append({"live": path, "migrated": migrated,
                                  "live_sha1": hashlib.sha1(open(path, "rb").read()).hexdigest()})
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print("%d copies, %d failed" % (manifest["copies"], manifest["fails"]))


main()
