import sys; sys.path.insert(0, sys.argv[1] if len(sys.argv) > 2 else '.'); 
from stage_check import *
import glob
# Every live instance as saved, then one with a transport rest (old ids 39 Play for, 40 Rest for).
for R in sorted(glob.glob('E:/reaper/finished/*.RPP')):
    if 'spectral_vowel_passage' not in open(R, encoding='utf-8', errors='replace').read(): continue
    for k in range(1, count(R) + 1):
        tag = os.path.basename(R).replace(' ', '_')[:-4] + f'_{k}'
        same(tag, *make(R, k, {}, tag))
R = 'E:/reaper/finished/rain-sound.RPP'
same('rest', *make(R, 1, {39: 1.5, 40: 1.0}, 'rest'))
