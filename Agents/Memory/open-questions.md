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

2. **Far > Near cueing asymmetry**
   Consistent across sessions at 0.05m. N-Far collapses monocularly (0.56→0.00pp) → stereoscopic in origin.
   Mechanism unclear: fixation vergence bias? Background/foreground weighting? Far dots more groupable stereoscopically?
   Note: projection is orthogonal (translation in XY, depth in Z), so no geometric account.

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

---

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
