import sys; sys.path.insert(0, sys.argv[1]); from stage_check import *
R = 'E:/reaper/finished/breathing.RPP'
# as saved
same('s3_plain', *make(R, 1, {}, 's3_plain'))
# play/rest and start delay in seconds
same('s3_sec', *make(R, 1, {41: 0.7, 42: 1.5, 43: 0.8}, 's3_sec'))
# the same under Every N beats (old rate mode 3, auto-morph time 8 beats)
same('s3_beats', *make(R, 1, {9: 3, 8: 8, 41: 1, 42: 3, 43: 2}, 's3_beats'), extra=('--tempo', '97'))
