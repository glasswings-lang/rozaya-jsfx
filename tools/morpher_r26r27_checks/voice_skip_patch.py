import sys
p = sys.argv[1]
s=open(p,encoding='utf-8',newline='').read(); nl='\r\n' if '\r\n' in s else '\n'; s=s.replace('\r\n','\n')
ERR=[]
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: ERR.append((a[:70],c,n)); return
    s=s.replace(a,b)
A = ["vvAL += hmA*hcg*wtsin(hph[vn]);", "vvAR += hmA*hcg*wtsin(hphR[vn]);",
     "vvA += hmA_arr[vn]*hcg*wtsin(hph[vn]);",
     "lyv_al += hmA*hcg*wtsin(lay_hph[lybo+vn]);", "lyv_ar += hmA*hcg*wtsin(lay_hphR[lybo+vn]);",
     "lyv_al += lyhA[vn]*hcg*wtsin(lay_hph[lybo+vn]);"]
B = ["vvBL += hmB*hcg*wtsin(hphB[vn]);", "vvBR += hmB*hcg*wtsin(hphBR[vn]);",
     "vvB += hmB_arr[vn]*hcg*wtsin(hphB[vn]);",
     "lyv_bl += hmB*hcg*wtsin(lay_hphB[lybo+vn]);", "lyv_br += hmB*hcg*wtsin(lay_hphBR[lybo+vn]);",
     "lyv_bl += lyhB[vn]*hcg*wtsin(lay_hphB[lybo+vn]);"]
for a in A: rep(a, "vA ? ( " + a[:-1] + " );")
for b in B: rep(b, "vB ? ( " + b[:-1] + " );")
rep("(hlevel > 0.0001 && have > 0) ? (\n  fA = slot_f0[vsi] * pitch_ratio;",
"""(hlevel > 0.0001 && have > 0) ? (
  // Only the voices the morph is actually on are summed (2026-09-16). At vmfr 0 voice B is
  // multiplied by 0, at 1 voice A is: its sines are skipped, and its phases still advance so
  // it rejoins in step. Focused slot sits at 0 all the time, and half the engine was wasted.
  vA = vmfr != 1; vB = vmfr != 0;
  fA = slot_f0[vsi] * pitch_ratio;""")
if ERR:
    for e in ERR: print('NO MATCH', e)
    raise SystemExit('NOTHING WRITTEN')
open(p,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))
print('voice skip applied to', p)
