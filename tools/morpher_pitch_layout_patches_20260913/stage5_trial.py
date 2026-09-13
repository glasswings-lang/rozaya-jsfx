"""Stage 5 on a SCRATCH copy of src: apply the patch, lint, compile, and read the unit
conversions out of a debug copy. Nothing in the repo is written."""
import os, re, shutil, subprocess, sys
import numpy as np

S = "C:/Users/solst/AppData/Local/Temp/claude/C--git-src-rozaya-jsfx/e718f425-9d04-4c43-8dd5-eb0cd1fae327/scratchpad"
ROOT = "C:/git-src/rozaya-jsfx"
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
trial = os.path.join(S, "stage5_trial.jsfx")
shutil.copyfile(os.path.join(ROOT, "src", "spectral_vowel_morpher.jsfx"), trial)

# The patch script, pointed at the trial copy.
patch = open(os.path.join(S, "stage5_units.py"), encoding="utf-8").read()
real = 'p = "C:/git-src/rozaya-jsfx/src/spectral_vowel_morpher.jsfx"'
assert patch.count(real) == 1
exec(compile(patch.replace(real, f"p = {trial!r}"), "stage5_units", "exec"), {})

lint = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "jsfx_lint.py"), trial], capture_output=True, text=True)
print("lint:", " | ".join(lint.stdout.strip().splitlines()[-2:]))
lst = subprocess.run([EXE, trial, "--seconds", "0.05", "--list"], capture_output=True, text=True)
print("compiles:", lst.returncode == 0 and "loaded and compiled" in lst.stdout,
      "| slider49:", re.search(r"slider49\s+(.*?)\s+\[", lst.stdout).group(1) if "slider49" in lst.stdout else None)

sys.argv = ["x"]
sys.path.insert(0, os.path.join(ROOT, "tools"))
import morpher_verify_20260913 as V

src = open(trial, encoding="utf-8", newline="").read()
cut = src.index("\r\n@serialize\r\n")
cases = ["tempo"] + [f"{fn}({off}, {u}, {base}, {nu})" for fn, off, u, base, nu, _, _ in V.CONV]
chain = "".join(f"cv_i == {i} ? {c} : " for i, c in enumerate(cases)) + "0"
dbg = src[:cut] + ("\r\ntuning_ref = 440; au_cyc = 20;\r\n" f"spl0 = {chain};\r\nspl1 = 0; cv_i += 1;\r\n") + src[cut:]
p = V.pinned(dbg, "trial_convert.jsfx")
out = os.path.join(V.tmp, "trial_convert.csv")
r = subprocess.run([EXE, p, "--seconds", "0.01", "--csv", out, "--quiet"], capture_output=True, text=True)
if r.returncode:
    raise SystemExit(r.stderr[-600:])
vals = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2,))[:len(cases)]
tempo = float(vals[0])
bad = 0
for (fn, off, u, base, nu, want, label), got in zip(V.CONV, vals[1:]):
    if want is None:
        want = (base + off * 60 / tempo) - base
    ok = abs(got - want) < 1e-4
    bad += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {label}: got {got:.6g}, want {want:.6g}")
print(f"convert on the trial copy: {len(V.CONV) - bad} of {len(V.CONV)} equal the worked answers (tempo {tempo})")
