"""Stage 6 on the SCRATCH copy that already has stage 5: apply the save-format patch, lint,
compile, then save a fresh instance and reopen it, reading every control back in each view.
Nothing in the repo is written."""
import os, re, subprocess, sys

S = "C:/Users/solst/AppData/Local/Temp/claude/C--git-src-rozaya-jsfx/e718f425-9d04-4c43-8dd5-eb0cd1fae327/scratchpad"
ROOT = "C:/git-src/rozaya-jsfx"
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
trial = os.path.join(S, "stage5_trial.jsfx")
pre6 = open(trial, encoding="utf-8", newline="").read()
assert "au_key(" in pre6 and "ser_magic = 7700055;" in pre6, "the trial copy must hold stage 5 and not stage 6"

patch = open(os.path.join(S, "stage6_saveformat.py"), encoding="utf-8").read()
real = 'p = "C:/git-src/rozaya-jsfx/src/spectral_vowel_morpher.jsfx"'
assert patch.count(real) == 1
exec(compile(patch.replace(real, f"p = {trial!r}"), "stage6_saveformat", "exec"), {})

lint = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "jsfx_lint.py"), trial], capture_output=True, text=True)
print("lint:", " | ".join(lint.stdout.strip().splitlines()[-2:]))

sys.argv = ["x"]
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_verify_20260913 as V

new = V.pinned(open(trial, encoding="utf-8").read(), "trial6.jsfx")
pre = V.pinned(pre6, "trial5.jsfx")
fails = 0
for end, tail in (("Layer 3", []), ("All", [[(V.LAYER, 0)]])):
    stages = V.SAVE_STAGES + tail
    s = os.path.join(V.tmp, f"t6-{end.replace(' ', '')}.RPP")
    V.save(new, stages, s)
    magic = V.blob_of(s, 1)[4][0]
    print(f"{'ok  ' if magic == 7700087.0 else 'FAIL'} saved on {end}: blob magic {magic:.0f}")
    fails += magic != 7700087.0
    for vname, view in V.VIEWS.items():
        want = V.listing(new, stages + view)
        got = V.listing(new, view, rpp=s)
        diff = sorted(k for k in want if k != V.CAPTURE and want[k] != got.get(k))
        ok = not diff and len(want) == 64
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} saved on {end}, reopened, {vname}: {len(want) - 1} controls as before"
              + (f" -- DIFFER at {[(k, want[k], got.get(k)) for k in diff]}" if diff else ""))
    old = V.listing(pre, V.VIEWS["Layer 14"], rpp=s)
    want = V.listing(new, stages + V.VIEWS["Layer 14"])
    canfail = any(want[k] != old.get(k) for k in (V.L_PITCH, V.L_PUNIT, V.L_FINE, V.L_FUNIT))
    fails += not canfail
    print(f"{'ok  ' if canfail else 'FAIL'} saved on {end}: the stage-5 build reopens Layer 14 without its pitch (the check can fail)")
    s2 = os.path.join(V.tmp, f"t6b-{end.replace(' ', '')}.RPP")
    V.save(new, [], s2, rpp=s)
    same = open(s, "rb").read() == open(s2, "rb").read()
    fails += not same
    print(f"{'ok  ' if same else 'FAIL'} saved on {end}, reopened and saved again: byte-identical")
print(f"stage 6 trial: {fails} failures")
