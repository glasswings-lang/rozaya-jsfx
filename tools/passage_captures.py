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
    python tools/passage_captures.py PROJECT.RPP --settings     # what you set
    python tools/passage_captures.py PROJECT.RPP --extract DIR  # write WAVs

WHAT COMES OUT IS THE RAW GRAB
------------------------------
Worth saying plainly, because it has caught someone out: the WAVs are the
audio as CAPTURED, before any of the settings that shape it. Fade times,
texture, pitch, spread, denoise -- none of that is in them, because none of it
is audio. It's a transformation applied while sound passes through, and the
only place the shaped version exists is a render.

That is not the settings being lost. They're all still in the project, and
`--settings` reads them back out: what each slot is set to, in words, showing
only what you changed from the starting values. `--extract` writes them beside
the WAVs as `settings.txt`, so the setup survives the project too and can be
read without opening a DAW at all.

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
                 "xfadeon", "capavg", "ot_harm", "ot_depth"):
        info[name] = take(NSLOTS)
    return info


# --------------------------------------------------------------------------
# the settings you dialled in
# --------------------------------------------------------------------------
#
# The per-slot fields above, in the order @serialize writes them, paired with
# the slider each one belongs to and the value it starts at. The point of the
# default is that it lets the listing show only what somebody CHANGED.
#
# That matters more than it sounds. Seventeen settings across eight slots is a
# hundred and thirty-six numbers, and handed over all at once that is a wall --
# "it makes me wanna run away cuz it's real lots and crowded" is exactly what
# the plugin's own UI already does to the person these were dialled in by. What
# they actually want to know is what they touched.
#
# Morpher keeps most of these as GLOBAL sliders and only stores Capture point
# per slot, so its blob simply ends early and every later field reads back as
# None. Absent is not the same as unchanged, so absent fields are skipped
# rather than reported as defaults.
SLOT_SETTINGS = [
    ("cappoint", "Capture point",        0.0,  "{v:g}"),
    ("capavg",   "Capture average",      1.0,  "{v:g}"),
    ("fadein",   "Fade in",              1.0,  "{v:g} seconds"),
    ("linger",   "Hold",                 4.0,  "{v:g} seconds"),
    ("xfade",    "Fade out",             1.0,  "{v:g} seconds"),
    ("gap",      "Gap after",            0.0,  "{v:g} seconds"),
    ("xfadeon",  "Crossfade into next",  1.0,  None),      # on / off
    ("mute",     "Muted",                0.0,  None),      # on / off
    ("voicedb",  "Voice level",          0.0,  "{v:+g} dB"),
    ("texture",  "Texture",             50.0,  "{v:g}  (0 is voice, 100 is wash)"),
    ("spread",   "Spread",               0.0,  "{v:g} Hz"),
    ("pitch",    "Pitch",                0.0,  "{v:+g} semitones"),
    ("width",    "Stereo width",        50.0,  "{v:g}"),
    ("lowcut",   "Low cut",              0.0,  "{v:g} Hz"),
    ("denoise",  "Denoise",              0.0,  "{v:g}"),
    ("ot_harm",  "Overtone harmonic",    0.0,  "{v:g}"),
    ("ot_depth", "Overtone depth",      24.0,  "{v:g} dB"),
]


def slot_settings(info, slot, changed_only=True):
    """What this slot is set to, as plain lines. Only what differs from the
    starting value, unless changed_only is False."""
    out = []
    for key, label, default, fmt in SLOT_SETTINGS:
        bank = info.get(key)
        if not bank or slot >= len(bank):
            continue                      # this plugin doesn't store it
        v = bank[slot]
        if changed_only and abs(v - default) < 1e-9:
            continue
        if fmt is None:
            out.append("%s: %s" % (label, "on" if v >= 0.5 else "off"))
        else:
            out.append("%s: %s" % (label, fmt.format(v=round(v, 4))))
    return out


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

    scores = []
    for lag in range(lo, hi + 1):
        s = 0.0
        for i in range(len(win) - lag):
            s += win[i] * win[i + lag]
        scores.append(s / energy)
    best_i = max(range(len(scores)), key=lambda i: scores[i])
    best_score = scores[best_i]

    # Below this the "period" is noise agreeing with itself by chance; calling
    # that a pitch is worse than admitting there isn't one.
    if best_score < 0.35:
        return None

    # Parabolic interpolation around the peak. Whole-sample lags quantise badly
    # up here -- at 220 Hz one lag either way is over 20 cents, which is enough
    # to name the wrong note. Fitting a curve through the peak and its two
    # neighbours recovers the fraction between them. (The plugin's own YIN does
    # the same thing, for the same reason.)
    lag = lo + best_i
    if 0 < best_i < len(scores) - 1:
        a_, b_, c_ = scores[best_i - 1], best_score, scores[best_i + 1]
        den = a_ - 2 * b_ + c_
        if den != 0:
            lag += 0.5 * (a_ - c_) / den
    return sr / lag if lag > 0 else None


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
    ap.add_argument("--unique", action="store_true",
                    help="write each distinct capture once, skipping identical "
                         "copies (duplicated tracks share their captures)")
    ap.add_argument("--settings", action="store_true",
                    help="show what each slot is SET TO -- only the settings "
                         "you changed from their starting values")
    ap.add_argument("--all-settings", action="store_true", dest="all_settings",
                    help="with --settings, show every setting, not just the "
                         "ones you changed")
    args = ap.parse_args()
    if args.all_settings:
        args.settings = True

    if args.extract:
        os.makedirs(args.extract, exist_ok=True)

    written = 0
    # Duplicating a track duplicates its captures, so a project built by
    # copying one instance across twenty tracks holds twenty copies of the
    # same eight sounds. Hashing what we write lets --unique collapse that,
    # and lets the default at least SAY so rather than quietly producing 206
    # files for 14 sounds.
    seen_audio = {}
    duplicates = 0
    notes = []          # (instance label, [(slot number, lines), ...])
    note_seen = set()   # so duplicated tracks don't write the same page twice
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
            inst_notes = []
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

                if args.settings:
                    # One per line, on purpose. A screen reader gets a breath
                    # between each, and a tired reader gets to stop anywhere.
                    lines = slot_settings(info, s,
                                          changed_only=not args.all_settings)
                    if lines:
                        print("         you changed:"
                              if not args.all_settings else "         set to:")
                        for ln in lines:
                            print("            %s" % ln)
                    else:
                        print("         everything here is at its starting "
                              "value")
                    inst_notes.append((s + 1, lines))

                if args.extract:
                    key = hash(info["audio"][s])
                    if key in seen_audio:
                        duplicates += 1
                        if args.unique:
                            print("         (identical to %s -- skipped)"
                                  % seen_audio[key])
                            continue
                    fn = "%s_%s_inst%d_slot%d.wav" % (
                        safe(os.path.splitext(os.path.basename(path))[0]),
                        safe(inst["track"]), idx, s + 1)
                    seen_audio.setdefault(key, fn)
                    write_wav(os.path.join(args.extract, fn),
                              info["audio"][s], srate, args.as_float)
                    written += 1

            # One entry per INSTANCE, and identical instances only once.
            # Copying a track copies its settings too, so a project built by
            # duplicating one instance across twenty tracks would otherwise
            # write the same page out twenty times -- which is the wall this
            # is meant to spare someone, rebuilt.
            if inst_notes:
                fingerprint = tuple((n, tuple(ls)) for n, ls in inst_notes)
                if fingerprint not in note_seen:
                    note_seen.add(fingerprint)
                    notes.append((label, inst_notes))

    if args.extract and notes:
        # The WAVs are the RAW grabs -- the settings are what shapes them, and
        # they only existed inside the project. Writing them down next to the
        # audio means the setup survives the project too, and can be read
        # without opening a DAW.
        note_path = os.path.join(args.extract, "settings.txt")
        try:
            with open(note_path, "w", encoding="utf-8") as fh:
                fh.write("What each capture is set to.\n\n"
                         "The WAV files next to this are the raw grabs, before "
                         "any of these settings.\nThese are what shape them.\n")
                for label, slots in notes:
                    fh.write("\n\n%s\n%s\n" % (label, "-" * len(label)))
                    for slot, lines in slots:
                        fh.write("\nslot %d\n" % slot)
                        if lines:
                            for ln in lines:
                                fh.write("   %s\n" % ln)
                        else:
                            fh.write("   everything at its starting value\n")
            print("\nwrote your settings to %s" % note_path)
        except OSError as exc:
            print("\ncouldn't write the settings file: %s" % exc)

    if args.extract:
        print("\nwrote %d WAV(s) to %s" % (written, args.extract))
        if duplicates and not args.unique:
            print("%d of those are identical copies of others (duplicated tracks"
                  " share their captures)."
                  " Re-run with --unique to write %d file(s) instead."
                  % (duplicates, written - duplicates))
        elif duplicates:
            print("skipped %d identical copy/copies" % duplicates)
    return 0


if __name__ == "__main__":
    sys.exit(main())
