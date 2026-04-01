# Catak et al. (2022) — Fixation and Performance Screening Methods
**Source**: Catak, Özkan, Kafaligonul & Stoner (2022). *Cortex* 151:89–104.
**Extracted**: 2026-04-01
**Purpose**: Reference for VRDots gamification entry task design — methods to verify that subjects can both fixate reliably and accurately report translations before entering the main experiment.

---

## Summary of Methods

### 1. Participants and Initial Screening

- 20 subjects recruited; **15 completed** (5 excluded for failing criterion performance in fixation training or practice — see below).
- Inclusion criteria: normal or corrected-to-normal visual acuity, no history of neurological disorders.
- All criteria established prior to data analysis.

---

### 2. Fixation Target Design

The fixation target was a **bull's eye with crosshair** (Thaler, Schütz, Goodale & Gegenfurtner, 2013 — cited as eliciting "reliable and stable fixation"):

```
  Outer ring: 0.6° diameter
  Inner circle: 0.24° diameter
  Crosshair: within inner circle

  [  (  *  )  ]   ← schematic (not to scale)
       ↑
  0.06° orientation bar inside inner circle
  (the fixation task target)
```

The bar inside the inner circle changed orientation from horizontal to vertical (and back) for **133 ms** with random onset timing on half of trials. This is the event subjects must detect to demonstrate they are fixating.

---

### 3. Fixation Training Session (§2.3) — the key screening procedure

Before any exposure to the main experiment, all potential participants completed a dedicated **fixation training session**. This served two purposes explicitly stated by the authors:

1. **Screen out subjects who could not reliably fixate** (including those who might track individual dots despite instruction not to)
2. **Substantially increase the cueing effect** — fixation training improved average performance in the main task (a practical as well as methodological benefit)

#### 3a. Individual threshold calibration

The orientation bar's luminance was individually calibrated so that the transition was **barely detectable** (at threshold contrast). The procedure:
- Subject adjusted green gun brightness (red gun fixed at maximum, 19.7 cd/m²) until a repetitive orientation transition was "barely detectable" at 60 Hz flicker
- Done 10 times for each of two conditions (central and peripheral) separately
- The mean threshold value across the 10 repeats was used for that subject throughout training and the main experiment
- This personalization minimized the effect of differential visual acuity between subjects

#### 3b. Two target locations — the diagnostic contrast

Training included two conditions presented interleaved:

| Condition | Target location | Logic |
|-----------|----------------|-------|
| **Central** | Bar inside the central fixation target | If subject makes an eye movement >0.6°, they cannot detect the central transition. Performance on this condition indexes fixation quality. |
| **Peripheral** | Same bar in a second bull's eye located **0.6° away** from center | If subject has a fixation break, they lose the peripheral target. Peripheral performance is impaired specifically by fixation breaks. |

The **difference between central and peripheral performance** is the diagnostic signal:
- High central + low peripheral difference → subject is fixating and sustaining it (transitions only detectable from the center when fixating, but peripheral transitions require no break to detect)
- The reverse (or collapsed) pattern → eye movements or breaks present

Formally: *"A high difference in detecting the transition between central and peripheral conditions suggests that the fixation was sustained."*

#### 3c. Training session structure

- 2 conditions × 108 trials per condition = **216 trials total**
- Purpose: train subjects to sustain fixation and screen their fixation stability

#### 3d. Inclusion criterion for fixation

To proceed to the main experiment, subjects were required to meet **both** of the following:
1. Performance **≥25% above chance level** on the central condition
2. **Same difference** between central and peripheral conditions (i.e., better central than peripheral, showing fixation is sustained)

*Operationally*: If a subject cannot detect the nearly-invisible orientation transition in the central target — which is only possible when fixating — they are excluded. The peripheral condition serves as a "sanity check" that the transition itself is detectable (if peripheral performance is also at chance, the stimulus is invisible, not the fixation poor).

---

### 4. Equiluminance Calibration (Heterochromatic Flicker Fusion)

Before training, each subject completed a **heterochromatic flicker fusion task** (Ives, 1912):
- Goal: equate the luminance of red and green dot fields so color differences are purely chromatic, not due to luminance contrast
- 2×2° square stimulus at 60 Hz flicker rate
- Red gun held at maximum (19.7 cd/m²); green gun adjusted until flicker was minimal
- Procedure repeated 10 times; average green gun value used for all subsequent sessions for that subject
- Ensures that any behavioral or ERP differences between red and green dot fields are not confounded by luminance differences

---

### 5. Practice Session Before Main Experiment

After passing fixation training, subjects completed a **practice session** before the main EEG session:
- **480 trials**: 240 cued + 240 uncued, no feature swaps (baseline no-swap conditions only)
- Purpose: ensure subjects understood the task and could achieve above-chance performance
- **Inclusion criterion**: correctly indicated translation direction on **>25% of trials** (>120/480)
  - This corresponds to **2× chance level** (chance = 12.5%, based on 8 possible directions)
  - Subjects who failed this were excluded from the main experiment

---

### 6. Trial Structure and In-Session Fixation Monitoring

Within the main experiment, fixation was enforced through trial repetition:

- Each trial began with a **subject-initiated key-press** (subject presses key when ready)
- **Variable fixation period**: 500–1000 ms of fixation before the first dot field appeared (allows fixation to stabilize before stimulus onset)
- Trials were **automatically repeated** if:
  - Subject responded earlier than **100 ms** after translation onset (anticipatory response)
  - Subject failed to respond within **1 sec after stimulus offset**
  - **Fixation break** occurred during the trial (detected and marked as skipped)
- Skipped (fixation break) trials were re-run later in the session
- Response window: 100 ms post-translation onset → 1 sec post-stimulus offset

---

### 7. Main Stimulus Parameters (for reference)

| Parameter | Value |
|-----------|-------|
| Aperture diameter | 3.3° |
| Dot density | 5 dots/deg² |
| Dot diameter | 0.05° |
| Rotation speed | 81°/sec |
| % coherently moving dots | 60% (remainder distributed across 7 other directions) |
| Translation duration | 133 ms |
| Translation speed | 2.26°/sec |
| Translation directions | 8 (compass rose; subjects mapped to numpad) |
| Viewing distance | 57 cm |
| Background luminance | 0.16 cd/m² |

---

### 8. Subject Attrition Summary

| Stage | N excluded | Reason |
|-------|-----------|--------|
| Fixation training | 5 | Failed fixation criterion and/or practice criterion |
| Main EEG session | 0 | (all remaining 15 completed) |
| EEG preprocessing (trial level) | ~8% of trials | Artifacts (oscillations, voltage jumps, eye blinks) |
| **Final N** | **15** | — |

---

## Commentary

### What worked well in this design

**The two-location fixation contrast is elegant.** Using both a central and peripheral fixation target simultaneously creates a built-in diagnostic: the fixation quality is not just "can you detect the bar" (which would confound acuity with fixation) but "can you detect it better at center than periphery," which specifically depends on fixation stability. Subjects who are tracking dots or breaking fixation will fail the pattern, not just the level.

**Individual threshold calibration is important.** Setting the bar transition at each subject's perceptual threshold ensures the task is equally demanding for all subjects regardless of acuity or contrast sensitivity. Without this, some subjects would pass trivially (high acuity) and others fail unfairly (low acuity) for reasons unrelated to fixation.

**The practice session criterion is appropriately set.** 2× chance (25%) is a conservative but achievable criterion. It ensures subjects understand the response mapping and can perform the translation discrimination at all before entering the EEG session.

**Trial repetition rather than exclusion.** Repeating fixation-break trials rather than discarding them maintains the trial count per condition, which matters for ERP averaging. For VRDots this also prevents the subtle bias that could arise if fixation-break trials were systematically associated with particular conditions (e.g., if subjects break fixation more often on uncued trials).

**Subject-initiated trial start.** The key-press to begin each trial gives the subject a moment to confirm they are fixating before the stimulus appears. This is simple and effective.

### Differences from VRDots context

**No eye-tracking.** Catak et al. used a behavioral fixation check (the orientation-transition task) rather than actual gaze measurement. This is appropriate for a lab setting with a chin rest at known viewing distance. VRDots runs on a head-mounted display (Quest) where eye-tracking is available via the device's built-in eye tracker (though not currently used). VRDots currently uses a fixation exclusion zone (radius ≥1.1°) enforced by the SmoothFixation component — a more direct method than Catak's behavioral proxy.

**Stereo/VR context.** Catak et al. used a standard monitor at 57 cm with a chin rest; head position was fixed. In VRDots, head movement is physically possible even if discouraged, and the vergence angle (fixation distance) must be set correctly for the stereo display to produce the intended disparities. The Catak fixation-training logic still applies conceptually but the implementation differs: the VR analog of a central/peripheral orientation transition task would need to be rendered in the headset.

**No equiluminance calibration needed.** VRDots currently uses same-color (COLOR_RED) conditions specifically to avoid color-channel confounds; the Catak equiluminance calibration is relevant only if running two-color conditions in VRDots.

**8-direction response mapping.** Catak used a numeric keypad (5 as center, surrounding keys as compass directions). VRDots uses a joystick/thumbstick response. The direction-reporting logic is equivalent in principle.

### Observation on training effects

Catak et al. note explicitly: *"training subjects to fixate accurately, and only including subjects that could do so reliably, substantially increased the average cueing effect."* This is a non-trivial finding — it suggests that some of the variance in cueing effects across individuals and studies may be explained by differences in fixation stability, not just in object-based attentional capacity. Poor fixators likely produce noisy or low-magnitude cueing effects even if their object-based attention is intact.

---

## Implications for VRDots Gamification Entry Task

The user's idea: use Catak-like methods as a **"passage into the project"** — a gamified screening phase that verifies a new subject (a) can fixate and (b) can accurately report translation direction, before being admitted to the main experiment.

### Proposed VRDots entry task structure

**Stage 1 — Fixation screening** (VR adaptation of Catak §2.3):
- Display the bull's eye fixation target (already implemented as SmoothFixation crosshair in VRDots)
- Add a brief orientation/flash event at the fixation center that occurs at unpredictable times
- Add a second target at a small eccentricity (~1–2° in VR terms)
- Task: report which location flashed (center vs. peripheral) via trigger/button
- Criterion: higher accuracy for center than periphery, both above chance
- This directly tests whether the subject is truly fixating vs. looking around
- Use the Quest's built-in eye tracker data as a parallel check if available

**Stage 2 — Translation direction screening** (Catak practice session §2.3):
- Show a single dot field (no second field) that translates briefly in one of the 8 directions
- Task: report translation direction via thumbstick
- Criterion: >2× chance (>25%) over, say, 80–120 trials
- This ensures the subject can actually see and report a translation before the cueing manipulation is introduced
- Can be made progressive: start with longer translations (200ms), step down to the 80ms used in the main experiment

**Stage 3 — Basic cueing demo** (gamification hook):
- Introduce the two-field display with a highly salient cue (exaggerated translation amplitude or duration)
- Demonstrate that the cue predicts the target field
- Let the subject discover the cueing effect before the difficulty is ramped up
- Only proceed to the main experiment after a brief practice block

**Gamification notes:**
- Each stage can be framed as "unlocking" the next level
- The fixation check could be presented as a calibration game ("keep your eye on the star") with visual feedback
- Translation direction reporting could be presented as a "motion tracking" game
- Subjects who fail Stage 1 could be given feedback and retry (the training effect Catak observed is real — subjects get better at fixating with practice)
- The Catak criterion (5/20 excluded) suggests roughly 25% of naïve subjects will need additional training or exclusion — worth planning for in subject recruitment

---

*Document created 2026-04-01. Update if VRDots fixation screening methods are modified.*
