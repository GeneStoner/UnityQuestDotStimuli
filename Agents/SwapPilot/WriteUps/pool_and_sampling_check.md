# Is the tiled model's normalization pool, and its sampling of visual space, defensible?

*Generated 2026-08-26. Companion to [v1_rf_sizes.md](v1_rf_sizes.md), which covers RF SIZES.
This covers two things that note does not: the spatial extent of the NORMALIZATION POOL, and the
DENSITY at which we sample visual space.*

The model under test is the tiled scaled-RF HC/PS model (`SurfaceSelectionModel`, branch
`hcps-models-II-III`, `ToyModel/pointset/`): 1473 point-sets in 19 rings over the S&B annulus
(0.396–2.00°), σ(E) = 0.05 + 0.07·E, normalization pool SD = 3.025 × σ_RF.

**Verdicts up front.**

| | verdict |
|---|---|
| **§1 normalization pool** | Absolute extent is inside the measured range. The *ratio* to the driving RF is about **half** the only direct measurement. And the constant was **never fitted** — it is an inherited pixel literal. Defensible for now, not derived. |
| **§2 sampling of visual space** | **Holds up, and better than the project has claimed.** The tiling reproduces cortical **point-image constancy to within 2%** without having been fitted to do so, and lands at about one point-set per ocular-dominance column. |

GS's position, 2026-08-26: **both are acceptable for now**, with the added argument in §1.4 that
part of the measured pool is feedback, which this model does not yet have.

---

## 1. The normalization pool

### 1.1 What the model does

`hcps_v1grid.m:80-89`. The denominator is an isotropic Gaussian over point-set **centres**, each
row with its own extent `nsig_i = normSigRF · σ_i`, `normSigRF = 3.025`, **row-normalized** — so
the denominator is a weighted *mean*, not a sum, and weight that falls where no point-sets exist
is simply never collected.

At the ring-11 example point-set (E = 1.105°):

| | σ / SD | FWHM |
|---|---|---|
| RF | 0.127° | 0.300° |
| pool | 0.385° | 0.907° |

### 1.2 The direct comparison — and we come out at half

[Nassi, Gómez-Laberge, Kreiman & Born 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4039070/)
(*Front Syst Neurosci*) is the only study I found that fits a normalization pool **as such**,
rather than inferring one from surround suppression. Macaque V1, RFs at 2–6° eccentricity. Drive
and normalization extents are fitted as error functions of Gaussian sensitivity profiles,
`f(x) = w·erf(x/2w)`, where a stimulus of diameter `x = w` covers 52% of the Gaussian. Since the
Gaussian is written `exp(−(y/w)²)`, **σ = w/√2**.

| | fitted w | as σ |
|---|---|---|
| drive, w_D | 0.32 ± 0.25° | 0.226° |
| normalization, w_N | **1.96 ± 1.29°** | **1.386°** |
| **ratio** | **6.12** | **6.12** |

**Ours is 3.02.** The absolute extents are closer than that ratio implies, because our RF is
larger than their drive extent:

| eccentricity | our σ_RF | our pool SD | their pool SD | ours / theirs |
|---|---|---|---|---|
| 2° | 0.190° | 0.575° | 1.386° | 0.41 |
| 4° | 0.330° | 0.998° | 1.386° | 0.72 |
| 6° | 0.470° | 1.422° | 1.386° | **1.03** |

So at the top of their recording range we match; at the bottom we are 2.4× too small.

### 1.3 Where we DO agree — and why the literature does not give one number

- [Zuiderbaan, Harvey & Dumoulin 2012](https://jov.arvojournals.org/article.aspx?articleid=2192086):
  difference-of-Gaussians pRFs in human V1, surround/centre **~3×**. We match almost exactly.
- Summation / suppression field **diameters** of **0.7–1.5°** at 1–3° eccentricity
  ([Sceniak et al. 1999](https://www.nature.com/articles/nn0899_733),
  [2001](https://journals.physiology.org/doi/10.1152/jn.2001.85.5.1873);
  [Cavanaugh, Bair & Movshon 2002](https://journals.physiology.org/doi/full/10.1152/jn.00692.2001);
  [Angelucci et al. 2002](https://www.jneurosci.org/content/22/19/8633)). Our pool FWHM runs
  **0.57–1.32°** across the annulus — inside that range.

⚠️ **"Normalization pool", "suppressive surround" and "DoG-pRF surround" are three different
constructs.** Ours matches the DoG convention and the summation-field diameters, and is half the
one direct normalization-pool fit. Which of those is the target decides whether we pass, and the
literature does not settle it.

### 1.4 GS's argument: part of the measured pool is FEEDBACK, which this model lacks

Directionally correct, and Nassi et al. is the paper that shows it — but it accounts for about a
quarter of the discrepancy as published.

- They report that feedback from V2 and V3 "can cover aggregate visual fields five–ten times the
  size of the receptive field center in V1", and that inactivation effects were strongest for
  stimulus diameters **2–8×** the RF centre.
- Inactivating V2/V3 feedback **shrinks** the pool: w_N 1.96° → **1.72°** (p = 0.006), a 12%
  reduction. Their conclusion: feedback's role is to *expand normalization's visuotopic footprint*
  rather than to modulate gain.

| | ratio to drive |
|---|---|
| feedback intact | 6.12 |
| **V2/V3 inactivated** | **5.38** |
| ours | 3.02 |

⚠️ **Removing V2/V3 feedback closes only 24% of the gap.** The argument survives because their
inactivation is *partial* — one retinotopically matched V2/V3 patch, leaving V4, MT and the rest
of V2/V3 intact — so the residual 5.38 still contains feedback of unknown size. But the published
numbers do not close the gap on their own, and we should not claim they do.

⚠️ **The mapping is not clean in the other direction either.** Our model *does* have a
feedback-like term: the attention-modulated cooperative pool feeding the same denominator. So "our
model has no feedback" is true of inter-areal feedback, not of the circuit.

### 1.5 ⛔ The caveat that outweighs the rest

**`normSigRF = 3.025` was never fitted to any of this.** `hcps_op.m:145` derives it from a native
**22-pixel literal** ÷ the 11×11 lattice spacing. Landing inside the literature range is a
**coincidence** and must be reported as one.

- The same 22-px literal was **1.65σ** on the 16×16 harness, so the model has historically run at
  two different extents.
- The 2026-07-25 sweep found `normSig` dominates **both** effect size and pool stability. This is
  a consequential parameter, not bookkeeping.
- Moving to the normalization literature proper would mean roughly **6σ** — never tested on the
  tiled model.

### 1.6 Edge truncation, measured

Because the pool is row-normalized, a point-set near an annulus edge is not *under*-normalized —
it is normalized by a **smaller, more local, radially lopsided** pool. Share of the ideal Gaussian
mass landing where point-set **centres** exist (`hcps_pool_truncation.m`):

| ring | E | pool SD | inside | lost outward | lost inward | n_eff |
|---|---|---|---|---|---|---|
| 1 | 0.42° | 0.241° | 62% | 0% | 38% | 124 |
| 9 | 0.94° | 0.351° | **96%** | — | — | 244 |
| 11 | 1.11° | 0.385° | **96%** | — | — | ~244 |
| 17 | 1.70° | 0.511° | 62% | 37% | 0% | 214 |
| 19 | 1.94° | 0.561° | **44%** | 56% | 0% | 191 |

Containment peaks mid-annulus and falls off symmetrically at both edges. Example figures should
use rings 9–11.

### 1.7 An architectural question we have never articulated: should the pool scale with eccentricity?

Our pool is **constant in RF units** (`nsig_i = normSigRF · σ_i`), so it grows in degrees with
eccentricity — 0.24° at ring 1, 0.56° at ring 19. Nassi et al. report a **single fitted extent**
pooled across 2–6°. To match their effective extent at each eccentricity our constant would have
to be:

| eccentricity | `normSigRF` needed | we run |
|---|---|---|
| 2° | 7.32 | 3.025 |
| 4° | 4.14 | 3.025 |
| 6° | 2.82 | 3.025 |

i.e. a pool roughly constant **in degrees**, not in RF units. Those are different architectural
claims about what normalization is: a fixed cortical neighbourhood (ours) versus a fixed patch of
visual space (theirs, as fitted).

⚠️ **Their data cannot settle this** — one value pooled across the whole eccentricity range, with
scatter of ±1.29° on a mean of 1.96°. So this is NOT a correction. It is a choice sitting
unexamined in `hcps_v1grid.m:84-89`, and the kind of thing a reviewer asks about.
⭐ The argument for ours: a pool constant in RF units keeps every point-set at the same operating
point, which is exactly the reason the code gives for the design. A single px/deg extent would
leave the periphery under-normalized and the fovea over-normalized.

### 1.8 ⚠️ The "half" framing overstates it

`w_N = 1.96 ± 1.29°` — the spread is two-thirds of the mean. On the σ scale, 1.386 ± 0.91. Our
pool at E = 4° is 0.998°, i.e. **0.43 SD below their population mean** — inside their distribution,
not outside it. (Whether 1.29 is an SD or an SEM could not be determined from the table; if SEM
the population is wider still, so the conclusion holds either way.) The 3.02-vs-6.12 comparison is
between point estimates from a measurement without the precision to make it a discrepancy.


---

## 2. Sampling of visual space

### 2.1 What the model does

Measured over all 1473 point-sets:

| quantity | value |
|---|---|
| nearest-neighbour spacing | **0.663 σ** (range 0.657–0.669) |
| neighbour's Gaussian evaluated at my own centre | **0.803** |
| normalized overlap integral of two adjacent RFs | **0.896** |
| spacing as a fraction of RF FWHM | 0.28 |
| coverage — a point falls inside N RFs at 1σ | 7.0 |
| …at FWHM/2 | 9.7 |
| summed Gaussian weighting (flat across the annulus) | 14.2 |

So **adjacent point-sets overlap enormously**: a neighbour is at 80% of peak at my centre.

### 2.2 ⭐ The result that matters — point-image constancy, unfitted

Converting to cortex with [Horton & Hoyt 1991](https://pubmed.ncbi.nlm.nih.gov/1867550/),
M = 17.3/(E + 0.75) mm/deg:

| E | M (mm/deg) | RF FWHM (deg) | **RF FWHM (mm cortex)** | **spacing (mm cortex)** |
|---|---|---|---|---|
| 0.42° | 14.79 | 0.187 | **2.76** | **0.78** |
| 1.10° | 9.33 | 0.300 | **2.80** | **0.79** |
| 1.94° | 6.43 | 0.438 | **2.81** | **0.79** |

**Both constant to under 2% across the whole annulus.** That is *point-image constancy*: the
central result of [Hubel & Wiesel 1974](https://pubmed.ncbi.nlm.nih.gov/4436457/), whose finding
was that RF scatter in a vertical penetration is roughly equal to mean field size, and that field
size and reciprocal magnification rise in parallel so their product is invariant.

⭐ **It was not fitted.** It falls out because σ(E) = 0.05 + 0.07·E is nearly proportional to
1/M(E) = 0.0434 + 0.0578·E — the two differ by a near-constant ~1.17. GS set the RF rule from Dow
et al.; the cortical constancy is a consequence nobody arranged.

### 2.3 Absolute scale

[Harvey & Dumoulin 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC6623292/) define the population
point image as CMF × pRF **σ** and get **3.21 mm** for human V1, near-constant (declining ~0.2
mm/deg over 1.0–5.5°).

On that same definition **ours is 1.19 mm — 2.7× smaller.** That is the expected direction: a pRF
aggregates over many neurons and inherits their positional scatter, so it must exceed any single
unit's RF. Consistent with the project's standing position that our σ sits **2.1–2.2× below human
pRF** and **1.8–1.9× above Dow's cRF radius** — between the two, where a hypercolumn-scale
point-set belongs.

### 2.4 Granularity: about one point-set per ocular-dominance column

Adjacent point-sets are **0.79 mm** apart in cortex, against a human OD column width of **863 μm**
([Adams, Sincich & Horton 2007](https://www.jneurosci.org/content/27/39/10391)). So we place
roughly **one point-set per OD column**, or about **2.2 per full hypercolumn** (an L+R cycle
≈ 1.73 mm).

### 2.5 Is the overlap defensible? Yes

Hubel & Wiesel's scatter result means neighbouring cells' RF centres routinely differ by far less
than one RF diameter. 80%-of-peak overlap between adjacent samples is the physiological norm, not
an artifact of our lattice.

### 2.6 Where it is vulnerable — and why it is probably benign

If a point-set is meant to **be** a hypercolumn, one-per-OD-column oversamples by ~2×. That
inflates `n_eff` and the coverage counts. But it does not change any reported quantity: the
denominator is row-normalized (a weighted *mean*, invariant to density) and the AI is a ratio of
sums (also invariant). The honest consequence is narrower: **"1473 hypercolumns" overstates the
claim by about two.**

---

## 3. What could not be verified

- **Cavanaugh et al. 2002's exact surround/centre ratio.** Both the author PDF and the publisher
  page failed to extract (403 / binary). Those numbers are carried from this project's own
  `v1_rf_sizes.md`, not from a reading of the paper on 2026-08-26.
- **A second independent normalization-pool fit.** I found none that is separable from surround
  suppression, so the 6.12 rests on a single paper.

## 4. Open items carried forward

GS, 2026-08-26: **both are acceptable for now.** Neither is a reason to change a value.

1. **`normSigRF = 3.025` is unfitted** (§1.5) and the pool's eccentricity scaling has never been
   articulated (§1.7). GS: acceptable for now.
2. **Inter-areal feedback is not in the model** (§1.4), and part of the measured pool is feedback.
   Directionally exculpatory; accounts for ~24% of the gap as published. GS: acceptable for now.

### ⭐ QUEUED: `hcps_normsig_sweep` — a test that was prescribed and never run

**Not a sensitivity check. A prediction was written down, the fix was built, and the test was
skipped.**

`logs/2026-07-25.md` already swept the pool width once, on the OLDER lattice at `sigNR = 1`,
WITHOUT the bounded pool:

| normSig | skew | AI |
|---|---|---|
| 0.50σ | 1.0 | +0.003 |
| 1.00σ | 1.8 | +0.101 |
| 1.65σ | 11.1 | +0.237 |
| 3.00σ | 53.5 | +0.330 |
| 5.00σ | 119.4 | +0.377 |

Its verdict: *"No setting in the swept range is both stable and effective ... the model is buying
its effect size from a normalization too weak to stabilise the network — the mechanism and the
runaway are the same knob."* Effect size and pathology rise on ONE dial.

The same entry proposed the fix — bound the cooperative pool, `Lat = CoopL·E/(1 + E/Emax)` — and
said: *"If it works it decouples the two and normalization width becomes a free parameter to set
on evidence."* **The fix WAS built the same day** (`hcps_grid.m:38-43`; the tiled model runs
Emax = 50). **The confirming sweep was never re-run** — no commit since 2026-07-25 mentions one.
We now sit at 3.025, which on the unbounded sweep was skew 53.

**⭐ WIDENED 2026-08-26 (GS): make it 2-D, and measure skew.**

⛔ **An audit found that `skew` has NEVER been computed on the tiled model — not once.** Every
stability script that knows how (`hcps_check_runaway`, `hcps_hotspot_diag`, `hcps_poolsweep`,
`hcps_poolconfirm`, `hcps_walkback`) runs the OLD LATTICE. The only tiled-model stability evidence
is `hcps_taue_sweep`'s pool `n_eff` — 274 of 1473 at τE 20 ms against 479 at 150 ms, concentrated
but nowhere near collapse. That is real, but it is **one 1-D slice through a 5-D space, using a
proxy for the metric the 07-25 log decided was the right one.** We have a point and one line
through it, not a stable *zone*.

**The metrics** (definitions lifted from `hcps_check_runaway.m:19-23`, so old and new numbers stay
comparable):

| | definition | healthy |
|---|---|---|
| **SKEW** | `max(E)/median(E)` across point-sets at a settled frame | **1–3** |
| **GROWTH** | `max(E)` last frame / `max(E)` at frame 12 — still climbing? | ≈1 |
| n_eff | `(ΣE)²/ΣE²` — effective number of point-sets carrying the pool | ≫1 |
| STATIC | `corr(E(t), E(t+6))` | ⚠️ NOT clean — 07-25 corrected itself; a legitimate static envelope from edge geometry contributes. **Skew is the meaningful metric.** |

**The design.**

- **Axis 1** `normSigRF` ∈ {0.5, 1, 1.65, 3.025, 4.5, 6}
- **Axis 2** `CoopL` ∈ {0, 0.1, 0.2, 0.3, 0.4} — 0.20 is the operating point; **CoopL = 0 is the
  control that must give AI exactly 0** (no pool, no route), a free correctness anchor
- **Third condition, as a LINE not a full axis**: `Emax` ∈ {50, Inf} swept along `CoopL = 0.2`
  only. `Emax = Inf` reproduces the pre-fix model exactly (`hcps_grid.m:41-42`), so that one row
  IS the decoupling test, at 6 cells rather than 30.
- 16 layouts per cell ⇒ ~576 model runs; the τE sweep was 112, so budget accordingly.

**Report per cell**: AI no-swap and swap with SE, d′ ratio, SKEW, GROWTH, n_eff.

⚠️ **Compute SKEW twice — globally AND on the well-contained core (rings 9–11).** Edge truncation
is severe on this geometry (§1.6: 96% containment mid-annulus, 44% at ring 19), so E is
systematically depressed at the edges and a perfectly healthy tiled model could read as skewed for
purely geometric reasons. The core figure is the honest one; the global figure is the one
comparable to the old-lattice numbers.

⭐ **Port, do not rewrite.** `hcps_hotspot_diag.m` Part B already runs a 2-D `normMult × sigNR`
sweep reporting skew/static/AI/AI-cold-95%. It just points at `ps_stimulus` / `ps_extract` /
`hcps_grid`. Repointing it at `hcps_vrstim` → `hcps_tile` → `hcps_v1grid` is cheaper than starting
from scratch and keeps the metric definitions identical.

**What the outcomes mean.**
**The decoupling test, as a prediction.** On the old lattice skew and AI rose together
(1.0/+0.003 → 119/+0.377). If `Emax = 50` did its job, the `CoopL = 0.2` line should show
**Emax = Inf → skew climbing with `normSigRF`**, reproducing 07-25, and **Emax = 50 → skew flat**
while AI still varies.

- **Skew now flat while AI still varies** → Emax did its job, the two are decoupled, and pool
  width becomes a parameter we can set on the literature rather than on effect size. `3.025`
  stops being a worry.
- **Skew still climbing with AI** → the headline result is still being bought from an unstable
  normalization, and that outranks everything else on the list.

⛔ **DISCIPLINE, stated before running it**: if the AI rises monotonically with `normSigRF`,
"bigger AI" is **NOT** a justification for moving it. That is exactly the reasoning correctly
rejected for τE, where the stated grounds were agreement with the 2-PS model and the failure of
the stability argument — not effect size.

⚠️ The 07-25 numbers do NOT transfer: different lattice, `sigNR = 1`, no Emax. Only the question
transfers.

## References

Adams, D. L., Sincich, L. C., & Horton, J. C. (2007). Complete pattern of ocular dominance columns
in human primary visual cortex. *Journal of Neuroscience, 27*, 10391–10403.

Angelucci, A., Levitt, J. B., Walton, E. J. S., Hupé, J.-M., Bullier, J., & Lund, J. S. (2002).
Circuits for local and global signal integration in primary visual cortex. *Journal of
Neuroscience, 22*, 8633–8646.

Cavanaugh, J. R., Bair, W., & Movshon, J. A. (2002). Nature and interaction of signals from the
receptive field center and surround in macaque V1 neurons. *Journal of Neurophysiology, 88*,
2530–2546.

Dow, B. M., Snyder, A. Z., Vautin, R. G., & Bauer, R. (1981). Magnification factor and receptive
field size in foveal striate cortex of the monkey. *Experimental Brain Research, 44*, 213–228.

Harvey, B. M., & Dumoulin, S. O. (2011). The relationship between cortical magnification factor
and population receptive field size in human visual cortex: constancies in cortical architecture.
*Journal of Neuroscience, 31*, 13604–13612.

Horton, J. C., & Hoyt, W. F. (1991). The representation of the visual field in human striate
cortex. *Archives of Ophthalmology, 109*, 816–824.

Hubel, D. H., & Wiesel, T. N. (1974). Uniformity of monkey striate cortex: a parallel relationship
between field size, scatter, and magnification factor. *Journal of Comparative Neurology, 158*,
295–305.

Nassi, J. J., Gómez-Laberge, C., Kreiman, G., & Born, R. T. (2014). Corticocortical feedback
increases the spatial extent of normalization. *Frontiers in Systems Neuroscience, 8*, 105.

Sceniak, M. P., Ringach, D. L., Hawken, M. J., & Shapley, R. (1999). Contrast's effect on spatial
summation by macaque V1 neurons. *Nature Neuroscience, 2*, 733–739.

Sceniak, M. P., Hawken, M. J., & Shapley, R. (2001). Visual spatial characterization of macaque V1
neurons. *Journal of Neurophysiology, 85*, 1873–1887.

Zuiderbaan, W., Harvey, B. M., & Dumoulin, S. O. (2012). Modeling center–surround configurations
in population receptive fields using fMRI. *Journal of Vision, 12*(3), 10.
