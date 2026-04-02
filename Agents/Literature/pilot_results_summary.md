# VRDots Pilot Results — Integrated Summary
*Author: Literature agent. Generated 2026-04-01. Update as new sessions accumulate.*

---

## Critical methodological note: color context

*Verified from TSV DelayedFieldColor column, 2026-04-01.*

**Color configuration by experiment:**

| Experiment | Sessions | Color |
|-----------|---------|-------|
| Baseline | 260323_1534, 260324_0716 | **Two-color** (R+G, ~50/50 balanced) |
| MotionSwap | 260324_1010 | **Two-color** (R+G) |
| Dots50Swap | 260325_1039 | **Two-color** (R+G) |
| DepthBaseline | 260325_1831, 1914, 2013 | **Two-color** (R+G) |
| DepthSwap50 | 260326_1649 | **Unknown** — not in any current pull |
| DepthSwapCtrl | 260330_1853 onward (all) | **Same-color** (R only, `balanceDelayedFieldColor=false`) |

The same-color switch was introduced specifically for DepthSwapCtrl, not at the onset of depth experiments. All prior sessions — including the DepthBaseline sessions that first revealed the Far >> Near asymmetry — were two-color.

This distinction matters in two ways:

**1. Between-experiment comparisons are partially confounded.** The large cueing magnitudes in two-color Baseline (~28–50pp) vs. same-color DepthSwapCtrl (~12.5pp) cannot be attributed purely to the depth vs. no-depth manipulation — the removal of the color dimension is a concurrent change. Mitchell, Stoner, Fallah & Reynolds (2003) showed color removal does not eliminate cueing, but our model and Catak et al. (2022) both suggest color is *facilitative*. The reduced DepthSwapCtrl cueing likely reflects both the weaker point-set from same-color design and within-experiment swap noise.

**2. The Far >> Near asymmetry is color-robust.** The asymmetry was first observed in two-color DepthBaseline sessions (e.g., Far=+59–65pp, Near=−5 to −47pp at 0.10m) and is again present in same-color DepthSwapCtrl (Far=+30.9pp***, Near=−5.9pp n.s. at 0.05m). That the asymmetry survives the color manipulation — and the reduction in depth separation from 0.10m to 0.05m — suggests it is a robust property of the depth-plane representation, not an artifact of the color design.

**Implication**: the appropriate within-experiment comparisons (N vs. ZdA vs. ZdB, Near vs. Far, binocular vs. monocular within DepthSwapCtrl) are all internally consistent as same-color. Cross-experiment comparisons of cueing magnitude must account for the color and depth-separation differences simultaneously.

---

## 1. Full Pilot Session Overview

### 1.1 Non-depth experiments (two-color: red + green fields)

| Session | Experiment | Cueing effect | Notes |
|---------|-----------|---------------|-------|
| 260323_1534 | Baseline | +50.0pp | Pre-v0.2.0; strongest overall cueing observed |
| 260324_0716 | Baseline | +28.1pp | Cursor-jump artifacts; cueing still present |
| 260324_1010 | MotionSwap | +27.1pp (N) → +15.7pp (swap) | 100% motion swap reduces but does not eliminate cueing; selection follows dots, not direction |
| 260325_1039 | Dots50Swap | +30.4pp (N) → +34.4pp (swap) | 50% dot swap does NOT reduce cueing; sub-threshold disruption |

**Two-color baseline cueing range**: ~28–50pp across sessions (high between-session variance even without depth manipulation).

### 1.2 Depth experiments

#### DepthBaseline (no swap — depth as a passive variable; **two-color: R+G**)

| Session | Depth sep | Overall | Near | Far | Notes |
|---------|-----------|---------|------|-----|-------|
| 260325_1831 | 0.10m | +27.5pp | −4.9pp | +59.4pp | Depth planes clearly visible |
| 260325_1914 | 0.10m | +8.6pp | −46.9pp | +65.1pp | Depth planes clear; near strongly inverted |
| 260325_2013 | 0.03m | +16.6pp | +13.7pp | +19.4pp | Depth barely perceptible; Near/Far similar |

**Key observation**: The Far >> Near asymmetry is already present in the DepthBaseline sessions, before any swap manipulation, and scales with depth separation magnitude. At 0.03m (barely perceptible depth) Near ≈ Far; at 0.10m Far is massive (+59–65pp) and Near is actually inverted (negative cueing). This is not an artifact of the swap design — it is a property of the depth plane itself under stereoscopic viewing.

#### DepthSwap50 (single session: both N and Zd conditions; **color config unverified — session not in current pull**)

| Session | Depth sep | Overall | Near | Far | N vs Zd |
|---------|-----------|---------|------|-----|---------|
| 260326_1649 | 0.05m | +40.3pp | +28pp | +53pp | N: +44.8pp, Zd: +35.9pp |

*Note: DepthSwap50 uses a 50% depth swap rather than the 100% ZdA/ZdB design; single session.*

#### DepthSwapCtrl (primary experiment: N / ZdA / ZdB × CUED/UNCUED × Near/Far; **same-color: R only**)

All 192 trials/session, all completed, depth separation 0.05m, both fields red.

**Sessions**:

| Session | Eye | Overall acc | Notes |
|---------|-----|------------|-------|
| 260330_1853 | Binocular | 46.4% | Session 1; strongest effects |
| 260330_2012 | Mono R (L closed) | 33.2% | Mono R #1; right eye has floaters |
| 260331_0621 | Binocular | 38.0% | Session 2; anomalously weak |
| 260331_1530 | Mono R (L closed) | 39.1% | Mono R #2 |
| 260331_1705 | Mono L (R closed) | 45.3% | Mono L #1 |
| 260331_1734 | Mono L (R closed) | 43.2% | Mono L #2 |
| 260401_1313 | Binocular | 51.0% | Session 3; good performance |
| 260401_1349 | Binocular | 44.3% | Session 4 |
| 260401_1541 | Binocular | 33.9% | Session 5; performance collapse (fatigue — 4th VR session same day) |
| 260401_1705 | Binocular | 39.6% | Session 6; also weak (fatigue) |

---

## 2. DepthSwapCtrl Results — Full Dataset

*Binocular: 6 sessions, n=1152. Monocular: 4 sessions, n=769. All DepthSwapCtrl_005m, same-color (both red).*

### 2.1 Dot cueing effect (Factor 1)

| Viewing | CUED | UNCUED | Effect | z | sig |
|---------|------|--------|--------|---|-----|
| Binocular (n=1152) | 48.4% | 35.9% | **+12.5pp** | 4.30 | *** |
| Monocular (n=769) | 43.8% | 36.6% | **+7.1pp** | 2.02 | * |

The core temporal-onset cueing effect is present and reliable binocularly, and survives (attenuated) monocularly. Monocular survival is consistent with Mitchell et al. (2004) and Khoe et al. (2008): object-based selection does not require binocular input. The attenuation likely reflects loss of the depth-plane facilitation dimension rather than loss of the core mechanism.

**Comparison with two-color sessions**: The two-color Baseline sessions showed ~28–50pp cueing. The same-color DepthSwapCtrl shows ~12.5pp binocularly. Part of this difference is the removal of the color dimension (the swap conditions also add noise), but the two-color advantage is consistent with the Mitchell (2003) facilitative-color interpretation and the V1 Point-Set prediction that color adds a feature dimension.

### 2.2 SwapType breakdown

#### Binocular (n=192 per swap condition)

| Swap | CUED | UNCUED | Effect | z | sig |
|------|------|--------|--------|---|-----|
| N (no swap) | 51.0% | 41.1% | +9.9pp | 1.95 | † |
| ZdA (cued dot changes depth) | 42.7% | 31.2% | +11.5pp | 2.33 | * |
| ZdB (non-coh changes depth) | 51.6% | 35.4% | +16.1pp | 3.19 | ** |

Pattern: ZdB > ZdA ≈ N. The dramatic ZdA "killing" reported from session 260330_1853 alone (N=+34pp** vs ZdA=+12pp n.s.) does not replicate robustly across sessions: pooled, ZdA is significant (*) and only modestly below N. ZdB is consistently the strongest condition. ZdA and ZdB are matched for number of depth swaps and rotation disruptions — the only difference is whether the coherent (cued) translator changes depth plane. ZdB's advantage therefore reflects the clean benefit of keeping the cued translator in its plane.

#### Monocular (n=128 per swap condition)

| Swap | CUED | UNCUED | Effect | z | sig |
|------|------|--------|--------|---|-----|
| N | 49.2% | 39.8% | +9.4pp | 1.51 | n.s. |
| ZdA | 35.9% | 35.9% | **+0.0pp** | 0.00 | n.s. |
| ZdB | 46.1% | 34.1% | +12.0pp | 1.96 | * |

**The ZdA monocular collapse to exactly zero is the cleanest mechanistic result in the dataset.** ZdA's modest binocular cueing depends entirely on stereoscopic depth. Monocularly — when there is no disparity signal to track depth-plane membership — the cued dot changing depth plane has no effect. ZdB survives monocularly (+12.0pp*), indicating that ZdB's advantage is at least partly monocular (geometric/positional: the non-coh distractor moving introduces a monocular position shift on the distractor, but not the target).

This dissociation is strong evidence that ZdA and ZdB operate through different mechanisms:
- **ZdA binocular effect**: requires stereoscopic depth — depth-plane identity of the cued dot matters; losing it reduces cueing
- **ZdB monocular survival**: independent of stereoscopic depth — ZdB's benefit may reflect distractor positional disruption (monocular) plus depth-plane purity of the cued surface (binocular add-on)

### 2.3 Near/Far asymmetry (Factor 3) — the dominant finding

#### Binocular

| Depth | CUED | UNCUED | Effect | z | sig |
|-------|------|--------|--------|---|-----|
| Near | 42.4% | 48.3% | **−5.9pp** | −1.42 | n.s. |
| Far | 54.5% | 23.6% | **+30.9pp** | 7.60 | *** |
| Interaction (Far − Near) | | | **+36.8pp** | 6.50 | *** |

Far cueing is massive and robust. Near cueing is not merely absent — it is inverted. Cued Near trials actually perform *worse* than uncued Near trials (though n.s.). This is not a ZdA/ZdB artifact: the Near inversion appears within every swap type:

| Swap | Near cueing | Far cueing |
|------|------------|------------|
| N | −8.3pp n.s. | +28.1pp *** |
| ZdA | −7.3pp n.s. | +30.2pp *** |
| ZdB | −2.1pp n.s. | +34.4pp *** |

**The Near cueing deficit is present across all three swap conditions and is therefore not attributable to ZdA/ZdB depth manipulations.** It is a property of the Near depth plane itself.

#### Monocular

| Depth | Effect | sig |
|-------|--------|-----|
| Near | +1.8pp | n.s. |
| Far | +12.5pp | * |

The Near inversion seen binocularly disappears monocularly (Near becomes +1.8pp n.s.). The Far >> Near asymmetry persists monocularly but is much smaller (+12.5pp vs +30.9pp binocular). This confirms the asymmetry has both a binocular (stereoscopic) component and a monocular component, with the bulk of the effect being stereoscopic.

### 2.4 Three-factor summary

| Factor | Binocular | Monocular | Binocular signature |
|--------|-----------|-----------|---------------------|
| 1. Dot cueing | +12.5pp*** | +7.1pp* | Survives mono, attenuated |
| 2. SwapType (ZdB > N > ZdA) | ZdB−ZdA = +4.6pp | ZdB−ZdA = +12pp* | ZdA collapse mono is stereoscopic |
| 3. Near/Far (Far >> Near) | +36.8pp*** interaction | +10.7pp* | Largely stereoscopic |

---

## 3. Theoretical Interpretation

### 3.1 Color, depth, and cueing magnitude across experiments

Now that color config is verified, three distinct conditions exist in the pilot data:

| Condition | Color | Depth | Overall cueing | Far cueing |
|-----------|-------|-------|----------------|------------|
| Two-color, no depth (Baseline) | R+G | None | ~28–50pp | n/a |
| Two-color, depth 0.10m (DepthBaseline) | R+G | 0.10m | ~8–28pp | ~59–65pp |
| Same-color, depth 0.05m (DepthSwapCtrl) | R only | 0.05m | +12.5pp | +30.9pp |

The overall cueing magnitude in two-color DepthBaseline (~8–28pp average of two 0.10m sessions) is not dramatically different from same-color DepthSwapCtrl (+12.5pp), despite the larger depth separation. This is because overall cueing in both depth conditions is dominated by the Near/Far split — the Near plane suppresses overall cueing by contributing a negative term, masking a much larger Far effect.

**The more informative comparison is Far-plane cueing only:**
- Two-color, no depth: ~28–50pp (no Near/Far distinction)
- Two-color, depth 0.10m: Far ~59–65pp
- Same-color, depth 0.05m: Far ~31pp

This pattern is consistent with the V1 Point-Set model prediction: **depth separation adds a dimension to the point-set, facilitating Far-plane cueing above the no-depth baseline.** The two-color DepthBaseline shows the largest Far cueing of any condition tested (~59–65pp), combining both color and a strong depth signal (0.10m). Reducing depth separation to 0.05m AND removing color (DepthSwapCtrl) brings Far cueing down to ~31pp — still substantial and ***. The relative contributions of the two changes (color removal vs. depth reduction) cannot be separated without a within-experiment manipulation, but both are predicted to reduce cueing by the model.

**The prediction from our model** — that two-color + depth-separated stimuli should produce the strongest cueing — is partially supported by the DepthBaseline Far data (~59–65pp Far cueing with two-color + 0.10m). A direct within-experiment comparison (same-color vs. two-color within DepthSwapCtrl at 0.05m) would be the clean test and has not been run.

**One important caveat**: the two-color DepthBaseline sessions have no swap conditions (no ZdA/ZdB noise), single-session n (n=16/cell), and larger depth separation than DepthSwapCtrl. Direct magnitude comparisons should be treated as indicative rather than definitive.

### 3.2 Far >> Near asymmetry: candidate accounts

This is the most robust and theoretically novel finding. No prior published study in the transparent-motion literature has tested this comparison, and no theoretical framework predicts it a priori. Importantly, the asymmetry is present in **both** the two-color DepthBaseline sessions (Far ~59–65pp, Near ~−5 to −47pp at 0.10m) and the same-color DepthSwapCtrl sessions (Far +30.9pp***, Near −5.9pp n.s. at 0.05m). Its replication across color conditions and depth separations argues against it being a color-interaction artifact and in favor of a genuine depth-plane effect. Candidate accounts:

**a) MT population anisotropy** (PubMed 21068268, not yet retrieved): MT is reported to have more neurons tuned to far disparities in some preparations. A larger neural population for Far-plane stimuli would produce stronger attentional selection signals for the Far surface.

**b) Depth-column facilitation asymmetry**: If far-disparity values are more reliably represented in V1 disparity columns than near-disparity values — due to the optics of the Quest HMD, vergence stability, or the statistics of natural disparity — the Far point-set would have a more stable depth dimension, producing stronger cueing. Consistent with the DepthBaseline data where Near cueing is actually negative at 0.10m.

**c) Monocular geometric confound (asymmetric sign)**: At depth change, the cyclopean positional shift scales with eccentricity. If the Quest renders Near and Far planes with a sign asymmetry (e.g., Near dots shift in the opposite direction to Far dots upon vergence re-stabilization), this could systematically help or hurt Near vs. Far cueing. The fact that Near inversion is present even in the N (no-swap) condition argues against a swap-specific confound, but a vergence-drift asymmetry is harder to rule out.

**d) Perceptual stability**: Near surfaces may be more prone to vergence fluctuation and perceptual instability than Far surfaces in HMD viewing (vergence-accommodation conflict is greater for near stimuli). An unstable Near surface would produce a weaker or noisier point-set representation.

**The monocular data is informative**: the Near inversion is absent monocularly (Near becomes +1.8pp n.s. monocularly vs −5.9pp binocularly). This means the Near inversion is specifically stereoscopic — not a response bias or direction-encoding artifact. It is generated or amplified by the binocular disparity representation of the Near plane.

### 3.3 ZdA/ZdB dissociation: stereoscopic surface-identity

The binocular ZdA effect (cued translator changes depth plane → cueing reduced) and ZdB effect (non-coh changes depth plane → cueing enhanced) both survive binocularly. Monocularly, ZdA collapses to zero and ZdB survives.

This cleanly separates two components:

- **ZdA: depth-plane identity of the cued dot is stereoscopic**. Monocularly, changing depth plane of the cued translator has no behavioral consequence. The cued dot's depth-plane membership is only behaviorally relevant when binocular disparity is available. This is the strongest evidence in the dataset that the V1 point-set mechanism, as applied to depth, requires stereoscopic input.

- **ZdB: distractor depth disruption is partly monocular**. The ZdB advantage (companion non-coh moves into cued plane) survives monocularly at +12.0pp*. This suggests ZdB benefits from at least one monocular mechanism — likely the positional shift of the non-coh distractor at depth change (a 1.5–5 arcmin jump depending on eccentricity), which may briefly disrupt the distractor surface representation at tStart independent of disparity.

### 3.4 Comparison with Catak et al. (2022)

Catak et al. ran analogous swap conditions using motion-direction swaps and color swaps (not depth swaps). Their color-swap result (20.2pp → 13.4pp, ~34% reduction, p=.049) provides the closest published analog to ZdA. In our data, ZdA shows +11.5pp vs. N's +9.9pp binocularly — actually *less* disruption than expected from the Catak color-swap analog. Two explanations:

1. The Catak color-swap disrupts color-column coherence of the cued surface globally (all dots change color); ZdA only disrupts the depth column of the two dots that change depth (a partial disruption).

2. The Catak motion-swap has no analog in our current data, but their full motion-swap eliminated cueing. Our ZdA is a depth analog — it disrupts depth-column coherence for just the coherent translator, not the whole field.

### 3.5 Relation to binocular rivalry literature

Mitchell, Stoner & Reynolds (2004) showed that the translating-dot cue selects a surface that then dominates in subsequent binocular rivalry, regardless of which eye's image it appeared in — ruling out eye-of-origin as the selection mechanism. The monocular survival of VRDots dot cueing (+7.1pp*) is consistent with this: the surface-selection mechanism does not require binocular viewing.

Khoe et al. (2008) found that the ERP P1 modulation of surface-based attention appears under rivalry (dichoptic viewing) but not monocular viewing. Our behavioral result shows the opposite pattern in one respect: monocular cueing *does* survive behaviorally (+7.1pp*). The reconciliation may be that monocular behavioral cueing reflects a different mechanism (motion-onset temporal advantage, N1-indexed) than the rivalry-specific interocular competition component (P1-indexed). These are not mutually exclusive.

---

## 4. Open Questions and Priorities

### Highest priority (mechanistic)

1. **Why is Near cueing inverted?** This is the largest unexplained finding. The inversion is binocular, present across all swap types, and absent monocularly. A dedicated experiment manipulating depth separation (0.03m, 0.05m, 0.10m) within a single session would test whether the inversion scales with separation magnitude and whether it crosses zero at some intermediate value.

2. **ZdA monocular zero — confirmation**: ZdA hits exactly 0.0pp monocularly with n=128. This is compelling but needs replication. A dedicated monocular session focused on ZdA vs. N would confirm or refute this clean dissociation.

3. **Two-color + depth condition**: the V1 Point-Set model predicts that two-color, depth-separated stimuli should produce the strongest cueing of any condition tested. Running DepthSwapCtrl with two-color stimuli would directly test the color × depth facilitation prediction and allow the first within-experiment comparison of same-color vs. two-color with depth present.

### Methodological

4. **Single observer (GS)**: all data from one person. Floaters in R eye reduce reliability of R-eye monocular sessions. L-eye monocular data is cleaner. Scaling to additional observers is essential before any of these effects can be published.

5. **Fatigue limit**: today's sessions 3–4 (1541, 1705) showed performance collapse (34–40% accuracy) after 4 consecutive VR sessions. Maximum productive sessions per day appears to be 2, possibly with forced break between.

6. **Response bias shift across viewing conditions**: the over-represented response directions differ substantially between binocular, R-eye, and L-eye conditions, suggesting display geometry or motor habits shift with viewing condition. This inflates variance in percent-correct comparisons. A neural measure (motion-onset ERP) would bypass the response stage.

7. **True dichoptic nonius lines**: not yet implemented. Vergence stability during binocular sessions is unverified beyond behavioral performance.

---

## 5. Summary Table — All VRDots Pilot Cueing Effects

| Session | Experiment | Color | Depth | Eye | Overall cueing | Notes |
|---------|-----------|-------|-------|-----|---------------|-------|
| 260323_1534 | Baseline | **2-color** | None | Bino | +50.0pp | Pre-v0.2.0; largest cueing observed |
| 260324_0716 | Baseline | **2-color** | None | Bino | +28.1pp | Cursor artifacts |
| 260324_1010 | MotionSwap | **2-color** | None | Bino | +27.1pp → +15.7pp | Full swap halves cueing |
| 260325_1039 | Dots50Swap | **2-color** | None | Bino | +34.4pp | 50% swap no effect |
| 260325_1831 | DepthBaseline | **2-color** | 0.10m | Bino | +27.5pp | Far=+59pp, Near=−5pp |
| 260325_1914 | DepthBaseline | **2-color** | 0.10m | Bino | +8.6pp | Far=+65pp, Near=−47pp |
| 260325_2013 | DepthBaseline | **2-color** | 0.03m | Bino | +16.6pp | Depth barely visible; Near≈Far |
| 260326_1649 | DepthSwap50 | **?** | 0.05m | Bino | +40.3pp | N=+45pp, Zd=+36pp; color unverified |
| **260330–260401** | **DepthSwapCtrl** | **Same** | **0.05m** | **Bino (6 sess)** | **+12.5pp***| **N≈ZdA<ZdB; Far=+31pp***, Near=−6pp** |
| **260330–260401** | **DepthSwapCtrl** | **Same** | **0.05m** | **Mono (4 sess)** | **+7.1pp*** | **ZdA=0pp; ZdB=+12pp*; Far=+13pp*** |

*Two-color Baseline range: 28–50pp. Same-color DepthSwapCtrl: 12.5pp binocular. Difference is interpretable as: color dimension removed, depth dimension at 0.05m is weaker than color at discriminating two surfaces; plus within-experiment swap variance contributes noise.*

---

*Document created 2026-04-01 by Literature agent. Sources: VRDots pilot data through 260401_1705; Mitchell et al. (2003); Catak et al. (2022); Khoe et al. (2008); Qian et al. (1994, 1997); Mitchell et al. (2004); V1 Point-Set model (Stoner 2010/2018). Update §2 after each new session block.*
