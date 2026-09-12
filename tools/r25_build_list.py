#!/usr/bin/env python3
"""Draft the R25 label list from a MEASURED selector_scope_probe report.

The kind of every control -- per target, all targets, per band... -- comes only from the
live measurement. This script turns those measurements into wording and writes the rows
docs/layouts/r25-labels-20260912.md holds; a person reads the list before
tools/r25_rename_apply.py applies it. Anything the measurement did not settle is listed
under "Not renamed", never guessed.

    python tools/r25_build_list.py REPORT BOARD_MAP > rows.md

REPORT    the --out file of selector_scope_probe.py
BOARD_MAP lines "track fx trackname -> file.jsfx" (from the bridge manifest)

Wording (R25): "X" -> "X (per target)"; "X (inner)" -> "X (per target, inner)". A control
that switches with a slot, band, layer, voice or segment selector as well says so first:
"(per band and target)". Measured on its block's target selector without switching:
"(all targets)". Only controls named "Drift <word>" or "Ramp <word>" are renamed.
"""
import collections, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORD = {"Drift target": "target", "Ramp target": "target", "Band selector": "band", "Layer": "layer",
        "Voice": "voice", "Segment": "segment", "Capture slot": "slot"}
ORDER = ["slot", "voice", "band", "layer", "segment", "target"]
LINE = re.compile(r"^(PER|ALL|\?)\s*\| track (\d+) (.+?) \| (.+?) \| p(\d+) (.+?) \| (.*)$")
BLOCK = re.compile(r"^(Drift|Ramp) [a-z]")


def sel_word(sel):
    for k, w in WORD.items():
        if sel == k or sel.startswith(k + " ("):
            return w
    return None


def new_label(old, kind):
    m = re.match(r"^(.*?) \((.*)\)$", old)
    return f"{m[1]} ({kind}, {m[2]})" if m else f"{old} ({kind})"


def main():
    report, board = sys.argv[1], sys.argv[2]
    files = {}
    for l in open(board, encoding="utf-8"):
        m = re.match(r"^(\d+) (\d+) .* -> (\S+\.jsfx)$", l.strip())
        if m:
            files[int(m[1])] = m[3]
    meas = collections.defaultdict(dict)       # (track, name) -> {selector: kind}
    for l in open(report, encoding="utf-8"):
        m = LINE.match(l.strip())
        if m:
            meas[(int(m[2]), m[6])][m[4]] = m[1]
    rows, skipped = [], []
    for (t, name), by_sel in sorted(meas.items()):
        if not BLOCK.match(name) or t not in files:
            continue
        own = "Drift target" if name.startswith("Drift") else "Ramp target"
        if "?" in by_sel.values():
            skipped.append(f"{files[t]}: '{name}' -- measured unclear on {[s for s, k in by_sel.items() if k == '?']}")
            continue
        words = sorted({sel_word(s) for s, k in by_sel.items() if k == "PER" and sel_word(s)}, key=ORDER.index)
        if words:
            kind = "per " + " and ".join(words)
        elif by_sel.get(own) == "ALL":
            kind = "all targets"
        else:
            skipped.append(f"{files[t]}: '{name}' -- never measured on its own {own}")
            continue
        src = open(os.path.join(ROOT, "src", files[t]), encoding="utf-8").read()
        decls = re.findall(rf"^slider(\d+):[^<\r\n]*<[^>\r\n]*>{re.escape(name)}\r?$", src, re.M)
        if len(decls) != 1:
            skipped.append(f"{files[t]}: '{name}' -- declared {len(decls)} times in src, want 1")
            continue
        rows.append(f"| src/{files[t]} | {decls[0]} | {name} | {new_label(name, kind)} |")
    print("| file | slider | old label | new label |\n|---|---|---|---|")
    print("\n".join(rows))
    print(f"\n{len(rows)} rows.\n\n## Not renamed -- look at by hand\n")
    print("\n".join(f"- {s}" for s in skipped) or "- none")


if __name__ == "__main__":
    main()
