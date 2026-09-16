#!/usr/bin/env python3
"""The Passage takeover migration, measured on every live instance BEFORE anything is written.

For each file tools/passage_migrate_takeover_20260916.files() finds, the migrated text is built
into --out (live files are only READ). Then, per instance, with the per-load rand() scramble pinned
(`_tp = 0.25`) in both test copies, 10 s of silence in:

  sound     the ORIGINAL Passage (48e3771) on the original file against the NEW Passage on the
            migrated copy. Bit-identical passes. Otherwise it passes when the difference sits at
            least 40 dB under the signal (the voice engine's tables, the wash gain now fixed
            instead of chased) AND no 1 s window's level differs by more than 1 dB.
  controls  every old control's value in its new slot: the pickers through the 111 map, High cut's
            20000 off -> 0, Output level raised by the displayed slot's offset (capped at +24)
  format    the migrated blob is 7700009

Writes the migrated copies and manifest.json to --out, which `apply` in the migration tool reads.

    python tools/passage_takeover_checks/verify_live.py --out DIR --survey wash_gain.json [--only NAME]
"""
import ctypes, hashlib, json, math, os, subprocess, sys, tempfile
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import passage_migrate_takeover_20260916 as mig
from rpp_sliders import parse_line

OUT = sys.argv[sys.argv.index("--out") + 1]
SURVEY = json.load(open(sys.argv[sys.argv.index("--survey") + 1]))
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
os.makedirs(OUT, exist_ok=True)
work = tempfile.mkdtemp(dir=OUT)


def pinned(text, name):
    if text.count("_tp = time_precise();") != 1:
        raise SystemExit("cannot pin " + name)
    d = os.path.join(work, name); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, mig.FX + ".jsfx")
    open(p, "w", encoding="utf-8", newline="").write(text.replace("_tp = time_precise();", "_tp = 0.25;"))
    return p


OLD_PIN = pinned(subprocess.run(["git", "show", mig.PRE_COMMIT + ":src/" + mig.FX + ".jsfx"], cwd=ROOT,
                                capture_output=True).stdout.decode("utf-8"), "old")
NEW_PIN = pinned(open(os.path.join(ROOT, "src", mig.FX + ".jsfx"), encoding="utf-8", newline="").read(), "new")


def render(plug, rpp, inst, out):
    if os.path.exists(out):
        os.remove(out)
    subprocess.run([mig.EXE, plug, "--rpp", rpp, "--fx", mig.FX, "--instance", str(inst), "--seconds", "10",
                    "--csv", out, "--quiet"], capture_output=True)
    return open(out, "rb").read() if os.path.exists(out) else b""


def instance_lines(path):
    L = open(path, encoding="utf-8", errors="replace").read().split("\n")
    out = []
    for h in mig.heads(L):
        a, b = mig.blob_span(L, h + 1)
        out.append((L[h + 1], mig.unpack("".join(x.strip() for x in L[a:b]))))
    return out


def controls_ok(old_line, new_line, offs):
    """Every old control in its new slot, with the three changes the migration makes on purpose."""
    o, n = parse_line(old_line), parse_line(new_line)
    bad = []
    shown = int(round(mig.num(o.get(1), 1)))
    shown = 0 if shown == 0 else shown - 1   # All shows Slot 1
    for oid, nid in mig.MAP.items():
        ov, nv = o.get(oid), n.get(nid)
        if ov is None:
            continue
        if oid == 18:
            want = 0.0 if mig.num(ov, 20000) >= 19999.5 else mig.num(ov, 0)
        elif oid in (44, 55):
            want = float(mig.T111[int(round(mig.num(ov, 0)))])
        elif oid == 29:
            base = mig.num(ov, 0)
            want = base if (base <= -60 or shown not in offs) else min(24.0, base + offs[shown])
        else:
            want = mig.num(ov, None)
        got = mig.num(nv, None)
        if want is None or got is None or abs(want - got) > 0.0015:
            bad.append((oid, nid, ov, nv, want))
    return bad


def main():
    gain = mig.wash_gain_db(open(os.path.join(ROOT, "src", mig.FX + ".jsfx"), encoding="utf-8").read())
    manifest = {"files": [], "instances": 0, "fails": 0, "wash_gain_db": gain}
    for path in mig.files():
        if ONLY and ONLY not in path:
            continue
        text, notes = mig.convert_file(path, SURVEY, work)
        migrated = os.path.join(OUT, os.path.basename(path))
        open(migrated, "w", encoding="utf-8", newline="").write(text)
        old_i, new_i = instance_lines(path), instance_lines(migrated)
        assert len(old_i) == len(new_i) == len(notes)
        for k, note in enumerate(notes, start=1):
            manifest["instances"] += 1
            offs = {int(s) - 1: v for s, v in note["offsets_db"].items()}
            fmt = int(round(new_i[k - 1][1][0]))
            bad = controls_ok(old_i[k - 1][0], new_i[k - 1][0], offs)
            a = render(OLD_PIN, path, k, os.path.join(work, "o.csv"))
            b = render(NEW_PIN, migrated, k, os.path.join(work, "n.csv"))
            if a == b and len(a) > 100:
                sound, ok_sound = "bit-identical", True
            elif len(a) < 100 or len(b) < 100:
                sound, ok_sound = "a render failed", False
            else:
                x = np.loadtxt(os.path.join(work, "o.csv"), delimiter=",", skiprows=1)[:, 2:]
                y = np.loadtxt(os.path.join(work, "n.csv"), delimiter=",", skiprows=1)[:, 2:]
                m = min(len(x), len(y)); x, y = x[:m], y[:m]
                rx = math.sqrt((x ** 2).mean())
                diff = 20 * math.log10(math.sqrt(((x - y) ** 2).mean()) / max(rx, 1e-12) + 1e-30)
                worst = 0.0
                for i in range(44100, m - 44100, 44100):
                    wa = math.sqrt((x[i:i + 44100] ** 2).mean()); wb = math.sqrt((y[i:i + 44100] ** 2).mean())
                    if wa > 1e-5 or wb > 1e-5:
                        worst = max(worst, abs(20 * math.log10(max(wb, 1e-9) / max(wa, 1e-9))))
                ok_sound = diff <= -40 or worst <= 1.0
                ok_sound = ok_sound and worst <= 1.0
                sound = "difference %.1f dB under the signal, largest 1 s level change %.2f dB" % (diff, worst)
            ok = ok_sound and not bad and fmt == mig.NEW_MAGIC
            manifest["fails"] += 0 if ok else 1
            print("%s %s #%d: %s; controls %s; blob %d; Output level offsets %s" % (
                "PASS" if ok else "FAIL", os.path.basename(path), k, sound,
                "all in place" if not bad else "WRONG %s" % bad[:4], fmt, note["offsets_db"] or "none"), flush=True)
        manifest["files"].append({"live": path, "migrated": migrated,
                                  "live_sha1": hashlib.sha1(open(path, "rb").read()).hexdigest()})
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print("%d instances, %d failed" % (manifest["instances"], manifest["fails"]))


main()
