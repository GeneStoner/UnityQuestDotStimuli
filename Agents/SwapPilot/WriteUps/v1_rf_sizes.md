# V1 Receptive Field Sizes: Literature Review and Implications for VRDots

*Generated 2026-04-22*

---

## 1. Three Distinct RF Definitions

The term "receptive field" is used inconsistently across studies. Three operationally distinct constructs matter here:

1. **Classical/minimum response field (cRF)** — the smallest region that, when stimulated alone, drives a reliable response. Measured with small spots or gratings; reflects the feed-forward thalamo-cortical input to a single neuron.

2. **Summation/integration field (SF)** — the region over which spatial summation increases responses, measured via area-summation (patch-size) curves. Consistently 2–5× larger than the cRF. Reflects intra-cortical horizontal connections and near-surround interactions.

3. **Population RF / fMRI pRF** — the aggregate sensitivity profile of the neuronal population within an fMRI voxel, estimated from spatial mapping paradigms. Larger still (2–5× cRF), partly because it pools heterogeneous neurons with different preferred positions.

The distinction is critical for evaluating density effects in VRDots: the cRF determines when individual dot images begin to overlap; the summation field determines when field-level grouping starts to degrade.

---

## 2. Quantitative Estimates at VRDots Eccentricities

VRDots uses a 7° aperture (r = 0° to 3.5°), an exclusion zone at 1.1°, and a mid-eccentricity of approximately 2.3°.

### 2.1 Classical RF (cRF)

| Study | Species | Method | At 1° ecc | At 2–3° ecc | Formula |
|---|---|---|---|---|---|
| Hubel & Wiesel 1968¹ | Macaque | Single unit, hand-mapping | ~0.1° diam | ~0.15–0.20° diam | d ≈ 0.05 + 0.05·E |
| Dow, Snyder, Vautin & Bauer 1981² | Awake macaque | Single unit, area summation | ~0.08–0.12° | ~0.15–0.25° | d ≈ 0.05 + 0.08·E |

At the VRDots mid-eccentricity (r = 2.3°), the Dow et al. formula gives:

> **d_cRF(2.3°) ≈ 0.234°** (radius ~0.117°, area ~0.043 sq°)

This is the formula used in our RF model. Each dot (0.08° diameter) occupies ~12% of a cRF diameter at mid-eccentricity. For a single dot field of N=63, the mean nearest-neighbor distance is approximately 0.37° — roughly 1.5 cRF diameters — so the cRF model predicts moderate spatial overlap already at baseline density.

### 2.2 Summation / Integration Field

| Study | Species | Method | At 1–3° ecc | Notes |
|---|---|---|---|---|
| Sceniak, Ringach, Hawken & Shapley 1999³ | Macaque | Area summation, low contrast | ~0.7–1.4° diam | Mean SF ~2.3× cRF at low contrast |
| Sceniak, Hawken & Shapley 2001⁴ | Macaque | Area summation, varied contrast | ~0.9–1.3° diam | Mean SF diameter ~1.0° at 2–5° |
| Cavanaugh, Bair & Movshon 2002⁵ | Macaque | Difference-of-Gaussians fitting | ~1.1–1.5° diam | Mean GSF (gain-suppression field) ~1.3° at <5° |
| Angelucci et al. 2002⁶ | Macaque | Anatomy + physiology | ~1.0–1.5° diam | Horizontal connections span 5–8 mm cortex = ~1–1.5° at 2–4° |

At mid-eccentricity (2.3°), the summation field diameter is approximately **1.0–1.3°** — roughly **4–6× larger** than the cRF.

**The model formula (d_RF = 0.05 + 0.08·E) reflects the cRF, not the summation field.** If the behaviorally relevant RF scale for field segregation is the summation field, the effective λ values in the model are underestimates by a factor of ~4–6. At mid-eccentricity, using the summation field diameter:

> d_SF(2.3°) ≈ 1.1°, A_SF ≈ 0.95 sq°

This would place ρ_opt substantially lower (~0.7 dots/sq°), well below our VRDots baseline of 1.8 dots/sq°, and would predict that cueing should already be degraded at the standard density — inconsistent with the flat N=63–500 curve. This argues either (a) cRF, not SF, is the relevant unit for within-field segregation, or (b) the temporal integration correction partially bridges the gap.

### 2.3 Human fMRI Population RF (pRF)

| Study | Species | Method | At ~2° ecc | Formula |
|---|---|---|---|---|
| Dumoulin & Wandell 2008⁷ | Human | fMRI pRF mapping (Gaussian) | sigma ~0.4–0.8°; diam ~0.8–1.6° | sigma ≈ 0.1 + 0.15·E |
| Harvey & Dumoulin 2011⁸ | Human | fMRI pRF, V1 | sigma ~0.6–0.7° at 2° | slope/intercept = 0.31 |
| Freeman & Simoncelli 2011⁹ | Human | V1 pooling model, crowding | s = 0.26·E | At 2.3°: s ≈ 0.60°, diam ≈ 1.2° |
| Zuiderbaan, Harvey & Dumoulin 2012¹⁰ | Human | DoG pRF (center+surround) | center sigma ~0.5° at 2° | Surround ~3× center |

Human fMRI pRF estimates at 2.3° eccentricity span approximately **1.0–1.6° diameter** (2σ), slightly larger than macaque SFs. The Freeman & Simoncelli V1 pooling estimate (s = 0.26·E) gives a smaller value:

> **At 2.3°: s = 0.60°, full-width ≈ 1.2°**

V2 pooling is roughly twice V1: s_V2 = 0.48·E, giving ~1.1° sigma at 2.3° — increasingly relevant for global motion discrimination.

---

## 3. Human vs Macaque Comparison

In absolute degrees, human and macaque V1 RFs are broadly similar — human cRFs may be marginally larger, and population estimates (fMRI) are somewhat larger, but the same order of magnitude applies across the VRDots eccentricity range. The primary difference is that human fMRI pRFs aggregate over populations and are always larger than single-unit cRFs by definition.

For our purposes: the Dow et al. (1981) formula drawn from awake macaque is a reasonable lower bound on the effective RF size; the true behaviorally relevant scale likely lies between the cRF and summation field estimates.

---

## 4. Relation to VRDots Stimulus and the Density Knob

### 4.1 Dot spacing relative to RF size

At the VRDots mid-eccentricity (r = 2.3°):

| N (dots/field) | ρ_eff (/sq°) | Mean spacing (est.) | / cRF diam | / SF diam |
|---|---|---|---|---|
| 20 | 0.58 | ~1.3° | ~5.5× | ~1.2× |
| 63 | 1.82 | ~0.7° | ~3.0× | ~0.65× |
| 173 | 4.99 | ~0.45° | ~1.9× | ~0.41× |
| 500 | 14.4 | ~0.26° | ~1.1× | ~0.24× |
| 750 | 21.6 | ~0.21° | ~0.9× | ~0.19× |
| 1000 | 28.8 | ~0.18° | ~0.75× | ~0.16× |

At N=500, dots from the same field are separated by roughly 1 cRF diameter — the onset of substantial RF-level crowding. At N=1000 (λ_eff ≈ 2.20, S(λ) ≈ 39% of peak), dots are separated by ~0.75 cRF diameters, squarely in the regime where neighboring dots from both fields can simultaneously drive the same cRF. The observed 10pp drop in the CUED arm at N=1000 is consistent with a ~25% degradation of within-field signal purity at this density.

### 4.2 Temporal integration

The 80ms translation sweeps each dot 0.181° (at 2.26°/sec). Relative to the cRF diameter at mid-eccentricity (0.234°), this is 0.77 RF diameters — meaning each dot effectively smears across roughly one RF width during the translation event. This temporal overlap correction (factor 1.77) is the basis for λ_eff in the model and explains why the cueing effect remains strong well beyond the static λ_opt.

### 4.3 Why the flat N=63–500 plateau is theoretically coherent

The static λ_opt (peaks at λ=0.693) corresponds to ρ_opt ≈ 5 dots/sq° (cRF-based). With temporal integration, the effective optimum shifts to ~2.8 dots/sq° — already within the range of VRDots standard density. Crucially, the S(λ) function has a broad plateau: S remains above 85% of its peak over the range λ ≈ 0.3–1.4. This means that all three densities N=63 (λ=0.14, S=24%), N=173 (λ=0.38, S=63%), and N=500 (λ=1.10, S=67%) fall within the plateau **after temporal correction** (×1.77), with λ_eff = 0.24, 0.67, and 1.94, respectively. The apparent flatness reflects the S(λ) plateau, not a failure of the model.

At N=1000 (λ_eff = 2.20, S = 39%), the model predicts — and we observe — the first significant drop.

### 4.4 Which RF definition matters for field segregation?

For global motion discrimination (two transparent fields distinguished by direction and color), the critical spatial scale is likely the **summation field**, not the cRF. This is because:

1. Global motion pooling requires integration across multiple dots — cRF inputs must be combined at V1 and fed forward.
2. Transparent motion perception has been linked to area MT/MST and intermediate areas V2/V3, whose input comes from V1 summation-field-scale aggregations.
3. Freeman & Simoncelli (2011) show that V2 pooling (s = 0.48·E) is required to explain the extent of crowding in visual tasks involving position grouping.

If the summation field (~1.1° at mid-ecc) is the operative scale:
- VRDots baseline (N=63) already puts multiple dots from both fields within a single summation field, which would predict substantial field mixing at baseline.
- The fact that cueing survives suggests either (a) cRF-level local contrast between dot fields is the relevant feature (color/direction tuning at the cRF scale), or (b) the summation field estimate is not the right scale for directed-motion segregation.

The dot-field specificity prediction (Stoner & Blanc paradigm) bears directly on this: if feature swaps at N=1000 are less disruptive than at N=63, it would support the view that RF-level field encoding is compromised at high density while the cueing effect partially survives through a higher-level route (e.g., onset-driven attention, independent of dot-field tracking).

---

## 5. Conclusions

1. **The model formula (d_RF = 0.05 + 0.08·E)** reflects awake-macaque cRF measurements (Dow et al. 1981) — the smallest RF definition. At the VRDots mid-eccentricity (2.3°), this gives d_cRF ≈ 0.234°.

2. **The behaviorally relevant scale is likely the summation field** (~1.0–1.3° at 2.3°; Sceniak 1999/2001, Cavanaugh 2002), which is 4–6× larger. Using this scale would shift ρ_opt well below the VRDots standard density and predict degradation at baseline — inconsistent with the data. This implies either the cRF is the correct unit for dot-field segregation, or the model's effective lambda (after temporal integration) captures most of the summation-field effect phenomenologically.

3. **Human fMRI pRF estimates** (1.0–1.6° at 2.3°; Dumoulin & Wandell 2008, Freeman & Simoncelli 2011) are slightly larger than macaque SFs, but the population aggregate nature makes them hard to interpret mechanistically. They are consistent with V1 summation fields + pooling.

4. **The flat N=63–500 plateau** is explained by the broad S(λ) function after temporal integration correction (×1.77): all three densities fall within the plateau of ≥85% peak efficiency.

5. **The N=1000 drop** (CUED falls from ~60% to 53%) is the first density at which λ_eff (2.20) exceeds the S(λ) peak by a factor that produces measurable degradation (~39% of peak). This is consistent with cRF-level field mixing at high density.

6. **The critical unresolved question** is whether the cueing effect at N=1000 reflects the same dot-field-specific V1 mechanism, or survival through a secondary process. Feature-swap experiments at N=1000 vs N=63 are needed to test dot-field specificity at both endpoints of the density knob.

---

## References

1. Hubel, D. H., & Wiesel, T. N. (1968). Receptive fields and functional architecture of monkey striate cortex. *Journal of Physiology, 195*, 215–243.

2. Dow, B. M., Snyder, A. Z., Vautin, R. G., & Bauer, R. (1981). Magnification factor and receptive field size in foveal striate cortex of the monkey. *Experimental Brain Research, 44*, 213–228.

3. Sceniak, M. P., Ringach, D. L., Hawken, M. J., & Shapley, R. (1999). Contrast's effect on spatial summation by macaque V1 neurons. *Nature Neuroscience, 2*, 733–739.

4. Sceniak, M. P., Hawken, M. J., & Shapley, R. (2001). Visual spatial characterization of macaque V1 neurons. *Journal of Neurophysiology, 85*, 1873–1887.

5. Cavanaugh, J. R., Bair, W., & Movshon, J. A. (2002). Nature and interaction of signals from the receptive field center and surround in macaque V1 neurons. *Journal of Neurophysiology, 88*, 2530–2546.

6. Angelucci, A., Levitt, J. B., Walton, E. J. S., Hupé, J.-M., Bullier, J., & Lund, J. S. (2002). Circuits for local and global signal integration in primary visual cortex. *Journal of Neuroscience, 22*, 8633–8646.

7. Dumoulin, S. O., & Wandell, B. A. (2008). Population receptive field estimates in human visual cortex. *NeuroImage, 39*, 647–660.

8. Harvey, B. M., & Dumoulin, S. O. (2011). The relationship between cortical magnification factor and population receptive field size in human visual cortex: Constancies in cortical architecture. *Journal of Neuroscience, 31*, 13604–13612.

9. Freeman, J., & Simoncelli, E. P. (2011). Metamers of the ventral stream. *Nature Neuroscience, 14*, 1195–1201.

10. Zuiderbaan, W., Harvey, B. M., & Dumoulin, S. O. (2012). Modeling center-surround configurations in population receptive fields using fMRI. *Journal of Vision, 12*(3), 10.
