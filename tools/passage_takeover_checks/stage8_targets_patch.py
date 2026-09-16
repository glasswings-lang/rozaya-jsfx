"""Stage 8: the 111 Drift/Ramp targets in control order, per-target period and time units, the
new fine-tune and layer targets, Auto-morph rate as a target, Play for / Rest for latched per
stretch on With the target. Wash grain leaves the list. Bank stride 32 -> 128; an older blob (22
targets at stride 32) is remapped on load, and its one shared period/time unit seeds every target.
"""
p = r'C:/git-src/rozaya-jsfx/src/spectral_vowel_passage.jsfx'
s = open(p, encoding='utf-8', newline='').read()
CRLF = '\r\n' in s
s = s.replace('\r\n', '\n')


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:220])
    s = s.replace(a, b)


NAMES = (["Morph", "Auto-morph rate", "Slot fade in", "Slot hold", "Slot fade out", "Slot gap after", "Texture",
          "Pitch source fine tune", "Pitch transpose", "Pitch fine tune", "Tuning reference", "Spread",
          "Spread fine tune", "Stereo width", "Denoise", "Low cut", "Low cut fine tune", "High cut",
          "High cut fine tune", "Overtone harmonic", "Overtone lift", "Overtone width"]
         + [x for part in ("pitch", "fine tune", "level", "harmonics", "overtone harmonic")
            for x in [f"Layer {part} (all layers)"] + [f"Layer {k} {part}" for k in range(1, 17)]]
         + ["Input level", "Output level", "Play for", "Rest for"])
assert len(NAMES) == 111 and NAMES[22] == "Layer pitch (all layers)" and NAMES[90] == "Layer overtone harmonic (all layers)"
PICK = "{" + ",".join(NAMES) + "}"

# --- the pickers and the two unit labels
for sl in (68, 80):
    i = s.find(f"slider{sl}:0<0,21,1{{Transpose,")
    j = s.find("\n", i)
    label = "Drift target" if sl == 68 else "Ramp target"
    assert i >= 0
    s = s[:i] + f"slider{sl}:0<0,110,1{PICK}>{label}" + s[j:]
rep("slider72:1<0,2,1{Cycles,Seconds,Beats}>Drift period unit (all targets)", "slider72:1<0,2,1{Cycles,Seconds,Beats}>Drift period unit")
rep("slider83:2<0,3,1{Cycles,Seconds,Minutes,Beats}>Ramp time unit (all targets)", "slider83:2<0,3,1{Cycles,Seconds,Minutes,Beats}>Ramp time unit")

# --- constants
a = s.find("N_TARGETS = 22;")
b = s.find("TG_GLOBAL = 16;", a); b = s.find("\n", b) + 1
s = s[:a] + """N_TARGETS = 111; // Drift/Ramp targets in CONTROL ORDER (2026-09-16, docs/layouts/spectral-vowel-passage-takeover.md):
                 // 0 Morph, 1 Auto-morph rate, 2-5 the slot timings, 6 Texture, 7 Pitch source fine tune,
                 // 8 Pitch transpose, 9 Pitch fine tune, 10 Tuning reference, 11 Spread, 12 Spread fine tune,
                 // 13 Stereo width, 14 Denoise, 15 Low cut, 16 its fine tune, 17 High cut, 18 its fine tune,
                 // 19 Overtone harmonic, 20 Overtone lift, 21 Overtone width, then five layer families of
                 // (all layers) + 16 from 22, 107 Input level, 108 Output level, 109 Play for, 110 Rest for.
                 // Whole-plugin targets live in slot 0's row (tg_glob). A 22-target save is remapped
                 // (t111_o2n); Wash grain (old 3) left the list.
T_MORPH = 0; T_AMRATE = 1; T_FADEIN = 2; T_SRCFINE = 7; T_TRANS = 8; T_FINE = 9; T_TUNE = 10; T_SPREAD = 11;
T_SPFINE = 12; T_WIDTH = 13; T_DENOISE = 14; T_LOWCUT = 15; T_LCFINE = 16; T_HICUT = 17; T_HCFINE = 18;
T_OTH = 19; T_OTL = 20; T_OTW = 21; T_TEX = 6; T_INPUT = 107; T_OUTPUT = 108; T_PLAY = 109; T_REST = 110;
LP_T0 = 23; LF_T0 = 40; LEV_T0 = 57; LH_T0 = 74; LOT_T0 = 91;   // Layer 1's target in each family
""" + s[b:]
rep("DSTRIDE = 32;\nDBANK   = DSTRIDE * NSLOTS;\n", """DSTRIDE = 128;   // 32 until 2026-09-16 (22 targets); an older save is read at 32 and remapped
DBANK   = DSTRIDE * NSLOTS;
tg_glob = freemem; freemem += DSTRIDE;   // 1 = a whole-plugin target, held in slot 0's row
tg_used = freemem; freemem += DSTRIDE;   // 1 = a target a 22-target save could hold
target_drift_punit = freemem; freemem += DBANK;   // CONFIG: Drift period unit, per (slot, target), since 2026-09-16
ramp_tunit         = freemem; freemem += DBANK;   // CONFIG: Ramp time unit, likewise
lay_nh_eff = freemem; freemem += 16; lay_ot_eff = freemem; freemem += 16; lay_ot_last = freemem; freemem += 16;
""")

# --- remap helpers and the drift loop's order
a = s.find("// A 14-target save's index, in the 22-target list.")
b = s.find("// Seconds per Drift period unit and per Ramp time unit")
assert a > 0 and b > a
s = s[:a] + """// A 14-target save's index, in the 22-target list.
function tg_o2n(o) (
  o == 0 ? 2 : o == 1 ? 4 : o == 2 ? 0 : o == 3 ? 14 : o == 4 ? 6 : o == 5 ? 15 :
  o == 6 ? 5 : o == 7 ? 18 : o == 8 ? 19 : o == 9 ? 8 : o;
);
// Move a bank saved at stride 16 in the old order (nsl slots, ntg targets each) into the 22-target
// layout at stride 32, which t111_remap then carries into this one; everything else takes dflt.
function tg_remap(bank, dflt, nsl, ntg) local(k, s, t) (
  k = 0; loop(nsl * 16, ser_scratch[k] = bank[k]; k += 1;);
  k = 0; loop(DBANK, bank[k] = dflt; k += 1;);
  s = 0; loop(nsl, t = 0; loop(ntg, bank[s*32 + tg_o2n(t)] = ser_scratch[s*16 + t]; t += 1;); s += 1;);
);
// A 22-target save's index (2026-09-12 to 09-16), in the 111 list; -1 for Wash grain, which left.
function t111_o2n(o) (
  o == 0 ? 8 : o == 1 ? 9 : o == 2 ? 6 : o == 3 ? -1 : o == 4 ? 11 : o == 5 ? 14 : o == 6 ? 15 :
  o == 7 ? 17 : o == 8 ? 19 : o == 9 ? 20 : o <= 13 ? o - 8 : o == 14 ? 13 : o == 15 ? 108 :
  o == 16 ? 10 : o == 17 ? 21 : o == 18 ? 0 : o == 19 ? 107 : o == 20 ? 109 : 110;
);
// Carry a bank held in the 22-target layout (stride 32) into this one.
function t111_remap(bank, dflt) local(k, s, t, n) (
  k = 0; loop(NSLOTS * 32, ser_scratch[k] = bank[k]; k += 1;);
  k = 0; loop(DBANK, bank[k] = dflt; k += 1;);
  s = 0; loop(NSLOTS, t = 0; loop(22, n = t111_o2n(t); n >= 0 ? bank[s*DSTRIDE + n] = ser_scratch[s*32 + t]; t += 1;); s += 1;);
);
function tg_is_all(t) ( t == 22 || t == 39 || t == 56 || t == 73 || t == 90; );
function tg_moves_dflt(t) ( (t >= 2 && t <= 5) || t == T_PLAY || t == T_REST ? 0 : 1; );   // With the target / On a clock
dro_i = 0; loop(DSTRIDE, tg_glob[dro_i] = dro_i <= 1 || dro_i == 10 || (dro_i >= 21 && dro_i <= 107) || dro_i >= 109; tg_used[dro_i] = 0; dro_i += 1; );
dro_i = 0; loop(22, t111_o2n(dro_i) >= 0 ? tg_used[t111_o2n(dro_i)] = 1; dro_i += 1; );
// THE DRIFT LOOP VISITS THE OLD FOURTEEN TARGETS FIRST, slot by slot in their old order, then the
// rest of the old twenty-two in theirs, then the new ones. Random drift draws rand(), one stream, so
// two targets wrapping on one sample must draw in the order they always did (the Morpher's rule).
dro_k = 0; dro_s = 0;
loop(NSLOTS, dro_t = 0; loop(14, dr_order[dro_k] = dro_s*DSTRIDE + t111_o2n(tg_o2n(dro_t)); dro_k += 1; dro_t += 1;); dro_s += 1;);
dro_s = 0;
loop(NSLOTS,
  dro_t = 0;
  loop(22,
    dro_old = 0; dro_j = 0; loop(14, tg_o2n(dro_j) == dro_t ? dro_old = 1; dro_j += 1;);
    (!dro_old && t111_o2n(dro_t) >= 0) ? ( dr_order[dro_k] = dro_s*DSTRIDE + t111_o2n(dro_t); dro_k += 1; );
    dro_t += 1;
  );
  dro_s += 1;
);
dro_s = 0;
loop(NSLOTS, dro_t = 0; loop(DSTRIDE, !tg_used[dro_t] ? ( dr_order[dro_k] = dro_s*DSTRIDE + dro_t; dro_k += 1; ); dro_t += 1;); dro_s += 1;);
""" + s[b:]

# --- @init defaults
rep("""    target_drift_moves[i] = (i % DSTRIDE) >= 10 && (i % DSTRIDE) <= 13 ? 0 : 1;   // slot timings with the target""",
"""    target_drift_moves[i] = tg_moves_dflt(i % DSTRIDE);   // slot timings and Play for / Rest for with the target
    target_drift_punit[i] = 1; ramp_tunit[i] = 2;   // Seconds, Minutes: the sliders' own defaults""")

# --- units per target in @block
rep("""slider83 == 3 && rm_tempo > 0 && rm_tnow != rm_tempo ? (
  rdi = 0;
  loop(DBANK,
    ramp_delay_elapsed_mem[rdi] < ramp_delay_mem[rdi] * 60 / rm_tempo * srate ? ramp_delay_elapsed_mem[rdi] *= rm_tempo / rm_tnow;
    rdi += 1;
  );
);""", """rm_tempo > 0 && rm_tnow != rm_tempo ? (
  rdi = 0;
  loop(DBANK,
    ramp_tunit[rdi] == 3 && ramp_delay_elapsed_mem[rdi] < ramp_delay_mem[rdi] * 60 / rm_tempo * srate ? ramp_delay_elapsed_mem[rdi] *= rm_tempo / rm_tnow;
    rdi += 1;
  );
);""")
rep("""drift_unit_sec = slider72 == 0 ? pv_cyc : slider72 == 1 ? 1 : 60 / max(tempo, 0.001);
ramp_unit_sec  = slider83 == 0 ? pv_cyc : slider83 == 1 ? 1 : slider83 == 2 ? 60 : 60 / max(tempo, 0.001);""",
"""// Per target since 2026-09-16: a save older than that held one unit for every target, so each
// target starts on it (units_seed, set in @serialize, read here once the sliders are in).
units_seed ? ( units_seed = 0; usd = 0; loop(DBANK, target_drift_punit[usd] = slider72; ramp_tunit[usd] = slider83; usd += 1; ); );""")
rep("function pr_frozen(accum_bank, resting_bank, idx, tick, play, rest) (",
"""function du_sec(u) ( u == 0 ? pv_cyc : u == 1 ? 1 : 60 / max(tempo, 0.001); );
function ru_sec(u) ( u == 0 ? pv_cyc : u == 1 ? 1 : u == 2 ? 60 : 60 / max(tempo, 0.001); );
function pr_frozen(accum_bank, resting_bank, idx, tick, play, rest) (""")
rep("    dper = target_drift_per[di] * drift_unit_sec;", "    dper = target_drift_per[di] * du_sec(target_drift_punit[di]);")
rep("    dtick = (target_drift_moves[di] == 0 && dtg >= 10 && dtg <= 13)", "    dtick = (target_drift_moves[di] == 0 && dtg >= 2 && dtg <= 5)")
rep("      rdelay_samps = ramp_delay_mem[ri] * ramp_unit_sec * srate;", "      ramp_unit_sec = ru_sec(ramp_tunit[ri]);\n      rdelay_samps = ramp_delay_mem[ri] * ramp_unit_sec * srate;")

# --- Wash grain is no longer a target
rep("""// Wash grain as a Drift/Ramp target (3), read once a block: it rebuilds a window.
(mod_active[sb_i*DSTRIDE + 3] || mod_active[sb_j*DSTRIDE + 3]) ? grain_ms = max(5, min(1000, grain_ms + dmodc(3, 3, slot_grain, 3)));
""", "")

# --- consumers renumbered
rep("mod_active[20] ? max(0.001, slider64 + au_key(20, 3, slider64, slider62))", "mod_active[T_PLAY] ? max(0.001, slider64 + au_key(T_PLAY, 3, slider64, slider62))")
rep("mod_active[21] ? max(0.001, slider65 + au_key(21, 3, slider65, slider62))", "mod_active[T_REST] ? max(0.001, slider65 + au_key(T_REST, 3, slider65, slider62))")
rep("eff_morph01 = mod_active[18] ? max(0, min(1, morph01 + (target_drift_offset[18] + ramp_offset_mem[18]) * 0.01)) : morph01;",
    "eff_morph01 = mod_active[T_MORPH] ? max(0, min(1, morph01 + (target_drift_offset[T_MORPH] + ramp_offset_mem[T_MORPH]) * 0.01)) : morph01;")
rep("                        + (dmod(2)) * 0.01));", "                        + (dmod(T_TEX)) * 0.01));")
rep("                                  + dmodc(4, 2, slot_spread, srate / FFTSIZE)));", "                                  + dmodc(T_SPREAD, 2, slot_spread, srate / FFTSIZE)));")
rep("au_key(sp_sl*DSTRIDE + 4, 2, slot_spread[sp_sl], srate / FFTSIZE)", "au_key(sp_sl*DSTRIDE + T_SPREAD, 2, slot_spread[sp_sl], srate / FFTSIZE)")
rep("sp_q(sp_sl*DSTRIDE + 4, sp_m)", "sp_q(sp_sl*DSTRIDE + T_SPREAD, sp_m)")
rep("pitch_mod_A = au_key(sb_i*DSTRIDE + 0, 1,", "pitch_mod_A = au_key(sb_i*DSTRIDE + T_TRANS, 1,")
rep("pitch_mod_B = au_key(sb_j*DSTRIDE + 0, 1,", "pitch_mod_B = au_key(sb_j*DSTRIDE + T_TRANS, 1,")
rep("fine_mod_A  = au_key(sb_i*DSTRIDE + 1, 1,", "fine_mod_A  = au_key(sb_i*DSTRIDE + T_FINE, 1,")
rep("fine_mod_B  = au_key(sb_j*DSTRIDE + 1, 1,", "fine_mod_B  = au_key(sb_j*DSTRIDE + T_FINE, 1,")
rep("tuning_ref = mod_active[16] ? max(20, min(2000, tuning_base + au_key(16, 2, tuning_base, 20))) : tuning_base;",
    "tuning_ref = mod_active[T_TUNE] ? max(20, min(2000, tuning_base + au_key(T_TUNE, 2, tuning_base, 20))) : tuning_base;")
rep("                                   + dmod(14)));", "                                   + dmod(T_WIDTH)));")
rep("au_key(sb_i*DSTRIDE + 7, 2, slot_hicut[sb_i], 20)", "au_key(sb_i*DSTRIDE + T_HICUT, 2, slot_hicut[sb_i], 20)")
rep("au_key(sb_j*DSTRIDE + 7, 2, slot_hicut[sb_j], 20)", "au_key(sb_j*DSTRIDE + T_HICUT, 2, slot_hicut[sb_j], 20)")
rep("au_key(sb_i*DSTRIDE + 6, 2, slot_lowcut[sb_i], 20)", "au_key(sb_i*DSTRIDE + T_LOWCUT, 2, slot_lowcut[sb_i], 20)")
rep("au_key(sb_j*DSTRIDE + 6, 2, slot_lowcut[sb_j], 20)", "au_key(sb_j*DSTRIDE + T_LOWCUT, 2, slot_lowcut[sb_j], 20)")
rep("cut_slot_hz(sb_i, 7, ", "cut_slot_hz(sb_i, T_HICUT, ")
rep("cut_slot_hz(sb_j, 7, ", "cut_slot_hz(sb_j, T_HICUT, ")
rep("cut_slot_hz(sb_i, 6, ", "cut_slot_hz(sb_i, T_LOWCUT, ")
rep("cut_slot_hz(sb_j, 6, ", "cut_slot_hz(sb_j, T_LOWCUT, ")
rep("                           + dmod(15)));", "                           + dmod(T_OUTPUT)));")
rep("                              + dmod(5)));", "                              + dmod(T_DENOISE)));")
rep("""mod_active[19] ? (
  eff_dry_db = max(-60, min(24, dry_db_base + target_drift_offset[19] + ramp_offset_mem[19]));""",
"""mod_active[T_INPUT] ? (
  eff_dry_db = max(-60, min(24, dry_db_base + target_drift_offset[T_INPUT] + ramp_offset_mem[T_INPUT]));""")
rep("(mod_active[sb_i*DSTRIDE + 9] ? max(0, min(48, slot_ot_depth[sb_i] + mo_q(sb_i*DSTRIDE + 9)))",
    "(mod_active[sb_i*DSTRIDE + T_OTL] ? max(0, min(48, slot_ot_depth[sb_i] + mo_q(sb_i*DSTRIDE + T_OTL)))")
rep("(mod_active[sb_j*DSTRIDE + 9] ? max(0, min(48, slot_ot_depth[sb_j] + mo_q(sb_j*DSTRIDE + 9)))",
    "(mod_active[sb_j*DSTRIDE + T_OTL] ? max(0, min(48, slot_ot_depth[sb_j] + mo_q(sb_j*DSTRIDE + T_OTL)))")
rep("eff_ot_h = max(0, min(NHARM, ot_harm_base + dmod(8)));", "eff_ot_h = max(0, min(NHARM, ot_harm_base + dmod(T_OTH)));")
rep("ot_w_eff = mod_active[17] ? max(0.5, min(4, ot_width + mo_q(17))) : ot_width;   // Overtone width (17)",
    "ot_w_eff = mod_active[T_OTW] ? max(0.5, min(4, ot_width + mo_q(T_OTW))) : ot_width;   // Overtone width")
rep("""        lgo_fi = au_key(lgk + 10, 3,""", """        lgo_fi = au_key(lgk + 2, 3,""")
rep("""        lgo_h  = au_key(lgk + 11, 3,""", """        lgo_h  = au_key(lgk + 3, 3,""")
rep("""        lgo_fo = au_key(lgk + 12, 3,""", """        lgo_fo = au_key(lgk + 4, 3,""")
rep("""        lgo_g  = au_key(lgk + 13, 3,""", """        lgo_g  = au_key(lgk + 5, 3,""")
rep("lg_sk = 10; loop(4, td_active[lgk + lg_sk]", "lg_sk = 2; loop(4, td_active[lgk + lg_sk]")

# --- the new fine-tune targets on Spread and the cuts
rep("(slot_spmode[sb_i] == 0 && slot_spmode[sb_j] == 0 && slot_spfine[sb_i] == 0 && slot_spfine[sb_j] == 0) ? (",
    "(slot_spmode[sb_i] == 0 && slot_spmode[sb_j] == 0 && slot_spfine[sb_i] == 0 && slot_spfine[sb_j] == 0 &&\n !mod_active[sb_i*DSTRIDE + T_SPFINE] && !mod_active[sb_j*DSTRIDE + T_SPFINE]) ? (")
rep("    sp_m = slot_spmode[sp_sl]; sp_fu = slot_spfunit[sp_sl]; sp_fn = slot_spfine[sp_sl];",
    "    sp_m = slot_spmode[sp_sl]; sp_fu = slot_spfunit[sp_sl]; sp_fn = slot_spfine[sp_sl];\n"
    "    mod_active[sp_sl*DSTRIDE + T_SPFINE] ? sp_fn += sp_q(sp_sl*DSTRIDE + T_SPFINE, sp_fu);")
rep("(slot_hcmode[sb_i] == 0 && slot_hcmode[sb_j] == 0 && slot_hcfine[sb_i] == 0 && slot_hcfine[sb_j] == 0) ? (",
    "(slot_hcmode[sb_i] == 0 && slot_hcmode[sb_j] == 0 && slot_hcfine[sb_i] == 0 && slot_hcfine[sb_j] == 0 &&\n !mod_active[sb_i*DSTRIDE + T_HCFINE] && !mod_active[sb_j*DSTRIDE + T_HCFINE]) ? (")
rep("(slot_lcmode[sb_i] == 0 && slot_lcmode[sb_j] == 0 && slot_lcfine[sb_i] == 0 && slot_lcfine[sb_j] == 0) ? (",
    "(slot_lcmode[sb_i] == 0 && slot_lcmode[sb_j] == 0 && slot_lcfine[sb_i] == 0 && slot_lcfine[sb_j] == 0 &&\n !mod_active[sb_i*DSTRIDE + T_LCFINE] && !mod_active[sb_j*DSTRIDE + T_LCFINE]) ? (")
rep("""    fine != 0 ? hz = cut_fine(hz, fine, funit);""",
"""    fine = fine + (mod_active[sl*DSTRIDE + tgt + 1] ? sp_q(sl*DSTRIDE + tgt + 1, funit) : 0);   // its fine tune target follows it
    fine != 0 ? hz = cut_fine(hz, fine, funit);""")

# --- Pitch source fine tune: moves what the Target note lands on, only while that link is live
rep("eff_semi_B = pv_semis(slot_tunit[sb_j], slot_pitch[sb_j] + pitch_mod_B) + pv_semis(slot_funit[sb_j], slot_fine[sb_j] + fine_mod_B);\n",
"""eff_semi_B = pv_semis(slot_tunit[sb_j], slot_pitch[sb_j] + pitch_mod_B) + pv_semis(slot_funit[sb_j], slot_fine[sb_j] + fine_mod_B);
// Pitch source fine tune (7), 2026-09-16, the Morpher's: it says where the capture's note sits, so a
// drift on it moves what the Target note lands on -- heard only while a slot has a Source note and
// Transpose in Semitones, and the sound moves the OPPOSITE way to the drift.
(mod_active[sb_i*DSTRIDE + T_SRCFINE] && slot_srcnote[sb_i] > 0 && slot_tunit[sb_i] == 1) ? eff_semi_A -=
  pv_src_semis(slot_srcnote[sb_i], slot_srcfunit[sb_i], slot_srcfine[sb_i] + au_key(sb_i*DSTRIDE + T_SRCFINE, 1, slot_srcfine[sb_i], slot_srcfunit[sb_i]))
  - pv_src_semis(slot_srcnote[sb_i], slot_srcfunit[sb_i], slot_srcfine[sb_i]);
(mod_active[sb_j*DSTRIDE + T_SRCFINE] && slot_srcnote[sb_j] > 0 && slot_tunit[sb_j] == 1) ? eff_semi_B -=
  pv_src_semis(slot_srcnote[sb_j], slot_srcfunit[sb_j], slot_srcfine[sb_j] + au_key(sb_j*DSTRIDE + T_SRCFINE, 1, slot_srcfine[sb_j], slot_srcfunit[sb_j]))
  - pv_src_semis(slot_srcnote[sb_j], slot_srcfunit[sb_j], slot_srcfine[sb_j]);
""")

# --- Auto-morph rate (1), in its rate mode's unit
rep("function du_sec(u)", """function au_rate(off, u, base, mode) local(beat, b, tt, rate) (
  beat = 60 / max(tempo, 0.001);
  !(u == 1 || (u >= 4 && u <= 9)) || (u == 7 && mode == 0) || (u == 5 && mode == 1) || (u == 1 && mode == 2) || (u == 8 && mode == 3) ? off : (
    b = mode == 0 ? 60 / max(base, 0.001) : mode == 1 ? base : mode == 2 ? 1 / max(base, 0.001) : mode == 3 ? base * beat : beat / max(base, 0.001);
    u == 1 || u == 7 ? (
      rate = 1 / max(b, 0.000001) + (u == 7 ? off / 60 : off);
      tt = rate > 0.000001 ? 1 / rate : 1000000;
    ) : (
      tt = b + (u == 4 ? off / 1000 : u == 5 ? off : u == 6 ? off * 60 : u == 8 ? off * beat : off * max(pv_cyc, 0.05));
    );
    tt = max(tt, 0.000001);
    (mode == 0 ? 60 / tt : mode == 1 ? tt : mode == 2 ? 1 / tt : mode == 3 ? tt / beat : beat / tt) - base;
  );
);
function du_sec(u)""")
rep("""auto_time = max(0.01,
  am_rmode == 0 ? 60 / max(am_rval, 0.001) :
  am_rmode == 1 ? am_rval :
  am_rmode == 2 ? 1 / max(am_rval, 0.001) :
  am_rmode == 3 ? am_rval * 60 / max(tempo, 0.001) :
                  (60 / max(tempo, 0.001)) / am_rval);
(automorph_mode > 0.5 && am_timing == 1) ? pv_cyc = auto_time;
""", """auto_time = max(0.01,
  am_rmode == 0 ? 60 / max(am_rval, 0.001) :
  am_rmode == 1 ? am_rval :
  am_rmode == 2 ? 1 / max(am_rval, 0.001) :
  am_rmode == 3 ? am_rval * 60 / max(tempo, 0.001) :
                  (60 / max(tempo, 0.001)) / am_rval);
(automorph_mode > 0.5 && am_timing == 1) ? pv_cyc = auto_time;   // a Cycle: one pass, without its own drift
mod_active[T_AMRATE] ? (
  am_rv = max(0.01, am_rval + au_key(T_AMRATE, 4, am_rval, am_rmode));
  auto_time = max(0.01,
    am_rmode == 0 ? 60 / max(am_rv, 0.001) : am_rmode == 1 ? am_rv : am_rmode == 2 ? 1 / max(am_rv, 0.001) :
    am_rmode == 3 ? am_rv * 60 / max(tempo, 0.001) : (60 / max(tempo, 0.001)) / am_rv);
);
""")
rep("function au_key(k, kind, base, nu) (\n  (target_drift_unit[k] == 0 && ramp_by_unit[k] == 0) || kind < 1 || kind > 3 ? mo_q(k) :",
    "function au_key(k, kind, base, nu) (\n  (target_drift_unit[k] == 0 && ramp_by_unit[k] == 0) || kind < 1 || kind > 4 ? mo_q(k) :")
rep("              au_time(target_drift_offset[k], target_drift_unit[k], base, nu) + au_time(ramp_offset_mem[k], ramp_by_unit[k], base, nu);\n);",
    "  kind == 3 ? au_time(target_drift_offset[k], target_drift_unit[k], base, nu) + au_time(ramp_offset_mem[k], ramp_by_unit[k], base, nu) :\n"
    "              au_rate(target_drift_offset[k], target_drift_unit[k], base, nu) + au_rate(ramp_offset_mem[k], ramp_by_unit[k], base, nu);\n);")

# --- layers take their targets, once a block
rep("""  layer_ratio[lz] = pow(2.0, (pv_semis(lay_punit[lz], lay_semi[lz]) + pv_semis(lay_funit[lz], lay_fine[lz])) / 12);
  lay_aud = lay_any_solo ? (lay_solo[lz] >= 0.5) : (lay_active[lz] >= 0.5);
  layer_gain[lz] = (lay_aud < 0.5 || lay_db[lz] <= -60) ? 0 : pow(10, lay_db[lz] / 20);""",
"""  layer_ratio[lz] = pow(2.0, (pv_semis(lay_punit[lz], lay_semi[lz] + (mod_active[LP_T0+lz] ? au_key(LP_T0+lz, 1, lay_semi[lz], lay_punit[lz]) : 0))
                           + pv_semis(lay_funit[lz], lay_fine[lz] + (mod_active[LF_T0+lz] ? au_key(LF_T0+lz, 1, lay_fine[lz], lay_funit[lz]) : 0))) / 12);
  lay_aud = lay_any_solo ? (lay_solo[lz] >= 0.5) : (lay_active[lz] >= 0.5);
  lay_edb = mod_active[LEV_T0+lz] ? max(-60, min(24, lay_db[lz] + mo_q(LEV_T0+lz))) : lay_db[lz];
  layer_gain[lz] = (lay_aud < 0.5 || lay_edb <= -60) ? 0 : pow(10, lay_edb / 20);
  lay_nh_eff[lz] = mod_active[LH_T0+lz] ? max(0, min(64, floor(lay_nharm[lz] + mo_q(LH_T0+lz) + 0.5))) : lay_nharm[lz];
  lay_ot_eff[lz] = (lay_ot_harm[lz] >= 0 && mod_active[LOT_T0+lz]) ? max(0, min(NHARM, lay_ot_harm[lz] + mo_q(LOT_T0+lz))) : lay_ot_harm[lz];
  lay_ot_eff[lz] != lay_ot_last[lz] ? ( lay_ot_last[lz] = lay_ot_eff[lz]; lay_ot_dirty = 1; );""")
rep("  (lz > 0 && layer_gain[lz] > 0.0001) ? ( nlay_on = 1; lay_ot_harm[lz] >= 0 ? lay_ot_any = 1; );",
    "  (lz > 0 && layer_gain[lz] > 0.0001) ? ( nlay_on = 1; lay_ot_eff[lz] >= 0 ? lay_ot_any = 1; );")
rep("lay_ot_harm[0] >= 0 && layer_gain[0] > 0.0001 ? lay_ot_any = 1;", "lay_ot_eff[0] >= 0 && layer_gain[0] > 0.0001 ? lay_ot_any = 1;")
# the voice and wash read the effective layer values
rep("  lk = floor(p / 2); cap = lay_nharm[lk]; cap <= 0 ? cap = NHARM;\n  og = (lay_ot_harm[lk] >= 0 && ot_on) ? lay_ot_gain + lk*NHARM : ot_gain;",
    "  lk = floor(p / 2); cap = lay_nh_eff[lk]; cap <= 0 ? cap = NHARM;\n  og = (lay_ot_eff[lk] >= 0 && ot_on) ? lay_ot_gain + lk*NHARM : ot_gain;")
rep("wt_cap[p] = lay_nharm[lk];", "wt_cap[p] = lay_nh_eff[lk];")
rep("function wt_otver(lk) ( (lay_ot_harm[lk] >= 0 && ot_on)", "function wt_otver(lk) ( (lay_ot_eff[lk] >= 0 && ot_on)")
rep("wt_cap[p] != lay_nharm[floor(p / 2)]", "wt_cap[p] != lay_nh_eff[floor(p / 2)]")
rep("""      lay_ot_harm[lok] >= 0 ? (
        lobo = lok*NHARM;
        oi = 0; loop(NHARM, lay_ot_gain[lobo+oi] = 1; oi += 1; );
        lay_ot_harm[lok] > 0 ? (
          olo = max(1, ceil(lay_ot_harm[lok] - otw));
          ohi = min(NHARM, floor(lay_ot_harm[lok] + otw));
          oi = olo;
          loop(max(0, ohi - olo + 1),
            od = abs(oi - lay_ot_harm[lok]) / otw;""", """      lay_ot_eff[lok] >= 0 ? (
        lobo = lok*NHARM;
        oi = 0; loop(NHARM, lay_ot_gain[lobo+oi] = 1; oi += 1; );
        lay_ot_eff[lok] > 0 ? (
          olo = max(1, ceil(lay_ot_eff[lok] - otw));
          ohi = min(NHARM, floor(lay_ot_eff[lok] + otw));
          oi = olo;
          loop(max(0, ohi - olo + 1),
            od = abs(oi - lay_ot_eff[lok]) / otw;""")
rep("    lay_ot_pre && lay_ot_harm[0] >= 0 ? m = wash_own_ot(0, srcb) * GINV;", "    lay_ot_pre && lay_ot_eff[0] >= 0 ? m = wash_own_ot(0, srcb) * GINV;")
rep("            lay_ot_pre && lay_ot_harm[lq] >= 0 ? ( lm = wash_own_ot(lq, srcb); ) : (", "            lay_ot_pre && lay_ot_eff[lq] >= 0 ? ( lm = wash_own_ot(lq, srcb); ) : (")
rep("  lb = ot_f0mix * lay_ot_harm[lk] * ot_bpf;\n  (lay_ot_harm[lk] > 0 &&", "  lb = ot_f0mix * lay_ot_eff[lk] * ot_bpf;\n  (lay_ot_eff[lk] > 0 &&")
rep("i = 0; loop(16, layer_ratio[i] = 1; layer_gain[i] = i == 0; i += 1; );",
    "i = 0; loop(16, layer_ratio[i] = 1; layer_gain[i] = i == 0; lay_nh_eff[i] = 0; lay_ot_eff[i] = -1; lay_ot_last[i] = -1; i += 1; );")

# --- Play for / Rest for keep their stretch's length on With the target
rep("""  pr_enabled ? (
    pr_accum += 1 / srate;
    pr_accum >= (pr_resting ? pr_rest_sec : pr_play_sec) ? (""", """  pr_enabled ? (
    // Drift movement mode (2026-09-16, the Morpher's): With the target, a stretch keeps the length it
    // began with; On a clock, it is read live.
    (pr_accum == 0 || !pr_len_set || target_drift_moves[T_PLAY] == 1) ? pr_play_lat = pr_play_sec;
    (pr_accum == 0 || !pr_len_set || target_drift_moves[T_REST] == 1) ? pr_rest_lat = pr_rest_sec;
    pr_len_set = 1;
    pr_accum += 1 / srate;
    pr_accum >= (pr_resting ? pr_rest_lat : pr_play_lat) ? (""")

# --- @slider: the pickers, whole-plugin targets, the (all layers) entries, per-target units
rep("dsel_slot = sel_target >= TG_GLOBAL ? 0 : cap_slot;\ndkey      = dsel_slot*DSTRIDE + sel_target;",
    "dsel_slot = tg_glob[sel_target] ? 0 : cap_slot;\ndkey      = dsel_slot*DSTRIDE + sel_target;\n"
    "dread     = tg_is_all(sel_target) ? dkey + 1 : dkey;   // an (all layers) entry shows Layer 1's and writes all sixteen")
rep("sel_move   = slider74;\n", "sel_move   = slider74;\nsel_punit  = slider72;\n")
rep("""last_drift_key != dkey ? (
  target_drift_up[last_drift_key]    = sel_up;""", """last_drift_key != dkey ? (
  !tg_is_all(last_drift_key % DSTRIDE) ? (
  target_drift_up[last_drift_key]    = sel_up;""")
rep("""  target_drift_moves[last_drift_key] = sel_move;
  slider70 = target_drift_up[dkey];
  slider71 = target_drift_down[dkey];
  slider73 = target_drift_per[dkey];
  slider75 = target_drift_shape[dkey];
  slider76 = target_drift_play[dkey]; slider77 = target_drift_rest[dkey];
  slider69 = target_drift_unit[dkey];
  slider74 = target_drift_moves[dkey];""", """  target_drift_moves[last_drift_key] = sel_move;
  target_drift_punit[last_drift_key] = sel_punit;
  );
  slider70 = target_drift_up[dread];
  slider71 = target_drift_down[dread];
  slider73 = target_drift_per[dread];
  slider75 = target_drift_shape[dread];
  slider76 = target_drift_play[dread]; slider77 = target_drift_rest[dread];
  slider69 = target_drift_unit[dread];
  slider74 = target_drift_moves[dread];
  slider72 = target_drift_punit[dread]; slider_automate(slider72);""")
rep("""  (cap_all && ps_inited && sel_target < TG_GLOBAL) ? (
    ps_all_key(20, sel_up,    sel_target, target_drift_up);""", """  tg_is_all(sel_target) ? (
    ps_inited ? (
      lay_all_key(20, sel_up, sel_target, target_drift_up); lay_all_key(21, sel_down, sel_target, target_drift_down);
      lay_all_key(22, sel_per, sel_target, target_drift_per); lay_all_key(23, sel_shape, sel_target, target_drift_shape);
      lay_all_key(27, sel_play, sel_target, target_drift_play); lay_all_key(28, sel_rest, sel_target, target_drift_rest);
      lay_all_key(42, sel_unit, sel_target, target_drift_unit); lay_all_key(31, sel_move, sel_target, target_drift_moves);
      lay_all_key(53, sel_punit, sel_target, target_drift_punit);
    );
  ) : (cap_all && ps_inited && !tg_glob[sel_target]) ? (
    ps_all_key(53, sel_punit, sel_target, target_drift_punit);
    ps_all_key(20, sel_up,    sel_target, target_drift_up);""")
rep("""    ps_last[27] = sel_play; ps_last[28] = sel_rest; ps_last[42] = sel_unit; ps_last[31] = sel_move;
  );
  target_drift_up[dkey]    = sel_up;""", """    ps_last[27] = sel_play; ps_last[28] = sel_rest; ps_last[42] = sel_unit; ps_last[31] = sel_move; ps_last[53] = sel_punit;
  );
  !tg_is_all(sel_target) ? (
  target_drift_punit[dkey] = sel_punit;
  target_drift_up[dkey]    = sel_up;""")
rep("""  target_drift_moves[dkey] = sel_move;
);""", """  target_drift_moves[dkey] = sel_move;
  );
);""")
rep("rsel_slot = rsel_target >= TG_GLOBAL ? 0 : cap_slot;\nrkey      = rsel_slot*DSTRIDE + rsel_target;",
    "rsel_slot = tg_glob[rsel_target] ? 0 : cap_slot;\nrkey      = rsel_slot*DSTRIDE + rsel_target;\nrread     = tg_is_all(rsel_target) ? rkey + 1 : rkey;")
rep("rsel_unit   = slider81;\n", "rsel_unit   = slider81;\nrsel_tunit  = slider83;\n")
rep("""last_ramp_key != rkey ? (
  ramp_by_mem[last_ramp_key]    = rsel_by;""", """last_ramp_key != rkey ? (
  !tg_is_all(last_ramp_key % DSTRIDE) ? (
  ramp_tunit[last_ramp_key] = rsel_tunit;
  ramp_by_mem[last_ramp_key]    = rsel_by;""")
rep("""  ramp_by_unit[last_ramp_key] = rsel_unit;
  slider82 = ramp_by_mem[rkey];
  slider84 = ramp_dur_mem[rkey];
  slider89 = ramp_delay_mem[rkey];
  slider85 = ramp_play_mem[rkey]; slider86 = ramp_rest_mem[rkey];
  slider81 = ramp_by_unit[rkey];""", """  ramp_by_unit[last_ramp_key] = rsel_unit;
  );
  slider82 = ramp_by_mem[rread];
  slider84 = ramp_dur_mem[rread];
  slider89 = ramp_delay_mem[rread];
  slider85 = ramp_play_mem[rread]; slider86 = ramp_rest_mem[rread];
  slider81 = ramp_by_unit[rread];
  slider83 = ramp_tunit[rread]; slider_automate(slider83);""")
rep("""  (cap_all && ps_inited && rsel_target < TG_GLOBAL) ? (
    ps_all_key(24, rsel_by,    rsel_target, ramp_by_mem);""", """  tg_is_all(rsel_target) ? (
    ps_inited ? (
      lay_all_key(24, rsel_by, rsel_target, ramp_by_mem); lay_all_key(25, rsel_dur, rsel_target, ramp_dur_mem);
      lay_all_key(26, rsel_delay, rsel_target, ramp_delay_mem); lay_all_key(29, rsel_play, rsel_target, ramp_play_mem);
      lay_all_key(30, rsel_rest, rsel_target, ramp_rest_mem); lay_all_key(43, rsel_unit, rsel_target, ramp_by_unit);
      lay_all_key(54, rsel_tunit, rsel_target, ramp_tunit);
    );
  ) : (cap_all && ps_inited && !tg_glob[rsel_target]) ? (
    ps_all_key(54, rsel_tunit, rsel_target, ramp_tunit);
    ps_all_key(24, rsel_by,    rsel_target, ramp_by_mem);""")
rep("""    ps_last[29] = rsel_play; ps_last[30] = rsel_rest; ps_last[43] = rsel_unit;
  );
  ramp_by_mem[rkey]    = rsel_by;""", """    ps_last[29] = rsel_play; ps_last[30] = rsel_rest; ps_last[43] = rsel_unit; ps_last[54] = rsel_tunit;
  );
  !tg_is_all(rsel_target) ? (
  ramp_tunit[rkey] = rsel_tunit;
  ramp_by_mem[rkey]    = rsel_by;""")
i = s.find("  ramp_by_unit[rkey] = rsel_unit;\n")
assert i > 0 and s.count("  ramp_by_unit[rkey] = rsel_unit;\n") == 1
j = s.find(");", i)
s = s[:j] + ");\n" + s[j:]
rep("function ps_all_key(k, raw, tgt, bank) local(pa) (",
"""// An (all layers) entry: a Drift or Ramp setting moved reaches that family's sixteen layer targets.
function lay_all_key(k, raw, tgt, bank) local(la) (
  raw != ps_last[k] ? ( la = 1; loop(16, bank[tgt + la] = raw; la += 1; ); ps_last[k] = raw; );
);
function ps_all_key(k, raw, tgt, bank) local(pa) (""")
rep("  ps_last[42] = slider69; ps_last[43] = slider81; ps_last[31] = slider74;\n",
    "  ps_last[42] = slider69; ps_last[43] = slider81; ps_last[31] = slider74; ps_last[53] = slider72; ps_last[54] = slider83;\n")

# --- @serialize: read older layouts at their own stride and carry them over
rep("  n_ser_targets = ser_magic >= 7700007 ? DBANK : ser_magic == 7700006 ? NSLOTS * 16 :",
    "  ser_nb        = ser_magic >= 7700009 ? DBANK : NSLOTS * 32;   // a 22-target save: stride 32\n"
    "  n_ser_targets = ser_magic >= 7700009 ? DBANK : ser_magic >= 7700007 ? NSLOTS * 32 : ser_magic == 7700006 ? NSLOTS * 16 :")
rep("""      loop(DSTRIDE,
        target_drift_up[mgs*DSTRIDE + mgt]    = target_drift_up[mgt];
        target_drift_down[mgs*DSTRIDE + mgt]  = target_drift_down[mgt];
        target_drift_per[mgs*DSTRIDE + mgt]   = target_drift_per[mgt];
        target_drift_shape[mgs*DSTRIDE + mgt] = target_drift_shape[mgt];
        ramp_by_mem[mgs*DSTRIDE + mgt]        = ramp_by_mem[mgt];
        ramp_dur_mem[mgs*DSTRIDE + mgt]       = ramp_dur_mem[mgt];
        ramp_delay_mem[mgs*DSTRIDE + mgt]     = ramp_delay_mem[mgt];""", """      loop(32,
        target_drift_up[mgs*32 + mgt]    = target_drift_up[mgt];
        target_drift_down[mgs*32 + mgt]  = target_drift_down[mgt];
        target_drift_per[mgs*32 + mgt]   = target_drift_per[mgt];
        target_drift_shape[mgs*32 + mgt] = target_drift_shape[mgt];
        ramp_by_mem[mgs*32 + mgt]        = ramp_by_mem[mgt];
        ramp_dur_mem[mgs*32 + mgt]       = ramp_dur_mem[mgt];
        ramp_delay_mem[mgs*32 + mgt]     = ramp_delay_mem[mgt];""")
rep("""    file_mem(0, target_drift_play,  DBANK);
    file_mem(0, target_drift_rest,  DBANK);
    file_mem(0, ramp_play_mem,      DBANK);
    file_mem(0, ramp_rest_mem,      DBANK);
    file_mem(0, target_drift_unit,  DBANK);
    file_mem(0, ramp_by_unit,       DBANK);
    file_mem(0, target_drift_moves, DBANK);
  );
""", """    file_mem(0, target_drift_play,  ser_nb);
    file_mem(0, target_drift_rest,  ser_nb);
    file_mem(0, ramp_play_mem,      ser_nb);
    file_mem(0, ramp_rest_mem,      ser_nb);
    file_mem(0, target_drift_unit,  ser_nb);
    file_mem(0, ramp_by_unit,       ser_nb);
    file_mem(0, target_drift_moves, ser_nb);
  );
  // --- A save older than 7700009 holds 22 targets at stride 32 (2026-09-16): carry every bank it
  //     held into the 111 list; what it did not hold keeps its default, Wash grain's drift goes, and
  //     its one Drift period unit and Ramp time unit start every target (units_seed, in @block).
  (file_avail(0) >= 0 && ser_magic < 7700009) ? (
    t111_remap(target_drift_up, 0); t111_remap(target_drift_down, 0); t111_remap(target_drift_per, 30);
    t111_remap(target_drift_shape, 0); t111_remap(ramp_by_mem, 0); t111_remap(ramp_dur_mem, 0); t111_remap(ramp_delay_mem, 0);
    ser_magic >= 7700008 ? (
      t111_remap(target_drift_play, 0); t111_remap(target_drift_rest, 0); t111_remap(ramp_play_mem, 0);
      t111_remap(ramp_rest_mem, 0); t111_remap(target_drift_unit, 0); t111_remap(ramp_by_unit, 0);
      t111_remap(target_drift_moves, -1);
    ) : (
      t111_remap(target_drift_moves, -1);
    );
    umk = 0; loop(DBANK, target_drift_moves[umk] < 0 ? target_drift_moves[umk] = tg_moves_dflt(umk % DSTRIDE); umk += 1; );
    units_seed = 1;
    last_drift_key = 0; last_ramp_key = 0;
  );
""")
rep("""    file_mem(0, lay_ot_harm, NLAY);
  ) : file_avail(0) >= 0 ? (""", """    file_mem(0, lay_ot_harm, NLAY);
    file_mem(0, target_drift_punit, DBANK); file_mem(0, ramp_tunit, DBANK);
  ) : file_avail(0) >= 0 ? (""")
rep("""    last_drift_key = (duptgt  >= TG_GLOBAL ? 0 : dupslot)*DSTRIDE + duptgt;
    last_ramp_key  = (duprtgt >= TG_GLOBAL ? 0 : dupslot)*DSTRIDE + duprtgt;
    slider70 = target_drift_up[last_drift_key];
    slider71 = target_drift_down[last_drift_key];
    slider73 = target_drift_per[last_drift_key];
    slider75 = target_drift_shape[last_drift_key];
    slider82 = ramp_by_mem[last_ramp_key];
    slider84 = ramp_dur_mem[last_ramp_key];
    slider89 = ramp_delay_mem[last_ramp_key];""", """    last_drift_key = (tg_glob[duptgt]  ? 0 : dupslot)*DSTRIDE + duptgt;
    last_ramp_key  = (tg_glob[duprtgt] ? 0 : dupslot)*DSTRIDE + duprtgt;
    dupd = tg_is_all(duptgt) ? last_drift_key + 1 : last_drift_key;
    dupr = tg_is_all(duprtgt) ? last_ramp_key + 1 : last_ramp_key;
    slider70 = target_drift_up[dupd];
    slider71 = target_drift_down[dupd];
    slider73 = target_drift_per[dupd];
    slider75 = target_drift_shape[dupd];
    slider82 = ramp_by_mem[dupr];
    slider84 = ramp_dur_mem[dupr];
    slider89 = ramp_delay_mem[dupr];
    ser_magic >= 7700009 ? ( slider72 = target_drift_punit[dupd]; slider83 = ramp_tunit[dupr]; );""")
rep("""    slider69 = target_drift_unit[last_drift_key];
    slider74 = target_drift_moves[last_drift_key];
    slider76 = target_drift_play[last_drift_key];
    slider77 = target_drift_rest[last_drift_key];
    slider81 = ramp_by_unit[last_ramp_key];
    slider85 = ramp_play_mem[last_ramp_key];
    slider86 = ramp_rest_mem[last_ramp_key];""", """    slider69 = target_drift_unit[dupd];
    slider74 = target_drift_moves[dupd];
    slider76 = target_drift_play[dupd];
    slider77 = target_drift_rest[dupd];
    slider81 = ramp_by_unit[dupr];
    slider85 = ramp_play_mem[dupr];
    slider86 = ramp_rest_mem[dupr];""")
rep("units_seed = 0;", "units_seed = 0;", 0) if False else None
rep("grain_seed = 0;\n", "grain_seed = 0; units_seed = 0; pr_len_set = 0; pr_play_lat = 0; pr_rest_lat = 0;\n")

open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if CRLF else s)
print('patched')
