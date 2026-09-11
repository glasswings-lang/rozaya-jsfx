#!/usr/bin/env python3
"""What only REAPER can show: nested selectors, note mirrors, and save/reopen, driven
live through kin_bridge.lua (REAPER/Scripts) in E:/reaper/finished/test-projects/
claude-testing002-bridge.RPP.

    python tools/bridge_ui_test.py drive   STATE.json   # checks, then leaves distinct values
    (Rozaya saves the project, closes it, reopens it)
    python tools/bridge_ui_test.py verify  STATE.json   # re-selects everything, reads it back

Checks, per plugin, found by control NAME on the bridge's board:
- Drift target and Ramp target: a value set on one target stays with it when the
  selector moves to another and back.
- Every "... note name": in Semitones, picking a note sets the value, and typing a
  value moves the note.
- The per-item selectors -- Polyrhythm's Voice, the Heartbeat / Breath Generator /
  Rhythm Track pitch targets, Resonance Bank's Band, the Morpher's Layer, Passage's
  Capture slot -- each item keeps its own value; All writes every item.
Values are compared by the board's normalized position against the slider's
declared range in src/, so display rounding cannot hide a wrong value.
"""
import json, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = r"C:\Users\solst\reaper_kin_bridge\command.txt"
MAN = r"C:\Users\solst\reaper_kin_bridge\manifest.txt"
DECL = re.compile(r"^slider(\d+):([^<]*)<([^>]*)>(.*)$")

# plugin file -> (selector param, item param, item a, item b, All index or None)
ITEM_SELECTORS = {
    "polyrhythm_phase_v3": (14, 17, 2, 3, 0),
    "heartbeat gen":       (8, 11, 1, 2, 0),
    "breath_gen":          (6, 9, 1, 2, 0),
    "rhythm-track":        (4, 7, 1, 2, 0),
    "resonance_bank":      (3, 6, 1, 2, None),
    "spectral_vowel_morpher": (20, 22, 7, 8, None),
    "spectral_vowel_passage": (0, 4, 1, 2, None),
}

ITEM_VALUES = {   # (item a, item b, All)
    "polyrhythm_phase_v3": (62, 64, 61),
    "heartbeat gen":       (50, 52, 51),
    "breath_gen":          (62, 64, 61),
    "rhythm-track":        (74, 76, 75),
    "resonance_bank":      (700, 900, 0),
}

def ranges(plugin):
    out = {}
    for line in open(os.path.join(ROOT, "src", plugin + ".jsfx"), encoding="utf-8"):
        d = DECL.match(line.rstrip("\r\n"))
        if d:
            spec = d.group(3).split("{")[0].split(",")
            enum = re.search(r"\{(.*)\}", d.group(3))
            out[int(d.group(1)) - 1] = (float(spec[0]), float(spec[1]),
                                        float(spec[2]) if len(spec) > 2 else 0,
                                        len(enum.group(1).split(",")) if enum else 0)
    return out

def board():
    tracks, cur = {}, None
    for line in open(MAN, encoding="utf-8", errors="replace"):
        m = re.match(r'track=(\d+) name="(.*)"', line)
        if m:
            cur = {"name": m.group(2), "params": {}}
            tracks[int(m.group(1))] = cur
            continue
        m = re.match(r'\s+p(\d+) "(.*)" norm=(\S+) val="(.*)"', line)
        if m and cur is not None:
            cur["params"][int(m.group(1))] = (m.group(2), float(m.group(3)), m.group(4))
    return tracks

def send(t, p, v):
    t0 = time.time()
    with open(BOX, "w") as f:
        f.write(f"setv {t} 0 {p} {v}\n")
    while os.path.getsize(BOX) > 0 and time.time() - t0 < 4:
        time.sleep(0.03)
    consumed = time.time()
    while os.path.getmtime(MAN) < consumed + 0.45 and time.time() - t0 < 6:
        time.sleep(0.05)

def norm_of(r, v):
    lo, hi, step, n = r
    return (v - lo) / (hi - lo) if hi > lo else 0

class Run:
    def __init__(self):
        self.fails, self.lines, self.expect = 0, [], []

    def check(self, t, rng, label, p, v, remember=None):
        # The bridge REWRITES the board every 0.4 s, so a read can land mid-write and
        # see half a file -- which crashed the first live run on track 3. Re-read
        # until this track and this control are both there.
        for _ in range(60):
            bd = board()
            if t in bd and p in bd[t]["params"]:
                break
            time.sleep(0.05)
        b = bd[t]["params"]
        got = b[p][1]
        want = norm_of(rng[p], v)
        ok = abs(got - want) < 0.002
        self.fails += not ok
        self.lines.append(f"{'ok  ' if ok else 'FAIL'} {board_name(t)}: {label} "
                          f"({b[p][0]} reads '{b[p][2]}')")
        if remember is not None:
            self.expect.append({"t": t, "select": remember, "p": p, "v": v, "label": label})
        return ok

_names = {}
def board_name(t):
    return _names.get(t, str(t))

def frac_value(r, frac):
    lo, hi, step, n = r
    v = lo + (hi - lo) * frac
    if step:
        v = round(round((v - lo) / step) * step + lo, 6)
    return v

def stable_board():
    # Two reads in a row with the same track count, so a half-written board cannot
    # silently drop the plugins at the end of the list.
    prev = None
    for _ in range(100):
        b = board()
        if prev is not None and len(b) == len(prev) and len(b) > 0:
            return b
        prev = b
        time.sleep(0.5)
    return b

def drive(state_path):
    b = stable_board()
    print(f"board: {len(b)} tracks", flush=True)
    run = Run()
    for t, tr in sorted(b.items()):
        plugin = tr["name"]
        _names[t] = plugin
        if not os.path.exists(os.path.join(ROOT, "src", plugin + ".jsfx")):
            continue
        rng = ranges(plugin)
        params = tr["params"]
        names = {p: n for p, (n, _, _) in params.items()}
        # note mirrors
        for p, n in names.items():
            if n.lower().endswith("note name") and "pitch mode" in names.get(p - 1, "").lower():
                send(t, p - 1, 1)
                send(t, p, 69)
                run.check(t, rng, f"{n}: A4 in Semitones sets the value to 69", p + 1, 69)
                send(t, p + 1, 72)
                run.check(t, rng, f"{n}: value 72 moves the note to C5", p, 72)
        # drift and ramp selectors
        for sel_name, amount_frac in (("Drift target", (0.3, 0.6)), ("Ramp target", (0.65, 0.8))):
            sp = next((p for p, n in names.items() if n == sel_name), None)
            if sp is None:
                continue
            ap = sp + 1
            a, c = frac_value(rng[ap], amount_frac[0]), frac_value(rng[ap], amount_frac[1])
            # Two targets that EXIST. Rhythm Track's lists hold only two entries, and
            # asking for index 2 there silently lands on 1 -- the first live run
            # reported that as a plugin failure when it was the test's.
            n_entries = rng[sp][3] or int(rng[sp][1] - rng[sp][0] + 1)
            t1 = 1 if n_entries >= 3 else 0
            t2 = t1 + 1
            send(t, sp, t1); send(t, ap, a)
            send(t, sp, t2); send(t, ap, c)
            send(t, sp, t1)
            run.check(t, rng, f"{sel_name}: target {t1} kept its {names[ap]}", ap, a, [[sp, t1]])
            send(t, sp, t2)
            run.check(t, rng, f"{sel_name}: target {t2} kept its {names[ap]}", ap, c, [[sp, t2]])
        # item selectors
        if plugin in ITEM_SELECTORS:
            sp, ip, ia, ib, allix = ITEM_SELECTORS[plugin]
            # Pitch values stay musical (a fraction of 0..20000 would be note 6200).
            # All uses 61, never 60: on All, a value equal to what item 1 already
            # shows is no change and writes nothing -- the runner trap, live.
            va, vb, vall = ITEM_VALUES.get(plugin, (frac_value(rng[ip], 0.31),
                                                    frac_value(rng[ip], 0.37),
                                                    frac_value(rng[ip], 0.34)))
            if allix is not None:
                send(t, sp, allix); send(t, ip, vall)
                send(t, sp, ia)
                run.check(t, rng, f"{names[sp]} All wrote item {ia}", ip, vall)
                send(t, sp, ib)
                run.check(t, rng, f"{names[sp]} All wrote item {ib}", ip, vall)
            send(t, sp, ia); send(t, ip, va)
            send(t, sp, ib); send(t, ip, vb)
            send(t, sp, ia)
            run.check(t, rng, f"{names[sp]} item {ia} kept its own {names[ip]}", ip, va, [[sp, ia]])
            send(t, sp, ib)
            run.check(t, rng, f"{names[sp]} item {ib} kept its own {names[ip]}", ip, vb, [[sp, ib]])
        print("\n".join(run.lines), flush=True)
        run.lines = []
    json.dump({"names": _names, "expect": run.expect}, open(state_path, "w"), indent=1)
    print(f"--- drive: {run.fails} failure(s); {len(run.expect)} values remembered for the reopen check")
    return run.fails

def verify(state_path):
    st = json.load(open(state_path))
    _names.update({int(k): v for k, v in st["names"].items()})
    run = Run()
    b = stable_board()
    for e in st["expect"]:
        t = e["t"]
        if b.get(t, {}).get("name") != _names[t]:
            run.fails += 1
            run.lines.append(f"FAIL track {t} is not {_names[t]} on the board any more")
            continue
        for sp, sv in e["select"]:
            send(t, sp, sv)
        run.check(t, ranges(_names[t]), "after reopen, " + e["label"], e["p"], e["v"])
    print("\n".join(run.lines))
    print(f"--- verify: {run.fails} failure(s) of {len(st['expect'])}")
    return run.fails

if __name__ == "__main__":
    phase, state = sys.argv[1], sys.argv[2]
    sys.exit(1 if (drive(state) if phase == "drive" else verify(state)) else 0)
