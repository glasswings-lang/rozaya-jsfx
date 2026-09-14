#!/usr/bin/env python3
"""The Morpher's pitch layout in the REAL REAPER, through kin_bridge.lua. Nothing is saved.

Only in claude-testing002-bridge.RPP -- it refuses any other project. Two traps from
Passage's install (session-log 2026-09-13) shape it:
  * installing does not reach an instance REAPER already has open, so the open Morpher is
    REBUILT from the migrated project file on DISK (its effect deleted, then its track
    chunk read from disk put back), never from a chunk the old instance wrote;
  * a selector is set a moment before the values it governs.

Then, on a TEMPORARY track with a fresh Morpher: values on Layer 14 and Layer 3 (pitch,
units, fine tune), a Drift amount unit on Layer 1 pitch and a Ramp by unit on Layer 1 fine
tune, parked on All. The track is duplicated by REAPER's own action -- the @serialize
duplicate path -- and every value is read back on the original and the copy. Both temporary
tracks are deleted. Bridge param index = slider number - 1.

    python tools/morpher_reaper_roundtrip_20260913.py --check   # read-only: project, track, names
    python tools/morpher_reaper_roundtrip_20260913.py --run
"""
import os, re, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reaper_bridge as rb

PROJECT = "claude-testing002-bridge.RPP"
TRACK = "spectral_vowel_morpher"
FXFILE = "JS: glasswings/spectral_vowel_morpher.jsfx"
TEMP = "claude-morpher-roundtrip"
P = lambda slider: slider - 1                      # bridge param index
LAYER, L_ACTIVE, L_PITCH, L_PUNIT, L_FINE, L_FUNIT = 29, 30, 31, 32, 33, 34
DT, DUP, DUNIT, RT, RBY, RUNIT = 46, 47, 49, 56, 57, 58
fails = 0


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def must(command, timeout=8.0):
    ok, text = rb.send(command, timeout)
    if not ok:
        raise SystemExit(f"REFUSED: the bridge answered an error to {command!r}: {text}")
    return text


def project_path():
    return (re.search(r'project="([^"]*)"', must("state")) or [None, ""])[1]


def track_index(name):
    for i, t in enumerate(rb.board()["tracks"]):
        if t["name"] == name:
            return i
    return None


def disk_chunk(rpp, name):
    """The <TRACK ...> block whose NAME is `name`, read from the project file on disk."""
    lines = open(rpp, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    for i, l in enumerate(lines):
        if l.strip().startswith("<TRACK") and i + 1 < len(lines) and lines[i + 1].strip() == f"NAME {name}":
            depth, j = 0, i
            while True:
                s = lines[j].strip()
                depth += s.startswith("<")
                depth -= s == ">"
                j += 1
                if depth == 0:
                    return "".join(lines[i:j])
    return None


def lua(code):
    p = os.path.join(tempfile.gettempdir(), "claude_morpher_roundtrip.lua")
    open(p, "w", encoding="utf-8").write(code)
    return must(f"evalfile {p}", timeout=15.0)


def get(track, param):
    text = must(f"get {track} 0 {param}")
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group(0)) if m else None, text


def setv(track, slider, value, pause=0.35):
    must(f"setv {track} 0 {P(slider)} {value}")
    time.sleep(pause)


def check():
    proj = project_path()
    report(proj.endswith(PROJECT), f"the open project is {proj}")
    # A fresh Morpher adopts its selector mirrors in @block, and nothing it is sent is stored
    # until then. With REAPER's audio engine stopped no @block runs, so every value would read
    # back as a default and look like a broken save (2026-09-13: six false failures this way).
    audio = lua('return tostring(reaper.Audio_IsRunning())').strip()
    report(audio == "1", f"REAPER's audio engine is running (Audio_IsRunning = {audio})")
    if audio != "1":
        raise SystemExit("REFUSED: REAPER's audio engine is not running -- no @block, so nothing would be stored")
    idx = track_index(TRACK)
    report(idx is not None, f"track {TRACK!r} is index {idx}")
    if idx is None:
        return None, None
    fx = rb.board()["tracks"][idx]["fx"]
    names = fx[0]["params"] if fx else {}
    print(f"     its Morpher has {len(names)} params; p28 = {names.get(28, ('?',))[0]!r}, p30 = {names.get(30, ('?',))[0]!r}")
    return proj, idx


def run():
    proj, idx = check()
    if not proj or not proj.endswith(PROJECT) or idx is None:
        raise SystemExit("REFUSED: not the claude test project, or no Morpher track")
    # 1. Rebuild the open instance from the migrated file on DISK.
    chunk = disk_chunk(proj, TRACK)
    if not chunk or "<JS " not in chunk:
        raise SystemExit("REFUSED: could not read the Morpher track from the project file on disk")
    cpath = os.path.join(tempfile.gettempdir(), "claude_morpher_chunk.txt")
    open(cpath, "w", encoding="utf-8", newline="").write(chunk)
    got = lua(f"""
local f = io.open([[{cpath}]], "r"); local chunk = f:read("a"); f:close()
local tr = reaper.GetTrack(0, {idx})
while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
local ok = reaper.SetTrackStateChunk(tr, chunk, false)
return tostring(ok) .. " fx=" .. reaper.TrackFX_GetCount(tr) .. " params=" .. reaper.TrackFX_GetNumParams(tr, 0)
""")
    time.sleep(1.5)
    names = rb.board()["tracks"][idx]["fx"][0]["params"]
    report(got.startswith("true") and names.get(P(LAYER), ("",))[0] == "Layer"
           and names.get(P(L_PITCH), ("",))[0].startswith("Layer pitch value"),
           f"track {idx} rebuilt from disk ({got}); p28 {names.get(P(LAYER), ('?',))[0]!r}")
    # 2. A temporary track with a fresh Morpher.
    before = len(rb.board()["tracks"])
    t = int(re.search(r"\d+", must(f"addtrack {TEMP}")).group(0))
    must(f"addfx {t} {FXFILE}")
    time.sleep(1.5)
    setv(t, LAYER, 14)
    for s, v in ((L_PUNIT, 2), (L_PITCH, 700), (L_FINE, 30), (L_FUNIT, 0)):
        setv(t, s, v, 0.15)
    setv(t, LAYER, 3)
    for s, v in ((L_PITCH, -20), (L_FUNIT, 1), (L_FINE, 0.5)):
        setv(t, s, v, 0.15)
    setv(t, DT, 16)
    for s, v in ((DUNIT, 3), (DUP, 25)):
        setv(t, s, v, 0.15)
    setv(t, RT, 33)
    for s, v in ((RUNIT, 1), (RBY, 4)):
        setv(t, s, v, 0.15)
    setv(t, LAYER, 0, 0.6)
    # 3. REAPER duplicates it: the copy is t + 1.
    lua(f"""
reaper.SetOnlyTrackSelected(reaper.GetTrack(0, {t}))
reaper.Main_OnCommand(40062, 0)
return reaper.CountTracks(0)
""")
    time.sleep(1.5)
    copy = t + 1
    report(rb.board()["tracks"][copy]["name"] == TEMP, f"REAPER made a copy at track {copy}")
    views = [("Layer 14", [(LAYER, 14)], {L_PITCH: 700, L_PUNIT: 2, L_FINE: 30, L_FUNIT: 0}),
             ("Layer 3", [(LAYER, 3)], {L_PITCH: -20, L_PUNIT: 1, L_FINE: 0.5, L_FUNIT: 1}),
             ("Drift target Layer 1 pitch", [(DT, 16)], {DUNIT: 3, DUP: 25}),
             ("Ramp target Layer 1 fine tune", [(RT, 33)], {RUNIT: 1, RBY: 4})]
    for track, which in ((copy, "the copy"), (t, "the original")):
        if track == copy:
            v, text = get(copy, P(LAYER))
            report(v == 0, f"{which} arrives parked on All (read {text})")
        for label, sel, want in views:
            for s, val in sel:
                setv(track, s, val, 0.5)
            got = {s: get(track, P(s)) for s in want}
            bad = {s: g[1] for s, g in got.items() if g[0] is None or abs(g[0] - want[s]) > 1e-6}
            report(not bad, f"{which}, {label}: {len(want)} values as set" + (f" -- DIFFER {bad}" if bad else ""))
    # 4. Put the project back as it was: delete the two temporary tracks, the copy first.
    must(f"deltrack {copy}")
    time.sleep(0.5)
    must(f"deltrack {t}")
    time.sleep(0.8)
    report(len(rb.board()["tracks"]) == before and track_index(TEMP) is None,
           f"the temporary tracks are gone ({len(rb.board()['tracks'])} tracks, as before)")
    print(f"{fails} failures; nothing saved")


if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    elif "--check" in sys.argv:
        check()
    else:
        raise SystemExit(__doc__)
