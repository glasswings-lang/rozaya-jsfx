#!/usr/bin/env python3
"""Insert `Drift movement` into Bubbler (slider 20) and Dapple (slider 22).

Same control, same reasoning, as Breath Generator's on the same day: whether a
target's drift steps with its own thing or runs on a clock stops being a rule
the plugin holds and becomes a switch. Rozaya: it *"should have been a switch
from the very beginning"*.

INSERTED beside the period controls, not appended -- its call, migration
accepted. Bubbler's sliders 20-30 move to 21-31; Dapple's 22-32 move to 23-33.

The stored value written for the new slider is the DEFAULT FOR WHICHEVER TARGET
THAT INSTANCE HAS SELECTED, read off its own drift-target slider. Not a flat 0:
an instance with no `<JS_SER>` block never reaches the bank restore, so a flat 0
would tell it that Bubble rate steps -- which it never did.

Blob: magic bumped and the new bank appended, holding exactly what
`drift_is_stepped()` hardcoded (targets 1-3 step, everything else flows). The
plugin still reads the older magic, so an unmigrated project keeps its config.
"""
import base64, struct, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line

SPECS = {
    "bubbler": dict(n=9,  target_slider=15, new_slider=20, first=20, last=30,
                    old_magic=3400009.0, new_magic=3500009.0, n_sliders_new=31),
    "dapple":  dict(n=11, target_slider=17, new_slider=22, first=22, last=32,
                    old_magic=3500011.0, new_magic=3600011.0, n_sliders_new=33),
}
PROJECTS = {
    "bubbler": ["E:/reaper/finished/birdsong-2.RPP",
                "E:/reaper/finished/birdsong.RPP",
                "E:/reaper/finished/the-sound-of-a-drain.RPP"],
    "dapple":  ["E:/reaper/finished/bubbles.RPP",
                "E:/reaper/to-play-with-later/womb-bubbles-proto.RPP"],
}


def moves_default(idx):
    """What drift_is_stepped() hardcoded: targets 1-3 step, the rest flow."""
    return 0.0 if 1 <= idx <= 3 else 1.0


def stream_len(n):
    # magic + 5 speed banks + last_speed_target + 6 drift banks + last_target_select
    return 1 + 5 * n + 1 + 6 * n + 1


def migrate(fx, path, apply_it):
    sp = SPECS[fx]
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if f"{fx}.jsfx" in l]
    done = skipped = noblob = 0
    for hi in reversed(hits):                       # reverse: blob edits move lines
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

        vals = None
        if bi is not None:
            b64, k = "", bi + 1
            while lines[k].strip() != ">":
                b64 += lines[k].strip()
                k += 1
            raw = base64.b64decode(b64)
            if len(raw) % 4:
                raise ValueError(f"{path}: blob is {len(raw)} bytes")
            vals = list(struct.unpack("<" + "f" * (len(raw) // 4), raw))
            if vals[0] == sp["new_magic"]:
                skipped += 1
                continue
            if vals[0] != sp["old_magic"]:
                raise RuntimeError(f"{path}: blob magic {vals[0]}, expected {sp['old_magic']}")
            if len(vals) != stream_len(sp["n"]):
                raise RuntimeError(f"{path}: blob has {len(vals)} floats, "
                                   f"expected {stream_len(sp['n'])}")

        slots = parse_line(lines[vi])
        if bi is None:
            # No blob, so idempotence has to come off the line -- and this is the
            # trap the first version fell into. It gated on "slider last+1 holds
            # something", which is never true here: not one of these 24 instances
            # stores ANY drift value, so every slot above the audio block is `-`
            # and a second run would have shifted the freshly written token into
            # Drift shape. Gate on the new slider itself instead.
            if slots.get(sp["new_slider"]) not in (None, "-"):
                skipped += 1
                continue
            # And refuse to guess if that assumption ever stops holding: a stored
            # value at the new slider's old meaning would make the gate ambiguous.
            for sid in range(sp["new_slider"], sp["last"] + 1):
                if slots.get(sid) not in (None, "-"):
                    raise RuntimeError(
                        f"{path}: slider {sid} holds {slots[sid]!r}; this script's "
                        "idempotence gate assumes nothing is stored at or above "
                        f"slider {sp['new_slider']}. Re-derive before running.")
            noblob += 1

        tok = slots.get(sp["target_slider"])
        try:
            sel = int(float(tok)) if tok not in (None, "-") else 0
        except ValueError:
            sel = 0

        for sid in range(sp["last"] + 1, sp["first"] - 1, -1):
            slots[sid + 1] = slots.get(sid)
        slots[sp["new_slider"]] = str(int(moves_default(sel)))
        new_line = render_line(lines[vi], slots, n_sliders=sp["n_sliders_new"])

        if apply_it:
            if vals is not None:
                new_vals = ([sp["new_magic"]] + vals[1:] +
                            [moves_default(i) for i in range(sp["n"])])
                nb64 = base64.b64encode(
                    struct.pack("<" + "f" * len(new_vals), *new_vals)).decode("ascii")
                chunks = [nb64[x:x + 128] for x in range(0, len(nb64), 128)]
                ln = lines[bi + 1]
                indent = ln[: len(ln) - len(ln.lstrip())]
                eol = "\r\n" if ln.endswith("\r\n") else "\n"
                lines[bi + 1:k] = [indent + c + eol for c in chunks]
            lines[vi] = new_line
        done += 1

    if apply_it and done:
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
    return done, skipped, noblob


def main():
    apply_it = "--apply" in sys.argv
    bak = Path("E:/reaper/finished/backups/snapshots/_pre-driftmoves-bubdap-20260909")
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
            print(f"{'MIGRATED' if apply_it else 'would migrate'} {d:>2} "
                  f"(done already {s}, no blob {nb})  {fx:<8} {p.name}")


if __name__ == "__main__":
    main()
