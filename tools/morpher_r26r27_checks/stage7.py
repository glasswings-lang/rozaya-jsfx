import sys; sys.path.insert(0, sys.argv[1]); from stage_check import *
R = 'E:/reaper/finished/breathing.RPP'
B = 'E:/reaper/finished/test-projects/claude-testing002-bridge.RPP'
same('s7_breathing', *make(R, 1, {}, 's7_breathing'))
same('s7_bridge', *make(B, 1, {}, 's7_bridge'))
same('s7_cuts_hz', *make(R, 1, {24: 150, 25: 3000}, 's7_cuts_hz'))
same('s7_cuts_hz_rest', *make(B, 1, {24: 90, 25: 5000, 42: 0.9, 43: 0.6}, 's7_cuts_hz_rest'))
