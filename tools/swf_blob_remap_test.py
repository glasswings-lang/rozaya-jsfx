#!/usr/bin/env python3
"""The Sweeping Filter's old-save remap, proven on targets no real project uses.

Only Sweep Rate, Frequency Low and Frequency High carry drift or ramp in the
library, so the render check over real projects cannot see whether Pan Sweep
Rate, Resonance and Wet/Dry land in the right place when an old save loads. This
builds synthetic OLD projects that do use them -- a real snapshot project with
its first Sweeping Filter's value line and blob replaced -- migrates each with
the real migration's convert(), and requires the pre-migration build on the
synthetic project to render bit-identically to the new build on its migration.

Covers both old magics (2100006 and 2200006), drift AND ramp, every one of the
six old targets, and the selectors pointing at a target other than 0.

    python tools/swf_blob_remap_test.py
"""
import base64, os, struct, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import swf_migrate_r22_20260910 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
SRC = os.path.join(ROOT, "src", "full-feature-sweeping-filter.jsfx")
BASE = os.path.join(mig.SNAP, "reaper__finished__strangeness.RPP")
FX = "full-feature-sweeping-filter"

# 45-layout slider values: pan on in Pan Sweep (10) so pan rate is audible, wet
# 0.5 so wet/dry is, resonance 0.5, a fast 30 BPM sweep, 1-second drift periods.
def line45(drift_t, ramp_t):
    v = {1: 300, 2: 3000, 3: 0.5, 5: 30, 6: 0, 8: 50, 9: 100, 16: 1, 17: 10, 18: 1, 19: 5,
         20: 8, 21: 20, 22: 0, 23: 1, 24: 0.5, 30: drift_t, 31: 0, 32: 0, 33: 1, 34: 1,
         35: 0, 38: ramp_t, 39: 0, 40: 1, 41: 0.1, 44: 1}
    return " ".join(str(v.get(i, "-")) for i in range(1, 65))

def blob(magic, cfg, last_d, last_r):
    """cfg: {old target: (drift up, drift down, ramp by, ramp dur)}"""
    up = [cfg.get(t, (0, 0, 0, 0))[0] for t in range(6)]
    dn = [cfg.get(t, (0, 0, 0, 0))[1] for t in range(6)]
    per = [1] * 6
    shp = [t % 2 for t in range(6)]
    by = [cfg.get(t, (0, 0, 0, 0))[2] for t in range(6)]
    dur = [cfg.get(t, (0, 0, 0, 0))[3] for t in range(6)]
    dly = [0] * 6
    vals = [magic] + up + dn + per + shp + [last_d] + by + dur + dly
    if magic == 2200006:
        vals += [0] * 24
    vals += [last_r]
    return base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode()

def synth(path, magic, cfg, last_d, last_r):
    L = open(BASE, encoding="utf-8", newline="").read().split("\n")
    i = next(i for i, l in enumerate(L) if "<JS " in l and FX in l)
    indent = L[i + 1][: len(L[i + 1]) - len(L[i + 1].lstrip())]
    cr = "\r" if L[i + 1].endswith("\r") else ""
    L[i + 1] = indent + line45(last_d, last_r) + cr
    k = next(k for k in range(i + 2, i + 6) if "<JS_SER" in L[k])
    j = k + 1
    while L[j].strip() != ">":
        j += 1
    L[k + 1:j] = [indent + blob(magic, cfg, last_d, last_r) + cr]
    open(path, "w", encoding="utf-8", newline="").write("\n".join(L))

CASES = [
    ("pan sweep rate drift, v1", 2100006, {3: (15, 15, 0, 0)}, 3, 0),
    ("resonance drift, v2", 2200006, {4: (0.4, 0.4, 0, 0)}, 4, 0),
    ("wet/dry drift, v1", 2100006, {5: (0.4, 0.4, 0, 0)}, 5, 0),
    ("pan sweep rate ramp, v2", 2200006, {3: (0, 0, 40, 0.05)}, 0, 3),
    ("resonance ramp, v1", 2100006, {4: (0, 0, 0.45, 0.05)}, 0, 4),
    ("wet/dry ramp, v2", 2200006, {5: (0, 0, -0.4, 0.05)}, 0, 5),
    ("all six at once, v2", 2200006,
     {0: (10, 10, 5, 0.1), 1: (100, 50, 0, 0), 2: (500, 500, -800, 0.1),
      3: (10, 10, 0, 0), 4: (0.2, 0.2, 0.1, 0.1), 5: (0.2, 0.2, 0, 0)}, 2, 4),
]

def render(plugin, proj, out):
    subprocess.run([EXE, plugin, "--rpp", proj, "--fx", FX, "--instance", "1", "--input", "noise",
                    "--seconds", "12", "--csv", out, "--quiet"], check=True, capture_output=True)
    return open(out).read()

def main():
    old_build = os.path.join(tempfile.gettempdir(), "swf_pre_r22_blobtest.jsfx")
    open(old_build, "w", encoding="utf-8", newline="").write(subprocess.run(
        ["git", "show", "a2ee1f1:src/full-feature-sweeping-filter.jsfx"], cwd=ROOT,
        capture_output=True, text=True, check=True).stdout)
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, magic, cfg, ld, lr in CASES:
            old_p, new_p = os.path.join(tmp, "old.RPP"), os.path.join(tmp, "new.RPP")
            synth(old_p, magic, cfg, ld, lr)
            text, n, _ = mig.convert(old_p, mig.L45, dry=True)
            open(new_p, "w", encoding="utf-8", newline="").write(text)
            a = render(old_build, old_p, os.path.join(tmp, "a.csv"))
            b = render(SRC, new_p, os.path.join(tmp, "b.csv"))
            # the configuration must matter, or the comparison proves nothing
            synth(old_p, magic, {}, ld, lr)
            base = render(old_build, old_p, os.path.join(tmp, "c.csv"))
            matters = a != base
            ok = a == b and matters
            fails += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name:28} old save loads bit-identical: {a == b}; "
                  f"the drift/ramp audibly matters: {matters}")
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
