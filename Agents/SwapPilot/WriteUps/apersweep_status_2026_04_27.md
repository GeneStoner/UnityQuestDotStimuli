# AperSweep — Status as of 2026-04-27

## What was built today

### New C# framework: variable-duration trials
All changes are in the wip/quest-pilot branch.

**`ExpSpecTestPhase.cs`**
- Added `public float[] translationDurations_ms` field (empty = fixed-duration fallback)
- Added `SampleTranslationDurationFrames(System.Random rng)` — samples uniformly from list, quantizes to 90Hz frame grid

**`TrialBlockRunner.cs`** — in `NextTrial()`:
- Samples duration from list, patches `translationEndFrame` and `totalFrames` on current trial
- `totalFrames` fixed to `tStart + max(durations) + 400ms` so ALL dots (noise and coherent) display for identical duration regardless of which level was sampled
- New columns `PresentedDurFrames` and `PresentedDurMs` written to TSV

**`StimulusBuilder.cs`** — `HandleOutOfBounds()`:
- Now also replots dots that drift INTO the exclusion zone (was only checking outer aperture)

**`CsvLogger.cs`**:
- Two new TSV columns after `TotalFrames`: `PresentedDurFrames`, `PresentedDurMs`

### New assets — aperture sweep (Axis 1: ~5 dots/deg², vary aperture)
All assets: N + D + Da + Db conditions, 8 duration levels, `repeatsPerStimulus=2` → 512 trials/block.

| Asset | Aperture | Dots | Excl. zone | Fixation arm |
|-------|----------|------|------------|--------------|
| `Exp_SubfieldSwap_AperSweep_Ap1.asset` | 1.0° | 16 | 0.5° | 0.5° |
| `Exp_SubfieldSwap_AperSweep_Ap165.asset` | 1.65° | 43 | 0.5° | 0.5° |
| `Exp_SubfieldSwap_AperSweep_Ap25.asset` | 2.5° | 98 | 0.75° | 0.75° |
| `Exp_SubfieldSwap_AperSweep_Ap35.asset` | 3.5° | 192 | 1.1° | 1.0° |

Duration levels (all assets): **20, 40, 65, 90, 130, 178, 250, 350ms**
At 90Hz these quantize to: 22, 44, 67, 90, 133, 178, 244, 356ms.

Fixation and exclusion zone scale proportionally with aperture. Dot size fixed at 0.08°.

---

## Sessions run today

| Session | Asset | n | Notes |
|---------|-------|---|-------|
| 260427_1554 | AperSweep_Ap35_v1 | 513 | Old level set (11–178ms, pre-rebuild) |
| 260427_1645 | AperSweep_Ap35_v1 | 38 | Aborted — slow rotation (lights off → tracking loss) |
| 260427_1741 | AperSweep_Ap35_v1 | 59 | Aborted — same |
| 260427_2007 | AperSweep_Ap35_v1 | 513 | New level set (20–350ms) ✓ use this |

**Slow rotation root cause:** Quest inside-out tracking cameras lost confidence (lights off). Frame rate drops from 90→72Hz; frame-based stimulus slows proportionally. Fix: keep lights on, keep Bluetooth on (controllers need it), only disable Wi-Fi during sessions.

Data location: `/tmp/quest_pull_apersweep/`

---

## Key results — Ap35 combined (n=1026, sessions 1554+2007)

Threshold analysis: Weibull fit to p(correct) vs log(duration). Criterion = 56.25% (midpoint above 8AFC chance). R = T_UNCUED / T_CUED.

| Cond | T_CUED | T_UNCUED | R | Note |
|------|--------|----------|---|------|
| N | 85ms | 426ms | **5.0** | T_UNCUED extrapolated past 356ms — read as R≥4 |
| D | 67ms | 290ms | **4.3** | T_UNCUED near range edge |
| Da | 104ms | 96ms | **0.92** | R≈1 — NO cueing advantage at 3.5° ✓ |
| Db | 108ms | 106ms | **0.98** | R≈1 — NO cueing advantage at 3.5° |

**Headline:** Da and Db completely eliminate cueing at 3.5° aperture. N and D show R≈4–5 (robust cueing). Consistent with fixed-duration HighDens results (Da≈0pp, N≈+22pp).

Figures:
- `Agents/SwapPilot/Figures/threshold_aperture_sweep_curves.png` — psychometric curves (accuracy)
- `Agents/SwapPilot/Figures/threshold_aperture_sweep_ratio.png` — R vs aperture summary
- `Agents/SwapPilot/Figures/threshold_precision_ap35.png` — raw R̄ (precision) vs duration, no fit

Analysis scripts:
- `Agents/SwapPilot/Analysis/threshold_aperture_sweep.py` — main Weibull threshold analysis
- `Agents/SwapPilot/Analysis/threshold_precision_ap35.py` — precision (R̄) version

---

## Known issues / pending fixes

1. **Time-based rotation not implemented** — rotation is still frame-based. Any frame rate drop (tracking loss, GC spike) appears as visible slowdown. Fix: use `Time.deltaTime` accumulation in `TrialBlockRunner.Update()` instead of fixed simDt step. Planned but not done.

2. **T_UNCUED extrapolated for N and D** — UNCUED psychometric function hasn't reached plateau by 356ms. Could add a single 400ms level to anchor the ceiling without making trials feel too long.

3. **Session file not visible in adb pull until app quits** — the Quest filesystem doesn't flush the file listing until the app exits. Use `adb shell ls ...` to check directly on device, then pull individually.

---

## Next steps (priority order)

1. **One more Ap35 session** (optional but recommended) — gets to ~24 trials/cell, better constrains T_UNCUED for N/D
2. **Run Ap25** — critical intermediate. Does Da collapse here (R≈1) or survive (R>1)? This pins the transition point.
3. **Run Ap165** — expected positive control (Da should survive, R>1)
4. **Implement time-based rotation** — prevents tracking-loss artifacts in future sessions
5. **Second observer** — all data is GS (author); needed before strong conclusions

**Scientific question being answered:** At what aperture does the Da (coherent-half swap) cueing collapse? We know it collapses at 3.5° (R≈1) and survives at 1.65° (from fixed-duration CatekExact: Da=+18.9pp). Ap25 is the critical test.

---

## Quick-start for tomorrow

```bash
# Pull data
adb shell ls /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ | grep tsv | sort
adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/vr_dots_session_XXXXXX.tsv /tmp/quest_pull_apersweep/

# Analyze new session
python3 Agents/SwapPilot/Analysis/threshold_aperture_sweep.py /tmp/quest_pull_apersweep/vr_dots_session_*.tsv

# Combined Ap35 analysis (all sessions)
python3 Agents/SwapPilot/Analysis/threshold_aperture_sweep.py \
  /tmp/quest_pull_apersweep/vr_dots_session_260427_1554.tsv \
  /tmp/quest_pull_apersweep/vr_dots_session_260427_2007.tsv

# Open figures
open Agents/SwapPilot/Figures/threshold_aperture_sweep_curves.png
open Agents/SwapPilot/Figures/threshold_aperture_sweep_ratio.png
```

Assets to run (in priority order): **Ap35** (one more), then **Ap25**, then **Ap165**.
Remember: lights on, Bluetooth on, Wi-Fi off.
