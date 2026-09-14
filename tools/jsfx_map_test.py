"""jsfx_map_test.py -- does jsfx_map still find what it was built to find?

  python tools/jsfx_map_test.py

1. Stage 3 of the Morpher pitch layout (ec2526f) put five layer banks into the new
   layer order and left the layers' random starting phases where they were. The
   report must raise exactly those four phase arrays as questions.
2. The Wash grain change (b4b8656) reordered nothing; it must raise no question.
3. The phase-order fix (82c6398) must not raise the phase arrays as questions.
4. Every plugin in src/ maps without error, with no overlapping fixed addresses,
   and the Morpher's table holds every `= freemem; freemem +=` line in the file.
"""
import glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "tools", "jsfx_map.py")
MORPHER = "src/spectral_vowel_morpher.jsfx"
PHASES = {"lay_hph", "lay_hphB", "lay_hphR", "lay_hphBR"}
fails = []


def run(*args):
    r = subprocess.run([sys.executable, MAP, *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        fails.append(f"{args}: exit {r.returncode}: {r.stderr.strip()[-300:]}")
    return r.stdout


def questions(rev):
    r = json.loads(run("impact", "--git", rev, MORPHER, "--json"))
    return {o["name"] for o in r["order_sensitive"]
            if o["why"] == "untreated sibling" and "rand" in o["what"] and o["when"] == "start"}


def check(label, ok, detail):
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else f" -- {detail}"))
    if not ok:
        fails.append(label)


q = questions("ec2526f")
check("stage 3 raises the four layer phase arrays, and only them", q == PHASES, sorted(q))
q = questions("b4b8656")
check("Wash grain change raises no question", q == set(), sorted(q))
q = questions("82c6398")
check("phase-order fix does not raise the phase arrays", not (q & PHASES), sorted(q))

plugins = sorted(glob.glob(os.path.join(ROOT, "src", "*.jsfx")))
check("found the plugins", len(plugins) >= 19, len(plugins))
for f in plugins:
    out = run("map", os.path.relpath(f, ROOT))
    bad = re.findall(r"\(gap-?0\)|\(gap-\d+\)", out)
    check(f"{os.path.basename(f)} maps, no overlapping addresses", "Memory, in allocation order" in out and not bad, bad)

text = open(os.path.join(ROOT, MORPHER), encoding="utf-8").read()
text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
want = len(re.findall(r"^\s*[A-Za-z_]\w*\s*=\s*freemem\s*;\s*freemem\s*\+=", re.sub(r"//.*", "", text), flags=re.M))
got = int(re.search(r"Memory, in allocation order \((\d+)\)", run("map", MORPHER)).group(1))
check(f"Morpher memory table holds all {want} freemem allocations", got == want and want > 80, f"table {got}")

print(f"\n{'ALL PASS' if not fails else str(len(fails)) + ' FAILED'}")
sys.exit(1 if fails else 0)
