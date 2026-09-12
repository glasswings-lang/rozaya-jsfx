#!/usr/bin/env python3
"""Which controls switch with a selector? Measured live in REAPER, never read off a label.

Rozaya, 2026-09-12, on Ramp start delay: "It switches. when. you change. the target? ...
if it's gonna do that, can't it at least say that's what it's doing?" Before any label
says "(per target)" or "(all targets)", this measures it on the real plugins in
claude-testing002-bridge.RPP through kin_bridge.lua.

For each plugin and each selector (Drift target, Ramp target, and Band / Layer / Voice /
Segment / Capture slot where a plugin has one), for each Drift and Ramp control:
  selector -> option 0, control -> A; selector -> option 1, read; control -> B;
  selector -> option 0, read.
  PER  = it read something other than A on option 1, and A again back on option 0
  ALL  = it read A on option 1, and B back on option 0 (the value did not switch)
  ?    = anything else (hidden, mirrored, clamped) -- look at it by hand
Nothing is saved. Visible values are put back afterwards; banks behind other options may
keep the test values, which is why this runs only in the test project.

    python tools/selector_scope_probe.py [--out report.txt] [--only name-substring]
"""
import sys, time
sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
import reaper_bridge as rb

OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
ONLY = sys.argv[sys.argv.index("--only") + 1].lower() if "--only" in sys.argv else None
EXTRA = ("Band", "Layer", "Voice", "Segment", "Capture slot")
A, B = 0.25, 0.75
PAUSE = 0.12


def once(cmd, timeout=6):
    ok, text = rb.send(cmd, timeout=timeout)
    if not ok:
        raise RuntimeError(f"bridge refused {cmd!r}: {text}")
    return text


def norm(t, f, p):
    return float(once(f"eval return reaper.TrackFX_GetParamNormalized(reaper.GetTrack(0,{t}),{f},{p})"))


def setn(t, f, p, v):
    once(f"set {t} {f} {p} {v}")
    time.sleep(PAUSE)


def seti(t, f, p, i):
    once(f"setv {t} {f} {p} {i}")
    time.sleep(PAUSE)


state = once("state")
if "claude-testing002-bridge" not in state:
    raise SystemExit("not in the claude test project: " + state.split("project=")[-1])
once("stop")
lines = []
board = rb.board()
for t, track in enumerate(board["tracks"]):
    for f, fx in enumerate(track["fx"]):
        if ONLY and ONLY not in fx["name"].lower():
            continue
        params = fx["params"]
        selectors = [(p, n) for p, (n, _, _) in params.items()
                     if n in ("Drift target", "Ramp target") or n.startswith(EXTRA)]
        members = [(p, n) for p, (n, _, _) in params.items()
                   if n.lower().startswith(("drift ", "ramp ")) and n not in ("Drift target", "Ramp target")]
        for sp, sname in selectors:
            if sname == "Drift target":
                block = [m for m in members if m[1].lower().startswith("drift ")]
            elif sname == "Ramp target":
                block = [m for m in members if m[1].lower().startswith("ramp ")]
            else:
                block = members
            if not block:
                continue
            s0 = norm(t, f, sp)
            for mp, mname in block:
                m0 = norm(t, f, mp)
                try:
                    seti(t, f, sp, 0); setn(t, f, mp, A); a_on0 = norm(t, f, mp)
                    seti(t, f, sp, 1); on1 = norm(t, f, mp)
                    setn(t, f, mp, B); b_on1 = norm(t, f, mp)
                    seti(t, f, sp, 0); back0 = norm(t, f, mp)
                    if abs(on1 - a_on0) > 1e-4 and abs(back0 - a_on0) <= 1e-4:
                        kind = "PER"
                    elif abs(on1 - a_on0) <= 1e-4 and abs(back0 - b_on1) <= 1e-4:
                        kind = "ALL"
                    else:
                        kind = "?"
                    detail = f"set {a_on0:.3f} | on option 1 read {on1:.3f} | set {b_on1:.3f} | back on 0 read {back0:.3f}"
                except RuntimeError as e:
                    kind, detail = "?", f"error: {e}"
                finally:
                    setn(t, f, mp, m0)
                line = f"{kind:3s} | track {t} {track['name']} | {sname} | p{mp} {mname} | {detail}"
                print(line, flush=True)
                lines.append(line)
            setn(t, f, sp, s0)
if OUT:
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"--- {sum(l.startswith('PER') for l in lines)} per-selector, {sum(l.startswith('ALL') for l in lines)} "
      f"shared, {sum(l.startswith('?') for l in lines)} to look at by hand")
