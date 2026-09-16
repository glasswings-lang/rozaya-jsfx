"""The wavetable voice against the sine bank in the cases that force table REBUILDS -- the cases the
first engine check (nightfall as saved) never reached, which is how a stuck rebuild shipped into
stage 5 unseen. Sine = f1b2df4 (stage 4); wavetable = the working copy. Layers off throughout.

  focus   Audition on Focused slot, the Capture slot stepped every second: both voices change slot
          with no handover, so every step is a rebuild.
  ot      Overtone harmonic 5 on All slots with a Sine drift of +-3 harmonics every 2 s: the curve
          moves continuously, so tables rebuild as fast as they are allowed.
  hicut   High cut 1500 Hz on All slots and a +-5 semitone Sine drift on Transpose every 3 s: partials
          cross the cut's fade, rebuilding on pitch.
python engine_stress.py SCRATCH
"""
import ctypes, math, os, subprocess, sys
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np
sys.path.insert(0, r'C:/git-src/rozaya-jsfx/tools')
import passage_migrate_takeover_20260916 as mig

ROOT = r'C:/git-src/rozaya-jsfx'
J = ROOT + '/tools/jsfx_run/build/Release/jsfx_run.exe'
S = sys.argv[1]; os.makedirs(S + '/sine', exist_ok=True); os.makedirs(S + '/wt', exist_ok=True)
sine = subprocess.run(['git', '-C', ROOT, 'show', 'f1b2df4:src/spectral_vowel_passage.jsfx'], capture_output=True).stdout.decode()
wt = open(ROOT + '/src/spectral_vowel_passage.jsfx', encoding='utf-8', newline='').read()
for t, d in ((sine, 'sine'), (wt, 'wt')):
    open(f'{S}/{d}/spectral_vowel_passage.jsfx', 'w', encoding='utf-8', newline='').write(t.replace('_tp = time_precise();', '_tp = 0.25;'))
L = open('E:/reaper/finished/nightfall.RPP', encoding='utf-8', errors='replace').read().split('\n')
idx = [i for i, l in enumerate(L) if '<JS' in l and 'spectral_vowel_passage' in l][0] + 1
L[idx] = mig.convert_line(L[idx])
rpp = f'{S}/nightfall_1.RPP'; open(rpp, 'w', encoding='utf-8', newline='').write('\n'.join(L))

BLOCKS_PER_S = 44100 // 512


def at(seconds_list):
    """--set-after groups landing at roughly these times (one group per --stage, a block apart)."""
    out, blk = [], 0
    for sec, sets in seconds_list:
        target = int(sec * BLOCKS_PER_S)
        while blk < target:
            out.append('--stage'); blk += 1
        for k, v in sets:
            out += ['--set-after', f'{k}={v}']
    return out


CASES = {
    'focus': at([(0, [(5, 0)])] + [(1 + i, [(1, 1 + (i * 3) % 8)]) for i in range(9)]),
    'ot': at([(0, [(1, 0)]), (0.05, [(47, 5)]), (0.1, [(68, 8)]), (0.15, [(70, 3), (71, 3), (73, 2)])]),
    'hicut': at([(0, [(1, 0)]), (0.05, [(44, 1500)]), (0.1, [(68, 0)]), (0.15, [(70, 5), (71, 5), (73, 3)])]),
}
for name, args in CASES.items():
    res = {}
    for eng in ('sine', 'wt'):
        r = subprocess.run([J, f'{S}/{eng}/spectral_vowel_passage.jsfx', '--rpp', rpp, '--fx', 'spectral_vowel_passage',
                            '--seconds', '10', '--quiet', '--csv', f'{S}/{name}_{eng}.csv', *args], capture_output=True, text=True)
        res[eng] = np.loadtxt(f'{S}/{name}_{eng}.csv', delimiter=',', skiprows=1)[:, 2:]
    a, b = res['sine'], res['wt']; d = a - b
    ra = math.sqrt((a ** 2).mean()); rd = math.sqrt((d ** 2).mean())
    worst = max(math.sqrt((d[i:i + 4410] ** 2).mean()) / max(1e-9, math.sqrt((a[i:i + 4410] ** 2).mean())) for i in range(0, len(a) - 4410, 4410))
    print(f"{name}: signal rms {ra:.4f}; difference {20 * math.log10(rd / ra + 1e-30):.1f} dB below it overall, "
          f"{20 * math.log10(worst + 1e-30):.1f} dB in the worst 100 ms; sine peak {abs(a).max():.3f}, wavetable peak {abs(b).max():.3f}", flush=True)
