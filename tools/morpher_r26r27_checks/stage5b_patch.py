p='src/spectral_vowel_morpher.jsfx'
s=open(p,encoding='utf-8',newline='').read(); nl='\r\n' if '\r\n' in s else '\n'; s=s.replace('\r\n','\n')
ERR=[]
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: ERR.append((a[:70],c,n)); return
    s=s.replace(a,b)
rep("ser_magic = 7700087;\n","""//   7700107 -- current (2026-09-16, R26/R27). 107 targets in the new control order (Wash grain
//              gone; Pitch source fine tune, Spread / Low cut / High cut fine tunes and Layer
//              harmonics in), and APPENDED at the very end: Drift period unit, Ramp time unit and
//              Drift movement mode, per target. A 7700087 blob reads at 87, is remapped by
//              t107_o2n, and seeds the per-target units from the one shared slider it still had.
ser_magic = 7700107;
""")
rep("(ser_magic == 7700087 || ser_magic == 7700055 ||","(ser_magic == 7700107 || ser_magic == 7700087 || ser_magic == 7700055 ||")
rep("n_ser_targets = ser_magic == 7700087 ? N_TARGETS : ","n_ser_targets = ser_magic == 7700107 ? N_TARGETS : ser_magic == 7700087 ? 87 : ")
rep("""    file_mem(0, target_drift_unit, N_TARGETS);
    file_mem(0, ramp_by_unit,      N_TARGETS);
  );
""","""    file_mem(0, target_drift_unit, n_ser_targets);
    file_mem(0, ramp_by_unit,      n_ser_targets);
  );
  // --- 7700107 (2026-09-16): the per-target units and Drift movement mode, appended last.
  ser_magic >= 7700107 ? (
    file_mem(0, target_drift_punit, N_TARGETS);
    file_mem(0, ramp_tunit,         N_TARGETS);
    file_mem(0, drift_moves,        N_TARGETS);
  );
""")
rep("""    last_ramp_target   = t55_o2n(max(0, min(54, last_ramp_target | 0)));
  );
""","""    last_ramp_target   = t55_o2n(max(0, min(54, last_ramp_target | 0)));
  );

  // --- The 87-target list -> the 107 of 2026-09-16, walked after every remap above has brought
  //     an old blob to 87. A selector parked on Wash grain lands on Morph. Every target takes the
  //     ONE Drift period unit and Ramp time unit the old save used, from their sliders (62, 73 on
  //     the migrated line), so nothing changes sound; Drift movement mode starts on With the target.
  (file_avail(0) >= 0 && ser_magic <= 7700087) ? (
    t107_remap(target_drift_up, 0);    t107_remap(target_drift_down, 0);
    t107_remap(target_drift_per, 30);  t107_remap(target_drift_shape, 0);
    t107_remap(ramp_by_mem, 0);        t107_remap(ramp_dur_mem, 0);
    t107_remap(ramp_delay_mem, 0);
    t107_remap(target_drift_play, 0);  t107_remap(target_drift_rest, 0);
    t107_remap(ramp_play_mem, 0);      t107_remap(ramp_rest_mem, 0);
    t107_remap(target_drift_unit, 0);  t107_remap(ramp_by_unit, 0);
    ser_t = t107_o2n(max(0, min(86, last_target_select | 0))); last_target_select = ser_t >= 0 ? ser_t : 0;
    ser_t = t107_o2n(max(0, min(86, last_ramp_target | 0)));   last_ramp_target   = ser_t >= 0 ? ser_t : 0;
    ser_i = 0;
    loop(N_TARGETS,
      target_drift_punit[ser_i] = slider62; ramp_tunit[ser_i] = slider73; drift_moves[ser_i] = 0;
      ser_i += 1;
    );
  );
""")
rep("""    dui_last[11] = slider59; dui_last[12] = slider71;
    dui_last[0] = slider60;""","""    dui_last[11] = slider59; dui_last[12] = slider71;
    dui_last[13] = slider62; dui_last[14] = slider73; dui_last[15] = slider64;
    slider_show(slider64, last_target_select >= 105);
    dui_last[0] = slider60;""")
if ERR:
    for e in ERR: print('NO MATCH', e)
    raise SystemExit('NOTHING WRITTEN')
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))
print('stage 5b (serialize) applied')
