#!/usr/bin/env python3
"""Measure, in the runner, whether a Drift/Ramp control switches with its target.

R25's labels came from a live probe on 2026-09-12. This re-measures them OUT of REAPER,
so the claim on every label can be checked at any time, by anyone, in about a minute.

Method, per control: put the target picker on option 1, set the control to a value that is
NOT its default, step a block, move the picker to option 0, and read the control back.
  value survived  -> ONE value serves every target      -> "(all targets)"
  value reverted  -> it switches with the picker        -> no mark
`Drift period` is measured alongside as the control case: it MUST come back per-target, or
the method itself is broken and no other result here means anything.
"""
import glob, os, re, subprocess, sys

RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'jsfx_run', 'build', 'Release', 'jsfx_run.exe')
SLIDER = re.compile(r'^slider(\d+):([^<]*)<([^>]*)>(.*)$')

def sliders(path):
    out = {}
    for ln in open(path, encoding='utf-8', errors='replace'):
        m = SLIDER.match(ln.rstrip('\n'))
        if m:
            out[int(m.group(1))] = (m.group(4).strip(), m.group(3))
    return out

def find(sl, prefix):
    for n, (name, _) in sorted(sl.items()):
        if name.lower().startswith(prefix.lower()):
            return n, name
    return None, None

def read_back(path, sel, sel_to, num, val):
    cmd = [RUN, path, '--set-after', f'{sel}=1', '--stage',
           '--set-after', f'{num}={val}', '--stage',
           '--set-after', f'{sel}={sel_to}', '--list']
    r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    for ln in r.stdout.splitlines():
        m = re.match(r'\s*slider%d\s+.*?=\s*([-\d.]+)' % num, ln)
        if m:
            return float(m.group(1))
    return None

CHECKS = [('Drift target', 'Drift period unit'), ('Drift target', 'Drift period mode'),
          ('Ramp target', 'Ramp time unit'), ('Ramp target', 'Ramp engage')]
bad = 0
for path in sorted(glob.glob('src/*.jsfx')):
    sl = sliders(path)
    print('== %s' % os.path.basename(path))
    dsel, _ = find(sl, 'Drift target')
    dper, dname = find(sl, 'Drift period (')
    if dsel and dper:
        got = read_back(path, dsel, 0, dper, 7.25)
        print('   %-42s %s' % ('CONTROL CASE  ' + dname,
              'per target (reverted to %g) OK' % got if got != 7.25 else 'SHARED -- METHOD BROKEN'))
        if got == 7.25:
            bad += 1
    for selname, ctlname in CHECKS:
        sel, _ = find(sl, selname)
        num, name = find(sl, ctlname)
        if not (sel and num):
            continue
        lo, hi = re.match(r'([-\d.]+),([-\d.]+)', sl[num][1]).groups()
        val = float(hi) if float(hi) <= 4 else 1.0
        got = read_back(path, sel, 0, num, val)
        shared = (got == val)
        marked = '(all targets)' in name or 'all targets' in name
        agree = 'agrees' if shared == marked else '*** DISAGREES WITH ITS LABEL ***'
        if shared != marked:
            bad += 1
        print('   %-42s %-12s label says %-13s %s'
              % (name, 'shared' if shared else 'per target',
                 'shared' if marked else 'per target', agree))
print()
print('MISMATCHES: %d' % bad)
sys.exit(1 if bad else 0)
