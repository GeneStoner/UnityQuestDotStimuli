# VRDots — Data Files Guide

*G. Stoner · September 2026*

---

## Overview

Every experimental session produces **three files**, all named with the session timestamp:

```
vr_dots_session_YYMMDD_HHMM.tsv
vr_dots_session_YYMMDD_HHMM.tsv.meta.json
vr_dots_session_YYMMDD_HHMM.tsv.sidecar.json
```

Send all three files to Gene after every session. The `.tsv` contains the trial-by-trial results. The `.sidecar.json` contains the complete stimulus parameters. The `.meta.json` is a brief session summary.

---

## The trial data file (`.tsv`)

A tab-separated table. One row per completed trial, one column per variable. Open in Excel or any spreadsheet app.

### Key columns

| Column | What it means |
|--------|---------------|
| `Trial` | Trial number within the session (starts at 0) |
| `Experiment` | Internal experiment identifier (e.g. `DensityCompare_HighDens_v2`) |
| `Cond` | Whether the translating field appeared **later** (`CUED`) or **earlier** (`UNCUED`) |
| `TransDeg` | True translation direction in degrees (0°=right, 90°=up, 180°=left, 270°=down, and four diagonals) |
| `RespDeg` | Observer's reported direction in degrees |
| `SwapType` | What swapped at translation onset: `N`=nothing, `CM`=colors+motion directions both swap |
| `RTf` | Response time in milliseconds from translation onset |
| `DelayedFieldColor` | Which color field appeared later: `R`=red, `G`=green |
| `SeedA0`–`SeedB3` | Random seeds used to generate this trial's dot positions (enables exact replay) |
| `MkHash32` | Fingerprint of the motion trajectory — use to verify trial identity across sessions |

### Computing accuracy

A trial is **correct** when `TransDeg == RespDeg`.

```python
import csv

with open('vr_dots_session_YYMMDD_HHMM.tsv') as f:
    trials = list(csv.DictReader(f, delimiter='\t'))

cued   = [t for t in trials if t['Cond'] == 'CUED']
uncued = [t for t in trials if t['Cond'] == 'UNCUED']

def pct(rows):
    correct = sum(1 for t in rows if float(t['TransDeg']) == float(t['RespDeg']))
    return 100 * correct / len(rows) if rows else 0

print(f"CUED:   {pct(cued):.1f}%  (n={len(cued)})")
print(f"UNCUED: {pct(uncued):.1f}%  (n={len(uncued)})")
print(f"Cueing effect: {pct(cued) - pct(uncued):+.1f} pp")
```

Chance performance is **12.5%** (1 of 8 equally-spaced directions). A healthy session typically shows CUED ~60–70% and UNCUED ~25–35%, giving a cueing effect of +25–35 percentage points.

---

## The sidecar file (`.tsv.sidecar.json`)

The authoritative record of **exactly what stimulus was shown**. Always keep this alongside the `.tsv`. The most important section is `experiment_spec`.

### `experiment_spec` — the stimulus parameters

Every parameter that defines the stimulus is recorded here. Key fields:

| Field | Typical value | What it means |
|-------|--------------|---------------|
| `spec_name` | `Exp_DensityCompare_HighDens` | Name of the experiment asset loaded |
| `dot_size_deg` | `0.12` | Dot diameter in degrees of visual angle |
| `dots_per_field` | `173` | Dots per perceptual field (red or green) |
| `aperture_radius_deg` | `3.5` | Radius of the circular dot aperture in degrees |
| `view_distance_m` | `2.0` | Virtual viewing distance in metres |
| `sim_hz` | `90` | Simulation frame rate |
| `rotation_speed_deg_per_sec` | `81` | Background rotation speed |
| `translation_speed_deg_per_sec` | `2.26` | Translation speed |
| `translation_duration_ms` | `80` | How long translation lasts |
| `delayed_onset_ms` | `750` | Delay between field onsets (the cue) |
| `repeats_per_stimulus` | `8` | Trials per unique stimulus condition |
| `include_no_swap_baseline` | `true` | Whether N (no-swap) trials are included |
| `include_cm_swaps` | `true/false` | Whether CM (color+motion swap) trials are included |
| `fixation_exclusion_radius_deg` | `1.1` | Radius of the dot-free zone around fixation |

### `calibration_colors` — dot colors

```json
"calibration_colors": {
    "rgba_red":   [0.8,   0.2,   0.2,   1],
    "rgba_green": [0.133, 0.545, 0.133, 1]
}
```

These are the RGBA values used for red and green dots. They are set to approximate equal luminance (verified by flicker photometry).

### `stimulus_builder` — rendering method

Records how dots were rendered on screen:

| Field | Value | Meaning |
|-------|-------|---------|
| `use_screen_space_shader` | `true` | Dots drawn as flat quads (not 3-D spheres) |
| `use_fixed_aa_shader` | `true` | Fixed anti-aliasing — stable dot brightness |
| `dot_blend_mode` | `additive` | Color overlap adds; no occlusion between red/green |
| `respawn_when_out_of_bounds` | `true` | Dots that leave the aperture reappear inside it |

**Important:** if `use_fixed_aa_shader` is `false`, dot brightness may vary slightly with sub-pixel position. All sessions from 2026-09-16 onward use the fixed shader.

### `build_date`

The date and time the app was built (e.g. `2026-09-16 12:37`). Use this to identify which version of the code was running if there is ever a question about stimulus correctness.

---

## The meta file (`.tsv.meta.json`)

A brief session summary. Useful for a quick sanity check:

```json
{
  "experiment_name": "DensityCompare_HighDens_v2",
  "stats": {
    "target_number_trials": 512,
    "completed_trials": 513
  }
}
```

`completed_trials` may exceed `target_number_trials` by 1 because a trial that is re-queued (observer re-donned headset mid-session) adds one extra completion.

---

## Pulling data from the headset

With the Quest 3 connected via USB and USB debugging enabled:

```bash
adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ ~/VRDotsData/
```

This copies all session files to a folder called `VRDotsData` in your home directory. Send the three files for each session to Gene at `generstoner@gmail.com`.

---

## File naming

`vr_dots_session_260916_1240.tsv` = session recorded on **2026-09-16 at 12:40**.

The timestamp is set by the Quest's internal clock when the session begins. If the Quest clock is wrong, timestamps will be wrong — check the clock in Quest Settings if dates look implausible.

---

## Contact

Gene Stoner — `generstoner@gmail.com`
