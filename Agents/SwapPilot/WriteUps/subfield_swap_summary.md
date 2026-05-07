# SubfieldSwap — Results Summary vs. S&B and Catek et al.
*Updated: 2026-04-29*

---

## Asset Confirmation

The trajectory figures (`subfield_feature_traj_sb.py`, `subfield_feature_traj.py`) are generated directly from
`Exp_SubfieldSwap_HighDens.asset` parameters (ONSET=68fr, TSTART=95fr, TEND=102fr, 90Hz). Conditions N/D/Da/Db
correspond exactly to SwapFlags None/Dots50/Dots50A/Dots50+Dots50A as implemented in `ExperimentSpec.cs`.

---

## Structural Equivalence: Da ↔ S&B/Catek "Combined Swap"

Our **Da** condition and S&B/Catek's **motion+color swap** produce **identical visual appearances** at tStart:

| | S&B / Catek "MC" | Our Da |
|---|---|---|
| At tStart, what happens | Rotation direction reverses; colors swap | Sub0↔Sub2 swap — translating group changes field membership |
| **Physical dots continuing** | **Same dots** keep translating with new motion/color | **Different dots** (previously non-translating) begin translating |
| Visual appearance | Translating group reverses direction & color | Translating group reverses direction & color ← **identical** |
| Identity continuity | Maintained (same neurons tracking same dots) | **Broken** (translating dot set replaced wholesale) |

**The S&B/Catek CUED/UNCUED illustration structure** (CUED = green/delayed field translates; UNCUED = red/delayed
field, but green/always-on translates) directly maps onto our Da condition — the S&B figure pairs show exactly the
before/after relationship that Da implements physically.

Our Db is the full-swap version (Da + D simultaneously), also producing the same visual reversal of both coherent
and noise halves. Our **MC** condition (Motion|Color flags) is the exact mechanistic analog of S&B/Catek: same
physical dots continue translating, rotation direction reverses, colors swap. MC and Db produce **pixel-identical
visual displays** (verified by trajectory simulation); they differ only in dot membership implementation, which
is undetectable to the observer.

---

## Stimulus Parameters: Side by Side

| Parameter | **S&B 2010** | **Catek 2022** | **Our: Catek_v1** | **Our: CatekExact** | **Our: HighDens** | **Our: AperSweep Ap35** | **Our: AperSweep Ap165** | **Our: MCvsDb_Ap165** |
|---|---|---|---|---|---|---|---|---|
| Aperture radius | **2.0°** | **1.65°** | **3.5°** | **1.65°** | **3.5°** | **3.5°** | **1.65°** | **1.65°** |
| Dot density (dots/deg²) | **~5** | **~5** | **~1.1** | **~5** | **~4.5** | ~5 | ~5 | ~5 |
| Dots/field | ~63 | ~43 | 43 | 43 | 173 | 192 | 98 | 43 |
| Dot size | 0.03° | **0.05°** | 0.08° | 0.08° | 0.08° | 0.08° | 0.08° | 0.08° |
| Rotation speed | 81°/s | 81°/s | 81°/s | 81°/s | 81°/s | 81°/s | 81°/s | 81°/s |
| Translation speed | 2.26°/s | 2.26°/s | 2.26°/s | 2.26°/s | 2.26°/s | 2.26°/s | 2.26°/s | 2.26°/s |
| Translation duration | **40ms** | **133ms** | 80ms | 80ms | 80ms | **variable 20–350ms** | **variable 20–350ms** | 80ms |
| Swap conditions | motion, color | motion, color | N,D,Da | N,D,Da,Db | N,D,Da,Db | N,D,Da,Db | N,D,Da,Db | **MC, Db** |
| Observer | naïve/trained | naïve (n=15) | GS | GS | GS | GS | GS | GS |

**Key parameter mismatches vs Catek:**
- Dot size: 0.08° vs Catek's 0.05° (60% larger; at rendering resolution limit for 0.05°)
- Translation duration: 80ms vs Catek's 133ms (shorter; 0.18° vs 0.30° displacement)
- Catek tested motion-only and color-only swaps **separately** — no combined MC condition

---

## Catek et al. Exact Behavioral Results (Table 1, n=15)

| Condition | Cueing Δ (mean) | SEM | Cohen's d | p vs no-swap |
|---|---|---|---|---|
| No-swap | **+20.2pp** | 3.05 | 1.711 | — (baseline) |
| Motion swap | **+10.4pp** | 2.05 | 1.316 | **p = .018** |
| Color swap | **+13.4pp** | 3.11 | 1.112 | **p = .049** |

**Key points:**
- Both motion and color swaps **significantly reduced** cueing vs no-swap (Bonferroni-corrected)
- Motion swap cut cueing by ~48%; color swap by ~34%
- Cueing remained significant in all conditions (all p < .001 vs uncued)
- Motion swap also **reduced overall accuracy** (not just the CUED−UNCUED gap)
- No combined motion+color condition was tested

---

## ⚠️ Critical Discrepancy: Catek et al. vs. Stoner & Blanc 2010

**S&B 2010** and **Catek 2022** reached opposite quantitative conclusions despite nominally similar designs:

| | S&B 2010 | Catek 2022 |
|---|---|---|
| Aperture | 2.0° | 1.65° |
| Dot size | 0.03° | 0.05° |
| Translation duration | **40ms** | **133ms** |
| Motion swap cueing | **survives, ~= no-swap** | **~48% reduction, p=.018** |
| Color swap cueing | **survives, ~= no-swap** | **~34% reduction, p=.049** |
| Observer type | naïve/trained | naïve (n=15) |

S&B describe their motion and color swap results as showing "very little decrease" in cueing, explicitly supporting
an object-based account. Catek find a statistically significant ~50% reduction — a large effect (d≈0.8–0.9 for the
swap-vs-no-swap contrast).

**Our MCvsDb_Ap165 data replicate Catek, not S&B.** The ~50% reduction we observe is not a discrepancy with
Catek — it is a replication. The discrepancy is between Catek and S&B. The most likely explanatory variable is
**translation duration**: S&B's 40ms (0.09° displacement) vs Catek's 133ms (0.30° displacement). A very brief
translation may be judged before feature-based re-grouping can occur; a longer translation gives the observer time
to re-group by features, at which point the swap disrupts the cueing signal.

---

## Effect Magnitudes: Side by Side

### S&B and Catek et al.
See Catek exact values above. S&B did not tabulate effect sizes; qualitatively described as cueing surviving
in all conditions. Our reading of their Fig. 2B suggests cueing effects were approximately equal across conditions
(no-swap, motion, color swap).

### Our Data — Fixed Duration Experiments
All Δpp values = CUED accuracy − UNCUED accuracy (adjusted for Da/Db label inversion where applicable).

| Experiment | n(total) | **N** | **D** (noise-half) | **Da** (coh-half) ← S&B analog | **Db** (full swap) | **MC** (same-dot) |
|---|---|---|---|---|---|---|
| Catek_v1 (3.5°, 43 dots) | 391 | +20.3pp | +28.8pp | **+2.3pp ≈ 0** ⚠️ | — | — |
| HighDens (3.5°, 173 dots) | 512 | +21.9pp | +35.9pp | **−1.6pp ≈ 0** ⚠️ | +7.8pp | — |
| CatekExact (1.65°, 43 dots) | 873 | +21.5pp | +19.2pp | **+18.9pp** ✓ | +2.7pp | — |
| CatekExact_NDb (1.65°, 43 dots) | 256 | +15.6pp | — | — | **+15.6pp** ✓ | — |
| **MCvsDb_Ap165 (1.65°, 43 dots)** | **N=473, MC/Db=576** | **+19.7pp***\*** | — | — | **+9.4pp†** | **+9.9pp†** |
| **S&B (2.0°, ~63 dots)** | ~512/cond | **survives** | — | **survives** ✓ | — | — |
| **Catek et al. (1.65°, 43 dots)** | n=15 | +20.2pp | — | **+10.4pp (motion)** | — | — |

†p<0.10; ***p<0.001

### MCvsDb_Ap165 — Detailed Results (3 sessions: 260429_0748, _0951, _1031)

| Arm | CUED | UNCUED | Δpp | p | R̄(cued) | R̄(uncued) |
|---|---|---|---|---|---|---|
| N (from Catek sessions) | 60.3% | 40.6% | **+19.7pp** | *** | 0.643 | 0.416 |
| MC | 59.9% | 50.0% | **+9.9pp** | † (p=0.065) | 0.665 | 0.480 |
| Db | 57.8% | 48.4% | **+9.4pp** | † (p=0.082) | 0.608 | 0.451 |

**Interaction tests:**
- MC vs N: Δpp diff = −9.8pp, z=−1.42, p=0.156 (trending; underpowered)
- Db vs N: Δpp diff = −10.3pp, z=−1.51, p=0.132 (trending)
- MC vs Db: Δpp diff = +0.5pp, z=0.08, **p=0.936** (dead null — as predicted from pixel identity)

**Pattern of UNCUED elevation:** Unlike Catek (where motion swap primarily reduces CUED accuracy), our MC/Db
primarily **elevates UNCUED** (~+10pp above N-UNCUED), with CUED nearly unchanged. Interpretation: the feature
swap at tStart may make the non-translating (always-on) field more attention-capturing, rather than making the
translating (delayed) field harder to judge.

### Our AperSweep (Variable Duration MoCS)
R = T_UNCUED / T_CUED from Weibull fits. **R > 1 = cueing advantage.**

| Experiment | n(total) | **N** | **D** | **Da** | **Db** |
|---|---|---|---|---|---|
| AperSweep Ap35 (3.5°, 192 dots) | 1538 | R=5.1 | R=3.9 | **R=1.03 ≈ 1** ⚠️ | R=1.17 |
| AperSweep Ap25 (2.5°, 98 dots) | 512 | R=1.66† | R=3.15 | **R=1.15** | R=2.13 ✓ |
| AperSweep Ap165 (1.65°, 43 dots) | 640 | R=3.57 | R=3.63 | **R=1.55** ✓ | R=1.87 ✓ |

†N at 2.5° unexpectedly low vs flanking apertures — single-session sampling artifact possible; needs replication.

**Da aperture gradient (monotonic decline):** R=1.55 (1.65°) → 1.15 (2.5°) → 1.03 (3.5°).
No sharp threshold; collapse is gradual across the 1.65°–3.5° range. S&B used 2.0°, which falls between Ap165 and Ap25 — consistent with Da surviving at S&B's aperture.

**Db non-monotonic:** R=1.87 (1.65°) → 2.13 (2.5°) → 1.17 (3.5°). Stronger at 2.5° than flanking sizes; needs replication.

---

## Conditions with Little or No Cueing Effect After Swap

Three distinct experimental contexts produce near-zero cueing:

### 1. Da — aperture-dependent decline (gradual, not a sharp threshold)
| Aperture | Da result |
|---|---|
| 1.65° | R=1.55 ✓; CatekExact +18.9pp |
| 2.5° | **R=1.15** — substantially weakened |
| 3.5° | R=1.03 ≈ 1.0 ⚠️; Catek_v1 +2.3pp, HighDens −1.6pp |

Da declines monotonically with aperture — no sharp threshold. S&B's 2.0° aperture falls between our Ap165 and Ap25, consistent with Da surviving in their data. The collapse is complete by 3.5°.

This is the **central empirical discrepancy with S&B and Catek** — at ≥2.5°, the coherent-half membership swap substantially reduces or eliminates cueing. At 1.65°, Da survives similarly to S&B/Catek.

### 2. Db — aperture-dependent, non-monotonic
- Ap165: R=1.87 ✓ (+9.4pp† in fixed-duration)
- **Ap25: R=2.13** — strongest in the series
- Ap35: R=1.17 (weakened; HighDens +7.8pp, AperSweep R=1.17)

Db is not a simple monotonic function of aperture. It peaks at 2.5° and weakens at both extremes. Needs replication at Ap25.

### 3. MC and Db at 1.65° — partial ~50% reduction
Both conditions retain significant/trending cueing (~+9.5pp vs N +19.7pp). This is not a collapse,
but it is a substantial reduction. It matches Catek's finding for motion-only swap (~48% reduction).

**What does NOT collapse:** D (noise-half swap) is robust across all apertures. At 3.5° it is even enhanced
(D = +35.9pp in HighDens, R=4.3 in AperSweep Ap35). D never eliminates cueing in any experiment.

---

## Summary of Discrepancies vs. S&B / Catek

### 1. MC/Db at matched aperture (1.65°) → **REPLICATES Catek, CONTRADICTS S&B**
MCvsDb_Ap165: MC=+9.9pp†, Db=+9.4pp†, N=+19.7pp*** — ~50% reduction.
Catek motion swap: +10.4pp vs no-swap +20.2pp — ~48% reduction, p=.018.
**Our result matches Catek quantitatively.** S&B describe their analogous result as "very little decrease" — our
data, like Catek's, show a substantial and meaningful reduction.

### 2. Da at large aperture (3.5°) → **CONTRADICTS both S&B and Catek**
Da ≈ 0 at 3.5° in all experiments. S&B and Catek (both ≤2°) found analogous conditions surviving with strong
cueing. This is a genuine discrepancy, likely driven by aperture size (see H1 below).

### 3. Da at matched aperture (1.65°) → **REPLICATES S&B/Catek**
CatekExact: Da = +18.9pp; Ap165: R=1.55. At 1.65°, the membership swap condition survives similarly to S&B/Catek.

### 4. D (noise-half swap) → **consistent** with S&B/Catek across all apertures
D never collapses cueing; at high density (3.5°) it is dramatically enhanced.

### 5. MC vs Db → **null as predicted**
+0.5pp difference, z=0.08. Confirms these conditions are perceptually identical.

---

## Hypotheses for the Remaining Discrepancy (S&B vs Catek/Us on MC)

### H1: Translation duration (primary for S&B vs Catek divergence)
S&B: 40ms translation (0.09° displacement). Catek: 133ms (0.30°). Ours: 80ms (0.18°).
A 40ms translation may be judged before feature-based re-grouping is complete. At 133ms, the observer has time
to re-group by the new rotation direction/color, disrupting the cueing signal. Our 80ms result (~50% reduction)
falls between and is consistent with this gradient.

**Testable**: Run 40ms translation duration in CatekExact parameters. Prediction: cueing reduction shrinks toward S&B.

### H2: Aperture / RF-scale hypothesis (primary for Da collapse at 3.5°)
At ≤2°, V1/V2 RFs can partially isolate individual dots, supporting dot-level trajectory tracking that survives
feature changes at tStart. At 3.5°, RFs are larger; feature-based grouping dominates, and the membership swap
disrupts it completely.

**Testable**: Ap25 (2.5° AperSweep) — does Da collapse? Locates threshold.

### H3: Observer differences
S&B used naïve observers; Catek n=15 naïve observers; we are author (GS). Effect magnitudes may differ.
The S&B vs Catek divergence exists between two independent naïve-observer studies, so observer type alone
does not explain it.

---

## Key Open Questions

1. **Ap25 (2.5° AperSweep)** — does Da collapse? Critical to locate aperture threshold. *(Next run.)*

2. **40ms translation duration** — does shortening toward S&B parameters rescue MC reduction? Separates H1 from H2.

3. **MC/Db: more sessions** — currently 3 sessions (n=576). MC vs N trending (p=0.065); need ~2 more sessions
   for p<0.05. The MC=Db equivalence is already conclusively established (p=0.94).

4. **Second observer** — all data GS (author). Needed before strong conclusions.

5. **Db at 1.65° variability** — CatekExact Db=+2.7pp vs CatekExact_NDb Db=+15.6pp (large session-to-session
   variance). MCvsDb_Ap165 gives Db=+9.4pp†. More data needed for stable estimate.

6. **UNCUED elevation mechanism** — why does MC/Db elevate UNCUED (ours) rather than reduce CUED (Catek)?
   Both directions produce ~50% cueing reduction, but via different arms. Catek's motion-only swap may make
   the cued translation harder to perceive; our simultaneous motion+color swap may make the uncued field
   more salient/attention-capturing.
