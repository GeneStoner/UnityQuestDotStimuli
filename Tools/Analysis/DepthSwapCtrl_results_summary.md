# DepthSwapCtrl Results Summary
*Generated 2026-03-30*

## Experiment Design

**Asset**: `Exp_DepthSwapCtrl` (`DepthSwapCtrl_005m`)
**Depth separation**: 0.05m (Near=1.975m, Far=2.025m at 2m view distance)
**Both fields red** (same color, `balanceDelayedFieldColor=false`)
**192 trials**: 2 cond × 8 headings × 2 rot configs × 3 swap types × 2 depths × 1 rep

### Swap Conditions

| Code | Description |
|------|-------------|
| N    | No swap. Translating dots stay in their original depth planes. |
| ZdA  | S0↔S2 depth swap at tStart. **Cued dot (S2) moves Near→Far.** Both translators end up in Far (ZdA CUED) or Near (ZdA UNCUED). |
| ZdB  | S1↔S3 depth swap at tStart. **Cued dot (S2) stays Near.** Companion non-coh (S1) moves Far→Near. Both translators end up in Near (ZdB CUED) or Far (ZdB UNCUED). |

**Design rationale**: ZdA and ZdB are matched for number of depth swaps (both swap 2 dots) and motion disruptions. The only difference is whether the cued coherent translator changes depth plane (ZdA) or stays (ZdB). Controls for disruption per se.

### Translation logic (CUED/UNCUED)
- CUED: S2=Coherent, S1=NonCoherent (delayed-field dots translate)
- UNCUED: S0=Coherent, S3=NonCoherent (non-delayed-field dots translate)
- Rotation follows depth-plane group membership (ZdA/ZdB); no color-follows-plane

---

## Sessions

| Session | Notes |
|---------|-------|
| 260330_1853 | Binocular, 192/192 complete |
| 260330_2012 | **Monocular — left eye closed**, 192/192 complete (1 requeued) |

---

## Binocular Results (260330_1853)

### Overall cueing by swap
| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N    | 65.6% (21/32) | 31.2% (10/32) | +34.4pp | ** (p=0.006) |
| ZdA  | 46.9% (15/32) | 34.4% (11/32) | +12.5pp | n.s. (p=0.309) |
| ZdB  | 78.1% (25/32) | 21.9%  (7/32) | +56.2pp | *** (p<0.0001) |

### Cueing by swap × depth (n=16 per cell)
| Swap | Depth | CUED | UNCUED | Δ | p |
|------|-------|------|--------|---|---|
| N    | Near  | 56.2% | 43.8% | +12.5pp | n.s. |
| N    | Far   | 75.0% | 18.8% | +56.2pp | ** |
| ZdA  | Near  | 43.8% | 50.0% | −6.2pp  | n.s. |
| ZdA  | Far   | 50.0% | 18.8% | +31.2pp | † |
| ZdB  | Near  | 81.2% | 25.0% | +56.2pp | ** |
| ZdB  | Far   | 75.0% | 18.8% | +56.2pp | ** |

---

## Monocular Results (260330_2012, L eye closed)

### Overall cueing by swap
| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N    | 43.8% (14/32) | 34.4% (11/32) | +9.4pp  | n.s. |
| ZdA  | 31.2% (10/32) | 25.0%  (8/32) | +6.2pp  | n.s. |
| ZdB  | 43.8% (14/32) | 22.6%  (7/31) | +21.2pp | n.s. |

Overall accuracy: binocular 46.4% → monocular 33.5%

### Cueing by swap × depth (n=16 per cell)
| Swap | Depth | CUED | UNCUED | Δ | p |
|------|-------|------|--------|---|---|
| N    | Near  | 50.0% | 31.2% | +18.8pp | n.s. |
| N    | Far   | 37.5% | 37.5% |  0.0pp  | n.s. |
| ZdA  | Near  | 25.0% | 25.0% |  0.0pp  | n.s. |
| ZdA  | Far   | 37.5% | 25.0% | +12.5pp | n.s. |
| ZdB  | Near  | 37.5% | 23.5% | +14.0pp | n.s. |
| ZdB  | Far   | 50.0% | 18.8% | +31.2pp | † (p=0.063) |

---

## Geometric Analysis: Depth-Change-Induced Positional Shifts

When a dot changes depth plane, it physically shifts in each eye's image. The shift is:
- **Cyclopean (average)**: proportional to eccentricity × |Δ(1/d)|
- **Disparity change**: IPD × |Δ(1/d)| = 2.71 arcmin (eccentricity-independent)
- **Translation distance** for comparison: 10.8 arcmin

| Eccentricity | Cyclopean shift (Near→Far) | As % of translation |
|---|---|---|
| 0°   | 0.0 arcmin | 0% |
| 1.0° | 1.5 arcmin | 14% |
| 2.0° | 3.0 arcmin | 28% |
| 3.5° | 5.3 arcmin | 49% |

**Key implication per condition** (which translator changes depth at tStart?):

| Condition | Coherent translator | Non-coh translator |
|-----------|--------------------|--------------------|
| N CUED    | no depth change    | no depth change |
| ZdA CUED  | **Near→Far** (confound!) | stays |
| ZdB CUED  | stays Near         | **Far→Near** |
| N UNCUED  | no depth change    | no depth change |
| ZdA UNCUED| **Far→Near** (confound!) | stays |
| ZdB UNCUED| stays Far          | **Near→Far** |

In ZdA, the dot being judged (coherent translator) simultaneously translates AND jumps depth — adding a spurious, eccentricity-scaled positional shift to the motion signal. In ZdB, only the non-coherent distractor changes depth.

---

## Interpretation and Conjecture

### What's clear
1. **ZdA kills cueing** (binocular): effect drops from +34pp to +12pp (n.s.). Plausible accounts: (a) monocular positional confound — the depth change adds spurious motion to the coherent translator; (b) depth-plane grouping disrupted — cued dot leaves its original plane.
2. **ZdB enhances cueing** (binocular): effect rises to +56pp***. Plausible accounts: (a) coherent translator has no depth-change confound; (b) companion non-coh dot joining the cued dot's plane increases within-plane grouping coherence.
3. **Far > Near cueing effect** (N condition binocular): Near=+12pp n.s., Far=+56pp**. The asymmetry is eccentricity/projection-independent (translation orthogonal to depth).
4. **N-Far collapses monocularly** (0.00pp): the Far advantage is specifically stereoscopic — it requires binocular depth perception. Consistent with depth-plane grouping being the driver.

### What's unclear (single session, n=16 per cell)
- Whether ZdB-Near collapse monocularly (+14pp n.s.) reflects genuine loss or just power
- Whether ZdA's cueing reduction is the monocular confound, depth-plane disruption, or both
- The mechanism of Far > Near: perhaps beyond-fixation objects are treated as "background," making coherent motion against that background more salient; or fixation vergence slightly favors Far plane processing

### Open questions
- **Right-eye-closed monocular session**: left eye may be a cleaner test (right eye has floaters). If effects recover toward binocular, general vision quality was suppressing the monocular session.
- **Replication**: all cells n=16; patterns are suggestive but not conclusive.
- **Stimulus verification**: triple-check that ZdA/ZdB depth assignments and rotation group assignments are correct before over-interpreting.
- **Monocular confound isolation**: could add a control condition where depth changes at a time OTHER than tStart to isolate the confound from the grouping effect.

---

## Analysis Scripts
- `gen_hypothetical_traj.py` — reference trajectory figure (N/ZdA/ZdB × CUED/UNCUED)
- `plot_results_with_traj.py` — combined trajectories + performance per session
- `analyze_vr_dots_v2.py` — standard per-session analysis
- `bino_vs_mono_comparison.png` — key comparison figure (in /tmp/quest_pull2/)
