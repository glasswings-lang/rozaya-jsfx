#!/usr/bin/env python3
"""List and extract the captures stored inside Spectral Vowel Passage / Morpher.

WHY THIS EXISTS
---------------
A capture only exists inside the project that made it.  You cannot reuse a good
vowel in another piece, back one up on its own, feed one to another plugin, or
hand one to anybody else -- and you cannot tell your eight slots apart without
playing all eight, which is a real problem when there is no waveform to look at.

But the audio is right there.  Both plugins store the RAW captured audio in their
`@serialize` blob (the analysis is re-derived from it on load, which is why
scrubbing Capture point re-tunes a slot without re-recording it).  The blob is a
plain memory dump, so it can be read straight out of the .RPP.

This tool only ever READS.  It never modifies a project.

    python tools/passage_captures.py PROJECT.RPP                # what's in there
    python tools/passage_captures.py PROJECT.RPP --extract DIR  # write WAVs

WHAT YOU GET
------------
The listing gives every slot a line: how loud it is, how long the real signal
lasts, and its pitch as a note name.  That is enough to tell slots apart, pick
the one you want, and spot the empty ones -- by reading, not by auditioning.

`--extract` writes one WAV per non-empty slot at the project's own sample rate,
named by track and slot.  Drop them in `<REAPER resource>/Data/glasswings_samples/`
and they appear in Sustain Looper's dropdown; or run them through
`loop_finder.py`; or just keep them, which is the point -- a capture that exists
only inside one .RPP is one bad save away from gone.

FORMAT NOTES
------------
The blob leads with a magic number that encodes its layout version, and this
refuses to read anything it does not recognise rather than guessing -- a
mis-parsed blob would produce plausible-looking garbage.  Layouts 7700001 to
7700004 are understood.  Only the leading fields (magic, have, n_used, then the
raw audio) are needed to extract, and those have never moved, so extraction works
across every version; the per-slot settings shown in the listing came later and
are read defensively, since older blobs simply end before them.
"""

import argparse
import math
import os
import re
import struct
import sys
import wave

MAXFFT = 32768          # samples per capture slot
NSLOTS = 8
KNOWN_MAGICS = {7700001: 6, 7700002: 9, 7700003: 9, 7700004: 10}   # magic -> Drift/Ramp target count
PLUGINS = ("spectral_vowel_passage.jsfx", "spectral_vowel_morpher.jsfx")

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# --------------------------------------------------------------------------
# reading the project
# --------------------------------------------------------------------------

def read_project(path):
    """Yield one dict per plugin instance: track name, plugin, decoded floats."""
    with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        lines = fh.read().split("\n")

    srate = 48000
    for line in lines[:200]:
        m = re.match(r"\s*SAMPLERATE\s+(\d+)", line)
        if m:
            srate = int(m.group(1))
            break

    track = "track"
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"\s*NAME\s+(.*)", line)
        if m:
            track = m.group(1).strip().strip('"') or "track"
        if "<JS" not in line:
            continue
        plugin = next((p for p in PLUGINS if p in line), None)
        if plugin is None:
            continue
        blob = _collect_blob(lines, i)
        if blob is None:
            continue
        out.append({"track": track, "plugin": plugin, "srate": srate,
                    "floats": blob, "line": i + 1})
    return out


def _collect_blob(lines, start):
    """Find the <JS_SER ...> block belonging to the <JS at `start` and decode it."""
    import base64
    j = start
    # The serialize block follows within a handful of lines (slider line, then
    # possibly a preset name), and always before the next <JS.
    while j < len(lines) and j < start + 12:
        if "<JS " in lines[j] and j != start:
            return None
        if lines[j].strip().startswith("<JS_SER"):
            body = []
            j += 1
            while j < len(lines) and not lines[j].strip().startswith(">"):
                body.append(lines[j].strip())
                j += 1
            raw = base64.b64decode("".join(body))
            n = len(raw) // 4
            return struct.unpack("<%df" % n, raw[: n * 4])
        j += 1
    return None


def parse_blob(floats):
    """Split a decoded blob into header, raw audio and (where present) settings."""
    if len(floats) < 3:
        return None
    magic = int(round(floats[0]))
    if magic not in KNOWN_MAGICS:
        return {"magic": magic, "unknown": True}

    n_used = int(round(floats[2]))
    if not (0 <= n_used <= NSLOTS):
        return {"magic": magic, "unknown": True}

    info = {"magic": magic, "have": floats[1], "n_used": n_used, "unknown": False}
    audio_end = 3 + n_used * MAXFFT
    info["audio"] = [floats[3 + s * MAXFFT: 3 + (s + 1) * MAXFFT] for s in range(n_used)]

    # Everything past the audio is settings, appended over time -- an older blob
    # simply stops early, so every read below is allowed to come up short.
    t = KNOWN_MAGICS[magic]
    o = audio_end
    def take(n):
        nonlocal o
        v = floats[o: o + n]
        o += n
        return v if len(v) == n else None

    for _ in range(4):
        take(t)
    take(1)
    for _ in range(3):
        take(t)
    take(1)
    for name in ("cappoint", "linger", "xfade", "voicedb", "texture", "spread",
                 "pitch", "width", "lowcut", "denoise", "mute", "fadein", "gap",
                 "xfadeon", "capavg"):
        info[name] = take(NSLOTS)
    return info


# --------------------------------------------------------------------------
# describing a slot
# --------------------------------------------------------------------------

def db(x):
    return float("-inf") if x <= 1e-9 else 20 * math.log10(x)


def describe(samples, srate):
    """Peak, RMS, how much of the grab is real signal, and a pitch estimate."""
    peak = max((abs(v) for v in samples), default=0.0)
    if peak < 1e-6:
        return {"empty": True}

    total = sum(v * v for v in samples)
    rms = math.sqrt(total / len(samples))

    # "Signal" = the span between the first and last sample above -40 dB of peak,
    # which is what you actually hear rather than the fixed grab length.
    thr = peak * 0.01
    first = next((i for i, v in enumerate(samples) if abs(v) > thr), 0)
    last = next((i for i in range(len(samples) - 1, -1, -1) if abs(samples[i]) > thr), len(samples) - 1)

    return {"empty": False, "peak": peak, "rms": rms,
            "dur": (last - first + 1) / srate,
            "start": first / srate,
            "f0": estimate_f0(samples[first:last + 1], srate)}


def estimate_f0(samples, srate):
    """Autocorrelation pitch estimate on a decimated window. None if unpitched.

    Decimated by 4 first: the search only needs to resolve 70-600 Hz, and doing
    it at full rate would make this the slowest thing in the tool by an order of
    magnitude for no extra accuracy.
    """
    dec = 4
    sr = srate / dec
    win = [samples[i] for i in range(0, min(len(samples), 12288), dec)]
    if len(win) < 256:
        return None
    mean = sum(win) / len(win)
    win = [v - mean for v in win]

    lo = max(2, int(sr / 600))
    hi = min(len(win) // 2, int(sr / 70))
    if hi <= lo:
        return None

    energy = sum(v * v for v in win)
    if energy <= 0:
        return None

    best_lag, best_score = 0, 0.0
    for lag in range(lo, hi + 1):
        s = 0.0
        for i in range(len(win) - lag):
            s += win[i] * win[i + lag]
        score = s / energy
        if score > best_score:
            best_score, best_lag = score, lag

    # Below this the "period" is noise agreeing with itself by chance; calling
    # that a pitch is worse than admitting there isn't one.
    if best_lag == 0 or best_score < 0.35:
        return None
    return sr / best_lag


def note_name(hz):
    if not hz:
        return "unpitched"
    midi = 69 + 12 * math.log2(hz / 440.0)
    n = int(round(midi))
    cents = int(round((midi - n) * 100))
    name = "%s%d" % (NOTE_NAMES[n % 12], n // 12 - 1)
    return "%-4s %+4d cents  %6.1f Hz" % (name, cents, hz)


# --------------------------------------------------------------------------
# writing
# --------------------------------------------------------------------------

def write_wav(path, samples, srate, as_float=False):
    if as_float:
        data = struct.pack("<%df" % len(samples), *samples)
        hdr = (b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " +
               struct.pack("<IHHIIHH", 16, 3, 1, srate, srate * 4, 4, 32) +
               b"data" + struct.pack("<I", len(data)))
        with open(path, "wb") as fh:
            fh.write(hdr + data)
        return
    with wave.open(path, "wb") as fh:
        fh.setnchannels(1)
        fh.setsampwidth(2)
        fh.setframerate(srate)
        fh.writeframes(struct.pack("<%dh" % len(samples),
                                   *(max(-32768, min(32767, int(v * 32767)))
                                     for v in samples)))


def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "track"


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+", help="REAPER .RPP project files")
    ap.add_argument("--extract", metavar="DIR",
                    help="write one WAV per non-empty slot into DIR")
    ap.add_argument("--float", action="store_true", dest="as_float",
                    help="write 32-bit float WAVs instead of 16-bit "
                         "(exact, but 16-bit is what loads everywhere)")
    ap.add_argument("--no-pitch", action="store_true",
                    help="skip pitch detection (faster on big projects)")
    args = ap.parse_args()

    if args.extract:
        os.makedirs(args.extract, exist_ok=True)

    written = 0
    for path in args.projects:
        print("== %s" % path)
        try:
            instances = read_project(path)
        except OSError as exc:
            print("   ERROR: %s" % exc)
            continue
        if not instances:
            print("   no Passage / Morpher instances found")
            continue

        for idx, inst in enumerate(instances, 1):
            info = parse_blob(inst["floats"])
            label = "%s  (%s, line %d)" % (inst["track"],
                                           inst["plugin"].replace(".jsfx", ""),
                                           inst["line"])
            if info is None or info.get("unknown"):
                got = info.get("magic") if info else "?"
                print("   %s\n      SKIPPED: unrecognised blob layout (magic %s)"
                      % (label, got))
                continue

            srate = inst["srate"]
            print("   %s -- %d slot(s), %d Hz" % (label, info["n_used"], srate))
            for s in range(info["n_used"]):
                d = describe(info["audio"][s], srate)
                if d["empty"]:
                    print("      slot %d  (empty -- captured silence)" % (s + 1))
                    continue
                pitch = "" if args.no_pitch else "  " + note_name(d["f0"])
                extra = ""
                if info.get("pitch") and info.get("capavg"):
                    extra = "  [pitch %+.1f st, avg %d]" % (
                        info["pitch"][s], int(round(info["capavg"][s])))
                print("      slot %d  %5.2f s  peak %6.1f dB  rms %6.1f dB%s%s"
                      % (s + 1, d["dur"], db(d["peak"]), db(d["rms"]), pitch, extra))

                if args.extract:
                    fn = "%s_%s_inst%d_slot%d.wav" % (
                        safe(os.path.splitext(os.path.basename(path))[0]),
                        safe(inst["track"]), idx, s + 1)
                    write_wav(os.path.join(args.extract, fn),
                              info["audio"][s], srate, args.as_float)
                    written += 1

    if args.extract:
        print("\nwrote %d WAV(s) to %s" % (written, args.extract))
    return 0


if __name__ == "__main__":
    sys.exit(main())
