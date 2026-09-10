#!/usr/bin/env python3
"""Verify the Polyrhythm v1 -> v3 crossing by RENDERING, per instance.

usage: polyv1_to_v3_verify_20260910.py MANIFEST WORKDIR [--jobs N] [--skip-log LOG]

For each (converted, snapshot, count) row of the tab-separated manifest, every
instance is rendered three ways:

  A  old plugin on the snapshot                      -- what the project sounded like
  R  old plugin on a copy of the snapshot whose bank-bound slider values are
     rounded to float32                              -- what a v3 blob CAN hold
  B  new plugin on the converted file

R against B must be byte-identical, except for an instance with a voice between
notes (note + cents regroups the arithmetic), which must agree within TOLERANCE
and says so. A against R is reported as the size of the rounding. B must not be
silent unless A is.

--skip-log skips instances an earlier run already printed as OK, so a stopped
run resumes. Deliberately does NOT import the converter's mapping.
"""
import sys, subprocess, hashlib, struct, os, argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line, SliderLineError

REPO = Path(__file__).resolve().parent.parent
RUN = str(REPO / "tools/jsfx_run/build/Release/jsfx_run.exe")
V1 = str(REPO / "archive/versions/polyrhythm_phase/v2.jsfx")   # archived 2026-09-10
V3 = str(REPO / "src/polyrhythm_phase_v3.jsfx")
# v1 sliders whose values live in a float32 bank once converted, from the v1
# declarations: On Duration, Attack, Release, Tremolo amount, Waveform, the forty
# per-voice sliders, and the visible Drift/Ramp values a blob-less instance banks.
BANK_BOUND = [5, 6, 7, 10, 14] + list(range(20, 60)) + [75, 76, 77, 78, 80, 81, 83]
SECONDS = 10
TOLERANCE = 1e-6   # -120 dB; only ever applied to a between-notes instance


def f32(tok):
    x = struct.unpack("<f", struct.pack("<f", float(tok)))[0]
    return repr(x) if x != int(x) else str(int(x))


def rounded_copy(snapshot, dest):
    lines = Path(snapshot).read_bytes().decode("utf-8", errors="surrogateescape").splitlines(keepends=True)
    for i, l in enumerate(lines):
        if "<JS " in l and "polyrhythm_phase.jsfx" in l:
            try:
                slots = parse_line(lines[i + 1])
                n = 86 if max(k for k in slots) > 64 else 64
                for k in BANK_BOUND:
                    if slots.get(k) is not None:
                        slots[k] = f32(slots[k])
                lines[i + 1] = render_line(lines[i + 1], slots, n_sliders=n)
            except SliderLineError:
                body = lines[i + 1]
                eol = "\r\n" if body.endswith("\r\n") else "\n"
                indent = body[:len(body) - len(body.lstrip())]
                toks = body.split()
                for k in BANK_BOUND:
                    if k <= len(toks) and toks[k - 1] != "-":
                        toks[k - 1] = f32(toks[k - 1])
                lines[i + 1] = indent + " ".join(toks) + eol
    Path(dest).write_bytes("".join(lines).encode("utf-8", errors="surrogateescape"))


def has_between_notes_voice(snapshot, inst):
    lines = Path(snapshot).read_text(encoding="utf-8", errors="replace").splitlines()
    seen = 0
    for i, l in enumerate(lines):
        if "<JS " in l and "polyrhythm_phase.jsfx" in l:
            seen += 1
            if seen != inst:
                continue
            toks = lines[i + 1].split()
            for v in range(8):
                k = 21 + 5 * v
                if k <= len(toks) and toks[k - 1] != "-" and float(toks[k - 1]) != int(float(toks[k - 1])):
                    return True
            return False
    raise RuntimeError(f"instance {inst} not in {snapshot}")


def render(plugin, rpp, fx, inst, out):
    r = subprocess.run([RUN, plugin, "--rpp", rpp, "--fx", fx, "--instance", str(inst),
                        "--seconds", str(SECONDS), "--quiet", "--csv", out], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"jsfx_run failed on {rpp} #{inst}: {r.stderr.strip()[:200]}")
    data = Path(out).read_bytes()
    vals = np.loadtxt(out, delimiter=",", skiprows=1, usecols=(2, 3), dtype=np.float64)
    os.remove(out)
    return hashlib.sha1(data).hexdigest(), vals


def check_one(task):
    conv, snap, rounded, inst, work = task
    os.makedirs(work, exist_ok=True)
    ha, a = render(V1, snap, "polyrhythm_phase.jsfx", inst, f"{work}/a.csv")
    hr, r = render(V1, rounded, "polyrhythm_phase.jsfx", inst, f"{work}/r.csv")
    hb, b = render(V3, conv, "polyrhythm_phase_v3.jsfx", inst, f"{work}/b.csv")
    rounding = float(np.max(np.abs(a - r))) if a.shape == r.shape else float("inf")
    peak_a, peak_b = float(np.max(np.abs(a))), float(np.max(np.abs(b)))
    between = has_between_notes_voice(snap, inst)
    if hr == hb:
        verdict, ok = "identical", True
    else:
        gap = float(np.max(np.abs(r - b))) if r.shape == b.shape else float("inf")
        ok = between and gap < TOLERANCE
        verdict = f"differ by at most {gap:.2e}" + (" (between-notes voice)" if between else "")
    ok = ok and (peak_b > 0 or peak_a == 0)
    # The FULL path: several of Tensor's files share a name with Rozaya's, and a
    # name-only label once made a resume skip 14 instances nobody had checked.
    label = f"{conv} #{inst}"
    line = (f"{'OK  ' if ok else 'FAIL'} {label} :: rounded-old vs new {verdict}; "
            f"rounding {rounding:.2e}; peak old {peak_a:.4f} new {peak_b:.4f}")
    return ok, label, rounding, line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest"); ap.add_argument("work")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--skip-log")
    args = ap.parse_args()
    os.makedirs(args.work, exist_ok=True)
    skip = set()
    if args.skip_log and Path(args.skip_log).exists():
        for l in Path(args.skip_log).read_text(encoding="utf-8").splitlines():
            if l.startswith("OK   ") and " :: " in l:
                skip.add(l[5:].split(" :: ")[0])
    tasks, fails, skipped = [], [], 0
    for idx, row in enumerate(Path(args.manifest).read_text(encoding="utf-8").splitlines()):
        conv, snap, n = row.split("\t")
        n = int(n)
        text = Path(conv).read_text(encoding="utf-8", errors="replace").splitlines()
        n3 = sum(1 for l in text if "<JS " in l and "polyrhythm_phase_v3.jsfx" in l)
        n1 = sum(1 for l in text if "<JS " in l and "polyrhythm_phase.jsfx" in l)
        if n3 != n or n1 != 0:
            fails.append(f"{conv}: expected {n} v3 and 0 v1 instances, found {n3} and {n1}")
            continue
        rounded = f"{args.work}/rounded_{idx}.rpp"
        rounded_copy(snap, rounded)
        for inst in range(1, n + 1):
            if f"{conv} #{inst}" in skip:
                skipped += 1
                continue
            tasks.append((conv, snap, rounded, inst, f"{args.work}/job_{idx}_{inst}"))
    print(f"{len(tasks)} instances to render, {skipped} already OK in the earlier run", flush=True)
    worst, done = 0.0, 0
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for fut in as_completed([ex.submit(check_one, t) for t in tasks]):
            ok, label, rounding, line = fut.result()
            done += 1
            worst = max(worst, rounding)
            print(line, flush=True)
            if not ok:
                fails.append(label)
    print(f"\n{done} rendered now + {skipped} earlier = {done + skipped}; worst rounding this run {worst:.2e}; {len(fails)} failed")
    for f in fails: print("  FAIL", f)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
