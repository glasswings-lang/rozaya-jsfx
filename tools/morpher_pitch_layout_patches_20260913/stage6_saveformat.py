p = "C:/git-src/rozaya-jsfx/src/spectral_vowel_morpher.jsfx"
t = open(p, encoding="utf-8", newline="").read()
NL = "\r\n"


def crlf(s):
    return s.replace("\r\n", "\n").replace("\n", NL)


def once(old, new):
    global t
    old, new = crlf(old), crlf(new)
    assert t.count(old) == 1, (t.count(old), old[:90])
    t = t.replace(old, new)


# --- the magic, and what it accepts
once("//   7700055 -- current (2026-09-11). Fifty-five targets in control order. Every\n"
     "//              older magic reads at its own width, runs the migrations below, and\n"
     "//              is then remapped from the 24-target list, selectors included.\n"
     "ser_magic = 7700055;",
     "//   7700055 -- (2026-09-11). Fifty-five targets in control order. Every\n"
     "//              older magic reads at its own width, runs the migrations below, and\n"
     "//              is then remapped from the 24-target list, selectors included.\n"
     "//   7700087 -- current (2026-09-13, the pitch layout). 87 targets, Layer 1-16 in their new\n"
     "//              order, and APPENDED at the very end: every layer's pitch, pitch unit, fine\n"
     "//              tune and fine tune unit, the Layer selector as shown (All included), and the\n"
     "//              Drift amount unit and Ramp by unit per target. Read only from a blob that\n"
     "//              WROTE them; an older one keeps @init's defaults (the ladder's intervals,\n"
     "//              Semitones, no fine tune, Target default), which are what the slider\n"
     "//              migration seeds, and walks 55 -> 87 and the ladder -> Layer 1-16 below.\n"
     "ser_magic = 7700087;")
once("(ser_magic == 7700055 || ser_magic == 7700011",
     "(ser_magic == 7700087 || ser_magic == 7700055 || ser_magic == 7700011")
once("n_ser_targets = ser_magic == 7700055 ? 55 :",
     "ser_new = ser_magic >= 7700087;   // holds the pitch layout's appended banks\n"
     "  n_ser_targets = ser_magic == 7700087 ? N_TARGETS : ser_magic == 7700055 ? 55 :")

# --- the appended banks, after the last field any older blob holds
once("  file_mem(0, target_drift_play, n_ser_targets);\n"
     "  file_mem(0, target_drift_rest, n_ser_targets);\n"
     "  file_mem(0, ramp_play_mem,     n_ser_targets);\n"
     "  file_mem(0, ramp_rest_mem,     n_ser_targets);\n",
     "  file_mem(0, target_drift_play, n_ser_targets);\n"
     "  file_mem(0, target_drift_rest, n_ser_targets);\n"
     "  file_mem(0, ramp_play_mem,     n_ser_targets);\n"
     "  file_mem(0, ramp_rest_mem,     n_ser_targets);\n"
     "\n"
     "  // --- 7700087 (2026-09-13): the pitch layout's banks, APPENDED at the very end. Gated on the\n"
     "  //     magic that WROTE them, never on EOF (Passage's rule). The selector is saved as SHOWN,\n"
     "  //     0 = All, since last_lay_sel above holds only a layer. ---\n"
     "  ser_new ? (\n"
     "    file_avail(0) < 0 ? ( ser_lay_selv = last_lay_selv; );\n"
     "    file_mem(0, lay_semi,  N_LAY_SLOTS);\n"
     "    file_mem(0, lay_punit, N_LAY_SLOTS);\n"
     "    file_mem(0, lay_fine,  N_LAY_SLOTS);\n"
     "    file_mem(0, lay_funit, N_LAY_SLOTS);\n"
     "    file_var(0, ser_lay_selv);\n"
     "    file_mem(0, target_drift_unit, N_TARGETS);\n"
     "    file_mem(0, ramp_by_unit,      N_TARGETS);\n"
     "  );\n")

# --- the read branch: the selector from the blob that saved it
once("    last_lay_sel = max(0, min(N_LAY_SLOTS-1, last_lay_sel | 0));\n"
     "    lay_selv = last_lay_sel + 1; last_lay_selv = lay_selv;\n",
     "    last_lay_sel = max(0, min(N_LAY_SLOTS-1, last_lay_sel | 0));\n"
     "    lay_selv = ser_new ? max(0, min(N_LAY_SLOTS, ser_lay_selv | 0)) : last_lay_sel + 1;\n"
     "    last_lay_sel = lay_selv == 0 ? 0 : lay_selv - 1; last_lay_selv = lay_selv;\n")

assert "\n" not in t.replace("\r\n", "")
open(p, "w", encoding="utf-8", newline="").write(t)
print("written")
