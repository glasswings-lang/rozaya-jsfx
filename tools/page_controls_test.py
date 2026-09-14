"""page_controls_test.py -- would page_controls have caught what it exists for?

  python tools/page_controls_test.py

Passage's page said `-96 to +96, default 0` for Transpose value until 91ac919 widened the
control to -20000..20000. That old page, read against today's plugin, must be flagged on
exactly that line; today's page must not be.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import page_controls as pc
import suite_status as ss

ROOT = os.path.dirname(HERE)
fails = []


def check(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else f" -- {detail}"))
    if not ok:
        fails.append(label)


sl = ss.sliders(os.path.join(ROOT, "src", "spectral_vowel_passage.jsfx"))
old = subprocess.run(["git", "show", "91ac919^:docs/plugins/spectral-vowel-passage.md"], cwd=ROOT,
                     capture_output=True, text=True, encoding="utf-8").stdout
new = open(os.path.join(ROOT, "docs", "plugins", "spectral-vowel-passage.md"), encoding="utf-8").read()
tv = lambda found: [f for f in found if f[0].startswith("MISMATCH") and "Transpose value" in f[2]]
check("the old Passage page's Transpose value range is flagged", len(tv(pc.check_page(old, sl))) == 1,
      tv(pc.check_page(old, sl)))
check("today's Passage page's Transpose value is not flagged", tv(pc.check_page(new, sl)) == [],
      tv(pc.check_page(new, sl)))
fake = new.replace("**Fine tune (per slot)**", "**Fine tuning knob (per slot)**", 1)
check("a renamed control entry is flagged NOT IN PLUGIN",
      any(f[0] == "NOT IN PLUGIN" and "Fine tuning knob" in f[2] for f in pc.check_page(fake, sl)))
gone = new.replace("Tuning reference", "Tuning ref").replace("tuning reference", "tuning ref")
check("a control named nowhere on the page is flagged NOT ON PAGE",
      any(f[0] == "NOT ON PAGE" and "Tuning reference" in f[3] for f in pc.check_page(gone, sl)))

print(f"\n{'ALL PASS' if not fails else str(len(fails)) + ' FAILED'}")
sys.exit(1 if fails else 0)
