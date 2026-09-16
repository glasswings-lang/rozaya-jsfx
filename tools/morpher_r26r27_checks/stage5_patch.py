import re
p='src/spectral_vowel_morpher.jsfx'
s=open(p,encoding='utf-8',newline='').read(); nl='\r\n' if '\r\n' in s else '\n'; s=s.replace('\r\n','\n')
ERR=[]
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: ERR.append((a[:70],c,n)); return
    s=s.replace(a,b)
names=['Morph','Auto-morph rate','Texture','Pitch source fine tune','Pitch transpose','Pitch fine tune','Tuning reference',
 'Spread','Spread fine tune','Stereo width','Denoise','Low cut','Low cut fine tune','High cut','High cut fine tune',
 'Overtone harmonic','Overtone lift','Overtone width']
for grp in ['pitch','fine tune','level','harmonics','overtone harmonic']:
    names.append(f'Layer {grp} (all layers)'); names += [f'Layer {k} {grp}' for k in range(1,17)]
names += ['Input level','Output level','Play for','Rest for']
assert len(names)==107
enum='{'+','.join(names)+'}'
for sl,tail in [(58,'Drift target'),(70,'Ramp target')]:
    s,c=re.subn(r'(?m)^slider%d:0<0,86,1\{[^}]*\}>%s$'%(sl,tail), lambda m: 'slider%d:0<0,106,1%s>%s'%(sl,enum,tail), s); assert c==1,sl
# constants
rep("N_TARGETS = 87;","N_TARGETS = 107;")
rep("LP_T0  = 16;","""// 107 since 2026-09-16 (R26/R27, docs/layouts/spectral-vowel-morpher-r26r27.md): 0 Morph,
//   1 Auto-morph rate, 2 Texture, 3 Pitch source fine tune, 4 Pitch transpose, 5 Pitch fine
//   tune, 6 Tuning reference, 7 Spread, 8 Spread fine tune, 9 Stereo width, 10 Denoise, 11 Low
//   cut, 12 its fine tune, 13 High cut, 14 its fine tune, 15-17 Overtone harmonic/lift/width,
//   18 Layer pitch (all), 35 fine tune (all), 52 level (all), 69 harmonics (all), 86 overtone
//   harmonic (all), each followed by its sixteen; 103 Input level, 104 Output level, 105 Play
//   for, 106 Rest for. Wash grain left the list. The 87-list offsets are kept as O87_*.
O87_LP_T0 = 16; O87_LEV_T0 = 50; O87_LOT_T0 = 67;
LP_T0  = 19;""")
rep("LF_T0  = 33;","LF_T0  = 36;")
rep("\nLEV_T0 = 50;","\nLEV_T0 = 53;\nLH_T0  = 70;     // Layer k's harmonics target (2026-09-16)")
rep("\nLOT_T0 = 67;","\nLOT_T0 = 87;")
rep("function mo_is_all(t) ( t == 15 || t == 32 || t == 49 || t == 66; );","function mo_is_all(t) ( t == 18 || t == 35 || t == 52 || t == 69 || t == 86; );")
rep("o <= 5 ? o : o <= 12 ? o + 2 : o == 13 ? 49 : o <= 29 ? LEV_T0 + lay_ladinv[o - 14] :\n  o == 30 ? 15 : o <= 33 ? LP_T0 + 13 + (o - 31) : o == 34 ? 66 : o <= 50 ? LOT_T0 + lay_ladinv[o - 35] :",
    "o <= 5 ? o : o <= 12 ? o + 2 : o == 13 ? 49 : o <= 29 ? O87_LEV_T0 + lay_ladinv[o - 14] :\n  o == 30 ? 15 : o <= 33 ? O87_LP_T0 + 13 + (o - 31) : o == 34 ? 66 : o <= 50 ? O87_LOT_T0 + lay_ladinv[o - 35] :")
rep("function mo_remap(bank, dflt) local(mr_k) (","""// An 87-target save's index (2026-09-13), in the 107 list; -1 for Wash grain, which left it.
function t107_o2n(o) (
  o <= 2 ? o : o == 3 ? -1 : o == 4 ? 7 : o <= 7 ? o - 1 : o <= 10 ? o + 1 : o == 11 ? 13 :
  o <= 65 ? o + 3 : o + 20;
);
function t107_remap(bank, dflt) local(tq_k, tq_n) (
  tq_k = 0; loop(87, tg_scratch[tq_k] = bank[tq_k]; tq_k += 1;);
  tq_k = 0; loop(N_TARGETS, bank[tq_k] = dflt; tq_k += 1;);
  tq_k = 0; loop(87, tq_n = t107_o2n(tq_k); tq_n >= 0 ? bank[tq_n] = tg_scratch[tq_k]; tq_k += 1;);
);
function mo_remap(bank, dflt) local(mr_k) (""")
rep("""mo_i = 0;
loop(N_TARGETS,
  mo_old = 0; mo_j = 0; loop(55, t55_o2n(mo_j) == mo_i ? mo_old = 1; mo_j += 1;);
  !mo_old ? ( mo_order[mo_k] = mo_i; mo_k += 1; );
  mo_i += 1;
);""","""mo_i = 0;
loop(87,
  mo_old = 0; mo_j = 0; loop(55, t55_o2n(mo_j) == mo_i ? mo_old = 1; mo_j += 1;);
  !mo_old ? ( mo_order[mo_k] = mo_i; mo_k += 1; );
  mo_i += 1;
);
// 2026-09-16: that 87-list order carried into the 107 list (Wash grain dropped), then the
// twenty-one new targets in index order -- so every drift that existed draws rand() as before.
mo_k = 0; loop(87, tg_scratch[mo_k] = mo_order[mo_k]; mo_k += 1;);
mo_n = 0; mo_k = 0;
loop(87, mo_i = t107_o2n(tg_scratch[mo_k]); mo_i >= 0 ? ( mo_order[mo_n] = mo_i; mo_n += 1; ); mo_k += 1;);
mo_i = 0;
loop(N_TARGETS,
  mo_old = 0; mo_j = 0; loop(87, t107_o2n(mo_j) == mo_i ? mo_old = 1; mo_j += 1;);
  !mo_old ? ( mo_order[mo_n] = mo_i; mo_n += 1; );
  mo_i += 1;
);""")
rep("ramp_by_unit      = freemem; freemem += 128;\n","""ramp_by_unit      = freemem; freemem += 128;
// Per target since 2026-09-16 (R26): Drift period unit, Ramp time unit, Drift movement mode.
target_drift_punit = freemem; freemem += 128;   // {0 Cycles, 1 Seconds, 2 Beats}
ramp_tunit         = freemem; freemem += 128;   // {0 Cycles, 1 Seconds, 2 Minutes, 3 Beats}
drift_moves        = freemem; freemem += 128;   // {0 With the target, 1 On a clock}
lay_nh_eff         = freemem; freemem += 32;    // each layer's harmonics with drift and ramp
""")
rep("    target_drift_unit[i]  = 0;   // Target default: today's meaning\n","    target_drift_unit[i]  = 0;   // Target default: today's meaning\n    target_drift_punit[i] = 1;   // Seconds, the slider's own default\n    ramp_tunit[i]         = 2;   // Minutes, likewise\n    drift_moves[i]        = 0;   // With the target\n")
rep(">Drift period unit (all targets)\n",">Drift period unit\n")
rep(">Ramp time unit (all targets)\n",">Ramp time unit\n")
rep("slider63:30<0,1000,0.001>Drift period (in drift period units, 0 = off)\n","""slider63:30<0,1000,0.001>Drift period (in drift period units, 0 = off)
// R23, 2026-09-16. Play for and Rest for are read once per stretch: With the target, a stretch
// keeps the length it began with; On a clock, a drift can end the one being heard. They are
// the only such targets here (each wash grain is written whole), so it shows only for them.
slider64:0<0,1,1{With the target,On a clock}>Drift movement mode
""")
rep("    slider63 = target_drift_per[dts];\n    slider65 = target_drift_shape[dts];\n",
    "    slider63 = target_drift_per[dts];\n    slider62 = target_drift_punit[dts];\n    slider64 = drift_moves[dts];\n    slider65 = target_drift_shape[dts];\n", 2)
rep("    slider_automate(slider63);\n    slider_automate(slider65);\n","    slider_automate(slider62);\n    slider_automate(slider63);\n    slider_automate(slider64);\n    slider_automate(slider65);\n")
rep("    dui_last[11] = slider59;\n    last_target_select = sel_target;\n","    dui_last[11] = slider59; dui_last[13] = slider62; dui_last[15] = slider64;\n    last_target_select = sel_target;\n")
rep("    mo_capture(sel_target, target_drift_unit,  slider59, 11);\n","    mo_capture(sel_target, target_drift_unit,  slider59, 11);\n    mo_capture(sel_target, target_drift_punit, slider62, 13);\n    mo_capture(sel_target, drift_moves,        slider64, 15);\n")
rep("    slider74 = ramp_dur_mem[rts];\n","    slider73 = ramp_tunit[rts];\n    slider74 = ramp_dur_mem[rts];\n", 2)
rep("    slider_automate(slider74);\n    slider_automate(slider79);\n","    slider_automate(slider73);\n    slider_automate(slider74);\n    slider_automate(slider79);\n")
rep("    dui_last[12] = slider71;\n    last_ramp_target = rsel_target;\n","    dui_last[12] = slider71; dui_last[14] = slider73;\n    last_ramp_target = rsel_target;\n")
rep("    mo_capture(rsel_target, ramp_by_unit,   slider71, 12);\n","    mo_capture(rsel_target, ramp_by_unit,   slider71, 12);\n    mo_capture(rsel_target, ramp_tunit,     slider73, 14);\n")
rep("ramp_engaged = slider78;\n","ramp_engaged = slider78;\n// Drift movement mode means something only for Play for (105) and Rest for (106).\nslider_show(slider64, slider58 >= 105);\n")
rep("  dui_last[11] = slider59; dui_last[12] = slider71;\n  drift_ui_inited = 1;","  dui_last[11] = slider59; dui_last[12] = slider71;\n  dui_last[13] = slider62; dui_last[14] = slider73; dui_last[15] = slider64;\n  drift_ui_inited = 1;")
rep("""drift_unit_sec  = slider62 == 0 ? auto_time :
                  slider62 == 1 ? 1 :
                                  60 / max(tempo, 0.001);
ramp_unit_sec   = slider73 == 0 ? auto_time :
                  slider73 == 1 ? 1 :
                  slider73 == 2 ? 60 :
                                  60 / max(tempo, 0.001);
// Drift period is a SECONDS value everywhere it is consumed. It used to follow
// Rate Mode; it follows its own unit control now.
drift_per_k     = drift_unit_sec;""","""// Per target since 2026-09-16: each target's own unit (target_drift_punit, ramp_tunit) picks
// its factor in the loops below, with exactly these expressions.""")
rep("function au_back(nu, tt)","""function mo_dunit_sec(u) ( u == 0 ? auto_time : u == 1 ? 1 : 60 / max(tempo, 0.001); );
function mo_runit_sec(u) ( u == 0 ? auto_time : u == 1 ? 1 : u == 2 ? 60 : 60 / max(tempo, 0.001); );
function au_back(nu, tt)""")
rep("    dper = target_drift_per[di] * drift_per_k;","    dper = target_drift_per[di] * mo_dunit_sec(target_drift_punit[di]);")
rep("    ramp_dur_mem[ri] > 0 ? (\n      rdelay_samps = ramp_delay_mem[ri] * ramp_unit_sec * srate;",
    "    ramp_dur_mem[ri] > 0 ? (\n      ramp_unit_sec = mo_runit_sec(ramp_tunit[ri]);\n      rdelay_samps = ramp_delay_mem[ri] * ramp_unit_sec * srate;")
rep("pr_play_sec     = mo_tsec(slider52, mod_active[85] ? max(0.001, slider54 + au_key(85, 3, slider54, slider52)) : slider54);\npr_rest_sec     = mo_tsec(slider52, mod_active[86] ? max(0.001, slider55 + au_key(86, 3, slider55, slider52)) : slider55);",
    "pr_play_sec     = mo_tsec(slider52, mod_active[105] ? max(0.001, slider54 + au_key(105, 3, slider54, slider52)) : slider54);\npr_rest_sec     = mo_tsec(slider52, mod_active[106] ? max(0.001, slider55 + au_key(106, 3, slider55, slider52)) : slider55);")
rep("eff_grain_ms = mod_active[3] ? max(5, min(1000, grain_ms + au_key(3, 3, grain_ms, 3))) : grain_ms;",
    "// Not a Drift or Ramp target since 2026-09-16: a fast grain drift made the wash wobble in\n// loudness whatever the timing, and no saved copy drove it.\neff_grain_ms = grain_ms;")
rep("mod_active[4] ? au_key(4, 2, spread_hz, srate / FFTSIZE) : 0","mod_active[7] ? au_key(7, 2, spread_hz, srate / FFTSIZE) : 0")
rep("tuning_ref = mod_active[7] ? max(20, min(2000, tuning_base + au_key(7, 2, tuning_base, 20))) : tuning_base;",
    "tuning_ref = mod_active[6] ? max(20, min(2000, tuning_base + au_key(6, 2, tuning_base, 20))) : tuning_base;")
rep("(mod_active[5] || mod_active[6] || mod_active[7]) ? (   // Transpose, Fine tune, Tuning reference",
    "(mod_active[3] || mod_active[4] || mod_active[5] || mod_active[6]) ? (   // Source fine tune, Transpose, Fine tune, Tuning reference")
rep("""  eff_semi = pv_semis(pitch_unit, target_drift_unit[5] == 0 && ramp_by_unit[5] == 0 ? pitch_semi + target_drift_offset[5] + ramp_offset_mem[5]
                                                                                   : pitch_semi + au_key(5, 1, pitch_semi, pitch_unit))
           + pv_semis(pitch_funit, pitch_fine + au_key(6, 1, pitch_fine, pitch_funit));""",
"""  eff_semi = pv_semis(pitch_unit, target_drift_unit[4] == 0 && ramp_by_unit[4] == 0 ? pitch_semi + target_drift_offset[4] + ramp_offset_mem[4]
                                                                                   : pitch_semi + au_key(4, 1, pitch_semi, pitch_unit))
           + pv_semis(pitch_funit, pitch_fine + au_key(5, 1, pitch_fine, pitch_funit));
  // Pitch source fine tune (3), 2026-09-16. It says where the capture's note sits, so a drift on
  // it moves what Pitch target note lands on: heard only while that link is live (a Pitch source
  // note set and Transpose in Semitones), and the sound moves the OPPOSITE way to the drift.
  mod_active[3] && slider12 > 0 && pitch_unit == 1 ? (
    eff_semi -= pv_src_semis(slider12, slider13, slider14 + au_key(3, 1, slider14, slider13)) - pv_src_semis(slider12, slider13, slider14);
  );""")
rep("stereo_width + (mod_active[8] ? target_drift_offset[8] + ramp_offset_mem[8] : 0)","stereo_width + (mod_active[9] ? target_drift_offset[9] + ramp_offset_mem[9] : 0)")
rep("mod_active[8] ? ( voice_detune","mod_active[9] ? ( voice_detune")
rep("mod_active[10] ? au_key(10, 2, lowcut_hz, 20) : 0","mod_active[11] ? au_key(11, 2, lowcut_hz, 20) : 0")
rep("mod_active[84] ? (   // Output level","mod_active[104] ? (   // Output level")
rep("voice_db_base + target_drift_offset[84] + ramp_offset_mem[84]","voice_db_base + target_drift_offset[104] + ramp_offset_mem[104]")
rep("mod_active[11] ? au_key(11, 2, hicut_hz, 20) : 0","mod_active[13] ? au_key(13, 2, hicut_hz, 20) : 0")
rep("ot_harm_base + target_drift_offset[12] + ramp_offset_mem[12]","ot_harm_base + target_drift_offset[15] + ramp_offset_mem[15]")
rep("mod_active[13] ? ( ot_depth_db = max(0, min(48, ot_depth_base + mo_q(13))); );","mod_active[16] ? ( ot_depth_db = max(0, min(48, ot_depth_base + mo_q(16))); );")
rep("mod_active[14] ? ( ot_width = max(0.5, min(4, ot_width_base + mo_q(14))); );","mod_active[17] ? ( ot_width = max(0.5, min(4, ot_width_base + mo_q(17))); );")
rep("mod_active[9] ? ( denoise_amt = max(0, min(100, denoise_base + mo_q(9))); );","mod_active[10] ? ( denoise_amt = max(0, min(100, denoise_base + mo_q(10))); );")
rep("mod_active[83] ? (\n  mo_dry_db = max(-60, min(24, dry_db_base + mo_q(83)));","mod_active[103] ? (\n  mo_dry_db = max(-60, min(24, dry_db_base + mo_q(103)));")
rep("nlay_on = 1; );\n  lz += 1;\n);\nbase_gain = layer_gain[LAY_ORIG];\n","""nlay_on = 1; );
  lz += 1;
);
base_gain = layer_gain[LAY_ORIG];
// Layer harmonics with drift and ramp (targets LH_T0+k, 2026-09-16): a whole count, 0..64,
// rounded; 0 still means uncapped. Exactly the stored count while nothing drives it.
lz = 0;
loop(N_LAY_SLOTS,
  lay_nh_eff[lz] = mod_active[LH_T0+lz] ? max(0, min(64, floor(lay_nharm[lz] + mo_q(LH_T0+lz) + 0.5))) : lay_nharm[lz];
  lz += 1;
);
""")
rep("lynh = lay_nharm[lyk] > 0 ? min(nharm_used, lay_nharm[lyk]) : nharm_used;","lynh = lay_nh_eff[lyk] > 0 ? min(nharm_used, lay_nh_eff[lyk]) : nharm_used;")
rep("""    pr_accum += 1 / srate;
    pr_accum >= (pr_resting ? pr_rest_sec : pr_play_sec) ? (""","""    // Drift movement mode (2026-09-16): With the target, a stretch keeps the length it began
    // with -- pr_accum is 0 only at the start and on each flip; On a clock, it is read live.
    (pr_accum == 0 || !pr_len_set || drift_moves[105] == 1) ? pr_play_lat = pr_play_sec;
    (pr_accum == 0 || !pr_len_set || drift_moves[106] == 1) ? pr_rest_lat = pr_rest_sec;
    pr_len_set = 1;
    pr_accum += 1 / srate;
    pr_accum >= (pr_resting ? pr_rest_lat : pr_play_lat) ? (""")
rep("pr_resting          = 0;\npr_accum            = 0;\n","pr_resting          = 0;\npr_accum            = 0;\npr_len_set          = 0;\n")
if ERR:
    for e in ERR: print('NO MATCH', e)
    raise SystemExit('NOTHING WRITTEN')
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))
print('stage 5 (without serialize) applied')
