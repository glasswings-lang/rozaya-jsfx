#!/usr/bin/env python3
"""Every plugin with a Source note must treat it the same way, measured.

Source note only says where zero is, for the note names. Rozaya, 2026-09-11:
"The source note is just to tell the targget what 0 semitones is though". So,
in every plugin that has one:

  audible   the scenario renders sound, and the same run twice is identical
  can-fail  Target F#4 sounds different from Target E4 (else nothing below counts)
  keeps     Source C4 -> D4 after Target E4 leaves the sound bit-identical
  re-reads  after that move, picking E4 again == Transpose 2 -- which is only
            true if the Target note had moved off E4 when the Source moved

Built because Passage re-read the Target and Bubbler and Sustain Looper did not,
and nothing compared them. A plugin that gains a Source note belongs in PLUGINS.

    python tools/source_note_check.py [plugin ...] [--rev GITREV]

--rev tests the plugins as they were at that commit (proves the check can fail).
"""
import os, subprocess, sys, tempfile, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
REV = sys.argv[sys.argv.index("--rev") + 1] if "--rev" in sys.argv else None
tmp = tempfile.mkdtemp()

# A sample for Sustain Looper, which renders silence without a file to load.
DATA = os.path.join(tmp, "data")
os.makedirs(os.path.join(DATA, "glasswings_samples"))
with wave.open(os.path.join(DATA, "glasswings_samples", "tone.wav"), "wb") as w:
    t = np.arange(48000 * 3) / 48000
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
    w.writeframes((np.sin(2 * np.pi * 220 * t) * 16000).astype("<i2").tobytes())

SINE = ["--input", "sine", "--input-hz", "220", "--input-db", "-6"]
# src/tgt/tv: slider numbers of Source note, Target note, Transpose value.
# lead: stages before the scenario (Passage must capture before it sounds).
PLUGINS = {
    "bubbler": dict(src=4, tgt=5, tv=6, block=8192, seconds=6, lead=[], args=SINE),
    "sustain_looper": dict(src=5, tgt=6, tv=7, block=8192, seconds=6, lead=[],
                           args=SINE + ["--data-root", DATA]),
    # Audition = Morph, Morph parked on Slot 1, capture into Slot 1.
    "spectral_vowel_passage": dict(src=5, tgt=8, tv=9, block=32768, seconds=16,
                                   lead=[[(36, 1), (34, 0), (1, 1)], [(2, 1)]], args=SINE, pin=True),
}
C4, D4, E4, FS4 = 61, 63, 64, 66   # Source note counts None as 0; Target note does not
E4_T, FS4_T = 64, 66
fails = 0


def report(ok, text):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {text}", flush=True)


def plugin_file(name, p):
    text = (subprocess.run(["git", "show", f"{REV}:src/{name}.jsfx"], cwd=ROOT, capture_output=True,
                           check=True).stdout.decode("utf-8") if REV else
            open(os.path.join(ROOT, "src", f"{name}.jsfx"), encoding="utf-8").read())
    if p.get("pin"):
        # Passage scrambles rand() per load; pin it in the test copy or no two runs match.
        if text.count("_tp = time_precise();") != 1:
            raise SystemExit(f"{name}: the load-time scramble line is not there exactly once")
        text = text.replace("_tp = time_precise();", "_tp = 0.25;")
    path = os.path.join(tmp, f"{name}.jsfx")
    open(path, "w", encoding="utf-8", newline="").write(text)
    return path


def render(path, p, steps):
    stages = [list(s) for s in p["lead"]] + [list(s) for s in steps] + [[]] * 5
    out = os.path.join(tmp, "out.csv")
    cmd = [EXE, path, "--seconds", str(p["seconds"]), "--csv", out, "--quiet",
           "--block", str(p["block"]), *p["args"]]
    for k, st in enumerate(stages):
        if k:
            cmd += ["--stage"]
        for s, v in st:
            cmd += ["--set-after", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-800:])
    a = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3))
    return a[(len(stages) + 2) * p["block"]:]


def check(name):
    p = PLUGINS[name]
    path = plugin_file(name, p)
    S, T, V = p["src"], p["tgt"], p["tv"]
    # Every scenario has four stages, and each move lands on the same stage in all of them.
    stay = render(path, p, [[(S, C4)], [(T, E4_T)], [], []])
    again = render(path, p, [[(S, C4)], [(T, E4_T)], [], []])
    report(np.array_equal(stay, again) and np.abs(stay).max() > 0,
           f"{name}: audible, and the same run twice is identical")
    other = render(path, p, [[(S, C4)], [(T, E4_T)], [(T, FS4_T)], []])
    report(not np.array_equal(stay, other), f"{name}: can-fail -- Target F#4 sounds different from E4")
    moved = render(path, p, [[(S, C4)], [(T, E4_T)], [(S, D4)], []])
    report(np.array_equal(stay, moved), f"{name}: Source C4 -> D4 leaves the sound identical")
    repick = render(path, p, [[(S, C4)], [(T, E4_T)], [(S, D4)], [(T, E4_T)]])
    by2 = render(path, p, [[(S, C4)], [(T, E4_T)], [(S, D4)], [(V, 2)]])
    report(np.array_equal(repick, by2) and not np.array_equal(repick, moved),
           f"{name}: after Source D4, picking E4 again == Transpose 2 (the Target name had moved)")


names = [a for a in sys.argv[1:] if not a.startswith("--") and a != REV] or list(PLUGINS)
for n in names:
    check(n)
print(f"\n{fails} failure(s)" + (f" at {REV}" if REV else ""))
sys.exit(1 if fails else 0)
