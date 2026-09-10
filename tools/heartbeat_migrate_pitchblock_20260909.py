#!/usr/bin/env python3
"""Give Heartbeat Generator the R22 pitch block.

`S1 Frequency Hz` and `S2 Frequency Hz` (sliders 9 and 10) become ONE block
behind a `Pitch target` selector -- {All, S1, S2} -- at sliders 9-15, and
everything from old slider 11 up moves up by five. 35 sliders -> 40.

THE POINT OF DIFFICULTY, and why this script is longer than the others: with a
selector, the per-target frequencies live in the serialized blob rather than on
the slider line. Heartbeat's one live instance has NO BLOB AT ALL, and it stores
S2 at 75 Hz -- not the default 120. Migrating the slider line alone would drop
that 75 on the floor.

So this CREATES the blob, at the current magic, with every bank holding exactly
what @init would produce, plus the two frequencies read off the old slider line.
Breath Generator's 2026-09-08 migration set the precedent for writing a blob
that was not there.
"""
import base64, struct, sys, shutil, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

FIRST, LAST, SHIFT, N_NEW = 11, 35, 5, 40
MAGIC = 2400004.0
NT = NS = 4
NP = 3
PROJECTS = ["E:/reaper/finished/transformation.RPP"]


def nearest_note(hz):
    if hz <= 0:
        return 60
    return max(0, min(127, int(round(69 + 12 * math.log2(hz / 440.0)))))


def build_blob(s1, s2):
    """Exactly the stream the plugin reads at MAGIC, in @init's own values."""
    v = [MAGIC]
    v += [0.0] * NS * 3            # speed ramp by / duration / start delay
    v += [0.0]                     # last_speed_target
    v += [0.0] * NT                # drift up
    v += [0.0] * NT                # drift down
    v += [8.0] * NT                # drift period -- @init's 8, not 0
    v += [0.0] * NT                # drift shape
    v += [0.0]                     # last_target_select
    v += [0.0] * NT * 2            # drift play / rest
    v += [0.0] * NS * 2            # ramp play / rest
    v += [0.0 if i < 2 else 1.0 for i in range(NT)]        # drift movement
    v += [float(nearest_note(s1)), float(nearest_note(s1)), float(nearest_note(s2))]
    v += [float(s1), float(s1), float(s2)]                 # the pitches
    v += [0.0] * NP                # mode = Hz
    v += [0.0] * NP                # fine tune
    v += [2.0] * NP                # fine unit = Cents
    v += [0.0]                     # last_pitch_target
    return v


def migrate(path, apply_it):
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True)
    done = skipped = 0
    for hi in reversed([i for i, l in enumerate(lines) if "heartbeat gen.jsfx" in l]):
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            t = lines[j].strip()
            if t and (t[0].isdigit() or t[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi+1}")

        bi = None
        for j in range(vi, min(vi + 6, len(lines))):
            if lines[j].strip().startswith("<JS_SER"):
                bi = j
                break
        if bi is not None:
            b64, k = "", bi + 1
            while lines[k].strip() != ">":
                b64 += lines[k].strip()
                k += 1
            first = struct.unpack("<f", base64.b64decode(b64)[:4])[0]
            if first == MAGIC:
                skipped += 1
                continue
            raise RuntimeError(f"{path}: instance already has a blob at magic {first}; "
                               "this script only knows how to CREATE one. Re-derive.")

        slots = parse_line(lines[vi])
        # slider 11 is `Stereo Width ms` (can be negative) before, `Note name`
        # (0..127) after. A negative there means unmigrated; but the surest
        # marker is that slider 15 is `Breath HRV Depth` (<= 0.25) before and
        # `Tuning reference` (>= 20) after.
        s15 = slots.get(15)
        if s15 not in (None, "-") and float(s15) >= 20:
            skipped += 1
            continue

        s1 = float(slots.get(9)) if slots.get(9) not in (None, "-") else 45.0
        s2 = float(slots.get(10)) if slots.get(10) not in (None, "-") else 120.0

        for sid in range(LAST, FIRST - 1, -1):
            slots[sid + SHIFT] = slots.get(sid)
        slots[9]  = "0"                       # Pitch target = All
        slots[10] = "0"                       # Pitch mode = Hz
        slots[11] = str(nearest_note(s1))     # Note name
        slots[12] = ("%g" % s1)               # Pitch value -- All reads S1
        slots[13] = "0"
        slots[14] = "2"
        slots[15] = "440"
        new_line = render_line(lines[vi], slots, n_sliders=N_NEW)

        if apply_it:
            vals = build_blob(s1, s2)
            b64 = base64.b64encode(struct.pack("<" + "f" * len(vals), *vals)).decode("ascii")
            chunks = [b64[x:x + 128] for x in range(0, len(b64), 128)]
            ln = lines[vi]
            indent = ln[: len(ln) - len(ln.lstrip())]
            eol = "\r\n" if ln.endswith("\r\n") else "\n"
            blob = ([indent + "<JS_SER" + eol] +
                    [indent + "  " + c + eol for c in chunks] +
                    [indent + ">" + eol])
            lines[vi] = new_line
            lines[vi + 1:vi + 1] = blob
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped


def main():
    apply_it = "--apply" in sys.argv
    bak = Path("E:/reaper/finished/backups/snapshots/_pre-heartbeat-pitch-20260909")
    for ps in PROJECTS:
        p = Path(ps)
        if not p.exists():
            print(f"MISSING {p}")
            continue
        if apply_it:
            bak.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bak / (p.parent.name + "__" + p.name))
        d, s = migrate(p, apply_it)
        print(f"{'MIGRATED' if apply_it else 'would migrate'} {d} (done {s})  {p.name}")


if __name__ == "__main__":
    main()
