#!/usr/bin/env python3
"""Womb's forty-nine targets, measured. docs/layouts/womb-r24-20260911.md.

Works on TEMP copies made by the migration's own convert(), so it can run before
anything live is written; `applied` then checks the live files equal those copies.

current    nine copies: the pre-change build (0503e72) on the snapshot == the new
           build on the migrated copy, not silent. to-sleep-within's selectors read
           Inhale (15) on the new build. womb-and-baby, converted: identical with its
           Breath rate drift zeroed on both sides (all that conversion may change).
saves      synthetic 2500011 / 2400011 / 2300010 / 2100010 saves with drift and ramp
           on all eleven old targets, Random on several, breath in Seconds: old ==
           new on the migrated line with the same blob, and they must matter.
names      the declared target list is the authored one, both selectors.
targets    each of the thirty-eight new targets, by drift, changes the sound, finite.
breathrate Breath rate counts like Set breath rate: +4 in Beats makes breaths LONGER,
           +30 in Seconds makes them shorter.
movement   With the target differs from On a clock on a heart and a breath target.
fresh      a fresh instance renders identically.
applied    the live files equal the verified copies.

    python tools/womb_r24_verify_20260911.py [current|saves|names|targets|breathrate|movement|fresh|applied]
"""
import base64, os, re, struct, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import womb_r24_migrate_20260911 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
NEW = os.path.join(ROOT, "src", "womb_sound_generator_v3.jsfx")
FX = "womb_sound_generator_v3"
PRE = "0503e72"
fails = 0
tmp = tempfile.mkdtemp()


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def build(commit):
    p = os.path.join(tmp, f"womb-{commit}.jsfx")
    if not os.path.exists(p):
        open(p, "wb").write(subprocess.run(["git", "show", f"{commit}:src/womb_sound_generator_v3.jsfx"], cwd=ROOT,
                                           capture_output=True, check=True).stdout)
    return p


def run(plugin, seconds, rpp=None, stages=(), extra=()):
    out = os.path.join(tmp, "o.csv")
    cmd = [EXE, plugin, "--seconds", str(seconds), "--csv", out, "--quiet", *extra]
    if rpp:
        cmd += ["--rpp", rpp, "--fx", FX, "--instance", "1"]
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))


def listing(plugin, rpp):
    from r25_names import base   # names match before and after the R25 rename (2026-09-12)
    r = subprocess.run([EXE, plugin, "--rpp", rpp, "--fx", FX, "--list"], capture_output=True, text=True, check=True)
    return {base(m.group(2)): float(m.group(3)) for m in
            (re.match(r"\s*slider(\d+)\s+(.*?)\s+\[.*\] = (\S+)", l) for l in r.stdout.splitlines()) if m}


def migrated(rel, convert_baby=False):
    want = mig.convert(f"{mig.SNAP}/{rel}", rel, convert_baby)
    p = os.path.join(tmp, "m-" + rel.replace("/", "_"))
    open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(want)
    return p


def zero_baby_drift(path):
    """A copy of path with Breath rate's drift up/down (old index 7, blob 2100010) at 0."""
    L = open(path, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    (hi,) = mig.heads(L)
    j, k = hi + 3, hi + 4
    while L[k].strip() != ">":
        k += 1
    raw = base64.b64decode("".join(x.strip() for x in L[j + 1:k]))
    v = list(struct.unpack("<%df" % (len(raw) // 4), raw))
    v[8] = v[18] = 0.0
    b = base64.b64encode(struct.pack("<%df" % len(v), *v)).decode()
    ind = L[j + 1][: len(L[j + 1]) - len(L[j + 1].lstrip())]
    eol = "\r\n" if L[j + 1].endswith("\r\n") else "\n"
    L[j + 1:k] = [ind + b[x:x + 128] + eol for x in range(0, len(b), 128)]
    out = path + ".nodrift.RPP"
    open(out, "w", encoding="utf-8", errors="surrogateescape", newline="").write("".join(L))
    return out


def current():
    for rel, live in mig.FILES:
        snap = f"{mig.SNAP}/{rel}"
        name = rel.split("/")[-1][:34]
        if rel.endswith(mig.BABY):
            m = migrated(rel, True)
            a, b = run(build(PRE), 40, zero_baby_drift(snap)), run(NEW, 40, zero_baby_drift(m))
            report(np.array_equal(a, b) and np.abs(a).max() > 0,
                   f"{name}: with its Breath rate drift zeroed, old == new {np.array_equal(a, b)}, peak {np.abs(a).max():.3f}")
            nl = listing(NEW, m)
            report(abs(nl.get("Drift up amount (units match target)", 0) - mig.BABY_UP) < 1e-5 and nl.get("Drift target") == 14,
                   f"{name}: converted drift reads target {nl.get('Drift target')}, up "
                   f"{nl.get('Drift up amount (units match target)')}, down {nl.get('Drift down amount (units match target)')}")
            continue
        m = migrated(rel)
        # scattered was never carried over: its oracle is 92effbe, the last build
        # with the 70-control layout its line is on.
        oracle = "92effbe" if rel.endswith(mig.SCATTERED) else PRE
        a, b = run(build(oracle), 40, snap), run(NEW, 40, m)
        same = np.array_equal(a, b)
        report(same and np.abs(a).max() > 0,
               f"{name}: {oracle} on snapshot == new on migrated {same}, peak {np.abs(a).max():.3f}")
        if rel.endswith(mig.SCATTERED):
            broken = np.abs(run(build(PRE), 40, snap)).max()
            report(broken > 5 * np.abs(a).max(),
                   f"scattered: and the pre-change build on its unmigrated line peaks {broken:.1f} -- the fault this repairs")
        if "to-sleep-within" in rel:
            ol, nl = listing(build(PRE), snap), listing(NEW, m)
            got = (ol.get("Drift target"), ol.get("Ramp target"), nl.get("Drift target"), nl.get("Ramp target"))
            report(got == (2, 2, 15, 15), f"to-sleep-within selectors old (Drift, Ramp) -> new: {got}")


OLD_NAMES = "Heart rate,S1-S2 gap,Inhale,Top pause,Exhale,Bottom pause,RSA depth,Breaths/min,Inhale Freq,Exhale Freq,Bloodflow offset"
#        up     down   period shape
DRIFT = {0: (6, 6, 3, 0), 1: (30, 30, 2, 2), 2: (1, 0.5, 2, 1), 3: (0.2, 0.1, 2, 0), 4: (1, 1, 3, 2),
         5: (0.2, 0.2, 2, 1), 6: (3, 3, 2, 0), 7: (2, 2, 3, 2), 8: (80, 60, 2, 0), 9: (60, 40, 3, 1),
         10: (20, 20, 2, 2)}
#        by    duration (s) delay
RAMP = {0: (-10, 20, 0), 1: (40, 15, 2), 7: (3, 10, 0), 8: (100, 12, 0), 10: (30, 10, 1)}


def old_blob(magic, mod):
    n = 11 if magic >= 2400000 else 10
    d = lambda k, dflt: [(DRIFT[t][k] if mod else dflt) for t in range(n)]
    r = lambda k: [(RAMP[t][k] if mod and t in RAMP else 0) for t in range(n)]
    v = [magic] + d(0, 0) + d(1, 0) + d(2, 8) + d(3, 0) + [4] + r(0) + r(1) + r(2) + [1]
    if magic == 2300010:
        v += [0, 0, 0]
    if magic >= 2400000:
        v += [(1.25 if mod and t == 4 else 0) for t in range(n)] + [(0.5 if mod and t == 4 else 0) for t in range(n)]
        v += [0] * n + [0] * n
    if magic >= 2500000:
        v += [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1]
    return base64.b64encode(struct.pack("<%df" % len(v), *v)).decode()


def project(path, line, b64):
    body = "\n".join("        " + b64[i:i + 128] for i in range(0, len(b64), 128))
    open(path, "w", newline="").write(
        "<REAPER_PROJECT 0.1 \"7.0\" 0\n  <TRACK\n    <FXCHAIN\n      <JS glasswings/womb_sound_generator_v3.jsfx \"\"\n"
        f"{line}      >\n      <JS_SER\n{body}\n      >\n    >\n  >\n>\n")


def saves():
    base = subprocess.run([EXE, build(PRE), "--list"], capture_output=True, text=True, check=True).stdout
    vals = {int(m.group(1)): m.group(2) for m in (re.match(r"\s*slider(\d+)\s.*\] = (\S+)", l) for l in base.splitlines()) if m}
    # visible drift = target 4's config, visible ramp = target 1's; Seconds ramp unit, engaged
    vals.update({72: 4, 73: 1, 74: 1, 75: 3, 78: 2, 77: 0, 79: 1.25, 80: 0.5,
                 81: 1, 82: 40, 83: 1, 84: 15, 88: 2, 87: 1, 25: 0, 3: 4})
    for magic in (2500011, 2400011, 2300010, 2100010):
        v = dict(vals)
        if magic < 2400000:
            v[79] = v[80] = 0
        toks = [str(v.get(i, "-")) for i in range(1, 89)]
        old_line = "        " + " ".join(toks[:64] + ['""'] + toks[64:]) + "\n"
        new_line = mig.remap_line(old_line, "synthetic")
        po, pn, pc = (os.path.join(tmp, f"{x}.RPP") for x in "onc")
        project(po, old_line, old_blob(magic, True))
        project(pn, new_line, old_blob(magic, True))
        project(pc, old_line, old_blob(magic, False))
        a, b, c = run(build(PRE), 60, po), run(NEW, 60, pn), run(build(PRE), 60, pc)
        same, matters = np.array_equal(a, b), not np.array_equal(a, c)
        report(same and matters and np.abs(a).max() > 0,
               f"old save {magic}: loads bit-identical {same}; its drift and ramp matter {matters}")


AUTHORED = ("Heart rate,Heart with breath,Systole,S1 pitch,S1 fine tune,S1 decay,S1 volume,S2 pitch,S2 fine tune,"
            "S2 decay,S2 volume,Brightness,HB stereo width,HB master volume,Breath rate,Inhale,Top pause,Exhale,"
            "Bottom pause,Inhale pitch,Inhale fine tune,Exhale pitch,Exhale fine tune,Inhale fade in,Inhale fade out,"
            "Exhale fade in,Exhale fade out,Breath high-pass,Breath post-filter Hz,Breath post-filter Q,Sigh interval,"
            "Sigh extra length,Breath stereo width,Breath volume,Bloodflow offset,Bloodflow attack,Bloodflow decay,"
            "Bloodflow dicrotic level,Bloodflow filter Hz,Bloodflow resonance,Bloodflow stereo width,Bloodflow volume,"
            "Tuning reference,HB play for,HB rest for,Breath play for,Breath rest for,Bloodflow play for,"
            "Bloodflow rest for")


def names():
    src = open(NEW, encoding="utf-8").read()
    for sid in (72, 81):
        m = re.search(rf"^slider{sid}:0<0,48,1{{(.*?)}}>", src, re.M)
        report(bool(m) and m.group(1) == AUTHORED, f"slider {sid}'s 49 names are the authored list")
    old = AUTHORED.split(",")
    for o, n in mig.O2N.items():
        pass
    renamed = {"S1-S2 gap": "Systole", "RSA depth": "Heart with breath", "Breaths/min": "Breath rate",
               "Inhale Freq": "Inhale pitch", "Exhale Freq": "Exhale pitch"}
    bad = [f"{o}->{old[mig.O2N[i]]}" for i, o in enumerate(OLD_NAMES.split(",")) if renamed.get(o, o) != old[mig.O2N[i]]]
    report(not bad, "every old target lands on its control's name" + (" -- " + "; ".join(bad) if bad else ""))


SHORT = [(26, 1), (27, 0), (28, 1), (29, 0)]
TARGETS = [(3, "S1 pitch", [], 20), (4, "S1 fine tune", [], 300), (5, "S1 decay", [], 40), (6, "S1 volume", [], 0.5),
           (7, "S2 pitch", [], 40), (8, "S2 fine tune", [], 300), (9, "S2 decay", [], 20), (10, "S2 volume", [], 0.3),
           (11, "Brightness", [], 0.3), (12, "HB stereo width", [], 2), (13, "HB master volume", [], 0.5),
           (20, "Inhale fine tune", [], 300), (22, "Exhale fine tune", [], 300), (23, "Inhale fade in", [], 0.2),
           (24, "Inhale fade out", [], 0.2), (25, "Exhale fade in", [], 0.2), (26, "Exhale fade out", [], 0.2),
           (27, "Breath high-pass", [], 200), (28, "Breath post-filter Hz", [], 200), (29, "Breath post-filter Q", [], 2),
           (30, "Sigh interval", SHORT + [(48, 0.2)], 0.15), (31, "Sigh extra length", SHORT + [(48, 0.05)], 3),
           (32, "Breath stereo width", [], 0.4), (33, "Breath volume", [], 0.4), (35, "Bloodflow attack", [], 0.1),
           (36, "Bloodflow decay", [], 0.3), (37, "Bloodflow dicrotic level", [], 0.5), (38, "Bloodflow filter Hz", [], 150),
           (39, "Bloodflow resonance", [], 0.4), (40, "Bloodflow stereo width", [], 0.4), (41, "Bloodflow volume", [], 0.5),
           (42, "Tuning reference", [(6, 1), (7, 33), (8, 33)], 150), (43, "HB play for", [(66, 2), (67, 1)], 2.5),
           (44, "HB rest for", [(66, 2), (67, 1)], 2.5), (45, "Breath play for", SHORT + [(68, 1), (69, 1)], 2.5),
           (46, "Breath rest for", SHORT + [(68, 1), (69, 1)], 2.5), (47, "Bloodflow play for", [(70, 2), (71, 1)], 2.5),
           (48, "Bloodflow rest for", [(70, 2), (71, 1)], 2.5)]


# A period of 1.3 s, never whole: see tools/rhythm_r24_verify_20260911.py, where a
# 1 s wave read on 0.5 s events sat on its zero crossings and "changed nothing".
def drifted(t, amt, extra=(), moves=1, unit=1, per=1.3, seconds=20):
    return run(NEW, seconds, stages=[list(extra), [(72, t)], [(76, unit), (75, per), (77, moves), (73, amt), (74, amt)]])


def targets():
    for t, name, extra, amt in TARGETS:
        secs = 30 if t in (30, 31, 45, 46) else 20
        # The gates (43-48) at 1.7 s. At 1.3 s a heartbeat gate cycle of three beats
        # (2.57 s) is almost exactly two waves, so every check read nearly the same
        # point and three gates "changed nothing" over 30 s -- measured 2026-09-11;
        # at 0.9, 1.7 and 2.3 s all three change at their first checks.
        per = 1.7 if t >= 43 else 1.3
        r = [drifted(t, a, extra, per=per, seconds=secs) for a in (0, amt)]
        moved = not np.array_equal(*r)
        report(moved and all(np.isfinite(x).all() for x in r), f"new target {t} {name}: changes the sound {moved}")


def period(x):
    """The breath's length: the strongest repeat of the 10 ms loudness, 0.4-6 s,
    after the first 3 s. (A hump counter was tried first and could not count a
    one-second breath -- 39 humps where 60 were due -- so it failed a correct plugin.)"""
    m = np.abs(x).sum(axis=1)
    e = np.array([m[i:i + 441].mean() for i in range(0, len(m) - 441, 441)])[300:]
    e = e - e.mean()
    ac = np.correlate(e, e, "full")[len(e) - 1:]
    return (np.argmax(ac[40:600]) + 40) * 0.01


def breathrate():
    solo = [(52, 1)]
    seg = lambda s: [(26, s[0]), (27, s[1]), (28, s[2]), (29, s[3])]
    for unit, name, base_seg, same_as, by in ((0, "Seconds", (1, 0, 1, 0), (0.5, 0, 0.5, 0), 30),
                                              (1, "Beats", (2, 0, 2, 0), (4, 0, 4, 0), 4)):
        st = solo + [(25, unit)]
        base = period(run(NEW, 40, stages=[st + seg(base_seg)]))
        static = period(run(NEW, 40, stages=[st + seg(same_as)]))
        ramped = period(run(NEW, 40, stages=[st + seg(base_seg), [(81, 14)],
                                             [(83, 1), (84, 0.1), (82, by), (87, 1)]]))
        report(abs(ramped - static) <= 0.03 and abs(ramped - base) > 0.3,
               f"Breath rate +{by} in {name}: breath {base:.2f} s -> {ramped:.2f} s, "
               f"and segments {same_as} typed by hand give {static:.2f} s")


def movement():
    for t, name, extra, amt in ((6, "S1 volume", [], 0.5), (33, "Breath volume", SHORT, 0.4)):
        a = drifted(t, amt, extra, moves=0, unit=0, per=3, seconds=20)
        b = drifted(t, amt, extra, moves=1, unit=0, per=3, seconds=20)
        report(not np.array_equal(a, b), f"Drift movement on {name}: With the target differs from On a clock")


def fresh():
    a, b = run(build(PRE), 20), run(NEW, 20)
    report(np.array_equal(a, b) and np.abs(a).max() > 0, "a fresh instance renders identically")


def applied():
    for rel, live in mig.FILES:
        want = mig.convert(f"{mig.SNAP}/{rel}", rel, True)
        have = open(live, encoding="utf-8", errors="surrogateescape", newline="").read()
        report(have == want, f"live {rel.split('/')[-1]} equals the verified copy")


def main():
    for p in (sys.argv[1:] or ["names", "fresh", "current", "saves", "targets", "breathrate", "movement"]):
        globals()[p]()
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
