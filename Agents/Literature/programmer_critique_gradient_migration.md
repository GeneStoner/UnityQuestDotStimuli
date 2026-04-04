# Programmer's Critique: Gradient Migration Hypothesis
*Response to `depth_ior_hypothesis.md` (revised version, 2026-04-02)*
*From the perspective of the stimulus implementation and data collected so far.*

---

## What I find compelling

The "same consolidation process, different attractors" framing is the strongest part. It directly accounts for why the 2D and depth results are not in conflict, and why the SOA was not a mistake — it is simply the interval at which attentional consolidation completes, and the depth gradient determines where consolidation lands. The account is parsimonious: one mechanism (gradient-driven consolidation) explains all four cells without requiring separate suppression or IOR machinery.

The crossover-depth mapping to stereoacuity is specific and falsifiable. It is not just a qualitative story — it makes a quantitative prediction (crossover ≈ stereoacuity threshold for this observer at 2m) that can be tested independently.

---

## Concerns from the stimulus/data side

### 1. The 0.03m Far anomaly undermines the gradient-requires-distinct-planes argument

CUED Far at 0.03m = **91%**, which is *higher* than at 0.05–0.15m (84%). If the gradient only becomes operative once depth planes are perceptually distinct (the explanation for why Near cueing is positive at 0.03m), then Far cueing should also be weak at 0.03m — or at least not *stronger* than at larger separations. The fact that Far cueing is highest at the smallest disparity suggests either:

(a) the Far gradient does not require distinct depth planes to operate — it is always present, even below stereoacuity, and
(b) something about the 0.03m condition specifically boosts CUED Far (e.g., less attentional competition from the Near plane when it is barely distinct)

Option (b) is actually consistent with the gradient account if reframed: when Near is weakly distinct, it does not compete for attention, so Far selection is cleanest. At larger separations Near becomes a competing attractor that fragments attention slightly, capping Far at ~84%. The 91% at 0.03m would then be the "uncontested Far" performance. This is a coherent re-framing but it is not in the current document. It also makes a prediction: Far cueing should be highest when Near is least distinct, and should drop as Near becomes a stronger competing surface. Current data are consistent with this but n=32 is too small to confirm the trend.

### 2. The CUED Far ≈ UNCUED Near gap (84–91% vs 75%) is unresolved

Both cells should — per the migration account — involve detecting Far translation with attention at Far. The gap is attributed to "incomplete migration or temporal uncertainty" but if migration is complete by tStart, neither applies. A cleaner explanation: **migration is stochastic**, not deterministic. On some fraction of UNCUED Near trials, migration has not completed by tStart and the observer detects Far translation with divided or partially Near-focused attention. That fraction decreases with depth separation (stronger gradient → faster migration), which predicts the UNCUED Near–CUED Far gap should shrink at larger depths. Looking at the data:

| Depth | CUED Far | UNCUED Near | Gap |
|-------|----------|-------------|-----|
| 0.03m | 91% | 50% | 41pp |
| 0.05m | 84% | 69% | 15pp |
| 0.10m | 84% | 75% | 9pp |
| 0.15m | 84% | 75% | 9pp |

The gap does shrink with depth and saturates at ~9pp by 0.10m. This is consistent with the stochastic migration account: at large depths, migration is nearly always complete by tStart; the residual 9pp gap is the irreducible cost of having started at Near. This should be made explicit in the hypothesis — it is a testable prediction (the gap should shrink with SOA as well as with depth separation).

### 3. Looming/approach asymmetry is an unaddressed alternative

Dots in the Near plane are moving toward the observer; dots in the Far plane are receding. Crossed disparity + expansion is a well-documented trigger for defensive orienting — rapid, reflexive, operating at ~100ms, and largely independent of voluntary attention. This provides a second account of Near salience that makes a different prediction from the gradient account:

- **Gradient account**: move fixation to Near depth → gradient re-anchors → reversal weakens or disappears
- **Looming account**: move fixation to Near depth → Near dots still approach (crossed disparity still present) → reversal persists

The fixation manipulation (Prediction 2 in the hypothesis) dissociates these. But until that experiment is done, the looming account is equally viable. The current document does not mention it, which leaves a gap a reviewer would notice immediately.

### 4. "Gradient overrides rotation" is asserted, not argued

The account claims ongoing Near rotation is insufficient to hold attention against the gradient, while the 2D rotation succeeds. This is the crux of the mechanism but it is stated without support. The question is: what is the relative "strength" of motion-based attentional sustaining vs. gradient-based pull? Without this, the account cannot predict when the gradient will and will not override motion. It may be that any depth asymmetry — however small — would produce migration given long enough time. If so, even at 0.03m, Near cueing should eventually reverse at longer SOAs. That would mean the 0.03m positive Near cueing is a timing effect, not a threshold effect — which contradicts the stereoacuity-crossover claim. These two parts of the account need to be reconciled.

### 5. n=32/cell — everything is provisional

All four depth conditions have n=32/cell (one session each). The entire theoretical edifice is built on data where individual cells have Wilson 95% CIs spanning ±15–20pp. The 0.03m Near cueing (+12.5pp, n.s.) that is foundational to the "crossover between 0.03 and 0.05m" claim could easily be −5pp or +30pp with one more session. Second sessions at every depth are needed before any of the parametric claims are stable. The crossover location in particular is sensitive to replication — if 0.05m Near cueing turns out to be +5pp in session 2, there is no crossover to locate.

---

## Predictions that could be tested *right now* without new experiments

### Current paradigm, current data

**Heading direction bias by depth plane**: the data currently report accuracy pooled across all 8 headings. It is possible that the Near reversal is concentrated in specific heading directions — e.g., headings with a strong looming component (0° = directly toward observer in the VR setup? depends on heading definition) vs. lateral or recession headings. This does not require new sessions — reanalyze the existing 4 sessions by heading × depth plane. If the reversal is stronger for approach-direction headings, looming is implicated. If it is uniform across headings, the gradient account is better supported.

*(Note to programmer: heading is `TransDeg` in the TSV; `DelayedFieldDepth` gives Near/Far. This is a 5-minute analysis.)*

**Rotation direction as a control**: each session is balanced for rotation CW vs CCW. If the gradient account is correct, rotation direction should not interact with the Near reversal. If there is a CW/CCW × depth interaction, something specific to the rotation dynamics is involved.

---

## Suggested data collection priority before new experiments

1. **Second sessions at each depth** (0.03, 0.05, 0.10, 0.15m, current paradigm) — doubles cell n to 64, confirms or refutes the crossover location and the depth-scaling trends. This is the minimum before any new paradigm makes sense. Single sessions at n=32/cell cannot anchor a theory.

2. **A second observer** at 0.05m and 0.10m (the two depths straddling the crossover). Two observers with n=64/cell at those depths would provide the first cross-observer replication and the most critical stability check. Observer-specific stereo acuity differences could shift the crossover — worth knowing before designing the fine-grained sweep.

3. **Heading × depth re-analysis of existing data** — costs nothing, could be informative immediately.

---

## Summary judgment

The gradient migration account is the best current explanation. It is parsimonious, consistent with the 2D literature, and makes specific falsifiable predictions. The main gaps are: (1) the looming alternative is not addressed; (2) the gradient-requires-distinct-planes argument is in tension with the 0.03m Far anomaly; (3) the "gradient overrides rotation" claim needs mechanistic support; (4) n=32/cell is too small to trust the parametric structure. Points (1) and (3) are theoretical gaps; points (2) and (4) are data gaps that more sessions can address. The SOA manipulation (Prediction 1) is the most powerful single follow-up experiment but should wait until the current paradigm has been replicated at n=64/cell.

---

*Programmer's note, 2026-04-02.*
