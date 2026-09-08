#!/usr/bin/env python3
"""Migrate Breath Generator projects to the 2026-09-08 layout (32 -> 40 sliders).

Authored from docs/layouts/breath-gen.md. The map below is a LITERAL authored
table; nothing here infers a mapping from the file.

Two things move, and they move together:

  * the slider line, renumbered by HOPS below;
  * the `<JS_SER>` blob, because the two filter frequencies stop being sliders
    and become a per-target pitch bank inside the blob. A slider-line-only
    migration would silently reset both frequencies to the plugin defaults.

Usage:
    python tools/breathgen_migrate_layout_20260908.py --dry-run
    python tools/breathgen_migrate_layout_20260908.py --apply

Idempotent: an instance whose blob already carries the 2300005 magic is skipped.
The gate is the MAGIC, deliberately -- an earlier version gated on the slider
count and silently covered only half the instances, because one project stores
nothing above slider 24 and so never looked migrated.
"""
import argparse, base64, math, re, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rpp_sliders import parse_line, render_line          # noqa: E402

OLD_N, NEW_N = 32, 40
OLD_MAGICS = (2100005.0, 2200005.0)
NEW_MAGIC = 2300005.0
TUNING = 440.0

# ---- AUTHORED slider map: new id -> old id, or a literal seed value ----------
# Seeds reproduce the OLD behaviour exactly, never the plugin's own defaults.
SEED = object()
MAP = {
    1:  (SEED, "0"),        # Set breath rate -- a one-shot, never saved non-zero
    2:  (SEED, "0"),        # Breath unit = Seconds, which is what it always was
    3:  1, 4: 2, 5: 3, 6: 4,                       # the four segments
    7:  (SEED, "1"),        # Pitch target = Inhale, NOT All -- see note below
    8:  (SEED, None),       # Note        ) filled per-instance from the old
    9:  (SEED, None),       # Pitch value ) frequency, computed below
    10: (SEED, "0"),        # Pitch mode = Hz, so every stored number keeps
    11: (SEED, "0"),        # Fine tune value
    12: (SEED, "0"),        # Fine tune mode = Hz
    13: (SEED, "440"),      # Tuning reference
    14: 7, 15: 8, 16: 9, 17: 10, 18: 11,           # fades
    19: 12, 20: 13,                                # stereo
    21: (SEED, "0"),        # Output (dB) -- 0 dB changes no existing level
    22: 14, 23: 15, 24: 16,                        # transport
    25: 17, 26: 18, 27: 19, 28: 20, 29: 21, 30: 22, 31: 23, 32: 24,   # drift
    33: 25, 34: 26, 35: 27, 36: 28, 37: 29, 38: 30, 39: 31, 40: 32,   # ramp
}
# Pitch target is seeded to Inhale rather than All deliberately. On All the
# visible block reads back from Inhale, which is correct but invites a user to
# nudge a control and move BOTH frequencies without meaning to on their first
# encounter with a migrated instance. Inhale is the honest starting point.

assert sorted(MAP) == list(range(1, NEW_N + 1))
_olds = [v for v in MAP.values() if not isinstance(v, tuple)]
assert sorted(_olds) == [i for i in range(1, OLD_N + 1) if i not in (5, 6)], _olds

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def hz_to_note_offset(f):
    """Nearest MIDI note at or below f, plus the exact Hz remainder.

    Hz mode is an OFFSET from the note, so this preserves the old frequency
    bit-for-bit while still naming a note for it.
    """
    n = int(math.floor(12 * math.log2(f / TUNING) + 69))
    n = max(0, min(127, n))
    return n, f - TUNING * 2 ** ((n - 69) / 12.0)


def note_name(n):
    return f"{NOTE_NAMES[n % 12]}{n // 12 - 1}"


def fmt(x):
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


# ---- blob ------------------------------------------------------------------
# Stream order, from @serialize in src/breath_gen.jsfx. N_TARGETS =
# N_SPEED_TARGETS = 5; N_PITCH = 3.
OLD_STREAM = [("sr_by", 5), ("sr_dur", 5), ("sr_delay", 5), ("last_sr", 1),
              ("dr_up", 5), ("dr_down", 5), ("dr_per", 5), ("dr_shape", 5),
              ("last_dr", 1)]
V22_EXTRA = [("dr_play", 5), ("dr_rest", 5), ("sr_play", 5), ("sr_rest", 5)]
PITCH = [("p_note", 3), ("p_val", 3), ("p_mode", 3), ("p_fine", 3),
         ("p_fmod", 3), ("last_pitch", 1)]


def read_blob(b64):
    raw = base64.b64decode(b64)
    if len(raw) % 4:
        raise ValueError(f"blob is {len(raw)} bytes, not a whole number of floats")
    vals = list(struct.unpack("<" + "f" * (len(raw) // 4), raw))
    magic = vals[0]
    fields, i = {}, 1
    stream = list(OLD_STREAM)
    if magic >= 2200005.0:
        stream += V22_EXTRA
    if magic >= NEW_MAGIC:
        stream += PITCH
    for name, n in stream:
        fields[name] = vals[i:i + n]
        i += n
    if i != len(vals):
        raise ValueError(f"blob has {len(vals)} floats, stream expects {i}")
    return magic, fields


def write_blob(fields):
    vals = [NEW_MAGIC]
    for name, n in OLD_STREAM + V22_EXTRA + PITCH:
        v = fields.get(name, [0.0] * n)
        assert len(v) == n, f"{name}: {len(v)} values, expected {n}"
        vals += v
    raw = struct.pack("<" + "f" * len(vals), *vals)
    b64 = base64.b64encode(raw).decode("ascii")
    return [b64[k:k + 128] for k in range(0, len(b64), 128)]


def migrate_file(path, apply_it, report):
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)
    n_before = len(lines)
    hits = [i for i, l in enumerate(lines) if "breath_gen.jsfx" in l]
    if not hits:
        return 0

    changed = 0
    # REVERSE ORDER. Creating a <JS_SER> block inserts lines, which invalidates
    # every index after it -- the second instance in organic-movement.RPP was
    # missed exactly that way on the first run. Walking backwards keeps the
    # earlier indices valid.
    for hi in reversed(hits):
        # the value line is the first token line after the <JS ...> header
        vi = None
        for j in range(hi + 1, min(hi + 6, len(lines))):
            s = lines[j].strip()
            if s and (s[0].isdigit() or s[0] in "-\""):
                vi = j
                break
        if vi is None:
            raise RuntimeError(f"{path}: no value line under the <JS> at line {hi+1}")

        slots = parse_line(lines[vi])

        # IDEMPOTENCE GATE: the BLOB MAGIC, not the slider count.
        #
        # The first version of this gated on "the line stores a slider above 32",
        # which looked right and silently covered only half the instances. An
        # instance whose stored values stop early -- organic-movement.RPP stores
        # nothing above slider 24 -- never trips it, so a second run would read
        # the ALREADY MIGRATED slider 5 (Exhale, a duration of 10) as a
        # frequency and destroy the pitch. The magic is exact and cannot be
        # fooled by which sliders happen to hold values.
        bi = None
        for j in range(vi, min(vi + 6, len(lines))):
            if lines[j].strip().startswith("<JS_SER"):
                bi = j
                break
        if bi is not None:
            probe, k = "", bi + 1
            while lines[k].strip() != ">":
                probe += lines[k].strip()
                k += 1
            probe_raw = base64.b64decode(probe)
            if len(probe_raw) >= 4:
                probe_magic = struct.unpack("<f", probe_raw[:4])[0]
                if probe_magic == NEW_MAGIC:
                    report.append(f"    line {vi+1}: already migrated"
                                  f" (blob magic {NEW_MAGIC:.0f}) -- skipped")
                    continue

        f_in = float(slots.get(5) or 800.0)
        f_ex = float(slots.get(6) or 600.0)
        n_in, off_in = hz_to_note_offset(f_in)
        n_ex, off_ex = hz_to_note_offset(f_ex)

        new = {}
        for nid, src in MAP.items():
            if isinstance(src, tuple):
                new[nid] = src[1]
            else:
                new[nid] = slots.get(src)
        new[8] = str(n_in)
        new[9] = fmt(off_in)

        out = render_line(lines[vi], new, NEW_N)

        # --- blob (bi was located by the idempotence gate above) ---
        be = created_at = None
        js_indent = ""
        if bi is None:
            # No blob at all -- an instance old enough to predate @serialize
            # here. One must be CREATED, or the two frequencies have nowhere to
            # land and both silently revert to the plugin's 800/600 defaults.
            # Every other field takes @init's values, which is what this
            # instance has effectively been running on all along.
            magic, fields = None, {"dr_per": [8.0] * 5}
            close = vi + 1
            while lines[close].strip() != ">":
                close += 1
            js_indent = lines[close][:len(lines[close]) - len(lines[close].lstrip())]
            created_at = close + 1
        else:
            be = bi + 1
            b64 = ""
            while lines[be].strip() != ">":
                b64 += lines[be].strip()
                be += 1
            magic, fields = read_blob(b64)
            if magic not in OLD_MAGICS and magic != NEW_MAGIC:
                raise RuntimeError(f"{path} line {bi+1}: unexpected blob magic {magic}")
        fields["p_note"] = [float(n_in), float(n_in), float(n_ex)]
        fields["p_val"] = [off_in, off_in, off_ex]
        fields["p_mode"] = [0.0, 0.0, 0.0]
        fields["p_fine"] = [0.0, 0.0, 0.0]
        fields["p_fmod"] = [0.0, 0.0, 0.0]
        fields["last_pitch"] = [1.0]
        ref = lines[bi + 1] if bi is not None else lines[vi]
        indent = ref[:len(ref) - len(ref.lstrip())]
        eol = "\r\n" if ref.endswith("\r\n") else "\n"
        new_b64 = [indent + c + eol for c in write_blob(fields)]

        was = f"{magic:.0f}" if magic is not None else "ABSENT, created"
        report.append(
            f"    line {vi+1}: inhale {f_in:g} Hz -> {note_name(n_in)} + {off_in:.4f} Hz"
            f" | exhale {f_ex:g} Hz -> {note_name(n_ex)} + {off_ex:.4f} Hz"
            f" | blob {was} -> {NEW_MAGIC:.0f}")

        lines[vi] = out
        if bi is not None:
            lines[bi + 1:be] = new_b64
        else:
            lines[created_at:created_at] = (
                [js_indent + "<JS_SER" + eol] + new_b64 + [js_indent + ">" + eol])
        changed += 1

    if changed and apply_it:
        # line count may legitimately change (blob re-wraps); assert the
        # instance count did not.
        joined = "".join(lines)
        assert joined.count("breath_gen.jsfx") == len(hits), "instance count changed"
        path.write_text(joined, encoding="utf-8", errors="surrogateescape", newline="")
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("paths", nargs="*", default=None)
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        ap.error("pass --dry-run or --apply")

    roots = [Path(p) for p in a.paths] if a.paths else [
        Path(r"E:/reaper/templates/breathscapes.RPP"),
        Path(r"E:/reaper/to-play-with-later/micle.RPP"),
        Path(r"E:/reaper/to-play-with-later/organic-movement.RPP"),
    ]
    total = skipped = 0
    for p in roots:
        report = []
        n = migrate_file(p, a.apply, report)
        print(f"{p}  {n} instance(s)")
        for r in sorted(report):
            print(r)
        total += n
        skipped += sum(1 for r in report if "skipped" in r)
    print(f"\n{'APPLIED' if a.apply else 'DRY RUN'}: {total} instance(s)"
          f", {skipped} already migrated")
    # Do not cry wolf. Nothing left to do is the CORRECT outcome on a re-run,
    # and a checker that reports failure when everything is fine is worse than
    # none -- the whole point is that when it says FAIL, you stop.
    if total + skipped != 4:
        print(f"WARNING: expected 4 instances in total,"
              f" accounted for {total + skipped}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
