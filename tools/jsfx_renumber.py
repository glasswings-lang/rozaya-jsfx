"""Renumber a plugin's sliders from an AUTHORED map, and prove nothing moved.

A script may APPLY an authored list; it may never INFER one. The map is written
by hand, in the layout doc, and passed here verbatim.

    python tools/jsfx_renumber.py apply  src/x.jsfx  "55:11, 11-54:+1"
    python tools/jsfx_renumber.py verify OLD.jsfx NEW.jsfx "55:11, 11-54:+1" [--input noise]

`apply` rewrites every `sliderN` token in the file -- declarations, code and
comments alike -- in ONE pass, so a chain like 11->12->13 cannot happen. It
refuses a map that sends two old ids to one new id. It does not move declaration
lines; REAPER orders by id, not file position.

`verify` is for a PURE renumber. Three checks, strongest first:
  1. TEXT: the new file holds exactly the lines of the mapped old file, in any
     order. Any hand edit beyond moving whole lines fails here. This is the check
     that catches a single code reference pointed at the wrong slider -- the
     render checks below did NOT, on 2026-09-10, because a wrong tuning reference
     read is inaudible once the test values have pushed the pitch to its clamp.
  2. DECLARATIONS: names, ranges and defaults match id-for-id through the map.
  3. RENDER, two passes, bit-identical: every continuous slider nudged 20% off
     its default with selectors left alone; then every selector moved one step
     with continuous sliders left alone. Small nudges, so times and pitches stay
     in a range a short render can hear. Reported with whether output was silent.
A plugin that is renumbered AND edited should be verified against real projects
instead (old plugin on old project, new plugin on migrated project).
"""
import collections, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
DECL = re.compile(r"^slider(\d+):([^<]*)<([^>]*)>(.*)$")

def parse_map(text):
    m = {}
    for part in [p.strip() for p in text.split(",") if p.strip()]:
        a, b = part.split(":")
        if "-" in a:
            lo, hi = map(int, a.split("-"))
            for i in range(lo, hi + 1):
                m[i] = i + int(b)
        else:
            m[int(a)] = int(b)
    return m

def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()

def declarations(text):
    out = {}
    for line in text.splitlines():
        d = DECL.match(line)
        if d:
            out[int(d.group(1))] = (d.group(2), d.group(3), d.group(4))
    return out

def full_map(m, ids):
    fm = {i: m.get(i, i) for i in ids}
    targets = list(fm.values())
    dup = {t for t in targets if targets.count(t) > 1}
    if dup:
        raise SystemExit(f"refusing: more than one slider would become {sorted(dup)}")
    return fm

def mapped_text(text, m):
    fm = full_map(m, declarations(text).keys())
    return re.sub(r"\bslider(\d+)\b",
                  lambda x: f"slider{fm.get(int(x.group(1)), int(x.group(1)))}", text), fm

def apply(path, m):
    new, fm = mapped_text(read(path), m)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print(f"{path}: {sum(1 for k, v in fm.items() if k != v)} slider ids renumbered, {len(fm)} declared")

def nudged(default, rng, which):
    spec = rng.split("{")[0].split(",")
    lo, hi = float(spec[0]), float(spec[1])
    step = float(spec[2]) if len(spec) > 2 else 0
    selector = "{" in rng or step >= 1
    d = float(default)
    if selector:
        if which != "selectors":
            return None
        return d + 1 if d + 1 <= hi else d - 1
    if which != "continuous":
        return None
    v = d * 0.8 if d != 0 else lo + (hi - lo) * 0.02
    return round(max(lo, min(hi, v)), 3)

def render(plugin, assigns, tmp, tag, extra):
    out = os.path.join(tmp, tag + ".csv")
    cmd = [EXE, plugin, "--seconds", "8", "--csv", out, "--quiet"] + extra
    for s, v in assigns:
        cmd += ["--slider", f"{s}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-500:])
    return read(out)

def verify(old, new, m, extra):
    to, tn = read(old), read(new)
    mt, fm = mapped_text(to, m)
    a_lines, b_lines = collections.Counter(mt.splitlines()), collections.Counter(tn.splitlines())
    text_ok = a_lines == b_lines
    print(f"  1. text is the mapped old file, lines in any order: {'PASS' if text_ok else 'FAIL'}")
    if not text_ok:
        for l in list((a_lines - b_lines).elements())[:5]:
            print(f"       expected: {l.strip()[:110]}")
        for l in list((b_lines - a_lines).elements())[:5]:
            print(f"       found:    {l.strip()[:110]}")
    do, dn = declarations(to), declarations(tn)
    bad = [k for k in do if dn.get(fm[k]) != do[k]]
    decl_ok = not bad and len(dn) == len(do)
    print(f"  2. names, ranges and defaults match through the map: {'PASS' if decl_ok else 'FAIL'}"
          + ("" if decl_ok else f" ({len(bad)} mismatched, e.g. old slider{bad[0] if bad else '?'})"))
    render_ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for which in ("continuous", "selectors"):
            vals = {k: nudged(do[k][0], do[k][1], which) for k in do if not do[k][0].startswith("/")}
            vals = {k: v for k, v in vals.items() if v is not None}
            a = render(old, list(vals.items()), tmp, "old", extra)
            b = render(new, [(fm[k], v) for k, v in vals.items()], tmp, "new", extra)
            loud = any(x.split(",")[2] not in ("0", "0.0", "-0") for x in a.splitlines()[1:2000:7])
            same = a == b
            render_ok &= same and loud
            print(f"  3. {len(vals)} {which} moved, renders bit-identical: {'PASS' if same else 'FAIL'}"
                  f" ({'non-zero output' if loud else 'SILENT -- proves nothing'})")
    return text_ok and decl_ok and render_ok

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "apply":
        apply(sys.argv[2], parse_map(sys.argv[3]))
    elif cmd == "verify":
        sys.exit(0 if verify(sys.argv[2], sys.argv[3], parse_map(sys.argv[4]), sys.argv[5:]) else 1)
    else:
        raise SystemExit(__doc__)
