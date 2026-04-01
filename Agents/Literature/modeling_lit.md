# VRDots Modeling Literature
**Version**: 0.1 — Initial pass
**Date**: 2026-03-31

This document tracks computational and theoretical models relevant to VRDots. For each model: citation, core mechanism (2–3 sentences), and VRDots relevance (specifically: does the model predict dot cueing, depth-field cueing, or the ZdB enhancement?).

---

## 1. Motion Coherence / MT Models

### 1.1 Simoncelli & Heeger (1998) — Two-Stage MT Energy Model

**Simoncelli, E.P., & Heeger, D.J. (1998). A model of neuronal responses in visual area MT. *Vision Research*, 38(5), 743–761.**

**Core mechanism**: A two-stage feedforward model (V1 → MT). V1 neurons perform oriented spatiotemporal filtering (motion energy), producing direction- and speed-tuned responses. MT neurons pool V1 inputs with specific weights to achieve velocity (speed + direction) selectivity. Both stages apply divisive normalization: each neuron's response is divided by the summed squared activity of a pool of neighboring neurons tuned to nearby orientations, directions, and spatial frequencies. Normalization controls gain and produces contrast saturation, direction opponency, and speed tuning.

**VRDots relevance**: In a two-surface transparent display (VRDots' rotating + translating fields), V1 encodes both motion directions simultaneously; MT must represent both. The normalization pool in MT is direction-broad, so the two surfaces compete through mutual suppression. This model does not explicitly predict dot cueing (which requires attention or surface-identity mechanisms not in the model), but it predicts that ZdB's removal of the distractor from the cued depth plane should reduce the normalization pressure on the cued surface's MT representation — a mechanistic substrate for ZdB enhancement. The model does not natively incorporate disparity, so depth-field cueing requires extension.

---

### 1.2 Weiss, Simoncelli & Adelson (2002) — Bayesian Motion Estimation

**Weiss, Y., Simoncelli, E.P., & Adelson, E.H. (2002). Motion illusions as optimal percepts. *Nature Neuroscience*, 5(6), 598–604.**

**Core mechanism**: A Bayesian observer model of local velocity estimation. The likelihood of a velocity given the image is derived from a Gaussian noise model on image measurements; the prior favors slow speeds (velocities near zero are more probable a priori). The posterior estimate is the MAP velocity. Under high noise or low contrast, the prior dominates and velocities are biased toward zero (slow-speed bias). This accounts for a wide range of motion illusions (oblique grating speed underestimation, plaid coherence phenomena) as rational inference under uncertainty.

**VRDots relevance**: The slow-speed prior predicts that both VRDots surfaces (which move at similar angular speeds) are subject to similar prior compression, so the prior alone does not differentiate CUED from UNCUED performance. Dot cueing requires a surface-identity mechanism (which surface is attended) that is outside this model's scope. The model does not predict depth-field cueing or ZdB enhancement. However, it is relevant to interpreting the 80ms translation duration: a slow-speed prior would slightly bias perceived translation speed toward zero, which could affect direction discrimination difficulty but should not interact with the cueing manipulation. Worth noting if VRDots directional thresholds are ever measured as a function of depth plane.

---

### 1.3 Qian, Andersen & Adelson (1994) — Transparent Motion as Locally Unbalanced Signals

**Qian, N., Andersen, R.A., & Adelson, E.H. (1994). Transparent motion perception as detection of unbalanced motion signals. *Journal of Neuroscience*, 14(12), 7357–7380 (three-part series: Psychophysics, Physiology, Modeling).**

**Core mechanism**: Transparent motion perception requires locally unbalanced motion signals. When two motion directions are precisely balanced in every local region (e.g., by pairing each leftward-moving dot with a nearby rightward-moving dot), transparency fails and the display appears as a single flickering surface. Transparency is perceived when the opposing signals are spatially unbalanced, or unbalanced in disparity or spatial frequency. The model proposes that local opponent-motion detectors suppress balanced bidirectional signals, leaving unbalanced signals as the substrate for transparent surface representation.

**VRDots relevance**: This is the most directly relevant computational model for the core VRDots stimulus. The two rotating dot fields create locally unbalanced motion signals (different directions, non-overlapping in direction space), enabling transparent surface perception. Critically, Qian et al. show that disparity imbalance is an additional source of transparency support: if the two surfaces differ in depth, opponent-motion suppression is relaxed even when motion directions are partially balanced. This predicts that depth-plane separation in VRDots should strengthen the two-surface percept — providing a mechanistic prediction for depth-field cueing. ZdA (cued dot changes depth plane) would reduce the depth-plane imbalance that supports the cued surface as a distinct unit, consistent with the observed cueing attenuation.

---

## 2. Normalization Models of Attention

### 2.0 Reynolds & Heeger (2009) — The Normalization Model of Attention

**Reynolds, J.H., & Heeger, D.J. (2009). The normalization model of attention. *Neuron*, 61(2), 168–185.**

**Core mechanism**: Extends divisive normalization to include an attention field. The response of each neuron is:

```
R = (E × A) / (σ + S)
```

where **E** is the stimulus drive (excitatory input tuned to the neuron's preferred features), **A** is the attention field (a Gaussian over space and/or feature space, representing the spread of the attentional enhancement), and **S** is the suppressive drive (normalization pool — computed by convolving the attention-weighted stimulus drive across a broader suppressive field). σ is a semi-saturation constant.

The critical insight is that the form of attentional modulation — **response gain** (multiplicative scaling of the maximum response) vs. **contrast gain** (leftward shift of the contrast response function) — depends on the relative size of the attention field versus the stimulus. When the attention field is **narrow** relative to the stimulus (or there is only one stimulus), attention produces response gain. When the attention field is **broad** and encompasses multiple competing stimuli, attention produces contrast gain (because the suppressive drive is also boosted). The model reconciles the long-standing response gain vs. contrast gain debate by showing both emerge from the same normalization operation under different stimulus/attention field configurations.

**VRDots relevance — dot cueing**: The delayed onset creates an asymmetry in the attention field. The exogenous cue (onset translation) drives the attention field to be concentrated near the cued surface's motion direction. This boosts E for the cued direction while the suppressive drive S (which pools across directions) is less selectively enhanced — net effect is response gain for the cued surface in MT. This is the normalization-model account of the basic dot cueing effect.

**VRDots relevance — why normalization alone fails**: In the transparent-motion display, both surfaces occupy identical spatial locations. If the attention field is spatially defined (as in Reynolds & Heeger's standard formulation), it cannot differentially boost one surface over the other based on spatial location alone. The model requires either a feature-tuned attention field (tuned to the cued surface's direction) or a spatially fine-grained signal (at the dot level, below MT RF size) to break the symmetry between surfaces. This is exactly the gap that the V1 Point-Set model (§6 below) fills — it provides the fine-grained spatial signal that feeds into the normalization computation.

**VRDots relevance — ZdB enhancement**: If the normalization pool in MT is partially depth-tuned (consistent with MT's weak disparity selectivity), then ZdB's movement of the distractor to a new depth plane briefly removes it from the normalization pool for the cued surface's depth stratum. This transiently reduces S while E × A is unchanged → response gain boost for the cued surface at target onset.

---

### 2.1 Lee & Maunsell (2009) — Normalization Model with Feature-Similarity Gain

**Lee, J., & Maunsell, J.H.R. (2009). A normalization model of attentional modulation of single unit responses. *PLOS One*, 4(2), e4651.**

**Core mechanism**: Combines Heeger's (1992) divisive normalization with Treue & Martinez-Trujillo's (1999) feature-similarity gain principle. The response of a direction-tuned neuron is:

```
               g(θ, θ_att) · E(θ)
R(θ)  =  ─────────────────────────────────────
          σ  +  Σ_φ  [ g(φ, θ_att) · E(φ) ]

  θ          = neuron's preferred direction
  θ_att      = attended direction
  E(θ)       = excitatory drive at θ (stimulus input)
  g(θ,θ_att) = feature-similarity gain:
               peaks at θ = θ_att, falls off with |Δθ|
  σ          = semi-saturation constant
  Σ over φ   = normalization pool (summed over all direction channels)
```

The feature-similarity gain g modulates *both* numerator and denominator. This produces a **double effect** when attending direction θ_att:

```
  Numerator:    g HIGH for cells near θ_att   →  excitation boosted  ↑
  Denominator:  g LOW  for cells near θ_att⊥  →  opponent suppression reduced  ↓

  Net:  attended direction → response UP ↑↑
        opponent direction → response DOWN ↓↓  (below unattended baseline)
```

Tested on MT neurons with two competing dots in the RF — the closest published analog to the VRDots transparent-motion stimulus. The model fits single-unit data without additional free parameters beyond the gain function shape.

**VRDots relevance**: In the transparent-motion display, MT neurons are simultaneously driven by two directions. The model predicts attending to the cued surface's direction boosts the numerator for neurons preferring that direction while reducing the normalization weight of neurons preferring the distractor direction — doubly suppressing the distractor. This is a stronger prediction than Reynolds & Heeger alone: it predicts both cued-surface enhancement AND below-baseline distractor-surface suppression. A testable consequence: UNCUED accuracy should fall *below* a neutral (no-cue) baseline, not just below CUED. The model is tested in MT, which is directly the area processing VRDots' translational motion signals.

---

### 2.2 Carandini & Heeger (2012) — Normalization as Canonical Neural Computation

**Carandini, M., & Heeger, D.J. (2012). Normalization as a canonical neural computation. *Nature Reviews Neuroscience*, 13(1), 51–62.**

**Core mechanism**: Divisive normalization is proposed as a canonical cortical computation: each neuron's response is divided by its own activity plus the summed (squared) activity of a pool of neighboring neurons. The normalization pool can be defined over spatial, orientation, or feature space depending on brain area. Normalization is implemented across visual cortex (V1–MT), olfactory cortex, prefrontal cortex, and multisensory areas, and accounts for phenomena including contrast gain control, cross-orientation suppression, attention effects, and multisensory integration. Attention modulates normalization by changing the gain or pool weighting.

**VRDots relevance**: Normalization provides a mechanistic framework for the ZdB enhancement. In the N (no-swap) condition, both depth planes are continuously occupied; the MT representation of the cued surface's translation is normalized by (suppressed by) ongoing activity from the distractor surface. In ZdB, the distractor moves to a new depth plane at target onset — if normalization pools are partially depth-tuned (consistent with MT's weak disparity selectivity), the distractor surface briefly loses its normalization influence on the cued surface, effectively boosting the cued surface's MT gain at the moment of the target translation. This is a parsimonious normalization account of ZdB enhancement that does not require invoking surface identity per se. It does not predict dot cueing (which requires an attention-bias mechanism) but could be combined with a biased-competition account (Section 3.1) for a unified model.

---

### 2.3 Doostani, Hossein-Zadeh & Vaziri-Pashkam (2023) — Normalization Predicts Human Visual Cortex Responses During Object-Based Attention

**Doostani, N., Hossein-Zadeh, G.-A., & Vaziri-Pashkam, M. (2023). The normalization model predicts responses in the human visual cortex during object-based attention. *eLife*, 12, e75726. https://doi.org/10.7554/eLife.75726**

**Core mechanism**: Divisive normalization — R = E / (σ + S), where the response to a compound stimulus is the weighted excitatory drive divided by a semi-saturation constant plus a normalization pool term — is tested against two simpler alternatives (weighted sum and weighted average) to explain fMRI responses when two objects are presented simultaneously. The study measures BOLD in five ROIs (V1, LO, pFs, EBA, PPA) while participants view isolated bodies, isolated houses, or superimposed body+house pairs, with attention directed to one object or maintained at fixation (via a color-detection task). Three computational models compete: *weighted sum* (responses to compound = sum of individual responses), *weighted average* (compound = average of individuals), and *normalization* (compound = weighted excitatory drive normalized by pooled suppressive drive). The normalization model fits best across all areas and all attention conditions.

**Key findings**: (1) Normalization outperforms both alternatives across the visual hierarchy, from V1 through higher-level object areas. (2) Attention modulates the normalization: directing attention to one object selectively amplifies the excitatory drive for that object while the normalization pool (which reflects both objects) suppresses the response to the unattended object below what would be expected from normalization alone. (3) The model is tested with human fMRI (not monkey electrophysiology), extending Reynolds & Heeger (2009) and Lee & Maunsell (2009) to the human brain and to the object-level domain. (4) Results hold both for spatially overlapping objects (compound stimuli at the same location) and for separately attended vs. ignored stimuli — the attention condition is object-based, not purely spatial.

**VRDots relevance**: This is the most direct human neuroimaging validation of the normalization account of object-based attention. The VRDots displays — two transparent dot fields occupying the same spatial region — are formally analogous to the superimposed body+house compound stimuli, except the objects are motion-defined surfaces rather than categorical objects, and the relevant brain areas are V1 and MT rather than EBA/PPA. The key prediction the Doostani et al. model makes for VRDots: when the cued surface is attended, its excitatory drive (E) is amplified, while the normalization pool (S) — which includes both surfaces — partially suppresses the distractor surface's representation. This is the mechanistic basis of the dot cueing effect. The ZdB enhancement has a direct analog: in ZdB, moving the distractor to a new depth plane at target onset would transiently reduce its contribution to S (if normalization pools have any depth-plane specificity), increasing the cued surface's net response exactly at target onset. The finding that normalization holds even at V1 (not just in higher-level object areas) is especially important for the V1 Point-Set model (§6): if normalization operates at V1 spatial scales, then fine-grained object-based selection at the dot level (via Point-Sets) could directly modulate the normalization computation that the Doostani et al. model describes.

**Note on citation year**: The paper is listed in eLife as article e75726; the published version carries a 2023 date. It has been listed in paper_list.md as "eLife 2022" based on its DOI submission date; update references to 2023 as the publication year.

---

## 3. Object-Based Attention / Biased Competition Models

### 3.1 Desimone & Duncan (1995) — Biased Competition

**Desimone, R., & Duncan, J. (1995). Neural mechanisms of selective visual attention. *Annual Review of Neuroscience*, 18, 193–222.**

**Core mechanism**: Stimuli in the visual field compete for representation in visual cortex. Competition is implemented through mutual suppression among neurons with overlapping receptive fields (consistent with normalization). The competition is biased by two sources: top-down attention (which increases gain for the attended stimulus) and bottom-up salience (which increases gain for salient onsets). The winning stimulus receives enhanced cortical representation; the losing stimulus is suppressed below its unattended baseline. This biased competition framework accounts for attention effects in V4 and IT, where responses to the attended stimulus in a pair are enhanced and responses to the unattended stimulus are suppressed.

**VRDots relevance**: This is the foundational framework for dot cueing in VRDots. The onset translation of one surface is a bottom-up salience signal that biases competition in favor of that surface — the cued surface wins the competition, receives enhanced representation, and the second translation (target) in that surface is therefore detected more accurately (CUED advantage). The UNCUED condition requires the observer to switch attention to the losing surface — a capacity-limited, time-consuming operation consistent with Pinilla et al.'s ~500ms interference cost. ZdB can be framed within biased competition: in ZdB, the distractor surface's abrupt depth-plane change at target onset is a second bottom-up event that, rather than drawing attention away from the cued surface, actually serves as evidence that the distractor is "elsewhere" — briefly withdrawing it from competition with the cued surface and boosting the cued surface's representation above its N-condition level. This gives a biased-competition account of ZdB enhancement without requiring a separate normalization model.

---

## 4. Depth-Plane Segmentation Models

### 4.1 Qian & Andersen (1997) — Motion-Stereo Integration in V1/MT

**Qian, N., & Andersen, R.A. (1997). A physiological model for motion-stereo integration and a unified explanation of Pulfrich-like phenomena. *Vision Research*, 37(12), 1683–1698.**

**Core mechanism**: V1 binocular simple cells that are jointly tuned for direction and disparity form the substrate for motion-stereo integration. Cells with the same preferred direction but different disparity preferences respond to surfaces at different depth planes moving in the same direction; cells with matched direction+disparity tuning respond to specific depth-plane + motion combinations. MT pools these V1 inputs and can therefore be simultaneously tuned for velocity and depth plane. This model predicts that adding disparity separation between two transparent surfaces increases the distinctness of their MT representations.

**VRDots relevance**: This model predicts depth-field cueing: surfaces in distinct depth planes are represented by distinct, non-overlapping populations of MT neurons (those jointly tuned for the appropriate direction + disparity combination). The MT representation of the cued surface is therefore more separable from the distractor when depth-plane separation is added — the cued surface's "MT channel" is more distinctive. ZdA disrupts this by moving the cued dot group out of its home depth-plane channel at target onset; ZdB enhances it by moving the distractor out of the cued-surface channel. This model provides the most direct mechanistic bridge between VRDots' depth-plane manipulation and the behavioral cueing effects.

---

### 4.2 MT Population Anisotropy — Near vs. Far Disparity Representation

**Presumed: Maunsell & Van Essen (1983) / DeAngelis & Uka (2003) (see also PubMed ID 21068268 — "Population anisotropy in area MT explains a perceptual difference between near and far disparity motion segmentation").**

**Core mechanism**: MT contains neurons tuned to near (crossed) and far (uncrossed) disparities, but the distribution may not be uniform — a population anisotropy. If MT has more cells tuned to near disparities or if near-tuned cells have stronger responses, then depth segmentation should be stronger for near-plane stimuli. Conversely, if far-tuned cells are sparser or weaker, the far-plane surface may be represented by a smaller, more selective population, which could paradoxically produce sharper tuning and thus better surface selectivity for the far surface.

**VRDots relevance**: This is the best available mechanistic candidate for the Far > Near cueing asymmetry observed in VRDots (binocular: Far = +47.9pp***, Near = +20.8pp* in DepthSwapCtrl sessions). If MT's far-disparity population is smaller but more sharply tuned, the Far surface's MT representation is more distinct from the Near surface's representation, boosting depth-field cueing specifically for Far trials. The monocular collapse of the Far > Near asymmetry (Factor 3 is entirely stereoscopic) is consistent with this mechanism: without disparity, MT can no longer differentiate by depth plane, and the anisotropy is invisible. **High priority: retrieve PubMed ID 21068268 to verify this account.**

---

## 6. The V1 Point-Set Model (Stoner 2010/2018; Stoner & Blanc 2010)

**Primary sources**:
- Stoner, G.R., & Blanc, G. (2010). Exploring the mechanisms underlying surface-based stimulus selection. *Vision Research*, 50(2), 229–241. [§1.3 for model motivation]
- Stoner, G.R. (2010/2018). Area V1 "point-set" as the unit of "object-based" selection. Program No. 172.13. 2018 Neuroscience Meeting Planner. Society for Neuroscience. ⚠️ *Citation as it appears in Catak et al. (2022) reference list — year discrepancy between inline (2010) and meeting year (2018); may be a 2018 SfN abstract. Verify.*)
- Catak, Özkan, Kafaligonul & Stoner (2022, *Cortex* 151:89) §4.2, §4.7 — most explicit published description.

---

### 6.1 Motivation: Why MT/MST Cannot Account for Dot-Field Specificity

MT and MST receptive fields are large (~5–20° diameter), far exceeding the spacing between intermixed dots of the two transparent dot fields (~0.05° dot diameter, 5 dots/deg²). A neuron in MT therefore has both surfaces simultaneously in its RF on virtually every trial. It cannot distinguish which dots belong to which surface based on spatial location alone. Any normalization/competition account operating exclusively at the MT level (e.g., motion-duration confound, directional adaptation) would predict effects based on *which direction* competes more strongly — not on *which spatially intermixed dots* belong to which surface.

**Stoner & Blanc (2010) showed this prediction fails**: reversing the motion-duration asymmetry (the key prediction of normalization-only accounts) did not reverse the cueing effect. The cueing effect is dot-field specific — it tracks which dots (sub-population) moved, not which direction had a processing advantage.

**Implication**: The selection mechanism must operate at a spatial scale fine enough to resolve individual dots. Area V1 satisfies this: V1 receptive fields are small enough (~0.05–0.3° in the foveal/parafoveal region) to contain mostly dots from one surface or the other at any given moment.

---

### 6.2 The Model: V1 Hypercolumn Point-Sets with Cooperative Excitatory Connections

**Unit of selection: the Point-Set**

A **Point-Set** is the set of V1 neurons whose receptive fields are co-located (same retinotopic location) and share the same direction-of-motion preference (i.e., they belong to the same direction column within the V1 hypercolumn at that retinotopic location). Each V1 hypercolumn contains direction columns spanning the full 360°; two of these columns correspond to the preferred directions of the two transparent surfaces (e.g., CW and CCW rotation).

**Architecture:**

```
 ═══════════════════════════════════════════════════════════
  GLOBAL LEVEL  (MT/MST, large RFs ~5–20°)
 ═══════════════════════════════════════════════════════════

  Onset translation of surface A  →  MT response for direction θ_A
       │
       │  feature-similarity gain broadcast  (Treue & MTT 1999 style)
       │  non-linear; direction-specific; whole-display
       ▼
  Gain field G_A:  multiplies all V1 neurons preferring θ_A
                   across the entire display

 ───────────────────────────────────────────────────────────
  LOCAL LEVEL  (V1, RFs ~0.05–0.3° foveal)
 ═══════════════════════════════════════════════════════════

  At each retinotopic location (x, y):

  ┌─ hypercolumn (x,y) ──────────────────────────────────┐
  │                                                       │
  │   Direction col θ_A          Direction col θ_B        │
  │   ┌───────────────────┐      ┌───────────────────┐    │
  │   │  n1 ⇄ n2 ⇄ n3    │      │  m1 ⇄ m2 ⇄ m3    │    │
  │   │  recurrent excit. │      │  recurrent excit. │    │
  │   │  within column    │      │  within column    │    │
  │   └───────────────────┘      └───────────────────┘    │
  │          ▲                           ▲                 │
  │      dot from A in RF            dot from B in RF      │
  │                                                        │
  │     NO cross-column excitatory connections             │
  └────────────────────────────────────────────────────────┘

  The POINT-SET for surface A =
    { all V1 neurons: RF at any (x,y) AND preferred direction θ_A }
    — distributed across the display, united by direction tuning
```

**How attention propagates through the model (step by step):**

```
1. Exogenous onset: surface A translates briefly
        │
        ▼
2. MT/MST detects direction θ_A transient
        │
        ▼
3. Global feature-similarity gain G_A broadcast back to V1
   → ALL V1 neurons preferring θ_A get a non-linear gain boost
   (this is the global, feature-based, non-linear enhancement component)
        │
        ▼
4. At each (x,y) where a surface-A dot currently sits:
   → V1 column θ_A activated by dot input AND boosted by G_A
   → Recurrent excitatory connections within θ_A column amplify
   → This location's θ_A column "wins" locally against θ_B column
        │
        ▼
5. Amplified V1 signal for surface A feeds forward to MT
   → MT now receives a fine-grained, DOT-SPECIFIC surface-A advantage
     (not just a direction advantage — actual dot spatial identity)
        │
        ▼
6. At MT, normalization (Lee & Maunsell / Reynolds & Heeger) amplifies:
   → Enhanced A input × reduced B normalization weight
   → Surface A's subsequent translation detected more accurately
```

**Mechanism: recursive excitatory (cooperative) connections within the hypercolumn**

Neurons within the same direction column at the same retinotopic location are linked by **recurrent excitatory connections**. These connections are:
- **Within-column**: linking neurons tuned to the same direction
- **Spatially local**: within the hypercolumn (same retinotopic point)
- **Recursive**: the excitation recirculates, implementing a form of within-surface signal amplification

Critically, the connections are **direction-specific within the hypercolumn**: CW-tuned neurons excite each other but do not excite CCW-tuned neurons at the same location. This provides surface specificity without requiring a high-level object representation.

**Why this is "object-based" without a high-level object representation**

The model achieves surface-specificity using only:
1. The fine-grained spatial structure of V1 (RFs small enough to resolve individual dots)
2. Direction tuning (which direction column a neuron belongs to)
3. Local recurrent excitation (no need to first identify which features belong to which object)

Selection operates **before** the feature dimensions are fully segregated in higher-order areas. The grouping IS the selection, implemented in V1's retinotopic architecture — this sidesteps the classic binding problem.

**Extension to multiple feature dimensions**

The model extends naturally to hypercolumns tuned to additional feature dimensions (color, depth/disparity). A single dot co-activates the direction, color, and depth columns at its retinotopic location simultaneously. Recurrent excitation within each column (and coupling between co-active columns for the same dot) allows the attentional bias to spread across feature dimensions:

```
  ┌─ hypercolumn (x,y) — surface A dot present ──────────┐
  │                                                       │
  │  Direction col θ_A   Color col C_A   Depth col D_A   │
  │  ┌──────────────┐   ┌──────────────┐ ┌────────────┐  │
  │  │  recurrent ↺ │   │  recurrent ↺ │ │ recurrent↺ │  │
  │  └──────┬───────┘   └──────┬───────┘ └─────┬──────┘  │
  │         └──── within-surface coupling ──────┘         │
  │         (co-active columns for same dot linked)        │
  └────────────────────────────────────────────────────────┘
```

Attending to surface A's motion direction automatically boosts:
- Color representation of surface A (→ Schoenfeld et al. 2003 PNAS, ~150ms)
- Depth-plane signal for surface A (→ depth-field cueing in VRDots)
- Sequential feature cascade as signal propagates forward (→ Schoenfeld et al. 2014 Nat Neurosci, ~60ms gap between modules)

**Two-component summary:**

```
Total selection signal  =
  [Local: recurrent excitation within V1 direction columns]
        ×
  [Global: non-linear feature-similarity gain from MT/MST back-projection]
```

The global component provides broad direction-tuned gain; the local component imposes dot-level spatial specificity on that gain. Neither alone is sufficient: global alone cannot distinguish intermixed dots; local alone lacks the gain magnitude to produce robust behavioral effects.

---

### 6.3 What the Model Predicts for VRDots

| VRDots Result | Point-Set Prediction |
|---------------|---------------------|
| Dot cueing (+19.8pp binocular) | ✓ Exogenous translation boosts V1 point-set for cued direction; recurrent excitation amplifies signal; survives to translation judgment |
| Cueing survives feature swaps (Catak 2022) | ✓ Selection is by dot spatial identity, not feature value; swapping features doesn't dissolve the point-set |
| N1 ERP at occipital/parieto-occipital sites | ✓ Consistent with V1/V2 or MT+ involvement; model predicts early cortical modulation |
| Depth-field cueing (+12.5pp binocular) | **Predicted by extension**: if V1 hypercolumns include depth (disparity) columns, point-sets can incorporate depth-plane membership — dots in the same depth plane share a disparity-column point-set, adding to the within-surface coherence signal |
| ZdA attenuation | **Predicted**: cued dot group changes depth column at tStart → disrupts the depth-plane point-set for the cued surface at the moment of target evaluation |
| ZdB enhancement | **Predicted**: distractor dot group changes depth column → the distractor's depth-plane point-set becomes incoherent, reducing its competitive excitation relative to the cued surface |
| Far > Near asymmetry | **Not directly predicted**: would require asymmetry in V1 disparity column density or coupling strength for near vs. far disparities |

---

### 6.4 Relation to Normalization Models

The V1 Point-Set model and normalization models (Reynolds & Heeger 2009; Lee & Maunsell 2009) are **complementary, not competing**:

- **Normalization** operates at MT: determines gain of the directional motion signal as a function of competition between the two surface directions and the attentional field. Explains response gain, contrast gain, and ZdB effects through changes in the normalization pool.

- **V1 Point-Sets** operate upstream: determine *which* directional signal receives the attentional boost that feeds into the MT normalization. The point-set mechanism is what makes the attentional field "surface-specific" rather than "direction-specific" or "spatially broad."

A complete account of VRDots requires both: V1 point-sets provide the fine-grained surface identity signal; MT normalization amplifies that signal and propagates it to the behavioral judgment. Neither model alone is sufficient:
- Normalization alone: cannot explain dot-field specificity (Stoner & Blanc 2010 disproof)
- V1 point-sets alone: need a gain mechanism to explain the magnitude of behavioral effects and their dependence on attention field width

---

## 7. Models vs. Surface- and Object-Based Effects

How each attention model accounts for the key empirical results in the transparent-motion and VRDots paradigms. ✓ = predicted, ✗ = fails or not predicted, — = outside model scope.

| Effect | Biased Competition (D&D 1995) | Reynolds & Heeger (2009) | Lee & Maunsell (2009) | Stoner Point-Set |
|--------|:-----------------------------:|:------------------------:|:---------------------:|:----------------:|
| **Basic cueing (CUED > UNCUED)** | ✓ onset = salience bias | ✓ onset concentrates attention field | ✓ g boosts cued direction ↑↑ | ✓ G_A × recurrent excitation |
| **Feature swap survives cueing** (Catak 2022; Stoner & Blanc 2010) | ambiguous | ✗ attention field is feature-indexed | ✗ g is direction-indexed | **✓ only** — selection by dot spatial identity, not feature value |
| **Duration confound fails** (Stoner & Blanc 2010) | — | ✗ predicts reversal | ✗ predicts reversal | **✓** — recurrent excitation not duration-dependent |
| **Feature spreading to color** (Schoenfeld 2003) | partial (integrated competition) | ✗ | ✗ | ✓ color column coupling within hypercolumn |
| **Sequential feature cascade ~60ms** (Schoenfeld 2014) | — | — | — | ✓ signal propagates forward through feature modules |
| **UNCUED below baseline** | ✓ (loser suppressed) | partial | **✓ explicit** — opponent direction suppressed below baseline | ✓ recurrent excitation for B column reduced |
| **Depth-field cueing** (VRDots Factor 2) | — | — | — | ✓ (disparity column extension) |
| **ZdA attenuation** | — | ✓ normalization pool disrupted | ✓ | ✓ cued surface depth-column incoherent at target onset |
| **ZdB enhancement** | ✓ distractor withdraws from competition | ✓ S reduced for cued surface | ✓ | ✓ distractor depth-column incoherent → reduced competitive excitation |
| **Far > Near asymmetry** (VRDots Factor 3) | — | — | — | ✗ not predicted; needs MT disparity anisotropy (§4.2) |
| **Cross-surface attentional blink** (Rodríguez 2006) | ✓ | ✓ direction-B suppressed | ✓ | ✓ downstream of point-set dominance |

**Key discriminating results**: Feature-swap survival and duration-confound failure are the empirical signatures of the Point-Set model. No other attention model listed here predicts either. Both require that selection track dot spatial identity, not feature value — which normalization and biased-competition models do not implement.

**Testable signature of Lee & Maunsell not yet checked in VRDots**: The model predicts UNCUED accuracy falls *below* an unbiased (no-cue) baseline, not just below CUED. If neutral-cue or no-cue baselines exist in VRDots sessions, this should be tested.

---

## 5. Models Not Yet Covered / Recommended Next

- **Treue & Martinez-Trujillo (1999)** *Nature* — Feature-similarity gain: attention to a motion direction boosts gain for all neurons tuned to that direction, not just those with overlapping receptive fields. Predicts that the translational cue in VRDots boosts gain for the entire cued surface's direction, even dots not yet in the aperture. Relevant to how the cueing effect propagates to the target translation 300ms later.

- **Born & Bradley (2005)** *Annual Review of Neuroscience* — MT structure/function review. Needed as background for all MT-based modeling claims above. Should be added to `pending_papers.md` for integration next session.

- **Cumming & DeAngelis (2001)** *Annual Review of Neuroscience* — Physiology of stereopsis. Establishes the V1 disparity-tuning substrate that Qian & Andersen (1997) builds on. Needed to characterize what 0.05m at 2m viewing distance means in disparity angular units (approximately 0.72 arcmin).

- A model that jointly handles transparent motion + attention + depth has not yet been identified in the literature. The Qian & Andersen (1994) + Desimone & Duncan (1995) combination covers the main phenomena but is not a unified computational model. This is the modeling gap VRDots data are positioned to motivate.

---

*Created 2026-03-31. Part 2 of Literature Agent session.*
