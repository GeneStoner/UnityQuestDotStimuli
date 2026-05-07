# Threshold Methods for Comparing CUED vs. UNCUED Translation Performance
## Step-by-Step Guide with Trial Count Estimates and Tradeoffs

*Purpose: evaluate adaptive staircase and method of constant stimuli as tools for extracting duration thresholds separately for CUED and UNCUED arms, enabling a continuous, ratio-scale measure of the cueing advantage in VRDots.*

---

## Background: Why a Threshold Measure?

The current VRDots protocol measures percent correct at a fixed translation duration (80ms). This gives a single number per condition but conflates two things: sensitivity (how well the observer can extract the translation signal) and the height of the psychometric function at one arbitrary point on it. A threshold measure asks instead: what is the minimum translation duration required to reach criterion performance in each condition? The CUED–UNCUED threshold difference (in ms) is then the cueing advantage expressed on a ratio scale — more sensitive, and directly interpretable in temporal terms.

**Proposed dependent variable:** T₇₅ — translation duration (ms) at 75% correct on the 8-AFC judgment.

---

## Two Methods Compared

### Method 1: Method of Constant Stimuli (MoCS)

Pre-select a fixed set of N duration levels spanning the expected threshold range. Present each level a fixed number of times in each condition (CUED, UNCUED). At the end, fit a psychometric function (Weibull or logistic) to the resulting accuracy-vs-duration data for each condition, and read off the threshold parameter.

### Method 2: Adaptive Staircase (QUEST or classical up-down)

Adjust the presented duration trial-by-trial based on the observer's responses, concentrating trials near the threshold level. The staircase converges to the threshold without wasting trials at obviously sub- or supra-threshold levels. Run separate (or interleaved) staircases for CUED and UNCUED.

---

## Method 1: Method of Constant Stimuli

### Step-by-Step

1. **Pilot to set level range.** Before running MoCS, run 30–50 informal trials at a few durations to find the rough performance range. You need levels spanning approximately 15%–95% correct. For VRDots 8-AFC, chance is 12.5%, so the range might be roughly 20ms–200ms depending on observer. Without a pilot, levels will be poorly placed and data wasted.

2. **Select duration levels.** Choose 5–7 levels, log-spaced across the expected threshold range. Log-spacing is appropriate because duration thresholds scale multiplicatively.
   - Example (5 levels): 20, 40, 80, 120, 180ms
   - Example (7 levels): 15, 25, 40, 65, 100, 150, 220ms
   - At least one level should produce near-chance performance; at least one should produce near-ceiling performance.

3. **Assign trial counts per level.** For a well-fitted Weibull, you need at minimum 20 trials per level per condition; 40–50 is better; 60+ gives a well-defined slope estimate.
   - With 6 levels and 40 trials each: 240 trials per condition.
   - CUED and UNCUED each get their own set of 240 trials = 480 trials total for the threshold measurement.

4. **Randomize trial order.** Interleave CUED and UNCUED trials randomly within each session. Do not block by condition — you want the observer naive to which condition is being measured at any moment, and you want time-of-session effects distributed evenly.

5. **Fit psychometric function.** Use a Weibull function:
   ```
   ψ(x; α, β, γ, λ) = λ + (1 − λ − γ) · (1 − exp(−(x/α)^β))
   ```
   - α = threshold (duration at which performance = γ + (1−γ−λ)·(1−1/e) ≈ 63% of the way from chance to ceiling)
   - β = slope
   - γ = guess rate (1/8 = 0.125 for 8-AFC)
   - λ = lapse rate (typically fixed at 0.02–0.04)

   **Use psignifit 4** (Schütt et al., 2016) or Palamedes toolbox (Prins & Kingdom, 2018). Both handle the 8-AFC floor correctly and provide confidence intervals on α.

6. **Extract threshold.** Read off T₇₅: the duration at which ψ = 75% correct. This is directly comparable between CUED and UNCUED fits.

7. **Bootstrap confidence intervals on the threshold difference.** Resample the trial-level data with replacement (2000 iterations), refit the psychometric function each time, and compute the distribution of (α_UNCUED − α_CUED). The 95% CI of this distribution is your comparison. If it excludes zero, the conditions differ.

### Wrinkles

- **Floor problem with 8-AFC.** Chance is 12.5%, not 50%. The psychometric function rises from 12.5%, so short-duration performance will cluster near chance but not below it. Standard Weibull implementations assume a 2-AFC floor (50%) unless you specify γ = 0.125 explicitly — check this in whatever software you use.

- **Lapse rate matters more with 8-AFC.** A single lapse (response to wrong direction) has a small effect in 2-AFC (chance is already 50%) but a larger effect in 8-AFC because it pulls performance toward 12.5% rather than 50%. Fix λ = 0.02–0.04 rather than estimating it freely unless you have many trials.

- **Level placement error is costly.** If your pilot estimate of the threshold range is off, several levels may land outside the informative zone of the psychometric function. The Weibull slope parameter β will then be poorly constrained. This is the primary weakness of MoCS relative to adaptive methods.

- **Duration resolution.** On Quest hardware at 90Hz, the minimum duration increment is 1 frame ≈ 11ms. Your duration levels must be integer multiples of the frame time (11.1ms at 90Hz, 8.3ms at 120Hz). Design levels accordingly — you cannot present 40.0ms, only 33.3ms or 44.4ms (3 or 4 frames at 90Hz).

---

## Method 2: Adaptive Staircase (QUEST)

### Step-by-Step

**Recommended: QUEST** (Watson & Pelli, 1983) rather than classical 1-up/2-down staircase. QUEST is a Bayesian adaptive procedure that maintains a posterior distribution over the threshold and places each trial at the current maximum-likelihood threshold estimate. It converges faster and gives a better-calibrated threshold estimate for the same number of trials.

For simultaneous estimation of threshold AND slope: use **QUEST+** (Watson, 2017), which treats both α and β as free parameters.

1. **Set priors.** QUEST requires a prior on the threshold location (mean and SD in log-duration space). From your pilot or existing data, estimate roughly where CUED and UNCUED thresholds lie. Use a broad SD (~1 log unit) if uncertain. The prior only affects early trials; later trials are dominated by the data.
   - Suggested prior for CUED: mean ~40ms, SD ~0.5 log units (covers 13–120ms)
   - Suggested prior for UNCUED: mean ~100ms, SD ~0.5 log units (covers 33–300ms)

2. **Target performance level.** QUEST targets a criterion performance level (tGuess in the original formulation). For 8-AFC, target 75% correct (halfway between chance and ceiling is a reasonable, sensitive operating point). Specify β (slope steepness) from literature or pilot — a reasonable starting value for duration discrimination is β ≈ 2.0–3.0.

3. **Run interleaved QUEST staircases.** Run one QUEST staircase for CUED and one for UNCUED simultaneously, interleaved randomly within each session. This balances order effects and keeps the observer from adapting to a single difficulty level. On each trial: randomly select which staircase contributes the trial; present the corresponding duration level; update only that staircase's posterior.

4. **Trials per staircase run.** For a usable threshold estimate from a single run:
   - Minimum: 40 trials (useful but noisy)
   - Good: 60–70 trials (SD of threshold estimate ~0.15 log units)
   - Excellent: 80–100 trials (SD ~0.10 log units)

   A session of 140 interleaved trials (70 CUED + 70 UNCUED) gives one threshold estimate per condition per session.

5. **Multiple runs.** Run 4–6 sessions per condition for a stable mean threshold. Average the QUEST threshold estimates across sessions (or pool all trial data and fit a single psychometric function with session as a random effect).

6. **Statistical comparison.** Two options:

   **Option A — Paired t-test on session-level threshold estimates.**
   You have 5 CUED estimates and 5 UNCUED estimates, each from the same session. Compute difference scores (UNCUED_i − CUED_i) per session. One-sample t-test on the difference scores against zero. Report Cohen's d.

   **Option B — Pool all trials, fit psychometric functions, bootstrap.**
   Same as MoCS step 7. This is more efficient because it uses all trial-level data rather than just the reversal/QUEST-estimated threshold per session.

7. **Check staircase convergence.** Plot the trial-by-trial duration sequence for each staircase. QUEST should show rapid convergence within the first 20 trials and then oscillation near threshold. If the staircase is still wandering at trial 50+, the prior was too far off or the lapse rate is high.

### Wrinkles

- **UNCUED staircase may converge to very long durations.** If UNCUED threshold is ~150ms and your rotation cycle is ~500ms, a single trial now occupies a substantial fraction of the display period. Decide in advance on a maximum allowable duration (e.g., 300ms) and hard-clamp the staircase there if needed.

- **Slope is not well-estimated by QUEST alone.** The standard QUEST estimator gives a precise threshold but treats slope as fixed (set by your prior). If you want a slope estimate, either use QUEST+ (Watson, 2017) or pool all staircase trials and fit a Weibull post-hoc. Do not report slope from a single QUEST run as meaningful.

- **Interleaving can cause attentional switching costs.** If the observer knows which condition is coming (e.g., from the trial structure), they may engage differently. In VRDots, CUED/UNCUED is defined by which field the target translation appears in — this is only revealed at the moment of translation, so the observer cannot strategically allocate attention differently before the trial. This is actually an advantage: CUED/UNCUED cannot be "gamed" in advance.

- **Frame-duration quantization.** Same issue as MoCS: QUEST will request a duration that may fall between frame boundaries. Round to the nearest frame before presenting; feed the rounded duration (not the QUEST-requested duration) back into the staircase as the stimulus level for that trial.

- **Classical staircase alternative** (if QUEST is not available): 1-up/2-down staircase converges to 70.7% correct; 1-up/3-down converges to 79.4%. Use step sizes of 0.2 log units until the first reversal, then 0.1 log units. Threshold = mean of the last 6 reversal points. Requires ~60–80 trials per staircase to get 10–12 reversals. Noisier than QUEST for the same trial count.

---

## Trial Count Estimates

### Target effect size

From current VRDots data: the cueing advantage at fixed 80ms duration is approximately +27pp. If CUED accuracy at 80ms is ~65% and UNCUED is ~38%, these likely bracket the respective thresholds (T₇₅ for CUED might be ~40ms; for UNCUED ~120–150ms). The threshold ratio is large (~3:1), corresponding to a Cohen's d of 3–5 on log-duration if between-run SD is ~0.15 log units. This is an enormous effect size — you need far fewer trials than a typical psychophysics study.

### MoCS trial counts

| Trials/level | Levels | Conditions | Total trials | Psychometric fit quality |
|---|---|---|---|---|
| 20 | 6 | 2 | 240 | Threshold OK; slope poorly constrained |
| 40 | 6 | 2 | 480 | Threshold good; slope usable |
| 60 | 7 | 2 | 840 | Threshold and slope both reliable |
| 40 | 7 | 2 | 560 | Recommended minimum |

Pilot trials (not counted above): ~60–100 to calibrate level spacing.

**Total including pilot: ~600–900 trials** for a complete MoCS measurement.

At ~200 trials/session (realistic for VRDots with randomized durations), this is 3–5 sessions.

### Adaptive staircase trial counts

| Trials/staircase | Sessions | Conditions | Total trials | Threshold precision |
|---|---|---|---|---|
| 50 | 4 | 2 | 400 | SD ~0.15 log units per estimate; paired t-test with n=4 pairs |
| 70 | 5 | 2 | 700 | SD ~0.12 log units; paired t-test with n=5 pairs |
| 80 | 6 | 2 | 960 | SD ~0.10 log units; well-powered for Cohen's d ≥ 1 |

For the expected large effect size (Cohen's d ≥ 2): **4 sessions of 140 trials (70 CUED + 70 UNCUED each) = 560 total trials** will give >0.99 power for a paired t-test. This can be verified with a G*Power calculation using d=2.0, α=0.05, n=4 pairs.

No pilot needed for adaptive method — the staircase self-calibrates. But the first session's data may be noisier as QUEST converges from a cold prior; consider treating session 1 as warm-up.

**Total: ~560–700 trials** for a complete adaptive measurement.

---

## Pros and Cons Summary

| Feature | Method of Constant Stimuli | Adaptive Staircase (QUEST) |
|---|---|---|
| **Total trials needed** | More (~600–900) | Fewer (~500–700) |
| **Pilot required?** | Yes — level spacing must be pre-set | No — self-calibrating |
| **Slope estimate** | Good (many trials at each level) | Poor from single run; requires QUEST+ or post-hoc fit |
| **Threshold estimate precision** | Good when levels are well-placed | Good; better if levels are near threshold |
| **Wasted trials** | Yes — extreme levels contribute little | Minimal — trials concentrate near threshold |
| **Sensitivity to prior** | None | Moderate — early trials affected by prior |
| **Robustness to lapses** | Good — lapses distributed across levels | Can distort staircase if lapse occurs near threshold |
| **Suitable for online analysis** | No | Yes — threshold available in real time |
| **Multiple conditions in one session** | Yes — interleave freely | Yes — interleave QUEST instances freely |
| **Software complexity** | Low — just fit Weibull to binomial data | Moderate — need QUEST implementation |
| **Frame-quantization issue** | Minor — levels are pre-set to valid frames | Minor — must round QUEST requests to frame grid |
| **Reveals psychometric function shape** | Yes — full function visible | Not directly (only threshold) |
| **Standard in motion perception literature** | Yes (Britten et al. 1992 style) | Yes (widely used in contrast/motion sensitivity) |

**Recommended default:** QUEST, interleaved CUED/UNCUED, 5 sessions of 140 trials = 700 trials total. Use post-hoc Weibull fit (psignifit 4) to get both threshold and slope from pooled data. Compare thresholds with paired t-test on session-level estimates and bootstrap confidence interval on the pooled-data difference.

**When to prefer MoCS:** if you want a clean psychometric function for publication (slope estimate, full curve visualization); if you want to rule out that the two conditions differ in slope and not just threshold; if you have reason to distrust QUEST convergence (e.g., highly variable performance).

---

## Statistical Analysis: Step-by-Step

### Primary analysis (session-level)

1. Each session yields one threshold estimate per condition: α_CUED,i and α_UNCUED,i.
2. Compute Δ_i = log(α_UNCUED,i) − log(α_CUED,i) for each session. Work in log-duration because threshold distributions are approximately log-normal.
3. One-sample t-test: H₀: mean(Δ) = 0. Report t(df), p, and Cohen's d = mean(Δ)/SD(Δ).
4. Back-transform to ratio: exp(mean(Δ)) = α_UNCUED / α_CUED (e.g., 2.8× longer duration needed for UNCUED).

### Secondary analysis (trial-level, more powerful)

1. Pool all trials across sessions. Each trial: [duration_ms, correct/incorrect, condition (CUED/UNCUED)].
2. Fit separate Weibull functions to CUED and UNCUED data using psignifit 4, specifying:
   - `sigmoid = 'weibull'`
   - `experiment_type = 'nAFC'`, `nAFC = 8`
   - Fixed `lapse_rate = 0.02`
3. Bootstrap the threshold difference:
   ```python
   import psignifit as ps
   import numpy as np

   def threshold_diff(data_cued, data_uncued, n_bootstrap=2000):
       diffs = []
       for _ in range(n_bootstrap):
           idx_c = np.random.choice(len(data_cued), len(data_cued), replace=True)
           idx_u = np.random.choice(len(data_uncued), len(data_uncued), replace=True)
           res_c = ps.psignifit(data_cued[idx_c], sigmoid='weibull',
                                experiment_type='nAFC', nAFC=8)
           res_u = ps.psignifit(data_uncued[idx_u], sigmoid='weibull',
                                experiment_type='nAFC', nAFC=8)
           diffs.append(res_u.threshold(0.75) - res_c.threshold(0.75))
       return np.array(diffs)

   diffs = threshold_diff(cued_data, uncued_data)
   ci = np.percentile(diffs, [2.5, 97.5])
   print(f"UNCUED - CUED threshold: {np.mean(diffs):.1f} ms, 95% CI [{ci[0]:.1f}, {ci[1]:.1f}]")
   ```
4. Report: threshold difference in ms, 95% CI, and whether CI excludes zero.

### Checking slope differences

Fit a constrained model (shared slope β) and an unconstrained model (separate β per condition). Compare with likelihood ratio test (or AIC/BIC). If slope differs, the threshold comparison is still valid but the interpretation changes — a steeper slope in CUED means the cued surface is not just more sensitive but more decisively processed.

---

## Extension to Other Conditions

Once the CUED/UNCUED baseline thresholds are established, the same method extends naturally to:

- **Near vs. Far**: run separate CUED QUEST staircases for near-plane and far-plane conditions; compare T₇₅
- **ZdA vs. ZdB**: compare CUED threshold in depth-continuous vs. depth-disrupted conditions
- **Density parametric**: track threshold as a function of dot count N; plot T₇₅(N) for CUED and UNCUED separately
- **SOA manipulation**: run QUEST at each of several cue-target SOAs; plot threshold vs. SOA to get an attention time-course function

In each case, the statistical comparison is the same: paired t-test on session-level threshold estimates, plus bootstrap CI on pooled psychometric function fits.

---

## Key References

**Adaptive staircase methods:**
- Watson, A. B. & Pelli, D. G. (1983). QUEST: A Bayesian adaptive psychometric method. *Perception & Psychophysics*, 33(2), 113–120.
- Watson, A. B. (2017). QUEST+: A general multidimensional Bayesian adaptive psychometric method. *Journal of Vision*, 17(3):10.
- Treutwein, B. (1995). Adaptive psychophysical procedures. *Vision Research*, 35(17), 2503–2522.
- Leek, M. R. (2001). Adaptive procedures in psychophysical research. *Perception & Psychophysics*, 63(8), 1279–1292.

**Psychometric function fitting:**
- Wichmann, F. A. & Hill, N. J. (2001). The psychometric function: I. Fitting, sampling, and goodness of fit. *Perception & Psychophysics*, 63(8), 1293–1313.
- Schütt, H. H., Harmeling, S., Macke, J. H., & Wichmann, F. A. (2016). Painfree and accurate Bayesian estimation of psychometric functions for (potentially) overdispersed data. *Vision Research*, 122, 105–123. [psignifit 4]
- Prins, N. & Kingdom, F. A. A. (2018). Applying the model-comparison approach to test specific research hypotheses in psychophysical research using the Palamedes Toolbox. *Frontiers in Psychology*, 9, 1250.

**Motion coherence threshold methods:**
- Britten, K. H., Shadlen, M. N., Newsome, W. T., & Movshon, J. A. (1992). The analysis of visual motion: A comparison of neuronal and psychophysical performance. *Journal of Neuroscience*, 12(12), 4745–4765.
- Gold, J. I. & Shadlen, M. N. (2001). Neural computations that underlie decisions about sensory stimuli. *Trends in Cognitive Sciences*, 5(1), 10–16.

**Attention and motion thresholds:**
- Treue, S. & Martínez-Trujillo, J. C. (1999). Feature-based attention influences motion processing gain in macaque visual cortex. *Nature*, 399, 575–579.
- Lu, Z.-L. & Dosher, B. A. (1998). External noise distinguishes attention mechanisms. *Vision Research*, 38(9), 1183–1198.
- Edwards, M., Cassidy, B., & Badcock, D. R. (2021). No effect of spatial attention on motion ensemble processing. *Attention, Perception, & Psychophysics*, 83, 2391–2403.

**Motion duration thresholds:**
- Watamaniuk, S. N. J. & Duchon, A. (1992). The human visual system averages speed information. *Vision Research*, 32(5), 931–941.
- Watamaniuk, S. N. J., Sekuler, R., & Williams, D. W. (1984). Direction perception in complex dynamic displays: The integration of direction information. *Vision Research*, 24(1), 55–62.
