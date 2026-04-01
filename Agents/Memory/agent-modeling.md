---
name: Modeling Agent (pinned — not yet active)
description: Future agent to build computational models that process VRDots stimuli and predict behavior
type: project
---

## Status
**PINNED — NOT YET ACTIVE**
Activate when experimental findings are stable enough to constrain a model.

## Intended role
Build and fit computational models that:
- Take VRDots stimulus parameters as input (dot positions, depth planes, timing, swap type)
- Predict psychophysical performance (accuracy, cueing effects)
- Distinguish between competing theoretical accounts (depth-plane grouping vs monocular confound,
  object-based vs feature-based attention)

## Candidate model classes to consider
- Motion coherence detector (e.g., Reichardt-style, with depth-plane weighting)
- Object-based attention model (grouping by common fate + depth-plane membership)
- Bayesian observer model (prior over depth-plane identity, noisy motion integration)
- Neural network processing pipeline (simulate low-level → mid-level → decision)

## Key phenomena the model must account for
- Dot cueing effect (CUED > UNCUED): present binocularly and monocularly
- Depth-field cueing (same plane advantage): present binocularly, absent monocularly
- ZdB enhancement (cued dot staying in plane boosts effect above N)
- ZdA attenuation (cued dot moving plane kills effect)
- Near/Far asymmetry (binocular only, Far > Near in N condition)
- Monocular rotation-reversal disruption (ZdA/ZdB look identical monocularly except for reversals)

## Resources when active
- `VRDots/Tools/Analysis/` — stimulus payload data for model input
- `VRDots/Agents/Literature/theory_doc.md` — theoretical constraints
- `DepthSwapCtrl_results_summary.md` — target behavioral data
- `factor-analysis.md` — quantitative effects to fit

## Note
Coordinate with Literature agent — model architecture should be grounded in
existing computational accounts of depth-plane grouping and motion coherence.
