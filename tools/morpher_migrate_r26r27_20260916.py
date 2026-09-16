#!/usr/bin/env python3
"""Spectral Vowel Morpher, R26/R27: 64 sliders -> 79, in ONE migration.
docs/layouts/spectral-vowel-morpher-r26r27.md holds the agreed order and the build log.

BUILT IN STAGES alongside the plugin; the live projects are migrated ONCE, when every stage
is in. Until then this file only offers `convert_line`, which the stage checks use on temp
copies. Live files are never written by anything here yet.

THE MAP IS AUTHORED (the layout doc's table, and the map tools/jsfx_renumber.py applied to
src); nothing is inferred. Every new control is seeded to what reproduces the old sound.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line, render_line

N_OLD, N_NEW = 64, 79

# old id -> new id
MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 9: 8, 8: 9, 10: 10, 11: 11, 13: 12, 15: 13,
       14: 14, 16: 15, 18: 16, 17: 17, 20: 18, 19: 19, 21: 20, 12: 22, 22: 25, 23: 26, 24: 29,
       25: 34, 26: 37, 27: 38, 28: 39, 29: 40, 30: 41, 32: 42, 31: 43, 34: 44, 33: 45, 35: 46,
       36: 47, 37: 48, 38: 49, 39: 50, 40: 51, 41: 53, 42: 54, 43: 55, 44: 56, 45: 57, 46: 58,
       49: 59, 47: 60, 48: 61, 51: 62, 50: 63, 52: 65, 53: 66, 54: 67, 55: 69, 56: 70, 58: 71,
       57: 72, 59: 73, 60: 74, 61: 75, 62: 76, 63: 78, 64: 79}
assert len(MAP) == N_OLD and len(set(MAP.values())) == N_OLD


def num(tok, dflt):
    try:
        return float(tok)
    except (TypeError, ValueError):
        return dflt


def convert_line(line):
    """A 64-slider Morpher line -> the 79-slider one. Stages not yet built leave their new
    slots unset ('-'), which the plugin reads as its declared default."""
    old = parse_line(line)
    new = {}
    for o, n in MAP.items():
        new[n] = old.get(o)
    # Stage 3: Transport unit. The three times counted beats when the old Rate mode (slider 9)
    # was Every N beats (3) or N per beat (4), else seconds.
    new[52] = "2" if num(old.get(9), 1) >= 3 else "0"
    return render_line(line, new, n_sliders=N_NEW)
