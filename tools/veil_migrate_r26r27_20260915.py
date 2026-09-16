#!/usr/bin/env python3
"""Move Veil's saved slider line from the 22-control layout to the 35-control one.

docs/layouts/veil.md holds the layout this applies. Veil is in ONE live project --
the bridge test project -- and everything else that matches is inside a backup
snapshot. Searched 2026-09-15: all of E:/reaper and E:/tensor's-rpp-projects plus
REAPER's ProjectTemplates and TrackTemplates.

THE MAP IS AUTHORED, one line per control; nothing is inferred. The @serialize
blob is left alone ON PURPOSE: the plugin reads a 3300005 save at its own width of
five and remaps the targets itself (1, 2, 7, 8, 10), which is the only part of the
old state that is not on the slider line.

Old sliders 1-4 (the two cutoffs and the two resonances) have no slider each any
more -- they are per-side banks now. They are carried by writing the MIDPOINT into
the new single control, which is exactly what the picker shows on `Both`, and the
two sides keep their @init defaults of 480/520 and 0.15/0.15. **That is lossless
only while the project's four values ARE those defaults**, which is checked below
and refused if not, rather than quietly flattening someone's stereo width.

Dry run by default; --apply writes. Idempotent: a line already 35 wide is left.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

FILES = ["E:/reaper/finished/test-projects/claude-testing002-bridge.RPP"]
JS = "glasswings/veil.jsfx"

# old target index -> new, for the two selectors
TGT = {0: 1, 1: 2, 2: 7, 3: 8, 4: 10}
# new slider <- old slider, for everything that simply moves
MOVE = {9: 5, 10: 6, 18: 8, 19: 9, 20: 11, 21: 10, 22: 12, 23: 13, 24: 14,
        28: 16, 29: 17, 30: 18, 31: 19, 32: 20, 34: 21, 35: 22}
# new slider <- a fixed value, for everything that is new
NEW = {1: "0", 2: "0", 3: "71", 5: "2", 6: "0", 8: "440",
       11: "0", 12: "0", 13: "0", 14: "0", 15: "0",
       17: "0", 25: "0", 27: "0", 33: "0"}
DEFAULTS = {1: 480.0, 2: 520.0, 3: 0.15, 4: 0.15}

def num(tok, dflt=0.0):
    try:
        return float(tok)
    except (TypeError, ValueError):
        return dflt

def migrate(line):
    old = parse_line(line)
    if old.get(35) is not None and old.get(23) is not None:
        return None, "already 35 wide"
    for k, v in DEFAULTS.items():
        got = num(old.get(k), v)
        if abs(got - v) > 1e-6:
            return None, ("slider %d is %g, not the default %g -- migrating it would "
                          "flatten the stereo width; do this one by hand" % (k, got, v))
    new = {}
    for k, v in NEW.items():
        new[k] = v
    for dst, src in MOVE.items():
        new[dst] = old.get(src)
    # the two cutoffs and the two resonances become one control each, at the midpoint
    new[4] = "%g" % ((num(old.get(1), 480) + num(old.get(2), 520)) / 2)
    new[7] = "%g" % ((num(old.get(3), 0.15) + num(old.get(4), 0.15)) / 2)
    # the two target selectors move with their targets
    new[16] = str(TGT.get(int(num(old.get(7))), 0))
    new[26] = str(TGT.get(int(num(old.get(15))), 0))
    return render_line(line, new, n_sliders=35), None

def main():
    apply = "--apply" in sys.argv
    hits = 0
    for path in FILES:
        if not os.path.exists(path):
            print("MISSING %s" % path); continue
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        out, i, changed = [], 0, 0
        while i < len(lines):
            out.append(lines[i])
            if JS in lines[i] and "<JS" in lines[i]:
                i += 1
                newline, why = migrate(lines[i])
                if newline is None:
                    print("  SKIP (%s)" % why); out.append(lines[i])
                else:
                    changed += 1
                    print("  OLD %s" % lines[i].strip())
                    print("  NEW %s" % newline.strip())
                    out.append(newline)
            i += 1
        hits += changed
        print("%s: %d instance(s)" % (path, changed))
        if apply and changed:
            open(path, "w", encoding="utf-8", newline="").write("\n".join(out))
    print("APPLIED" if apply else "DRY RUN -- pass --apply to write")
    return 0 if hits else 1

if __name__ == "__main__":
    sys.exit(main())
