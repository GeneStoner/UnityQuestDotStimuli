---
name: VRDots Open Questions and Design Considerations
description: Open empirical questions and pending design decisions for future sessions
type: project
---

## Open Empirical Questions

1. **ZdA/ZdB: monocular confound vs depth-plane grouping**
   The ZdA impairment and ZdB enhancement are consistent with EITHER:
   (a) Monocular positional confound: depth change adds spurious motion to ZdA's coherent translator (0–5 arcmin shift, scales with eccentricity, up to 49% of translation distance)
   (b) Depth-plane grouping: ZdA disrupts the cued dot's plane membership; ZdB reinforces it
   **Best test**: right-eye-closed monocular session (left eye has floaters — bad monocular test so far).
   If ZdB-Near survives monocularly (R eye), grouping account gains support.
   **Secondary test**: add a condition where depth changes at a time OTHER than tStart.

2. **Far > Near cueing asymmetry — three competing accounts**
   Consistent across sessions at 0.05m. Entirely stereoscopic (absent monocularly). Three accounts currently viable:
   (a) **Gradient migration** (dynamic): attention drifts from Near toward Far during delay; Near cue eroded by tStart. Predicts asymmetry grows with SOA.
   (b) **Bounded-window** (GS, introspective): attentional spotlight extends "beyond" attended plane; Near leaks into Far (nothing bounds it); Far is clean (nothing lies beyond). Predicts SOA-invariant asymmetry. KEY TENSION: DepthParam shows asymmetry GROWS with depth separation — but if leakage decreases as planes become more segregable at larger disparities, the account predicts it should SHRINK. Unresolved.
   (c) **MT disparity-population anisotropy** (Calabro & Vaina 2011, PMID 21068268 — verify citation): more MT neurons tuned to near-disparity → more cross-talk → worse near-plane selectivity. Predicts asymmetry scales with absolute disparity, SOA-invariant.
   **Critical dissociation**: SOA experiment (gradient migration vs. b/c); three-plane display (b vs. c); fixation-depth reversal (vergence-driven vs. disparity-driven).

3. **ZdB-Near vs ZdB-Far dissociation (binocular)**
   ZdB-Near=+56pp**, ZdB-Far=+56pp** — both equally strong binocularly.
   But ZdB-Near collapses monocularly while ZdB-Far shows a trend (+31pp†).
   Is Far special in ZdB specifically? Or noise (n=16)?

4. **Near/Far asymmetry in N monocular**
   N-Near=+19pp n.s., N-Far=+0pp n.s. monocularly.
   N-Far collapses completely but N-Near shows a (n.s.) trend. Binocular depth perception
   seems to HELP the Far condition but slightly HURT the Near condition — odd.

5. **Replication / statistical power**
   All DepthSwapCtrl cells are n=16. ZdA/ZdB results are suggestive but need replication.
   Run 3+ more sessions before drawing strong conclusions.

6. **Single subject (GS) throughout**. Generalizability unknown.

7. **Zd (legacy Depth50) Near cell**
   Still underpowered from 260326_1649 (+22pp n.s. at n~31). One more Zd session would clarify.

8. **DepthParam crossover depth** (~0.035–0.045m)
   Near cueing transitions from positive (0.03m) to negative (0.05m). Crossover predicted to map to stereoacuity threshold at 2m. Needs fine-grained sweep (0.033/0.038/0.042/0.047m) after second sessions confirm the basic pattern.

9. **SOA manipulation**
   At short SOA (~100–150ms), gradient migration incomplete → Near cueing should match Far cueing. As SOA lengthens, migration completes → Near cueing advantage disappears. SOA at which Near cueing = Far cueing estimates migration completion time at each depth. Wait for n=64/cell DepthParam replication first.

10. **Fixation-depth reversal experiment**
    If fixation placed at current Near depth (1.975m), gradient re-anchors → Far > Near asymmetry should weaken or disappear (gradient account). If it persists: near-object salience or looming account. Critical dissociation. See depth_ior_hypothesis.md §Prediction 2.

11. **Heading × depth reanalysis (free, no new sessions)**
    Reanalyze existing DepthParam sessions by TransDeg × DelayedFieldDepth. If Far > Near asymmetry is uniform across 8 headings → depth-plane account. If concentrated in approach-direction headings → looming/approach mechanism. Code: `TransDeg` × `DelayedFieldDepth` from existing TSVs.

12. **Second sessions at each DepthParam depth**
    All parametric claims based on n=32/cell (single sessions). Wilson 95% CI ≈ ±15–20pp. The crossover location (between 0.03 and 0.05m) and all trend claims are provisional. Second sessions at 0.03/0.05/0.10/0.15m are Priority 1 before any new paradigm.

13. **Second observer at 0.05m and 0.10m**
    All data from observer GS. Observer-specific stereo acuity may shift crossover depth. Two observers with n=64/cell at 0.05m and 0.10m (straddling crossover) needed before designing fine-grained sweep.

---

14. **Color vs depth contribution to ZdCoh disruption — RESOLVED (2026-04-06)**
    DecoupledDots (linkDepthColor=0) directly dissociates: F3 Color-field cueing = +0.9pp n.s. across all model specs. Color is null. The DepthColorLinked F2 effect is entirely attributable to depth-plane continuity. Color-only swap (C condition) confirms: performance indistinguishable from N (no swap).

15. **UNCUED elevation in Session 2 (DepthColorLinked)**
    Session 2 (260404_1123) showed UNCUED +14–16pp vs Session 1 +3–6pp. Observer reported no strategy change. Criterion shift? Noise at n=64/cell? Monitor across sessions — if UNCUED stays elevated, reassess factor structure.

16. **Does color differentiation suppress UNCUED tracking?**
    DepthColorLinked UNCUED = +9.8pp vs DepthSwapCtrl ZdA+ZdB UNCUED = +20.8pp. Color may make it harder to accidentally track the non-cued field. Needs replication at matched n.

17. **Disparity-tuned neurons vs perceived depth order (new, 2026-04-09)**
    The Near/Far asymmetry and depth-plane continuity effect (F2) implicate disparity-tuned neurons. But does the mechanism require actual binocular disparity, or would perceived depth order from monocular cues (occlusion, motion parallax, size gradients) suffice? F2 partially survived monocular viewing (+7.1pp) in DepthSwapCtrl, but that session had essentially no alternative depth cues at 0.05m separation. A manipulation using monocular-only depth cues (e.g., occlusion to define depth planes) while eliminating binocular disparity would localise the critical computation to either early V1/V2 binocular cells or higher-order depth-order representations.

18. **Additive vs conjunctive attention cueing — refining the framing**
    The F1×F2 interaction in both GLMs shows the conjunction of dot cue + depth continuity is required. Is this (a) a depth-plane spatial window that the dot cue activates (gating model), or (b) object-based tracking where depth is an identity feature? Current data are consistent with both. Key dissociation: teleport cued dots to a completely new 3D location at tStart — does cueing survive? If yes, it tracks the object identity not the spatial window.

19. **Observer GS esophoria as a confound for Far > Near asymmetry**
    GS has clinically documented esophoria (prism-corrected glasses, not worn in VR). Crossed disparity (Near plane) may be perceptually noisier for GS specifically due to vergence strain. The Far > Near asymmetry could be observer-specific rather than a general property of depth attention. Second observer with normal vergence at 0.05m and 0.10m is the critical test.

## Pending Design Decisions

### Monocular Sessions (both L-eye-closed / R-eye active) — DONE
- 260330_2012: L-eye closed, R-eye active (floaters may affect quality)
- 260331_1530: L-eye closed, R-eye active (second session, same eye)
- Both are right-eye sessions. Left-eye-closed monocular not yet run.
- Pooled mono (n=385): dot cueing survives (*), depth-field cueing does not (n.s.), Near/Far absent (n.s.)

### Confound Isolation Control
- Add a condition where the same depth change happens at onset (not tStart) — before translation
- This would disentangle the positional-shift confound (only at tStart) from depth-plane grouping (persistent)

### Stimulus Verification — HIGH PRIORITY
- Triple-check ZdA/ZdB depth assignments, rotation group assignments, translation subfield assignments
- Run `verify_trajectories.py` on DepthSwapCtrl sessions once it supports ZdA/ZdB
- Compare against `gen_hypothetical_traj.py` reference trajectories

### Preview Frame at Trial Onset — IMPLEMENTED (2026-03-27)
- Field A (sub0+sub1) shown static at frame-0 positions during WaitingForStart

### Fixation Target / Nonius Lines — PARTIALLY IMPLEMENTED (2026-03-27)
- Binocular nonius lines working; true dichoptic deferred (requires OVR Compositor Layers)

### Mod 3 — Minimum Pre-Trigger Hold (not implemented)
- Enforce minimum ready-hold time before accepting trigger to ensure vergence is established

### analyze_vr_dots_v2.py depth column support
- Currently ignores depth columns in per-breakdown analysis (backburner)
- The manual chi2 analysis above handles it for now

### Notes field in session meta.json
- Convention: add `"notes": "..."` field to .meta.json by hand after session
- e.g. `"notes": "monocular — left eye closed"`
