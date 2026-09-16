"""Stage 5: the voice engine plays ONE wavetable per voice instead of 64 sines (2026-09-16).

Every partial of a voice is phi_n + n * PHI, where PHI is the voice's running phase: the sine
engine already WAS a single periodic wave. So each voice position (A = vsi, B = vsj) gets a
one-cycle table holding its partials, built with a native ifft only when what is in it changes
(the slot, a capture, the Overtone curve, the High cut, or which partials fit under Nyquist),
and crossfaded from the previous table over WT_XF samples. Per sample a voice is one table read
per channel, where it was 64 sines per channel.
"""
p = r'C:/git-src/rozaya-jsfx/src/spectral_vowel_passage.jsfx'
s = open(p, encoding='utf-8', newline='').read()
CRLF = '\r\n' in s
s = s.replace('\r\n', '\n')


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:200])
    s = s.replace(a, b)


# --- memory and state, after the Spread running sums
rep("spc           = freemem; freemem += NBINS + 1;   // Spread in Semitones/Cents: running sums of mtmp\n",
"""spc           = freemem; freemem += NBINS + 1;   // Spread in Semitones/Cents: running sums of mtmp
// --- The voice's wavetables (2026-09-16). Two positions (0 = A, the vsi voice; 1 = B, vsj), two
//     tables each (the one playing and the one being faded to), each an ifft buffer of 2*WTN.
//     Built by wt_build; see the voice engine in @sample.
WTN = 8192; WT_XF = 256;
wt_tab   = freemem; freemem += 4;         // table addresses, [p*2 + q]
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
""")
# --- @init: the start phases are the sine engine's random ones, drawn in the same order
rep("i = 0; loop(NHARM, hph[i] = rand(1)*TWOPI; hphB[i] = rand(1)*TWOPI; hphR[i] = hph[i]; hphBR[i] = hphB[i]; i += 1; );\n",
"""i = 0; loop(NHARM, hph[i] = rand(1)*TWOPI; hphB[i] = rand(1)*TWOPI; hphR[i] = hph[i]; hphBR[i] = hphB[i]; i += 1; );
// The wavetable voice (2026-09-16) starts from those same phases: bank 0 is A's, bank 1 is B's.
i = 0; loop(NHARM, wt_phi[i] = hph[i]; wt_phi[NHARM + i] = hphB[i]; i += 1; );
i = 0; loop(2, wt_ph[i*2] = 0; wt_ph[i*2+1] = 0; wt_act[i] = 0; wt_xf[i] = 0; wt_wait[i] = 0;
               wt_bank[i] = i; wt_slot[i] = -1; i += 1; );
""")
# --- a capture or re-analysis changes a slot's partials
rep("    slot_f0[slot] = f0d; slot_hnorm[slot] = mx > 0 ? mx : 1;",
    "    slot_f0[slot] = f0d; slot_hnorm[slot] = mx > 0 ? mx : 1; harm_ver += 1;")
# --- the Overtone curve changed
rep("  ot_on_last = ot_on; ot_h_last = ot_h_smooth; ot_db_last = ot_db_smooth; ot_w_last = ot_w_smooth;\n",
    "  ot_on_last = ot_on; ot_h_last = ot_h_smooth; ot_db_last = ot_db_smooth; ot_w_last = ot_w_smooth;\n  ot_ver += 1;   // the voice's wavetables rebuild\n")
# --- the builder, after hc_g
rep("function hc_g(f) ( f > hc_lo ? (hc_top - f) * hc_inv : 1; );\n",
"""function hc_g(f) ( f > hc_lo ? (hc_top - f) * hc_inv : 1; );
// Build voice position p's next table from a slot at frequency f, and start fading to it. The
// partials are exactly the sine engine's: magnitude / the slot's peak, the Overtone curve, the High
// cut's fade, each at its start phase; a partial is left out once its right-channel copy (the higher
// of the two) would reach hc_bound. JSFX's ifft does not scale, so each bin holds half the amplitude.
function wt_build(p, slot, f) local(q, b, hn, nrm, a, ps, re, im, fr, pb) (
  q = 1 - wt_act[p]; b = wt_tab[p*2 + q]; pb = wt_bank[p] * NHARM;
  memset(b, 0, 2*WTN);
  nrm = slot_hnorm[slot]; nrm <= 0 ? nrm = 1;
  fr = f * (1 + voice_detune);
  hn = 1;
  loop(NHARM,
    hn * fr < hc_bound ? (
      a = slot_harm[slot*NHARM + hn - 1] / nrm * ot_gain[hn - 1] * hc_g(hn * f) * 0.5;
      ps = wt_phi[pb + hn - 1] - PI * 0.5;
      re = a * cos(ps); im = a * sin(ps);
      b[2*hn] = re; b[2*hn + 1] = im; b[2*(WTN - hn)] = re; b[2*(WTN - hn) + 1] = -im;
    );
    hn += 1;
  );
  fft_ipermute(b, WTN); ifft(b, WTN);
  wt_act[p] = q; wt_xf[p] = wt_slot[p] < 0 ? 0 : WT_XF; wt_wait[p] = WT_XF;
  wt_slot[p] = slot; wt_otv[p] = ot_ver; wt_hv[p] = harm_ver; wt_f[p] = f; wt_hct[p] = hc_on ? hc_top : 0;
  wt_nb[p] = fr > 0 ? floor(hc_bound / fr) : NHARM + 1;
);
// Rebuild position p's table when what it holds has changed: another slot, a capture, the Overtone
// curve, the High cut, a partial crossing Nyquist, or -- only while the High cut is fading some
// partial -- the pitch moving by more than a fifth of a cent's worth of ratio.
function wt_check(p, slot, f) local(fr, nb) (
  wt_wait[p] > 0 ? wt_wait[p] -= 1;
  fr = f * (1 + voice_detune); nb = fr > 0 ? floor(hc_bound / fr) : NHARM + 1;
  (wt_slot[p] != slot || wt_otv[p] != ot_ver || wt_hv[p] != harm_ver || wt_hct[p] != (hc_on ? hc_top : 0) ||
   min(nb, NHARM + 1) != min(wt_nb[p], NHARM + 1) ||
   (hc_on && NHARM * f > hc_lo && abs(f - wt_f[p]) > 0.0001 * wt_f[p])) && (wt_wait[p] <= 0 || wt_slot[p] < 0) ? wt_build(p, slot, f);
);
// One channel of position p, advancing its phase by f / srate. Reads both tables while fading.
function wt_read(p, ch, f) local(ph, x, i0, fr, t, v, m) (
  m = WTN - 1;
  ph = wt_ph[p*2 + ch]; x = ph * WTN; i0 = floor(x); fr = x - i0;
  t = wt_tab[p*2 + wt_act[p]];
  v = t[2*(i0 & m)] * (1 - fr) + t[2*((i0 + 1) & m)] * fr;
  wt_xf[p] > 0 ? (
    t = wt_tab[p*2 + 1 - wt_act[p]];
    v = v + (t[2*(i0 & m)] * (1 - fr) + t[2*((i0 + 1) & m)] * fr - v) * wt_xf[p] / WT_XF;
  );
  ph += f / srate; ph >= 1 ? ph -= floor(ph);
  wt_ph[p*2 + ch] = ph;
  v;
);
""")
# --- handover: the voice that takes over the other's slot takes its phases, bank and table too
rep("""  (vsi == last_vsj && vsi != last_vsi) ? (
    vcp = 0; loop(NHARM, hph[vcp]  = hphB[vcp]; hphR[vcp]  = hphBR[vcp]; vcp += 1; );
  ) : (
    (vsj == last_vsi && vsj != last_vsj) ? (
      vcp = 0; loop(NHARM, hphB[vcp] = hph[vcp];  hphBR[vcp] = hphR[vcp];  vcp += 1; );
    );
  );
""", """  (vsi == last_vsj && vsi != last_vsi) ? (
    vcp = 0; loop(NHARM, hph[vcp]  = hphB[vcp]; hphR[vcp]  = hphBR[vcp]; vcp += 1; );
    wt_take(0, 1);
  ) : (
    (vsj == last_vsi && vsj != last_vsj) ? (
      vcp = 0; loop(NHARM, hphB[vcp] = hph[vcp];  hphBR[vcp] = hphR[vcp];  vcp += 1; );
      wt_take(1, 0);
    );
  );
""")
rep("function wt_read(p, ch, f)", """// Position p takes position o's voice whole: phases, start-phase bank, playing table and its stamps.
// Nothing is rebuilt, so the handover is as seamless as the sine engine's phase copy.
function wt_take(p, o) (
  wt_ph[p*2] = wt_ph[o*2]; wt_ph[p*2 + 1] = wt_ph[o*2 + 1]; wt_bank[p] = wt_bank[o];
  memcpy(wt_tab[p*2 + wt_act[p]], wt_tab[o*2 + wt_act[o]], 2*WTN); wt_xf[p] = 0;
  wt_slot[p] = wt_slot[o]; wt_otv[p] = wt_otv[o]; wt_hv[p] = wt_hv[o]; wt_nb[p] = wt_nb[o]; wt_f[p] = wt_f[o]; wt_hct[p] = wt_hct[o];
);
function wt_read(p, ch, f)""")

# --- the voice engine itself
a = s.find("  bA = vsi*NHARM; bB = vsj*NHARM;\n  voice_detune > 0 ? (")
b = s.find(") : ( hVL = 0; hVR = 0; );", a)
assert a > 0 and b > a
s = s[:a] + """  // One wavetable per voice (2026-09-16): see wt_build. Same partials, same phases, same
  // detuned right channel; the sine bank below this comment's old place ran 64 sines per channel.
  wt_check(0, vsi, fA); wt_check(1, vsj, fB);
  voice_detune > 0 ? (
    fAL = fA*(1-voice_detune); fAR = fA*(1+voice_detune);
    fBL = fB*(1-voice_detune); fBR = fB*(1+voice_detune);
    vvAL = wt_read(0, 0, fAL); vvAR = wt_read(0, 1, fAR);
    vvBL = wt_read(1, 0, fBL); vvBR = wt_read(1, 1, fBR);
    hVL = ((1-vmfr)*vvAL + vmfr*vvBL) * 0.08;   // ~match the wash's ~0.1 RMS
    hVR = ((1-vmfr)*vvAR + vmfr*vvBR) * 0.08;
  ) : (
    // Mono (Stereo width 0): one table read per voice, L = R.
    vvA = wt_read(0, 0, fA); vvB = wt_read(1, 0, fB);
    hVL = ((1-vmfr)*vvA + vmfr*vvB) * 0.08;
    hVR = hVL;
  );
  wt_xf[0] > 0 ? wt_xf[0] -= 1; wt_xf[1] > 0 ? wt_xf[1] -= 1;
""" + s[b:]
open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if CRLF else s)
print('patched')
