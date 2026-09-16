p='src/spectral_vowel_morpher.jsfx'
s=open(p,encoding='utf-8',newline='').read(); nl='\r\n' if '\r\n' in s else '\n'; s=s.replace('\r\n','\n')
ERR=[]
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: ERR.append((a[:70],c,n)); return
    s=s.replace(a,b)
rep("slider22:0<0,1000,0.1>Spread (Hz)\n","""// --- Spread, a pitch block since 2026-09-16 (R27). Rozaya, told that in Hz the blur is one
//     fixed width everywhere and in Semitones it would blur evenly across the range: "For that
//     reason alone we should have a spread unit, and it should encorperate the usual pitch block."
//     No note name: "it's just semitones worth of width." Hz with no fine tune is exactly the
//     blur it always was. In Semitones or Cents each frequency blurs that interval either side;
//     a fine tune in Hz then widens both sides by that many Hz.
slider21:0<0,2,1{Hz,Semitones,Cents}>Spread pitch mode
slider22:0<0,1000,0.1>Spread value (Hz / semitones / cents)
slider23:2<0,2,1{Hz,Semitones,Cents}>Spread fine tune unit
slider24:0<-1000,1000,0.001>Spread fine tune
""")
rep("mtmp      = freemem; freemem += NBINS;\n","mtmp      = freemem; freemem += NBINS;\nspc       = freemem; freemem += NBINS + 1;   // Spread in Semitones/Cents: running sums of mtmp\n")
rep("spread_hz     = slider22;\n","spread_hz     = slider22;   // Spread value, in Spread pitch mode's unit\nspread_mode   = slider21; spread_funit = slider23; spread_fine = slider24;\n")
rep("function au_back(nu, tt)","""// Spread (7) and Spread fine tune (8) in a width unit {0 Hz, 1 Semitones, 2 Cents}: Semitones and
// Cents amounts convert into each other; anything else takes the amount as it stands.
function sp_amt(off, u, mode) ( u == 2 ? (mode == 2 ? off * 100 : off) : u == 3 ? (mode == 1 ? off / 100 : off) : off; );
function sp_q(k, mode) ( sp_amt(target_drift_offset[k], target_drift_unit[k], mode) + sp_amt(ramp_offset_mem[k], ramp_by_unit[k], mode); );
function au_back(nu, tt)""")
rep("eff_spread_hz    = max(0,  min(1000, spread_hz    + (mod_active[7] ? au_key(7, 2, spread_hz, srate / FFTSIZE) : 0)));\n",
"""sp_mode = spread_mode;
eff_spread_fine = spread_fine + (mod_active[8] ? sp_q(8, spread_funit) : 0);
sp_mode == 0 ? (
  // Hz: the blur it always was, and exactly the old expression while the fine tune is 0.
  eff_spread_hz    = max(0,  min(1000, spread_hz    + (mod_active[7] ? au_key(7, 2, spread_hz, srate / FFTSIZE) : 0)));
  eff_spread_fine != 0 ? (
    eff_spread_hz = spread_funit == 0 ? max(0, eff_spread_hz + eff_spread_fine) :
                    spread_funit == 1 ? eff_spread_hz * pow(2, eff_spread_fine / 12) :
                                        eff_spread_hz * pow(2, eff_spread_fine / 1200);
  );
  sp_semis = 0; sp_extra_hz = 0;
) : (
  sp_semis = max(0, spread_hz + (mod_active[7] ? sp_q(7, sp_mode) : 0));
  sp_mode == 2 ? sp_semis /= 100;
  sp_extra_hz = 0;
  spread_funit == 0 ? ( sp_extra_hz = max(0, eff_spread_fine); ) : ( sp_semis += spread_funit == 1 ? eff_spread_fine : eff_spread_fine / 100; );
  sp_semis = max(0, min(48, sp_semis));
);
""")
rep("  sp = floor(eff_spread_hz * FFTSIZE / srate);   // eff_ = base + Drift offset\n",
    "  sp = sp_mode == 0 ? floor(eff_spread_hz * FFTSIZE / srate) : 0;   // eff_ = base + Drift offset\n")
rep("""    i += 1;
  );
  ot_wash = (ot_on && ot_bin > 0) ? 1 : 0;""","""    i += 1;
  );
  // Spread in Semitones or Cents (2026-09-16): each bin blurs from f / r to f * r, r = 2^(width/12),
  // plus any fine tune in Hz on both sides -- a window that grows with frequency, so running
  // sums (spc) give each bin its own mean in one pass.
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
  ot_wash = (ot_on && ot_bin > 0) ? 1 : 0;""")
if ERR:
    for e in ERR: print('NO MATCH', e)
    raise SystemExit('NOTHING WRITTEN')
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))
print('stage 6 applied')
