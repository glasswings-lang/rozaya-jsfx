p = "C:/git-src/rozaya-jsfx/src/spectral_vowel_morpher.jsfx"
t = open(p, encoding="utf-8", newline="").read()
NL = "\r\n"


def crlf(s):
    return s.replace("\r\n", "\n").replace("\n", NL)


def once(old, new):
    global t
    old, new = crlf(old), crlf(new)
    assert t.count(old) == 1, (t.count(old), old[:90])
    t = t.replace(old, new)


# --- banks and their defaults
once("tg_scratch  = freemem; freemem += 128;  // @init's and @serialize's copy of a 55-target list\n",
     "tg_scratch  = freemem; freemem += 128;  // @init's and @serialize's copy of a 55-target list\n"
     "// Drift amount unit and Ramp by unit, per target (2026-09-13). 0 = Target default.\n"
     "target_drift_unit = freemem; freemem += 128;\n"
     "ramp_by_unit      = freemem; freemem += 128;\n")
once("    ramp_rest_mem[i]      = 0;\n",
     "    ramp_rest_mem[i]      = 0;\n"
     "    target_drift_unit[i]  = 0;   // Target default: today's meaning\n"
     "    ramp_by_unit[i]       = 0;\n")

# --- the conversion, Passage's, after pv_semis which it calls
once("pv_inited = 0;   // the Source/Target note trackers are adopted in @block\n",
     "pv_inited = 0;   // the Source/Target note trackers are adopted in @block\n"
     "// --- The amount units (2026-09-13), Passage's. A Drift or Ramp amount is held in the unit its\n"
     "// picker names, {0 Target default, 1 Hz, 2 Semitones, 3 Cents, 4 Milliseconds, 5 Seconds,\n"
     "// 6 Minutes, 7 BPM, 8 Beats, 9 Cycles, 10 dB, 11 Percent, 12 Degrees}, and turned into the\n"
     "// target's OWN unit here, against the value it rides on. A unit that cannot fit acts as Target\n"
     "// default -- Rozaya: \"It should fall back to the target's native unit, if one's not already\n"
     "// been set :)\". Percent, dB and count targets therefore take every amount as it stands.\n"
     "//\n"
     "// A pitch value (Transpose, Fine tune, a layer's pitch and fine tune) in nu {0 Hz, 1 Semitones,\n"
     "// 2 Cents}: Hz counts from the Tuning reference, and an Hz amount moves the heard frequency.\n"
     "function au_pitch(off, u, base, nu) local(s, s2, r) (\n"
     "  (u < 1 || u > 3) || (u == 1 && nu == 0) || (u == 2 && nu == 1) || (u == 3 && nu == 2) ? off : (\n"
     "    r = max(tuning_ref, 0.001);\n"
     "    s = pv_semis(nu, base);\n"
     "    s2 = u == 2 ? s + off : u == 3 ? s + off / 100 : 12 * log(max(r * pow(2, s / 12) + off, 0.001) / r) / log(2);\n"
     "    (nu == 1 ? s2 : nu == 2 ? s2 * 100 : r * pow(2, s2 / 12) - r) - base;\n"
     "  );\n"
     ");\n"
     "// A frequency in Hz (Spread, Low cut, High cut, Tuning reference): Semitones and Cents move it\n"
     "// by an interval, counted from the value, or from `floor` below it -- a cutoff at 0 still moves\n"
     "// (Rozaya: \"I'd expect it to do as advertised lol\"). Floors, Passage's: 20 Hz for the cutoffs\n"
     "// and the Tuning reference, one FFT bin for Spread.\n"
     "function au_freq(off, u, base, floor) local(b) (\n"
     "  b = max(base, floor);\n"
     "  u == 2 ? b * pow(2, off / 12) - base : u == 3 ? b * pow(2, off / 1200) - base : off;\n"
     ");\n"
     "// A length (Wash grain, Play for, Rest for) in nu {0 Seconds, 1 Hz, 2 Beats, 3 Milliseconds}.\n"
     "// Time units add time; Hz and BPM move the rate the length is one cycle of. A Cycle is one\n"
     "// Auto-morph traversal, as in the period units (au_cyc, set per block).\n"
     "au_cyc = 20;\n"
     "function au_sec(nu, v) ( nu == 3 ? v / 1000 : nu == 1 ? (v > 0.000001 ? 1 / v : 0) : nu == 2 ? v * 60 / max(tempo, 0.001) : v; );\n"
     "function au_back(nu, tt) ( nu == 3 ? tt * 1000 : nu == 1 ? (tt > 0.000001 ? 1 / tt : 0) : nu == 2 ? tt * max(tempo, 0.001) / 60 : tt; );\n"
     "function au_time(off, u, base, nu) local(b, tt, rate) (\n"
     "  !(u == 1 || (u >= 4 && u <= 9)) || (u == 4 && nu == 3) || (u == 5 && nu == 0) || (u == 1 && nu == 1) || (u == 8 && nu == 2) ? off : (\n"
     "    b = au_sec(nu, base);\n"
     "    u == 1 || u == 7 ? (\n"
     "      rate = (b > 0.000001 ? 1 / b : 0) + (u == 7 ? off / 60 : off);\n"
     "      tt = rate > 0.000001 ? 1 / rate : 0;\n"
     "    ) : (\n"
     "      tt = b + (u == 4 ? off / 1000 : u == 6 ? off * 60 : u == 8 ? off * 60 / max(tempo, 0.001) : u == 9 ? off * max(au_cyc, 0.05) : off);\n"
     "    );\n"
     "    au_back(nu, max(0, tt)) - base;\n"
     "  );\n"
     ");\n"
     "// Auto-morph time, in its Rate mode {0 BPM, 1 Seconds, 2 Hz, 3 Every N beats, 4 N per beat}.\n"
     "// Mine, from the same rules: the amount passes through where its unit is the mode's own, time\n"
     "// units add to the period, Hz and BPM add to the rate, and a Cycle is the period itself.\n"
     "function au_rate(off, u, base, mode) local(beat, b, tt, rate) (\n"
     "  beat = 60 / max(tempo, 0.001);\n"
     "  !(u == 1 || (u >= 4 && u <= 9)) || (u == 7 && mode == 0) || (u == 5 && mode == 1) || (u == 1 && mode == 2) || (u == 8 && mode == 3) ? off : (\n"
     "    b = mode == 0 ? 60 / max(base, 0.001) : mode == 1 ? base : mode == 2 ? 1 / max(base, 0.001) : mode == 3 ? base * beat : beat / max(base, 0.001);\n"
     "    u == 1 || u == 7 ? (\n"
     "      rate = 1 / max(b, 0.000001) + (u == 7 ? off / 60 : off);\n"
     "      tt = rate > 0.000001 ? 1 / rate : 1000000;\n"
     "    ) : (\n"
     "      tt = b + (u == 4 ? off / 1000 : u == 5 ? off : u == 6 ? off * 60 : u == 8 ? off * beat : off * max(au_cyc, 0.05));\n"
     "    );\n"
     "    tt = max(tt, 0.000001);\n"
     "    (mode == 0 ? 60 / tt : mode == 1 ? tt : mode == 2 ? 1 / tt : mode == 3 ? tt / beat : beat / tt) - base;\n"
     "  );\n"
     ");\n"
     "// Drift + Ramp on one target in its own unit, each amount converted from its own picker. kind\n"
     "// 1 pitch value (nu = its unit), 2 frequency (nu = the floor in Hz), 3 length (nu = its unit),\n"
     "// 4 Auto-morph time (nu = Rate mode); anything else takes the amounts as they stand. Both\n"
     "// pickers on Target default is exactly mo_q, so nothing saved changes.\n"
     "function au_key(k, kind, base, nu) (\n"
     "  (target_drift_unit[k] == 0 && ramp_by_unit[k] == 0) || kind < 1 || kind > 4 ? mo_q(k) :\n"
     "  kind == 1 ? au_pitch(target_drift_offset[k], target_drift_unit[k], base, nu) + au_pitch(ramp_offset_mem[k], ramp_by_unit[k], base, nu) :\n"
     "  kind == 2 ? au_freq(target_drift_offset[k], target_drift_unit[k], base, nu) + au_freq(ramp_offset_mem[k], ramp_by_unit[k], base, nu) :\n"
     "  kind == 3 ? au_time(target_drift_offset[k], target_drift_unit[k], base, nu) + au_time(ramp_offset_mem[k], ramp_by_unit[k], base, nu) :\n"
     "              au_rate(target_drift_offset[k], target_drift_unit[k], base, nu) + au_rate(ramp_offset_mem[k], ramp_by_unit[k], base, nu);\n"
     ");\n")

# --- consumers, @block
once("mo_at_raw = mod_active[1] ? max(0.01, auto_time_raw + mo_q(1)) : auto_time_raw;",
     "// One Auto-morph traversal without its own drift: what a Cycle is in the amount units.\n"
     "au_cyc = max(0.01,\n"
     "  time_mode == 0 ? 60 / max(auto_time_raw, 0.001) :\n"
     "  time_mode == 1 ? auto_time_raw :\n"
     "  time_mode == 2 ? 1 / max(auto_time_raw, 0.001) :\n"
     "  time_mode == 3 ? auto_time_raw * 60 / max(tempo, 0.001) :\n"
     "                   (60 / max(tempo, 0.001)) / auto_time_raw);\n"
     "mo_at_raw = mod_active[1] ? max(0.01, auto_time_raw + au_key(1, 4, auto_time_raw, time_mode)) : auto_time_raw;")
once("pr_play_sec     = (mod_active[85] ? max(0.001, slider42 + mo_q(85)) : slider42) * tr_k;",
     "pr_play_sec     = (mod_active[85] ? max(0.001, slider42 + au_key(85, 3, slider42, time_mode >= 3 ? 2 : 0)) : slider42) * tr_k;")
once("pr_rest_sec     = (mod_active[86] ? max(0.001, slider43 + mo_q(86)) : slider43) * tr_k;",
     "pr_rest_sec     = (mod_active[86] ? max(0.001, slider43 + au_key(86, 3, slider43, time_mode >= 3 ? 2 : 0)) : slider43) * tr_k;")
once("eff_grain_ms = mod_active[3] ? max(5, min(1000, grain_ms + mo_q(3))) : grain_ms;",
     "eff_grain_ms = mod_active[3] ? max(5, min(1000, grain_ms + au_key(3, 3, grain_ms, 3))) : grain_ms;")
once("  layer_ratio[lz] = pow(2.0, (pv_semis(lay_punit[lz], lay_semi[lz] + (mod_active[LP_T0+lz] ? mo_q(LP_T0+lz) : 0))\n"
     "                             + pv_semis(lay_funit[lz], lay_fine[lz] + (mod_active[LF_T0+lz] ? mo_q(LF_T0+lz) : 0)))/12);",
     "  layer_ratio[lz] = pow(2.0, (pv_semis(lay_punit[lz], lay_semi[lz] + (mod_active[LP_T0+lz] ? au_key(LP_T0+lz, 1, lay_semi[lz], lay_punit[lz]) : 0))\n"
     "                             + pv_semis(lay_funit[lz], lay_fine[lz] + (mod_active[LF_T0+lz] ? au_key(LF_T0+lz, 1, lay_fine[lz], lay_funit[lz]) : 0)))/12);")

# --- consumers, @sample
once("eff_spread_hz    = max(0,  min(1000, spread_hz    + (mod_active[4] ? target_drift_offset[4] + ramp_offset_mem[4] : 0)));",
     "eff_spread_hz    = max(0,  min(1000, spread_hz    + (mod_active[4] ? au_key(4, 2, spread_hz, srate / FFTSIZE) : 0)));")
once("tuning_ref = mod_active[7] ? max(20, min(2000, tuning_base + mo_q(7))) : tuning_base;",
     "tuning_ref = mod_active[7] ? max(20, min(2000, tuning_base + au_key(7, 2, tuning_base, 20))) : tuning_base;")
once("  eff_semi = pv_semis(pitch_unit, pitch_semi + target_drift_offset[5] + ramp_offset_mem[5])\n"
     "           + pv_semis(pitch_funit, pitch_fine + target_drift_offset[6] + ramp_offset_mem[6]);",
     "  // On Target default Transpose keeps the sum exactly as it was always written.\n"
     "  eff_semi = pv_semis(pitch_unit, target_drift_unit[5] == 0 && ramp_by_unit[5] == 0 ? pitch_semi + target_drift_offset[5] + ramp_offset_mem[5]\n"
     "                                                                                   : pitch_semi + au_key(5, 1, pitch_semi, pitch_unit))\n"
     "           + pv_semis(pitch_funit, pitch_fine + au_key(6, 1, pitch_fine, pitch_funit));")
once("eff_lowcut_hz    = max(0,  min(20000, lowcut_hz    + (mod_active[10] ? target_drift_offset[10] + ramp_offset_mem[10] : 0)));",
     "eff_lowcut_hz    = max(0,  min(20000, lowcut_hz    + (mod_active[10] ? au_key(10, 2, lowcut_hz, 20) : 0)));")
once("eff_hicut_hz = max(200, min(20000, hicut_hz + (mod_active[11] ? target_drift_offset[11] + ramp_offset_mem[11] : 0)));",
     "eff_hicut_hz = max(200, min(20000, hicut_hz + (mod_active[11] ? au_key(11, 2, hicut_hz, 20) : 0)));")

# --- the two pickers join their selectors
once("    slider54 = target_drift_rest[dts];\n    slider_automate(slider47);",
     "    slider54 = target_drift_rest[dts];\n    slider49 = target_drift_unit[dts];\n    slider_automate(slider49);\n    slider_automate(slider47);")
once("    dui_last[3] = slider52; dui_last[4] = slider53; dui_last[5] = slider54;\n    last_target_select = sel_target;",
     "    dui_last[3] = slider52; dui_last[4] = slider53; dui_last[5] = slider54;\n    dui_last[11] = slider49;\n    last_target_select = sel_target;")
once("    mo_capture(sel_target, target_drift_rest,  slider54, 5);\n",
     "    mo_capture(sel_target, target_drift_rest,  slider54, 5);\n"
     "    mo_capture(sel_target, target_drift_unit,  slider49, 11);\n")
once("    slider62 = ramp_rest_mem[rts];\n    slider_automate(slider57);",
     "    slider62 = ramp_rest_mem[rts];\n    slider58 = ramp_by_unit[rts];\n    slider_automate(slider58);\n    slider_automate(slider57);")
once("    dui_last[9] = slider61; dui_last[10] = slider62;\n    last_ramp_target = rsel_target;",
     "    dui_last[9] = slider61; dui_last[10] = slider62;\n    dui_last[12] = slider58;\n    last_ramp_target = rsel_target;")
once("    mo_capture(rsel_target, ramp_rest_mem,  slider62, 10);\n",
     "    mo_capture(rsel_target, ramp_rest_mem,  slider62, 10);\n"
     "    mo_capture(rsel_target, ramp_by_unit,   slider58, 12);\n")
once("  dui_last[9] = slider61; dui_last[10] = slider62;\n  drift_ui_inited = 1;",
     "  dui_last[9] = slider61; dui_last[10] = slider62;\n  dui_last[11] = slider49; dui_last[12] = slider58;\n  drift_ui_inited = 1;")
once("    slider62 = ramp_rest_mem[rts];\n    dui_last[0] = slider47;",
     "    slider62 = ramp_rest_mem[rts];\n    slider49 = target_drift_unit[dts];\n    slider58 = ramp_by_unit[rts];\n"
     "    dui_last[11] = slider49; dui_last[12] = slider58;\n    dui_last[0] = slider47;")

assert "\n" not in t.replace("\r\n", "")
open(p, "w", encoding="utf-8", newline="").write(t)
print("written; mo_q uses left:", t.count("mo_q("))
