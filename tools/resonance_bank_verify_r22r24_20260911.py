#!/usr/bin/env python3
"""Resonance Bank's 2026-09-11 build, measured. docs/layouts/resonance-bank-r22-r24.md.

1  projects   the pre-change build (a993f0f) on each snapshot project against
              the new build on that project migrated IN A TEMP COPY: bit-identical
              and not silent; then every control decoded by NAME from both --list
              outputs, target selectors through the old -> new map.
2  old saves  synthetic v1 / v2 / v3 saves with drift and ramp on all five old
              targets across four bands, parallel and serial, one with a band
              soloed: old build on the save == new build on its migration, and the
              drift/ramp must matter (the same save without it renders differently).
3  targets    each of the 10 targets, by drift, changes the sound and stays finite;
              a ramp on each whole-plugin target does too; a whole-plugin target set
              from band 5 renders identically to the same set from band 0.
4  units      Frequency Semitones 69 == Cents 6900 == Hz 440; a width of 12
              semitones (and 1200 cents) == the same width typed in Hz; 7 semitones
              must NOT equal it.

    python tools/resonance_bank_verify_r22r24_20260911.py [projects|saves|targets|units]
"""
import base64, os, re, struct, subprocess, sys, tempfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import resonance_bank_migrate_r22r24_20260911 as mig

EXE = str(ROOT / "tools" / "jsfx_run" / "build" / "Release" / "jsfx_run.exe")
SRC = str(ROOT / "src" / "resonance_bank.jsfx")
OLD_COMMIT = "a993f0f"
SNAP = Path("E:/reaper/finished/backups/snapshots/_pre-rb-r22-20260911")
PROJECTS = [SNAP / "to-play-with-later" / "wind.RPP",
            SNAP / "test-projects" / "claude-testing002-bridge.RPP"]
FX = "resonance_bank"
fails = 0


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def run(plugin, out, seconds=12, rpp=None, stages=()):
    cmd = [EXE, plugin, "--input", "noise", "--seconds", str(seconds), "--csv", out, "--quiet"]
    if rpp:
        cmd += ["--rpp", str(rpp), "--fx", FX]
    for k, stage in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in stage:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))


def listing(plugin, rpp):
    r = subprocess.run([EXE, plugin, "--rpp", str(rpp), "--fx", FX, "--list"],
                       capture_output=True, text=True, check=True)
    out = {}
    for line in r.stdout.splitlines():
        m = re.match(r"\s*slider(\d+)\s+(.*?)\s+\[.*\] = (\S+)", line)
        if m:
            out[m.group(2)] = float(m.group(3))
    return out


# ---- 1 ----------------------------------------------------------------------
RENAMED = {"Frequency (Hz)": "Frequency (Hz / semitones / cents)",
           "Width up (Hz above center)": "Width up (Hz / semitones / cents)",
           "Width down (Hz below center)": "Width down (Hz / semitones / cents)"}
NEW_EXPECT = {"Tuning reference (Hz)": 440, "Pitch mode": 0, "Note name": 69, "Fine tune": 0,
              "Fine tune unit": 2, "Width up unit": 0, "Width down unit": 0}


def projects(old_build, tmp):
    for snap in PROJECTS:
        text, n, done, _ = mig.convert(snap)
        migrated = os.path.join(tmp, "migrated.RPP")
        open(migrated, "w", encoding="utf-8", errors="surrogateescape", newline="").write(text)
        a = run(old_build, os.path.join(tmp, "a.csv"), 40, snap)
        b = run(SRC, os.path.join(tmp, "b.csv"), 40, migrated)
        report(np.array_equal(a, b) and np.abs(a).max() > 0,
               f"{snap.name}: {done} of {n} migrated; old on snapshot == new on migrated over 40 s: "
               f"{np.array_equal(a, b)}; peak {np.abs(a).max():.4f}")
        lo, ln = listing(old_build, snap), listing(SRC, migrated)
        bad = []
        for name, v in lo.items():
            nn = RENAMED.get(name, name)
            want = mig.O2N[int(v)] if name in ("Drift target", "Ramp target") else v
            if nn not in ln or abs(ln[nn] - want) > 1e-9:
                bad.append(f"{name}: {v} -> {ln.get(nn)}")
        for name, want in NEW_EXPECT.items():
            if ln.get(name) != want:
                bad.append(f"new {name}: {ln.get(name)}, expected {want}")
        report(not bad and len(ln) == 35,
               f"{snap.name}: {len(lo)} old controls matched by name, 7 new ones as meant"
               + ("" if not bad else " -- " + "; ".join(bad)))


# ---- 2 ----------------------------------------------------------------------
BANDS = {0: (300, 0, 100, 80, -0.3, 1), 1: (1200, -6, 300, 200, 0, 2),
         2: (3000, 3, 500, 500, 0.4, 0), 3: (6000, -3, 400, 400, 0, 3)}
# (band, old target): (up, down, period, mode, shape, play, rest)
DRIFT = {(0, 0): (80, 40, 0.7, 1, 0, 0, 0), (0, 3): (4, 4, 1.3, 2, 2, 0, 0),
         (1, 1): (150, 100, 0.9, 1, 1, 1.25, 0.5), (1, 4): (0.5, 0.5, 90, 0, 0, 0, 0),
         (2, 2): (200, 200, 1.1, 1, 2, 0, 0), (3, 0): (500, 500, 2, 3, 1, 0, 0)}
# (band, old target): (by, duration, delay, play, rest)
RAMP = {(0, 3): (-6, 3, 0.5, 0, 0), (1, 0): (400, 4, 0, 1, 0.5),
        (2, 4): (-0.6, 2, 0, 0, 0), (3, 1): (300, 5, 0, 0, 0)}
LAST_D, LAST_R = [3, 1, 2, 0], [3, 0, 4, 1]


def old_blob(ver, with_mod, solo_band=None):
    def bank16(k, off):
        return [BANDS[b][k] if b in BANDS else off for b in range(16)]
    vals = [{1: 1016005, 2: 2016005, 3: 3016005}[ver]]
    vals += bank16(0, 500) + bank16(1, -60) + bank16(2, 250) + bank16(3, 250) + bank16(4, 0) + bank16(5, 0)
    vals += [LAST_D[b] if b < 4 else 0 for b in range(16)]
    dr = lambda k, off: [(DRIFT.get((s // 5, s % 5)) or [0, 0, 0, off, 0, 0, 0])[k]
                         if with_mod else (off if k == 3 else 0) for s in range(80)]
    vals += dr(0, 2) + dr(1, 2) + dr(2, 2) + dr(3, 2) + dr(4, 2)
    if ver >= 2:
        vals += dr(5, 2) + dr(6, 2)
        rp = lambda k: [(RAMP.get((s // 5, s % 5)) or [0] * 5)[k] if with_mod else 0 for s in range(80)]
        vals += rp(0) + rp(1) + rp(2) + rp(3) + rp(4)
        vals += [LAST_R[b] if b < 4 else 0 for b in range(16)]
    if ver == 3:
        vals += [1 if b == solo_band else 0 for b in range(16)]
    return base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode()


def old_project(path, ver, mode, with_mod, solo_band=None):
    b = 2
    f, g, wu, wd, pan, order = BANDS[b]
    line = {1: 3, 2: mode, 3: b, 4: f, 5: wu, 6: wd, 7: g, 8: pan, 9: order,
            10: int(solo_band == b), 11: 0.8, 12: 0.7, 13: LAST_D[b], 17: 1, 21: LAST_R[b],
            23: 0, 27: 1}
    vals = " ".join(str(line.get(i, "-")) for i in range(1, 65))
    blob = old_blob(ver, with_mod, solo_band)
    blob_lines = "\n".join("        " + blob[i:i + 128] for i in range(0, len(blob), 128))
    open(path, "w", newline="").write(
        "<REAPER_PROJECT 0.1 \"7.0\" 0\n  <TRACK\n    <FXCHAIN\n"
        "      <JS glasswings/resonance_bank.jsfx \"\"\n        " + vals + "\n      >\n"
        "      <JS_SER\n" + blob_lines + "\n      >\n    >\n  >\n>\n")


def saves(old_build, tmp):
    for name, ver, mode, solo in (("v3 parallel", 3, 0, None), ("v3 serial", 3, 1, None),
                                  ("v2 parallel", 2, 0, None), ("v1 parallel", 1, 0, None),
                                  ("v1 serial", 1, 1, None), ("v3 band 1 soloed", 3, 0, 1)):
        old_p, new_p, base_p = (os.path.join(tmp, x) for x in ("old.RPP", "new.RPP", "base.RPP"))
        old_project(old_p, ver, mode, True, solo)
        open(new_p, "w", newline="").write(mig.convert(Path(old_p))[0])
        old_project(base_p, ver, mode, False, solo)
        a = run(old_build, os.path.join(tmp, "a.csv"), 12, old_p)
        b = run(SRC, os.path.join(tmp, "b.csv"), 12, new_p)
        c = run(old_build, os.path.join(tmp, "c.csv"), 12, base_p)
        same, matters = np.array_equal(a, b), not np.array_equal(a, c)
        report(same and matters and np.isfinite(b).all(),
               f"old save {name:17}: loads bit-identical {same}; drift and ramp matter {matters}")


# ---- 3 ----------------------------------------------------------------------
BAND0 = [(14, 0), (7, 1000), (16, 1)]
SEMI0 = [(14, 0), (5, 1), (6, 81), (7, 81), (16, 1)]
TARGETS = [(0, "Input gain", BAND0, 6), (1, "Tuning reference", SEMI0, 150),
           (2, "Frequency", BAND0, 500), (3, "Fine tune", BAND0, 300),
           (4, "Width up", BAND0, 500), (5, "Width down", BAND0, 200),
           (6, "Gain", BAND0, 6), (7, "Pan", BAND0, 0.8),
           (8, "Wet/dry mix", BAND0, 0.4), (9, "Output volume", BAND0, 0.4)]


def targets(tmp):
    for t, name, band, amt in TARGETS:
        runs = [run(SRC, os.path.join(tmp, f"t{k}.csv"), 6, None,
                    [band, [(20, t)], [(24, 1), (23, 1), (21, a), (22, a)]])
                for k, a in ((0, 0), (1, amt))]
        moved = not np.array_equal(*runs)
        report(moved and all(np.isfinite(r).all() for r in runs),
               f"drift target {t} {name:17} changes the sound: {moved}")
    for t, name, amt in ((0, "Input gain", -12), (1, "Tuning reference", 300),
                         (8, "Wet/dry mix", -0.4), (9, "Output volume", -0.4)):
        band = SEMI0 if t == 1 else BAND0
        runs = [run(SRC, os.path.join(tmp, f"r{k}.csv"), 6, None,
                    [band, [(28, t)], [(30, 0), (31, 3), (29, a), (34, 1)]])
                for k, a in ((0, 0), (1, amt))]
        moved = not np.array_equal(*runs)
        report(moved, f"ramp target  {t} {name:17} changes the sound: {moved}")
    for t, name in ((0, "Input gain"), (9, "Output volume")):
        # Same number of stages both sides: each stage is a block later, and a
        # drift that starts a block later is at a different phase.
        from0 = run(SRC, os.path.join(tmp, "g0.csv"), 6, None,
                    [BAND0, [(4, 0)], [(20, t)], [(24, 1), (23, 1), (21, 0.3), (22, 0.3)]])
        from5 = run(SRC, os.path.join(tmp, "g5.csv"), 6, None,
                    [BAND0, [(4, 5)], [(20, t)], [(24, 1), (23, 1), (21, 0.3), (22, 0.3)]])
        report(np.array_equal(from0, from5),
               f"{name} is one setting for the whole plugin: set from band 5 == from band 0")


# ---- 4 ----------------------------------------------------------------------
def units(tmp):
    base = [(14, 0), (16, 2)]
    hz = run(SRC, os.path.join(tmp, "p0.csv"), 4, None, [base + [(7, 440)]])
    semi = run(SRC, os.path.join(tmp, "p1.csv"), 4, None, [base + [(5, 1), (6, 69), (7, 69)]])
    cents = run(SRC, os.path.join(tmp, "p2.csv"), 4, None, [base + [(5, 2), (7, 6900)]])
    other = run(SRC, os.path.join(tmp, "p3.csv"), 4, None, [base + [(7, 466.16)]])
    report(np.array_equal(hz, semi) and np.array_equal(hz, cents) and not np.array_equal(hz, other),
           f"A4: Semitones 69 == Hz 440 {np.array_equal(hz, semi)}, Cents 6900 == Hz 440 "
           f"{np.array_equal(hz, cents)}, and 466 Hz differs {not np.array_equal(hz, other)}")
    band = [(14, 0), (7, 1000), (16, 2)]
    w_hz = run(SRC, os.path.join(tmp, "w0.csv"), 4, None, [band + [(10, 1000), (12, 500)]])
    w_st = run(SRC, os.path.join(tmp, "w1.csv"), 4, None, [band + [(11, 1), (10, 12), (13, 1), (12, 12)]])
    w_ct = run(SRC, os.path.join(tmp, "w2.csv"), 4, None, [band + [(11, 2), (10, 1200), (13, 2), (12, 1200)]])
    w_7 = run(SRC, os.path.join(tmp, "w3.csv"), 4, None, [band + [(11, 1), (10, 7), (13, 1), (12, 7)]])
    report(np.array_equal(w_hz, w_st) and np.array_equal(w_hz, w_ct) and not np.array_equal(w_hz, w_7),
           f"widths on a 1000 Hz band: 12 semitones == 1000 up / 500 down Hz {np.array_equal(w_hz, w_st)}, "
           f"1200 cents too {np.array_equal(w_hz, w_ct)}, 7 semitones differs {not np.array_equal(w_hz, w_7)}")


def main():
    pick = sys.argv[1:] or ["projects", "saves", "targets", "units"]
    with tempfile.TemporaryDirectory() as tmp:
        old_build = os.path.join(tmp, "old_resonance_bank.jsfx")
        open(old_build, "wb").write(subprocess.run(
            ["git", "show", f"{OLD_COMMIT}:src/resonance_bank.jsfx"], cwd=ROOT,
            capture_output=True, check=True).stdout)
        if "projects" in pick: projects(old_build, tmp)
        if "saves" in pick: saves(old_build, tmp)
        if "targets" in pick: targets(tmp)
        if "units" in pick: units(tmp)
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
