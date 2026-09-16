import sys
p = sys.argv[1] if len(sys.argv) > 1 else 'src/spectral_vowel_morpher.jsfx'
staged = '--staged' in sys.argv
s=open(p,encoding='utf-8',newline='').read(); nl='\r\n' if '\r\n' in s else '\n'; s=s.replace('\r\n','\n')
g0 = s.index("function gen_grain() local(")
body0 = s.index("  si = vsi; sj = vsj; mfr = vmfr;", g0)
br = s.index("  W <= FFTSIZE ? (", body0)
alt = s.index("  ) : (\n", br)
prep = s[body0:br]
short = s[br + len("  W <= FFTSIZE ? (\n"):alt]
# sanity: the short branch is what we expect
for piece in ["build_spectrum(0);", "build_spectrum(1);", "accR[aw] += fftwork[2*i]  * gnorm * synwin[i];", "rms_smooth"]:
    assert piece in short, piece
locals_line = s[g0:body0]
newfuncs = """// --- The wash grain, in four pieces (2026-09-16). One grain used to be built in ONE sample:
//     the spectrum prep, both channels' layered builds and their inverse FFTs, and the overlap-add
//     -- one heavy moment every hop, doubled by three layers, and a dropout when it overran the
//     audio block. Rozaya: "I used to be able to fuck with more than 3 layers. Now at 3 it starts
//     making it crackle". gen_grain() still runs all four at once (long grains, and any hop the
//     pieces could not finish); @sample spreads them across the hop instead.
""" + locals_line.replace("function gen_grain() local(", "function gg_prep() local(") + prep + ");\n" + """function gg_buildL() local(i, sv) (
  i = 0; loop(NBINS, phase[i] = rand(1)*TWOPI; i += 1; );
  build_spectrum(0);
  gg_rms = 0; i = 0; loop(W, sv = fftwork[2*i]; grainbuf[i] = sv; gg_rms += sv*sv; i += 1; );
  gg_rms = sqrt(gg_rms / W);
  gg_nlay = nlay_on; gg_bsb = bsum_base; gg_bsa = bsum_all; gg_W = W;
);
function gg_buildR() local(i) (
  build_spectrum(1);
  i = 0; loop(W, grainR[i] = fftwork[2*i]; i += 1; );
);
function gg_commit() local(i, rms, gnorm, aw) (
  rms = gg_rms;
  (gg_nlay && gg_bsb > 0 && gg_bsa > 0) ? ( rms = rms * sqrt(gg_bsb / gg_bsa); );
  rms > 0.0000001 ? ( rms_smooth <= 0 ? rms_smooth = rms : rms_smooth += 0.02 * (rms - rms_smooth); );
  gnorm = rms_smooth > 0.0000001 ? (0.07 / rms_smooth) : 0;
  i = 0;
  loop(W,
    aw = accpos + i; aw >= ACCLEN ? aw -= ACCLEN;
    accL[aw] += grainbuf[i] * gnorm * synwin[i];
    accR[aw] += grainR[i]   * gnorm * synwin[i];
    i += 1;
  );
);
"""
new_gen = locals_line + prep + "  W <= FFTSIZE ? (\n  gg_buildL(); gg_buildR(); gg_commit();\n" + s[alt:]
# replace from gen_grain start to end of file tail region: rebuild carefully
s = s[:g0] + newfuncs + new_gen
# the prep now lives in gg_prep; gen_grain keeps its own inline copy of it (identical), so a full
# grain is prep + the three pieces. Trigger in @sample:
a = "hopcount >= HOP ? ( hopcount = 0; (have > 0 && wlevel > 0.0001) ? gen_grain(); );"
assert s.count(a) == 1
b = ("""// Spread the grain across the hop (2026-09-16): prep, left, right, each a quarter-hop apart and so
// in different audio blocks at any usual buffer size; the hop boundary only adds the grain in. A
// piece is only used if all three ran for this hop and the grain length did not change since.
gg_gap = floor(HOP / 4);
""" + ("gg_ok = GG_STAGED && have > 0 && wlevel > 0.0001 && W <= FFTSIZE && gg_gap >= 1;\n") + """gg_ok ? (
  hopcount == HOP - 3 * gg_gap ? ( gg_prep(); gg_stage = 1; );
  hopcount == HOP - 2 * gg_gap && gg_stage == 1 ? ( gg_buildL(); gg_stage = 2; );
  hopcount == HOP - gg_gap && gg_stage == 2 ? ( gg_buildR(); gg_stage = 3; );
);
hopcount >= HOP ? (
  hopcount = 0;
  (have > 0 && wlevel > 0.0001) ? ( (gg_ok && gg_stage == 3 && gg_W == W) ? gg_commit() : gen_grain(); );
  gg_stage = 0;
);""")
s = s.replace(a, b)
a = "NSLOTS = 8; MAXFFT = 32768; INRING = 65536;"
assert s.count(a) == 1
s = s.replace(a, a + "\nGG_STAGED = %d;   // 1: build each wash grain in pieces across the hop (2026-09-16)" % (1 if staged else 0))
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))
print('grain split applied, staged =', staged)
