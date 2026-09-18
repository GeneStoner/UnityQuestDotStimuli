# What limits performance and the cueing effect
*Working list of factors, what the data says about each, and what to do. 2026-09-18.*

The goal is the largest, most reliable cueing effect. Two things can shrink it: anything that lowers sensitivity into the floor of the 8-alternative task, and anything that adds noise without touching the cue. Items are ordered by how much they currently cost us.

## 1. Colour asymmetry (largest known cost)

**Evidence.** Across 111 archived sessions the red field is reported better than the green one, median +9.0 pp, and up to +59 pp in some sessions. In GS's practice block (200 ms translation), red 89.1% vs green 28.1%. Closing one eye took green to 60.9% while red barely moved (85.9%), so the cause is largely binocular. Both-red sessions show no asymmetry between the two fields (76.6% vs 79.7%), so the code treats the fields identically.

**Ruled out.** Translation duration, coherent fraction, subfield assignment and occlusion are identical for the two colours (code audit + both-red control). Equiluminance error is now small for GS: a careful flicker run gives green 0.668 against the 0.697 used, a 4% difference.

**Live candidates.** Chromatic aberration from the pancake lenses and from prism glasses, producing a colour-dependent vergence or blur difference; foveal calibration applied to a stimulus at 1.1–3.5° eccentricity; asymmetric masking (green in the presence of red).

**To do.** Binocular repeat with the current calibration; other-eye control; both-green practice block (`Exp_Practice_BothGreen`); session without prism glasses. Report d′ so the two colours can be compared without floor effects.

## 2. Operating point: floor and ceiling

The psychometric function for an 8-alternative task is steepest at **d′ ≈ 1.3, about 49% correct**; that is also where statistical power peaks. A fixed cueing effect measured with the uncued cell near 12.5% or the cued cell near 100% is compressed.

**Target.** Uncued 35–40%, cued 55–65%. GS's uncued cells (d′ ≈ 1.0) are well placed; cued cells (d′ ≈ 2.1) are past the steep region. Afife's whole range (d′ 0.22–0.58) is too low.

**To do.** Adjust translation duration per observer — the QUEST staircase (`useQuestAdaptive`) already exists but is unused. Report d′, not percent correct.

## 3. Response errors and bias

**Evidence.** Reported direction is `atan2` of the raw thumbstick vector in *controller* coordinates, snapped to 8 and subject to a deadzone: a rotated grip rotates the mapping. Response counts are far from uniform — GS χ²(7) = 55 (SW over-chosen 108 times vs 64 expected), Afife χ²(7) = 166 (E chosen 15 times, NE 113). Afife's error distribution is nearly flat, the signature of reporting difficulty rather than misperception.

**To do.** A short response-training block with feedback for new observers; consistent controller grip; optionally log the raw (pre-snap) angle and stick magnitude to separate boundary responses from genuine errors.

## 4. Attention lapses, blinks and fatigue

**Evidence.** GS within one 512-trial session: 48.4% (Q1), 57.0%, 57.8%, 46.9% (Q4) — warm-up and fatigue of about 10 pp each, though the cueing effect itself kept rising (+17.4 → +34.2 pp). Afife shows learning instead: 12.5% (chance) to 26.6%.

**Skipping a trial.** There is a mechanism, but it is indirect: pressing the trigger **without selecting a direction** cancels the trial. Cancelled trials are logged with `RespDeg = -1` and **re-inserted at a random position in the remaining queue**, so the trial is repeated later. There is no dedicated skip button and no record of *why* a trial was skipped.

**Policy.** Skipping should be reserved for a blink or an external disturbance, never for uncertainty — on an 8-alternative task a guess is informative and a skipped trial is not. Afife's 103 skipped trials in one session (20%) is far above what that policy implies.

**Done 2026-09-18.** The policy is in the observer instructions, and a skipped trial now shows "Trial skipped — it will be repeated later" in the headset instead of passing silently. **To do.** Consider a dedicated skip button with a logged reason. Consider interleaving easy catch trials (the 200 ms practice stimulus, ~10% of trials) so the lapse rate can be measured and divided out.

## 5. Fixation

Not verifiable: the Quest 3 has no eye tracking (the Quest Pro does). Nonius lines exist for a vergence check (`SmoothFixation.showNoniusLines`) but nothing confirms fixation during a trial. The fixation target is large — measured at 1.67° across, inside the 2.2° dot-free zone.

**To do.** Open. Options: a secondary fixation task (detect a brief dimming of the fixation target), or accept and document the limitation.

## 6. Stimulus sampling and direction

**Evidence.** Every trial draws a unique dot sample; nothing is yoked across conditions (512 unique seed sets per session, and `MkHash32` fingerprints the motion-type sequence, not the dots). Direction profiles vary 25–39 pp within a session but correlate only r = +0.28 between sessions, so most of that is sampling noise. Cardinal vs diagonal differs by about 2 pp across 50 sessions; GS's recent sessions show a larger diagonal advantage (7–15 pp), partly confounded with his response bias.

**To do.** Analyse with direction as a factor rather than pooling. Yoking seeds across conditions would remove stimulus-sampling variance, but the stable component looks small, so the gain is likely a point or two of standard error. **Pinned:** one dedicated session repeating 8 seeds 8 times each would measure the per-sample variance component directly and settle whether yoking is worth it.

## 7. Display and timing (resolved 2026-09-17/18)

Fixed today, listed so the history is clear: the app requested 60 Hz, which the Quest 3 does not support, so every session before 2026-09-17 ran at 72 Hz with translations about 9% shorter than intended; the scene rendered below panel resolution; and the flicker calibration never reached the stimulus. Sessions now record refresh rate, render scale and measured per-trial timing, so a repeat would be visible in the data.

## Housekeeping: why the trial count varies between sessions

Rows in a TSV = planned trials + one row per cancelled attempt. A cancelled trial is logged (`RespDeg = -1`) and then repeated, so a 512-trial session with 103 cancellations writes 615 rows, of which 512 carry responses. `meta.json` records `target_number_trials`, `completed_trials` and `requeued_trials`. Analyses should exclude `RespDeg = -1` rows, which `Tools/analyze_session.py` does automatically.
