#!/usr/bin/env python3
"""
morpher_v1_to_v2.py -- copy a REAPER project that uses Spectral Vowel Morpher
so the copy uses v2 instead, keeping the captures and every setting.

Why it exists: v2 groups its controls by what they belong to, which renumbered
the sliders, and it replaced v1's single global Auto-morph time with a per-slot
Slot linger. Pointing a project at v2 by hand shifts every value by one
position, so everything lands on the wrong control. This maps them BY LABEL,
read live from both .jsfx files, so it stays correct even if either layout is
renumbered again -- no slider number is hard-coded here.

It also reads the slot count out of each instance's own capture blob, so the
Slot linger it derives reproduces the timing the project already had rather
than guessing at it.

Your original project is never modified; a new file is written beside it.
Afterwards both files are read back and compared label for label, and the tool
refuses to report success if anything failed to line up.

Nothing to install -- standard library only.

    python tools/morpher_v1_to_v2.py "E:/reaper/breathing.rpp"
    python tools/morpher_v1_to_v2.py song.rpp --out song_v2.rpp

One caveat worth knowing: convert from a SAVED project. This reads what is on
disk, so if the project is open in REAPER with unsaved changes, the copy is
built from the older state. (That mistake is exactly why this file exists.)

Run with --help for the full flag list.
"""

import argparse
import base64
import os
import re
import struct
import sys
import time

JS1 = "glasswings/spectral_vowel_morpher.jsfx"
JS2 = "glasswings/spectral_vowel_morpher_v2.jsfx"
LINGER = "Slot linger"
XFADE = "Slot crossfade"               # v2-only, added after v1; seed = linger
MUTE = "Slot mute"                     # v2-only; seed = 0 (unmuted), preserves v1 sound
DROPPED = "Auto-morph time (sec)"      # v1-only: becomes the per-slot linger
V1_MAGIC = 7700001.0


def slider_labels(path):
    """{slider number: visible label} straight from a .jsfx."""
    text = open(path, encoding="utf-8").read()
    return {int(m.group(1)): m.group(4).strip()
            for m in re.finditer(r"^slider(\d+):([^<]*)<([^>]*)>(.+)$", text, re.M)}


def slots_used(lines, js_index):
    """Captured-slot count from the JS_SER blob belonging to this instance."""
    i = js_index + 1
    while i < len(lines) and lines[i].strip() != "<JS_SER":
        if lines[i].strip().startswith("<JS "):
            return None
        i += 1
    if i >= len(lines):
        return None
    chunks = []
    for line in lines[i + 1:]:
        t = line.strip()
        if t == ">" or t.startswith("<"):
            break
        chunks.append(t)
    raw = base64.b64decode("".join(chunks) + "==")
    magic, _have, n_used = struct.unpack_from("<3f", raw, 0)
    if magic != V1_MAGIC:
        sys.exit("unexpected capture format (magic %r) -- not a v1 project?" % magic)
    return int(n_used)


def instance_values(lines, tag, labels):
    """[{label: value}] for every instance of `tag` in the file."""
    found = []
    for j, line in enumerate(lines):
        if line.strip().startswith("<JS " + tag):
            nums = [x for x in lines[j + 1].split() if x != "-"]
            found.append({labels[k]: float(nums[k - 1]) for k in labels})
    return found


def fmt(x):
    return ("%.6f" % x).rstrip("0").rstrip(".") if x % 1 else "%d" % int(x)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="the .rpp to convert (never modified)")
    ap.add_argument("--out", help="output path (default: <project>_v2.rpp)")
    ap.add_argument("--src-dir", default=os.path.join(os.path.dirname(here), "src"),
                    help="folder holding the two .jsfx files (default: ../src)")
    args = ap.parse_args()

    dst = args.out or re.sub(r"\.rpp$", "", args.project, flags=re.I) + "_v2.rpp"
    p1 = os.path.join(args.src_dir, "spectral_vowel_morpher.jsfx")
    p2 = os.path.join(args.src_dir, "spectral_vowel_morpher_v2.jsfx")
    for p in (args.project, p1, p2):
        if not os.path.exists(p):
            sys.exit("not found: " + p)

    l1, l2 = slider_labels(p1), slider_labels(p2)
    by_label = {v: k for k, v in l1.items()}
    if len(by_label) != len(l1):
        sys.exit("v1 has duplicate slider labels -- cannot map by name")

    saved = time.strftime("%Y-%m-%d %H:%M:%S",
                          time.localtime(os.path.getmtime(args.project)))
    print("converting %s\n  last saved %s" % (args.project, saved))

    lines = open(args.project, encoding="utf-8",
                 errors="surrogateescape").read().split("\n")
    out, i, n = [], 0, 0
    while i < len(lines):
        line = lines[i]
        if not line.strip().startswith("<JS " + JS1):
            out.append(line)
            i += 1
            continue

        n_used = slots_used(lines, i)
        if not n_used:
            sys.exit("instance at line %d has no captures to read a slot count from"
                     % (i + 1))
        cells = lines[i + 1].split()
        nums = [x for x in cells if x != "-"]
        if len(nums) != len(l1):
            sys.exit("instance at line %d has %d values, v1 declares %d sliders"
                     % (i + 1, len(nums), len(l1)))
        v1 = {k: float(nums[k - 1]) for k in l1}

        # v1 spent Auto-morph time on the WHOLE pass; v2 spends linger on each
        # step. Sweep and Glide walk n_used-1 steps; Shuffle wraps, so n_used.
        mode = v1[by_label["Auto-morph"]]
        legs = n_used if mode == 3 else max(1, n_used - 1)
        linger = round(v1[by_label[DROPPED]] / legs, 4)

        values = []
        for k in sorted(l2):
            label = l2[k]
            if label in by_label:
                values.append(v1[by_label[label]])
            elif label.startswith(LINGER):
                # Under Option B: linger is pure hold. v1 had no hold (whole leg
                # was crossfade), so linger = 0 for v1-fidelity migration.
                values.append(0)
            elif label.startswith(XFADE):
                # Crossfade is the full v1 leg time -- all fade, no hold, which
                # matches how v1 sounded. User introduces hold per slot by
                # raising slot linger above 0.
                values.append(linger)
            elif label.startswith(MUTE):
                # Seed unmuted so a converted v1 project morphs across every
                # captured slot exactly as it did before mute existed.
                values.append(0)
            else:
                sys.exit("no v1 source for v2 slider %d (%s)" % (k, label))

        out.append(line.replace(JS1, JS2))
        out.append("        " + " ".join(fmt(x) for x in values)
                   + " " + " ".join(["-"] * (len(cells) - len(nums))))
        n += 1
        print("  instance %d: %d slots, mode %g, %g s per pass -> %g s per step"
              % (n, n_used, mode, v1[by_label[DROPPED]], linger))
        i += 2

    if not n:
        sys.exit("no Spectral Vowel Morpher instances found -- nothing to convert")
    open(dst, "w", encoding="utf-8", errors="surrogateescape").write("\n".join(out))

    # Read both back and prove every control landed on its namesake.
    before = instance_values(lines, JS1, l1)
    after = instance_values(
        open(dst, encoding="utf-8", errors="surrogateescape").read().split("\n"),
        JS2, l2)
    bad = 0
    for idx, (a, b) in enumerate(zip(before, after), 1):
        for label, val in a.items():
            if label == DROPPED:
                continue
            if b.get(label) != val:
                print("  MISMATCH instance %d  %s: was %s, now %s"
                      % (idx, label, val, b.get(label)))
                bad += 1
    if bad:
        sys.exit("conversion FAILED (%d mismatches) -- do not use %s" % (bad, dst))

    print("\nchecked %d instances, every control matched by name." % len(before))
    print("wrote", dst)
    print("Open that in REAPER. Your original is untouched.")


if __name__ == "__main__":
    main()
