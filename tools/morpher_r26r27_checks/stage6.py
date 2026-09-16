import sys; sys.path.insert(0, sys.argv[1]); from stage_check import *
R = 'E:/reaper/finished/breathing.RPP'
B = 'E:/reaper/finished/test-projects/claude-testing002-bridge.RPP'
same('s6_breathing', *make(R, 1, {}, 's6_breathing'))
same('s6_breathing_spread150', *make(R, 1, {12: 150}, 's6_breathing_spread150'))
same('s6_bridge', *make(B, 1, {}, 's6_bridge'))
