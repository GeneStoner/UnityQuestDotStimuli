# Density and the limits of surface-based attentional selection

*Draft — 2026-04-24*

---

## Introduction

When two transparent dot fields occupy the same region of space and move in different directions, observers can selectively attend to one field and judge its motion independently of the other. The mechanism supporting this selectivity has been the subject of sustained investigation, yet its computational basis remains poorly understood. A central question is whether the selection operates on abstract surface representations — in which case individual dot locations should be irrelevant — or whether it is implemented by spatially fine-grained mechanisms that track the positions of individual dots.

Stoner and Blanc (2010) addressed this question using a delayed-onset paradigm. Two superimposed dot fields rotated in opposite directions; one field was present from the start of each trial (the always-on field) and the other appeared 750 ms later (the delayed field). After 300 ms of joint rotation, one field briefly translated, and observers judged the direction of translation. Performance was substantially better when the delayed field translated (the cued condition) than when the always-on field did (the uncued condition), a cueing effect of approximately 35 percentage points. Crucially, this advantage survived a swap of the motion directions of the two fields at the moment translation began: if the delayed field adopted the rotation direction previously belonging to the always-on field (and vice versa), the cueing effect was preserved. Because the swap eliminated any difference in rotation history, color, or speed between the two fields — leaving dot spatial location as the only remaining distinguishing property — the result demonstrated that the attentional advantage is conferred on a dot-position-specific basis. Whatever mechanism delivers the advantage to the delayed field does so by tracking the locations of individual dots, not by detecting a global feature of the field.

Catek et al. (in prep.) extended this finding using a depth-plane manipulation. In their paradigm, one of the two dot fields was shifted to a different depth plane at the moment translation began. When the coherent translator (the delayed field) changed depth plane at that moment, the cueing effect was sharply attenuated. When only the always-on field changed depth plane, the cueing effect was preserved or enhanced. Because the two conditions were matched for the total amount of depth change in the scene, the disruption was specific to a change in the spatial properties of the attended surface at the critical moment. This result reinforces the conclusion that the mechanism tracking the delayed field is sensitive to fine-grained spatial continuity: it does not merely register which field appeared first and label it globally, but maintains a representation that is vulnerable to spatial discontinuity in the attended surface.

Together, these findings point to a spatially fine-grained selection mechanism. Regardless of whether one interprets the underlying computation as spatial attention directed to dot positions, figure-ground segmentation, or object-based attention to a transparent surface, the empirical signature is the same: the competitive advantage of the delayed field is implemented at the level of individual dot locations, not at the level of a global surface label.

---

## The density prediction

A spatially fine-grained mechanism, by definition, must resolve the positions of individual dots. If the mechanism confers its advantage by tracking delayed-field dot positions specifically, then its operation depends on being able to distinguish those positions from the interleaved positions of always-on dots. At low dot density, the two fields are well-separated in space at any given moment, and such resolution is straightforward. As density increases, however, dots from the two fields crowd one another: within any small region of the visual field, the ratio of delayed-field to always-on dots approaches equality, and the spatial positions of one field increasingly overlap with those of the other.

The prediction follows directly. If surface-based attentional selection is spatially fine-grained, increasing dot density should degrade it: the advantage of the delayed field should erode as crowding makes individual dot positions less diagnostic of field membership. This prediction holds regardless of the specific mechanism proposed — any account that grounds the selection in dot-level spatial information must contend with the consequences of increasing that information's density.

A secondary prediction concerns the symmetry of any density-driven degradation. If density degrades the spatial information supporting field-level selection, the degradation should be symmetric: both the cued and uncued conditions should suffer proportionally, since both depend on the same spatial resolution to determine which field is which. The cueing effect (cued minus uncued) should therefore decrease monotonically with density, with neither arm differentially spared.

---

## Experiment

We tested these predictions using a parametric density manipulation within the delayed-onset paradigm of Stoner and Blanc (2010). Dot density was varied across four values spanning more than an order of magnitude: N = 63, 173, 500, and 1000 dots per field. All other parameters were held constant: aperture radius 3.5°, fixation exclusion radius 1.1°, rotation speed 81°/s, translation speed 2.26° over 80 ms, pre-translation rotation 300 ms, 8-alternative forced choice for translation direction. Each density condition comprised 512 trials run in a single session.

---

## Results

Contrary to the prediction, the cueing effect was entirely flat across the density range N = 63 to N = 500, spanning a factor of eight in dot density (Figure 1). Cued performance was approximately 67% correct and uncued performance approximately 33% correct at every density in this range, yielding a cueing effect of ~35 percentage points throughout. Crowding across this range had no measurable effect on attentional selection.

At N = 1000, the cueing effect declined to approximately 25 percentage points — a reliable reduction. Critically, however, this decline was not symmetric. Cued performance fell from ~67% to ~53% correct. Uncued performance remained flat at ~28–33% correct, statistically indistinguishable from performance at lower densities. The two arms of the cueing effect dissociated: only the cued arm was sensitive to the transition from N = 500 to N = 1000.

---

## Interpretation

The flat plateau over N = 63–500 is inconsistent with a spatially fine-grained mechanism in the sense originally implied: increasing the opportunity for spatial crowding across nearly an order of magnitude produced no degradation whatsoever. Whatever mechanism confers the advantage, it is not limited by the spatial resolution required to track individual dot positions at these densities.

The asymmetric breakdown at N = 1000 introduces a further constraint. If high density degraded spatial resolution uniformly — making it harder to track any field — both arms should decline together. Instead, the uncued arm remained stable while the cued arm fell. This pattern is inconsistent with a general loss of spatial resolution and inconsistent with a general increase in noise. It requires that whatever is lost at N = 1000 was contributing specifically to cued performance, with no corresponding contribution to uncued performance.

One candidate is the integrity of the transparent motion percept itself. At sufficiently high density, two superimposed counter-rotating dot fields may no longer be perceived as two distinct surfaces; the local motion signals within any small region become dominated by conflicting directions, and surface segregation fails. If the advantage of the delayed field depends on its being parsed as a distinct perceptual surface — as Stoner and Blanc's results imply — then the failure of surface segregation at high density would specifically erode the cued arm, since that is the arm that requires an intact surface representation to function. The uncued arm, which never benefited from surface-level selection in the first place, would have nothing to lose and would remain flat.

This account is provisional. Whether the transition at N = 1000 reflects a threshold in transparent motion perception, a limit on attentional tracking, or some other density-sensitive process remains an open question. The planned N = 750 session will locate the transition more precisely and test whether the dissociation between cued and uncued arms is already apparent before N = 1000.

---

*Data: `/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Analysis/density_ultrahigh_analysis.py`*
*Figures: `../Figures/density_ultrahigh_comparison.png`, `../Figures/vrdots_competition_model.png`*
