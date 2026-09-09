// jsfx_run -- compile and RUN a JSFX plugin outside REAPER, and read what comes out.
//
// This exists because every check in this repo has been a check of the SOURCE
// TEXT. Reading proves what the code says; it does not prove what the plugin
// does. On 2026-09-08 a Breath Generator rebuild passed 238 file assertions, a
// clean lint, a verified migration and three careful read-throughs, and was
// still audibly broken the moment Rozaya pressed play. Nothing in the toolchain
// could have caught that, because nothing in the toolchain had ever run a
// plugin.
//
// Built on ysfx (github.com/jpcima/ysfx, Apache-2.0), which is a real JSFX
// compiler and runtime. See README.md here for the build.
//
// Public domain (CC0), like the rest of this suite.

#include "ysfx.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <map>

static void usage()
{
    std::printf(
        "usage: jsfx_run <file.jsfx> [options]\n"
        "\n"
        "  --list              print every slider (id, name, range, current) and exit\n"
        "  --sr N              sample rate, default 44100\n"
        "  --block N           block size, default 512\n"
        "  --seconds S         how long to run, default 10\n"
        "  --rpp FILE          load a REAL project's state -- the slider line AND\n"
        "                      the <JS_SER> blob -- exactly as a host would\n"
        "  --fx SUBSTR         which plugin inside that project (substring match)\n"
        "  --instance N        which instance of it, 1-based, default 1\n"
        "  --slider N=V        set slider N (1-based, as written in the .jsfx) to V.\n"
        "                      Repeatable. Applied BEFORE @init, like a project load.\n"
        "  --set-after N=V     same, but applied AFTER init and the first block --\n"
        "                      this is what moving a control by hand looks like.\n"
        "  --rms MS            print an RMS envelope every MS ms, default 50\n"
        "  --csv FILE          dump every output sample as time,L,R\n"
        "  --quiet             suppress the envelope (use with --csv)\n"
        "\n"
        "The envelope is what you want for anything rhythmic: each line is one\n"
        "window, so segment boundaries are visible as the level moving.\n");
}

struct Assign { uint32_t idx; double val; };

// ---------------------------------------------------------------------------
// Loading a REAL project's state: the slider line AND the <JS_SER> blob.
//
// This is the whole point. Setting sliders by hand exercises the fresh-instance
// path; a project load ALSO restores serialized memory, by an independent path
// with no guaranteed order against @slider. Bugs live in that gap, and nothing
// in this repo could reach it before.
// ---------------------------------------------------------------------------

static int b64val(char c)
{
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+') return 62;
    if (c == '/') return 63;
    return -1;
}

static std::vector<uint8_t> b64decode(const std::string &s)
{
    std::vector<uint8_t> out;
    int acc = 0, bits = 0;
    for (char c : s) {
        int v = b64val(c);
        if (v < 0) continue;                 // skips '=' and whitespace
        acc = (acc << 6) | v; bits += 6;
        if (bits >= 8) { bits -= 8; out.push_back((uint8_t)((acc >> bits) & 0xFF)); }
    }
    return out;
}

// Parse the value line the way tools/rpp_sliders.py does, and for the same
// reasons: a '-' means nothing stored, and past 64 sliders REAPER writes a
// quoted "" marker at token index 64 which is NOT a slider.
static void parse_value_line(const std::string &line,
                             std::vector<ysfx_state_slider_t> &out)
{
    std::vector<std::string> tok;
    for (size_t i = 0; i < line.size();) {
        while (i < line.size() && std::isspace((unsigned char)line[i])) ++i;
        size_t j = i;
        while (j < line.size() && !std::isspace((unsigned char)line[j])) ++j;
        if (j > i) tok.push_back(line.substr(i, j - i));
        i = j;
    }
    for (size_t k = 0; k < tok.size(); ++k) {
        if (k == 64 && tok.size() > 64) continue;          // the "" marker
        uint32_t sid = (k < 64) ? (uint32_t)k : (uint32_t)(k - 1);
        if (sid >= ysfx_max_sliders) break;
        if (tok[k] == "-" || tok[k].front() == '"') continue;
        ysfx_state_slider_t s{};
        s.index = sid;
        s.value = std::strtod(tok[k].c_str(), nullptr);
        out.push_back(s);
    }
}

// Returns false if the plugin was not found in the project.
static bool load_from_rpp(const char *rpp, const char *fxmatch,
                          std::vector<ysfx_state_slider_t> &sliders,
                          std::vector<uint8_t> &blob, int which)
{
    FILE *f = std::fopen(rpp, "rb");
    if (!f) { std::fprintf(stderr, "cannot open %s\n", rpp); return false; }
    std::vector<std::string> lines;
    { std::string cur; int c;
      while ((c = std::fgetc(f)) != EOF) {
          if (c == '\n') { lines.push_back(cur); cur.clear(); }
          else if (c != '\r') cur.push_back((char)c);
      }
      if (!cur.empty()) lines.push_back(cur);
    }
    std::fclose(f);

    int seen = 0;
    for (size_t i = 0; i < lines.size(); ++i) {
        if (lines[i].find(fxmatch) == std::string::npos) continue;
        if (lines[i].find("<JS") == std::string::npos) continue;
        if (++seen != which) continue;

        for (size_t j = i + 1; j < lines.size() && j < i + 6; ++j) {
            const std::string &t = lines[j];
            size_t p = t.find_first_not_of(" \t");
            if (p == std::string::npos) continue;
            char c0 = t[p];
            if (std::isdigit((unsigned char)c0) || c0 == '-' || c0 == '"') {
                parse_value_line(t, sliders);
                break;
            }
        }
        for (size_t j = i + 1; j < lines.size() && j < i + 8; ++j) {
            if (lines[j].find("<JS_SER") == std::string::npos) continue;
            std::string b;
            for (size_t k = j + 1; k < lines.size(); ++k) {
                size_t p = lines[k].find_first_not_of(" \t");
                if (p != std::string::npos && lines[k][p] == '>') break;
                b += lines[k].substr(p == std::string::npos ? 0 : p);
            }
            blob = b64decode(b);
            break;
        }
        return true;
    }
    std::fprintf(stderr, "no <JS ...%s> instance #%d in %s\n", fxmatch, which, rpp);
    return false;
}

static bool parse_assign(const char *s, Assign &out)
{
    const char *eq = std::strchr(s, '=');
    if (!eq) return false;
    long n = std::strtol(s, nullptr, 10);
    if (n < 1 || n > (long)ysfx_max_sliders) return false;
    out.idx = (uint32_t)(n - 1);          // ysfx is 0-based; the source is 1-based
    out.val = std::strtod(eq + 1, nullptr);
    return true;
}

int main(int argc, char **argv)
{
    if (argc < 2) { usage(); return 2; }
    const char *path = argv[1];
    double sr = 44100.0, seconds = 10.0, rms_ms = 50.0;
    uint32_t block = 512;
    bool list_only = false, quiet = false;
    const char *csv = nullptr, *rpp = nullptr, *fxmatch = nullptr;
    int which = 1;
    std::vector<Assign> before;
    std::vector<std::vector<Assign>> stages(1);

    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> const char * {
            if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); }
            return argv[++i];
        };
        if (a == "--list") list_only = true;
        else if (a == "--quiet") quiet = true;
        else if (a == "--sr") sr = std::strtod(next(), nullptr);
        else if (a == "--block") block = (uint32_t)std::strtoul(next(), nullptr, 10);
        else if (a == "--seconds") seconds = std::strtod(next(), nullptr);
        else if (a == "--rms") rms_ms = std::strtod(next(), nullptr);
        else if (a == "--csv") csv = next();
        else if (a == "--rpp") rpp = next();
        else if (a == "--fx") fxmatch = next();
        else if (a == "--instance") which = (int)std::strtol(next(), nullptr, 10);
        else if (a == "--slider" || a == "--set-after") {
            Assign as{};
            if (!parse_assign(next(), as)) { std::fprintf(stderr, "bad assignment\n"); return 2; }
            (a == "--slider" ? before : stages.back()).push_back(as);
        }
        else if (a == "--stage") stages.push_back({});
        else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); usage(); return 2; }
    }

    ysfx_config_t *cfg = ysfx_config_new();
    ysfx_t *fx = ysfx_new(cfg);

    if (!ysfx_load_file(fx, path, 0)) {
        std::fprintf(stderr, "FAILED TO LOAD: %s\n", path);
        return 1;
    }
    // Compile WITH @serialize and WITHOUT gfx. Real error messages, which is
    // half the point of having a compiler at all.
    if (!ysfx_compile(fx, ysfx_compile_no_gfx)) {
        std::fprintf(stderr, "FAILED TO COMPILE: %s\n", path);
        return 1;
    }
    std::printf("loaded and compiled: %s\n", ysfx_get_name(fx) ? ysfx_get_name(fx) : path);

    // --list used to return HERE, before any slider or project state was
    // applied, so it printed the DECLARED defaults and silently ignored
    // everything you had asked for. It now lists what the plugin actually
    // HOLDS, after a real block has run -- which is the only version that can
    // show you a value the plugin computed for itself.
    if (list_only) {
        ysfx_set_sample_rate(fx, sr);
        ysfx_set_block_size(fx, block);
        for (const Assign &a : before) ysfx_slider_set_value(fx, a.idx, a.val);
        ysfx_init(fx);
        {
            std::vector<float> l(block, 0.0f), r(block, 0.0f);
            const float *ii[2] = { l.data(), r.data() };
            float *oo[2] = { l.data(), r.data() };
            ysfx_process_float(fx, ii, oo, 2, 2, block);
            for (const auto &st : stages) {
                for (const Assign &a : st) ysfx_slider_set_value(fx, a.idx, a.val);
                ysfx_process_float(fx, ii, oo, 2, 2, block);
            }
        }
        for (uint32_t i = 0; i < ysfx_max_sliders; ++i) {
            if (!ysfx_slider_exists(fx, i)) continue;
            ysfx_slider_range_t r{};
            ysfx_slider_get_range(fx, i, &r);
            std::printf("  slider%-3u %-52s [%g .. %g step %g] = %g%s\n",
                        i + 1, ysfx_slider_get_name(fx, i),
                        r.min, r.max, r.inc, ysfx_slider_get_value(fx, i),
                        ysfx_slider_is_enum(fx, i) ? "  (enum)" : "");
        }
        return 0;
    }

    ysfx_set_sample_rate(fx, sr);
    ysfx_set_block_size(fx, block);

    // A REAL project load: slider values AND the serialized blob, together,
    // through the same entry point a host uses. This is the path that a
    // hand-set-sliders run cannot reach, and it is where the restore-order
    // bugs in this suite have always lived.
    if (rpp) {
        if (!fxmatch) fxmatch = ".jsfx";
        std::vector<ysfx_state_slider_t> ss;
        std::vector<uint8_t> blob;
        if (!load_from_rpp(rpp, fxmatch, ss, blob, which)) return 1;
        ysfx_state_t st{};
        st.sliders = ss.data();
        st.slider_count = (uint32_t)ss.size();
        st.data = blob.data();
        st.data_size = blob.size();
        if (!ysfx_load_state(fx, &st)) {
            std::fprintf(stderr, "ysfx_load_state failed\n");
            return 1;
        }
        std::printf("project state loaded: %u sliders, %zu bytes serialized\n",
                    st.slider_count, blob.size());
    }

    // Sliders set by hand, which is the fresh-instance path.
    for (const Assign &a : before) ysfx_slider_set_value(fx, a.idx, a.val);
    if (!rpp) ysfx_init(fx);

    uint32_t total = (uint32_t)(seconds * sr);
    uint32_t win = (uint32_t)(rms_ms * 0.001 * sr);
    if (win < 1) win = 1;

    std::vector<float> inL(block, 0.0f), inR(block, 0.0f);
    std::vector<float> outL(block, 0.0f), outR(block, 0.0f);
    const float *ins[2] = { inL.data(), inR.data() };
    float *outs[2] = { outL.data(), outR.data() };

    FILE *cf = nullptr;
    if (csv) {
        cf = std::fopen(csv, "w");
        if (!cf) { std::fprintf(stderr, "cannot write %s\n", csv); return 1; }
        std::fprintf(cf, "sample,seconds,L,R\n");
    }

    if (!quiet)
        std::printf("\n  time(s)        rmsL        rmsR      peakL      peakR\n");

    double accL = 0, accR = 0, pkL = 0, pkR = 0;
    uint32_t inwin = 0, done = 0;
    size_t stage_i = 0;

    while (done < total) {
        uint32_t n = block;
        if (done + n > total) n = total - done;

        ysfx_process_float(fx, ins, outs, 2, 2, n);

        // A hand-moved control lands after the engine is running, never during
        // the load. Each --stage group lands one block after the last, which
        // NESTED SELECTORS require: set the selector, let @slider run, THEN set
        // that target's values, exactly as a person does it. Both at once writes
        // the values to the PREVIOUSLY selected target.
        if (stage_i < stages.size()) {
            for (const Assign &a : stages[stage_i]) ysfx_slider_set_value(fx, a.idx, a.val);
            stage_i++;
        }

        for (uint32_t k = 0; k < n; ++k) {
            double l = outL[k], r = outR[k];
            if (cf) std::fprintf(cf, "%u,%.9g,%.9g,%.9g\n", done + k, (done + k) / sr, l, r);
            accL += l * l; accR += r * r;
            if (std::fabs(l) > pkL) pkL = std::fabs(l);
            if (std::fabs(r) > pkR) pkR = std::fabs(r);
            if (++inwin >= win) {
                if (!quiet)
                    std::printf("  %8.3f  %10.6f  %10.6f  %9.6f  %9.6f\n",
                                (done + k + 1) / sr,
                                std::sqrt(accL / inwin), std::sqrt(accR / inwin), pkL, pkR);
                accL = accR = pkL = pkR = 0; inwin = 0;
            }
        }
        done += n;
    }

    if (cf) std::fclose(cf);
    ysfx_free(fx);
    ysfx_config_free(cfg);
    return 0;
}
