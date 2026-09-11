#!/usr/bin/env python3
"""The Morpher's fifty-five targets, measured. docs/layouts/spectral-vowel-morpher-r24-20260911.md.

THE PLUGIN SCRAMBLES rand() ON EVERY LOAD from time_precise(), so two renders of
the same build on the same project never match (measured 2026-09-11). Every render
here runs a TEST COPY of each build with that one line pinged to a constant --
`_tp = time_precise();` -> `_tp = 0.25;`, applied identically to old and new -- and
two runs of a pinned copy are byte-identical. The shipped plugin keeps its scramble.

Works on temp copies made by the migration's own convert(); `applied` then checks
the live files equal them.

current   all 123 instances: the pre-change build (81b00ff) on the snapshot == the
          new build on the migrated copy, 8 s of noise in, not silent.
blobs     a real 24-target blob and a real 7-target blob with drift and ramp written
          into every old target: old == new on the migrated line, and they matter.
names     the declared list is the authored one; every old target keeps its name.
targets   each of the 31 new targets, by drift, changes the sound, finite.
all       an "all layers" drift reaches more than its first member.
fresh     a fresh instance renders identically.
applied   the live files equal the verified copies.

    python tools/morpher_r24_verify_20260911.py [section ...] [--jobs N]
"""
import base64, concurrent.futures as cf, os, re, struct, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_r24_migrate_20260911 as mig
from rpp_sliders import parse_line, render_line

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "spectral_vowel_morpher"
PRE = "81b00ff"
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 6
fails = 0
tmp = tempfile.mkdtemp()


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def pinned(text, name):
    if text.count("_tp = time_precise();") != 1:
        raise SystemExit("the load-time scramble line is not there exactly once")
    p = os.path.join(tmp, name)
    open(p, "w", encoding="utf-8", newline="").write(text.replace("_tp = time_precise();", "_tp = 0.25;"))
    return p


OLD = pinned(subprocess.run(["git", "show", f"{PRE}:src/{FX}.jsfx"], cwd=ROOT, capture_output=True,
                            check=True).stdout.decode("utf-8"), "old.jsfx")
NEW = pinned(open(os.path.join(ROOT, "src", f"{FX}.jsfx"), encoding="utf-8").read(), "new.jsfx")
_n = 0


def run(plugin, seconds, rpp=None, inst=1, stages=()):
    global _n
    _n += 1
    out = os.path.join(tmp, f"o{_n}_{os.getpid()}_{id(stages)}.csv")
    cmd = [EXE, plugin, "--input", "noise", "--seconds", str(seconds), "--csv", out, "--quiet"]
    if rpp:
        cmd += ["--rpp", rpp, "--fx", FX, "--instance", str(inst)]
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    a = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))
    os.remove(out)
    return a


def migrated(rel):
    want, n = mig.convert(f"{mig.SNAP}/{rel}")
    p = os.path.join(tmp, "m-" + re.sub(r"[/\\ ']", "_", rel))
    open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(want)
    return p, n


def current():
    jobs = []
    for rel, live in mig.files():
        m, n = migrated(rel)
        jobs += [(rel, f"{mig.SNAP}/{rel}", m, k) for k in range(1, n + 1)]

    def one(j):
        rel, snap, m, k = j
        a, b = run(OLD, 8, snap, k), run(NEW, 8, m, k)
        return rel, k, np.array_equal(a, b), float(np.abs(a).max())
    bad = 0
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for rel, k, same, pk in ex.map(one, jobs):
            ok = same and pk > 0
            bad += not ok
            if not ok:
                report(False, f"{rel} #{k}: old == new {same}, peak {pk:.3f}")
    report(bad == 0, f"{len(jobs) - bad} of {len(jobs)} instances: old on snapshot == new on migrated, not silent")


def blob_of(path, inst=1):
    L = open(path, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    hs = mig.heads(L)
    hi = hs[inst - 1]
    j = hi + 3
    k = j + 1
    while L[k].strip() != ">":
        k += 1
    raw = base64.b64decode("".join(x.strip() for x in L[j + 1:k]))
    return L, hi, j, k, list(struct.unpack("<%df" % (len(raw) // 4), raw))


def write_project(path, L, hi, j, k, vals, line_fn):
    b = base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode()
    ind = L[j + 1][: len(L[j + 1]) - len(L[j + 1].lstrip())]
    eol = "\r\n" if L[j + 1].endswith("\r\n") else "\n"
    L2 = list(L)
    L2[hi + 1] = line_fn(L[hi + 1])
    L2[j + 1:k] = [ind + b[x:x + 128] + eol for x in range(0, len(b), 128)]
    open(path, "w", encoding="utf-8", errors="surrogateescape", newline="").write("".join(L2))


def find_instance(magics):
    for rel, live in mig.files():
        p = f"{mig.SNAP}/{rel}"
        L = open(p, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
        for n in range(1, len(mig.heads(L)) + 1):
            v = blob_of(p, n)[4]
            if v[0] in magics and v[2] >= 2:
                return p, n, v[0]
    raise SystemExit(f"no instance with magic in {magics} and two captures")


def blobs():
    for magics, width in (((7700011.0, 7700010.0, 7700008.0), 24), ((7700002.0,), 7)):
        p, n, magic = find_instance(magics)
        L, hi, j, k, v = blob_of(p, n)
        off = 3 + int(v[2]) * 32768
        mod = list(v)
        for t in range(width):
            mod[off + t] = 0.4 + 0.1 * t                    # up
            mod[off + width + t] = 0.3 + 0.05 * t           # down
            mod[off + 2 * width + t] = 1.3 + 0.2 * (t % 5)  # period, seconds
            mod[off + 3 * width + t] = t % 3                # shape: Sine, Triangle, Random
        mod[off + 4 * width] = 1                            # remembered drift target
        r0 = off + 4 * width + 1
        for t in range(0, width, 3):
            mod[r0 + t] = 2.0                               # ramp by
            mod[r0 + width + t] = 4.0                       # duration (seconds, below)
        mod[r0 + 3 * width] = 2                             # remembered ramp target
        # Layer levels need an audible base for a level drift to be heard.
        def old_line(line, t_d=1, t_r=2):
            s = parse_line(line)
            s[35], s[44] = str(t_d), str(t_r)
            s[36], s[37], s[38], s[40] = fmt(mod[off + t_d]), fmt(mod[off + width + t_d]), \
                fmt(mod[off + 2 * width + t_d]), fmt(mod[off + 3 * width + t_d])
            s[45], s[47] = fmt(mod[r0 + t_r]), fmt(mod[r0 + width + t_r])
            s[39], s[46], s[50], s[10] = "1", "1", "1", "60"
            n_s = max(kk for kk, vv in s.items() if vv is not None)
            return render_line(line, s, n_sliders=n_s)
        po, pn, pc = (os.path.join(tmp, f"b{width}{x}.RPP") for x in "onc")
        write_project(po, L, hi, j, k, mod, old_line)
        write_project(pn, L, hi, j, k, mod, lambda ln: mig.remap_line(old_line(ln), "synthetic"))
        write_project(pc, L, hi, j, k, v, old_line)
        a, b, c = run(OLD, 12, po, n), run(NEW, 12, pn, n), run(OLD, 12, pc, n)
        same, matters = np.array_equal(a, b), not np.array_equal(a, c)
        report(same and matters and np.abs(a).max() > 0,
               f"a real {magic:.0f} blob with drift and ramp on all {width} old targets: "
               f"loads bit-identical {same}; they matter {matters}")


def fmt(x):
    return str(int(x)) if float(x) == int(x) else repr(round(float(x), 6))


LADDER = ["4 octaves down", "3 octaves down", "2 octaves down", "1 octave down", "a fifth down", "a fourth down",
          "Original (unison)", "a fourth up", "a fifth up", "1 octave up", "2 octaves up", "3 octaves up",
          "4 octaves up", "Custom 1", "Custom 2", "Custom 3"]
AUTHORED = (["Morph", "Auto-morph time", "Texture", "Wash grain", "Spread", "Pitch", "Stereo width", "Denoise",
             "Low cut", "High cut", "Overtone harmonic", "Overtone lift", "Overtone width", "Layer level (all layers)"]
            + [f"{x} level" for x in LADDER] + ["Layer pitch (all Custom layers)", "Custom 1 pitch", "Custom 2 pitch",
                                                "Custom 3 pitch", "Layer overtone harmonic (all layers)"]
            + [f"{x} overtone harmonic" for x in LADDER] + ["Input level", "Output level", "Play for", "Rest for"])
OLD_NAMES = ["Texture", "Spread", "Pitch", "Stereo width", "Low cut", "Output level", "Overtone harmonic",
             "High cut"] + [f"{x} level" for x in LADDER]


def names():
    src = open(os.path.join(ROOT, "src", f"{FX}.jsfx"), encoding="utf-8").read()
    for sid in (35, 44):
        m = re.search(rf"^slider{sid}:0<0,54,1{{(.*?)}}>", src, re.M)
        report(bool(m) and m.group(1).split(",") == AUTHORED, f"slider {sid}'s 55 names are the authored list")
    bad = [f"{o} -> {AUTHORED[mig.O2N[i]]}" for i, o in enumerate(OLD_NAMES) if AUTHORED[mig.O2N[i]] != o]
    report(not bad and len(AUTHORED) == 55, "every old target keeps its name at its new index" + (": " + "; ".join(bad) if bad else ""))


def base_project():
    # AUTHORED, not searched for. The first search picked i-was-born-here, whose
    # captures list no usable slot: with no voice to lift, all seventeen layer
    # overtone targets "changed nothing", and so did the same control moved by hand.
    # Rozaya asked the right questions -- was the lift raised, was the harmonic high
    # enough, did the sound have more than one harmonic. breath-by-breath pt. 2's
    # first instance is five pitched voice captures, E2 to G3.
    return f"{mig.SNAP}/finished/breath-by-breath pt. 2.RPP", 1


# Pure voice, overtone on at harmonic 6 with the lift raised to 36 dB.
OT = [(10, 0), (18, 6), (19, 36)]
def layer(i, harm=None):
    st = [[(21, i)], [(23, -6)] + ([(27, harm)] if harm is not None else [])]
    return st


# (target, name, stages before the drift, amount)
def target_cases():
    c = [(0, "Morph", [[(7, 0), (6, 50)]], 40), (1, "Auto-morph time", [[(7, 1), (8, 1), (9, 2)]], 1.5),
         (3, "Wash grain", [[(10, 70)]], 100), (7, "Denoise", [[(10, 70)]], 60),
         (11, "Overtone lift", [OT], 20), (12, "Overtone width", [OT], 2),
         (13, "Layer level (all layers)", [], 50),
         (30, "Layer pitch (all Custom layers)", layer(13), 5)]
    c += [(31 + q, f"Custom {q + 1} pitch", layer(13 + q), 5) for q in range(3)]
    c += [(34, "Layer overtone harmonic (all layers)", [OT] + layer(9, 3), 2)]
    c += [(35 + i, f"{LADDER[i]} overtone harmonic", [OT] + layer(i, 3), 2) for i in range(16)]
    c += [(51, "Input level", [], 20), (53, "Play for", [[(31, 1), (32, 1)]], 0.7),
          (54, "Rest for", [[(31, 1), (32, 1)]], 0.7)]
    return c


def drift_stages(pre, t, amt, per=1.3):
    return list(pre) + [[(35, t)], [(39, 1), (38, per), (36, amt), (37, amt)]]


def targets():
    p, n = base_project()
    cases = target_cases()

    def one(case):
        t, name, pre, amt = case
        per = 1.7 if t in (53, 54) else 1.3
        r = [run(NEW, 8, p, n, drift_stages(pre, t, a, per)) for a in (0, amt)]
        return t, name, not np.array_equal(*r), all(np.isfinite(x).all() for x in r)
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for t, name, moved, finite in ex.map(one, cases):
            report(moved and finite, f"new target {t} {name}: changes the sound {moved}")
    report(len(cases) == 31, f"{len(cases)} new targets tested, 31 expected")


def all_entry():
    p, n = base_project()
    pre = layer(3) + layer(9)          # two layers audible: 1 octave down and 1 octave up
    one_layer = run(NEW, 8, p, n, drift_stages(pre, 17, 50))   # 1 octave down's level only
    every = run(NEW, 8, p, n, drift_stages(pre, 13, 50))       # Layer level (all layers)
    report(not np.array_equal(one_layer, every),
           "Layer level (all layers) reaches more than its first member (1 octave up moves too)")


def layers():
    """No project uses a layer overtone harmonic, so the 123-instance check cannot
    see one. A bulk rename broke it on 2026-09-11 while all 123 still passed; this is
    the check that caught it, on a pitched voice with the lift raised."""
    p, n = base_project()
    for h in (3, 4):
        a, b = run(OLD, 6, p, n, [OT] + layer(9, h)), run(NEW, 6, p, n, [OT] + layer(9, h))
        report(np.array_equal(a, b), f"a layer overtone harmonic of {h} set by hand: old == new")
    a, b = run(NEW, 6, p, n, [OT] + layer(9, 3)), run(NEW, 6, p, n, [OT] + layer(9, 4))
    report(not np.array_equal(a, b), "and 3 against 4 changes the sound, so the check can fail")


def fresh():
    a, b = run(OLD, 8), run(NEW, 8)
    report(np.array_equal(a, b), "a fresh instance renders identically")


def applied():
    bad = [rel for rel, live in mig.files()
           if open(live, encoding="utf-8", errors="surrogateescape", newline="").read() != mig.convert(f"{mig.SNAP}/{rel}")[0]]
    report(not bad, "every live file equals its verified copy" + (": " + ", ".join(bad) if bad else ""))


def main():
    secs = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()]
    for s in (secs or ["names", "fresh", "current", "blobs", "targets", "all_entry"]):
        globals()[s]()
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
