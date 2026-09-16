"""Old pinned Passage (pre-build) on a project line vs new pinned Passage on convert_line(line).
Usage from a stage script: make(rpp, instance, {old_slider_id: value}, tag) -> same(tag, ...).
Pins: time_precise() -> 0.25 in both, so the RNG draws the same."""
import sys, os, subprocess
sys.path.insert(0, r'C:/git-src/rozaya-jsfx/tools')
from rpp_sliders import parse_line, render_line
import importlib; mig = importlib.import_module('passage_migrate_takeover_20260916')
S = sys.argv[1]; J = r'C:/git-src/rozaya-jsfx/tools/jsfx_run/build/Release/jsfx_run.exe'
OLD = S + '/pin/old/spectral_vowel_passage.jsfx'; NEW = S + '/pin/new/spectral_vowel_passage.jsfx'
def pin():
    os.makedirs(S + '/pin/old', exist_ok=True); os.makedirs(S + '/pin/new', exist_ok=True)
    old = subprocess.run(['git', '-C', r'C:/git-src/rozaya-jsfx', 'show', '48e3771:src/spectral_vowel_passage.jsfx'],
                         capture_output=True).stdout.decode('utf-8')
    new = open(r'C:/git-src/rozaya-jsfx/src/spectral_vowel_passage.jsfx', encoding='utf-8', newline='').read()
    for t, p in ((old, OLD), (new, NEW)):
        assert t.count('_tp = time_precise();') == 1
        open(p, 'w', encoding='utf-8', newline='').write(t.replace('_tp = time_precise();', '_tp = 0.25;'))
pin()
def make(src_rpp, inst, edits, tag):
    L = open(src_rpp, encoding='utf-8', errors='replace').read().split('\n')
    idx = [i for i, l in enumerate(L) if '<JS' in l and 'spectral_vowel_passage' in l][inst - 1] + 1
    d = parse_line(L[idx]); d.update({k: str(v) for k, v in edits.items()})
    L[idx] = render_line(L[idx], d, n_sliders=63)
    o = f'{S}/{tag}_old.RPP'; open(o, 'w', encoding='utf-8', newline='').write('\n'.join(L))
    L[idx] = mig.convert_line(L[idx])
    n = f'{S}/{tag}_new.RPP'; open(n, 'w', encoding='utf-8', newline='').write('\n'.join(L))
    return o, n, inst
def render(plug, rpp, inst, out, extra=()):
    r = subprocess.run([J, plug, '--rpp', rpp, '--fx', 'spectral_vowel_passage', '--instance', str(inst),
                        '--seconds', '8', '--csv', out, '--quiet', *extra], capture_output=True)
    if r.returncode: print(r.stderr.decode()[-400:])
def same(tag, o, n, inst, extra=()):
    render(OLD, o, inst, f'{S}/{tag}_o.csv', extra); render(NEW, n, inst, f'{S}/{tag}_n.csv', extra)
    import numpy as np
    a = open(f'{S}/{tag}_o.csv', 'rb').read(); b = open(f'{S}/{tag}_n.csv', 'rb').read()
    x = np.loadtxt(f'{S}/{tag}_n.csv', delimiter=',', skiprows=1, usecols=(2,))
    print(f"{'PASS' if a == b and len(a) > 100 else 'FAIL'} {tag}: old vs new {'bit-identical' if a == b else 'DIFFERENT'} (sounding: {np.abs(x).max() > 0}, peak {np.abs(x).max():.4f})", flush=True)
    return a == b
def count(rpp):
    return sum(1 for l in open(rpp, encoding='utf-8', errors='replace') if '<JS' in l and 'spectral_vowel_passage' in l)
