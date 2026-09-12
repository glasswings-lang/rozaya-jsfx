#!/usr/bin/env python3
"""Drive REAPER through kin_bridge.lua and wait for its answers.

The bridge (C:/Users/solst/AppData/Roaming/REAPER/Scripts/kin_bridge.lua) must be
running in REAPER. Its command list is at the top of that file.

    python tools/reaper_bridge.py "state"
    python tools/reaper_bridge.py "goto 12.5" "state"

As a module:  send("state") -> "ok play_state=0 ..."; board() -> the manifest parsed.
"""
import itertools, os, re, sys, time

DIR = r"C:\Users\solst\reaper_kin_bridge"
CMD, MAN, REPLY = (os.path.join(DIR, f) for f in ("command.txt", "manifest.txt", "reply.txt"))
# Unique across runs: reply.txt is never emptied by the bridge, and a clock-based counter
# once matched a previous run's answer (2026-09-12).
_ids = itertools.count(1)
_run = f"{os.getpid()}x{time.time_ns() % 10**12}"


def send(command, timeout=5.0):
    """Send one command; return (ok, text). Raises TimeoutError if the bridge never answers."""
    tag = f"@c{_run}n{next(_ids)}"
    with open(CMD, "a", encoding="utf-8") as f:
        f.write(f"{tag} {command}\n")
    end = time.time() + timeout
    while time.time() < end:
        try:
            for line in open(REPLY, encoding="utf-8", errors="replace"):
                if line.startswith(tag + " "):
                    status, _, text = line[len(tag) + 1:].rstrip("\n").partition(" ")
                    return status == "ok", text
        except FileNotFoundError:
            pass
        time.sleep(0.02)
    raise TimeoutError(f"no answer to {command!r} in {timeout} s -- is kin_bridge.lua running?")


def board():
    """The manifest: {'transport': {...}, 'tracks': [{name, fx: [{name, params: {i: (name, norm, text)}}]}]}"""
    out = {"transport": {}, "tracks": []}
    for line in open(MAN, encoding="utf-8", errors="replace"):
        if line.startswith("# transport "):
            out["transport"] = dict(re.findall(r'(\w+)="?([^"\s]*)"?', line[12:]))
        elif m := re.match(r'track=(\d+) name="(.*)" fx_count', line):
            out["tracks"].append({"name": m[2], "fx": []})
        elif m := re.match(r'\s+fx=(\d+) name="(.*)" params', line):
            out["tracks"][-1]["fx"].append({"name": m[2], "params": {}})
        elif m := re.match(r'\s+p(\d+) "(.*)" norm=(\S+) val="(.*)"', line):
            out["tracks"][-1]["fx"][-1]["params"][int(m[1])] = (m[2], float(m[3]), m[4])
    return out


if __name__ == "__main__":
    for c in sys.argv[1:]:
        ok, text = send(c)
        print(("ok  " if ok else "ERR ") + c + " -> " + text)
