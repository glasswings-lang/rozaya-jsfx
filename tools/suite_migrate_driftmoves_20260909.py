#!/usr/bin/env python3
"""Insert `Drift movement` into Womb v3, Heartbeat Generator and Melody Phase.

The last three plugins that decided for themselves whether a drift steps with
its own thing or runs on a clock. Same control, same insert-don't-append call
from Rozaya, 2026-09-09.

NO BLOB IS TOUCHED, and that is deliberate. A survey of the 82 instances found
SEVEN different stored formats between them -- Womb carries magic 2100010 and a
pre-magic 5, Melody carries 1000028, two different lengths of 2200028, and
2300028. Every one of those is a format its plugin still reads. Leaving them
alone means each keeps being read exactly as before, and the new bank simply is
not present, so it falls to @init's defaults -- which ARE the old hardcoded
behaviour. Rewriting seven formats to append one field would be all risk and no
gain.

So only the slider line changes. The token written for the new control is the
default for WHICHEVER TARGET that instance has selected, not a flat 0: nothing
restores the bank for these blobs, so a flat 0 would tell a continuous target
that it steps.

IDEMPOTENCE cannot come from the blob, and for Womb and Melody it cannot come
from "is the new slider empty" either -- both legitimately store values there
already. It comes from the TOKEN COUNT: a plugin with more than 64 sliders
writes 64 values, a `""` marker, then the rest, so one more slider is one more
token. Heartbeat Generator has 35 and is padded to 64 either way, so it gates on
its new slider being empty -- verified true for its single instance.
"""
import sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

SPECS = {
    "womb_sound_generator_v3": dict(
        n=11, target_slider=55, new_slider=60, first=60, last=70,
        n_sliders_old=70, n_sliders_new=71,
        steps=lambda i: i < 6 or i == 7),
    "heartbeat gen": dict(
        n=4, target_slider=18, new_slider=23, first=23, last=34,
        n_sliders_old=34, n_sliders_new=35,
        steps=lambda i: i < 2),
    "melody_phase": dict(
        n=28, target_slider=71, new_slider=76, first=76, last=86,
        n_sliders_old=86, n_sliders_new=87,
        steps=lambda i: 18 <= i <= 27),
}

PROJECTS = {
    "womb_sound_generator_v3": [
        "E:/reaper/finished/back-to-life.RPP", "E:/reaper/finished/deep-night.RPP",
        "E:/reaper/finished/to-sleep-within.RPP", "E:/reaper/to-play-with-later/micle.RPP",
        "E:/reaper/to-play-with-later/noisescape-august-18-2026.RPP",
        "E:/reaper/to-play-with-later/surges.RPP",
        "E:/reaper/to-play-with-later/womb-and-baby-heartbeats-with-bloodflow.RPP",
        "E:/reaper/to-play-with-later/womb-bubbles-proto.RPP"],
    "heartbeat gen": ["E:/reaper/finished/transformation.RPP"],
    "melody_phase": [
        "E:/reaper/finished/melodic.RPP", "E:/reaper/finished/outcoming.RPP",
        "E:/reaper/finished/slow-summer.RPP", "E:/reaper/finished/upswing.RPP",
        "E:/reaper/to-play-with-later/simple-sequence-check.RPP",
        "E:/reaper/to-play-with-later/simple-sequence.RPP",
        "E:/reaper/to-play-with-later/testing-proof of concept.RPP"],
}


def token_count(line):
    return len(line.strip().split())


def migrate(fx, path, apply_it):
    sp = SPECS[fx]
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if f"{fx}.jsfx" in l]
    done = skipped = 0
    for hi in reversed(hits):
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            s = lines[j].strip()
            if s and (s[0].isdigit() or s[0] in '-"'):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under <JS> at line {hi+1}")

        slots = parse_line(lines[vi])
        if sp["n_sliders_old"] > 64:
            # More than 64 sliders: one more slider is one more token.
            expected_old = 64 + 1 + (sp["n_sliders_old"] - 64)
            n = token_count(lines[vi])
            if n == expected_old + 1:
                skipped += 1
                continue
            if n != expected_old:
                raise RuntimeError(f"{path}: value line has {n} tokens, "
                                   f"expected {expected_old} or {expected_old+1}")
        else:
            # Padded to 64 either way, so gate on the new slider being empty --
            # and refuse to guess if that ever stops being a safe marker.
            if slots.get(sp["new_slider"]) not in (None, "-"):
                skipped += 1
                continue
            for sid in range(sp["new_slider"], sp["last"] + 1):
                if slots.get(sid) not in (None, "-"):
                    raise RuntimeError(
                        f"{path}: slider {sid} holds {slots[sid]!r}; this gate "
                        f"assumes nothing is stored at or above {sp['new_slider']}.")

        tok = slots.get(sp["target_slider"])
        try:
            sel = int(float(tok)) if tok not in (None, "-") else 0
        except ValueError:
            sel = 0
        for sid in range(sp["last"] + 1, sp["first"] - 1, -1):
            slots[sid + 1] = slots.get(sid)
        slots[sp["new_slider"]] = "0" if sp["steps"](sel) else "1"
        new_line = render_line(lines[vi], slots, n_sliders=sp["n_sliders_new"])
        if apply_it:
            lines[vi] = new_line
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped, 0


def main():
    apply_it = "--apply" in sys.argv
    bak = Path("E:/reaper/finished/backups/snapshots/_pre-driftmoves-suite-20260909")
    tot = 0
    for fx, projects in PROJECTS.items():
        for ps in projects:
            p = Path(ps)
            if not p.exists():
                print(f"MISSING {p}")
                continue
            if apply_it:
                bak.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, bak / (p.parent.name + "__" + p.name))
            d, s, nb = migrate(fx, p, apply_it)
            tot += d
            print(f"{'MIGRATED' if apply_it else 'would migrate'} {d:>2} "
                  f"(done {s}, no blob {nb})  {fx[:14]:<15} {p.name}")
    print(f"TOTAL {tot}")


if __name__ == "__main__":
    main()
