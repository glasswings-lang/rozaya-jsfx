#!/usr/bin/env python3
"""The Morpher R26/R27 migration, measured on every live instance BEFORE anything is written.

For each of the files tools/morpher_migrate_r26r27_20260916.files() finds, the migrated text is
built into a temp folder (live files are only READ). Then, per instance, with the per-load
rand() scramble pinned in test copies (`_tp = 0.25`, as every Morpher tool does):

  sound     the pre-build Morpher on the ORIGINAL file == the new Morpher on the MIGRATED copy,
            8 s of silence in, byte-for-byte
  controls  every old control's loaded value == its new slot's (the target pickers through the
            87 -> 107 map, High cut's old 20000 off -> 0), and Transport unit seeded
  format    the migrated blob is 7700107

Writes the migrated copies and a manifest to --out DIR, which `apply` in the migration tool uses.

    python tools/morpher_r26r27_checks/verify_live.py --out DIR [--jobs N] [--only NAME]
"""
import concurrent.futures as cf, hashlib, json, os, re, subprocess, sys, tempfile

if os.name == "nt":   # Idle priority, inherited by every render (memory: heavy renders at Idle)
    import ctypes
    k = ctypes.windll.kernel32
    k.GetCurrentProcess.restype = ctypes.c_void_p
    k.SetPriorityClass.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    k.SetPriorityClass(k.GetCurrentProcess(), 0x40)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_migrate_r26r27_20260916 as mig
from rpp_sliders import parse_line

OUT = sys.argv[sys.argv.index("--out") + 1]
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 6
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
os.makedirs(OUT, exist_ok=True)
tmp = tempfile.mkdtemp()


def pinned(src_text, name):
    if src_text.count("_tp = time_precise();") != 1:
        raise SystemExit("cannot pin " + name)
    d = os.path.join(tmp, name)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, mig.FX)
    open(p, "w", encoding="utf-8", newline="").write(src_text.replace("_tp = time_precise();", "_tp = 0.25;"))
    return p


PRE = mig.pre_plugin(tmp)
PRE_PIN = pinned(open(PRE, encoding="utf-8").read(), "pre_pin")
NEW_PIN = pinned(open(os.path.join(ROOT, "src", mig.FX), encoding="utf-8").read(), "new_pin")


def render(plug, rpp, inst, out):
    subprocess.run([mig.EXE, plug, "--rpp", rpp, "--fx", "spectral_vowel_morpher", "--instance", str(inst),
                    "--seconds", "8", "--csv", out, "--quiet"], capture_output=True)
    return open(out, "rb").read() if os.path.exists(out) else b""


def listing(plug, rpp, inst):
    r = subprocess.run([mig.EXE, plug, "--rpp", rpp, "--fx", "spectral_vowel_morpher", "--instance", str(inst),
                        "--list"], capture_output=True, text=True).stdout
    d = {}
    for line in r.splitlines():
        m = re.match(r"\s+slider(\d+)\s+.*\] = (\S+)", line)
        if m:
            d[int(m.group(1))] = m.group(2)
    return d


def check_instance(orig, new_file, inst, key):
    a = render(PRE_PIN, orig, inst, os.path.join(tmp, key + "_old.csv"))
    b = render(NEW_PIN, new_file, inst, os.path.join(tmp, key + "_new.csv"))
    sound_ok = len(a) > 1000 and a == b
    sounding = any(abs(float(r.split(b",")[2])) > 0 for r in b.splitlines()[1:2000:7]) if b else False
    lo, ln = listing(PRE_PIN, orig, inst), listing(NEW_PIN, new_file, inst)
    bad = []
    if len(lo) != 64 or len(ln) != 79:
        bad.append("listed %d old / %d new controls" % (len(lo), len(ln)))
    for o, n in mig.MAP.items():
        if o not in lo or n not in ln:
            continue
        want = lo[o]
        if o in (46, 56):
            want = str(mig.T107.get(int(float(lo[o])), 0))
        if o == 25 and float(lo[o]) >= 20000:
            want = "0"
        if abs(float(want) - float(ln[n])) > 1e-6 * max(1.0, abs(float(want))):
            bad.append("slider %d -> %d: %s vs %s" % (o, n, want, ln[n]))
    seed = "2" if float(lo.get(9, 1)) >= 3 else "0"
    if float(ln.get(52, -1)) != float(seed):
        bad.append("Transport unit %s, expected %s" % (ln.get(52), seed))
    return key, sound_ok, sounding, bad


def main():
    manifest = {"files": []}
    todo = []
    fails = 0
    for i, path in enumerate(mig.files()):
        if ONLY and ONLY not in path:
            continue
        text, notes = mig.convert_text(path, PRE, tmp)
        new_file = os.path.join(OUT, "%02d_%s" % (i, os.path.basename(path)))
        open(new_file, "w", encoding="utf-8", newline="").write(text)
        L = text.split("\n")
        for h in mig.heads(L):
            a, b = mig.blob_span(L, h + 1)
            if int(round(mig.struct.unpack("<f", mig.base64.b64decode(L[a].strip()[:8])[:4])[0])) != mig.NEW_MAGIC:
                print("FAIL format %s: a blob is not %d" % (path, mig.NEW_MAGIC)); fails += 1
        manifest["files"].append({"live": path, "migrated": new_file, "instances": len(notes),
                                  "old_magics": [m for _, m in notes],
                                  "live_sha1": hashlib.sha1(open(path, "rb").read()).hexdigest()})
        for n, _ in notes:
            todo.append((path, new_file, n, "%02d_%d" % (i, n)))
    print("%d files, %d instances converted into %s; measuring..." % (len(manifest["files"]), len(todo), OUT), flush=True)
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for key, sound_ok, sounding, bad in ex.map(lambda t: check_instance(*t), todo):
            ok = sound_ok and not bad
            fails += not ok
            path = next(t[0] for t in todo if t[3] == key)
            print("%s %s %s: sound %s (sounding %s)%s" % ("ok  " if ok else "FAIL", key, os.path.basename(path),
                  "identical" if sound_ok else "DIFFERENT", sounding, "; " + "; ".join(bad) if bad else ""), flush=True)
    manifest["fails"] = fails
    manifest["instances"] = len(todo)
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print("DONE: %d instances, %d failures" % (len(todo), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
