"""Stage 6: sixteen global layers (the Morpher's), on the wavetable voice and in the wash.

Layer 1 is the original voice: Active at 0 dB, pitch 0 -- a saved Passage sounds as it did. Layers
2-16 start Inactive at -6 dB (Rozaya, 2026-09-16) on the Morpher's starting pitches. Each layer is
the whole morph again at its own ratio from each slot's own pitch, in the voice (its own pair of
wavetables) and in the wash (the grain spectrum read again at its ratio).
"""
p = r'C:/git-src/rozaya-jsfx/src/spectral_vowel_passage.jsfx'
s = open(p, encoding='utf-8', newline='').read()
CRLF = '\r\n' in s
s = s.replace('\r\n', '\n')


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:200])
    s = s.replace(a, b)


# --- declarations, after Overtone width
rep("slider49:1<0.5,4,0.1>Overtone width (all slots, harmonics either side)\n",
"""slider49:1<0.5,4,0.1>Overtone width (all slots, harmonics either side)

// --- Layers (2026-09-16, the Morpher's, GLOBAL here). Rozaya: "the per slot layering doesn't really
//     make sense to me ... I would just have it be global". Each layer is the whole morph -- voice and
//     wash -- again at its own pitch from each slot's own pitch, so the stack moves as one. Layer 1 is
//     the original and moves like any layer. All at 0: only a control actually moved reaches all
//     sixteen. The level and active defaults are Layer 1's, because the selector opens on Layer 1;
//     Layers 2-16 start Inactive at -6 dB (Rozaya: "If they're not active they don't need to be that
//     low, they're just... off.").
slider50:1<0,16,1{All,Layer 1,Layer 2,Layer 3,Layer 4,Layer 5,Layer 6,Layer 7,Layer 8,Layer 9,Layer 10,Layer 11,Layer 12,Layer 13,Layer 14,Layer 15,Layer 16}>Layer
slider51:1<0,1,1{Inactive,Active}>Layer active
slider52:1<0,2,1{Hz,Semitones,Cents}>Layer pitch mode
slider53:0<-20000,20000,0.001>Layer pitch value (Hz / semitones / cents)
slider54:2<0,2,1{Hz,Semitones,Cents}>Layer fine tune unit
slider55:0<-1000,1000,0.001>Layer fine tune
slider56:0<-60,24,0.01>Layer level (dB, -60 = off)
slider57:0<0,1,1{Off,Solo}>Layer solo
// A CPU and colour control: a layer keeps only its first N partials (0 = all).
slider58:0<0,64,1>Layer harmonics (0 = full)
// -1 follows the slots' Overtone harmonic; any other number is this layer's own, with the slots'
// lift and the global width.
slider59:-1<-1,64,1>Layer overtone harmonic (-1 = follow the global)
""")

# --- memory, after the wavetable state; the tables grow to sixteen layers x two positions
rep("""wt_tab   = freemem; freemem += 4;         // table addresses, [p*2 + q]
wt_tab[0] = freemem; freemem += 2*WTN; wt_tab[1] = freemem; freemem += 2*WTN;
wt_tab[2] = freemem; freemem += 2*WTN; wt_tab[3] = freemem; freemem += 2*WTN;
wt_phi   = freemem; freemem += 2*NHARM;   // each phase bank's partial start phases, [bank*NHARM + n-1]
wt_ph    = freemem; freemem += 4;         // running phase in cycles, [p*2 + channel]
wt_act   = freemem; freemem += 2;         // which of the two tables is playing
wt_xf    = freemem; freemem += 2;         // samples left in the fade from the other table
wt_wait  = freemem; freemem += 2;         // samples before the next build may start
wt_bank  = freemem; freemem += 2;         // which start-phase bank the voice's partials use
wt_slot  = freemem; freemem += 2;         // what the playing table was built from ...
wt_otv   = freemem; freemem += 2;
wt_hv    = freemem; freemem += 2;
wt_nb    = freemem; freemem += 2;
wt_f     = freemem; freemem += 2;
wt_hct   = freemem; freemem += 2;
""", """//     A voice p is layer k's position: p = k*2 (A) or k*2 + 1 (B); Layer 1 is k = 0.
NLAY = 16; NVOI = 32;
wt_tab   = freemem; freemem += NVOI*2;    // table addresses, [p*2 + q]
wti = 0; loop(NVOI*2, wt_tab[wti] = freemem; freemem += 2*WTN; wti += 1; );
wt_phi   = freemem; freemem += NVOI*NHARM;   // each phase bank's partial start phases, [bank*NHARM + n-1]
wt_ph    = freemem; freemem += NVOI*2;    // running phase in cycles, [p*2 + channel]
wt_act   = freemem; freemem += NVOI;      // which of the two tables is playing
wt_xf    = freemem; freemem += NVOI;      // samples left in the fade from the other table
wt_wait  = freemem; freemem += NVOI;      // samples before the next build may start
wt_bank  = freemem; freemem += NVOI;      // which start-phase bank the voice's partials use
wt_slot  = freemem; freemem += NVOI;      // what the playing table was built from ...
wt_otv   = freemem; freemem += NVOI;
wt_hv    = freemem; freemem += NVOI;
wt_nb    = freemem; freemem += NVOI;
wt_f     = freemem; freemem += NVOI;
wt_hct   = freemem; freemem += NVOI;
wt_cap   = freemem; freemem += NVOI;
// The layer banks (config, saved from 7700009) and what @block derives from them.
lay_active  = freemem; freemem += NLAY;
lay_semi    = freemem; freemem += NLAY;   // pitch value, in lay_punit
lay_punit   = freemem; freemem += NLAY;
lay_fine    = freemem; freemem += NLAY;
lay_funit   = freemem; freemem += NLAY;
lay_db      = freemem; freemem += NLAY;
lay_solo    = freemem; freemem += NLAY;
lay_nharm   = freemem; freemem += NLAY;
lay_ot_harm = freemem; freemem += NLAY;
layer_ratio = freemem; freemem += NLAY;
layer_gain  = freemem; freemem += NLAY;
lay_ot_gain = freemem; freemem += NLAY*NHARM;   // a layer's own Overtone curve, when it has one
lay_ot_norm = freemem; freemem += NLAY;
lay_otv     = freemem; freemem += NLAY;          // bumped when that curve changes
lay_ui_last = freemem; freemem += 16;            // the nine visible layer controls, last seen
curmag_pre  = freemem; freemem += NBINS;         // the wash before the slots' overtone, for a layer with its own
""")
# --- @init: start phases for the layer voices, drawn WITHOUT rand() so every existing random
#     stream (Drift's Random shape, grain phases) is untouched
rep("""i = 0; loop(NHARM, wt_phi[i] = hph[i]; wt_phi[NHARM + i] = hphB[i]; i += 1; );
i = 0; loop(2, wt_ph[i*2] = 0; wt_ph[i*2+1] = 0; wt_act[i] = 0; wt_xf[i] = 0; wt_wait[i] = 0;
               wt_bank[i] = i; wt_slot[i] = -1; i += 1; );
""", """i = 0; loop(NHARM, wt_phi[i] = hph[i]; wt_phi[NHARM + i] = hphB[i]; i += 1; );
// Layers 2-16: fixed scattered phases (a hash, not rand(), so no random stream moves).
i = NHARM*2; loop((NVOI - 2)*NHARM, wtq = sin(i * 12.9898 + 78.233) * 43758.5453; wt_phi[i] = (wtq - floor(wtq)) * TWOPI; i += 1; );
i = 0; loop(NVOI, wt_ph[i*2] = 0; wt_ph[i*2+1] = 0; wt_act[i] = 0; wt_xf[i] = 0; wt_wait[i] = 0;
                  wt_bank[i] = i; wt_slot[i] = -1; wt_cap[i] = 0; i += 1; );
""")
# --- layer bank defaults, in the one-time guard
rep("  i = 0; loop(NBINS, doff[i] = rand(1)*2 - 1; i += 1; );\n",
"""  // Layers: Layer 1 is the original, on at 0 dB; the rest off at -6 dB, on the Morpher's pitches.
  i = 0; loop(NLAY, lay_active[i] = i == 0; lay_db[i] = i == 0 ? 0 : -6; lay_punit[i] = 1; lay_fine[i] = 0; lay_funit[i] = 2;
                    lay_solo[i] = 0; lay_nharm[i] = 0; lay_ot_harm[i] = -1; lay_otv[i] = 0; lay_ot_norm[i] = 1; i += 1; );
  lay_semi[0] = 0;
  lay_semi[1] = -48; lay_semi[2] = -36; lay_semi[3] = -24; lay_semi[4] = -12; lay_semi[5] = -7; lay_semi[6] = -5;
  lay_semi[7] = 5;   lay_semi[8] = 7;   lay_semi[9] = 12;  lay_semi[10] = 24; lay_semi[11] = 36; lay_semi[12] = 48;
  lay_semi[13] = -12; lay_semi[14] = 12; lay_semi[15] = -24;
  i = 0; loop(NBINS, doff[i] = rand(1)*2 - 1; i += 1; );
""")
rep("dl_n = 0; rl_n = 0; ro_n = 0;\n",
    "dl_n = 0; rl_n = 0; ro_n = 0;\nnlay_on = 0; base_gain = 1; lay_ot_any = 0; lay_ui_inited = 0; last_lay_selv = 1;\n"
    "i = 0; loop(16, layer_ratio[i] = 1; layer_gain[i] = i == 0; i += 1; );\n")

# --- the builder takes a harmonic cap and a curve per voice
rep("""function wt_build(p, slot, f) local(q, b, hn, nrm, a, ps, re, im, fr, pb) (
  q = 1 - wt_act[p]; b = wt_tab[p*2 + q]; pb = wt_bank[p] * NHARM;""",
"""function wt_build(p, slot, f) local(q, b, hn, nrm, a, ps, re, im, fr, pb, lk, og, cap) (
  q = 1 - wt_act[p]; b = wt_tab[p*2 + q]; pb = wt_bank[p] * NHARM;
  lk = floor(p / 2); cap = lay_nharm[lk]; cap <= 0 ? cap = NHARM;
  og = (lay_ot_harm[lk] >= 0 && ot_on) ? lay_ot_gain + lk*NHARM : ot_gain;""")
rep("""    hn * fr < hc_bound ? (
      a = slot_harm[slot*NHARM + hn - 1] / nrm * ot_gain[hn - 1] * hc_g(hn * f) * 0.5;""",
"""    (hn * fr < hc_bound && hn <= cap) ? (
      a = slot_harm[slot*NHARM + hn - 1] / nrm * og[hn - 1] * hc_g(hn * f) * 0.5;""")
rep("  wt_slot[p] = slot; wt_otv[p] = ot_ver; wt_hv[p] = harm_ver;",
    "  wt_slot[p] = slot; wt_otv[p] = wt_otver(lk); wt_cap[p] = lay_nharm[lk]; wt_hv[p] = harm_ver;")
rep("function wt_build(p, slot, f)",
"""// The version of the Overtone curve voice positions of layer lk read: its own, or the slots'.
function wt_otver(lk) ( (lay_ot_harm[lk] >= 0 && ot_on) ? 1000000 + lay_otv[lk] * 2 + lk * 0.001 : ot_ver; );
function wt_build(p, slot, f)""")
rep("  (wt_slot[p] != slot || wt_otv[p] != ot_ver || wt_hv[p] != harm_ver ||",
    "  (wt_slot[p] != slot || wt_otv[p] != wt_otver(floor(p / 2)) || wt_cap[p] != lay_nharm[floor(p / 2)] || wt_hv[p] != harm_ver ||")
rep("  wt_slot[p] = wt_slot[o]; wt_otv[p] = wt_otv[o];", "  wt_slot[p] = wt_slot[o]; wt_otv[p] = wt_otv[o]; wt_cap[p] = wt_cap[o];")

# --- handover: every layer's pair hands over as the base pair does
rep("    wt_take(0, 1);\n", "    wtk = 0; loop(NLAY, wt_take(wtk*2, wtk*2 + 1); wtk += 1; );\n")
rep("      wt_take(1, 0);\n", "      wtk = 0; loop(NLAY, wt_take(wtk*2 + 1, wtk*2); wtk += 1; );\n")

# --- the voice: Layer 1 at its ratio and gain, then every other audible layer
a = s.find("  wt_check(0, vsi, fA); wt_check(1, vsj, fB);")
b = s.find("  wt_xf[0] > 0 ? wt_xf[0] -= 1; wt_xf[1] > 0 ? wt_xf[1] -= 1;\n", a)
assert a > 0 and b > a
s = s[:a] + """  // Layer 1 is the original: its ratio and gain (1 and 1 unless moved, which multiply exactly).
  fAo = fA * layer_ratio[0]; fBo = fB * layer_ratio[0];
  wt_check(0, vsi, fAo); wt_check(1, vsj, fBo);
  voice_detune > 0 ? (
    fAL = fAo*(1-voice_detune); fAR = fAo*(1+voice_detune);
    fBL = fBo*(1-voice_detune); fBR = fBo*(1+voice_detune);
    vvAL = wt_read(0, 0, fAL); vvAR = wt_read(0, 1, fAR);
    vvBL = wt_read(1, 0, fBL); vvBR = wt_read(1, 1, fBR);
    hVL = base_gain * ((1-vmfr)*vvAL + vmfr*vvBL) * 0.08;   // ~match the wash's ~0.1 RMS
    hVR = base_gain * ((1-vmfr)*vvAR + vmfr*vvBR) * 0.08;
  ) : (
    // Mono (Stereo width 0): one table read per voice, L = R.
    vvA = wt_read(0, 0, fAo); vvB = wt_read(1, 0, fBo);
    hVL = base_gain * ((1-vmfr)*vvA + vmfr*vvB) * 0.08;
    hVR = hVL;
  );
  // Layers 2-16: the same two voices at each layer's ratio, gated on the layer's gain, so a layer
  // that is off costs nothing. Each has its own tables and phases.
  nlay_on ? (
    lyk = 1;
    loop(NLAY - 1,
      lyg = layer_gain[lyk];
      lyg > 0.0001 ? (
        lyfa = fA * layer_ratio[lyk]; lyfb = fB * layer_ratio[lyk];
        wt_check(lyk*2, vsi, lyfa); wt_check(lyk*2 + 1, vsj, lyfb);
        voice_detune > 0 ? (
          hVL += lyg * ((1-vmfr)*wt_read(lyk*2, 0, lyfa*(1-voice_detune)) + vmfr*wt_read(lyk*2 + 1, 0, lyfb*(1-voice_detune))) * 0.08;
          hVR += lyg * ((1-vmfr)*wt_read(lyk*2, 1, lyfa*(1+voice_detune)) + vmfr*wt_read(lyk*2 + 1, 1, lyfb*(1+voice_detune))) * 0.08;
        ) : (
          lyv = lyg * ((1-vmfr)*wt_read(lyk*2, 0, lyfa) + vmfr*wt_read(lyk*2 + 1, 0, lyfb)) * 0.08;
          hVL += lyv; hVR += lyv;
        );
        wt_xf[lyk*2] > 0 ? wt_xf[lyk*2] -= 1; wt_xf[lyk*2 + 1] > 0 ? wt_xf[lyk*2 + 1] -= 1;
      );
      lyk += 1;
    );
  );
""" + s[b:]

# --- a layer's own Overtone curve, built where the slots' curve is
rep("""    ot_boost = otg;                            // the wash rebuilds the window itself
  ) : (
    oi = 0; loop(NHARM, ot_gain[oi] = 1; oi += 1; );
    ot_boost = 1; ot_norm = 1;
  );
""", """    ot_boost = otg;                            // the wash rebuilds the window itself
    // A layer with its own Overtone harmonic (2026-09-16, the Morpher's): the same curve and power
    // normalisation, centred on its harmonic. Lift and width are the slots'.
    lok = 0;
    loop(NLAY,
      lay_ot_harm[lok] >= 0 ? (
        lobo = lok*NHARM;
        oi = 0; loop(NHARM, lay_ot_gain[lobo+oi] = 1; oi += 1; );
        lay_ot_harm[lok] > 0 ? (
          olo = max(1, ceil(lay_ot_harm[lok] - otw));
          ohi = min(NHARM, floor(lay_ot_harm[lok] + otw));
          oi = olo;
          loop(max(0, ohi - olo + 1),
            od = abs(oi - lay_ot_harm[lok]) / otw;
            ow = od >= 1 ? 0 : (0.5 + 0.5*wtsin(od*PI + PI*0.5));
            lay_ot_gain[lobo+oi-1] = 1 + (otg - 1)*ow;
            oi += 1;
          );
          lay_ot_gain[lobo] = 1;
        );
        opw = 0; oi = 0; loop(NHARM, opw += lay_ot_gain[lobo+oi]*lay_ot_gain[lobo+oi]; oi += 1; );
        lay_ot_norm[lok] = opw > 0 ? sqrt(NHARM / opw) : 1;
        oi = 0; loop(NHARM, lay_ot_gain[lobo+oi] = lay_ot_gain[lobo+oi] * lay_ot_norm[lok]; oi += 1; );
        lay_otv[lok] += 1;
      );
      lok += 1;
    );
  ) : (
    oi = 0; loop(NHARM, ot_gain[oi] = 1; oi += 1; );
    ot_boost = 1; ot_norm = 1;
  );
""")
rep("(ot_on != ot_on_last || (ot_on && (ot_h_smooth != ot_h_last || ot_db_smooth != ot_db_last || ot_w_smooth != ot_w_last))) ? (",
    "(ot_on != ot_on_last || lay_ot_dirty || (ot_on && (ot_h_smooth != ot_h_last || ot_db_smooth != ot_db_last || ot_w_smooth != ot_w_last))) ? (\n  lay_ot_dirty = 0;")

# --- wash: keep the pre-overtone spectrum when a layer has its own harmonic
rep("  ot_wash = (ot_on && ot_bin > 0) ? 1 : 0;\n  i = 0;\n  loop(NBINS,\n    i < cutbin ? ( curmag[i] = 0; ) : ( curmag[i] = max(0, curmag[i] - thr); );\n",
    "  ot_wash = (ot_on && ot_bin > 0) ? 1 : 0;\n  lay_ot_pre = ot_wash && lay_ot_any && nlay_on;\n  i = 0;\n  loop(NBINS,\n    i < cutbin ? ( curmag[i] = 0; ) : ( curmag[i] = max(0, curmag[i] - thr); );\n    lay_ot_pre ? curmag_pre[i] = curmag[i];\n")
rep("""function build_spectrum(useR) local(i, srcb, b0, fr, m, ph, woff, re, im, mir) (""",
"""function build_spectrum(useR) local(i, srcb, b0, fr, m, ph, woff, re, im, mir, lq, lm, od, ow, lb) (""")
rep("""    srcb = i * GR;
    (srcb >= 0 && srcb < NBINS - 1) ? ( b0 = floor(srcb); fr = srcb - b0; m = (curmag[b0]*(1-fr) + curmag[b0+1]*fr) * GINV; ) : ( m = 0; );
""", """    srcb = i * GR / layer_ratio[0];   // Layer 1 moves like any layer; exactly i * GR at ratio 1
    (srcb >= 0 && srcb < NBINS - 1) ? ( b0 = floor(srcb); fr = srcb - b0; m = (curmag[b0]*(1-fr) + curmag[b0+1]*fr) * GINV; ) : ( m = 0; );
    lay_ot_pre && lay_ot_harm[0] >= 0 ? m = wash_own_ot(0, srcb) * GINV;
    m *= base_gain;
    // Layers 2-16 on the wash: the same spectrum read again at each layer's ratio and summed in,
    // sharing this bin's random phase (a phase-randomised bed is noise wherever two land).
    nlay_on ? (
      lq = 1;
      loop(NLAY - 1,
        layer_gain[lq] > 0.0001 ? (
          srcb = i * GR / layer_ratio[lq];
          (srcb >= 0 && srcb < NBINS - 1) ? (
            lay_ot_pre && lay_ot_harm[lq] >= 0 ? ( lm = wash_own_ot(lq, srcb); ) : (
              b0 = floor(srcb); fr = srcb - b0; lm = curmag[b0]*(1-fr) + curmag[b0+1]*fr; );
            m += layer_gain[lq] * lm * GINV;
          );
        );
        lq += 1;
      );
    );
""")
rep("function build_spectrum(useR)", """// A layer with its own Overtone harmonic, on the wash: the pre-overtone spectrum at srcb, lifted
// around that layer's harmonic with the slots' lift and width and normalised by its own curve.
function wash_own_ot(lk, srcb) local(b0, fr, m, lb, od, ow) (
  b0 = floor(srcb); fr = srcb - b0; m = curmag_pre[b0]*(1-fr) + curmag_pre[b0+1]*fr;
  lb = ot_f0mix * lay_ot_harm[lk] * ot_bpf;
  (lay_ot_harm[lk] > 0 && srcb > ot_f0bin && abs(srcb - lb) < ot_binw) ? (
    od = abs(srcb - lb) / ot_binw; ow = 0.5 + 0.5*wtsin(od*PI + PI*0.5);
    m * (1 + (ot_boost - 1)*ow) * lay_ot_norm[lk];
  ) : m * lay_ot_norm[lk];
);
function build_spectrum(useR)""")

# --- @slider: the layer selector and its nine controls
rep("drift_restart_free = slider79;   // 0 = restart on play (sync), 1 = free-running\n",
"""drift_restart_free = slider79;   // 0 = restart on play (sync), 1 = free-running
// --- Layers (2026-09-16), the Morpher's model: the selector is a view, every edit is written as it
//     happens, only a control actually moved is written, and on All it reaches all sixteen. Nothing
//     is written until @block or @serialize has adopted what is on screen.
lay_selv = max(0, min(NLAY, floor(slider50 + 0.5)));
lay_sel  = lay_selv == 0 ? 0 : lay_selv - 1;
lay_ui_inited ? (
  last_lay_selv != lay_selv ? (
    slider51 = lay_active[lay_sel]; slider52 = lay_punit[lay_sel]; slider53 = lay_semi[lay_sel];
    slider54 = lay_funit[lay_sel];  slider55 = lay_fine[lay_sel];  slider56 = lay_db[lay_sel];
    slider57 = lay_solo[lay_sel];   slider58 = lay_nharm[lay_sel]; slider59 = lay_ot_harm[lay_sel];
    sliderchange(-1);
    lay_adopt(); last_lay_selv = lay_selv;
  ) : (
    lay_put(0, slider51, lay_active); lay_put(1, slider52, lay_punit); lay_put(2, slider53, lay_semi);
    lay_put(3, slider54, lay_funit);  lay_put(4, slider55, lay_fine);  lay_put(5, slider56, lay_db);
    lay_put(6, slider57, lay_solo);   lay_put(7, slider58, lay_nharm); lay_put(8, slider59, lay_ot_harm);
  );
);
""")
rep("function ps_all(k, raw, v, bank) local(pa) (",
"""function lay_adopt() (
  lay_ui_last[0] = slider51; lay_ui_last[1] = slider52; lay_ui_last[2] = slider53; lay_ui_last[3] = slider54;
  lay_ui_last[4] = slider55; lay_ui_last[5] = slider56; lay_ui_last[6] = slider57; lay_ui_last[7] = slider58;
  lay_ui_last[8] = slider59;
);
// A layer control moved: write the shown layer, or all sixteen on All.
function lay_put(k, v, bank) local(lp) (
  v != lay_ui_last[k] ? (
    lay_selv == 0 ? ( lp = 0; loop(NLAY, bank[lp] = v; lp += 1; ); ) : ( bank[lay_sel] = v; );
    lay_ui_last[k] = v;
    k == 8 ? lay_ot_dirty = 1;
  );
);
function ps_all(k, raw, v, bank) local(pa) (""")

# --- @block: adopt, then derive ratios, gains and flags from the banks
rep("!ps_inited ? ( ps_adopt(); ps_inited = 1; );\n",
"""!ps_inited ? ( ps_adopt(); ps_inited = 1; );
!lay_ui_inited ? ( last_lay_selv = max(0, min(NLAY, floor(slider50 + 0.5))); lay_adopt(); lay_ui_inited = 1; );
// Layers (2026-09-16): derived from the banks, so here and not in @slider. Solo overrides Active, as in
// the Morpher: any layer soloed silences every layer that is not, the original included.
lay_any_solo = 0; lz = 0; loop(NLAY, lay_solo[lz] >= 0.5 ? lay_any_solo = 1; lz += 1; );
nlay_on = 0; lay_ot_any = 0; lz = 0;
loop(NLAY,
  layer_ratio[lz] = pow(2.0, (pv_semis(lay_punit[lz], lay_semi[lz]) + pv_semis(lay_funit[lz], lay_fine[lz])) / 12);
  lay_aud = lay_any_solo ? (lay_solo[lz] >= 0.5) : (lay_active[lz] >= 0.5);
  layer_gain[lz] = (lay_aud < 0.5 || lay_db[lz] <= -60) ? 0 : pow(10, lay_db[lz] / 20);
  (lz > 0 && layer_gain[lz] > 0.0001) ? ( nlay_on = 1; lay_ot_harm[lz] >= 0 ? lay_ot_any = 1; );
  lz += 1;
);
lay_ot_harm[0] >= 0 && layer_gain[0] > 0.0001 ? lay_ot_any = 1;
base_gain = layer_gain[0];
""")

# --- @serialize: the layer banks append to 7700009; the sliders follow the shown layer on load
rep("    file_mem(0, slot_hcmode, NSLOTS); file_mem(0, slot_hcfunit, NSLOTS); file_mem(0, slot_hcfine, NSLOTS);\n  ) : file_avail(0) >= 0 ? (",
    "    file_mem(0, slot_hcmode, NSLOTS); file_mem(0, slot_hcfunit, NSLOTS); file_mem(0, slot_hcfine, NSLOTS);\n"
    "    file_mem(0, lay_active, NLAY); file_mem(0, lay_semi, NLAY); file_mem(0, lay_punit, NLAY); file_mem(0, lay_fine, NLAY);\n"
    "    file_mem(0, lay_funit, NLAY);  file_mem(0, lay_db, NLAY);   file_mem(0, lay_solo, NLAY);  file_mem(0, lay_nharm, NLAY);\n"
    "    file_mem(0, lay_ot_harm, NLAY);\n  ) : file_avail(0) >= 0 ? (")
rep("    tuning_ref = slider30 >= 20 ? slider30 : 440;\n",
    "    tuning_ref = slider30 >= 20 ? slider30 : 440;\n"
    "    dlay = max(0, min(NLAY, floor(slider50 + 0.5))); dlay = dlay == 0 ? 0 : dlay - 1;\n"
    "    slider51 = lay_active[dlay]; slider52 = lay_punit[dlay]; slider53 = lay_semi[dlay]; slider54 = lay_funit[dlay];\n"
    "    slider55 = lay_fine[dlay]; slider56 = lay_db[dlay]; slider57 = lay_solo[dlay]; slider58 = lay_nharm[dlay];\n"
    "    slider59 = lay_ot_harm[dlay];\n"
    "    lay_adopt(); lay_ui_inited = 1; last_lay_selv = max(0, min(NLAY, floor(slider50 + 0.5))); lay_ot_dirty = 1;\n")

open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if CRLF else s)
print('patched')
