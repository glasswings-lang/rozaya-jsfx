#!/usr/bin/env python3
"""
rate_calc.py -- works out the base rate for a second plugin instance so one
of its voices lands exactly where you want it, relative to a voice in the
first instance.

Why it exists: voices inside an instance stack UPWARD from the base rate.
So placing a high-numbered voice LOW means cancelling the stack as well as
making the shift -- two subtractions pulling opposite ways, held at once.
That's a bookkeeping job, not a music job. This does the bookkeeping and
shows its work so you can check it by reading instead of by remembering.

No plugin can do this itself: instance 2 has no idea instance 1 exists.
It has to live out here.

Nothing to install -- standard library only.

    python tools/rate_calc.py --base 30 --aim 8 --offset -0.05

Run with --help for the full flag list.
"""

import argparse
import sys


# ---------------------------------------------------------------- THE MATH

def voice_rate(base, n, step):
    """Rate of voice n. Voice 1 sits at the base rate."""
    return base + (n - 1) * step


def base_needed(target_rate, aim_voice, step):
    """What base rate puts voice `aim_voice` exactly on `target_rate`."""
    return target_rate - (aim_voice - 1) * step


# ------------------------------------------------------------------ OUTPUT

def make_fmt(decimals):
    return lambda x: ("%." + str(decimals) + "f") % x


# Everything shown also gets kept, so --save can write it to a file.
# Reading a table in an editor beats scrolling back through a terminal.
CAPTURED = []


def say(line=""):
    CAPTURED.append(line)
    print(line)


def say_voices(base, voices, step, fmt, mark=None, mark_txt=""):
    say("  voice      rate")
    say("  " + "-" * 22)
    for n in range(1, voices + 1):
        tag = mark_txt if (mark is not None and n == mark) else ""
        say("  %3d    %10s%s" % (n, fmt(voice_rate(base, n, step)), tag))
    say()


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="rate_calc.py",
        description="Base rate for a second instance so a chosen voice lands "
                    "where you want it. Shows its work.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # 8th voice of instance 2, one step below instance 1's first voice
  python tools/rate_calc.py --base 30 --aim 8 --offset -0.05

  # same, but land it against instance 1's voice 4 instead
  python tools/rate_calc.py --base 30 --aim 8 --against 4 --offset -0.05

  # just show me what one instance's voices are doing
  python tools/rate_calc.py --base 30 --show

  # I already set instance 2 to 29.6 -- what did that actually give me?
  python tools/rate_calc.py --base 30 --inspect 29.6 --aim 8
""")

    p.add_argument("--base", type=float, required=False, default=30.0,
                   metavar="BPM",
                   help="base rate of the FIRST instance (default: 30)")
    p.add_argument("--step", type=float, default=0.05, metavar="BPM",
                   help="how much faster each voice runs than the one before "
                        "(default: 0.05)")
    p.add_argument("--voices", type=int, default=8, metavar="N",
                   help="voices per instance (default: 8)")

    p.add_argument("--aim", type=int, default=8, metavar="N",
                   help="which voice of the SECOND instance you're placing "
                        "(default: 8)")
    p.add_argument("--against", type=int, default=1, metavar="N",
                   help="which voice of the FIRST instance to place it "
                        "against (default: 1)")
    p.add_argument("--offset", type=float, default=-0.05, metavar="BPM",
                   help="how far off that voice you want it. negative = "
                        "slower (default: -0.05)")

    p.add_argument("--inspect", type=float, default=None, metavar="BPM",
                   help="reverse mode: you already set instance 2 to this "
                        "rate -- report what offset that actually produced")
    p.add_argument("--show", action="store_true",
                   help="just list one instance's voices and stop")
    p.add_argument("--merged", action="store_true",
                   help="also list all voices from both instances together, "
                        "slowest first, with the gap between each")
    p.add_argument("--decimals", type=int, default=3, metavar="N",
                   help="decimal places to show (default: 3)")
    p.add_argument("--save", nargs="?", const="rate_calc_report.txt",
                   default=None, metavar="FILE",
                   help="also write everything to a text file you can open in "
                        "an editor (default name: rate_calc_report.txt)")

    a = p.parse_args(argv)
    fmt = make_fmt(a.decimals)

    def finish(code):
        if a.save:
            with open(a.save, "w") as fh:
                fh.write("\n".join(CAPTURED) + "\n")
            print("(Saved to %s)" % a.save)
        return code

    # --- sanity checks, so a typo says so instead of printing nonsense
    if a.voices < 1:
        p.error("--voices must be at least 1")
    if not (1 <= a.aim <= a.voices):
        p.error("--aim must be between 1 and %d (you have %d voices)"
                % (a.voices, a.voices))
    if not (1 <= a.against <= a.voices):
        p.error("--against must be between 1 and %d (you have %d voices)"
                % (a.voices, a.voices))

    say()
    say("RATE CALC")
    say("=" * 46)
    say("Instance 1 base: %s bpm" % fmt(a.base))
    say("Voices: %d, each %s bpm above the last" % (a.voices, fmt(a.step)))
    say()

    # --- just show one instance and stop
    if a.show:
        say("Instance 1 voices:")
        say()
        say_voices(a.base, a.voices, a.step, fmt)
        return finish(0)

    anchor = voice_rate(a.base, a.against, a.step)

    # --- reverse mode: they already set it, what did they get
    if a.inspect is not None:
        got = voice_rate(a.inspect, a.aim, a.step)
        gap = got - anchor
        say("You set instance 2 to %s bpm." % fmt(a.inspect))
        say()
        say("  voice %d of instance 2 is at   %s" % (a.aim, fmt(got)))
        say("  voice %d of instance 1 is at   %s" % (a.against, fmt(anchor)))
        say("  " + "-" * 34)
        say("  difference:                   %s bpm" % fmt(gap))
        say()
        say("Instance 2 voices:")
        say()
        say_voices(a.inspect, a.voices, a.step, fmt,
                     mark=a.aim, mark_txt="   <- this one")
        return finish(0)

    # --- forward mode: what should they dial in
    target = anchor + a.offset
    base_b = base_needed(target, a.aim, a.step)
    shift = base_b - a.base
    stack = (a.aim - 1) * a.step

    say("You want voice %d of instance 2" % a.aim)
    say("to sit %s bpm from voice %d of instance 1 (%s bpm)."
          % (fmt(a.offset), a.against, fmt(anchor)))
    say()
    say("-" * 46)
    say("  DIAL IN:  %s bpm" % fmt(base_b))
    say("  (%s bpm from instance 1)" % fmt(shift))
    say("-" * 46)
    say()
    say("The working:")
    say("  voice %d of instance 1      %10s" % (a.against, fmt(anchor)))
    say("  your offset                %10s" % fmt(a.offset))
    say("  = target                   %10s" % fmt(target))
    say("  minus the stack (%d x %s) %10s"
          % (a.aim - 1, fmt(a.step), "-" + fmt(stack)))
    say("  = base rate                %10s" % fmt(base_b))
    say()

    say("Instance 2 voices:")
    say()
    say_voices(base_b, a.voices, a.step, fmt,
                 mark=a.aim, mark_txt="   <- this one")

    # --- verify, out loud
    hit = voice_rate(base_b, a.aim, a.step)
    gap = hit - anchor
    say("Check: voice %d of instance 2 lands at %s," % (a.aim, fmt(hit)))
    say("       voice %d of instance 1 is at %s."
          % (a.against, fmt(anchor)))
    say("       difference %s, you asked for %s."
          % (fmt(gap), fmt(a.offset)))
    if abs(gap - a.offset) < 1e-9:
        say("       Matches.")
    else:
        say("       DOES NOT MATCH -- something is wrong, don't trust this.")
        return finish(1)
    say()

    if a.merged:
        every = sorted(
            [("1", voice_rate(a.base, n, a.step)) for n in range(1, a.voices + 1)]
            + [("2", voice_rate(base_b, n, a.step)) for n in range(1, a.voices + 1)],
            key=lambda pair: pair[1])
        say("All %d voices together, slowest first:" % (a.voices * 2))
        say()
        prev = None
        for inst, r in every:
            gap_txt = "" if prev is None else "   (+%s)" % fmt(r - prev)
            say("  %10s   instance %s%s" % (fmt(r), inst, gap_txt))
            prev = r
        say()

    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
