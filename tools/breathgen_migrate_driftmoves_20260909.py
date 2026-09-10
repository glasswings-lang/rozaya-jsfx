#!/usr/bin/env python3
"""Insert Breath Generator's `Drift movement` control (slider 30) into projects.

WHAT CHANGED IN THE PLUGIN
--------------------------
`Drift movement` is a new per-target enum at slider 30: `With the target` (the
drift advances one step each time that target's own thing happens) or `On a
clock` (it advances continuously). Until now that choice was hardcoded by target
index -- the rate and four segments stepped, the two pitch targets flowed.

It is INSERTED, not appended, because it belongs beside the period controls it
qualifies. Rozaya, 2026-09-09: *"Don't apend when we can aford not to. we can
afford not to."* So sliders 30-40 each move up one, to 31-41.

WHAT THIS DOES TO A PROJECT
---------------------------
1. Slider line: every stored value for sliders 30-40 shifts to 31-41, and
   slider 30 is written as 0. The visible 0 is corrected on load anyway --
   @serialize re-reads the bank for whichever target is selected -- but a stored
   value has to be there or REAPER restores the shifted line by position.
2. Blob: magic 2400007 -> 2500007, with seven values appended for the new bank,
   in target order, holding EXACTLY what the old hardcoded rule did:
   rate + four segments = 0 (with the target), two pitch targets = 1 (on a clock).

So a migrated project sounds identical. Nothing stored changes meaning.

IDEMPOTENCE is gated on the blob magic, which is exact. Re-running is a no-op.
"""
import base64, struct, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

OLD_MAGIC, NEW_MAGIC = 2400007.0, 2500007.0
N = 7
MOVES = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]   # what drift_is_stepped() hardcoded
FIRST_MOVED, LAST_MOVED, NEW_SLIDER = 30, 40, 30
N_SLIDERS_NEW = 41

PROJECTS = [
    Path("E:/reaper/templates/breathscapes.RPP"),
    Path("E:/reaper/to-play-with-later/micle.RPP"),
    Path("E:/reaper/to-play-with-later/organic-movement.RPP"),
]


def migrate_file(path, apply_it):
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if "breath_gen.jsfx" in l]
    done = skipped = 0
    # Reverse order: editing a blob changes line counts below it.
    for hi in reversed(hits):
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            s = lines[j].strip()
            if s and (s[0].isdigit() or s[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi+1}")

        bi = None
        for j in range(vi, min(vi + 6, len(lines))):
            if lines[j].strip().startswith("<JS_SER"):
                bi = j
                break
        if bi is None:
            raise RuntimeError(f"{path}: no <JS_SER> under the <JS> at line {hi+1}")

        b64, k = "", bi + 1
        while lines[k].strip() != ">":
            b64 += lines[k].strip()
            k += 1
        raw = base64.b64decode(b64)
        if len(raw) % 4:
            raise ValueError(f"{path}: blob is {len(raw)} bytes")
        vals = list(struct.unpack("<" + "f" * (len(raw) // 4), raw))
        magic = vals[0]

        if magic == NEW_MAGIC:
            skipped += 1
            continue
        if magic != OLD_MAGIC:
            raise RuntimeError(f"{path}: blob magic {magic}, expected {OLD_MAGIC}")

        expect = 1 + (3 * N + 1) + (4 * N + 1) + (4 * N) + (5 * 3 + 1)
        if len(vals) != expect:
            raise RuntimeError(f"{path}: blob has {len(vals)} floats, expected {expect}")

        # --- the slider line ---
        slots = parse_line(lines[vi])
        for sid in range(LAST_MOVED + 1, FIRST_MOVED - 1, -1):
            slots[sid + 1] = slots.get(sid)
        slots[NEW_SLIDER] = "0"
        new_line = render_line(lines[vi], slots, n_sliders=N_SLIDERS_NEW)

        # --- the blob ---
        new_vals = [NEW_MAGIC] + vals[1:] + MOVES
        nraw = struct.pack("<" + "f" * len(new_vals), *new_vals)
        nb64 = base64.b64encode(nraw).decode("ascii")
        chunks = [nb64[x:x + 128] for x in range(0, len(nb64), 128)]
        indent = lines[bi + 1][: len(lines[bi + 1]) - len(lines[bi + 1].lstrip())]
        eol = "\r\n" if lines[bi + 1].endswith("\r\n") else "\n"

        if apply_it:
            lines[bi + 1:k] = [indent + c + eol for c in chunks]
            lines[vi] = new_line
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    total = tskip = 0
    for p in PROJECTS:
        if not p.exists():
            print(f"MISSING {p}")
            continue
        if apply_it:
            bak = Path("E:/reaper/finished/backups/snapshots/_pre-driftmoves-20260909")
            bak.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bak / (p.parent.name + "__" + p.name))
        d, s = migrate_file(p, apply_it)
        total += d
        tskip += s
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d} (already done: {s})  {p}")
    print(f"TOTAL {total} instance(s), {tskip} already migrated")


if __name__ == "__main__":
    main()
