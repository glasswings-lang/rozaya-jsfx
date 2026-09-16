#!/usr/bin/env python3
"""Spectral Vowel Passage takes over from the Morpher: 63 sliders -> 89, in ONE migration.
docs/layouts/spectral-vowel-passage-takeover.md holds the agreed order and the build log.

BUILT IN STAGES alongside the plugin; live projects are migrated ONCE, when every stage is
in. Until then this file only offers `convert_line`, which the stage checks use on temp
copies. THE MAP IS AUTHORED (the layout doc); nothing is inferred. Every new control is
seeded to what reproduces the old sound.
"""
import math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line, render_line

N_OLD, N_NEW = 63, 89

MAP_TEXT = ("1-4:+0, 36:5, 34:6, 35:7, 25:11, 21:12, 22:13, 23:14, 24:15, 31:16, 32:17, 26:18, "
            "27:19, 13:20, 14:21, 5:22, 7:23, 6:24, 8:25, 10:26, 9:27, 12:28, 11:29, 30:30, 15:32, "
            "28:35, 16:36, 17:39, 18:44, 19:47, 20:48, 33:49, 37:60, 29:61, 41:62, 38:63, 39:64, "
            "40:65, 42:66, 43:67, 44:68, 47:69, 45:70, 46:71, 49:72, 48:73, 50:74, 51:75, 52:76, "
            "53:77, 54:79, 55:80, 57:81, 56:82, 58:83, 59:84, 60:85, 61:86, 62:88, 63:89")

def _map():
    m = {}
    for part in [p.strip() for p in MAP_TEXT.split(",")]:
        a, b = part.split(":")
        if "-" in a:
            lo, hi = map(int, a.split("-"))
            for i in range(lo, hi + 1):
                m[i] = i + int(b)
        else:
            m[int(a)] = int(b)
    return m
MAP = _map()
assert len(MAP) == N_OLD and len(set(MAP.values())) == N_OLD and set(MAP) == set(range(1, 64))


def num(tok, dflt):
    try:
        return float(tok)
    except (TypeError, ValueError):
        return dflt


def cut_note(hz, ref):
    """The plugin's cut_note in Hz mode: 0 Off, else 1 + the nearest note number."""
    if hz <= 0:
        return 0
    m = 69 + 12 * math.log(max(hz, 0.000001) / max(ref, 0.001)) / math.log(2)
    return 1 + max(0, min(127, math.floor(m + 0.5)))


def convert_line(line):
    """One Passage slider line, old numbering -> new. Stages add their seeds here."""
    old = parse_line(line)
    new = {MAP[i]: old.get(i) for i in range(1, N_OLD + 1)}
    # Stage 4: High cut's off was 20000 and is 0; the note names follow the values, in Hz.
    # The pitch modes and fine tunes stay unset: the plugin's defaults are Hz and 0.
    ref = num(old.get(30), 440)
    ref = ref if ref >= 20 else 440
    if old.get(18) is not None and num(old.get(18), 20000) >= 19999.5:
        new[44] = "0"
    if new.get(39) is not None:
        new[38] = str(cut_note(num(new[39], 0), ref))
    if new.get(44) is not None:
        new[43] = str(cut_note(num(new[44], 0), ref))
    return render_line(line, new, n_sliders=N_NEW)


if __name__ == "__main__":
    sys.exit("stage build: nothing to apply yet")
