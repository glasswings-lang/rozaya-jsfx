#!/usr/bin/env python3
"""Verify the Breath Generator layout migration against a PRE-migration snapshot.

Decodes by control NAME, not by re-applying the migration's own table -- a
verifier built on the same table agrees with itself perfectly and proves
nothing. It also range-checks every migrated value against the NEW slider
declarations parsed out of src/breath_gen.jsfx, and separates "was already out
of range" from "is out of range now".

    python tools/breathgen_verify_layout_20260908.py <snapshot-dir> <live-dir-or-files...>
"""
import base64, math, re, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line   # noqa: E402

TUNING = 440.0

OLD_NAMES = {1: "Inhale", 2: "Top pause", 3: "Exhale", 4: "Bottom pause",
             5: "Inhale Hz", 6: "Exhale Hz", 7: "Inhale fade in",
             8: "Inhale fade out", 9: "Exhale fade in", 10: "Exhale fade out",
             11: "Fade mode", 12: "Stereo width", 13: "Stereo flip",
             14: "Start delay", 15: "Play for", 16: "Rest for",
             17: "Drift target", 18: "Drift up", 19: "Drift down",
             20: "Drift period", 21: "Drift period unit", 22: "Drift shape",
             23: "Drift play for", 24: "Drift rest for", 25: "Ramp target",
             26: "Ramp by", 27: "Ramp time unit", 28: "Ramp duration",
             29: "Ramp play for", 30: "Ramp rest for", 31: "Ramp engage",
             32: "Ramp start delay"}
NEW_NAMES = {3: "Inhale", 4: "Top pause", 5: "Exhale", 6: "Bottom pause",
             14: "Inhale fade in", 15: "Inhale fade out", 16: "Exhale fade in",
             17: "Exhale fade out", 18: "Fade mode", 19: "Stereo width",
             20: "Stereo flip", 22: "Start delay", 23: "Play for",
             24: "Rest for", 25: "Drift target", 26: "Drift up",
             27: "Drift down", 28: "Drift period", 29: "Drift period unit",
             30: "Drift shape", 31: "Drift play for", 32: "Drift rest for",
             33: "Ramp target", 34: "Ramp by", 35: "Ramp time unit",
             36: "Ramp duration", 37: "Ramp play for", 38: "Ramp rest for",
             39: "Ramp engage", 40: "Ramp start delay"}


def declared_ranges(src=Path("src/breath_gen.jsfx")):
    out = {}
    for m in re.finditer(r"^slider(\d+):([-\d.]+)<([-\d.]+),([-\d.]+),",
                         src.read_text(encoding="utf-8"), re.M):
        out[int(m.group(1))] = (float(m.group(3)), float(m.group(4)))
    return out


def instances(path):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    for i, l in enumerate(lines):
        if "breath_gen.jsfx" not in l:
            continue
        vi = next(j for j in range(i + 1, i + 6)
                  if lines[j].strip() and (lines[j].strip()[0].isdigit()
                                           or lines[j].strip()[0] in '-"'))
        blob = None
        for j in range(vi, min(vi + 6, len(lines))):
            if lines[j].strip().startswith("<JS_SER"):
                b, k = "", j + 1
                while lines[k].strip() != ">":
                    b += lines[k].strip()
                    k += 1
                blob = b
                break
        yield parse_line(lines[vi]), blob


def pitch_from_blob(blob):
    raw = base64.b64decode(blob)
    v = struct.unpack("<" + "f" * (len(raw) // 4), raw)
    assert abs(v[0] - 2300005.0) < 0.5, f"magic is {v[0]}, expected 2300005"
    base = 1 + 16 + 21 + 20          # sr(16) + drift(21) + play/rest(20)
    note = v[base:base + 3]
    val = v[base + 3:base + 6]
    mode = v[base + 6:base + 9]
    return note, val, mode


def hz(note, val):
    return TUNING * 2 ** ((note - 69) / 12.0) + val


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    snap = Path(sys.argv[1])
    live = [Path(p) for p in sys.argv[2:]]
    rng = declared_ranges()
    checks = fails = 0

    for lp in live:
        sp = snap / (lp.parent.name + "__" + lp.name)
        if not sp.exists():
            print(f"NO SNAPSHOT for {lp} (looked for {sp.name})")
            fails += 1
            continue
        olds = list(instances(sp))
        news = list(instances(lp))
        if len(olds) != len(news):
            print(f"FAIL {lp.name}: {len(olds)} instances before, {len(news)} after")
            fails += 1
            continue
        print(f"\n{lp.name}: {len(news)} instance(s)")
        for k, ((o, _ob), (n, nb)) in enumerate(zip(olds, news), 1):
            # 1. every named control kept its value
            back = {v: kk for kk, v in NEW_NAMES.items()}
            for oid, name in OLD_NAMES.items():
                if name in ("Inhale Hz", "Exhale Hz"):
                    continue
                nid = back[name]
                ov, nv = o.get(oid), n.get(nid)
                checks += 1
                if (ov is None) != (nv is None) or (ov is not None and float(ov) != float(nv)):
                    print(f"  FAIL inst {k}: {name}: was {ov!r} (slider {oid}),"
                          f" now {nv!r} (slider {nid})")
                    fails += 1
            # 2. the two frequencies survive through the pitch block
            note, val, _ = pitch_from_blob(nb)
            for label, oid, slot in (("inhale", 5, 1), ("exhale", 6, 2)):
                want = float(o.get(oid) or (800.0 if oid == 5 else 600.0))
                got = hz(note[slot], val[slot])
                checks += 1
                if abs(got - want) > 1e-4:
                    print(f"  FAIL inst {k}: {label} {want} Hz -> {got} Hz")
                    fails += 1
            # 3. range-check, separating pre-existing from newly-introduced
            for nid, nv in n.items():
                if nv is None or nid not in rng:
                    continue
                lo, hi_ = rng[nid]
                checks += 1
                if not (lo - 1e-9 <= float(nv) <= hi_ + 1e-9):
                    name = NEW_NAMES.get(nid, f"slider{nid}")
                    oid = {v: kk for kk, v in OLD_NAMES.items()}.get(name)
                    pre = oid is not None and o.get(oid) == nv
                    tag = "was ALREADY out of range" if pre else "OUT OF RANGE NOW"
                    print(f"  {'note' if pre else 'FAIL'} inst {k}: {name} = {nv}"
                          f" against [{lo}, {hi_}] -- {tag}")
                    if not pre:
                        fails += 1
            print(f"  instance {k}: inhale {hz(note[1], val[1]):.4f} Hz,"
                  f" exhale {hz(note[2], val[2]):.4f} Hz")

    print(f"\n{checks} checks, {fails} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
