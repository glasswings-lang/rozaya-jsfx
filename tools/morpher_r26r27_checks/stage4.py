import sys; sys.path.insert(0, sys.argv[1]); from stage_check import *
R = 'E:/reaper/finished/breathing.RPP'
same('s4_plain', *make(R, 1, {}, 's4_plain'))
same('s4_rest', *make(R, 1, {42: 1.5, 43: 1.0}, 's4_rest'))
