---
name: Depth-Swap Upward-Motion Artifact
description: Root cause, fix, data exclusion rule, and key numbers for the transform.forward pitch-misalignment artifact in Z/CZ depth-swap conditions
type: project
---

## Summary
All sessions collected before 2026-04-11 with a 100% depth swap (Z/CZ conditions) contain a systematic upward-motion artifact. Bug fixed 2026-04-11. Data collected from `_v2` assets onward is clean.

**Why:** `StimulusBuilder.ApplyDepthOffsets()` applied depth offsets along `transform.forward` (StimulusBuilder world-space axis) rather than `Camera.main.transform.forward`. If the StimulusBuilder was pitched upward by angle θ, a depth-plane swap of 0.10m produced an apparent upward screen-space velocity of `0.10 × sin(θ) / 0.013s ≈ 220° × sin(θ) per second` — at 5° pitch this is ~19°/sec vs the 2.26°/sec translation signal (8.2× per frame). This dominated direction perception on virtually every Z/CZ trial.

**How to apply:** Any TSV file whose `experimentName` does NOT contain `_v2` is pre-fix. Exclude Z/CZ condition rows from those files for quantitative analysis of depth-swap effects. N and C conditions in pre-fix files are clean.

---

## The Fix (2026-04-11)
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

---

## Data Exclusion Rule
- TSV `experimentName` contains `_v2` → clean (post-fix)
- TSV `experimentName` does NOT contain `_v2` → pre-fix; Z/CZ rows contaminated

Assets renamed with `_v2`:
- `Exp_DecoupledDots_005m` → `DecoupledDots_005m_v2`
- `Exp_DecoupledDots_Inv_005m` → `DecoupledDots_Inv_005m_v2`
- `Exp_DepthColorLinked` → `DepthColorLinked_005m_v2`
- `Exp_BothFar_005m` → `BothFar_005m_v2` (was already _v2 at creation)
- `Exp_DepthSwapCtrl` → `DepthSwapCtrl_005m_v2`

---

## Key Numbers (from pre-fix data)
| Condition | UP (90°) share of wrong responses |
|-----------|----------------------------------|
| N | 4.3% |
| C | 6.0% |
| Z | **49.6%** |
| CZ | **50.0%** |

- DOWN heading (270°) in Z condition: 61% of responses report UP — the artifact directly opposes the signal
- UP heading (90°) in Z condition: artificially elevated accuracy (artifact + signal coincide)
- Artifact affects ALL headings in Z/CZ equally — not just vertical
- RotCfg 0: 52% UP; RotCfg 1: 47% UP — artifact is not moderated by any experimental factor
- CUED arm: 51% UP in Z wrong responses; UNCUED: 49% — cueing advantage (CUED − UNCUED delta) is preserved

## Scaling with depth change
- DecoupledDots Z (0.10m total swap): 50% UP in wrong responses
- BothFar Z (0.05m total swap): 44% UP
- DepthColorLinked ZdA/ZdB (50% of dots, 0.10m per dot): 26% / 22% UP

---

## Impact on Existing Findings
**Robust (artifact-independent):**
1. F1 dot cueing effect — from N condition, unaffected
2. Color null (C condition) — C has no artifact (6% UP, same as N)
3. ZdNoi > ZdCoh dissociation — both afflicted similarly (26% vs 22% UP); 19pp cueing gap survives
4. Far > Near asymmetry (from N condition) — entirely unaffected

**Suspect (need rerun with _v2 assets):**
- Absolute Z/CZ accuracy levels
- F2 effect magnitude (Z vs N gap) — inflated
- F1×F2 interaction magnitude — suspect
- BothFar depth×cueing interaction — partially suspect

---

## Write-Up and Figures
- **Write-up**: `Agents/SwapPilot/WriteUps/depth_swap_artifact_writeup.md` (+ `.pdf`)
- **Artifact analysis figure (3-page PDF)**: `Agents/SwapPilot/Figures/depth_swap_artifact.pdf`
  - Panel A: UP bias by swap condition (N/C/Z/CZ)
  - Panel B: per-session consistency
  - Panel C: RotCfg invariance
  - Panel D: accuracy by heading, N vs Z
  - Panel E: scaling across experiments
- **Stereo trace demo (3-panel)**: `Agents/SwapPilot/Figures/stereo_trace_artifact_demo.pdf`
  - Panel 1: 2D local-space (artifact invisible)
  - Panel 2: pre-fix stereo (upward jump visible at tStart)
  - Panel 3: post-fix stereo (clean)
- **Full stereo traces (3-page PDF)**: `Agents/SwapPilot/Figures/decoupled_stereo_traces.pdf`
  - Page 1: pre-fix — all 4 swaps (N/C/Z/CZ) × CUED/UNCUED; Z/CZ show ~0.25° upward jump at tStart
  - Page 2: post-fix — same layout; Z/CZ flat
  - Page 3: comparison table with jump magnitudes

---

## Stereo Projection Math
For dot at local (x, y) meters with depth z meters at view distance D=2.0m:
```
z_world = D + z_depth
x_screen = x / z_world   (degrees × 57.3)
y_screen = y / z_world

Pre-fix (pitch θ):
  z_world = D + z_depth × cos(θ)
  y_bias  = z_depth × sin(θ)
  y_screen = y / z_world + y_bias / z_world
```

---

## Verification Protocol (post-fix)
After each new session with Z/CZ conditions, run `depth_swap_artifact_analysis.py`. Confirm UP share of wrong responses in Z ≤ 10% (N-condition baseline). Only proceed if clean.

Three recommended additions to pre-collection pipeline:
1. Stereo-projected traces for any new stimulus design (run before collecting data)
2. Single-frame inspection tool: render dot positions at tStart±1 in screen space per eye
3. Post-session wrong-response direction monitor: flag any direction >15% of wrong responses
