"""Stage 4: Spread, Low cut and High cut become per-slot pitch blocks (the Morpher's stages 6-7)."""
p = r'C:/git-src/rozaya-jsfx/src/spectral_vowel_passage.jsfx'
s = open(p, encoding='utf-8', newline='').read()


def rep(a, b, n=1):
    global s
    if s.count(a) == n:
        s = s.replace(a, b)
        return
    a2, b2 = a.replace('\n', '\r\n'), b.replace('\n', '\r\n')
    assert s.count(a2) == n, (s.count(a), s.count(a2), a[:160])
    s = s.replace(a2, b2)


NAMES = "C C# D D# E F F# G G# A A# B".split()
NOTES = ",".join(f"{n}{o}" for o in range(-1, 10) for i, n in enumerate(NAMES) if (o + 1) * 12 + i <= 127)

# --- declarations
rep("slider32:0<0,1000,0.1>Spread (Hz)\n",
"""// --- Spread, a pitch block since 2026-09-16 (the Morpher's shape, per slot here). Rozaya, on the
//     Morpher: "For that reason alone we should have a spread unit, and it should encorperate the
//     usual pitch block." No note name: "it's just semitones worth of width." Hz with no fine
//     tune is exactly the blur it always was. In Semitones or Cents each frequency blurs that
//     interval either side; a fine tune in Hz then widens both sides by that many Hz.
slider31:0<0,2,1{Hz,Semitones,Cents}>Spread pitch mode
slider32:0<0,1000,0.1>Spread value (Hz / semitones / cents)
slider33:2<0,2,1{Hz,Semitones,Cents}>Spread fine tune unit
slider34:0<-1000,1000,0.001>Spread fine tune
""")
rep("slider39:0<0,20000,1>Low cut (Hz)\nslider44:20000<200,20000,10>High cut (Hz, 20000 = off)\n",
"""// --- Low cut and High cut, per-slot pitch blocks since 2026-09-16 (the Morpher's). 0 means OFF in
//     every unit, and each note list starts on a dedicated Off (Rozaya: "Feels like 0 could just
//     be 0, then the first thing everything lands on is a dedicated off position"). In Semitones
//     the value is a note number (69 = A4 at the Tuning reference), in Cents that times 100. The
//     note name and the value follow each other; switching the mode converts the value. A drift
//     or ramp on a cut that is ON stops at the lowest real frequency rather than switching it
//     off, and moves nothing while it is off. High cut's off was 20000 before this.
slider37:0<0,2,1{Hz,Semitones,Cents}>Low cut pitch mode
slider38:0<0,128,1{Off,NOTES}>Low cut note name
slider39:0<0,20000,0.001>Low cut value (0 = off)
slider40:2<0,2,1{Hz,Semitones,Cents}>Low cut fine tune unit
slider41:0<-1000,1000,0.001>Low cut fine tune
slider42:0<0,2,1{Hz,Semitones,Cents}>High cut pitch mode
slider43:0<0,128,1{Off,NOTES}>High cut note name
slider44:0<0,20000,0.001>High cut value (0 = off)
slider45:2<0,2,1{Hz,Semitones,Cents}>High cut fine tune unit
slider46:0<-1000,1000,0.001>High cut fine tune
""".replace("NOTES", NOTES))

# --- banks
rep("slot_hicut    = freemem; freemem += NSLOTS;\n",
"""slot_hicut    = freemem; freemem += NSLOTS;   // 0 = off since 2026-09-16 (was 20000)
// The Spread and cut pitch blocks (2026-09-16), per slot. Saved from 7700009. The note names are
// not banked: they are always the value's, shown in its mode.
slot_spmode   = freemem; freemem += NSLOTS;
slot_spfunit  = freemem; freemem += NSLOTS;
slot_spfine   = freemem; freemem += NSLOTS;
slot_lcmode   = freemem; freemem += NSLOTS;
slot_lcfunit  = freemem; freemem += NSLOTS;
slot_lcfine   = freemem; freemem += NSLOTS;
slot_hcmode   = freemem; freemem += NSLOTS;
slot_hcfunit  = freemem; freemem += NSLOTS;
slot_hcfine   = freemem; freemem += NSLOTS;
spc           = freemem; freemem += NBINS + 1;   // Spread in Semitones/Cents: running sums of mtmp
""")
rep("slot_grain[i] = 150; slot_hicut[i] = 20000; slot_tmunit[i] = 0; i += 1; );   // Wash grain's default; High cut off",
    "slot_grain[i] = 150; slot_hicut[i] = 0; slot_tmunit[i] = 0;\n"
    "  slot_spmode[i] = 0; slot_spfunit[i] = 2; slot_spfine[i] = 0; slot_lcmode[i] = 0; slot_lcfunit[i] = 2; slot_lcfine[i] = 0;\n"
    "  slot_hcmode[i] = 0; slot_hcfunit[i] = 2; slot_hcfine[i] = 0; i += 1; );   // Wash grain's default; cuts off")
rep("eff_spread_hz = 0; eff_lowcut_hz = 0; eff_stereo_width = 0;",
    "eff_spread_hz = 0; eff_lowcut_hz = 0; eff_stereo_width = 0; sp_mode = 0; sp_semis = 0; sp_extra_hz = 0;")

# --- functions, straight after au_key
i = s.find("function au_key(k, kind, base, nu) (")
assert i > 0
j = s.find(");", s.find("au_time(target_drift_offset[k]", i)) + 2
FUN = """
// Spread and its fine tune in a width unit {0 Hz, 1 Semitones, 2 Cents} (2026-09-16, the Morpher's):
// Semitones and Cents amounts convert into each other; anything else takes the amount as it stands.
function sp_amt(off, u, mode) ( u == 2 ? (mode == 2 ? off * 100 : off) : u == 3 ? (mode == 1 ? off / 100 : off) : off; );
function sp_q(k, mode) ( sp_amt(target_drift_offset[k], target_drift_unit[k], mode) + sp_amt(ramp_offset_mem[k], ramp_by_unit[k], mode); );
// The cut blocks. A value in {0 Hz, 1 Semitones (a note number), 2 Cents} -> Hz.
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
function cut_fine(hz, f, u) ( u == 0 ? hz + f : u == 1 ? hz * pow(2, f / 12) : hz * pow(2, f / 1200); );
function cut_q(k, base, mode, floor) (
  mode == 0 ? au_key(k, 2, base, floor) :
  cut_amt(target_drift_offset[k], target_drift_unit[k], base, mode) + cut_amt(ramp_offset_mem[k], ramp_by_unit[k], base, mode);
);
// One slot's heard cut in Hz (tgt: 6 Low cut, 7 High cut). Off (0) moves nothing. On, a drift stops
// at the cut's own frequency or `bottom`, whichever is lower, instead of switching it off.
function cut_slot_hz(sl, tgt, v, mode, funit, fine, bottom) local(cv, hz) (
  v <= 0 ? 0 : (
    cv = v + cut_q(sl*DSTRIDE + tgt, v, mode, 20);
    hz = mode == 0 ? cv : cut_hz_of(mode, cv);
    fine != 0 ? hz = cut_fine(hz, fine, funit);
    max(min(cut_hz_of(mode, v), bottom), min(20000, hz));
  );
);
"""
s = s[:j] + FUN.replace('\n', '\r\n' if s[j:j + 2] == '\r\n' else '\n') + s[j:]

# --- @slider: note <-> value links, before the slot banks capture
rep("""    slider25 = max(0, min(127, floor(slider27 + pv_src + 0.5))); slider_automate(slider25);
  );
);
""", """    slider25 = max(0, min(127, floor(slider27 + pv_src + 0.5))); slider_automate(slider25);
  );
);
// The cut blocks (2026-09-16): the note name and the value follow each other, and a mode switch
// converts the value. Never on a slot switch -- the trackers are refreshed after the slot block.
(ps_inited && last_cap_sel == cap_sel) ? (
  slider37 != lc_last_mode ? ( slider39 = cut_conv(slider39, lc_last_mode, slider37); slider38 = cut_note(slider37, slider39); sliderchange(-1); ) :
  slider38 != lc_last_note ? ( slider39 = cut_from_note(slider37, slider38); sliderchange(-1); ) :
  slider39 != lc_last_val  ? ( slider38 = cut_note(slider37, slider39); sliderchange(-1); );
  slider42 != hc_last_mode ? ( slider44 = cut_conv(slider44, hc_last_mode, slider42); slider43 = cut_note(slider42, slider44); sliderchange(-1); ) :
  slider43 != hc_last_note ? ( slider44 = cut_from_note(slider42, slider43); sliderchange(-1); ) :
  slider44 != hc_last_val  ? ( slider43 = cut_note(slider42, slider44); sliderchange(-1); );
);
""")
SAVE = ("    slot_spmode[X] = slider31; slot_spfunit[X] = slider33; slot_spfine[X] = slider34;\n"
        "    slot_lcmode[X] = slider37; slot_lcfunit[X] = slider40; slot_lcfine[X] = slider41;\n"
        "    slot_hcmode[X] = slider42; slot_hcfunit[X] = slider45; slot_hcfine[X] = slider46;\n")
# slot switch: save
rep("    slot_grain[last_cap_slot] = slider21; slot_hicut[last_cap_slot] = slider44; slot_tmunit[last_cap_slot] = slider11;\n  );\n",
    "    slot_grain[last_cap_slot] = slider21; slot_hicut[last_cap_slot] = slider44; slot_tmunit[last_cap_slot] = slider11;\n"
    + SAVE.replace('X', 'last_cap_slot') + "  );\n")
# slot switch: load
rep("  slider21 = slot_grain[cap_slot]; slider44 = slot_hicut[cap_slot]; slider11 = slot_tmunit[cap_slot];\n  sliderchange(-1);",
    "  slider21 = slot_grain[cap_slot]; slider44 = slot_hicut[cap_slot]; slider11 = slot_tmunit[cap_slot];\n"
    "  slider31 = slot_spmode[cap_slot]; slider33 = slot_spfunit[cap_slot]; slider34 = slot_spfine[cap_slot];\n"
    "  slider37 = slot_lcmode[cap_slot]; slider40 = slot_lcfunit[cap_slot]; slider41 = slot_lcfine[cap_slot];\n"
    "  slider42 = slot_hcmode[cap_slot]; slider45 = slot_hcfunit[cap_slot]; slider46 = slot_hcfine[cap_slot];\n"
    "  slider38 = cut_note(slider37, slider39); slider43 = cut_note(slider42, slider44);\n  sliderchange(-1);")
# All slots
rep("    ps_all(41, slider11, slider11, slot_tmunit);\n",
    "    ps_all(41, slider11, slider11, slot_tmunit);\n"
    "    ps_all(44, slider31, slider31, slot_spmode); ps_all(45, slider33, slider33, slot_spfunit); ps_all(46, slider34, slider34, slot_spfine);\n"
    "    ps_all(47, slider37, slider37, slot_lcmode); ps_all(48, slider40, slider40, slot_lcfunit); ps_all(49, slider41, slider41, slot_lcfine);\n"
    "    ps_all(50, slider42, slider42, slot_hcmode); ps_all(51, slider45, slider45, slot_hcfunit); ps_all(52, slider46, slider46, slot_hcfine);\n")
# live edit
rep("  slot_grain[cap_slot] = slider21; slot_hicut[cap_slot] = slider44; slot_tmunit[cap_slot] = slider11;\n  ps_adopt();",
    "  slot_grain[cap_slot] = slider21; slot_hicut[cap_slot] = slider44; slot_tmunit[cap_slot] = slider11;\n"
    + SAVE.replace('X', 'cap_slot').replace('    ', '  ') + "  ps_adopt();")
# trackers after the slot block
rep("pv_last_tgt = slider25; pv_last_tval = slider27; pv_last_src = slider22; pv_last_sf = slider24; pv_last_sfu = slider23;\ncap_point01",
    "pv_last_tgt = slider25; pv_last_tval = slider27; pv_last_src = slider22; pv_last_sf = slider24; pv_last_sfu = slider23;\n"
    "lc_last_mode = slider37; lc_last_note = slider38; lc_last_val = slider39;\n"
    "hc_last_mode = slider42; hc_last_note = slider43; hc_last_val = slider44;\ncap_point01")
# ps_adopt
rep("  ps_last[42] = slider69; ps_last[43] = slider81; ps_last[31] = slider74;\n",
    "  ps_last[42] = slider69; ps_last[43] = slider81; ps_last[31] = slider74;\n"
    "  ps_last[44] = slider31; ps_last[45] = slider33; ps_last[46] = slider34; ps_last[47] = slider37; ps_last[48] = slider40;\n"
    "  ps_last[49] = slider41; ps_last[50] = slider42; ps_last[51] = slider45; ps_last[52] = slider46;\n"
    "  lc_last_mode = slider37; lc_last_note = slider38; lc_last_val = slider39;\n"
    "  hc_last_mode = slider42; hc_last_note = slider43; hc_last_val = slider44;\n")
# capture
rep("  slot_grain[cpk] = slider21; slot_hicut[cpk] = slider44;\n",
    "  slot_grain[cpk] = slider21; slot_hicut[cpk] = slider44;\n" + SAVE.replace('X', 'cpk').replace('    ', '  '))

# --- gen_grain: Spread in Semitones/Cents
rep("  sp = floor(eff_spread_hz * FFTSIZE / srate);   // eff_ = base + Drift offset\n",
    "  sp = sp_mode == 0 ? floor(eff_spread_hz * FFTSIZE / srate) : 0;   // eff_ = base + Drift offset\n")
rep("""    i += 1;
  );
  pk = 0; i = 0; loop(NBINS, curmag[i] > pk ? pk = curmag[i]; i += 1; );
  thr = eff_denoise""", """    i += 1;
  );
  // Spread in Semitones or Cents (2026-09-16, the Morpher's): each bin blurs from f / r to f * r,
  // r = 2^(width/12), plus any fine tune in Hz on both sides -- a window that grows with frequency,
  // so running sums (spc) give each bin its own mean in one pass.
  sp_mode != 0 && (sp_semis > 0 || sp_extra_hz > 0) ? (
    sp_r = pow(2, sp_semis / 12); sp_ex = sp_extra_hz * FFTSIZE / srate;
    spc[0] = 0; i = 0; loop(NBINS, spc[i + 1] = spc[i] + mtmp[i]; i += 1; );
    i = 0;
    loop(NBINS,
      sp_lo = max(0, min(i, floor(i / sp_r - sp_ex + 0.5)));
      sp_hi = min(NBINS - 1, max(i, floor(i * sp_r + sp_ex + 0.5)));
      curmag[i] = (spc[sp_hi + 1] - spc[sp_lo]) / (sp_hi - sp_lo + 1);
      i += 1;
    );
  );
  pk = 0; i = 0; loop(NBINS, curmag[i] > pk ? pk = curmag[i]; i += 1; );
  thr = eff_denoise""")

# --- @sample: Spread
rep("""eff_spread_hz = max(0, min(1000, sblend(slot_spread, sb_i, sb_j, sb_f)
                                + dmodc(4, 2, slot_spread, srate / FFTSIZE)));
""", """(slot_spmode[sb_i] == 0 && slot_spmode[sb_j] == 0 && slot_spfine[sb_i] == 0 && slot_spfine[sb_j] == 0) ? (
  // Both slots in Hz with no fine tune (2026-09-16): exactly the old expression.
  sp_mode = 0; sp_semis = 0; sp_extra_hz = 0;
  eff_spread_hz = max(0, min(1000, sblend(slot_spread, sb_i, sb_j, sb_f)
                                  + dmodc(4, 2, slot_spread, srate / FFTSIZE)));
) : (
  // Otherwise each slot resolves to a width in semitones plus Hz either side, and the two blend.
  sp_mode = 1; eff_spread_hz = 0; sp_semis = 0; sp_extra_hz = 0;
  sp_k = 0;
  loop(2,
    sp_sl = sp_k == 0 ? sb_i : sb_j; sp_w = sp_k == 0 ? 1 - sb_f : sb_f;
    sp_m = slot_spmode[sp_sl]; sp_fu = slot_spfunit[sp_sl]; sp_fn = slot_spfine[sp_sl];
    sp_m == 0 ? (
      sp_hz = max(0, min(1000, slot_spread[sp_sl] + au_key(sp_sl*DSTRIDE + 4, 2, slot_spread[sp_sl], srate / FFTSIZE)));
      sp_fn != 0 ? sp_hz = sp_fu == 0 ? max(0, sp_hz + sp_fn) : sp_fu == 1 ? sp_hz * pow(2, sp_fn / 12) : sp_hz * pow(2, sp_fn / 1200);
      sp_extra_hz += sp_w * sp_hz;
    ) : (
      sp_st = max(0, slot_spread[sp_sl] + sp_q(sp_sl*DSTRIDE + 4, sp_m));
      sp_m == 2 ? sp_st /= 100;
      sp_fu == 0 ? ( sp_extra_hz += sp_w * max(0, sp_fn); ) : ( sp_st += sp_fu == 1 ? sp_fn : sp_fn / 100; );
      sp_semis += sp_w * max(0, min(48, sp_st));
    );
    sp_k += 1;
  );
);
""")
# --- @sample: High cut
rep("""eff_hicut_hz = slot_hicut[sb_i] == slot_hicut[sb_j] ? slot_hicut[sb_i] : sblend(slot_hicut, sb_i, sb_j, sb_f);
eff_hicut_hz = max(200, min(20000, eff_hicut_hz + dmodc(7, 2, slot_hicut, 20)));
""", """// Pitch blocks since 2026-09-16: 0 is off, and an off slot blends as 20000 (the old off). Both
// slots in Hz with no fine tune: the old expression, except that an off slot's drift moves nothing.
(slot_hcmode[sb_i] == 0 && slot_hcmode[sb_j] == 0 && slot_hcfine[sb_i] == 0 && slot_hcfine[sb_j] == 0) ? (
  hcb_i = slot_hicut[sb_i] > 0 ? slot_hicut[sb_i] : 20000; hcb_j = slot_hicut[sb_j] > 0 ? slot_hicut[sb_j] : 20000;
  eff_hicut_hz = hcb_i == hcb_j ? hcb_i : hcb_i * (1 - sb_f) + hcb_j * sb_f;
  hcd = (slot_hicut[sb_i] > 0 ? au_key(sb_i*DSTRIDE + 7, 2, slot_hicut[sb_i], 20) : 0) * (1 - sb_f)
      + (slot_hicut[sb_j] > 0 ? au_key(sb_j*DSTRIDE + 7, 2, slot_hicut[sb_j], 20) : 0) * sb_f;
  eff_hicut_hz = max(min(eff_hicut_hz, 200), min(20000, eff_hicut_hz + hcd));
) : (
  hcb_i = slot_hicut[sb_i] > 0 ? cut_slot_hz(sb_i, 7, slot_hicut[sb_i], slot_hcmode[sb_i], slot_hcfunit[sb_i], slot_hcfine[sb_i], 200) : 20000;
  hcb_j = slot_hicut[sb_j] > 0 ? cut_slot_hz(sb_j, 7, slot_hicut[sb_j], slot_hcmode[sb_j], slot_hcfunit[sb_j], slot_hcfine[sb_j], 200) : 20000;
  eff_hicut_hz = hcb_i * (1 - sb_f) + hcb_j * sb_f;
);
""")
# --- @sample: Low cut
rep("""eff_lowcut_hz = max(0, min(20000, sblend(slot_lowcut, sb_i, sb_j, sb_f)
                                + dmodc(6, 2, slot_lowcut, 20)));
""", """// Pitch blocks since 2026-09-16. Both slots in Hz with no fine tune: the old expression, except
// that an off slot's drift moves nothing and an on cut's drift stops one FFT bin up, not at off.
(slot_lcmode[sb_i] == 0 && slot_lcmode[sb_j] == 0 && slot_lcfine[sb_i] == 0 && slot_lcfine[sb_j] == 0) ? (
  lcb = sblend(slot_lowcut, sb_i, sb_j, sb_f);
  lcd = (slot_lowcut[sb_i] > 0 ? au_key(sb_i*DSTRIDE + 6, 2, slot_lowcut[sb_i], 20) : 0) * (1 - sb_f)
      + (slot_lowcut[sb_j] > 0 ? au_key(sb_j*DSTRIDE + 6, 2, slot_lowcut[sb_j], 20) : 0) * sb_f;
  eff_lowcut_hz = lcb > 0 ? max(min(lcb, srate / FFTSIZE), min(20000, lcb + lcd)) : 0;
) : (
  eff_lowcut_hz = cut_slot_hz(sb_i, 6, slot_lowcut[sb_i], slot_lcmode[sb_i], slot_lcfunit[sb_i], slot_lcfine[sb_i], srate / FFTSIZE) * (1 - sb_f)
                + cut_slot_hz(sb_j, 6, slot_lowcut[sb_j], slot_lcmode[sb_j], slot_lcfunit[sb_j], slot_lcfine[sb_j], srate / FFTSIZE) * sb_f;
);
""")

# --- @serialize
rep("ser_magic = 7700008;\nfile_var(0, ser_magic);\n(ser_magic == 7700008 ||",
    "ser_magic = 7700009;\nfile_var(0, ser_magic);\n(ser_magic == 7700009 || ser_magic == 7700008 ||")
rep("""    file_mem(0, target_drift_moves, DBANK);
  );
""", """    file_mem(0, target_drift_moves, DBANK);
  );
  // --- 7700009 (2026-09-16): the Spread and cut pitch blocks, per slot, APPENDED. An older save
  //     keeps @init's defaults (Hz, fine tune 0 in Cents), and its High cut's off, 20000, becomes 0.
  ser_magic >= 7700009 ? (
    file_mem(0, slot_spmode, NSLOTS); file_mem(0, slot_spfunit, NSLOTS); file_mem(0, slot_spfine, NSLOTS);
    file_mem(0, slot_lcmode, NSLOTS); file_mem(0, slot_lcfunit, NSLOTS); file_mem(0, slot_lcfine, NSLOTS);
    file_mem(0, slot_hcmode, NSLOTS); file_mem(0, slot_hcfunit, NSLOTS); file_mem(0, slot_hcfine, NSLOTS);
  ) : file_avail(0) >= 0 ? (
    hco = 0; loop(NSLOTS, slot_hicut[hco] >= 19999.5 ? slot_hicut[hco] = 0; hco += 1; );
  );
""")
rep("      slider21 = slot_grain[cps]; slider44 = slot_hicut[cps]; slider11 = slot_tmunit[cps];\n    );\n",
    "      slider21 = slot_grain[cps]; slider44 = slot_hicut[cps]; slider11 = slot_tmunit[cps];\n    );\n"
    "    ser_magic >= 7700009 ? (\n"
    "      slider31 = slot_spmode[cps]; slider33 = slot_spfunit[cps]; slider34 = slot_spfine[cps];\n"
    "      slider37 = slot_lcmode[cps]; slider40 = slot_lcfunit[cps]; slider41 = slot_lcfine[cps];\n"
    "      slider42 = slot_hcmode[cps]; slider45 = slot_hcfunit[cps]; slider46 = slot_hcfine[cps];\n"
    "    );\n"
    "    tuning_ref = slider30 >= 20 ? slider30 : 440;\n"
    "    slider38 = cut_note(slider37, slider39); slider43 = cut_note(slider42, slider44);\n")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
