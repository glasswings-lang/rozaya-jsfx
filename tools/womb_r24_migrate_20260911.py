#!/usr/bin/env python3
"""Womb's forty-nine targets: the ten files, and why.

docs/layouts/womb-r24-20260911.md. The plugin remaps an old eleven- or ten-target
blob itself, selectors included. The LINE's two selectors (72 Drift target, 81 Ramp
target) are remapped here in every copy, because two copies carry an UNVERSIONED
blob the plugin cannot remap from: to-sleep-within (Drift and Ramp on Inhale, 2)
and deep-night (a Ramp selector stored as 0.75, which the plugin reads as 0). A
selector is floored, as the plugin reads it, and written back whole.

  scattered      NEVER CARRIED OVER: its Womb line is still the 70-control layout of
                 2026-09-06, missed by both 2026-09-09 migrations (Drift movement,
                 then the pitch blocks), so the current plugin has been reading
                 its values in the wrong places -- the render peaks near 64. Taken
                 through both, using THOSE SCRIPTS' OWN RULES (imported, not
                 retyped), then the selector remap. Checked against 92effbe, the
                 last build with the 70-control layout. ("Yes, sync all the broken
                 things.")
  womb-and-baby  HELD unless --convert-womb-and-baby. Its Breath rate drift is in
                 Beats, where the target now counts beats per breath. The authored
                 conversion: up 5 / down 10 breaths a minute at tempo 70 on a
                 4.666668-beat breath becomes up 9.333344 / down 1.166667 beats --
                 the same two extremes, 14 and 3.5 beats. Asked of Rozaya
                 2026-09-11, not yet answered.

IDEMPOTENT BY CONSTRUCTION: reads the snapshot and writes the live file. A live
file equal to the result is already done; one equal to the snapshot is written;
anything else is refused. Dry run by default; --apply writes.
"""
import base64, math, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line, as_float
import suite_migrate_driftmoves_20260909 as driftmoves
import womb_migrate_pitchblocks_20260909 as pitchblocks

SNAP = "E:/reaper/finished/backups/snapshots/_pre-womb-r24-20260911"
LATER, FIN = "E:/reaper/to-play-with-later", "E:/reaper/finished"
FILES = [(f"to-play-with-later/{n}", f"{LATER}/{n}") for n in (
    "womb-bubbles-proto.RPP", "womb-and-baby-heartbeats-with-bloodflow.RPP", "micle.RPP", "scattered.rpp",
    "noisescape-august-18-2026.RPP", "surges.RPP")] + \
        [(f"finished/{n}", f"{FIN}/{n}") for n in ("back-to-life.RPP", "to-sleep-within.RPP", "deep-night.RPP")] + \
        [("finished/test-projects/claude-testing002-bridge.RPP", f"{FIN}/test-projects/claude-testing002-bridge.RPP")]
BABY = "womb-and-baby-heartbeats-with-bloodflow.RPP"
N_SLIDERS = 88
O2N = {0: 0, 1: 2, 2: 15, 3: 16, 4: 17, 5: 18, 6: 1, 7: 14, 8: 19, 9: 21, 10: 34}
# 9.333332 was first typed here, a rounding slip: the refusal below caught it, since
# the old slow extreme is 14.000012 beats on this 4.666668-beat breath.
BABY_UP, BABY_DOWN = 9.333344, 1.166667


def refuse(where, why):
    raise SystemExit(f"REFUSED {where}: {why}")


def heads(lines):
    return [i for i, l in enumerate(lines) if "<JS " in l and "<JS_SER" not in l and "womb_sound_generator_v3.jsfx" in l]


def remap_line(line, where, extra=None):
    s = parse_line(line)
    n = max(k for k, v in s.items() if v is not None)
    for sid in (72, 81):
        if s.get(sid) is not None:
            v = as_float(s[sid], f"slider {sid}")
            o = int(math.floor(v))
            if not 0 <= o <= 10:
                refuse(where, f"slider {sid} = {s[sid]} is not an eleven-target index")
            s[sid] = str(O2N[o])
    s.update(extra or {})
    return render_line(line, s, n_sliders=max(n, 72 if s.get(72) else n))


SCATTERED = "scattered.rpp"


def carry_scattered(line, where):
    """70 -> 71 by suite_migrate_driftmoves_20260909's Womb rule, then 71 -> 88 by
    womb_migrate_pitchblocks_20260909's, then the selector remap."""
    sp = driftmoves.SPECS["womb_sound_generator_v3"]
    slots = parse_line(line)
    stored = max(k for k, v in slots.items() if v is not None)
    if stored != sp["n_sliders_old"]:
        refuse(where, f"stores {stored} sliders, not the 70-control layout")
    sel = int(float(slots.get(sp["target_slider"]) or 0))
    for sid in range(sp["last"], sp["first"] - 1, -1):
        slots[sid + 1] = slots.get(sid)
    slots[sp["new_slider"]] = "0" if sp["steps"](sel) else "1"
    if float(slots[6]) <= 2:
        refuse(where, "slider 6 already reads as a pitch mode")
    new = {b: slots.get(a) for a, b in pitchblocks.MOVES}
    for src, (m, note, val, fine, fmod, default) in pitchblocks.FREQS.items():
        tok = slots.get(src)
        hz = float(tok) if tok not in (None, "-") else default
        new[m], new[note], new[fine], new[fmod] = "0", str(pitchblocks.nearest(hz)), "0", "2"
        new[val] = tok if tok not in (None, "-") else ("%g" % default)
    new[pitchblocks.TUNING_REF_SLIDER] = "440"
    return remap_line(render_line(line, new, n_sliders=pitchblocks.N_NEW), where)


def baby(lines, where):
    """The held conversion, applied only on request. Every input is asserted first."""
    (hi,) = heads(lines)
    s = parse_line(lines[hi + 1])
    tempo = next(float(l.split()[1]) for l in lines if l.strip().startswith("TEMPO "))
    seg = [as_float(s[k]) for k in (26, 27, 28, 29)]
    beats = sum(seg)
    if as_float(s[25]) != 1 or abs(tempo - 70) > 1e-9 or abs(beats - 4.666668) > 1e-6:
        refuse(where, f"breath unit {s[25]}, tempo {tempo}, breath {beats} beats -- not what was authored")
    if (s.get(72), s.get(73), s.get(74)) != ("7", "5", "10"):
        refuse(where, f"visible drift {s.get(72)} {s.get(73)} {s.get(74)} is not Breaths/min 5/10")
    r0 = tempo / beats
    quick, slow = tempo / (r0 + 5), tempo / (r0 - 10)
    if abs((beats - quick) - BABY_DOWN) > 1e-5 or abs((slow - beats) - BABY_UP) > 1e-5:
        refuse(where, f"authored amounts do not reach the old extremes {quick} and {slow}")
    j = hi + 3
    if not lines[j].strip().startswith("<JS_SER"):
        refuse(where, "no blob after the <JS> block")
    k = j + 1
    while lines[k].strip() != ">":
        k += 1
    raw = base64.b64decode("".join(x.strip() for x in lines[j + 1:k]))
    v = list(struct.unpack("<%df" % (len(raw) // 4), raw))
    if v[0] != 2100010.0 or (v[8], v[18]) != (5.0, 10.0):
        refuse(where, f"blob {v[0]} Breaths/min up/down {v[8]}/{v[18]}, not 2100010 5/10")
    v[8], v[18] = BABY_UP, BABY_DOWN
    b64 = base64.b64encode(struct.pack("<%df" % len(v), *v)).decode("ascii")
    ind = lines[j + 1][: len(lines[j + 1]) - len(lines[j + 1].lstrip())]
    eol = "\r\n" if lines[j + 1].endswith("\r\n") else "\n"
    new_blob = [ind + b64[x:x + 128] + eol for x in range(0, len(b64), 128)]
    if len(new_blob) != k - (j + 1):
        refuse(where, "blob line count would change")
    lines[j + 1:k] = new_blob
    lines[hi + 1] = remap_line(lines[hi + 1], where, {73: str(BABY_UP), 74: str(BABY_DOWN)})


def convert(snap_path, rel, convert_baby):
    text = open(snap_path, encoding="utf-8", errors="surrogateescape", newline="").read()
    lines = text.splitlines(keepends=True)
    n_lines, hs = len(lines), heads(lines)
    if len(hs) != 1:
        refuse(snap_path, f"{len(hs)} Womb instances, expected 1")
    if rel.endswith(BABY):
        if not convert_baby:
            return None
        baby(lines, snap_path)
    elif rel.endswith(SCATTERED):
        lines[hs[0] + 1] = carry_scattered(lines[hs[0] + 1], snap_path)
    else:
        lines[hs[0] + 1] = remap_line(lines[hs[0] + 1], snap_path)
    if len(lines) != n_lines or len(heads(lines)) != 1:
        refuse(snap_path, "line or instance count changed")
    return "".join(lines)


def main():
    apply_it = "--apply" in sys.argv
    convert_baby = "--convert-womb-and-baby" in sys.argv
    for rel, live in FILES:
        snap = f"{SNAP}/{rel}"
        want = convert(snap, rel, convert_baby)
        if want is None:
            print(f"{'HELD':13} {live}  (pass --convert-womb-and-baby once Rozaya says yes)")
            continue
        have = open(live, encoding="utf-8", errors="surrogateescape", newline="").read()
        orig = open(snap, encoding="utf-8", errors="surrogateescape", newline="").read()
        if have == want:
            state = "already done"
        elif have != orig:
            refuse(live, "changed since the snapshot")
        elif apply_it:
            open(live, "w", encoding="utf-8", errors="surrogateescape", newline="").write(want)
            state = "WRITTEN"
        else:
            state = "would write"
        print(f"{state:13} {live}")


if __name__ == "__main__":
    main()
