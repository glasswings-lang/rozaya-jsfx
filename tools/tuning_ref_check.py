"""Does each plugin's Tuning reference actually move its pitch? Measured, not read.

THE TEST IS AN EQUIVALENCE, NOT A PITCH READING. Doubling the reference must
sound EXACTLY like raising a note an octave: 880 * 2^((57-69)/12) and
440 * 2^((69-69)/12) are the same double, so the two renders must be
bit-identical. That holds for noise as much as tone -- a first version measured
pitch from the spectrum, and on Dapple's noise it could not even see a two
semitone note change (2026-09-10).

For each plugin:
  moves        reference 440 and 880 on the same note render DIFFERENTLY
  from start   (note, ref 880)  ==  (note + octave, ref 440), bit for bit
  while playing  start at (note, 440); two seconds in, move the reference to 880
               ==  start at (note, 440); two seconds in, move the note up an octave
  Hz ignores it  in plain Hz, reference 440 and 880 render bit-identically

Bubbler and the Sustain Looper take a SHIFT, where the reference matters only for
a shift said in Hz, measured from it: +200 Hz from 880 is the same ratio as +100
Hz from 440, so those are the pair.

The Shepards have no note to raise, so they keep a spectrum reading: their tones
are clean enough for it. Expected +200.4 cents for 440 -> 494.

    python tools/tuning_ref_check.py            # every plugin
    python tools/tuning_ref_check.py dapple     # names containing "dapple"
"""
import math, os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
SR, BLOCK, SECONDS, MOVE_AT = 44100, 512, 8.0, 2.0
LOOPER_RPP = "E:/reaper/finished/energy healing vol. 2.RPP"
DATA_ROOT = "C:/Users/solst/AppData/Roaming/REAPER/Data"

def notes(*triples, up=0):
    """(mode slider, name slider, value slider, midi note) -> settings, note mode."""
    out = []
    for m, n, v, note in triples:
        out += [(m, 1), (n, note + up), (v, note + up)]
    return out

# a / b: settings such that (a, ref 880) must equal (b, ref 440).
# pre: set before init (selectors). hz: settings where the reference must not matter.
CASES = [
    dict(name="breath_gen", file="breath_gen.jsfx", ref=13,
         a=notes((8, 9, 10, 57)), b=notes((8, 9, 10, 57), up=12), hz=[]),
    dict(name="dapple", file="dapple.jsfx", ref=9,
         a=notes((4, 5, 6, 57)), b=notes((4, 5, 6, 57), up=12), hz=[]),
    dict(name="heartbeat", file="heartbeat gen.jsfx", ref=15, pre=[(9, 0)],
         # 57, not 45: on All, a value equal to the one shown writes nothing, so
         # 45 left S2 at 120 -- a note near 8.4 kHz, where Heartbeat blows up.
         a=notes((10, 11, 12, 57)), b=notes((10, 11, 12, 57), up=12), hz=[]),
    dict(name="melody", file="melody_phase.jsfx", ref=7,
         a=[(8, -12)], b=[(8, 0)], hz=[(5, 0)]),
    dict(name="polyrhythm_v3", file="polyrhythm_phase_v3.jsfx", ref=6,
         a=[(7, -12)], b=[(7, 0)], hz_pre=[(15, 0)], hz=[(16, 0)]),
    dict(name="rhythm_track", file="rhythm-track.jsfx", ref=11,
         a=notes((6, 7, 8, 69)), b=notes((6, 7, 8, 69), up=12), hz=[]),
    dict(name="sweep_dwell", file="sweep-dwell-filter.jsfx", ref=55, input="noise",
         a=notes((1, 2, 3, 57), (6, 7, 8, 81)),
         b=notes((1, 2, 3, 57), (6, 7, 8, 81), up=12), hz=[]),
    dict(name="womb", file="womb_sound_generator_v3.jsfx", ref=63,
         a=notes((6, 7, 8, 33), (13, 14, 15, 45), (30, 31, 32, 57), (35, 36, 37, 52)),
         b=notes((6, 7, 8, 33), (13, 14, 15, 45), (30, 31, 32, 57), (35, 36, 37, 52), up=12),
         hz=[]),
    dict(name="bubbler", file="bubbler.jsfx", ref=10,
         a=[(7, 0), (6, 200)], b=[(7, 0), (6, 100)], hz=[(7, 1), (6, 5)]),
    dict(name="sustain_looper", file="sustain_looper.jsfx", ref=11,
         rpp=LOOPER_RPP, fx="sustain_looper",
         a=[(8, 0), (7, 200)], b=[(8, 0), (7, 100)], hz=[(8, 1), (7, 5)]),
    dict(name="shepard_scale", file="shepard-scale.jsfx", ref=13, spectral=True),
    dict(name="shepard_tone", file="shepard-tone.jsfx", ref=12, spectral=True),
]

def render(c, tmp, tag, pre=(), first=(), later=()):
    out = os.path.join(tmp, f"{c['name']}-{tag}.csv")
    cmd = [EXE, os.path.join(ROOT, "src", c["file"]), "--sr", str(SR), "--block",
           str(BLOCK), "--seconds", str(SECONDS), "--csv", out, "--quiet"]
    if "rpp" in c:
        cmd += ["--rpp", c["rpp"], "--fx", c["fx"], "--data-root", DATA_ROOT]
    if "input" in c:
        cmd += ["--input", c["input"]]
    for s, v in pre:
        cmd += ["--slider", f"{s}={v}"]
    for s, v in first:
        cmd += ["--set-after", f"{s}={v}"]
    if later:
        cmd += ["--stage"] * int(MOVE_AT * SR / BLOCK)
        for s, v in later:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"jsfx_run failed on {tag}\n{r.stderr[-600:]}")
    return np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))

def log_spectrum(x):
    grid = np.exp(np.linspace(math.log(40), math.log(10000), int(1200 * math.log2(250))))
    n = 1 << 16
    w = np.hanning(n)
    mag = np.mean([np.abs(np.fft.rfft(x[i:i + n] * w)) ** 2
                   for i in range(0, len(x) - n + 1, n // 2)], axis=0)
    db = 10 * np.log10(mag + 1e-20)
    g = np.interp(grid, np.fft.rfftfreq(n, 1 / SR), np.maximum(db, db.max() - 70))
    return g - g.mean()

def shift_cents(a, b, span=450):
    score = lambda lag: (np.dot(a[:len(a) - lag], b[lag:]) if lag >= 0 else
                         np.dot(a[-lag:], b[:len(b) + lag])) / (len(a) - abs(lag))
    return max(range(-span, span + 1), key=score)

def verdict(ok):
    return "PASS" if ok else "FAIL"

def check(c, tmp):
    ref, pre, lines = c["ref"], c.get("pre", []), []
    if c.get("spectral"):
        a = render(c, tmp, "440", pre, [(ref, 440)])
        if not np.abs(a).max():
            return False, [f"{c['name']}: SILENT, nothing was measured"]
        sa = log_spectrum(a[int(3 * SR):].mean(axis=1))
        ok = True
        for tag, first, later in (("from the start", [(ref, 494)], ()),
                                  ("while playing", [(ref, 440)], [(ref, 494)])):
            b = render(c, tmp, tag.replace(" ", "_"), pre, first, later)
            got = shift_cents(sa, log_spectrum(b[int(3 * SR):].mean(axis=1)))
            ok &= abs(got - 200) <= 6
            lines.append(f"{c['name']}: 440 to 494 {tag}: moved {got:+d} cents, "
                         f"expected +200 -- {verdict(abs(got - 200) <= 6)}")
        return ok, lines

    a440 = render(c, tmp, "a440", pre, c["a"] + [(ref, 440)])
    a880 = render(c, tmp, "a880", pre, c["a"] + [(ref, 880)])
    b440 = render(c, tmp, "b440", pre, c["b"] + [(ref, 440)])
    if not np.abs(a440).max():
        return False, [f"{c['name']}: SILENT, nothing was measured"]
    moves = not np.array_equal(a440, a880)
    start = np.array_equal(a880, b440)
    lines.append(f"{c['name']}: the reference changes the sound: {verdict(moves)}")
    lines.append(f"{c['name']}: doubling it equals an octave up, from the start: {verdict(start)}"
                 + ("" if start else f" (largest sample gap {np.abs(a880 - b440).max():.3g})"))
    live_ref = render(c, tmp, "live_ref", pre, c["a"] + [(ref, 440)], [(ref, 880)])
    live_note = render(c, tmp, "live_note", pre, c["a"] + [(ref, 440)], c["b"])
    live = np.array_equal(live_ref, live_note)
    gap = np.abs(live_ref - live_note)
    lines.append(f"{c['name']}: same, moved while playing: {verdict(live)}"
                 + ("" if live else f" (largest sample gap {gap.max():.3g}, first at "
                    f"{np.argmax(gap.max(axis=1) > 0) / SR:.2f} s)"))
    ok = moves and start and live
    if c.get("hz") is not None:
        hp = pre + c.get("hz_pre", [])
        h1 = render(c, tmp, "hz440", hp, c["hz"] + [(ref, 440)])
        h2 = render(c, tmp, "hz880", hp, c["hz"] + [(ref, 880)])
        same, loud = np.array_equal(h1, h2), bool(np.abs(h1).max())
        ok &= same and loud
        lines.append(f"{c['name']}: in plain Hz the reference changes nothing: "
                     f"{verdict(same and loud)}" + ("" if loud else " (silent, not measured)"))
    return ok, lines

def main():
    pick = sys.argv[1:]
    cases = [c for c in CASES if not pick or any(p in c["name"] for p in pick)]
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        for c in cases:
            try:
                ok, lines = check(c, tmp)
            except Exception as e:
                ok, lines = False, [f"{c['name']}: ERROR {e}"]
            fails += not ok
            print("\n".join(lines), flush=True)
    print(f"\n{len(cases) - fails} of {len(cases)} plugins pass.")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
