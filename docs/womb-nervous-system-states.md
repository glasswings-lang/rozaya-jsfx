# Nervous-system states: physiology reference for a heartbeat/breath instrument

Research grounding for a sound-design project that depicts three nervous-system states as a journey. The mapping target is a heartbeat/breath synthesizer, so every state below is described in **concrete cardiac and respiratory numbers** a sound designer can dial in: heart rate, HRV level and *quality*, respiratory sinus arrhythmia (RSA) amplitude, breathing rate/depth, and coherence character.

Numbers flagged **~** are rough ranges or population averages — individuals vary widely, and several of these figures come from group means in meta-analyses, not hard thresholds. Treat them as design anchors, not clinical facts.

## The three-state framework and the coherence spine

The organizing frame is **polyvagal theory** (Stephen Porges): the autonomic nervous system is not a simple on/off "sympathetic vs parasympathetic" dial but three phylogenetically layered circuits that the body moves *between* as a hierarchy of responses to safety and threat ([Polyvagal Institute](https://www.polyvagalinstitute.org/whatispolyvagaltheory); [Porges review, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3108032/)):

1. **Ventral vagal** (myelinated vagus, nucleus ambiguus) — safety, social engagement, calm. Home base. Runs the "vagal brake."
2. **Sympathetic** — mobilization: fight/flight, hyperarousal.
3. **Dorsal vagal** (unmyelinated vagus, dorsal motor nucleus) — immobilization: shutdown, collapse, freeze.

The **spine of the project** is a second, orthogonal contrast that overlays the state journey: **coherent vs incoherent heart-rhythm patterns** (HeartMath). The key physiological insight is that coherence is *not about the amount of HRV* — a chaotic stressed heart and a calm coherent heart can have the same total variability. What changes is the **pattern**: coherence is a smooth, ordered, sine-wave-like oscillation at ~0.1 Hz; incoherence is a jagged, erratic, disordered waveform ([HeartMath, Science of the Heart — Coherence](https://www.heartmath.org/research/science-of-the-heart/coherence/)).

So the three states below can be read as a journey **from incoherence into coherence, then settling** — from a jagged dysregulated rhythm, through an actively-generated smooth 0.1 Hz coherent rhythm, to a restful high-HRV parasympathetic calm.

---

## State 1 — Dysregulated / traumatised

Sympathetic hyperarousal *or* dorsal-vagal freeze. These are two different autonomic states with **opposite cardiac signatures**, but both are "dysregulated" and both read as incoherent. Decide which one the sound is depicting — or move between them.

**Chronic trauma / PTSD baseline (sympathetic-dominant hyperarousal):**

- **Heart rate:** elevated resting HR. Meta-analyses find PTSD groups have significantly *higher* resting heart rate than controls ([Psychiatry Investigation meta-analysis](https://www.psychiatryinvestigation.org/journal/view.php?number=1117); [Cambridge/Psych Medicine meta-analysis, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7525781/)). A resting HR of **~75–90+ bpm** is a reasonable "activated baseline" anchor (normal calm resting adult is ~60–75).
- **HRV level — low.** PTSD is associated with reduced resting HRV. Meta-analytic mean differences vs healthy controls: **RMSSD ~ −8.5 ms**, **SDNN ~ −9.9 ms**, and a large drop in high-frequency (parasympathetic) HRV ([PLOS One traumatic-injury meta-analysis](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280718); [Psych Medicine meta-analysis, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7525781/)). For context, healthy short-term RMSSD is ~**27–72 ms** ([Kubios](https://www.kubios.com/blog/heart-rate-variability-normal-range/); [HRV metrics overview, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5624990/)); dysregulated sits at the low end or below.
- **HRV quality — erratic / incoherent.** Low *and* disordered: jagged, chaotic rhythm, no clean 0.1 Hz peak. This is the HeartMath "incoherence" pattern, associated with anger, anxiety, frustration ([HeartMath Coherence](https://www.heartmath.org/research/science-of-the-heart/coherence/)).
- **RSA amplitude — small.** Reduced parasympathetic/vagal tone means the breath-linked speed-up/slow-down of the heart is compressed. Low RSA = low vagal tone marker (see Key Mechanisms).
- **Breathing — fast, shallow, irregular.** Rapid upper-chest breathing; rate well above the calm ~12–16/min, often 18–25+/min, with an unstable, non-periodic rhythm. Sighs and breath-holds break any regularity.
- **Coherence character:** **incoherent** — jagged, unstable, no dominant slow rhythm.

**Dorsal-vagal freeze / shutdown / tonic immobility (the opposite pole):**

- **Heart rate:** the unmyelinated dorsal vagus can *dramatically drop* cardiac output — **bradycardia**, heart rate falling toward or below baseline; in extreme immobilization/faint, sharply slowed ([Porges review, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3108032/); [Tonic Immobility overview, ScienceDirect](https://www.sciencedirect.com/topics/neuroscience/tonic-immobility)). Model this as a HR that **sinks and flattens** rather than races.
- **HRV — low and flat.** Collapse, not activation. Little variability, muted RSA, a numb/deadened rhythm.
- **Breathing — slow, shallow, faint.** Reduced respiration rate and depth, sometimes near-suspended.
- **Coherence character:** flat/dead rather than jagged — low energy, low variability, no organizing rhythm.

> Design note: a "fear-potentiated freeze" (attentive immobility, still sympathetically charged — held-breath, braced, high HR but motionless) is distinct again from dorsal-vagal *shutdown* (collapsed, bradycardic, limp). Freeze feels like trapped energy; shutdown like collapse with no energy ([defense cascade / tonic immobility, ScienceDirect](https://www.sciencedirect.com/topics/neuroscience/tonic-immobility)). Two different HR gestures if the piece needs both.

---

## State 2 — Activated coherence

The HeartMath **coherence** state and Lehrer/Vaschillo's **resonance-frequency breathing** are, physiologically, the same phenomenon: a deliberately generated, high-amplitude, smooth ~0.1 Hz oscillation of heart rate. This is an *active, engaged* calm — not resting, but entrained and efficient.

- **Heart rate:** moderate and steady (no elevation); the story is in the *oscillation around* the mean, not the mean itself.
- **The signature HRV pattern:** a **smooth, sine-wave-like heart-rhythm oscillation at ~0.1 Hz** — one full cycle every **~10 seconds** ([HeartMath Coherence](https://www.heartmath.org/research/science-of-the-heart/coherence/); [resonance breathing guide, Frontiers](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.570400/full)). In the frequency domain this is a single narrow, tall peak in the low-frequency band. This is the visual/sonic centerpiece of the coherent state.
- **RSA amplitude — large and smooth.** At resonance, heart-rate oscillations amplify **~4–10×** over resting baseline (measured as the difference between the fastest and slowest HR within each breath) ([Frontiers resonance guide](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.570400/full); [Lehrer/Vaschillo HRV biofeedback](https://ohm.health/blog/resonance-breathing-101)). This is a *big*, clean, breath-locked swing in HR — the heart audibly speeding and slowing with the breath.
- **Resonance breathing rate:** slow paced breathing at **~4.5–6.5 breaths/min** for adults, assessed in 0.5-bpm steps; **~6 breaths/min = 0.1 Hz** is the canonical center ([Frontiers resonance guide](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.570400/full)). Each person has an individual resonance frequency within that band (set by blood volume / baroreflex loop delay), but ~5.5–6/min is the safe generic anchor. (Children's band is higher, ~6.5–9.5/min.)
- **Inhale:exhale ratio:** commonly taught around **1:1** (e.g. 5 s in / 5 s out at 6/min) for maximizing RSA amplitude; a slightly longer exhale (e.g. 4 s in / 6 s out) tilts further parasympathetic (see extended-exhale mechanism below). Either works for coherence; equal or exhale-weighted.
- **Coherence character:** **maximally coherent** — the cleanest, tallest, most regular 0.1 Hz sine of the three states. Respiration, heart rhythm, and baroreflex are entrained and phase-locked.

> Why ~6/min specifically: it hits the **resonance frequency of the baroreflex** — the natural ~10-second delay in the blood-pressure feedback loop. Breathing at that rate drives HR and blood-pressure oscillations exactly in phase, so they reinforce like pushing a swing at its natural period. See Key Mechanisms.

---

## State 3 — Resting coherence

Ventral-vagal / parasympathetic rest — restful-alert, safe, settled. **Not** dorsal-vagal shutdown (State 1's second pole): this is high vagal *tone* with the system online, not collapsed. The difference from State 2 is that this is passive settling rather than an actively driven 0.1 Hz resonance — HRV is high and calm, breathing is naturally slow, the vagal brake is engaged.

- **Heart rate:** low resting HR, **~50–70 bpm** for a healthy calm adult (lower in fit individuals). A strong vagal brake holds HR down below its intrinsic pacemaker rate.
- **HRV — high and calm.** Robust parasympathetic tone: RMSSD toward the upper end of normal (**~50–70+ ms**, higher in the young/fit) ([Kubios normal ranges](https://www.kubios.com/blog/heart-rate-variability-normal-range/); [HRV overview, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5624990/)). Smooth and organized, not jagged — but a gentler, more naturally-arising variability than the driven resonance peak of State 2.
- **RSA amplitude — healthy and evident.** Clear breath-linked HR modulation. Typical resting peak-to-trough swing averages **~8–14 bpm** (range can span <5 to >30) ([RSA / vagal tone, relaxmore](https://www.relaxmore.net/p/rsa-english)). Larger RSA = stronger, more flexible vagal tone.
- **Breathing — slow, deep, smooth, unforced.** Naturally slow relaxed rate, roughly **~8–12 breaths/min**, diaphragmatic, with a relaxed and often **slightly extended exhale**. Not paced or effortful.
- **Vagal-brake / extended-exhale effect:** the exhale-dominant, unhurried breath keeps the parasympathetic vagal brake engaged, so HR drifts down and stays low. Each exhale nudges the heart slower (see Key Mechanisms).
- **Coherence character:** **coherent and calm** — organized and smooth, but lower-amplitude and less metronomic than the actively-driven State 2 resonance. Settled rather than entrained.

---

## Key mechanisms

### Coherence vs chaos (the spine)

- A **coherent** heart rhythm is "a relatively harmonic, sine-wave-like signal with a very narrow, high-amplitude peak in the low-frequency region" at ~0.1 Hz (10-second cycles) ([HeartMath Coherence](https://www.heartmath.org/research/science-of-the-heart/coherence/)).
- An **incoherent** rhythm is erratic, jagged, disordered — many frequencies, no dominant slow peak.
- Critically: **the total amount of HRV can be identical in both** — "state-specific emotions are reflected in the *patterns* of the heart's rhythms independent of changes in the amount of heart rate variability" ([HeartMath Coherence](https://www.heartmath.org/research/science-of-the-heart/coherence/)). Coherence is *order*, not *magnitude*. For the sound design this means the coherent-vs-incoherent contrast should live in the **smoothness/regularity of the modulation**, not just its depth.
- Coherent states track positive emotion (appreciation, calm); incoherent states track anger, frustration, anxiety.

### Respiratory sinus arrhythmia (RSA)

- **Heart speeds up on inhale, slows down on exhale**, every breath ([RSA overview, ScienceDirect](https://www.sciencedirect.com/topics/medicine-and-dentistry/respiratory-sinus-arrhythmia); [relaxmore RSA](https://www.relaxmore.net/p/rsa-english)).
- Mechanism: on **exhale**, neurons in the nucleus ambiguus fire strongest, applying the **vagal brake** → HR slows. On **inhale**, the brake eases ("inspiratory gating") → HR rises ([brainstem sources of cardiac vagal tone, PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5157093/)).
- **RSA amplitude is a vagal-tone marker:** the beat-to-beat swing between fastest (inhale) and slowest (exhale) HR indexes the strength/flexibility of vagal regulation. Larger amplitude = more flexible, "fitter" vagal tone; typical resting swing averages ~8–14 bpm ([relaxmore RSA](https://www.relaxmore.net/p/rsa-english)). This is the single most sound-mappable number: **RSA amplitude = how much the heartbeat rate visibly breathes**.

### Resonance-frequency breathing (Lehrer / Vaschillo)

- Breathing at **~0.1 Hz (~6 breaths/min)** hits the **resonance frequency of the cardiovascular system**, set by the **baroreflex** (blood-pressure feedback) loop, which has a natural delay of ~5 s each way ≈ a 10-second cycle ([Frontiers resonance guide](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.570400/full)).
- At this rate, respiration-driven and baroreflex-driven HR oscillations line up **in phase** and reinforce — like pushing a swing at its natural period — producing the largest possible HRV/RSA amplitude, **~4–10× resting baseline** ([Frontiers resonance guide](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.570400/full); [Ohm resonance breathing 101](https://ohm.health/blog/resonance-breathing-101)).
- Individual resonance frequency varies within **4.5–6.5/min** (blood volume determines the loop delay), which is why clinical protocols sweep the rate to find each person's peak.

### The extended exhale / vagal brake

- A **prolonged exhale relative to inhale** shifts sympathovagal balance toward parasympathetic ([prolonged-expiration relaxation, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6037091/); [extending-exhale for stress, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10395759/)).
- Mechanism: during **inhalation** vagal outflow is inhibited (sympathetic-favoring); during **exhalation** vagal flow is restored (parasympathetic). Exhale also raises cardiac output momentarily → baroreceptors sense the pressure rise → baroreflex *further* boosts vagal activity → HR slows ([prolonged-expiration, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6037091/)).
- Net: **the longer you spend exhaling, the longer the vagal brake holds the heart slow.** This is the physiological basis for "breathe out longer than you breathe in" as a down-regulation tool, and the reason State 3's slightly-extended exhale settles HR.

### The vagal brake (ventral vagal)

- The myelinated ventral vagus continuously restrains the heart's intrinsic pacemaker, holding resting HR *below* its natural rate. Rapidly releasing and re-applying this brake is how a safe, regulated nervous system flexibly modulates cardiac output without needing sympathetic activation ([Polyvagal Institute](https://www.polyvagalinstitute.org/whatispolyvagaltheory); [Porges review, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3108032/)). RSA is essentially this brake pulsing with the breath. Strong vagal brake = low resting HR + high RSA = State 3.

---

## Quick mapping table (design anchors)

| | HR (bpm) | HRV level | HRV quality | RSA amplitude | Breathing | Coherence |
|---|---|---|---|---|---|---|
| **1. Dysregulated — sympathetic** | ~75–90+ | low | jagged, erratic | small | fast ~18–25+/min, shallow, irregular | incoherent (jagged) |
| **1. Dysregulated — dorsal freeze** | dropping / bradycardic | low | flat, dead | muted | slow, shallow, faint | flat / dead |
| **2. Activated coherence** | steady, moderate | driven-high | smooth 0.1 Hz sine | **large (4–10×)** | paced ~5.5–6/min, ~1:1 or exhale-long | **maximally coherent** |
| **3. Resting coherence** | ~50–70 | high, calm | smooth, gentle | evident ~8–14 bpm swing | slow ~8–12/min, deep, exhale-weighted | coherent, settled |

All figures are approximate design anchors — see per-state notes for the sourced ranges and caveats.

---

## Sources

- [Polyvagal Institute — What is Polyvagal Theory?](https://www.polyvagalinstitute.org/whatispolyvagaltheory)
- [Porges — The polyvagal theory: new insights into adaptive reactions of the autonomic nervous system (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3108032/)
- [HeartMath Institute — Science of the Heart: Coherence](https://www.heartmath.org/research/science-of-the-heart/coherence/)
- [Frontiers in Neuroscience — A Practical Guide to Resonance Frequency Assessment for HRV Biofeedback (Lehrer et al.)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.570400/full)
- [Ohm Health — Resonance Breathing 101 (Lehrer/Vaschillo/Gevirtz background)](https://ohm.health/blog/resonance-breathing-101)
- [Psychiatry Investigation — PTSD and Alterations in Resting HRV: Systematic Review and Meta-Analysis](https://www.psychiatryinvestigation.org/journal/view.php?number=1117)
- [Psychological Medicine (Cambridge) — Autonomic dysfunction in PTSD indexed by HRV: a meta-analysis (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7525781/)
- [PLOS One — Non-acute traumatic injury and HRV: systematic review and meta-analysis](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280718)
- [Kubios — HRV normal ranges](https://www.kubios.com/blog/heart-rate-variability-normal-range/)
- [Shaffer & Ginsberg — An Overview of Heart Rate Variability Metrics and Norms (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5624990/)
- [RSA / vagal tone overview (relaxmore, de Caluwé)](https://www.relaxmore.net/p/rsa-english)
- [Respiratory Sinus Arrhythmia — overview (ScienceDirect)](https://www.sciencedirect.com/topics/medicine-and-dentistry/respiratory-sinus-arrhythmia)
- [Brainstem sources of cardiac vagal tone and RSA (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5157093/)
- [The relaxation effect of prolonged expiratory breathing (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6037091/)
- [Slow breathing for reducing stress: the effect of extending exhale (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10395759/)
- [Tonic Immobility / defense cascade — overview (ScienceDirect)](https://www.sciencedirect.com/topics/neuroscience/tonic-immobility)
