#!/usr/bin/env python3
"""Move the four live Breath Generator instances from the 32-slider layout to
the 40-slider one (docs/layouts/breath-gen.md).

AUTHORED, NOT INFERRED. Every one of the four instances below has its forty
values written out in full, read off the old slider line by hand. Nothing here
maps old positions to new ones by rule, because the pitch does not survive such
a rule: old sliders 5 and 6 were two independent filter frequencies on the
slider LINE, and the new layout keeps pitch in per-target BANKS inside the
serialized blob. So each instance also gets a freshly written blob.

The blob layout is read straight out of @serialize, in order:
  magic, sr_value[7], sr_dur[7], sr_delay[7], last_speed_target,
  drift_up[7], drift_down[7], drift_per[7], drift_shape[7], last_target_select,
  drift_play[7], drift_rest[7], sr_play[7], sr_rest[7],
  pitch_note[3], pitch_val[3], pitch_mode[3], pitch_fine[3], pitch_fmod[3],
  last_pitch_target

Every drift and ramp value below is @init's own default, because drift and ramp
are configured in ZERO instances -- confirmed again here by decoding the old
blobs: the only non-zero entries were drift_per = 8, which IS the default.
"""

import base64
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rpp_sliders

N_TARGETS = 7
N_PITCH = 3
MAGIC = 2400000 + N_TARGETS

# --- The four instances, authored -----------------------------------------
# `sliders` is slider1..slider40 in order. `pitch` is (inhale_note, inhale_hz,
# exhale_note, exhale_hz); the notes are the nearest MIDI note at or below the
# frequency at A4 = 440, the same convention @init uses for its own 800/600.
INSTANCES = [
    dict(
        path="E:/reaper/templates/breathscapes.RPP", nth=0,
        was="8 8 8 8 300 180 0.1 0.2 0.1 0.2 1 0 0 0 0 0",
        sliders=[
            1.875, 0,                      # breath rate (60/32), unit Seconds
            8, 8, 8, 8,                    # inhale, top, exhale, bottom
            0, 0, 62, 300, 0, 2, 440,      # pitch: All, Hz, D4, 300 Hz, no fine
            0.1, 0.2, 0.1, 0.2, 1,         # fades, Linear
            0, 0,                          # stereo width, flip
            0,                             # output dB
            0, 0, 0,                       # start delay, play, rest
            0, 0, 0, 8, 0, 0, 0, 0,        # drift, all @init defaults
            0, 0, 2, 0, 0, 0, 0, 0,        # ramp, all @init defaults
        ],
        pitch=(62, 300, 53, 180),
    ),
    dict(
        path="E:/reaper/to-play-with-later/micle.RPP", nth=0,
        was="8 0 12 0 420 350 0.3 0.2 0.2 0.3 3 0 0 0 0 0",
        sliders=[
            3.0, 0,                        # breath rate (60/20)
            8, 0, 12, 0,
            0, 0, 68, 420, 0, 2, 440,      # G#4, 420 Hz
            0.3, 0.2, 0.2, 0.3, 3,         # Exponential
            0, 0,
            0,
            0, 0, 0,
            0, 0, 0, 8, 0, 0, 0, 0,
            0, 0, 2, 0, 0, 0, 0, 0,
        ],
        pitch=(68, 420, 65, 350),
    ),
    dict(
        path="E:/reaper/to-play-with-later/organic-movement.RPP", nth=0,
        was="5 0.1 10 0.1 300 180 0.3 0.2 0.2 0.3 3 0 0",
        sliders=[
            3.947368, 0,                   # breath rate (60/15.2)
            5, 0.1, 10, 0.1,
            0, 0, 62, 300, 0, 2, 440,
            0.3, 0.2, 0.2, 0.3, 3,
            0, 0,
            0,
            0, 0, 0,
            0, 0, 0, 8, 0, 0, 0, 0,
            0, 0, 2, 0, 0, 0, 0, 0,
        ],
        pitch=(62, 300, 53, 180),
    ),
    dict(
        path="E:/reaper/to-play-with-later/organic-movement.RPP", nth=1,
        was="5 0.1 10 0.1 300 180 0.31 0.21 0.21 0.31 3 0 0",
        sliders=[
            3.947368, 0,
            5, 0.1, 10, 0.1,
            0, 0, 62, 300, 0, 2, 440,
            0.31, 0.21, 0.21, 0.31, 3,
            0, 0,
            0,
            0, 0, 0,
            0, 0, 0, 8, 0, 0, 0, 0,
            0, 0, 2, 0, 0, 0, 0, 0,
        ],
        pitch=(62, 300, 53, 180),
    ),
]


def build_blob(pitch):
    in_note, in_hz, ex_note, ex_hz = pitch
    f = [float(MAGIC)]
    f += [0.0] * N_TARGETS          # speed_ramp_target_value_mem
    f += [0.0] * N_TARGETS          # speed_ramp_dur_mem
    f += [0.0] * N_TARGETS          # speed_ramp_delay_mem
    f += [0.0]                      # last_speed_target
    f += [0.0] * N_TARGETS          # target_drift_up
    f += [0.0] * N_TARGETS          # target_drift_down
    f += [8.0] * N_TARGETS          # target_drift_per   (@init default)
    f += [0.0] * N_TARGETS          # target_drift_shape
    f += [0.0]                      # last_target_select
    f += [0.0] * N_TARGETS          # drift_play_mem
    f += [0.0] * N_TARGETS          # drift_rest_mem
    f += [0.0] * N_TARGETS          # sr_play_mem
    f += [0.0] * N_TARGETS          # sr_rest_mem
    # Slot 0 is `All`, a writing convenience; it mirrors Inhale so a reload
    # parked on All reads back the inhale, which is what pitch_read_slot does.
    f += [float(in_note), float(in_note), float(ex_note)]   # pitch_note_mem
    f += [float(in_hz),   float(in_hz),   float(ex_hz)]     # pitch_val_mem
    f += [0.0] * N_PITCH            # pitch_mode_mem: Hz
    f += [0.0] * N_PITCH            # pitch_fine_mem
    f += [2.0] * N_PITCH            # pitch_fmod_mem: Cents, matching slider12
    f += [0.0]                      # last_pitch_target: All
    # 11 per-target banks, 5 per-pitch banks, and four lone scalars: the magic
    # and the three `last selected` markers.
    expected = N_TARGETS * 11 + N_PITCH * 5 + 4
    assert len(f) == expected, (len(f), expected)
    return f


def blob_lines(floats, indent):
    raw = struct.pack('<%df' % len(floats), *floats)
    b64 = base64.b64encode(raw).decode('ascii')
    return [indent + b64[i:i + 128] for i in range(0, len(b64), 128)]


def find_instances(lines):
    return [i for i, l in enumerate(lines)
            if l.strip().startswith('<JS glasswings/breath_gen.jsfx')]


def main():
    dry = '--apply' not in sys.argv
    by_path = {}
    for inst in INSTANCES:
        by_path.setdefault(inst['path'], []).append(inst)

    for path, insts in by_path.items():
        with open(path, 'r', encoding='utf-8', newline='') as fh:
            lines = fh.readlines()
        heads = find_instances(lines)
        assert len(heads) == max(i['nth'] for i in insts) + 1, \
            '%s: found %d instances, authored %d' % (path, len(heads), len(insts))

        # Work from the bottom up so earlier line numbers stay valid.
        for inst in sorted(insts, key=lambda i: -i['nth']):
            head = heads[inst['nth']]
            vline = lines[head + 1]

            # Guard: the line we are replacing must be the one that was read.
            got = ' '.join(vline.split()[:len(inst['was'].split())])
            assert got == inst['was'], \
                '%s inst %d: expected %r, found %r' % (path, inst['nth'], inst['was'], got)

            slots = rpp_sliders.parse_line(vline)
            for n, v in enumerate(inst['sliders'], start=1):
                slots[n] = rpp_sliders.fmt(v)
            for n in range(len(inst['sliders']) + 1, 65):
                slots[n] = None
            lines[head + 1] = rpp_sliders.render_line(vline, slots, n_sliders=40)

            # The blob. Two of the four instances have no <JS_SER> at all, so
            # this both replaces and creates.
            indent = vline[:len(vline) - len(vline.lstrip())]
            outer = indent[:-2]
            new_ser = ['%s<JS_SER\n' % outer] \
                + [l + '\n' for l in blob_lines(build_blob(inst['pitch']), indent)] \
                + ['%s>\n' % outer]
            j = head + 2
            assert lines[j].strip() == '>', 'no closing > for the <JS block'
            j += 1
            if j < len(lines) and lines[j].strip() == '<JS_SER':
                k = j
                while lines[k].strip() != '>':
                    k += 1
                lines[j:k + 1] = new_ser
            else:
                lines[j:j] = new_ser
            print('%s instance %d: 40 sliders + %d-float blob'
                  % (os.path.basename(path), inst['nth'], len(build_blob(inst['pitch']))))

        if dry:
            print('  (dry run, nothing written -- pass --apply)')
        else:
            with open(path, 'w', encoding='utf-8', newline='') as fh:
                fh.writelines(lines)
            print('  written: %s' % path)


if __name__ == '__main__':
    main()
