#!/usr/bin/env python3
"""The Morpher -> Passage carry-over, measured on every live Morpher copy BEFORE anything is written.

For each file tools/morpher_migrate_r26r27_20260916.files() finds, the carried text is built into
--out (live files are only READ). Then, per copy, rand() pinned in every test copy (`_tp = 0.25`):

  each slot   the Morpher (src, its auto-gain restarted on the slot switch) auditioning that slot alone
              against Passage auditioning the same slot of the carried copy, 3.5 s each, level from 1 s
              in: within 1 dB. This is
              what the Output level offsets and the layer rebase have to get right.
  as saved    12 s of each as saved: overall level within 2 dB. The two walk the slots in different
              random orders, so only the overall level is comparable, and the Morpher's auto-gain filled
              in the dip halfway through a crossfade that Passage now lets through (back-to-life: each
              slot within 0.3 dB, as saved 0.7-1.5 dB quieter).
  controls    every Morpher control's loaded value in its Passage slot: the pickers through the 111
              list, Layer level and Output level as the carry changed them, Auto-morph timing on Rate.
  format      the carried blob is 7700009 and the <JS line names Passage.

    python tools/passage_takeover_checks/verify_morpher_carry.py --out DIR [--only NAME]
"""
import ctypes, hashlib, json, math, os, subprocess, sys, tempfile
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_to_passage_takeover_20260916 as mc
import morpher_migrate_r26r27_20260916 as mm
import passage_migrate_takeover_20260916 as pm
from rpp_sliders import parse_line

OUT = sys.argv[sys.argv.index("--out") + 1]
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
# --part I/N: this run takes every Nth file starting at I (0-based); --merge N joins the parts' manifests.
PART = tuple(map(int, sys.argv[sys.argv.index("--part") + 1].split("/"))) if "--part" in sys.argv else None
os.makedirs(OUT, exist_ok=True)
work = tempfile.mkdtemp(dir=OUT)
EXE = pm.EXE


def pinned(text, name, fname):
    if text.count("_tp = time_precise();") != 1:
        raise SystemExit("cannot pin " + name)
    d = os.path.join(work, name); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, fname)
    open(p, "w", encoding="utf-8", newline="").write(text.replace("_tp = time_precise();", "_tp = 0.25;"))
    return p


if "--merge" in sys.argv:
    n = int(sys.argv[sys.argv.index("--merge") + 1])
    parts = [json.load(open(os.path.join(OUT, "manifest_part%d.json" % i))) for i in range(n)]
    merged = {"files": sum((p["files"] for p in parts), []), "copies": sum(p["copies"] for p in parts),
              "fails": sum(p["fails"] for p in parts)}
    if len(merged["files"]) != len(mm.files()):
        raise SystemExit("REFUSED: the parts hold %d files, not %d" % (len(merged["files"]), len(mm.files())))
    json.dump(merged, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print("%d files, %d copies, %d failed" % (len(merged["files"]), merged["copies"], merged["fails"]))
    sys.exit(0)

M_SRC = open(os.path.join(ROOT, "src", "spectral_vowel_morpher.jsfx"), encoding="utf-8", newline="").read()
P_SRC = open(os.path.join(ROOT, "src", "spectral_vowel_passage.jsfx"), encoding="utf-8", newline="").read()
M_PIN = pinned(M_SRC, "m", "spectral_vowel_morpher.jsfx")
P_PIN = pinned(P_SRC, "p", "spectral_vowel_passage.jsfx")
PROBE = mc.probe_plugin(work)
LEVEL = mc.level_probe(work)
READER = os.path.join(work, "reader", "spectral_vowel_passage.jsfx")
os.makedirs(os.path.dirname(READER), exist_ok=True)
open(READER, "w", encoding="utf-8", newline="").write(mc.carry_reader(P_SRC))


def rms_csv(path, a, b):
    x = np.loadtxt(path, delimiter=",", skiprows=1)[:, 2:]
    seg = x[int(a * 44100):int(b * 44100)]
    return math.sqrt((seg ** 2).mean()) if len(seg) else 0.0


def render(plug, rpp, fx, inst, secs, csv, extra=()):
    if os.path.exists(csv):
        os.remove(csv)
    subprocess.run([EXE, plug, "--rpp", rpp, "--fx", fx, "--instance", str(inst), "--seconds", str(secs), "--quiet",
                    "--csv", csv, *extra], capture_output=True)
    return os.path.exists(csv)


def loaded_line(plug, rpp, fx, inst):
    out = os.path.join(work, "loaded.RPP")
    if os.path.exists(out):
        os.remove(out)
    subprocess.run([EXE, plug, "--rpp", rpp, "--fx", fx, "--instance", str(inst), "--seconds", "0.05", "--quiet",
                    "--save-rpp", out], capture_output=True)
    L = open(out, encoding="utf-8").read().split("\n")
    return L[[i for i, l in enumerate(L) if "<JS" in l and "<JS_SER" not in l][0] + 1]


def db(a, b):
    return 20 * math.log10(max(b, 1e-9) / max(a, 1e-9))


def controls(m_line, p_line, note):
    o, n = parse_line(m_line), parse_line(p_line)
    bad = []
    shown_slot = int(round(pm.num(o.get(1), 1))); shown_slot = 0 if shown_slot == 0 else shown_slot - 1
    for mk, pk in mc.M2P.items():
        ov, nv = o.get(mk), n.get(pk)
        if ov is None:
            continue
        want = pm.num(ov, None)
        if mk in (58, 70):
            want = float(mc.t_m2p(int(round(want))))
        elif mk == 51:   # Output level, the shown slot's offset
            off = note["offsets_db"].get(str(shown_slot + 1))
            want = want if (want <= -60 or off is None) else min(24.0, want + off)
        elif mk == 46 and note["rebased_from_db"] is not None:   # Layer level, rebased
            shown_layer = int(round(pm.num(o.get(40), 1)))
            want = 0.0 if shown_layer <= 1 else (want if want <= -60 else want - note["rebased_from_db"])
        got = pm.num(nv, None)
        if want is None or got is None or abs(want - got) > 0.002:
            bad.append((mk, pk, ov, nv, want))
    if pm.num(n.get(8), -1) != 1:
        bad.append(("timing", 8, None, n.get(8), 1))
    return bad


def main():
    manifest = {"files": [], "copies": 0, "fails": 0}
    for fi, path in enumerate(mm.files()):
        if ONLY and ONLY not in path:
            continue
        if PART and fi % PART[1] != PART[0]:
            continue
        print(os.path.basename(path), flush=True)
        text, notes = mc.convert_file(path, work, PROBE, READER, log=lambda s: print(s, flush=True),
                                      level_plug=LEVEL, passage_pin=P_PIN)
        migrated = os.path.join(OUT, os.path.basename(path))
        open(migrated, "w", encoding="utf-8", newline="").write(text)
        ML = open(migrated, encoding="utf-8").read().split("\n")
        heads = [i for i, l in enumerate(ML) if "<JS" in l and "spectral_vowel_passage" in l and "<JS_SER" not in l]
        if any("spectral_vowel_morpher" in l for l in ML if "<JS" in l):
            raise SystemExit("REFUSED: a Morpher <JS line is left in %s" % migrated)
        # The carried copies are the Passage copies in the file, in order, after any Passage copies it already had.
        orig = open(path, encoding="utf-8", errors="replace").read().split("\n")
        n_passage_before = sum(1 for l in orig if "<JS" in l and "spectral_vowel_passage" in l and "<JS_SER" not in l)
        order = []   # carried copy k -> its Passage instance number in the migrated file
        seen_m, seen_p = 0, 0
        for l in orig:
            if "<JS" in l and "<JS_SER" not in l and ("spectral_vowel_morpher" in l or "spectral_vowel_passage" in l):
                seen_p += 1
                if "spectral_vowel_morpher" in l:
                    seen_m += 1; order.append(seen_p)
        for k, note in enumerate(notes, start=1):
            manifest["copies"] += 1
            pinst = order[k - 1]
            blob_ok = True
            a, b = pm.blob_span(ML, heads[pinst - 1] + 1)
            blob_ok = int(round(pm.unpack("".join(x.strip() for x in ML[a:b]))[0])) == 7700009
            bad = controls(loaded_line(M_PIN, path, "spectral_vowel_morpher", k),
                           loaded_line(P_PIN, migrated, "spectral_vowel_passage", pinst), note)
            worst_slot, slot_notes = 0.0, []
            for s in range(note["n_used"]):
                lm = mc.slot_level(LEVEL, path, "spectral_vowel_morpher", k, s, work, secs=3.5)
                lp = mc.slot_level(P_PIN, migrated, "spectral_vowel_passage", pinst, s, work, secs=3.5)
                if not lm or not lp:
                    worst_slot = 99 if (lm or lp) else worst_slot; slot_notes.append("slot %d silent in %s" % (s + 1, "both" if not (lm or lp) else ("the Morpher" if not lm else "Passage"))); continue
                d = db(lm, lp)
                worst_slot = max(worst_slot, abs(d)); slot_notes.append("%+.2f" % d)
            okm = render(M_PIN, path, "spectral_vowel_morpher", k, 12, os.path.join(work, "ma.csv"))
            okp = render(P_PIN, migrated, "spectral_vowel_passage", pinst, 12, os.path.join(work, "pa.csv"))
            saved_d = db(rms_csv(os.path.join(work, "ma.csv"), 2, 12), rms_csv(os.path.join(work, "pa.csv"), 2, 12)) if okm and okp else 99
            ok = blob_ok and not bad and worst_slot <= 1.0 and abs(saved_d) <= 2.0
            manifest["fails"] += 0 if ok else 1
            print("%s %s copy %d: each slot %s dB; as saved %+.2f dB; controls %s; blob %s" % (
                "PASS" if ok else "FAIL", os.path.basename(path), k, " ".join(slot_notes) or "(none captured)", saved_d,
                "all in place" if not bad else "WRONG %s" % bad[:4], "7700009" if blob_ok else "WRONG"), flush=True)
        manifest["files"].append({"live": path, "migrated": migrated,
                                  "live_sha1": hashlib.sha1(open(path, "rb").read()).hexdigest()})
    name = "manifest.json" if not PART else "manifest_part%d.json" % PART[0]
    json.dump(manifest, open(os.path.join(OUT, name), "w"), indent=1)
    print("%d copies, %d failed" % (manifest["copies"], manifest["fails"]), flush=True)


main()
