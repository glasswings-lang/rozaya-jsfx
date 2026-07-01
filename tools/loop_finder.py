#!/usr/bin/env python3
"""
loop_finder.py -- find loop-ready material in any recording, blind-friendly.

Scans an audio file for every distinct SOUND EVENT (above the noise floor,
junk transients like mic-bangs auto-excluded), trims each event to its loud
core, FLATTENS the level so it loops without pumping, and writes a loop-ready
WAV per event. Labels each by shape (steady / shaped) and brightness
(dark / mid / airy) so you know what you got without seeing a waveform.

  - "steady" = level barely moves across the clip (a held texture; loops as-is).
  - "shaped" = a gesture that swelled/faded (e.g. a mouth "hooo"); the flatten
               pass removes the swell so it, too, loops cleanly.

Drop the clips straight into a sampler's crossfade loop (e.g. the suite's
Sustain Looper). Made because finding loop points by eye is a visual task.

EVERY behaviour is a documented flag (run `--help`) -- no code editing needed.
Typical workflow: run with `--list` to preview what it finds, adjust flags,
then run for real. Full flag reference is in tools/README.md.

Requires: numpy, soundfile.  Public domain (CC0), like the rest of the suite.
"""
import os, argparse, numpy as np, soundfile as sf


def analyze(mono, sr, win_ms=40, hop_ms=10):
    """Per-frame level (dB, ref = file peak) and spectral centroid (Hz)."""
    win = int(win_ms/1000*sr); hop = int(hop_ms/1000*sr)
    idx = np.arange(0, max(1, len(mono)-win), hop)
    w = np.hanning(win); freqs = np.fft.rfftfreq(win, 1/sr)
    rms = np.empty(len(idx)); cen = np.empty(len(idx))
    for j, i in enumerate(idx):
        fr = mono[i:i+win]
        rms[j] = np.sqrt(np.mean(fr**2)) + 1e-9
        m = np.abs(np.fft.rfft(fr*w)) + 1e-9
        cen[j] = np.sum(freqs*m)/np.sum(m)
    return hop, 20*np.log10(rms/np.max(rms)), cen


def runs_of(mask, min_frames):
    """Contiguous True runs (start, end_exclusive) of length >= min_frames."""
    out = []; s = None
    for i, fl in enumerate(mask):
        if fl and s is None: s = i
        if (not fl) and s is not None:
            if i-s >= min_frames: out.append((s, i))
            s = None
    if s is not None and len(mask)-s >= min_frames: out.append((s, len(mask)))
    return out


def brightness(c):
    return "dark" if c < 1200 else ("mid" if c < 2800 else "airy")


def flatten(seg, sr, do_flatten=True, smooth_ms=40, fade_ms=6.0, peak_dbfs=-3.0):
    """Optionally divide out the macro envelope (so it loops w/o pumping),
    then normalize to peak_dbfs and apply short edge fades."""
    if do_flatten:
        mono = seg.mean(axis=1) if seg.ndim > 1 else seg
        w = int(smooth_ms/1000*sr)
        env = np.sqrt(np.convolve(mono**2, np.ones(w)/w, mode='same')) + 1e-4
        gain = np.clip(np.median(env)/env, 0.0, 4.0)
        seg = seg * (gain[:, None] if seg.ndim > 1 else gain)
    out = seg * ((10**(peak_dbfs/20)) / (np.max(np.abs(seg)) + 1e-12))
    f = int(fade_ms/1000*sr)
    if f > 0 and len(out) > 2*f:
        ramp = 0.5*(1-np.cos(np.linspace(0, np.pi, f)))
        r = ramp[:, None] if out.ndim > 1 else ramp
        out[:f] *= r; out[-f:] *= r[::-1]
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Find & extract loop-ready clips from a recording. "
                    "All behaviour is controlled by the flags below (no code editing).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("input", help="audio file to scan (WAV/FLAC/OGG)")

    # --- what counts as a keepable sound event ---
    ap.add_argument("--sensitivity", type=float, default=4.0,
        help="how far below the typical level still counts as sound (dB). RAISE to catch quieter breaths, LOWER to ignore them")
    ap.add_argument("--gap", type=float, default=0.08,
        help="bridge silences shorter than this within one event (sec). RAISE to keep a swelly breath whole, LOWER to split more")
    ap.add_argument("--min-dur", type=float, default=0.5, help="shortest clip to keep (sec)")
    ap.add_argument("--core-db", type=float, default=10.0,
        help="trim each event to within this many dB of its own peak. LOWER = tighter, steadier core")

    # --- junk (mic bang / bump) handling ---
    ap.add_argument("--bang-jump", type=float, default=15.0,
        help="a sudden level jump this big (dB) marks a junk transient to skip. RAISE to be less aggressive")
    ap.add_argument("--keep-junk", action="store_true", help="do NOT skip loud transients at all")

    # --- extraction / output ---
    ap.add_argument("--max-clips", type=int, default=12, help="keep at most this many (longest first)")
    ap.add_argument("--peak-db", type=float, default=-3.0, help="normalize each clip to this peak level (dBFS)")
    ap.add_argument("--fade-ms", type=float, default=6.0, help="edge fade length (ms)")
    ap.add_argument("--no-flatten", action="store_true", help="keep the natural level shape (do NOT flatten the swell)")
    ap.add_argument("--as-float", action="store_true", help="write 32-bit float WAV instead of 16-bit")
    ap.add_argument("--outdir", default=None, help="where to write clips (default: the input file's folder)")
    ap.add_argument("--prefix", default=None, help="filename prefix (default: from the input name)")

    # --- labeling + preview ---
    ap.add_argument("--flat-db", type=float, default=2.0,
        help="internal wobble under this dB is labeled 'steady', else 'shaped'")
    ap.add_argument("--list", dest="dry", action="store_true",
        help="just PRINT what would be extracted; write NO files (use to tune flags first)")
    a = ap.parse_args()

    x, sr = sf.read(a.input, always_2d=True)
    mono = x.mean(axis=1)
    outdir = a.outdir or os.path.dirname(a.input) or "."
    prefix = a.prefix or os.path.splitext(os.path.basename(a.input))[0][:16]

    hop, rdb, cen = analyze(mono, sr)
    dt = hop/sr
    tof = lambda fr: fr*hop

    # --- junk transients ---
    med = np.median(rdb)
    if a.keep_junk:
        bang = np.zeros(len(rdb), dtype=bool)
    else:
        donset = np.diff(rdb, prepend=rdb[0])
        bang = (donset > a.bang_jump) | (rdb > med + 20)
        if bang.any():
            bw = int(0.5/dt)
            bang = np.convolve(bang.astype(float), np.ones(2*bw+1), 'same') > 0

    # --- floor + active mask, bridge brief dips ---
    floor = (np.percentile(rdb[~bang], 50) - a.sensitivity) if (~bang).any() else med-10
    active = (rdb > floor) & (~bang)
    g = max(1, int(a.gap/dt))
    active = (np.convolve(active.astype(float), np.ones(2*g+1), 'same') > 0) & (~bang)

    events = runs_of(active, int(a.min_dur/dt))

    cands = []
    for (s, e) in events:
        seg = rdb[s:e]; pk = np.max(seg)
        core = runs_of(seg > pk - a.core_db, int(a.min_dur*0.6/dt))
        if core:
            c0, c1 = max(core, key=lambda r: r[1]-r[0]); c0 += s; c1 += s
        else:
            c0, c1 = s, e
        rng = np.max(rdb[c0:c1]) - np.min(rdb[c0:c1])
        shape = "steady" if rng < a.flat_db else "shaped"
        bright = brightness(np.median(cen[c0:c1]))
        cands.append((c0, c1, tof(c1)-tof(c0), shape, bright))

    cands.sort(key=lambda c: c[2], reverse=True)
    cands = sorted(cands[:a.max_clips], key=lambda c: c[0])

    print(f"source: {os.path.basename(a.input)}  ({len(mono)/sr:.1f}s, {sr}Hz)")
    print(f"floor {floor:.1f}dB, junk frames excluded: {int(bang.sum())}")
    print(("PREVIEW (no files written) -- " if a.dry else "") + f"{len(cands)} clip(s):\n")
    sub = 'FLOAT' if a.as_float else 'PCM_16'
    for k, (c0, c1, nsamp, shape, bright) in enumerate(cands, 1):
        name = f"{prefix}_{shape}_{bright}_{k:02d}.wav"
        if not a.dry:
            clip = flatten(x[tof(c0):tof(c1)].astype(np.float64), sr,
                           do_flatten=not a.no_flatten, fade_ms=a.fade_ms, peak_dbfs=a.peak_db)
            sf.write(os.path.join(outdir, name), clip.astype(np.float32), sr, subtype=sub)
        print(f"  {name:34s} [{tof(c0)/sr:6.1f}s]  {nsamp/sr:4.1f}s  {shape:6s} {bright}")
    print(f"\n{'would write to' if a.dry else 'wrote to'}: {outdir}")


if __name__ == "__main__":
    main()
