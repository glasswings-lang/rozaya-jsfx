#!/usr/bin/env python3
"""Range-check every stored slider value in every project against its plugin.

WHY
---
A mid-list slider insert shifts every saved value one place, silently. The
cheapest detector for that -- and the one that actually found the 2026-09-02
Melody Phase drift bug after a day of reasoning had not -- is simply:

    does every stored value fit inside the control it now lands on?

A shifted map nearly always parks at least one value outside its slider's
declared min/max. `Drift period = 0` against a declared minimum of 1 was the
whole finding.

This reads the layout out of the INSTALLED plugin (what REAPER actually loads),
not out of src/, because those can differ -- and it is the installed one whose
numbering the project is being read against.

USE
    python tools/scan_slider_ranges.py <project dir or .RPP> [...]
    python tools/scan_slider_ranges.py --effects <dir> <projects...>

Out-of-range values are a strong signal, not a proof: a plugin can write a value
outside a declared range programmatically (slider_automate), and a shift between
two similar ranges can hide completely. Read the hits, do not just count them.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, SliderLineError, is_quoted  # noqa: E402

DECL = re.compile(r'^slider(\d+):([^<]*)<([^,]*),([^,]*),([^>]*)>(.*)$')
JS_RE = re.compile(r'^\s*<JS\s+(\S+)')

DEFAULT_EFFECTS = os.path.expandvars(
    r"%APPDATA%\REAPER\Effects")


def read_layout(path):
    lay = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                m = DECL.match(ln.strip())
                if not m:
                    continue
                try:
                    lo, hi = float(m.group(3)), float(m.group(4))
                except ValueError:
                    continue          # a file-selector slider has no numeric range
                lay[int(m.group(1))] = (lo, hi, m.group(6).split("}")[-1].strip())
    except OSError:
        return None
    return lay


def scan(path, effects, cache):
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    hits, checked, instances = [], 0, 0
    for i, ln in enumerate(lines):
        m = JS_RE.match(ln)
        if not m:
            continue
        rel = m.group(1).strip('"')
        if rel not in cache:
            cache[rel] = read_layout(os.path.join(effects, rel.replace("/", os.sep)))
        lay = cache[rel]
        if not lay or i + 1 >= len(lines):
            continue
        instances += 1
        try:
            slots = parse_line(lines[i + 1])
        except SliderLineError as e:
            hits.append((rel, i + 2, None, "UNPARSEABLE: %s" % e))
            continue
        for sid, tok in sorted(slots.items()):
            if tok is None or sid not in lay or is_quoted(tok):
                continue
            checked += 1
            try:
                v = float(tok)
            except ValueError:
                hits.append((rel, i + 2, sid, "non-numeric %r" % tok))
                continue
            lo, hi, name = lay[sid]
            if not (lo - 1e-9 <= v <= hi + 1e-9):
                hits.append((rel, i + 2, sid,
                             "%s = %s outside [%s, %s]" % (name, tok, lo, hi)))
    return hits, checked, instances


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--effects", default=DEFAULT_EFFECTS,
                    help="REAPER Effects folder (default: %(default)s)")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, f) for f in names
                          if f.lower().endswith(".rpp")]
        else:
            files.append(p)

    cache = {}
    total_h = total_c = 0
    per_plugin = {}
    for path in sorted(files):
        hits, checked, inst = scan(path, args.effects, cache)
        total_c += checked
        total_h += len(hits)
        if hits:
            print("\n%s   (%d instances, %d values checked)"
                  % (path, inst, checked))
            seen = set()
            for rel, line, sid, msg in hits:
                per_plugin.setdefault(rel, 0)
                per_plugin[rel] += 1
                key = (rel, sid, msg)
                if key in seen:
                    continue
                seen.add(key)
                n = sum(1 for h in hits if (h[0], h[2], h[3]) == key)
                print("   %-34s slider %-4s %s   [x%d]"
                      % (rel, sid if sid else "?", msg, n))
    print("\n%d values checked, %d out of range" % (total_c, total_h))
    if per_plugin:
        print("\nBY PLUGIN:")
        for rel, n in sorted(per_plugin.items(), key=lambda kv: -kv[1]):
            print("   %-40s %d" % (rel, n))
    missing = [k for k, v in cache.items() if v is None]
    if missing:
        print("\nNOT FOUND in the effects folder (not checked): %s"
              % ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
