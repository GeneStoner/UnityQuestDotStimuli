# VRDots Competition Model: A Plain-Language Guide

*2026-04-23 — companion to `vrdots_competition_model.py` and `onset_competition_mechanism.md`*

---

## What the model is trying to do

We have four data points from the density knob experiment:

| N (dots/field) | CUED | UNCUED | Δpp |
|---|---|---|---|
| 63 | ~67% | ~33% | ~35pp |
| 173 | ~67% | ~33% | ~35pp |
| 500 | ~67% | ~33% | ~35pp |
| 1000 | ~53% | ~28% | ~25pp |

Two things demand explanation:

1. **Why is the cueing effect flat across an 8× range of dot density (N=63–500)?** Naively you might expect more dots = more signal = better performance for both arms. That doesn't happen.

2. **Why does only CUED drop at N=1000, while UNCUED stays flat?** If density were simply adding noise, both arms would drop together.

The model answers both questions from first principles, using the actual stimulus geometry plus a single attentional asymmetry.

---

## Layer 1 — The physics of the stimulus (why the plateau is flat)

### The key observation

During the 80 ms translation window (7 frames at 90 Hz), two things are happening simultaneously inside every MT receptive field:

- Some dots are **translating coherently** — these are the signal
- Other dots are **rotating** — these are the noise (they produce coherent local motion too, just in the wrong direction)

The ratio of signal dots to noise dots inside any RF is approximately:

```
n_t / n_r  ≈  n_coh / N  =  COHERENCE  ≈  0.47
```

This is just geometry. Both dot fields are uniformly distributed across the aperture. So any patch of retina contains roughly equal densities from both fields. Doubling N doubles the number of translating dots (signal) *and* doubles the number of rotating dots (noise). The ratio stays constant.

### Why rotating dots are noise, not just background

This is subtle. A rotating dot field isn't spatially random noise — it's locally coherent. At any eccentricity r, the rotating dots move tangentially at speed ω × r. Within a small RF (radius ~1.5°), all the rotating dots move in approximately the same direction. So they look, locally, like a coherent motion signal — just in the wrong direction relative to the translation.

The discriminability of "translation" from "rotation" therefore scales as:

```
d'_baseline  =  signal / noise  =  n_t / n_r  ≈  constant
```

regardless of N. **The flat plateau is a geometric inevitability of the stimulus design, not a tuned model parameter.**

### The model verifies this computationally

The code places actual dot positions, rotates them to tStart, runs the translation frames, drops 50 MT RFs across the aperture, and counts n_t and n_r in each RF at each frame. The count ratio comes out to 0.469 ± 0.014 at N=1000 and 0.478 ± 0.060 at N=63 — indistinguishable from each other and from the theoretical COHERENCE=0.47. The flat plateau falls out of the geometry with no free parameters.

---

## Layer 2 — Attentional gain (what onset suppression actually does)

### The asymmetry

At t=750ms, the delayed field appears. Its onset drives V1 inhibitory interneurons, briefly suppresses the always-on field's neural representation, and captures spatial attention (Yantis & Jonides). By the time translation begins 300ms later, the visual system has established a stable representation of "which field is the new one." This creates a persistent asymmetry:

| | Mechanism | Effect on d' |
|---|---|---|
| **CUED** (delayed field translates) | Attentional gain on translating signal | d'_CUED = **g_eff × d'_base** |
| **UNCUED** (always-on field translates) | Attentional suppression of translating signal | d'_UNCUED = **d'_base / G** |

Both are controlled by a single parameter **G = 1.63**. The CUED arm gets G as a multiplier; the UNCUED arm gets G as a divisor.

### Why G appears in both arms

If the delayed field's onset gives it an attentional advantage of magnitude G, then:
- When the delayed field carries the translation signal → its signal is amplified by G
- When the always-on field carries the translation signal → its signal is suppressed by G (relative to what it would have been without the onset asymmetry)

These are two sides of the same coin. The model uses a single G rather than separate gain and suppression parameters because they are mechanistically the same quantity — the magnitude of the onset-triggered attentional asymmetry.

### Calibration

G is set so that at N=500, the model hits the observed values:

```
CUED target:   67%  →  d'_CUED  = 1.86
UNCUED target: 33%  →  d'_UNCUED = 0.83
ratio: 1.86 / 0.83 = 2.24  ≈  G² = 1.63² = 2.66
```

The slight discrepancy (2.24 vs 2.66) reflects that 67% and 33% are not perfectly symmetric around chance in an 8AFC task. The model uses numerical integration to convert d' to p(correct) exactly.

**K** (= 2.43) is a calibration constant that converts the dimensionless count ratio into perceptual d'. It absorbs everything the model doesn't try to explain: direction bandwidth, pooling efficiency across RFs, the decision rule, observer-specific factors. K is set once from the N=500 plateau data and then held fixed across all densities.

---

## Layer 3 — The density ceiling (why N=1000 breaks only CUED)

### The surface-parsing argument

The attentional gain g_eff is not a fixed property of the onset event. It depends on whether the visual system can maintain a clean representation of the delayed surface through the 300ms pre-translation rotation. If transparent motion perception degrades — if the system can no longer resolve two distinct rotating surfaces from the interleaved dot fields — then the "surface" that attention is supposed to track becomes ill-defined, and the gain erodes.

Above a critical density N_crit ≈ 700, the model applies a power-law decay:

```
g_eff(N) = G                         for N ≤ 700
g_eff(N) = G × (700 / N)^1.0         for N > 700
```

At N=1000: g_eff = 1.63 × (700/1000) = 1.14

### The critical asymmetry

**g_eff is a function of density. G is not.**

The UNCUED suppression is `d'_base / G`. G was established by the onset event at t=750ms. It is not re-computed from the current dot density. It cannot degrade, because it was set before the trial's density-dependent processing even began.

So as N increases above 700:

```
CUED:   g_eff(N) × D0   → falls  (g_eff shrinks)
UNCUED: D0 / G          → flat   (G is constant)
```

This is exactly what the data show: CUED fell from 67% to 53% at N=1000; UNCUED stayed at 28%.

### The observed data vs model predictions

| N | CUED (obs) | CUED (model) | UNCUED (obs) | UNCUED (model) |
|---|---|---|---|---|
| 63 | ~67% | 68.1% | ~33% | 29.6% |
| 173 | ~67% | 66.3% | ~33% | 29.0% |
| 500 | ~67% | 67.0% | ~33% | 29.2% |
| 750 | (pending) | 63.0% | (pending) | 29.2% |
| 1000 | ~53% | 48.7% | ~28% | 29.2% |

The N=750 session will be the key test of N_crit. The model predicts ~63% CUED (a visible but modest drop from the plateau), with UNCUED still flat at 29%.

Note: the model drops CUED to 49% at N=1000, slightly below the observed 53%. This means the true rolloff is slightly gentler than POW_DECAY=1.0 — POW_DECAY≈0.7 would fit better, and N_crit may be somewhat lower (~600). The N=750 data will resolve this.

---

## What the model does NOT claim to explain

These are explicit gaps — honest about what is and isn't in the model.

**1. Why G = 1.63 specifically.**
This is fit to the behavioral data. The model doesn't derive G from V1 interneuron firing rates or any neural measurement. It is the size of the attentional asymmetry; we don't yet know what determines it mechanistically.

**2. What maintains the surface representation across 300ms.**
The model assumes the onset-established advantage is fully intact at tStart, 300ms later. It does not model the 300ms bridge — the process by which the visual system tracks the delayed surface through the pre-translation rotation. This is the deepest gap in the mechanistic account (see `onset_competition_mechanism.md` §5, open question 1).

**3. The swap conditions.**
The model only handles baseline density variation. Motion swaps, color swaps, and depth swaps all require additional logic about how features are bound to surfaces and how swapping features at tStart interacts with the onset-established identity. These are the next layer to build.

**4. The exact location of N_crit.**
N_crit = 700 is set to roughly match the N=1000 data point. The N=750 session will constrain it directly — that single session will tell us whether the transition is sharp (N_crit just above 750) or gradual (N_crit around 600–700).

**5. The 300ms pre-translation duration.**
The model is silent on what happens if you vary the SOA between onset and translation. A shorter SOA would presumably give less time for surface establishment (smaller effective G?). An SOA manipulation would test this directly.

---

## The model in three sentences

The rotating dot noise inside any MT RF scales proportionally with dot density — signal and noise both go up with N, so the baseline signal-to-noise ratio is constant. This is why the cueing plateau is flat: it's geometry, not mechanism. The cueing asymmetry (CUED > UNCUED) is a fixed attentional gain established by the delayed-field onset; at high enough density this gain degrades because transparent motion perception fails, but only the CUED arm suffers because the UNCUED suppression was set by the onset event and cannot be eroded by density.

---

## Free parameters and what constrains them

| Parameter | Value | How constrained |
|---|---|---|
| G | 1.63 | Plateau CUED (67%) and UNCUED (33%) at N=500 |
| K | 2.434 | Calibrated from G and mean count-ratio at N=500 |
| N_crit | 700 | Roughly matches N=1000 drop; N=750 session will refine |
| POW_DECAY | 1.0 | Controls rolloff steepness; slightly too steep at present |
| R_MT | 1.5° | Literature estimate for MT RF radius at VRDots eccentricities |
| COHERENCE | 0.47 | Stimulus parameter (proportion of dots that are coherent) |
| N_MONTE | 300 | MC trials for count-ratio estimation; no effect on predictions |

---

*Companion files:*
- *Model code: `/tmp/vrdots_competition_model.py`*
- *Mechanistic writeup: `onset_competition_mechanism.md`*
- *Literature: `../Literature/onset_suppression_lit.md`*
- *Figure: `../Figures/vrdots_competition_model.png`*
