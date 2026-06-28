#!/usr/bin/env python3
"""click_detect.py -- accessible QA for rendered audio.

Render a test from REAPER (a steady drone, or a parameter automation sweep),
then run this on the WAV. It prints a TEXT report of clicks, dropouts, and
amplitude pumping with timestamps -- so you can find glitches by reading
instead of listening for subtle artifacts.

    python tools/click_detect.py path/to/render.wav

Exit code is 0 if clean, 1 if anything was flagged (handy for scripting).
"""
import sys, math


def load_wav(path):
    # Try soundfile, then scipy, then stdlib wave (PCM only).
    try:
        import soundfile as sf
        import numpy as np
        x, sr = sf.read(path, always_2d=True)
        return np.asarray(x, dtype=float), sr
    except Exception:
        pass
    try:
        import numpy as np
        from scipy.io import wavfile
        sr, x = wavfile.read(path)
        x = np.asarray(x, dtype=float)
        if x.ndim == 1:
            x = x[:, None]
        # normalize integer PCM to [-1, 1]
        if np.issubdtype(np.dtype(x.dtype), np.integer) or abs(x).max() > 2:
            x = x / (abs(x).max() + 1e-12)
        return x, sr
    except Exception:
        pass
    import wave
    import numpy as np
    w = wave.open(path, "rb")
    sr = w.getframerate(); n = w.getnframes()
    ch = w.getnchannels(); sw = w.getsampwidth()
    raw = w.readframes(n); w.close()
    dt = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw)
    if dt is None:
        raise SystemExit(f"unsupported sample width {sw*8}-bit; install soundfile")
    x = np.frombuffer(raw, dtype=dt).astype(float).reshape(-1, ch)
    x = x / (float(2 ** (sw * 8 - 1)))
    return x, sr


def ts(n, sr):
    s = n / sr
    return f"{int(s // 60):d}:{s % 60:06.3f}"


def analyze(x, sr, name):
    import numpy as np
    out = []
    flagged = False
    mono = x
    peak = float(np.abs(mono).max()) + 1e-12
    # active region = where signal is meaningfully above the noise floor
    win = max(1, int(sr * 0.05))
    e = np.convolve(mono ** 2, np.ones(win) / win, mode="same")
    rms_w = np.sqrt(e)
    active = rms_w > 0.02 * np.median(rms_w[rms_w > 0]) if np.any(rms_w > 0) else rms_w > 0

    # --- clicks: 1st-difference outliers far above the local norm ---
    d = np.abs(np.diff(mono))
    med = np.median(d[d > 0]) + 1e-12
    thr = max(25 * med, 0.08 * peak)
    idx = np.where(d > thr)[0]
    # cluster samples within 5 ms into single events
    events = []
    gap = int(sr * 0.005)
    for i in idx:
        if events and i - events[-1][-1] <= gap:
            events[-1].append(i)
        else:
            events.append([i])
    clicks = [(grp[0], d[grp].max() / peak) for grp in events]
    if clicks:
        flagged = True
        out.append(f"  CLICKS: {len(clicks)}")
        for n0, mag in clicks[:25]:
            out.append(f"    {ts(n0, sr)}  jump {mag*100:.0f}% of peak")
        if len(clicks) > 25:
            out.append(f"    ... +{len(clicks)-25} more")
    else:
        out.append("  clicks: none")

    # --- dropouts: short near-silent gaps surrounded by signal ---
    sw = max(1, int(sr * 0.008))
    er = np.sqrt(np.convolve(mono ** 2, np.ones(sw) / sw, mode="same"))
    med_active = np.median(er[active]) if np.any(active) else 0.0
    drop = (er < 0.04 * med_active) & active if med_active > 0 else np.zeros_like(er, bool)
    # collapse to spans
    spans = []
    in_d = False
    for i, v in enumerate(drop):
        if v and not in_d:
            start = i; in_d = True
        elif not v and in_d:
            spans.append((start, i)); in_d = False
    spans = [(a, b) for a, b in spans if (b - a) > sr * 0.002]  # > 2 ms
    if spans:
        flagged = True
        out.append(f"  DROPOUTS: {len(spans)}")
        for a, b in spans[:25]:
            out.append(f"    {ts(a, sr)}  ({(b-a)/sr*1000:.0f} ms gap)")
    else:
        out.append("  dropouts: none")

    # --- amplitude pumping / churn over the active region ---
    if np.any(active):
        env = rms_w[active]
        churn = float(env.std() / (env.mean() + 1e-12))
        verdict = "steady" if churn < 0.08 else ("some movement" if churn < 0.2 else "PUMPING/churn")
        out.append(f"  level steadiness: {churn:.3f} ({verdict})")
        if churn >= 0.2:
            flagged = True
    return flagged, out


def main():
    if len(sys.argv) < 2:
        print(__doc__); raise SystemExit(2)
    path = sys.argv[1]
    x, sr = load_wav(path)
    print(f"{path}  ({sr} Hz, {x.shape[1]} ch, {x.shape[0]/sr:.2f} s)")
    any_flag = False
    chans = ["L", "R"] if x.shape[1] == 2 else [f"ch{i}" for i in range(x.shape[1])]
    for c, nm in enumerate(chans):
        print(f"[{nm}]")
        f, lines = analyze(x[:, c], sr, nm)
        any_flag = any_flag or f
        print("\n".join(lines))
    print("\nRESULT:", "ISSUES FLAGGED" if any_flag else "clean")
    raise SystemExit(1 if any_flag else 0)


if __name__ == "__main__":
    main()
