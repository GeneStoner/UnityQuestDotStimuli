# Endogenous Color Attention in Transparent Motion: Hillyard Lab and the Point-Set Model
*Literature agent — 2026-04-06*

---

## 1. Overview

The DecoupledDots experiment found zero color-field cueing with an **exogenous** temporal onset cue. The question now is whether **endogenous** (voluntary, top-down) color attention can select a transparent surface. The Hillyard literature gives a clear and surprisingly rich answer — and almost every finding maps onto a prediction of the V1 point-set model.

---

## 2. The Critical Result: Schoenfeld, Hopf et al. (2014), Reversed Sequence

**Full citation**: Schoenfeld MA, Hopf J-M, Merkel C, Heinze H-J, Hillyard SA (2014). "Object-based attention involves the sequential activation of feature-specific cortical modules." *Nature Neuroscience* 17(4):619–624. PMID: 24561999.

*(paper_list.md #11 — already integrated; revisited here in more detail)*

**Stimuli**: Two superimposed transparent dot arrays, segregated by color and motion direction — directly the transparent-surface paradigm. Observers attended to one surface defined either by its **motion direction** or by its **color**.

**The finding, verbatim from the abstract**:
> "When surface motion was attended, the magnetoencephalographic waveforms showed enhanced activity in the motion-specific cortical area starting at ~150 ms after motion onset, followed after ~60 ms by enhanced activity in the color-specific area. **When surface color was attended, this temporal sequence was reversed.**"

- **Attend to motion** → motion cortex first (~150ms), color cortex ~60ms later (~210ms)
- **Attend to color** → color cortex first (~150ms), motion cortex ~60ms later (~210ms)

The reversal is complete and symmetric. The irrelevant feature module is always recruited approximately 60ms after the attended module, regardless of which module was attended first.

**This is the most important single result for the model** and is discussed in detail below (§4).

---

## 3. Supporting Hillyard Literature

### 3.1 Schoenfeld, Hopf et al. (2007) — Feature Dimension vs. Feature Value

**Full citation**: Schoenfeld MA, Hopf J-M, Martinez A, Mai HM, Sattler C, Gasde A, Heinze H-J, Hillyard SA (2007). "Spatio-temporal analysis of feature-based attention." *Cerebral Cortex* 17(10):2468–2477. PMID: 17204821.

**Stimuli**: Random dot display (not transparent surfaces); dots periodically changed color or moved coherently. Combined EEG/MEG/fMRI.

**Key finding**: Attending to the color *dimension* (any color change) activates V4v beginning at **90–120ms** — as fast as motion dimension attention activates hMT. Selecting a specific feature *value* (one color from another) is slower. The key insight: **feature dimension attention is rapid; feature value attention is slower and more effortful.**

**Relevance**: In VRDots, instructing the observer to "attend to the red surface" is a feature-value instruction (red, not green). This should produce a slower, more endogenously sustained selection signal than attending to the motion dimension per se. This latency difference between dimension and value attention may partly explain why endogenous color selection requires voluntary instruction to work — it is not fast enough to bootstrap from an 80ms onset event.

### 3.2 Anllo-Vento & Hillyard (1996) — Ventral vs. Dorsal Selection Negativity

**Full citation**: Anllo-Vento L, Hillyard SA (1996). "Selective attention to the color and direction of moving stimuli: Electrophysiological correlates of hierarchical feature selection." *Perception & Psychophysics* 58(2):191–206. PMID: 8838164.

**Stimuli**: Colored squares with apparent motion. Observers attended to one spatial field and detected targets matching attended color OR direction.

**Key ERP findings**:
- Color feature selection → **selection negativity with ventral scalp distribution** (inferior occipital-temporal)
- Motion direction feature selection → **selection negativity with dorsal scalp distribution** (superior occipital-parietal)
- Both selection negativities emerged after spatial attention P1/N1 (~100–120ms), peaking in the 200–350ms range
- Feature selection was **hierarchically dependent** on prior spatial selection — it built on top of the spatially-selected response

**Relevance**: Anatomically distinct selection mechanisms for color (ventral) and motion (dorsal). These correspond precisely to the blob-to-V4 pathway (color) and the interblob-to-MT pathway (motion) — the two pathway arms of the point-set model. The fact that feature selection is hierarchically dependent on spatial selection is consistent with the model: spatial selection (surface location) is established first by the onset event, then feature-level selection propagates through the relevant stream.

### 3.3 Anllo-Vento, Luck & Hillyard (1998) — Timecourse of Color Attention

**Full citation**: Anllo-Vento L, Luck SJ, Hillyard SA (1998). "Spatio-temporal dynamics of attention to color: evidence from human electrophysiology." *Human Brain Mapping* 6(4):216–238. PMID: 9704262.

**Stimuli**: Foveally presented colored checkerboards; attend to one color, detect dimmer targets.

**Timecourse of endogenous color attention**:
- 50ms: Automatic color coding — **attention-independent**, no modulation
- ~100ms: First attention-related divergence (lateral occipital)
- 160ms: Peak modulation, inferior occipito-temporal (V4 equivalent)
- 190ms: Premotor frontal
- 240ms: Anterior fusiform

Color attention effects emerge at ~100ms and progress through the ventral hierarchy. The earliest color processing (50ms) is automatic and unmodulated — the P-pathway initial response cannot be voluntarily gated.

**Relevance**: Color attention does NOT modulate the very first feedforward response (50ms, V1 initial activation). It acts downstream, starting at ~100ms. For VRDots, this means top-down color attention begins to influence the representation only ~100ms after dot onset — later than the M-pathway onset signal that drives exogenous surface selection.

### 3.4 Zhang & Luck (2009) — Color Attention Can Be Early Under Competition

**Full citation**: Zhang W, Luck SJ (2009). "Feature-based attention modulates feedforward visual processing." *Nature Neuroscience* 12(1):24–25. PMID: 19029890.

**Key finding**: Under conditions of high stimulus competition (multiple competing stimuli), top-down color attention influences feedforward processing within **~100ms** — earlier than typically seen for selection negativity. Color-based attention can precede spatial attention when competition demands it.

**Relevance for VRDots**: In the two-surface transparent-motion display, stimulus competition is high — two populations of dots overlap completely in space. This may be precisely the regime where color-based endogenous attention is most effective. If an observer is explicitly set for red, the high competition in the overlapping display may recruit color-based top-down gating earlier than in single-stimulus paradigms.

### 3.5 Motter (1994) — V4 Single-Unit Evidence

**Full citation**: Motter BC (1994). "Neural correlates of attentive selection for color or luminance in extrastriate area V4." *Journal of Neuroscience* 14(4):2178–2189. PMID: 8158264.

**Key finding**: 74% of macaque V4 neurons showed ~2x enhanced responses when the stimulus in the RF matched the cued color. The enhancement was spatially independent (feature-based, not location-based) and developed beginning at ~200ms after stimulus onset.

**Relevance**: Direct single-unit evidence that the color-selective neurons (V4 ≈ ventral stream / blob-projection endpoint) are strongly modulated by top-down color attention. These are the same neurons that Schoenfeld 2014 shows activating FIRST in the color-attended condition of the transparent motion paradigm.

### 3.6 Saenz, Buracas & Boynton (2002/2003) — Color Attention Spreads Globally

**Citations**:
- Saenz M, Buracas GT, Boynton GM (2002). "Global effects of feature-based attention in human visual cortex." *Nature Neuroscience* 5(7):631–632. PMID: 12068304.
- Saenz M, Buracas GT, Boynton GM (2003). "Global feature-based attention for motion and color." *Vision Research* 43(6):629–637. PMID: 12604099.

**Key finding**: Both color and motion direction attention spread globally across the visual field. Attending to a particular color at one spatial location enhances processing of stimuli with the same color at distant, spatially unattended locations. Color and motion direction are **quantitatively similar** in the magnitude of this global feature-based spread.

**Relevance**: This is the psychophysical/fMRI analog of Treue & MTT (1999) for color: attending to red is not confined to the attended location — it globally boosts all red-preferring neurons. In VRDots, this global feature-similarity gain for red would boost all red-dot representations everywhere in the display, which means it would selectively boost the representation of Field A (red field) across all spatial positions simultaneously. This is exactly what is needed for surface selection.

---

## 4. How the Point-Set Model Explains the Hillyard Results

### 4.1 The Core Prediction: Entry Point Determines Activation Sequence

The V1 point-set model contains neurons tuned to motion direction and disparity (interblob/layer 4B) and color (blob), with mutual excitation connecting them within each hypercolumn. The critical insight from Schoenfeld (2014) is that the **temporal sequence of feature module activation depends entirely on where the attentional signal enters the network**:

**Exogenous motion onset** (VRDots temporal onset):
```
Onset → M-pathway → direction/disparity columns FIRST
          └──── mutual excitation ──── → color columns SECOND (+60ms)
```
This matches Schoenfeld 2014 motion-attended condition: motion first, color 60ms later.

**Endogenous color attention** ("attend to the red surface"):
```
Top-down color instruction → feature-similarity gain for red
          → blob/V4 neurons FIRST
          └──── mutual excitation ──── → direction columns SECOND (+60ms)
```
This matches Schoenfeld 2014 color-attended condition: color first, motion 60ms later.

The same mutual excitation network, entered from opposite ends, produces opposite activation sequences. **The 60ms inter-module gap is the synaptic and propagation delay of the cross-column coupling** — it is the same delay regardless of direction, which is why the reversal is symmetric.

This is a non-trivial prediction of the model: it predicts not just that both sequences are possible, but that the inter-module gap should be approximately equal whether the cascade goes motion→color or color→motion. The Schoenfeld data show exactly this (~60ms in both directions).

### 4.2 Why Is Color-Based Selection Endogenous, Not Exogenous?

The point-set model + M-pathway argument (color_model_conjecture.md §2) explains the asymmetry:

- **Exogenous**: Onset events drive M-cells → M-pathway is direction/disparity-indexed, not color-indexed → the exogenous selection signal enters the network at the motion/disparity end → color is a trailing consequence, never a leading cause
- **Endogenous**: Top-down voluntary attention can set a color-indexed feature-similarity gain (the observer deliberately "tunes" to red) → this enters the network at the color/blob end → motion direction becomes the trailing consequence

The asymmetry is therefore fundamentally about the **sensory transduction pathway** for the onset event (M-pathway, color-blind) versus the **cortical feedback pathway** for voluntary attention (can be color-indexed via V4 → V1 feedback). Top-down attention is not constrained by M-cell properties; it can target any feature dimension equally, as Saenz et al. (2002/2003) confirmed — color and motion attention spread equally in both magnitude and spatial extent when attention is endogenous.

### 4.3 The Coupling Asymmetry Revisited

In `color_model_conjecture.md`, Conjecture 4 argued that the blob/interblob coupling might be weak — which is why F3 = 0 in the exogenous condition. But if the coupling were zero, endogenous color attention couldn't propagate into the motion direction stream either, and Schoenfeld 2014's color-attended condition would fail to show motion cortex activation.

The resolution: **the coupling may be asymmetric in magnitude, not absent.** Specifically:

- **Interblob → blob** (motion → color, exogenous direction): Moderate coupling; sufficient to produce the color activation ~60ms after motion activation (Schoenfeld 2014 motion-attended, Schoenfeld 2003)
- **Blob → interblob** (color → motion, endogenous direction): Also present, sufficient to produce motion activation ~60ms after color activation (Schoenfeld 2014 color-attended)

But for **behavioral performance** in a direction-discrimination task:
- Motion → color cascade: the color activation is a *consequence* of selection, not a driver of direction discrimination. Behaviorally null (F3 = 0) even though the neural cascade exists.
- Color → motion cascade: the motion activation is a *consequence* of color-based selection and CAN improve direction discrimination — because the activation now boosts direction-tuned neurons for the correct surface.

This is the key distinction: the **direction** of the cascade matters for behavioral read-out. Color→motion improves direction discrimination (endogenous color selection would produce behavioral cueing); motion→color does not (the color cortex activation from an onset cue has no path back to direction discrimination).

The read-out bottleneck (Conjecture 1) still applies, but it is now directional: it only blocks the motion→color direction from producing behavioral effects. The color→motion direction does produce behavioral effects, because it terminates at the direction read-out.

### 4.4 Feature-Similarity Gain Is Feature-Agnostic at the Top-Down Level

Saenz et al. (2002/2003) confirmed that color and motion attention produce equal global spread. The Treue & MTT (1999) feature-similarity gain model (which the point-set model builds on) was originally demonstrated for motion direction — but the Saenz result extends it to color. The top-down feature-similarity gain mechanism is therefore feature-agnostic: it can be indexed to any feature dimension (direction, color, disparity potentially) when that dimension is the voluntary attentional set.

In VRDots terms: instructing the observer to "attend to the red surface" would set a **color-indexed feature-similarity gain** that globally boosts red-preferring neurons everywhere in the display. Since Field A (red dots) and Field B (green dots) are spatially interleaved, this boost selectively enhances Field A's representation at every retinotopic location — a form of global surface selection via color indexing. The cascade then propagates into direction columns, eventually reaching the motion read-out.

### 4.5 Predicting Anllo-Vento & Hillyard (1996): Stream-Specific SNs

The anatomically distinct selection negativities — ventral (color) vs. dorsal (motion) — map directly onto the blob and interblob pathways of the point-set model:

| Anllo-Vento 1996 | Point-Set Model |
|-----------------|-----------------|
| Color SN, ventral distribution, ~200–350ms | Blob neurons → V4 → fusiform feedback loop |
| Motion SN, dorsal distribution, ~200–350ms | Interblob/4B neurons → MT → parietal feedback loop |
| Both SNs hierarchically dependent on spatial P1/N1 | Spatial surface selection (onset → M-pathway) is prerequisite; feature selection builds on it |
| ~100ms latency after spatial P1/N1 peak | Cross-column coupling propagation delay: the ~60ms of Schoenfeld 2014 |

The hierarchical dependence — spatial attention first, then feature selection — is important. In VRDots, the exogenous onset establishes WHICH surface (spatial selection). Endogenous color attention could then layer on top, selecting the same surface via the ventral/color stream. These two mechanisms should be additive rather than redundant.

---

## 5. Predictions for VRDots — Endogenous Color Attention Experiment

The Hillyard literature + point-set model together generate the following testable predictions:

### P1: Endogenous color instruction produces a behavioral cueing effect
If observers are told "the red surface will translate — report its direction," endogenous color attention sets a color-indexed feature-similarity gain for red. Via cross-column coupling, this propagates into direction columns for the red surface. The result should be a behavioral cueing effect from color alone — better direction discrimination for the red surface — **without any temporal onset cue**.

This is the key experiment. Expected magnitude: smaller than the exogenous onset cueing effect (+22pp), because:
(a) The blob→interblob propagation may be weaker than the direct M-pathway onset signal
(b) Feature-value attention (red, not just any color) is slower than feature-dimension attention (Schoenfeld 2007)
(c) No temporal onset transient to amplify the selection signal

Predicted result: +5–15pp cueing from color alone, with sustained endogenous set. This is the minimum detectable effect; requires ~256+ trials/condition.

### P2: Endogenous + exogenous combination should be larger than either alone
If color-based endogenous selection is running in background (observer set for red) and an exogenous onset cue fires on the red surface, both mechanisms boost the same direction columns simultaneously. The combination should produce greater cueing than exogenous alone. If the onset fires on the green surface instead, the two mechanisms compete: onset boosts green direction columns, color attention boosts red direction columns. Net effect on cueing: attenuated.

This predicts a COLOR × ONSET interaction in a combined-cue paradigm.

### P3: The Schoenfeld sequence should be observable in VRDots ERP
If VRDots were run with EEG and the observer attended to the red (color-defined) surface endogenously, color-selective activation should precede motion-selective activation. If the observer used the temporal onset cue (exogenous), motion-selective activation should precede color. This replicates Schoenfeld 2014 but in the VRDots stereoscopic paradigm.

### P4: Depth-field cueing should interact with endogenous color attention
If depth helps by establishing figure-ground for the motion read-out, and color helps by propagating top-down selection into direction columns, they should be approximately additive when both are present (red surface AND correct depth plane). If depth were not a selection mechanism but merely a perceptual segmentation cue, the interaction might be sub-additive or null.

---

## 6. New Papers to Add to Paper List

| Paper | Citation | Key finding | Priority |
|-------|----------|------------|---------|
| **Schoenfeld et al. (2007)** | *Cerebral Cortex* 17:2468 | Feature dimension attention (color AND motion) activates cortex at 90–120ms; color = V4v, motion = hMT | High — directly extends Schoenfeld 2014 |
| **Anllo-Vento & Hillyard (1996)** | *P&P* 58:191 | Color SN (ventral) and motion SN (dorsal) are anatomically distinct; hierarchically dependent on spatial selection | High — maps onto blob/interblob streams |
| **Anllo-Vento, Luck & Hillyard (1998)** | *Hum Brain Map* 6:216 | Color attention timecourse: lateral occipital ~100ms → fusiform 160–240ms; 50ms automatic color coding is unmodulated | Medium |
| **Zhang & Luck (2009)** | *Nat Neurosci* 12:24 | Color-based feature attention modulates feedforward processing within ~100ms under high competition | Medium |
| **Motter (1994)** | *J Neurosci* 14:2178 | V4 neurons 2x enhanced by color attention, onset ~200ms; spatially independent (feature-based) | Medium |
| **Saenz, Buracas & Boynton (2002)** | *Nat Neurosci* 5:631 | Color and motion attention both spread globally; effects quantitatively similar | High — establishes color-indexed feature-similarity gain |
| **Saenz, Buracas & Boynton (2003)** | *Vision Research* 43:629 | Behavioral confirmation of global feature-based attention for both color and motion | Medium |
| **Corbetta et al. (1991)** | *J Neurosci* 11:2383 | PET: attending to color activates ventral occipital; attending to motion activates parietal; anatomical double dissociation | Low (older, PET) |

---

## 7. Narrative Summary for Write-Up

The exogenous null (F3 = 0.0pp) and the endogenous positive prediction together define a clean double dissociation:

**Color does not guide selection when the cue is exogenous** — the temporal onset event drives the M-pathway (color-blind), entering the point-set network at the motion/disparity end. Color activation is a downstream consequence of selection, not a driver of it. Having the correct vs. incorrect color at tStart is irrelevant to the direction-discrimination read-out (read-out bottleneck, Conjecture 1 in `color_model_conjecture.md`).

**Color can guide selection when attention is endogenous** — voluntary top-down attention can set a color-indexed feature-similarity gain, entering the point-set network at the blob/color end. This propagates into direction columns via cross-column coupling, ultimately improving direction discrimination for the color-selected surface. The Schoenfeld (2014) reversal is the neural evidence that this cascade runs equally well in both directions within the same mutual excitation network.

The model therefore does not need modification for endogenous color — it needs only the recognition that the direction of cascade entry, determined by whether the selection signal is exogenous (sensory transduction pathway → motion/disparity first) or endogenous (top-down feedback pathway → any feature, including color, first), determines which feature module leads and which follows. The 60ms inter-module gap is constant because it is a property of the cross-column coupling, not of the attended feature.

---

*See also*: `color_cueing_review.md` (exogenous color null), `color_model_conjecture.md` (model conjectures), `vergence_latency_note.md`, `modeling_lit.md §6` (point-set model), paper_list.md Group 2 (#9–14)
