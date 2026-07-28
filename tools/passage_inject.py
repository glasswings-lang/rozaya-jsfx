#!/usr/bin/env python3
"""Write a WAV into a Spectral Vowel Passage / Morpher capture slot.

The companion to `passage_captures.py`, which reads slots out. This puts them
back — so a capture can move between projects, or be assembled from a file
instead of caught live.

    python tools/passage_inject.py PROJECT.RPP --set 3=vowel.wav
    python tools/passage_inject.py PROJECT.RPP --set 3=a.wav --set 5=b.wav
    python tools/passage_inject.py PROJECT.RPP --set 3=a.wav --instance 2

By default it writes a NEW project beside the original and leaves yours alone.

WHY THIS IS POSSIBLE AT ALL
---------------------------
The saved blob holds only the RAW audio — the wash spectrum and the harmonic
analysis are not in there, they are re-derived from that audio every time the
project loads. So injection does not have to compute anything: drop audio in and
the plugin analyses it itself, exactly as if you had captured it. That is also
why the edit is a fixed-offset splice — everything before the audio (the version
marker and the counts) and everything after it (all the per-slot settings) is
left untouched, so it cannot misalign the way a mid-stream insert would.

A capture therefore no longer has to come from a performance. Anything you can
put in a WAV can become a slot: one extracted from another project, a clip out of
`loop_finder.py`, or a generated source.

WHAT IT DOES TO YOUR AUDIO
--------------------------
A slot is exactly 32768 samples — about 0.68 s at 48 kHz — mono, at the project's
own sample rate. So:

* **Sample rate must match the project.** The blob records no rate of its own;
  audio just plays at whatever the project runs at, so a 44.1k file in a 48k
  project comes out sharp and short with nothing reporting an error anywhere.
  That silent, plausible-sounding failure is the one most likely to bite, so a
  mismatch is refused unless you pass `--resample`.
* **Stereo is summed to mono**, because the capture buffer is mono. Your stereo
  placement arrives centred.
* **Longer files are trimmed** to the loudest 0.68 s (override with `--from`).
* **Shorter files are centred and padded** with silence, and the slot's Capture
  point is set to put the analysis window on the audio rather than on the padding
  — otherwise a short file analyses as silence and the slot goes quiet.

SAFETY
------
Copies by default. `--in-place` keeps a `.pre-inject-bak`. Either way the result
is re-read and re-decoded before it is allowed to stand, and the run is abandoned
if anything other than the intended slots changed. Close the project in REAPER
first — REAPER holds its own copy and writes it back over yours on the next save.
"""

import argparse
import base64
import math
import os
import re
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from passage_captures import (KNOWN_MAGICS, MAXFFT, NSLOTS, PLUGINS,   # noqa: E402
                              describe, note_name, db)

WA = 8192   # the plugin's analysis window; Capture point positions this inside the grab


# --------------------------------------------------------------------------
# WAV reading (stdlib `wave` refuses float WAVs, which our own extractor writes)
# --------------------------------------------------------------------------

def read_wav(path):
    """Return (mono samples as floats, sample rate). Handles PCM 8/16/24/32 and float 32/64."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("not a WAV file")

    fmt = None
    body = None
    o = 12
    while o + 8 <= len(data):
        cid = data[o:o + 4]
        size = struct.unpack("<I", data[o + 4:o + 8])[0]
        chunk = data[o + 8:o + 8 + size]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", chunk[:16])
        elif cid == b"data":
            body = chunk
        o += 8 + size + (size & 1)
    if fmt is None or body is None:
        raise ValueError("WAV is missing its format or data chunk")

    tag, ch, sr, _, _, bits = fmt
    if tag == 0xFFFE:      # extensible: the real tag lives in the chunk's tail
        tag = 1 if bits in (8, 16, 24, 32) else 3

    if tag == 3:
        if bits == 32:
            vals = struct.unpack("<%df" % (len(body) // 4), body[: len(body) // 4 * 4])
        elif bits == 64:
            vals = struct.unpack("<%dd" % (len(body) // 8), body[: len(body) // 8 * 8])
        else:
            raise ValueError("unsupported float width: %d-bit" % bits)
    elif tag == 1:
        if bits == 8:
            vals = [(b - 128) / 128.0 for b in body]
        elif bits == 16:
            n = len(body) // 2
            vals = [v / 32768.0 for v in struct.unpack("<%dh" % n, body[:n * 2])]
        elif bits == 24:
            vals = []
            for i in range(0, len(body) - 2, 3):
                v = body[i] | (body[i + 1] << 8) | (body[i + 2] << 16)
                if v & 0x800000:
                    v -= 0x1000000
                vals.append(v / 8388608.0)
        elif bits == 32:
            n = len(body) // 4
            vals = [v / 2147483648.0 for v in struct.unpack("<%di" % n, body[:n * 4])]
        else:
            raise ValueError("unsupported PCM width: %d-bit" % bits)
    else:
        raise ValueError("unsupported WAV encoding (format tag %d)" % tag)

    if ch > 1:
        vals = [sum(vals[i:i + ch]) / ch for i in range(0, len(vals) - ch + 1, ch)]
    return list(vals), sr


def resample(samples, src_sr, dst_sr):
    """Linear interpolation. Enough for material that gets spectrally analysed anyway."""
    if src_sr == dst_sr:
        return samples
    ratio = dst_sr / src_sr
    out_n = int(len(samples) * ratio)
    out = []
    for i in range(out_n):
        x = i / ratio
        i0 = int(x)
        f = x - i0
        a = samples[i0] if i0 < len(samples) else 0.0
        b = samples[i0 + 1] if i0 + 1 < len(samples) else a
        out.append(a * (1 - f) + b * f)
    return out


def fit_to_slot(samples, from_sec, srate):
    """Trim or pad to exactly MAXFFT. Returns (samples, capture_point 0..1)."""
    if len(samples) > MAXFFT:
        if from_sec is not None:
            start = max(0, min(len(samples) - MAXFFT, int(from_sec * srate)))
        else:
            # Loudest window, scanned on a coarse grid: on a held vowel with a
            # quiet approach and release this lands on the sustained middle,
            # which is the part worth capturing.
            step = max(1, MAXFFT // 16)
            best, start = -1.0, 0
            for s in range(0, len(samples) - MAXFFT + 1, step):
                e = sum(v * v for v in samples[s:s + MAXFFT:64])
                if e > best:
                    best, start = e, s
        out = samples[start:start + MAXFFT]
        return out, 0.5
    # Shorter: centre it, then aim Capture point at the audio, not the padding.
    pad = MAXFFT - len(samples)
    head = pad // 2
    out = [0.0] * head + list(samples) + [0.0] * (pad - head)
    centre = head + len(samples) / 2
    span = MAXFFT - WA
    cp = 0.5 if span <= 0 else (centre - WA / 2) / span
    return out, max(0.0, min(1.0, cp))


# --------------------------------------------------------------------------
# project surgery
# --------------------------------------------------------------------------

def find_instances(lines):
    """Locate each Passage/Morpher instance and its <JS_SER> block extent."""
    out = []
    track = "track"
    srate = 48000
    for line in lines[:200]:
        m = re.match(r"\s*SAMPLERATE\s+(\d+)", line)
        if m:
            srate = int(m.group(1))
            break
    for i, line in enumerate(lines):
        m = re.match(r"\s*NAME\s+(.*)", line)
        if m:
            track = m.group(1).strip().strip('"') or "track"
        if "<JS" not in line or not any(p in line for p in PLUGINS):
            continue
        j = i + 1
        while j < len(lines) and j < i + 12 and not lines[j].strip().startswith("<JS_SER"):
            j += 1
        if j >= len(lines) or not lines[j].strip().startswith("<JS_SER"):
            continue
        first = j + 1
        k = first
        while k < len(lines) and not lines[k].strip().startswith(">"):
            k += 1
        raw = base64.b64decode("".join(l.strip() for l in lines[first:k]))
        n = len(raw) // 4
        out.append({"track": track, "srate": srate, "line": i + 1,
                    "body": (first, k),
                    "indent": lines[first][: len(lines[first]) - len(lines[first].lstrip())],
                    "width": len(lines[first].strip()),
                    "floats": list(struct.unpack("<%df" % n, raw[:n * 4]))})
    return out


def cappoint_index(magic, n_used):
    """Where slot_cappoint[0] sits in the float stream, or None if the blob is too short."""
    t = KNOWN_MAGICS[magic]
    # magic, have, n_used | audio | 4 drift banks + last_target | 3 ramp banks
    # + last_ramp | slot_cappoint...
    return 3 + n_used * MAXFFT + 7 * t + 2


def encode_block(floats, indent, width):
    b64 = base64.b64encode(struct.pack("<%df" % len(floats), *floats)).decode("ascii")
    width = width if width > 0 else 128
    return [indent + b64[i:i + width] for i in range(0, len(b64), width)]


def inject(inst, jobs, verbose=True):
    """Return new float stream for one instance. `jobs` is {slot_index: samples}."""
    f = inst["floats"]
    magic = int(round(f[0]))
    if magic not in KNOWN_MAGICS:
        raise ValueError("unrecognised blob layout (magic %s)" % magic)
    n_used = int(round(f[2]))
    need = max(jobs) + 1
    new_n_used = max(n_used, need)
    if new_n_used > NSLOTS:
        raise ValueError("slot %d is beyond the plugin's %d slots" % (need, NSLOTS))

    audio = [list(f[3 + s * MAXFFT: 3 + (s + 1) * MAXFFT]) for s in range(n_used)]
    while len(audio) < new_n_used:
        audio.append([0.0] * MAXFFT)          # silence for slots skipped over
    tail = list(f[3 + n_used * MAXFFT:])

    for slot, (samples, cp) in jobs.items():
        audio[slot] = samples
        ci = cappoint_index(magic, 0) - 3     # offset within `tail`
        if 0 <= ci + slot < len(tail):
            tail[ci + slot] = cp
        elif verbose:
            print("      (blob predates per-slot Capture point; set it by ear)")

    return [float(magic), 1.0, float(new_n_used)] + [v for s in audio for v in s] + tail


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="REAPER .RPP project file")
    ap.add_argument("--set", action="append", required=True, metavar="SLOT=FILE",
                    help="put FILE into slot SLOT (1-8). Repeatable.")
    ap.add_argument("--instance", type=int, default=None,
                    help="which plugin instance (1-based) when the project has more than one")
    ap.add_argument("--from", dest="from_sec", type=float, default=None,
                    help="seconds into a long file to take the slot from "
                         "(default: its loudest stretch)")
    ap.add_argument("--resample", action="store_true",
                    help="allow a sample-rate mismatch, resampling to the project's rate")
    ap.add_argument("--in-place", action="store_true",
                    help="edit the project itself (keeps a .pre-inject-bak)")
    ap.add_argument("--out", help="write here instead of the default <name>-injected.RPP")
    args = ap.parse_args()

    jobs_spec = {}
    for item in args.set:
        if "=" not in item:
            ap.error("--set wants SLOT=FILE, got %r" % item)
        k, v = item.split("=", 1)
        try:
            slot = int(k)
        except ValueError:
            ap.error("slot must be a number 1-%d, got %r" % (NSLOTS, k))
        if not 1 <= slot <= NSLOTS:
            ap.error("slot must be 1-%d, got %d" % (NSLOTS, slot))
        jobs_spec[slot - 1] = v

    with open(args.project, "r", encoding="utf-8", errors="surrogateescape",
              newline="") as fh:
        text = fh.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)

    instances = find_instances(lines)
    if not instances:
        print("no Passage / Morpher instances found in %s" % args.project)
        return 1
    if args.instance is None:
        if len(instances) > 1:
            print("This project has %d instances — say which with --instance N:" % len(instances))
            for i, inst in enumerate(instances, 1):
                print("   %d  %s (line %d)" % (i, inst["track"], inst["line"]))
            return 1
        args.instance = 1
    if not 1 <= args.instance <= len(instances):
        print("no instance %d (project has %d)" % (args.instance, len(instances)))
        return 1
    inst = instances[args.instance - 1]
    srate = inst["srate"]
    print("target: %s (line %d), %d Hz" % (inst["track"], inst["line"], srate))

    jobs = {}
    for slot, path in sorted(jobs_spec.items()):
        try:
            samples, wsr = read_wav(path)
        except (OSError, ValueError) as exc:
            print("   slot %d: ERROR reading %s -- %s" % (slot + 1, path, exc))
            return 1
        note = []
        if wsr != srate:
            if not args.resample:
                print("   slot %d: REFUSED -- %s is %d Hz, the project is %d Hz.\n"
                      "      Nothing records the rate inside the project, so this would\n"
                      "      simply play at the wrong pitch and length with no error.\n"
                      "      Pass --resample to convert it, or supply a %d Hz file."
                      % (slot + 1, os.path.basename(path), wsr, srate, srate))
                return 1
            samples = resample(samples, wsr, srate)
            note.append("resampled %d->%d Hz" % (wsr, srate))
        fitted, cp = fit_to_slot(samples, args.from_sec, srate)
        if len(samples) > MAXFFT:
            note.append("trimmed from %.2f s" % (len(samples) / srate))
        elif len(samples) < MAXFFT:
            note.append("padded from %.2f s" % (len(samples) / srate))
        jobs[slot] = (fitted, cp)
        d = describe(fitted, srate)
        pitch = "empty" if d["empty"] else note_name(d["f0"])
        print("   slot %d <- %s" % (slot + 1, os.path.basename(path)))
        print("      %s  peak %.1f dB  capture point %d%%%s"
              % (pitch, db(d["peak"]) if not d["empty"] else float("-inf"),
                 round(cp * 100), ("  [" + ", ".join(note) + "]") if note else ""))

    try:
        new_floats = inject(inst, jobs)
    except ValueError as exc:
        print("   ERROR: %s" % exc)
        return 1

    first, last = inst["body"]
    lines[first:last] = encode_block(new_floats, inst["indent"], inst["width"])

    dest = args.out or (args.project if args.in_place else
                        re.sub(r"\.rpp$", "", args.project, flags=re.I) + "-injected.RPP")
    if args.in_place and not args.out:
        backup = args.project + ".pre-inject-bak"
        if os.path.exists(backup):
            print("   ERROR: %s already exists; move it aside first" % backup)
            return 1
        shutil.copy2(args.project, backup)
        print("   backed up -> %s" % backup)

    with open(dest, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        fh.write(nl.join(lines))

    # --- verify: re-read what we wrote and prove only the intended slots moved ---
    with open(dest, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        check = find_instances(fh.read().split(nl))
    if len(check) != len(instances):
        print("   VERIFY FAILED: instance count changed. %s left in place." % dest)
        return 1
    back = check[args.instance - 1]["floats"]
    old = inst["floats"]
    old_n = int(round(old[2]))
    new_n = int(round(back[2]))
    problems = []
    if int(round(back[0])) != int(round(old[0])):
        problems.append("version marker changed")
    for s in range(new_n):
        got = back[3 + s * MAXFFT: 3 + (s + 1) * MAXFFT]
        if s in jobs:
            want = jobs[s][0]
            if max((abs(a - b) for a, b in zip(got, want)), default=0) > 1e-6:
                problems.append("slot %d did not land correctly" % (s + 1))
        elif s < old_n:
            was = old[3 + s * MAXFFT: 3 + (s + 1) * MAXFFT]
            if any(a != b for a, b in zip(got, was)):
                problems.append("slot %d changed but should not have" % (s + 1))
    if problems:
        print("   VERIFY FAILED: %s" % "; ".join(problems))
        return 1

    print("   verified: %d slot(s) written, every other slot byte-identical" % len(jobs))
    print("   wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
