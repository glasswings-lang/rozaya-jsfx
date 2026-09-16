"""Stages 1-8 against the pre-build Passage: every live instance as saved, then cuts and Spread set.
python stage4.py SCRATCH_DIR   (runs at Idle priority; prints one line per render pair)"""
import ctypes, glob, sys
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
from stage_check import *

for R in sorted(glob.glob('E:/reaper/finished/*.RPP')):
    if 'spectral_vowel_passage' not in open(R, encoding='utf-8', errors='replace').read():
        continue
    for k in range(1, count(R) + 1):
        tag = os.path.basename(R).replace(' ', '_')[:-4] + f'_{k}'
        same(tag, *make(R, k, {}, tag))
R = 'E:/reaper/finished/rain-sound.RPP'
# old ids: 15 Spread, 17 Low cut, 18 High cut, 39 Play for, 40 Rest for
same('rest', *make(R, 1, {39: 1.5, 40: 1.0}, 'rest'))
same('cuts', *make(R, 1, {17: 150, 18: 3000}, 'cuts'))
same('spread', *make(R, 1, {15: 120}, 'spread'))
