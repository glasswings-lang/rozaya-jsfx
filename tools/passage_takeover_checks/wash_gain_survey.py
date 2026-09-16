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
sys.path.insert(0, ROOT + '/tools')
import passage_migrate_takeover_20260916 as mig
for rpp in (sys.argv[3:] or mig.files()):
    text = open(rpp, encoding='utf-8', errors='replace').read()
    n = sum(1 for l in text.split('\n') if '<JS' in l and 'spectral_vowel_passage' in l)
    for inst in range(1, n + 1):
        slots = {}
        s = 0
        while s < 8:
            csv = f'{S}/p.csv'
            subprocess.run([J, plug, '--rpp', rpp, '--fx', 'spectral_vowel_passage', '--instance', str(inst), '--seconds', '6',
                            '--quiet', '--csv', csv, '--set-after', '5=0', '--set-after', f'1={s + 1}'], capture_output=True)
            x = np.loadtxt(csv, delimiter=',', skiprows=1)
            rs, info = x[-1, 2], x[-1, 3]
            n_used = int(info // 10); tex = info - n_used * 10
            if tex > 0.0001 and rs > 1e-9:
                slots[s + 1] = {'boost_db': round(20 * math.log10(0.07 / rs), 2), 'texture': round(float(tex), 3)}
            else:
                slots[s + 1] = {'boost_db': None, 'texture': round(float(tex), 3)}
            s += 1
            if s >= n_used:
                break
        key = os.path.basename(rpp)
        res.setdefault(key, {})[inst] = slots
        print(key, inst, slots, flush=True)
json.dump(res, open(OUT, 'w'), indent=1)
