#!/usr/bin/env python3
"""Hidden-limit audit (2026-09-13): does each control the 2026-09-06 range sweep widened
really reach its new top, or does the code stop it short?

Reading the code missed Spread (the sweep's clamp scan followed a value one hop). This
LISTENS. For each control, in up to three of Rozaya's saved copies of its plugin, set after
the first block (--set-after, the way a person moves it):
  half  = half the old ceiling (or the lower bound, if that is higher)
  old   = the old ceiling
  mid   = halfway between the old ceiling and the new top
  top   = the new top
Verdicts:
  couldn't judge   half == old in every copy tried: not heard, so nothing is proved
  HIDDEN LIMIT     old == top: past the old ceiling nothing changes
  STOPS BETWEEN    mid == top but old != mid: a limit somewhere above the old ceiling
  reaches          old != mid != top
The detector was proven first on three known limits (Passage Spread 150, both Wash grains).
A few seconds of render cannot hear a length in minutes, and a drift or per-voice value is
only heard where that copy uses it -- 104 of 154 were "couldn't judge" on 2026-09-13.
Results: docs/backlog.md, "Hidden limits".

The control list (hidden_limit_audit_20260913_controls.json) is the sweep's 176 range
changes (commits 8423c4d, 7e63784) matched to TODAY's slider ids by name, minus 10 in
archived plugins and 12 replaced since. Ids move when a layout changes: re-match before
trusting a run on a later tree. Passage runs on migrated temp copies of its saves.

    python tools/hidden_limit_audit_20260913.py [--jobs N] [--only plugin.jsfx] [--id N]
"""
import concurrent.futures as cf, json, os, re, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import passage_migrate_20260911 as mig

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
LIVE = "E:/reaper"
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 2
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
ONLY_ID = int(sys.argv[sys.argv.index("--id") + 1]) if "--id" in sys.argv else None
SECONDS, COPIES = 6, 3
tmp = tempfile.mkdtemp()
controls = json.load(open(os.path.join(ROOT, "tools", "hidden_limit_audit_20260913_controls.json")))


def saved_copies():
    """plugin file name -> [(project path, instance number)], backups skipped."""
    names = {os.path.basename(c["file"]) for c in controls}
    out = {n: [] for n in names}
    for top, dirs, files in os.walk(LIVE):
        dirs[:] = [d for d in dirs if d.lower() != "backups"]
        for f in files:
            if not f.lower().endswith(".rpp"):
                continue
            p = os.path.join(top, f).replace("\\", "/")
            counts = {}
            for line in open(p, encoding="utf-8", errors="surrogateescape"):
                if "<JS " in line and "<JS_SER" not in line:
                    for n in names:
                        if n in line:
                            counts[n] = counts.get(n, 0) + 1
                            out[n].append((p, counts[n]))
    return out


insts = saved_copies()
plugins, rpps = {}, {}


def context(fx, k):
    if fx not in plugins:
        text = open(os.path.join(ROOT, "src", fx), encoding="utf-8").read()
        if text.count("_tp = time_precise();") == 1:   # the spectral plugins scramble rand() by load time
            text = text.replace("_tp = time_precise();", "_tp = 0.25;")
        plugins[fx] = os.path.join(tmp, fx)
        open(plugins[fx], "w", encoding="utf-8", newline="").write(text)
    if (fx, k) not in rpps:
        rpp, inst = insts[fx][k]
        if fx == mig.FX:
            conv = os.path.join(tmp, f"audit{k}-" + re.sub(r"[/\\: ']", "_", rpp))
            open(conv, "w", encoding="utf-8", errors="surrogateescape", newline="").write(mig.convert(rpp)[0])
            rpp = conv
        rpps[(fx, k)] = (rpp, inst)
    return plugins[fx], rpps[(fx, k)]


def render(fx, sid, value, k):
    plugin, (rpp, inst) = context(fx, k)
    out = os.path.join(tmp, f"a_{abs(hash((fx, sid, value, k)))}.csv")
    cmd = [EXE, plugin, "--rpp", rpp, "--fx", fx[:-5], "--instance", str(inst), "--seconds", str(SECONDS),
           "--input", "noise", "--csv", out, "--quiet", "--stage", "--set-after", f"{sid}={value}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{fx} slider{sid}={value}: {r.stderr[-300:]}")
    a = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))
    os.remove(out)
    return a


def one(m):
    fx = os.path.basename(m["file"])
    lo, top = float(m["cur_range"][0]), float(m["cur_range"][1])
    old = float(m["old"][1])
    if not lo < old < top:
        return m, "skipped", f"old ceiling {old} is not inside today's range {lo}..{top}"
    if not insts.get(fx):
        return m, "couldn't judge", "no saved copy of this plugin"
    half, mid = max(lo, old / 2), (old + top) / 2
    values = f"half {half:g}, old {old:g}, mid {mid:g}, top {top:g}"
    tried = []
    for k in range(min(COPIES, len(insts[fx]))):
        try:
            r = {n: render(fx, m["cur_id"], v, k) for n, v in (("half", half), ("old", old), ("mid", mid), ("top", top))}
        except RuntimeError as e:
            return m, "error", str(e)
        where = f"{os.path.basename(insts[fx][k][0])} #{insts[fx][k][1]}"
        eq = lambda a, b: np.array_equal(r[a], r[b])
        if eq("half", "old"):
            tried.append(where)
            continue
        v = "HIDDEN LIMIT" if eq("old", "top") else "STOPS BETWEEN" if eq("mid", "top") else "reaches"
        return m, v, f"{values}; heard in {where}"
    return m, "couldn't judge", f"{values}; not heard in {', '.join(tried)}"


if __name__ == "__main__":
    todo = [m for m in controls if (not ONLY or os.path.basename(m["file"]) == ONLY)
            and (ONLY_ID is None or m["cur_id"] == ONLY_ID)]
    counts = {}
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for m, verdict, note in ex.map(one, todo):
            counts[verdict] = counts.get(verdict, 0) + 1
            print(f"{verdict:15} {os.path.basename(m['file'])} slider{m['cur_id']} '{m['cur_name'][:60]}' -- {note}", flush=True)
    print("---", counts, f"of {len(todo)} controls")
