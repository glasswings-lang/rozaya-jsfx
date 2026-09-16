import re
p='src/spectral_vowel_morpher.jsfx'
s=open(p,encoding='utf-8',newline='').read(); nl='\r\n' if '\r\n' in s else '\n'; s=s.replace('\r\n','\n')
ERR=[]
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: ERR.append((a[:70],c,n)); return
    s=s.replace(a,b)
notes=re.search(r'\{None,(C-1[^}]*)\}', s).group(1)
assert len(notes.split(','))==128
off_enum='{Off,'+notes+'}'
rep("slider29:0<0,20000,1>Low cut (Hz)\n",f"""// --- Low cut and High cut, pitch blocks since 2026-09-16 (R27). 0 means OFF in every unit, and
//     each note list starts on a dedicated Off -- Rozaya: "Feels like 0 could just be 0, then the
//     first thing everything lands on is a dedicated off position". In Semitones the value is a
//     note number (69 = A4 at the Tuning reference), in Cents that times 100. The note name and
//     the value follow each other; switching the mode converts the value. A drift or ramp on a
//     cut that is ON stops at the lowest real frequency rather than switching it off
//     (Rozaya: "I like that re: the drift move"), and moves nothing while it is off.
slider27:0<0,2,1{{Hz,Semitones,Cents}}>Low cut pitch mode
slider28:0<0,128,1{off_enum}>Low cut note name
slider29:0<0,20000,0.001>Low cut value (0 = off)
slider30:2<0,2,1{{Hz,Semitones,Cents}}>Low cut fine tune unit
slider31:0<-1000,1000,0.001>Low cut fine tune
""")
rep("//     20000 means off, and off is bit-identical to this control not existing.\nslider34:20000<200,20000,10>High cut (Hz, 20000 = off)\n",
f"""//     Off (0, since 2026-09-16; it was 20000) is bit-identical to this control not existing.
slider32:0<0,2,1{{Hz,Semitones,Cents}}>High cut pitch mode
slider33:0<0,128,1{off_enum}>High cut note name
slider34:0<0,20000,0.001>High cut value (0 = off)
slider35:2<0,2,1{{Hz,Semitones,Cents}}>High cut fine tune unit
slider36:0<-1000,1000,0.001>High cut fine tune
""")
rep("function au_back(nu, tt)","""// The cut blocks (2026-09-16). A value in {0 Hz, 1 Semitones (a note number), 2 Cents} -> Hz.
function cut_hz_of(mode, v) ( mode == 0 ? v : mode == 1 ? tuning_ref * pow(2, (v - 69) / 12) : tuning_ref * pow(2, (v / 100 - 69) / 12); );
function cut_v_of(mode, hz) local(m) ( m = 69 + 12 * log(max(hz, 0.000001) / max(tuning_ref, 0.001)) / log(2); mode == 0 ? hz : mode == 1 ? m : m * 100; );
// Switching the mode keeps the frequency; 0 stays 0 (off).
function cut_conv(v, from, to) ( v <= 0 ? 0 : cut_v_of(to, cut_hz_of(from, v)); );
// The note name a value shows: 0 Off, else 1 + the nearest note number.
function cut_note(mode, v) local(m) (
  v <= 0 ? 0 : ( m = mode == 1 ? v : mode == 2 ? v / 100 : 69 + 12 * log(max(v, 0.000001) / max(tuning_ref, 0.001)) / log(2);
                 1 + max(0, min(127, floor(m + 0.5))); );
);
function cut_from_note(mode, n) ( n <= 0 ? 0 : mode == 0 ? tuning_ref * pow(2, (n - 1 - 69) / 12) : mode == 1 ? n - 1 : (n - 1) * 100; );
// A drift or ramp amount on a cut, in its mode's unit. Hz is au_freq, exactly as before.
function cut_amt(off, u, base, mode) local(f) (
  u == 1 ? ( f = cut_hz_of(mode, base) + off; (f > 0 ? cut_v_of(mode, f) : 0) - base; ) :
  u == 2 ? (mode == 2 ? off * 100 : off) : u == 3 ? (mode == 1 ? off / 100 : off) : off;
);
function cut_q(k, base, mode, floor) (
  mode == 0 ? au_key(k, 2, base, floor) :
  cut_amt(target_drift_offset[k], target_drift_unit[k], base, mode) + cut_amt(ramp_offset_mem[k], ramp_by_unit[k], base, mode);
);
function cut_fine(hz, f, u) ( u == 0 ? hz + f : u == 1 ? hz * pow(2, f / 12) : hz * pow(2, f / 1200); );
function au_back(nu, tt)""")
rep("hicut_hz      = slider34;                                    // base for High cut drift (20000 = off)\n",
"""hicut_hz      = slider34;                                    // base for High cut drift (0 = off since 2026-09-16)
lc_mode = slider27; lc_funit = slider30; lc_fine = slider31;
hc_mode = slider32; hc_funit = slider35; hc_fine = slider36;
// The note name and the value follow each other, and a mode switch converts the value.
// Trackers adopted in @block, like every other mirror here, so a restore is never an edit.
cut_ui_inited ? (
  slider27 != lc_last_mode ? ( slider29 = cut_conv(slider29, lc_last_mode, slider27); slider28 = cut_note(slider27, slider29); sliderchange(-1); ) :
  slider28 != lc_last_note ? ( slider29 = cut_from_note(slider27, slider28); sliderchange(-1); ) :
  slider29 != lc_last_val  ? ( slider28 = cut_note(slider27, slider29); sliderchange(-1); );
  slider32 != hc_last_mode ? ( slider34 = cut_conv(slider34, hc_last_mode, slider32); slider33 = cut_note(slider32, slider34); sliderchange(-1); ) :
  slider33 != hc_last_note ? ( slider34 = cut_from_note(slider32, slider33); sliderchange(-1); ) :
  slider34 != hc_last_val  ? ( slider33 = cut_note(slider32, slider34); sliderchange(-1); );
  lc_last_mode = slider27; lc_last_note = slider28; lc_last_val = slider29;
  hc_last_mode = slider32; hc_last_note = slider33; hc_last_val = slider34;
  lowcut_hz = slider29; hicut_hz = slider34;
);
""")
rep("!pv_inited ? (","""!cut_ui_inited ? (
  lc_last_mode = slider27; lc_last_note = slider28; lc_last_val = slider29;
  hc_last_mode = slider32; hc_last_note = slider33; hc_last_val = slider34;
  cut_ui_inited = 1;
);
!pv_inited ? (""")
rep("eff_lowcut_hz    = max(0,  min(20000, lowcut_hz    + (mod_active[11] ? au_key(11, 2, lowcut_hz, 20) : 0)));\n",
"""// Low cut (11, fine tune 12). Off at 0. In Hz with no fine tune the old expression, except that
// a drift stops one FFT bin up instead of at 0, so it cannot switch an ON cut off.
lowcut_hz > 0 ? (
  lc_v  = lowcut_hz + (mod_active[11] ? cut_q(11, lowcut_hz, lc_mode, 20) : 0);
  lc_hz = lc_mode == 0 ? lc_v : cut_hz_of(lc_mode, lc_v);
  lc_f  = lc_fine + (mod_active[12] ? sp_q(12, lc_funit) : 0);
  lc_f != 0 ? lc_hz = cut_fine(lc_hz, lc_f, lc_funit);
  eff_lowcut_hz = max(min(cut_hz_of(lc_mode, lowcut_hz), srate / FFTSIZE), min(20000, lc_hz));
) : (
  eff_lowcut_hz = 0;
);
""")
rep("eff_hicut_hz = max(200, min(20000, hicut_hz + (mod_active[13] ? au_key(13, 2, hicut_hz, 20) : 0)));\nhc_on = eff_hicut_hz < 19999.5 ? 1 : 0;\n",
"""// High cut (13, fine tune 14). Off at 0. On, it is the old expression in Hz with no fine tune: floored
// at 200 Hz (or the cut's own frequency, if it was set lower by note), and reaching 20000 is off.
hicut_hz > 0 ? (
  hc_v  = hicut_hz + (mod_active[13] ? cut_q(13, hicut_hz, hc_mode, 20) : 0);
  hc_hz = hc_mode == 0 ? hc_v : cut_hz_of(hc_mode, hc_v);
  hc_f  = hc_fine + (mod_active[14] ? sp_q(14, hc_funit) : 0);
  hc_f != 0 ? hc_hz = cut_fine(hc_hz, hc_f, hc_funit);
  eff_hicut_hz = max(min(cut_hz_of(hc_mode, hicut_hz), 200), min(20000, hc_hz));
  hc_on = eff_hicut_hz < 19999.5 ? 1 : 0;
) : (
  eff_hicut_hz = 20000; hc_on = 0;
);
""")
if ERR:
    for e in ERR: print('NO MATCH', e)
    raise SystemExit('NOTHING WRITTEN')
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))
print('stage 7 applied')
