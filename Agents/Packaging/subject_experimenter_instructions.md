# VRDots — Subject and Experimenter Instructions

*G. Stoner · September 2026*

---

## Part 1 — Instructions for the Subject

### What the experiment is about

You will watch two overlapping fields of moving dots inside a VR headset. The dots rotate continuously. At unpredictable moments, one group of dots will briefly translate (slide) in a straight line. Your job is to judge which direction those dots moved.

You will not be told which group of dots will move on any given trial. Part of what we are studying is whether your visual system can track and maintain information about a group of objects over time — even when those objects are mixed with another group.

---

### The task: 8-direction judgment

After each brief movement, report the direction the dots traveled. There are 8 possible directions — the 4 cardinal directions and the 4 diagonals:

```
   NW   N   NE
     ↖  ↑  ↗
  W ←     → E
     ↙  ↓  ↘
   SW   S   SE
```

Use the **right thumbstick** on the controller to point in the direction you perceived the motion. Push the stick toward North for upward motion, toward East for rightward motion, and so on for the diagonals.

---

### How to register your response (step by step)

1. **Wait** for the dots to move. (They will rotate continuously; you are waiting for the brief translation.)
2. **Push the thumbstick** in the direction you thought the dots moved. A visual indicator will appear confirming which direction is registered.
3. **Press the trigger once** to lock your choice. The indicator changes to confirm the lock.
4. **Press the trigger a second time** to submit your answer. The next trial begins.

> **Tip:** You can change your direction after Step 2 — just push the thumbstick somewhere new. If you change direction after locking (Step 3), the lock releases automatically and you can re-select.

> **If you confirmed by accident** (pressed trigger without selecting a direction): the trial will be silently re-added to the end of the session and repeated later. There is no penalty.

---

### Fixation

Keep your gaze on the **small white target at the center** of the display throughout each trial. This is important — eye movements during the trial can interfere with what you perceive.

The fixation target is a small ring with a dot in the center. Focus on it and try not to move your eyes, even when the dots translate. If you notice your eyes wandering, bring them back to the center before pressing the trigger to start the next trial.

---

### Session length and breaks

- A typical session is **512 trials**, which takes approximately **15–20 minutes**.
- You may take off the headset between trials (after you hear/see the trial end). The experiment will wait for you to press the trigger before starting the next trial.
- If you feel any discomfort (eye strain, nausea), stop and inform the experimenter.

---

### Quick reference card

| Action | Controller |
|--------|-----------|
| Start next trial | Right trigger |
| Indicate direction | Right thumbstick (push toward motion) |
| Lock direction | Right trigger (first press after selecting) |
| Confirm response | Right trigger (second press after locking) |
| Change direction after lock | Move thumbstick to new direction (lock releases) |

---

---

## Part 2 — Instructions for the Experimenter

### Before the first session: flicker calibration

The experiment uses red and green dot fields. For the results to be interpretable, these two colors must appear **equally bright** to the observer. Because green is photopically brighter than red at equal display values, we measure each observer's personal isoluminance point using a brief calibration procedure.

**Calibration is done once per observer** and stored on the headset. It takes about 5 minutes.

#### What is flicker photometry?

When a display alternates rapidly between two colors (here: 15 times per second), the observer perceives a flickering sensation if the two colors differ in brightness. As the brightness difference is reduced, the flicker weakens. At the isoluminance point — where red and green appear equally bright to that observer — the flicker is minimized or disappears entirely. This method is sensitive and reliable.

#### Running the calibration

1. Load the **FlickerCalibration** scene in Unity and build/deploy it to the Quest (or keep it pre-installed as a separate app).
2. The observer sees a flickering disk alternating between red and green.
3. **Task for observer**: Push the **right thumbstick up or down** to increase or decrease the green brightness until the flicker is as weak (or invisible) as possible.
4. When satisfied, press the **right trigger** to record that trial's setting.
5. Repeat for all 10 trials (starting values are randomized). The system averages the results automatically.
6. Calibration is saved to the headset. **It persists across sessions** — you do not need to repeat it unless you are running a different observer.

> **If calibration already exists:** the app will offer the option to skip calibration and use the saved values. For a new observer, always run fresh calibration.

#### Signs of good calibration

- The observer reports the flicker is nearly gone at their chosen setting.
- Repeated settings across 10 trials are reasonably consistent (± 10% variation is normal).
- If one observer's setting is very different from others (~50% lower or higher green), check that they understood the task.

---

### Running an experimental session

#### 1. Check the headset

- Charge the Quest to at least 50% before starting.
- Ensure USB debugging is enabled (one-time setup — see the Quick Reference guide).
- Confirm controllers are charged and paired.

#### 2. Load the correct experiment

1. In Unity: open `Assets/Scenes/UpToDateScene`.
2. In the **Hierarchy**, click `TrialBlockManager` → find `TrialBlockRunner` in the Inspector.
3. Confirm the **Spec** slot contains the correct asset (Gene will specify which one).
4. Confirm both **Use Screen Space Shader** and **Use Fixed AA Shader** are ticked on the `StimulusBuilder` component.
5. **Cmd+S** (save), then `File → Build Settings → Build and Run`.

#### 3. Seat the observer

- Adjust the headset for comfort and clear vision. The dots should look sharp and evenly bright across the display.
- Remind the observer of the fixation instruction and the two-stage response procedure (see Part 1 above, or hand them the Quick Reference card).
- Tell them the experiment will wait for their trigger press before each trial — they set the pace.

#### 4. Starting the session

The headset shows:

- **"VRDots"** banner with the experiment name below it.
- **"Trigger: start"** at the bottom.
- A green status line: **"Controllers ready"** — if this is red, check USB/controller pairing before proceeding.

The observer selects the experiment with the thumbstick (if multiple options are shown) and presses the trigger to begin.

#### 5. During the session

- The experiment runs unattended. The observer self-paces between trials.
- If the observer needs to pause: they take off the headset. The next trial waits indefinitely for a trigger press.
- If an observer accidentally confirms without selecting a direction, the trial is silently requeued — no intervention needed.
- **Do not stop the app mid-session** unless necessary — data is written continuously, but an interrupted session may have an incomplete final trial.

#### 6. After the session — pull the data

With the Quest still connected via USB:

```bash
adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ ~/VRDotsData/
```

Each session produces three files. Send all three to Gene at `generstoner@gmail.com`:

```
vr_dots_session_YYMMDD_HHMM.tsv
vr_dots_session_YYMMDD_HHMM.tsv.meta.json
vr_dots_session_YYMMDD_HHMM.tsv.sidecar.json
```

See the **Data Files Guide** for a full explanation of what each file contains.

---

### Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| "Waiting for controllers..." in red | Controller not paired or battery dead | Re-pair controller; check battery |
| Experiment does not start after trigger | Wrong scene loaded, or spec slot empty | Check Unity Inspector setup |
| Dots look dim or uneven | Flicker calibration not loaded | Re-run calibration for this observer |
| Session shows "Trial 1 of 0" | Spec slot was empty at build time | Re-assign spec and rebuild |
| Observer feels nausea | Normal VR discomfort | Stop session; rest 10+ min before retry |

---

## Contact

Gene Stoner — `generstoner@gmail.com`
