---
name: Stimulus Artifact Fixes 2026-04-13
description: Root causes, fixes, and impact on DecoupledDots findings for the two motion artifacts fixed 2026-04-13
type: project
---

## Two artifacts fixed 2026-04-13 (commit 5c4c95a)

### Artifact 1: Upward jerk at depth-swap frame
**Root cause**: `StimulusBuilder.ApplyDepthOffsets()` used `transform.forward` (StimulusBuilder world axis) instead of the true optical axis. StimulusBuilder was pitched ~5° → ~19°/sec upward impulse at every depth-swap frame (8.2× the 2.26°/sec translation signal).
**Fix**: `StimulusBuilder.Start()` now computes `transform.rotation` once at scene load from actual camera→stimulus geometry. `transform.forward` is then correct and fixed for the session.

### Artifact 2: Radial expansion/contraction at depth-swap frame
**Root cause**: Perspective scaling (`perspScale = (D+z)/D`) when applied inside `ApplyDepthOffsets` to `ToLocalPlane(dot.position)` accumulated each frame — `StepTranslation` read back the scaled lateral position and then `ApplyDepthOffsets` scaled it again, causing continuous outward/inward drift.
**Fix**: `SubfieldRuntime.trajectoryPos[]` stores each dot's authoritative 2D local position (no depth, no scale). All motion step methods (`StepTranslation`, `StepTranslationBalanced`, `StepRotation`) read from and write to `trajectoryPos`. `ApplyDepthOffsets` reads from `trajectoryPos` and applies `perspScale` cleanly — no accumulation possible.

**Rollback**: `git checkout ca933f2 -- Assets/Scripts/StimulusBuilder.cs`

---

## Impact on findings: session 260413_1846 (n=512, DecoupledDots_005m_v2)

First clean session post-fix. Key results vs previous DecoupledDots (n=2051, pre-fix):

| Effect | Pre-fix | Post-fix | Interpretation |
|--------|---------|----------|----------------|
| F1 dot cueing | +22.3pp*** | +27.3pp*** | Robust, unchanged |
| F2 depth cueing | +12.5pp*** | +6.2pp n.s. | Weaker — see below |
| F3 color cueing | 0.0pp n.s. | −2.3pp n.s. | Null, confirmed |
| F1×F2 synergy | +32.7pp*** | +7.8pp n.s. | **Collapsed — see below** |
| Near/Far (CUED) | Far > Near | +21.9pp (n.s., n=32) | Direction intact |
| Near/Far (UNCUED) | Near > Far | −18.8pp (n.s., n=32) | Direction intact |

**Key interpretation (GS, 2026-04-13)**: The previous F1×F2 synergy (+32.7pp***) was largely an artifact of the upward jerk. The jerk specifically punished CUED+Z trials (where the dot cue and depth swap coincide), suppressing CUED+Z accuracy and inflating the apparent synergy. Post-fix, depth swap does reduce cueing but only modestly (+9.4pp interaction, not significant). GS's provisional conclusion: cueing is mostly XY (motion-based), not depth-field-based. Depth swap is attentionally disruptive but not specifically a depth-field cue.

**Residual artifact**: UP bias in Z wrong responses = 37.6% (vs N=21.0%). Still elevated ~16pp above N baseline. Source unclear — possibly `Start()` running before XR tracking fully initializes (small residual pitch), or perspScale jump at swap frame creating a brief radial transient.

**Next steps**:
- One more session with current asset to confirm
- Move to 50% swaps (ZdA/ZdB) — keeps attentional disruption constant while varying which dots swap depth
- Architectural rewrite (shader-based or trajectoryPos + per-frame camera tracking) to fully eliminate remaining artifacts and head-tilt sensitivity

**Why:** Previous F1×F2 interaction was the headline finding of DecoupledDots. If it was artifactual, the story changes to: cueing is XY-based; depth has a modest disruption effect; Near/Far asymmetry is a real structural effect.

**How to apply:** Do not cite the +32.7pp F1×F2 synergy as a clean result. Flag as provisional pending artifact-free replication. The F1, F3, Near/Far findings are robust (artifact-independent conditions).
