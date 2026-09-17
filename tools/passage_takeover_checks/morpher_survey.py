"""What every live Morpher copy actually uses, read through the installed-equivalent Morpher (src) after
one block: the things that decide how hard carrying it into Passage is. JSON + one line per copy.

python morpher_survey.py SCRATCH OUT.json   (Idle priority)
"""
import ctypes, json, os, subprocess, sys
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
import numpy as np

ROOT = r'C:/git-src/rozaya-jsfx'
sys.path.insert(0, ROOT + '/tools')
import morpher_migrate_r26r27_20260916 as mm

J = ROOT + '/tools/jsfx_run/build/Release/jsfx_run.exe'
S, OUT = sys.argv[1], sys.argv[2]
os.makedirs(S, exist_ok=True)
src = open(ROOT + '/src/spectral_vowel_morpher.jsfx', encoding='utf-8', newline='').read()
i = src.rfind('\n@serialize')
# Targets that are PER SLOT in Passage (Morpher index): Texture 2, source fine 3, transpose 4, fine 5,
# Spread 7-8, width 9, denoise 10, low cut 11-12, high cut 13-14, overtone harmonic 15, lift 16, output 105.
probe = r'''
svk == 0 ? (
  sv_d = 0; sv_r = 0; sv_ps = 0; sv_psr = 0; sv_ramp = 0; sv_lay = 0; sv_ldt = 0;
  svi = 0; loop(N_TARGETS,
    td_active[svi] ? ( sv_d += 1; target_drift_shape[svi] == 2 ? sv_r += 1;
      (svi == 2 || (svi >= 3 && svi <= 5) || (svi >= 7 && svi <= 16) || svi == 105) ? ( sv_ps += 1; target_drift_shape[svi] == 2 ? sv_psr += 1; );
      (svi >= 18 && svi <= 104) ? sv_ldt += 1; );
    (ramp_by_mem[svi] != 0 && ramp_dur_mem[svi] > 0) ? ( sv_ramp += 1; (svi >= 18 && svi <= 104) ? sv_ldt += 1;
      (svi == 2 || (svi >= 3 && svi <= 5) || (svi >= 7 && svi <= 16) || svi == 105) ? sv_ps += 1; );
    svi += 1; );
  svi = 1; loop(15, layer_gain[svi] > 0.0001 ? sv_lay += 1; svi += 1; );
);
spl0 = svk == 0 ? n_used : svk == 1 ? slider7 : svk == 2 ? slider10 : svk == 3 ? slider5 : svk == 4 ? sv_lay :
       svk == 5 ? lay_db_base[0] : svk == 6 ? sv_d : svk == 7 ? sv_r : svk == 8 ? sv_ramp : svk == 9 ? pr_enabled :
       svk == 10 ? sv_ps : svk == 11 ? sv_psr : svk == 12 ? sv_ldt : svk == 13 ? layer_gain[0] : svk == 14 ? slider1 : 0;
spl1 = 0; svk += 1;
'''
plug = S + '/msurvey.jsfx'
open(plug, 'w', encoding='utf-8', newline='').write(src[:i] + probe + src[i:])
KEYS = ['n_used', 'automorph', 'texture', 'audition', 'layers_on', 'layer1_db', 'drifts', 'random_drifts', 'ramps',
        'play_rest', 'perslot_mods', 'perslot_random', 'layer_mods', 'layer1_gain', 'capture_slot']
res = {}
for path in mm.files():
    text = open(path, encoding='utf-8', errors='replace').read()
    n = sum(1 for l in text.split('\n') if '<JS' in l and 'spectral_vowel_morpher' in l and '<JS_SER' not in l)
    for inst in range(1, n + 1):
        csv = S + '/m.csv'
        if os.path.exists(csv):
            os.remove(csv)
        subprocess.run([J, plug, '--rpp', path, '--fx', 'spectral_vowel_morpher', '--instance', str(inst), '--seconds', '0.05',
                        '--quiet', '--csv', csv], capture_output=True)
        if not os.path.exists(csv):
            print('RENDER FAILED', path, inst, flush=True); continue
        # svk counts samples after the first block, so read the first 15 samples of the SECOND block
        t = np.loadtxt(csv, delimiter=',', skiprows=1)[:, 2]
        k0 = int(np.argmax(np.arange(len(t)) >= 0))
        d = {KEYS[j]: round(float(t[j]), 3) for j in range(len(KEYS))}
        res.setdefault(path, {})[inst] = d
        print(os.path.basename(path), inst, d, flush=True)
json.dump(res, open(OUT, 'w'), indent=1)
