#!/usr/bin/env python3
"""Apply the AUTHORED R25 label list to src/ -- never infer one.

The list lives in docs/layouts/r25-labels-20260912.md as table rows:

    | src/bubbler.jsfx | 37 | Ramp start delay (in ramp time units) | Ramp start delay (per target, in ramp time units) |

Each row must match EXACTLY: that slider number, declared once, with that old label -- or,
if the list was applied on an earlier run, with exactly the new label, which counts as
done. Anything else is a refusal, not a skip. The kind in each new label comes from
tools/selector_scope_probe.py measured live in REAPER, written into the list by hand.

A label rename moves no saved value (REAPER restores by position), so no migration.

    python tools/r25_rename_apply.py            # dry run: what would change
    python tools/r25_rename_apply.py --apply    # write, then re-read and verify

After --apply every file is re-read: each listed slider must carry its new label, and the
number of changed lines per file must equal the rows applied to it THIS run -- nothing
else touched.
"""
import collections, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(ROOT, "docs", "layouts", "r25-labels-20260912.md")
APPLY = "--apply" in sys.argv
ROW = re.compile(r"^\|\s*(src/[^|]+?\.jsfx)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")


def rows():
    out = collections.defaultdict(list)
    for line in open(LIST, encoding="utf-8-sig"):
        m = ROW.match(line)
        if m:
            out[m[1]].append((int(m[2]), m[3], m[4]))
    return out


def decl_re(sid):
    # sliderN:default<range>label  -- the label is everything after the first '>' of the range
    return re.compile(rf"^(slider{sid}:[^<\r\n]*<[^>\r\n]*>)(.*?)(\r?)$")


def main():
    plan = rows()
    if not plan:
        raise SystemExit(f"no rows found in {LIST}")
    total, refusals, done = 0, [], []
    applied = collections.Counter()               # rel -> rows changed this run
    new_texts = {}
    for rel, items in sorted(plan.items()):
        path = os.path.join(ROOT, rel)
        lines = open(path, encoding="utf-8", newline="").read().split("\n")
        seen = collections.Counter(sid for sid, _, _ in items)
        for sid, n in seen.items():
            if n > 1:
                refusals.append(f"{rel}: slider{sid} listed {n} times")
        for sid, old, new in items:
            hits = [i for i, l in enumerate(lines) if decl_re(sid).match(l)]
            if len(hits) != 1:
                refusals.append(f"{rel}: slider{sid} declared {len(hits)} times, want 1")
                continue
            m = decl_re(sid).match(lines[hits[0]])
            if m[2] == new:
                done.append((rel, sid))           # applied on an earlier run: exactly the new label
                continue
            if m[2] != old:
                refusals.append(f"{rel}: slider{sid} label is '{m[2]}', list says '{old}'")
                continue
            print(f"{rel} slider{sid}: '{old}' -> '{new}'")
            lines[hits[0]] = m[1] + new + m[3]
            total += 1
            applied[rel] += 1
        new_texts[path] = "\n".join(lines)
    if refusals:
        print("\nREFUSED -- nothing written:")
        for r in refusals:
            print("  " + r)
        sys.exit(1)
    print(f"\n{total} label(s) to change in {len(applied)} file(s); {len(done)} already applied"
          + ("" if APPLY else " -- dry run, nothing written"))
    if not APPLY or not total:
        return
    touched = {os.path.join(ROOT, rel) for rel in applied}
    before = {p: open(p, encoding="utf-8", newline="").read().split("\n") for p in touched}
    for p in touched:
        open(p, "w", encoding="utf-8", newline="").write(new_texts[p])
    # Verify the OUTPUT: re-read each file.
    fails = 0
    for rel, items in plan.items():
        path = os.path.join(ROOT, rel)
        after = open(path, encoding="utf-8", newline="").read().split("\n")
        if path in before:
            changed = sum(a != b for a, b in zip(before[path], after)) + abs(len(after) - len(before[path]))
            if changed != applied[rel] or len(after) != len(before[path]):
                fails += 1
                print(f"FAIL {rel}: {changed} lines changed, {applied[rel]} rows applied")
        for sid, _, new in items:
            got = [decl_re(sid).match(l) for l in after]
            got = [g[2] for g in got if g]
            if got != [new]:
                fails += 1
                print(f"FAIL {rel}: slider{sid} reads {got}, want '{new}'")
    print("verified: every listed label reads as listed, nothing else changed" if not fails else f"{fails} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
