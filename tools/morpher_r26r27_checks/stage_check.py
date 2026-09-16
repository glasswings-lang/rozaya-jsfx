"""Old pinned Morpher on a project line (edited) vs new pinned Morpher on convert_line(line)."""
import sys, os, subprocess, filecmp
sys.path.insert(0, r'C:/git-src/rozaya-jsfx/tools')
from rpp_sliders import parse_line, render_line
import importlib; mig = importlib.import_module('morpher_migrate_r26r27_20260916')
S = sys.argv[1]; J = r'C:/git-src/rozaya-jsfx/tools/jsfx_run/build/Release/jsfx_run.exe'
OLD = S + '/pin/old/spectral_vowel_morpher.jsfx'; NEW = S + '/pin/new/spectral_vowel_morpher.jsfx'
def make(src_rpp, inst, edits, tag):
    L = open(src_rpp, encoding='utf-8', errors='replace').read().split('\n')
    idx = [i for i, l in enumerate(L) if '<JS' in l and 'spectral_vowel_morpher' in l][inst - 1] + 1
    d = parse_line(L[idx]); d.update({k: str(v) for k, v in edits.items()})
    L[idx] = render_line(L[idx], d, n_sliders=64)
    o = f'{S}/{tag}_old.RPP'; open(o, 'w', encoding='utf-8', newline='').write('\n'.join(L))
    L[idx] = mig.convert_line(L[idx])
    n = f'{S}/{tag}_new.RPP'; open(n, 'w', encoding='utf-8', newline='').write('\n'.join(L))
    return o, n, inst
def render(plug, rpp, inst, out, extra=()):
    subprocess.run([J, plug, '--rpp', rpp, '--fx', 'spectral_vowel_morpher', '--instance', str(inst),
                    '--seconds', '8', '--csv', out, '--quiet', *extra], capture_output=True)
def same(tag, o, n, inst, extra=()):
    render(OLD, o, inst, f'{S}/{tag}_o.csv', extra); render(NEW, n, inst, f'{S}/{tag}_n.csv', extra)
    import numpy as np
    a = open(f'{S}/{tag}_o.csv', 'rb').read(); b = open(f'{S}/{tag}_n.csv', 'rb').read()
    x = np.loadtxt(f'{S}/{tag}_n.csv', delimiter=',', skiprows=1, usecols=(2,))
    print(f"{'PASS' if a == b else 'FAIL'} {tag}: old vs new {'bit-identical' if a == b else 'DIFFERENT'} (sounding: {np.abs(x).max() > 0})", flush=True)
    return a == b
