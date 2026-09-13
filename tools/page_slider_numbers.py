#!/usr/bin/env python3
"""Do the slider numbers written on the plugin pages still name the right control?

The pages say things like **Ramp by (per target, slider 30)**. Every reorder moves the
controls and nothing moved the numbers: on 2026-09-13, 56 of 62 such entries named a
control that had since moved, some to a slider three or four places away.

Four shapes are read, each naming a control and a number together:
  **Name (..., slider N ...)**          **Name ...** `range` (slider N)
  ### Name (slider N)                   slider N — Name
The control is found in src/ by its declared label (the name, or the name followed by
" ("). History ("sat at slider 27 until ...") is none of these shapes and is left alone;
every other "slider N" on a page is printed for reading by hand.

    python tools/page_slider_numbers.py          # report only
    python tools/page_slider_numbers.py --fix    # rewrite a wrong number that has ONE right answer
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = {"breath-generator": "breath_gen", "bubbler": "bubbler", "dapple": "dapple",
         "heartbeat-generator": "heartbeat gen", "melody-phase": "melody_phase",
         "polyrhythm-phase-v3": "polyrhythm_phase_v3", "resonance-bank": "resonance_bank",
         "rhythm-track": "rhythm-track", "shepard-scale": "shepard-scale", "shepard-tone": "shepard-tone",
         "spectral-vowel-morpher": "spectral_vowel_morpher", "spectral-vowel-passage": "spectral_vowel_passage",
         "stereo-phaser": "stereo-phaser", "sustain-looper": "sustain_looper",
         "sweep-dwell-filter": "sweep-dwell-filter", "sweeping-filter": "full-feature-sweeping-filter",
         "tremolo": "Full_Feature_Tremolo", "veil": "veil", "womb": "womb_sound_generator_v3"}
DECL = re.compile(r"^slider(\d+):[^<]*<[^>]*>(.*?)\s*$")
SHAPES = [
    re.compile(r"\*\*(?P<name>[^*\n(]+?) \([^)\n]*?\bslider (?P<n>\d+)\b[^)\n]*\)\*\*"),
    re.compile(r"\*\*(?P<name>[^*\n(]+?)(?: \([^)\n]*\))?\*\*[^\n]*?\(slider (?P<n>\d+)\)"),
    re.compile(r"^#+ (?P<name>[^(\n]+?) \(slider (?P<n>\d+)\)", re.M),
    re.compile(r"\bslider (?P<n>\d+) — (?P<name>[^*`\n(]+)"),
]
FIX = "--fix" in sys.argv


def labels(src):
    out = {}
    for line in open(os.path.join(ROOT, "src", src + ".jsfx"), encoding="utf-8"):
        m = DECL.match(line)
        if m:
            out[int(m[1])] = m[2]
    return out


def where(name, lab):
    for nm in (name, name[:-len(" selector")] if name.endswith(" selector") else None):
        if nm:
            hit = [k for k, v in lab.items() if v == nm or v.startswith(nm + " (")]
            if hit:
                return hit
    return []


right = wrong = fixed = unsure = 0
for page, src in PAGES.items():
    path = os.path.join(ROOT, "docs", "plugins", page + ".md")
    text = open(path, encoding="utf-8", newline="").read()
    lab = labels(src)
    edits, covered = [], set()
    for shape in SHAPES:
        for m in shape.finditer(text):
            n, name = int(m["n"]), m["name"].strip()
            if m.start("n") in covered:
                continue
            covered.add(m.start("n"))
            line = text.count("\n", 0, m.start()) + 1
            hit = where(name, lab)
            if n in hit:
                right += 1
            elif len(hit) == 1:
                wrong += 1
                print(f"{page}.md:{line}  {name}: slider {n} -> {hit[0]}  (slider {n} is '{lab.get(n)}')")
                edits.append((m.start("n"), m.end("n"), str(hit[0])))
            else:
                unsure += 1
                print(f"UNSURE {page}.md:{line}  {name}: slider {n}; candidates {hit} -- read by hand")
    for m in re.finditer(r"\bslider (\d+)\b", text):
        if m.start(1) not in covered:
            line = text.count("\n", 0, m.start()) + 1
            ctx = text[max(0, m.start() - 60):m.end() + 20].replace("\n", " ")
            print(f"  (history or prose, not changed) {page}.md:{line}: ...{ctx}...")
    if FIX and edits:
        for a, b, new in sorted(edits, reverse=True):
            text = text[:a] + new + text[b:]
        open(path, "w", encoding="utf-8", newline="").write(text)
        fixed += len(edits)
print(f"--- {right} right, {wrong} wrong, {unsure} unsure" + (f"; {fixed} rewritten" if FIX else " (report only)"))
sys.exit(1 if (wrong and not FIX) or unsure else 0)
