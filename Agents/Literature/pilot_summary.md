# DepthSwapCtrl Pilot — Summary, Analyses, and Tentative Interpretations
*Last updated: 2026-04-01*

---

## 1. What We Did

Single observer (GS), Meta Quest, binocular and monocular viewing. All sessions used `Exp_DepthSwapCtrl`: 192 trials, N/ZdA/ZdB × CUED/UNCUED × Near/Far × 2 rotations × 8 headings × 1 rep. Both fields red (same color), 0.05 m depth separation at 2.0 m, 3.5° aperture, 63 dots/field, 81°/s rotation, 2.26°/s translation, 80 ms translation burst (6 frames at 75 Hz), 750 ms delayed onset.

**10 sessions total:**
| Session | Eye | Overall | Notes |
|---------|-----|---------|-------|
| 260330_1853 | Binocular | 46.4% | Session 1 |
| 260330_2012 | R-eye (L closed) | 33.2% | Mono R #1; floaters |
| 260331_0621 | Binocular | 38.0% | Session 2; anomalous |
| 260331_1530 | R-eye (L closed) | 39.1% | Mono R #2 |
| 260331_1705 | L-eye (R closed) | 45.3% | Mono L #1 |
| 260331_1734 | L-eye (R closed) | 43.2% | Mono L #2 |
| 260401_1313 | Binocular | 51.0% | Session 3 |
| 260401_1349 | Binocular | 44.3% | Session 4 |
| 260401_1541 | R-eye (L closed) | 33.9% | Mono R #3 |
| 260401_1705 | L-eye (R closed) | 39.6% | Mono L #3 |

All sessions: 192/192 trials, 192/192 trajectories verified.

---

## 2. Three-Factor Analysis Framework

| Factor | Definition | Levels |
|--------|-----------|--------|
| 1. Dot cueing | Delayed-onset dots translate | CUED vs UNCUED |
| 2. Depth-field cueing | Coherent translator in same depth plane as delayed-onset field | same vs different |
| 3. Depth plane | Absolute depth of coherent translator | Far vs Near |

**Master summary (marginal chi-square):**

| Factor | Binocular (n=768) | Mono R (n=577) | Mono L (n=576) | All mono (n=1153) |
|--------|-------------------|----------------|----------------|-------------------|
| 1. Dot cueing | +16.4pp *** | +8.4pp * | +4.2pp n.s. | +6.3pp * |
| 2. Depth-field cueing | +6.0pp † | +3.6pp n.s. | +7.6pp † | +5.6pp † |
| 3. Far vs Near | +10.7pp ** | −2.2pp n.s. | +1.4pp n.s. | −0.4pp n.s. |

**Binocular by swap condition:**

| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N | 55.5% | 42.2% | +13.3pp | * |
| ZdA | 48.4% | 32.8% | +15.6pp | * |
| ZdB | 55.5% | 35.2% | +20.3pp | ** |

**All mono by swap condition:**

| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N | 46.9% | 39.6% | +7.3pp | n.s. |
| ZdA | 34.4% | 33.3% | +1.0pp | n.s. |
| ZdB | 45.3% | 34.7% | +10.6pp | * |

---

## 3. Error Distribution

| Error | Binocular | Mono R | Mono L |
|-------|-----------|--------|--------|
| 0° (correct) | 44.9% | 35.4% | 44.3% |
| ±45° (adjacent) | 23.2% | 28.4% | 21.7% |
| ±90° | 10.0% | 11.3% | 12.2% |
| ±135° | 11.3% | 15.9% | 13.5% |
| 180° (opposite) | 10.5% | 8.8% | 8.2% |

Cardinal vs diagonal accuracy:
- Binocular: Cardinal 45.6%, Diagonal 44.3% (comparable)
- Mono R: Cardinal **30.8%**, Diagonal **39.9%** (large cardinal deficit — suspect display distortion)
- Mono L: Cardinal 42.0%, Diagonal 43.4% (comparable, like binocular)

Response biases (deviation from flat 12.5%):
- Binocular: toward 270° (+6.1pp), 225° (+3.5pp); away from 315° (−4.4pp)
- Mono R: toward 45° (+6.7pp), 90° (+3.6pp); away from 180° (−4.2pp)
- Mono L: toward 90° (+4.0pp), 0° (+2.1pp); away from 315° (−4.5pp)

Note: bias patterns differ across viewing conditions — the binocular default (lower-left) is avoided under R-eye viewing, replaced by upper-right bias. This shift is consistent with display geometry appearing rotated under monocular viewing.

---

## 4. Tentative Interpretations

### 4.1 Dot cueing (Factor 1) — temporal onset advantage
The cueing effect (CUED > UNCUED) survives monocularly but is attenuated (+16pp binocular → +6pp mono). The effect is present in a no-stereo, no-swap condition (N), confirming that the basic temporal onset advantage is not dependent on stereoscopic depth. This is consistent with prior published work on object-based attention using overlapping dot fields without depth (Mitchell, Valdes-Sosa, Blaser, and colleagues). The attenuation monocularly could reflect: (a) a genuine stereoscopic component, (b) increased response noise monocularly (display distortion, floaters in R eye), or (c) both.

### 4.2 ZdA vs ZdB — what the depth swap does
ZdA and ZdB are matched for number of depth swaps (2 dots each) and rotation reversals (2 each). The critical difference: in ZdA the coherent translator changes depth plane at tStart; in ZdB it stays in its onset plane while the companion moves.

- **ZdB > N binocularly** (ZdB=+20pp**, N=+13pp*): having the companion non-coherent dot move INTO the cued plane at tStart *enhances* cueing above the no-swap baseline. This is not what a simple disruption account predicts. Possible mechanisms: (a) depth-plane grouping sharpening — the companion departing its original plane reduces contamination of the cued plane; (b) active suppression of the unattended surface becoming more effective when the two surfaces are more clearly segregated at tStart.
- **ZdA ≈ N binocularly** (ZdA=+16pp*): the cued dot moving planes is costly but the cueing effect survives. The temporal onset advantage is robust enough to persist even when the cued translator changes depth.
- **Monocularly, ZdA collapses** (+1.0pp n.s.): ZdA and ZdB are identical monocularly except for which dots undergo rotation reversals (both have 2 reversals). The fact that ZdA collapses monocularly while ZdB survives (*) is the key dissociation — it implicates the depth-plane change of the coherent translator specifically, not the reversal count. However, a monocular geometric confound exists: in ZdA, the coherent translator shifts position by up to ~5 arcmin when it changes depth at tStart (position shift scales with eccentricity). This spurious spatial displacement could partially account for ZdA's monocular collapse.

### 4.3 Depth-field cueing (Factor 2) — translation plane advantage
The advantage of translating in the same depth plane as the delayed-onset field survives monocularly at marginal levels (†). This was unexpected. Two accounts: (a) the translation-plane advantage has a non-stereoscopic component — perhaps the shared onset timing creates a grouping signal that is plane-specific even without depth; (b) the rotation reversals in ZdA/ZdB, which are visible monocularly, are partially driving this factor through an indirect route. Distinguishing these requires a condition where depth-field cueing is manipulated without reversals.

### 4.4 Near/Far asymmetry (Factor 3) — entirely stereoscopic
Far > Near translation (+11pp**) is present binocularly and absent across all monocular conditions. No theoretical prediction from prior literature anticipates this asymmetry. Candidate explanations: (a) physiological asymmetry in disparity processing (more neurons tuned to crossed/near disparities in V1/MT); (b) vergence microfluctuations affecting Near more than Far at the fixation distance used; (c) headset-specific optical properties. Needs replication and parametric follow-up.

### 4.5 Caveats
- **Single observer**: all data from GS. Session-to-session variance is large (ZdB ranged +3pp to +56pp across 4 binocular sessions). Generalizability unknown.
- **R-eye data quality**: R-eye sessions show lower overall accuracy (35.4%) vs L-eye (44.3%), cardinal heading deficit, and a shifted response bias pattern — probably reflecting floaters in R eye combined with possible display distortion under monocular viewing. R-eye data should be treated with extra caution.
- **Response bias**: substantial direction-specific biases exist and differ across viewing conditions. Percent correct conflates perceptual signal strength with response-stage artifacts. These biases mean monocular data cannot be straightforwardly compared to binocular using percent correct alone.
- **Session 2 anomaly** (260331_0621): near-zero cueing across all conditions — origin unclear (fatigue, vergence instability, random variation at n=32/cell).

---

## 5. Historical Context and Cross-Experiment Comparison

### 5.1 No-depth baseline at current parameters

The cueing effect has been measured without stereo depth at the current timing (80ms translation, 8-AFC) in three datasets:

| Dataset | n | Δ | p | Notes |
|---------|---|---|---|-------|
| Jan 2026 (260122 pooled) | 128 | **+45pp** | *** | No depth, no swap |
| March 23 pooled | 192 | **+33pp** | *** | No depth, no swap |
| DepthSwapCtrl N, binocular | ~256 | **+13pp** | * | 0.05m depth, stereo |
| DepthSwapCtrl N, all mono | ~384 | **+7pp** | n.s. | 0.05m depth, monocular |

The Jan/March no-depth baselines (+33–45pp) are substantially larger than DepthSwapCtrl binocular N (+13pp). Two non-exclusive explanations: (a) adding stereo depth reduces overall cueing by introducing competing near-plane attention capture; (b) session-to-session variability at small n means the no-depth estimates are noisy. The Jan/March difference (+45 vs +33pp) with the same parameters illustrates this variability.

**Qualification**: The no-depth sessions (Jan, March) had no depth planes and no swap conditions — the observer may have been in a simpler attentional state. DepthSwapCtrl introduces Near/Far depth complexity even in the N condition, which may reduce cueing independently of stereoscopic processing per se.

### 5.2 The Near reversal — a depth-plane attentional capture effect

At 0.10m depth separation (DepthBaseline, March 25), the Near plane showed a strong *reversal* of cueing — UNCUED outperformed CUED by up to 47pp***. The Far plane simultaneously showed +59–60pp*** cueing. This is a large, bidirectional dissociation within the same session.

At 0.05m (DepthSwapCtrl), the reversal disappears but the asymmetry persists: Far=+56pp*** vs Near=+13pp n.s. (binocular N condition). Monocularly, both collapse to near zero.

**Tentative interpretation**: Near-plane stimuli may exert a default attentional priority — possibly related to looming/threat processing or binocular prominence of near-disparate stimuli. When the *UNCUED* field translates at Near depth, this salience advantage overrides the temporal onset cue, producing the reversal. As depth separation decreases, this near-capture effect weakens. The fact that Factor 3 (Far > Near) is entirely absent monocularly confirms it is stereoscopic in origin — it requires genuine disparity signals, not just a monocular depth cue.

This is potentially a novel finding: near-plane motion captures attention even against a competing temporal onset cue, and this effect scales with disparity magnitude.

### 5.3 Motion and dot swaps (March 24–25)

Motion swap reduces cueing ~50% (+29pp → +16pp n.s.) but does not eliminate it. The temporal onset advantage survives a mid-trial change in motion type, suggesting the cue operates primarily on object identity rather than motion feature continuity.

Dot50 swap has no effect (+29pp → +34pp n.s.). Swapping half the dots mid-trial leaves cueing intact — spatial layout and dot identity continuity are not required. The grouping that supports cueing is more abstract than individual dot tracking.

---

## 6. Open Questions and Next Steps

### Immediate (within current pilot)
1. Replicate binocular findings with a second observer — the data pattern is coherent but n=1
2. Investigate display distortion under monocular viewing — does the response wheel appear rotated?
3. Understand Near/Far asymmetry — is it real or an artifact of vergence/optics?

### Measurement
4. **ERP as complement to percent correct**: a neural measure would bypass the response stage entirely. Key targets:
   - *Motion-reversal ERP at tStart*: in ZdA/ZdB, rotation reversals in the cued field should generate a direction-change VEP — enhanced if the cued object is preferentially processed, detectable even on incorrect trials
   - *Delayed-onset ERP at frame 56*: motion onset of Field B — should be enhanced CUED vs UNCUED
   - *Implication*: if enhancement is object-level, all motions of the cued field are enhanced (reversal, non-coherent, translation) — not just the coherent translation. This complicates interpretation of *what* the cueing effect indexes but opens richer measurement possibilities.

### Stimulus design
5. True dichoptic nonius lines — verify vergence during binocular sessions
6. Both-field preview during WaitingForStart — allow vergence stabilization at trial onset
7. Fixation training stage (Catak et al.) — essential for naïve observers

### Theoretical
8. ZdB enhancement mechanism — needs parametric follow-up (vary companion displacement, depth separation)
9. ZdA geometric confound — design condition that separates depth-plane change from position shift
10. Depth-field cueing monocular survival — design condition without rotation reversals to isolate

---

## 7. Headset Comfort and Ergonomics (Note)
To be addressed before multi-subject data collection. Key issues: pressure from headset frame and prescription lens insert, neck strain from headset weight, vergence-accommodation dissociation (VAD), session length limits, and acclimatization protocol for naïve observers. Relevant literature: VR comfort guidelines, VAD effects on perceptual tasks. Assign to Packaging/Protocol agent.
