# VRDots Stereo Depth Experiments — Artifacts and Resolutions

*G. Stoner · September 2026*

---

## Background

The stereo depth series introduced disparity via a screen-space shader (`DotScreenSpace.shader`). Each dot field was offset in depth by `depthSeparation_m` metres along the camera's forward axis, placing one field in the Near plane and the other in the Far plane relative to fixation (view distance 2.0 m). The paradigm was otherwise identical to the 2D version: two overlapping colour-coded rotating dot fields, one with a 750 ms delayed onset, 8AFC heading judgment.

Two separate artifacts were discovered and resolved over the course of data collection (March–April 2026).

---

## Artifact 1 — `transform.forward` Pitch Bias

### What it did

In `StimulusBuilder.ApplyDepthOffsets()`, the depth offset was applied along `transform.forward` — the StimulusBuilder GameObject's own world-space forward axis — rather than `Camera.main.transform.forward`. If the StimulusBuilder was pitched upward by even a few degrees (θ), a depth-plane swap of Δz metres at trial start (tStart) produced a spurious upward screen-space velocity:

> v_up ≈ Δz × sin(θ) / Δt

At θ ≈ 5°, Δz = 0.10 m (100% depth swap), and Δt = 0.013 s (one frame at 90 Hz):

> v_up ≈ 0.10 × 0.087 / 0.013 ≈ **19°/sec**

The translation signal was 2.26°/sec. The artifact was **8.2× the signal**, essentially forcing observers to report "upward" on every trial with a depth swap at tStart, regardless of actual translation direction.

### Smoking-gun numbers

In pre-fix sessions with 100% depth swap (Z and CZ conditions):

| Condition | "UP" share of wrong responses |
|-----------|-------------------------------|
| N (no swap) | 4.3% |
| C (colour swap only) | 6.0% |
| Z (depth swap only) | **49.6%** |
| CZ (colour + depth swap) | **50.0%** |

On a 270° (downward) heading in the Z condition, **61% of responses reported UP** — the artifact directly opposed the signal. On a 90° (upward) heading, accuracy was artificially inflated because the artifact and signal aligned.

The bias was invariant to rotation configuration (RotCfg 0: 52% UP; RotCfg 1: 47% UP) and to whether the cued or uncued arm was examined — confirming it was a low-level motion artifact, not a cueing effect.

### Scaling with depth swap magnitude

The artifact scaled with the total depth displacement:

| Experiment | Depth change per trial | "UP" share in Z wrong responses |
|-----------|------------------------|--------------------------------|
| DecoupledDots (100% swap, 0.10 m) | 0.10 m | 50% |
| BothFar (100% swap, 0.05 m) | 0.05 m | 44% |
| DepthColorLinked (50% of dots, 0.10 m per dot) | ~0.05 m effective | 26–22% |

Critically, conditions **without a depth swap at tStart** (N and C conditions, DepthBaseline, DepthParam) had no artifact at all — those data are entirely clean regardless of whether the session was pre-fix.

### The fix (2026-04-11)

One line in `StimulusBuilder.ApplyDepthOffsets()`:

```csharp
// Before (buggy):
Vector3 zVec = transform.forward * z;

// After (fixed):
Vector3 depthAxis = (Camera.main != null)
    ? Camera.main.transform.forward
    : transform.forward;
Vector3 zVec = depthAxis * z;
```

Post-fix experiment assets were renamed with a `_v2` suffix in their `experimentName` field (e.g. `DecoupledDots_005m_v2`). Any TSV file whose `Experiment` column lacks `_v2` is pre-fix.

### Data exclusion rule

- TSV `Experiment` contains `_v2` → post-fix, Z/CZ rows clean
- TSV `Experiment` does **not** contain `_v2` → pre-fix; **exclude Z/CZ condition rows**
- N and C condition rows in pre-fix files are unaffected

### What survived from pre-fix data

The following results are artifact-independent and remain valid from pre-fix sessions:

1. **F1 dot cueing effect** — derived from the N condition (no depth swap); fully clean
2. **Color null** — C condition has no depth component; 6% UP (same as N); clean
3. **Far > Near cueing asymmetry** — derived from the N condition; fully clean
4. **ZdNoi > ZdCoh dissociation** (DepthColorLinked) — both conditions show similar attenuated artifact (26% vs 22% UP); the 19 pp gap between them survives

The pre-fix **F1×F2 interaction** in DecoupledDots (+32.7 pp***) is unreliable. Post-fix it collapsed to +7.8 pp n.s. — this finding must be replicated with clean sessions.

---

## Artifact 2 — Disparity Sign Bug

### What it did

In the single session 260415_2242 (`DecoupledDots_005m_v2`, collected 2026-04-15 — the day after the pitch fix), the disparity sign was inverted in code. Dots assigned to the "Near" depth plane were rendered at the Far stereo offset and vice versa. Observers experienced the opposite depth layout from what the TSV labels indicated.

This did not affect 2D motion — the heading judgment and temporal onset cue were unaffected. However, any analysis that splits by Near vs Far depth plane is confounded: the labels encode the opposite percept.

### Resolution

The bug was identified immediately after the session and corrected before further data collection. Session 260415_2242 is retained with the following restriction:

- **Overall cueing effects** (collapsed across Near/Far): valid
- **Near/Far breakdown**: excluded from analysis

---

## Summary: Data Quality Map

| Experiment | Sessions | Conditions affected | Status |
|-----------|----------|-------------------|--------|
| DepthBaseline | 260325_1831/1914 | — | ✅ Fully clean |
| DepthSwapCtrl binocular | 260330–260401 | ZdA/ZdB (attenuated ~26% UP) | ⚠️ Absolute levels suspect; dissociation valid |
| DepthSwapCtrl monocular | 260330–260331 | ZdA/ZdB (attenuated) | ⚠️ Same |
| DepthParam (all depths) | 260402 | — (no swap at tStart) | ✅ Fully clean |
| DepthColorLinked | 260404–260406 | ZdA/ZdB (attenuated ~26/22% UP) | ⚠️ Absolute levels suspect; ZdNoi > ZdCoh valid |
| DecoupledDots pre-fix | 260406–260407 | Z/CZ fully contaminated | ⛔ Z/CZ unusable; N/C clean |
| BothFar | 260411_1225 | Z attenuated | ⚠️ Partially suspect |
| DecoupledDots post-fix | 260413_1846 | — | ✅ Fully clean |
| DecoupledDots sign-bug | 260415_2242 | Near/Far label inversion | ⚠️ Collapse across depth planes only |

---

## Verification Protocol (for future sessions)

After any session with Z/CZ conditions, run `depth_swap_artifact_analysis.py` and confirm:

- "UP" share of wrong responses in Z condition ≤ 10% (matches N-condition baseline)

If this threshold is exceeded, do not analyse the depth-swap conditions and investigate the StimulusBuilder pitch before collecting further data.
