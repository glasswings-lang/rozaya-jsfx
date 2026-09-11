#!/usr/bin/env python3
"""Check the 2026-09-10 Sweeping Filter migration. Deliberately does NOT import
the migration's tables.

1. RENDER (the 45-layout instances in E:/reaper): the pre-migration build
   (git show a2ee1f1) on the SNAPSHOT project against the new src on the LIVE
   project, noise in, 30 s. Must be bit-identical and non-silent.
2. BY NAME (every instance): decode the old line with the OLD plugin's own
   declarations out of git, decode the new line with src's declarations, and
   compare control by control after the documented unit changes. Tensor's
   organic-movement is also compared, value for value, with Rozaya's copy of the
   same project that the 2026-09-05 migration produced.

    python tools/swf_verify_r22_20260910.py
"""
import glob, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
SNAP = "E:/reaper/finished/backups/snapshots/_pre-swf-r22-20260910"
SRC = os.path.join(ROOT, "src", "full-feature-sweeping-filter.jsfx")
FX = "full-feature-sweeping-filter"
DECL = re.compile(r"^slider(\d+):([^<]*)<([^>]*)>(.*)$")
OLD_COMMIT = {"45": "a2ee1f1", "23": "ae4a655", "22": "d19873f"}
_hz = {}
exec(subprocess.run(["git", "show", "bf81d1d:tools/sweepfilter_migrate_hz.py"], cwd=ROOT,
                    capture_output=True, text=True, check=True).stdout.replace(
                    'if __name__ == "__main__":', "if False:"), _hz)
HZ_MATCH = _hz["match"]

def names(text):
    out = {}
    for line in text.splitlines():
        d = DECL.match(line)
        if d:
            enum = re.search(r"\{(.*)\}", d.group(3))
            out[int(d.group(1))] = (d.group(4).strip(), enum.group(1).split(",") if enum else None)
    return out

def git(commit):
    return subprocess.run(["git", "show", f"{commit}:src/{FX}.jsfx"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout

def instances(path):
    L = open(path, encoding="utf-8", errors="replace").read().split("\n")
    return [parse_line(L[i + 1] + "\n") for i, l in enumerate(L) if "<JS " in l and FX in l]

def decode(slots, decl):
    out = {}
    for s, tok in slots.items():
        if tok in (None, "-") or s not in decl:
            continue
        name, enum = decl[s]
        out[name] = enum[int(float(tok))] if enum else float(tok)
    return out

def live_of(snapname):
    p = snapname.split("__")
    return "/".join([{"reaper": "E:/reaper", "tensors-rpp-projects": "E:/tensor's-rpp-projects"}[p[0]]] + p[1:])

# old control name -> new control name, as written in the layout docs
RENAME = {
    "Frequency Low Hz": "Low frequency (Hz / semitones / cents)",
    "Frequency High Hz": "High frequency (Hz / semitones / cents)",
    "Rate Value": "Rate Value (BPM / sec / Hz / beats per cycle / per beat)",
    "Pan Sweep Rate Unit": "Pan sweep rate mode",
    "Filter Speed Multiplier (Linked Sweep)": "Pan sweep every (cycles)",
    "Start Delay (in Rate Mode units)": "Start delay (in rate mode units)",
}

def main():
    fails = 0
    new_decl = names(open(SRC, encoding="utf-8").read())
    old_build = os.path.join(tempfile.gettempdir(), "swf_pre_r22.jsfx")
    open(old_build, "w", encoding="utf-8", newline="").write(git("a2ee1f1"))
    decl_cache = {k: names(git(c)) for k, c in OLD_COMMIT.items()}
    rozaya_organic = None
    for snapname in sorted(os.listdir(SNAP)):
        snap, live = os.path.join(SNAP, snapname), live_of(snapname)
        olds, news = instances(snap), instances(live)
        if len(olds) != len(news):
            print(f"FAIL {live}: {len(olds)} instances before, {len(news)} after"); fails += 1; continue
        tensor = snapname.startswith("tensors")
        for n, (o, w) in enumerate(zip(olds, news), 1):
            realcount = len([t for t in o.values() if t not in (None, "-")])
            key = "45" if not tensor else str(realcount)
            od, nd = decode(o, decl_cache[key]), decode(w, new_decl)
            if snapname.endswith("to-play-with-later__organic-movement.RPP"):
                rozaya_organic = rozaya_organic or []
                rozaya_organic.append(od)
            bad = []
            for name, v in od.items():
                nn = RENAME.get(name, name)
                if nn not in nd:
                    bad.append(f"{name} missing"); continue
                if tensor and name in ("Frequency Low Hz", "Frequency High Hz", "Resonance"):
                    continue          # peak-matched together; checked just below
                if tensor and name in ("Rate Mode", "Pan Sweep Rate Unit"):
                    if v != nd[nn]:
                        bad.append(f"{name}: {v} became {nd[nn]}")
                    continue
                if tensor and name == "Filter Speed Multiplier (Linked Sweep)":
                    if abs(1 / v - nd[nn]) > 1e-6:
                        bad.append(f"{name}: {v} became {nd[nn]}")
                    continue
                if name in ("Drift target", "Ramp target"):
                    if v.replace(" ", "").lower().replace("sweeprate", "ratevalue").replace("frequencylow", "lowfrequency").replace("frequencyhigh", "highfrequency") != nd[nn].replace(" ", "").lower():
                        bad.append(f"{name}: {v} became {nd[nn]}")
                    continue
                if v != nd[nn]:
                    bad.append(f"{name}: {v} became {nd[nn]}")
            if tensor:
                # Frequencies and Resonance, recomputed here from the OLD named values
                # with bf81d1d's match() -- the maths that migrated E:/reaper on
                # 2026-08-22 -- loaded independently of the migration script.
                new_lo, new_res = HZ_MATCH(od["Frequency Low Hz"], od["Resonance"])
                new_hi, _ = HZ_MATCH(od["Frequency High Hz"], od["Resonance"])
                want = {"Low frequency (Hz / semitones / cents)": float(int(round(new_lo))),
                        "High frequency (Hz / semitones / cents)": float(int(round(new_hi))),
                        "Resonance": float("%.3f" % new_res)}
                for k, v in want.items():
                    if nd.get(k) != v:
                        bad.append(f"{k}: wanted {v}, found {nd.get(k)}")
            for name, want in (("Low pitch mode", "Hz"), ("High pitch mode", "Hz"), ("Tuning reference (Hz)", 440.0)):
                if nd.get(name) != want:
                    bad.append(f"{name} is {nd.get(name)}")
            label = f"{os.path.basename(live)} #{n}"
            if bad:
                fails += 1
                print(f"FAIL by name {label}: " + "; ".join(bad[:4]))
            else:
                print(f"ok   by name {label}: {len(od)} controls")
            if tensor and snapname.endswith("organic-movement.RPP"):
                pass
            if not tensor:
                with tempfile.TemporaryDirectory() as tmp:
                    a, b = os.path.join(tmp, "a.csv"), os.path.join(tmp, "b.csv")
                    for plug, proj, out in ((old_build, snap, a), (SRC, live, b)):
                        subprocess.run([EXE, plug, "--rpp", proj, "--fx", FX, "--instance", str(n),
                                        "--input", "noise", "--seconds", "30", "--csv", out, "--quiet"],
                                       capture_output=True, check=True)
                    A, B = open(a).read(), open(b).read()
                    loud = any(r.split(",")[2] not in ("0", "-0") for r in A.splitlines()[1:40000:97])
                    ok = A == B and loud
                    fails += not ok
                    print(f"{'ok  ' if ok else 'FAIL'} render  {label}: "
                          f"{'bit-identical' if A == B else 'DIFFERENT'}, {'non-silent' if loud else 'SILENT'}")
    # Tensor's organic-movement against Rozaya's already-migrated copy
    t_new = instances("E:/tensor's-rpp-projects/organic-movement.RPP")
    r_new = instances("E:/reaper/to-play-with-later/organic-movement.RPP")
    for n, (t, r) in enumerate(zip(t_new, r_new), 1):
        td, rd = decode(t, new_decl), decode(r, new_decl)
        diff = {k: (td.get(k), rd.get(k)) for k in set(td) | set(rd) if td.get(k) != rd.get(k)}
        fails += bool(diff)
        print(f"{'FAIL' if diff else 'ok  '} Tensor's organic-movement #{n} equals Rozaya's migrated copy"
              + (f": {diff}" if diff else f", all {len(td)} controls"))
    print(f"\n{'ALL PASS' if not fails else f'{fails} FAILURES'}")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
