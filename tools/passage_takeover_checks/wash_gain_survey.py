"""How much the grain auto-gain boosts each captured slot of every live Passage copy, measured through
the ORIGINAL plugin (48e3771): each slot auditioned alone (Focused slot) until the smoother settles,
then 0.07 / rms_smooth, in dB. Writes JSON {project: {instance: {slot: {boost_db, texture}}}}.

python wash_gain_survey.py SCRATCH OUT.json [ONE.RPP]     (Idle priority; every live file, or one)
"""
import ctypes, glob, json, math, os, subprocess, sys
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np

ROOT = r'C:/git-src/rozaya-jsfx'
J = ROOT + '/tools/jsfx_run/build/Release/jsfx_run.exe'
S, OUT = sys.argv[1], sys.argv[2]
os.makedirs(S, exist_ok=True)
src = subprocess.run(['git', '-C', ROOT, 'show', '48e3771:src/spectral_vowel_passage.jsfx'], capture_output=True).stdout.decode()
src = src.replace('_tp = time_precise();', '_tp = 0.25;')
i = src.rfind('\n@serialize')
# Probe: the smoother, how many slots are captured, and the auditioned slot's own Texture.
src = src[:i] + '\nspl0 = rms_smooth; spl1 = n_used * 10 + slot_texture[cap_slot];\n' + src[i:]
plug = S + '/probe.jsfx'
open(plug, 'w', encoding='utf-8', newline='').write(src)

res = {}
# Results already measured (a resumed run): {file: {instance: slots}} from an earlier OUT.
if os.path.exists(OUT):
    res = json.load(open(OUT))
# A second probe reads every slot's Texture and the captured count in its first ten samples,
# so a slot with no wash (Texture 0) is never rendered for six seconds.
tex_src = src.replace('\nspl0 = rms_smooth; spl1 = n_used * 10 + slot_texture[cap_slot];\n',
                      '\ntxi = min(txi, 8); spl0 = txi < 8 ? slot_texture[txi] : n_used; spl1 = 0; txi += 1;\n')
assert tex_src != src
tex_plug = S + '/tex.jsfx'
open(tex_plug, 'w', encoding='utf-8', newline='').write(tex_src)
sys.path.insert(0, ROOT + '/tools')
import passage_migrate_takeover_20260916 as mig
for rpp in (sys.argv[3:] or mig.files()):
    text = open(rpp, encoding='utf-8', errors='replace').read()
    n = sum(1 for l in text.split('\n') if '<JS' in l and 'spectral_vowel_passage' in l)
    key = os.path.basename(rpp)
    for inst in range(1, n + 1):
        if str(inst) in res.get(key, {}):
            continue
        csv = f'{S}/t.csv'
        subprocess.run([J, tex_plug, '--rpp', rpp, '--fx', 'spectral_vowel_passage', '--instance', str(inst), '--seconds', '0.01',
                        '--quiet', '--csv', csv], capture_output=True)
        t = np.loadtxt(csv, delimiter=',', skiprows=1)[:, 2]
        n_used = int(round(t[8]))
        slots = {}
        for s_ in range(n_used):
            tex = float(t[s_])
            if tex <= 0.0001:
                slots[str(s_ + 1)] = {'boost_db': None, 'texture': round(tex, 3)}
                continue
            csv = f'{S}/p.csv'
            subprocess.run([J, plug, '--rpp', rpp, '--fx', 'spectral_vowel_passage', '--instance', str(inst), '--seconds', '6',
                            '--quiet', '--csv', csv, '--set-after', '5=0', '--set-after', f'1={s_ + 1}'], capture_output=True)
            x = np.loadtxt(csv, delimiter=',', skiprows=1)
            rs = x[-1, 2]
            slots[str(s_ + 1)] = {'boost_db': round(20 * math.log10(0.07 / rs), 2) if rs > 1e-9 else None, 'texture': round(tex, 3)}
        res.setdefault(key, {})[str(inst)] = slots
        print(key, inst, slots, flush=True)
        json.dump(res, open(OUT, 'w'), indent=1)
json.dump(res, open(OUT, 'w'), indent=1)
