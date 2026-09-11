#!/usr/bin/env python3
"""The 2026-09-11 small R24 batch, measured. docs/layouts/r24-small-batch-20260911.md.

current  every saved copy on the current layout: the pre-change build (403fe41)
         on its snapshot == the new build on the live file, bit for bit, not
         silent. Where the file holds an old-format blob, the new build on the
         UNCHANGED snapshot must match too: that is the plugin remapping it alone.
saves    synthetic old saves with drift and ramp on EVERY old target, each old
         save format, per plugin: old build == new build, and the drift and
         ramp must matter (the same save without them renders differently).
targets  every NEW target, by drift, changes the sound and stays finite.
broken   the copies that were never carried over. Tensor's Tremolos and the
         track template: the last build that still read their first-release
         layout (705ee29) on the snapshot == the new build on the migrated file,
         and every control decoded by name; Tensor's playing-around against
         Rozaya's own migrated copy. scattered's Dapples: the last 32-control
         build (272a438) on the snapshot == the new build on the migrated file.

    python tools/r24_batch_verify_20260911.py [current|saves|targets|broken] [plugin ...]
"""
import base64, os, re, struct, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import r24_batch_migrate_20260911 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
SNAP = mig.SNAP
PRE = "403fe41"
PLUGS = ["bubbler", "dapple", "Full_Feature_Tremolo", "veil"]
LIVE = {"finished": "E:/reaper/finished", "to-play-with-later": "E:/reaper/to-play-with-later"}
BRIDGE = "test-projects/claude-testing002-bridge.RPP"
CURRENT = {
    "bubbler": [("finished/birdsong-2.RPP", 3), ("finished/birdsong.RPP", 2),
                ("finished/the-sound-of-a-drain.RPP", 5), (BRIDGE, 1)],
    "dapple": [("finished/bubbles.RPP", 11), ("to-play-with-later/womb-bubbles-proto.RPP", 3), (BRIDGE, 1)],
    "Full_Feature_Tremolo": [("finished/bilateral stimulation tones.RPP", 1), ("finished/melodic.RPP", 1),
                             ("finished/returning-home.RPP", 2), ("finished/upswing.RPP", 1),
                             ("to-play-with-later/knocking.RPP", 1), ("to-play-with-later/playing-around.RPP", 1),
                             ("to-play-with-later/simple-sequence-check.RPP", 2),
                             ("to-play-with-later/simple-sequence.RPP", 2), (BRIDGE, 1)],
    "veil": [(BRIDGE, 1)],
}
fails = 0
tmp = tempfile.mkdtemp()


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def build(plugin, commit):
    path = os.path.join(tmp, f"{plugin}-{commit}.jsfx")
    if not os.path.exists(path):
        src = subprocess.run(["git", "show", f"{commit}:src/{plugin}.jsfx"], cwd=ROOT,
                             capture_output=True, check=True).stdout
        open(path, "wb").write(src)
    return path


def new(plugin):
    return os.path.join(ROOT, "src", plugin + ".jsfx")


def run(plugin_file, seconds=10, rpp=None, fx=None, inst=1, stages=()):
    out = os.path.join(tmp, "out.csv")
    cmd = [EXE, plugin_file, "--input", "noise", "--seconds", str(seconds), "--csv", out, "--quiet"]
    if rpp:
        cmd += ["--rpp", rpp, "--fx", fx, "--instance", str(inst)]
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))


def listing(plugin_file, rpp, fx, inst=1):
    r = subprocess.run([EXE, plugin_file, "--rpp", rpp, "--fx", fx, "--instance", str(inst), "--list"],
                       capture_output=True, text=True, check=True)
    return {m.group(2): float(m.group(3)) for m in
            (re.match(r"\s*slider(\d+)\s+(.*?)\s+\[.*\] = (\S+)", l) for l in r.stdout.splitlines()) if m}


def live_path(rel):
    top, name = rel.split("/", 1)
    return f"{SNAP}/{rel}" if rel == BRIDGE else f"{LIVE[top]}/{name}"


# ---- current ------------------------------------------------------------------
def current(plugs):
    for p in plugs:
        a = run(build(p, PRE), 6)
        b = run(new(p), 6)
        report(np.array_equal(a, b), f"{p}: a fresh instance renders identically")
        for rel, n in CURRENT[p]:
            for k in range(1, n + 1):
                a = run(build(p, PRE), 20, f"{SNAP}/{rel}", p, k)
                b = run(new(p), 20, live_path(rel), p, k)
                c = run(new(p), 20, f"{SNAP}/{rel}", p, k)
                ok = np.array_equal(a, b) and np.array_equal(a, c) and np.abs(a).max() > 0
                report(ok, f"{p} {rel} #{k}: old on snapshot == new on live {np.array_equal(a, b)}, "
                           f"== new on the unchanged snapshot {np.array_equal(a, c)}, peak {np.abs(a).max():.3f}")
    if "Full_Feature_Tremolo" in plugs:
        lk = listing(new("Full_Feature_Tremolo"), f"{SNAP}/to-play-with-later/knocking.RPP", "Full_Feature_Tremolo")
        ll = listing(new("Full_Feature_Tremolo"), live_path("to-play-with-later/knocking.RPP"), "Full_Feature_Tremolo")
        report(lk.get("Drift target") == 2 and ll.get("Drift target") == 2,
               f"knocking's Drift target reads Tremolo amount (2) from the old save {lk.get('Drift target')} "
               f"and from the migrated file {ll.get('Drift target')}")


# ---- saves --------------------------------------------------------------------
def b64(vals):
    return base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode()


def project(path, fx, line, blob):
    vals = " ".join(str(line.get(i, "-")) for i in range(1, 65))
    body = "\n".join("        " + blob[i:i + 128] for i in range(0, len(blob), 128))
    open(path, "w", newline="").write(
        f"<REAPER_PROJECT 0.1 \"7.0\" 0\n  <TRACK\n    <FXCHAIN\n      <JS glasswings/{fx}.jsfx \"\"\n"
        f"        {vals}\n      >\n      <JS_SER\n{body}\n      >\n    >\n  >\n>\n")


def banks(n, table, width, dflt=0.0):
    return [[(table.get(t, [dflt] * width)[k]) for t in range(n)] for k in range(width)]


SAVES = {
    "veil": dict(n=4, magics=[3200004],
                 line={1: 480, 2: 700, 3: 0.3, 4: 0.45, 5: 1, 6: -3, 7: 1, 11: 0, 15: 3, 17: 0, 21: 1},
                 # up, down, period, shape, play, rest
                 drift={0: [150, 100, 1.3, 0, 0, 0], 1: [200, 200, 0.7, 2, 0, 0],
                        2: [0.3, 0.2, 2, 1, 1.25, 0.5], 3: [0.2, 0.3, 0.9, 2, 0, 0]},
                 # by, dur, delay, play, rest
                 ramp={0: [-200, 3, 0.5, 0, 0], 3: [0.4, 2, 0, 0.5, 0.25]}, last_d=1, last_r=3, per_dflt=20),
    "bubbler": dict(n=9, magics=[3500009, 3400009],
                    line={1: 8, 2: 2, 3: 50, 4: 0, 6: 5, 7: 1, 8: 0, 9: 2, 10: 440, 11: 7, 12: 12, 13: 150,
                          14: 80, 15: 60, 16: 0, 21: 5, 25: 1, 30: 2, 32: 1, 36: 1},
                    drift={0: [60, 60, 1.1, 0, 0, 0], 1: [30, 30, 0.8, 2, 0, 0], 2: [3, 3, 1.7, 1, 0, 0],
                           3: [5, 5, 1.3, 2, 0, 0], 4: [6, 6, 0.9, 0, 0, 0], 5: [80, 80, 1.2, 1, 0, 0],
                           6: [20, 20, 0.6, 2, 0, 0], 7: [30, 30, 1.4, 0, 1.25, 0.5], 8: [4, 4, 1.0, 1, 0, 0]},
                    moves=[1, 0, 1, 0, 1, 0, 1, 0, 1],
                    ramp={0: [120, 4, 0, 0, 0], 2: [-5, 3, 0.5, 0, 0], 8: [-6, 5, 0, 1, 0.5]},
                    last_d=5, last_r=2, per_dflt=20),
    "dapple": dict(n=11, magics=[3600011, 3500011],
                   line={1: 10, 2: 2, 3: 50, 4: 0, 5: 62, 6: 300, 7: 0, 8: 2, 9: 440, 10: 50, 11: 0.85,
                         12: 120, 13: 40, 14: 50, 15: 0, 16: 80, 17: 0, 22: 7, 26: 1, 31: 6, 33: 1, 37: 1},
                   drift={0: [120, 120, 1.1, 0, 0, 0], 1: [30, 30, 0.8, 2, 0, 0], 2: [100, 80, 1.3, 1, 0, 0],
                          3: [30, 30, 1.7, 2, 0, 0], 4: [0.1, 0.3, 0.9, 0, 0, 0], 5: [60, 60, 1.2, 1, 0, 0],
                          6: [30, 30, 0.7, 2, 0, 0], 7: [40, 40, 1.5, 0, 1.25, 0.5], 8: [30, 30, 1.0, 1, 0, 0],
                          9: [40, 40, 0.6, 2, 0, 0], 10: [5, 5, 1.3, 0, 0, 0]},
                   moves=[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                   ramp={2: [200, 4, 0, 0, 0], 6: [30, 3, 0, 0, 0], 10: [-8, 5, 0, 1, 0.5]},
                   last_d=7, last_r=6, per_dflt=20),
    "Full_Feature_Tremolo": dict(n=6, magics=[2200006, 2100006],
                   line={1: 4, 2: 2, 3: 50, 4: -12, 5: 10, 6: 1, 7: 10, 8: 1, 9: 0, 10: 0, 11: 1, 12: 9, 13: 1,
                         14: 5, 15: 8, 16: 0.5, 17: 2, 18: 1, 24: 4, 28: 1, 32: 1, 34: 1, 38: 1},
                   drift={0: [1, 1, 1.3, 0, 0, 0], 1: [6, 6, 0.9, 2, 0, 0], 2: [0.3, 0.3, 1.1, 1, 0, 0],
                          3: [20, 20, 0.7, 0, 1.25, 0.5], 4: [8, 8, 1.5, 2, 0, 0], 5: [8, 8, 1.2, 1, 0, 0]},
                   ramp={0: [2, 4, 0, 0, 0], 1: [-20, 3, 0.5, 0, 0], 2: [0.5, 5, 0, 1, 0.5]},
                   last_d=4, last_r=1, per_dflt=8),
}


def old_blob(p, magic, with_mod):
    s = SAVES[p]
    n = s["n"]
    dr = banks(n, s["drift"] if with_mod else {}, 6)
    if not with_mod:
        dr[2] = [s["per_dflt"]] * n
    else:
        dr[2] = [s["drift"].get(t, [0, 0, s["per_dflt"]])[2] for t in range(n)]
    rp = banks(n, s["ramp"] if with_mod else {}, 5)
    if p == "Full_Feature_Tremolo":
        v = [magic] + dr[0] + dr[1] + dr[2] + dr[3] + [s["last_d"]] + rp[0] + rp[1] + rp[2] + [s["last_r"]]
        if magic == 2200006:
            v += dr[4] + dr[5] + rp[3] + rp[4]
        return v
    v = [magic] + rp[0] + rp[1] + rp[2] + rp[3] + rp[4] + [s["last_r"]]
    v += dr[0] + dr[1] + dr[2] + dr[3] + dr[4] + dr[5] + [s["last_d"]]
    if magic in (3500009, 3600011):
        v += [float(m) for m in s["moves"]]
    return v


def saves(plugs):
    for p in plugs:
        for magic in SAVES[p]["magics"]:
            a_p, c_p = os.path.join(tmp, "a.RPP"), os.path.join(tmp, "c.RPP")
            project(a_p, p, SAVES[p]["line"], b64(old_blob(p, magic, True)))
            project(c_p, p, SAVES[p]["line"], b64(old_blob(p, magic, False)))
            a = run(build(p, PRE), 10, a_p, p)
            b = run(new(p), 10, a_p, p)
            c = run(build(p, PRE), 10, c_p, p)
            same, matters = np.array_equal(a, b), not np.array_equal(a, c)
            report(same and matters and np.isfinite(b).all(),
                   f"{p} old save {magic}: loads bit-identical {same}; its drift and ramp matter {matters}")


# ---- targets ------------------------------------------------------------------
# (plugin, target, name, base settings, drift slider ids (selector, up, down, period, unit, moves), amount)
TARGETS = [
    ("veil", 4, "Output", [(6, -6)], (7, 8, 9, 10, 11, None), 6),
    ("bubbler", 3, "Fine tune", [(15, 100)], (21, 22, 23, 24, 25, 26), 300),
    ("bubbler", 4, "Tuning reference", [(15, 100), (7, 0), (6, 200)], (21, 22, 23, 24, 25, 26), 150),
    ("bubbler", 11, "Play for", [(15, 100), (18, 2), (19, 2)], (21, 22, 23, 24, 25, 26), 1.5),
    ("bubbler", 12, "Rest for", [(15, 100), (18, 2), (19, 2)], (21, 22, 23, 24, 25, 26), 1.5),
    ("dapple", 3, "Fine tune", [], (22, 23, 24, 25, 26, 27), 300),
    ("dapple", 4, "Tuning reference", [(4, 1), (5, 57), (6, 57)], (22, 23, 24, 25, 26, 27), 150),
    ("dapple", 13, "Play for", [(19, 2), (20, 2)], (22, 23, 24, 25, 26, 27), 1.5),
    ("dapple", 14, "Rest for", [(19, 2), (20, 2)], (22, 23, 24, 25, 26, 27), 1.5),
    ("Full_Feature_Tremolo", 5, "Stereo phase offset", [(1, 4), (2, 2), (10, 1)], (24, 25, 26, 27, 28, None), 90),
    ("Full_Feature_Tremolo", 6, "Pan spread", [(1, 4), (2, 2), (11, 1), (12, 9), (13, 0.5)], (24, 25, 26, 27, 28, None), 0.4),
    ("Full_Feature_Tremolo", 7, "Pan glide", [(1, 4), (2, 2), (11, 1), (12, 1), (14, 5)], (24, 25, 26, 27, 28, None), 150),
    ("Full_Feature_Tremolo", 9, "Pan sweep every", [(1, 4), (2, 2), (11, 1), (12, 11)], (24, 25, 26, 27, 28, None), 0.8),
    ("Full_Feature_Tremolo", 10, "Play for", [(1, 4), (2, 2), (20, 2), (21, 2)], (24, 25, 26, 27, 28, None), 1.5),
    ("Full_Feature_Tremolo", 11, "Rest for", [(1, 4), (2, 2), (20, 2), (21, 2)], (24, 25, 26, 27, 28, None), 1.5),
]


def targets(plugs):
    for p, t, name, base, (sel, up, dn, per, unit, moves), amt in TARGETS:
        if p not in plugs:
            continue
        runs = []
        for a in (0, amt):
            last = [(unit, 1), (per, 1), (up, a), (dn, a)] + ([(moves, 1)] if moves else [])
            runs.append(run(new(p), 8, stages=[base, [(sel, t)], last]))
        moved = not np.array_equal(*runs)
        report(moved and all(np.isfinite(r).all() for r in runs), f"{p} new target {t} {name}: changes the sound {moved}")


# ---- broken -------------------------------------------------------------------
APRIL_NAMES = {"Rate Value": "Rate Value (BPM / sec / Hz / beats per cycle / per beat)",
               "Depth dB": "Tremolo amount (dB, 0 = strongest)",
               "Pan Sweep Rate Unit": "Pan sweep rate mode",
               "Filter Speed Multiplier (Linked Sweep)": "Pan sweep every (cycles)"}


def broken(plugs):
    if "Full_Feature_Tremolo" in plugs:
        fx = "Full_Feature_Tremolo"
        for rel, live, kind in mig.FILES:
            if kind != "tremolo_april":
                continue
            snap = f"{SNAP}/{rel}"
            n = open(snap, encoding="utf-8", errors="replace").read().count(f"/{fx}.jsfx")
            for k in range(1, n + 1):
                a = run(build(fx, "705ee29"), 20, snap, fx, k)
                b = run(new(fx), 20, live, fx, k)
                old_l, new_l = listing(build(fx, "d19873f"), snap, fx, k), listing(new(fx), live, fx, k)
                bad = []
                for name, v in old_l.items():
                    nn = APRIL_NAMES.get(name, name)
                    want = (mig.HZ_SEC_BPM[int(v)] if name in ("Rate Mode", "Pan Sweep Rate Unit")
                            else 1 / v if name.startswith("Filter Speed") else v)
                    if nn not in new_l or abs(new_l[nn] - want) > 1e-6:
                        bad.append(f"{name} {v} -> {new_l.get(nn)}")
                same = np.array_equal(a, b)
                report(same and not bad and np.abs(a).max() > 0,
                       f"{fx} {rel} #{k}: 705ee29 on snapshot == new on migrated {same}; "
                       f"{len(old_l)} controls by name" + ("" if not bad else " -- " + "; ".join(bad)))
        tensor = run(new(fx), 20, "E:/tensor's-rpp-projects/playing-around.RPP", fx)
        mine = run(new(fx), 20, "E:/reaper/to-play-with-later/playing-around.RPP", fx)
        report(np.array_equal(tensor, mine),
               "Tensor's playing-around, migrated, renders identically to Rozaya's own copy")
    if "dapple" in plugs:
        fx = "dapple"
        rel, live = "to-play-with-later/scattered.rpp", "E:/reaper/to-play-with-later/scattered.rpp"
        for k in (1, 2):
            a = run(build(fx, "272a438"), 20, f"{SNAP}/{rel}", fx, k)
            b = run(new(fx), 20, live, fx, k)
            old_l, new_l = listing(build(fx, "272a438"), f"{SNAP}/{rel}", fx, k), listing(new(fx), live, fx, k)
            bad = []
            for name, v in old_l.items():
                # Renamed since 2026-09-06; names are not stored in projects.
                nn = {"Pitch (Hz)": "Pitch value (Hz / semitones / cents)",
                      "Ramp duration": "Ramp duration (in ramp time units)",
                      "Ramp start delay": "Ramp start delay (in ramp time units)"}.get(name, name)
                want = mig.DP_O2N[int(v)] if name in ("Drift target", "Ramp target") else v
                if nn not in new_l or abs(new_l[nn] - want) > 1e-6:
                    bad.append(f"{name} {v} -> {new_l.get(nn)}")
            for name, want in (("Pitch mode", 0), ("Fine tune", 0), ("Fine tune unit", 2),
                               ("Tuning reference (Hz)", 440)):
                if new_l.get(name) != want:
                    bad.append(f"new {name} {new_l.get(name)}")
            same = np.array_equal(a, b)
            report(same and not bad and np.abs(a).max() > 0,
                   f"dapple scattered #{k}: 272a438 on snapshot == new on migrated {same}; "
                   f"{len(old_l)} controls by name" + ("" if not bad else " -- " + "; ".join(bad)))


def main():
    args = sys.argv[1:]
    parts = [a for a in args if a in ("current", "saves", "targets", "broken")] or \
            ["current", "saves", "targets", "broken"]
    plugs = [p for p in PLUGS if any(a.lower() in p.lower() for a in args if a not in parts)] or PLUGS
    for part in parts:
        globals()[part](plugs)
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
