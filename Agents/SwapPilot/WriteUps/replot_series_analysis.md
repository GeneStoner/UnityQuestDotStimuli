# Replot Series — Analysis as of 2026-05-18

**Experiment:** `PeakDensity_Replot*_v1` series  
**Parameters:** Ap 3.5° radius, 500 dots/field, 80 ms translation, 750 ms delayed onset, N (no swap) condition, single observer (G.S.)  
**Figure:** `Agents/SwapPilot/Figures/replot_series_summary.png`

---

## Motivation

Do observers use dot-identity continuity to perform the cueing task, and if so, which dots matter? At translation onset (tStart), dots in one or more subfields are randomly repositioned ("replotted") — breaking identity continuity for those dots while leaving their motion statistics unchanged. By varying *which* subfields are replotted while holding the total number of displaced dots constant, we can ask whether the disruption effect depends on the identity of the disrupted dots or merely on their count.

---

## Design

Each field has two subfields (~250 dots each):

| Label | Field | Motion at tStart | Role |
|---|---|---|---|
| **CT** | Translating | Linear (coherent) | Carries direction signal |
| **NT** | Translating | NonCoherent (noise) | Noise dots of translating field |
| **RA** | Non-translating | RotationCW/CCW | Half of competing field |
| **RB** | Non-translating | RotationCW/CCW | Other half (RA ≡ RB, symmetric) |

---

## Conditions and results

| Condition | Replotted | N dots | CUED | UNCUED | Grand mean | Δ | n/arm |
|---|---|---|---|---|---|---|---|
| NoReplot | — | 0 | 63.3% | 28.5% | 45.9% | +34.8pp *** | 256 |
| ReplotCT | CT | 250 | 30.5% | 19.2% | 24.9% | +11.3pp *** | ~643 |
| ReplotRA | RA | 250 | 58.6% | 40.2% | 49.4% | +18.4pp *** | 256 |
| ReplotRA+RB | RA+RB | 500 | 59.0% | 38.3% | 48.6% | +20.7pp *** | 256 |
| ReplotBoth | CT+NT+RA+RB | 1000 | 23.4% | 24.6% | 24.0% | −1.2pp n.s. | 256 |

---

## Factor analysis (GLM)

OLS linear probability model on trial-level data (N = 2,823 trials). Effect coding: CT (0/1 → −1/+1), R (0/0.5/1 → −1/0/+1 continuous), Cue (UNCUED/CUED → −1/+1).

**Grand mean** = 36.2%

| Term | Effect (pp) | 95% CI | p | sig |
|---|---|---|---|---|
| CT → grand mean | −23.5 | [−26.8, −20.3] | <.001 | *** |
| R → grand mean | +0.9 | [−2.7, +4.6] | .61 | n.s. |
| CT×R → grand mean | −1.8 | [−5.4, +1.8] | .33 | n.s. |
| CT×Cue → CT effect on Δ | −9.8 | [−13.0, −6.5] | <.001 | *** |
| R×Cue → R effect on Δ | −6.6 | [−10.3, −3.0] | <.001 | *** |
| CT×R×Cue → 3-way | +0.4 | [−3.2, +4.0] | .83 | n.s. |

---

## Key findings

### 1. Two separable, additive mechanisms

CT replotting and R replotting affect the cueing advantage through completely different routes:

- **CT mechanism**: reduces grand mean accuracy (task gets harder for everyone) AND reduces the cueing advantage. Both arms fall. The coherent translating dots are necessary for direction discrimination.

- **R mechanism**: leaves grand mean unchanged but raises the UNCUED arm, reducing Δ. The competitor field's dot continuity actively suppresses performance on uncued trials. Disrupting that continuity releases the suppression.

The CT×R×Cue 3-way interaction is n.s. (+0.4pp), confirming these mechanisms are additive and independent. ReplotBoth performance (Δ ≈ −1pp) is consistent with the sum of both effects collapsing Δ to zero.

### 2. Competitor suppression saturates at a single subfield (RA ≈ RA+RB)

| R | UNCUED (CT=0) |
|---|---|
| 0 (NoReplot) | 28.5% |
| 0.5 (RA, 250 dots) | 40.2% |
| 1.0 (RA+RB, 500 dots) | 38.3% |

Replotting one of the two rotating subfields (RA, 250 dots) produces essentially the same UNCUED rise as replotting both (RA+RB, 500 dots). The effect appears threshold-like: disrupting any portion of the competitor's continuity releases attentional suppression, with no further benefit from disrupting the full competitor field.

### 3. The cueing advantage decomposes into two orthogonal DVs

- **Grand mean** = (CUED + UNCUED) / 2 — reflects direction discriminability; affected by CT, not R.
- **Cueing effect Δ** = CUED − UNCUED — reflects differential cue utility; affected by both CT and R independently.

Analyzing only Δ would obscure the distinct mechanisms. CT and R both reduce Δ by ~10pp each, but through entirely different arms.

---

## Tentative conclusions

1. **Translating field identity supports direction discrimination.** Losing CT (coherent translating dot continuity) degrades the observer's ability to determine which direction the cued field moved — grand mean drops ~24pp. This is consistent with observers using dot-identity tracking across the rotation→translation boundary to accumulate coherent motion evidence. *(Note: CT replot also costs one coherent motion vector — see caveat below.)*

2. **Competitor field identity mediates attentional suppression.** The always-on (non-cued) field's dot continuity during rotation appears to maintain attentional capture, suppressing performance on uncued trials. When that continuity is broken (RA or RA+RB replot), the suppression releases and uncued accuracy rises ~10pp.

3. **The two mechanisms are genuinely separable.** The additivity of CT and R effects, their distinct signatures (grand mean vs UNCUED arm), and their independence in the GLM all point to distinct underlying processes. One supports perceptual extraction of the translation direction; the other reflects attentional allocation between the two competing fields.

4. **Competitor suppression does not scale linearly with disrupted-dot count.** RA (250 dots) ≈ RA+RB (500 dots) for the UNCUED rise. A threshold effect: disrupting any continuity in the competitor field is sufficient; more disruption adds nothing. This may reflect an all-or-nothing property of attentional object representation.

---

## Caveats

**One-fewer-coherent-frame confound (CT conditions only).** When CT is replotted at tStart, the motion vector from frame tStart−1 → tStart is non-coherent (dot jumps to new random position). This means the observer gets one fewer clean coherent motion sample (~11ms fewer at 90Hz). The CT effect on grand mean could partly reflect this reduced translation evidence rather than (or in addition to) lost dot identity. A future control: a no-replot condition with translation duration shortened by one frame (≈ 69ms instead of 80ms) would isolate the frame-count contribution.

---

## What remains to be done

### Priority conditions (confound-free — do not involve CT):
1. **ReplotNT** (NT, 250 dots): sanity check. Expected null. Confirms noise dots carry no identity information relevant to the cueing effect.
2. **ReplotNTRA** (NT+RA, 500 dots): reference condition at matched N. If NT is null, NT+RA ≈ RA — confirms that a 250-dot disruption of NT adds nothing on top of RA's saturating competitor effect.

### Priority conditions (involving CT — confound acknowledged):
3. **ReplotCTNT** (CT+NT, 500 dots): full translating field, matched N to RA+RB. Tests: does CT+NT reduce Δ more than CT alone?
4. **ReplotCTRA** (CT+RA, 500 dots): cross-field combination. Tests additivity of CT and RA effects at matched N.

### Future control:
5. **Short-translation control**: NoReplot with 69ms translation (6 frames). Quantifies the one-fewer-frame contribution to the CT effect on grand mean.

### Replication:
6. All existing conditions are single-session (except CT, which has 5 sessions). Multiple sessions needed to stabilize estimates, particularly RA (1 session, n=256/arm) and ReplotBoth (1 session).

---

*Analysis: `Agents/SwapPilot/Analysis/` — see `replot_comparison.py` (figure) and inline GLM in conversation.*  
*Sessions: 260422_1431 (NoReplot), 260504_112x (CT), 260518_1341 (RA), 260518_0802 (RA+RB), 260518_0950 (ReplotBoth)*  
*Last updated: 2026-05-18*
