#!/usr/bin/env python3
"""
loop_finder.py -- find loop-ready material in any recording, blind-friendly.

Scans an audio file for every distinct SOUND EVENT (above the noise floor,
junk transients like mic-bangs auto-excluded), trims each event to its loud
core, FLATTENS the level so it loops without pumping, and writes a loop-ready
WAV per event. Labels each by shape (steady / shaped) and brightness
(dark / mid / airy) so you know what you got without seeing a waveform.

  - "steady"  = level barely moves across the clip (a held texture; loops as-is).
  - "shaped"  = a gesture that swelled/faded (e.g. a mouth "hooo"); the flatten
                pass removes the swell so it, too, loops cleanly.

Every behaviour is a documented flag (run --help). Use --list first to PREVIEW
what it would grab, tune the flags, then run for real. Full reference and
examples in tools/README.md. Public domain (CC0), like the rest of the suite.

Requires: numpy, soundfile.
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


def make_clip(seg, sr, do_flatten=True, smooth_ms=40, fade_ms=6, peak_dbfs=-3.0):
    """Optionally flatten the macro amplitude envelope, normalize, edge-fade."""
    mono = seg.mean(axis=1) if seg.ndim > 1 else seg
    if do_flatten:
        w = max(1, int(smooth_ms/1000*sr))
        env = np.sqrt(np.convolve(mono**2, np.ones(w)/w, mode='same')) + 1e-4
        gain = np.clip(np.median(env)/env, 0.0, 4.0)
        out = seg * (gain[:, None] if seg.ndim > 1 else gain)
    else:
        out = seg.copy()
    out *= (10**(peak_dbfs/20)) / (np.max(np.abs(out)) + 1e-12)
    f = int(fade_ms/1000*sr)
    if f > 0 and len(out) > 2*f:
        ramp = 0.5*(1-np.cos(np.linspace(0, np.pi, f)))
        r = ramp[:, None] if seg.ndim > 1 else ramp
        out[:f] *= r; out[-f:] *= r[::-1]
    return out


def build_parser():
    p = argparse.ArgumentParser(
        description="Find & extract loop-ready clips from a recording. "
                    "Run with --list first to preview, then for real.")
    p.add_argument("input", help="audio file to scan")
    p.add_argument("--list", action="store_true",
                   help="preview only: print what would be extracted, write no files")
    p.add_argument("--sensitivity", type=float, default=4.0, metavar="DB",
                   help="how far below the typical level still counts as sound; "
                        "raise to catch quieter sounds, lower to ignore them (default 4)")
    p.add_argument("--gap", type=float, default=0.08, metavar="SEC",
                   help="bridge silences shorter than this within one event; "
                        "raise to keep a swelly breath whole, lower to split finer (default 0.08)")
    p.add_argument("--min-dur", type=float, default=0.5, metavar="SEC",
                   help="shortest clip to keep (default 0.5)")
    p.add_argument("--core-db", type=float, default=10.0, metavar="DB",
                   help="trim each event to within this many dB of its own peak; "
                        "lower = tighter, steadier core (default 10)")
    p.add_argument("--bang-jump", type=float, default=15.0, metavar="DB",
                   help="a sudden level jump this big flags a junk transient to skip; "
                        "raise to be less aggressive (default 15)")
    p.add_argument("--keep-junk", action="store_true",
                   help="don't skip loud transients at all (keep everything)")
    p.add_argument("--max-clips", type=int, default=12, metavar="N",
                   help="keep at most this many, longest first (default 12)")
    p.add_argument("--peak-db", type=float, default=-3.0, metavar="DB",
                   help="normalize each clip to this peak level in dBFS (default -3)")
    p.add_argument("--fade-ms", type=float, default=6.0, metavar="MS",
                   help="edge fade length to avoid boundary clicks (default 6)")
    p.add_argument("--no-flatten", action="store_true",
                   help="keep the natural level shape; do NOT flatten the swell")
    p.add_argument("--as-float", action="store_true",
                   help="write 32-bit float WAV instead of 16-bit PCM")
    p.add_argument("--flat-db", type=float, default=2.0, metavar="DB",
                   help="internal wobble under this dB is labeled 'steady', else 'shaped' (default 2)")
    p.add_argument("--outdir", default=None, help="where to write clips (default: input's folder)")
    p.add_argument("--prefix", default=None, help="filename prefix (default: from the input name)")
    return p


def main():
    a = build_parser().parse_args()

    x, sr = sf.read(a.input, always_2d=True)
    mono = x.mean(axis=1)
    outdir = a.outdir or os.path.dirname(a.input) or "."
    prefix = a.prefix or os.path.splitext(os.path.basename(a.input))[0][:16]

    hop, rdb, cen = analyze(mono, sr)
    dt = hop/sr
    tof = lambda fr: fr*hop            # frame index -> sample index

    # --- exclude junk transients (mic bangs, bumps): sharp onset or way-loud ---
    med = np.median(rdb)
    if a.keep_junk:
        bang = np.zeros(len(rdb), dtype=bool)
    else:
        donset = np.diff(rdb, prepend=rdb[0])
        bang = (donset > a.bang_jump) | (rdb > med + 20)
        if bang.any():
            bw = int(0.5/dt)
            bang = np.convolve(bang.astype(float), np.ones(2*bw+1), 'same') > 0

    # --- floor + active mask; bridge brief dips so one event isn't split ---
    floor = (np.percentile(rdb[~bang], 50) - a.sensitivity) if (~bang).any() else med-10
    active = (rdb > floor) & (~bang)
    g = max(1, int(a.gap/dt))
    active = (np.convolve(active.astype(float), np.ones(2*g+1), 'same') > 0) & (~bang)

    events = runs_of(active, int(a.min_dur/dt))

    # --- each event -> loud core -> classify ---
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
    print(f"{'PREVIEW (no files written)' if a.list else 'keeping'}: {len(cands)} clip(s)\n")
    subtype = 'FLOAT' if a.as_float else 'PCM_16'
    for k, (c0, c1, nsamp, shape, bright) in enumerate(cands, 1):
        name = f"{prefix}_{shape}_{bright}_{k:02d}.wav"
        if not a.list:
            clip = make_clip(x[tof(c0):tof(c1)].astype(np.float64), sr,
                             do_flatten=not a.no_flatten, fade_ms=a.fade_ms, peak_dbfs=a.peak_db)
            sf.write(os.path.join(outdir, name), clip.astype(np.float32), sr, subtype=subtype)
        print(f"  {name:34s} [{tof(c0)/sr:6.1f}s]  {nsamp/sr:4.1f}s  {shape:6s} {bright}")
    if a.list:
        print("\n(preview only - nothing written. drop --list to extract.)")
    else:
        print(f"\nwrote to: {outdir}")


if __name__ == "__main__":
    main()
