"""The voice engine, sine bank (a pinned build) against wavetables (another pinned build), on real
instances migrated with convert_line. Reports each pair's difference in dB below the signal and
both builds' block times. Idle priority.

python engine_compare.py SCRATCH SINE_JSFX WT_JSFX "project.RPP:instance" ... [--seconds 8]"""
import ctypes, math, os, subprocess, sys
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np
sys.path.insert(0, r'C:/git-src/rozaya-jsfx/tools')
import passage_migrate_takeover_20260916 as mig

J = r'C:/git-src/rozaya-jsfx/tools/jsfx_run/build/Release/jsfx_run.exe'
S, SINE, WT = sys.argv[1], sys.argv[2], sys.argv[3]
args = sys.argv[4:]
secs = '8'
if '--seconds' in args:
    k = args.index('--seconds'); secs = args[k + 1]; del args[k:k + 2]
os.makedirs(S, exist_ok=True)
for spec in args:
    rpp, inst = spec.rsplit(':', 1); inst = int(inst)
    L = open(rpp, encoding='utf-8', errors='replace').read().split('\n')
    idx = [i for i, l in enumerate(L) if '<JS' in l and 'spectral_vowel_passage' in l][inst - 1] + 1
    L[idx] = mig.convert_line(L[idx])
    tag = os.path.basename(rpp)[:-4].replace(' ', '_') + f'_{inst}'
    new = f'{S}/{tag}.RPP'
    open(new, 'w', encoding='utf-8', newline='').write('\n'.join(L))
    out = {}
    for name, plug in (('sine', SINE), ('wt', WT)):
        r = subprocess.run([J, plug, '--rpp', new, '--fx', 'spectral_vowel_passage', '--instance', str(inst),
                            '--seconds', secs, '--csv', f'{S}/{tag}_{name}.csv', '--block-times', f'{S}/{tag}_{name}.times'],
                           capture_output=True, text=True)
        bt = [l for l in (r.stdout + r.stderr).splitlines() if 'block times' in l]
        out[name] = (np.loadtxt(f'{S}/{tag}_{name}.csv', delimiter=',', skiprows=1)[:, 2:], bt[0] if bt else r.stderr[-300:])
    a, b = out['sine'][0], out['wt'][0]
    d = a - b; ra = math.sqrt((a ** 2).mean()); rd = math.sqrt((d ** 2).mean())
    print(f"{tag}: signal rms {ra:.4f}, difference {20 * math.log10(rd / ra + 1e-30) if ra > 0 else 0:.1f} dB below it, "
          f"largest single-sample difference {np.abs(d).max():.6f} (peak {np.abs(a).max():.4f})", flush=True)
    print(f"   sine: {out['sine'][1]}\n   wt:   {out['wt'][1]}", flush=True)
