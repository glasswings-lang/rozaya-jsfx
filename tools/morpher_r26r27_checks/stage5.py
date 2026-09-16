import sys; sys.path.insert(0, sys.argv[1]); from stage_check import *
R = 'E:/reaper/finished/breathing.RPP'
B = 'E:/reaper/finished/test-projects/claude-testing002-bridge.RPP'
same('s5_breathing', *make(R, 1, {}, 's5_breathing'))
same('s5_breathing_rest', *make(R, 1, {42: 1.5, 43: 1.0}, 's5_breathing_rest'))
same('s5_bridge', *make(B, 1, {}, 's5_bridge'))
same('s5_bridge_rest', *make(B, 1, {42: 0.9, 43: 0.6}, 's5_bridge_rest'))
