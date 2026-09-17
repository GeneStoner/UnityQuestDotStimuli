# VRDots Experiment Asset Catalog

All runs on Meta Quest 3, single observer G.S. unless noted.

*Last updated: 2026-09-11*

---

## Data File Location

All session data lives in `Agents/Data/` (top level) and `Agents/Data/files/` (early pilot subset).
Naming: `vr_dots_session_YYMMDD_HHMM.tsv` + `.tsv.meta.json` + `.tsv.sidecar.json`.
Identify the experiment from the `Experiment` column in the TSV (added 2026-03-24; absent in pre-pilot sessions).

---

## Common Parameters (all experiments unless noted)

| Parameter | Value |
|-----------|-------|
| Observer | G.S. (single subject) |
| Device | Meta Quest 3 |
| View distance | 2.0 m |
| Dot size | 0.08° |
| Rotation speed | 81 °/s |
| Translation speed | 2.26 °/s |
| Translation duration | 80 ms (except S&B Replication = 44 ms) |
| Delayed onset | 750 ms |
| Pre-translation hold | 300 ms |
| Sim rate | 90 Hz |
| Task | 8AFC heading (0–315° in 45° steps); chance = 12.5% |

Timing per trial: Field A visible from t=0; Field B appears at t=750 ms; translation 1050–1130 ms; post-translation to 1530 ms.

### Fixation configurations

Three named fixation types are used across experiments. The dot exclusion radius is the inner zone where no dots are spawned. It scales with aperture (~31% of aperture radius in the aperture sweep series).

**Type A — Large** (all stereo depth experiments; 2D Baseline; Density series; AperSweep Ap35)

- Dot excl. radius: 1.1°; fixation dot radius: 0.15°; ring: inner 0.20°, outer 0.50°; crosshair arm: 1.0°

**Type B — S&B small** (S&B Replication Ap2 and Ap35 variants)

- Dot excl. radius: 0.396°; fixation dot radius: 0.059°; ring: inner 0.079°, outer 0.198°; crosshair arm: 0.396°; scale factor: 0.222

**Type C — Catek** (SubfieldSwap CatekExact; AperSweep Ap165)

- Dot excl. radius: 0.5°; fixation dot radius: 0.10°; ring: inner 0.10°, outer 0.25°; crosshair arm: 0.5°; scale factor: 0.47

**AperSweep Ap25 only** (custom, proportionally scaled)

- Dot excl. radius: 0.79°; fixation dot radius: 0.11°; ring: inner 0.14°, outer 0.35°; crosshair arm: 0.71°

---

## Pre-Pilot Development Sessions (Dec 2025 – Jan 2026)

Sessions in `Agents/Data/`: `251216` through `260115`, plus `260117` and `260122`.
~200+ session files. No `Experiment` column in TSVs; no `experiment_name` in meta.json. Most have <64 completed trials. These are software development and testing sessions — **not scientific data**.

---

## 2D Baseline Sessions (March 2026)

Early pilot sessions in `Agents/Data/` and `Agents/Data/files/`. Marked by the absence of depth columns in TSVs.

### Baseline / MotionSwap / Dots50Swap

Asset: `Exp_Baseline` / `Exp_MotionSwap` / `Exp_Dots50Swap`

| Parameter | Value |
|-----------|-------|
| Aperture radius | 3.5° |
| Dots/field | 63 |
| Density | 1.64 dots/°² |
| Dot excl. radius | 1.1° (Type A) |
| Depth separation | 0 (fixation plane only) |
| Colors | R/G balanced |
| Swaps | None / Motion / Dots50 |
| Repeats/stimulus | 1 → 64 trials (Baseline), 128 trials (MotionSwap/Dots50Swap) |

| Session | Experiment | N | Notes |
|---------|-----------|---|-------|
| 260323_1534 | Baseline | 64 | First complete session |
| 260324_0716 | Baseline | 64 | 25% adjacent-direction errors → led to hysteresis fix |
| 260324_1010 | MotionSwap | 128 | |
| 260325_1039 | Dots50Swap | 128 | |

⚠️ Sessions 260323_1052 through 260323_1341 and 260323_1531 in `Agents/Data/`: abbreviated or development runs, <64 completed trials.

---

## Stereo Depth Series (March–April 2026)

### DepthBaseline

Asset: `Exp_DepthBaseline` — TSV experimentName: `DepthBaseline`

| Parameter | Value |
|-----------|-------|
| Aperture radius | 3.5° |
| Dots/field | 63 |
| Density | 1.64 dots/°² |
| Dot excl. radius | 1.1° (Type A) |
| Depth separation | 0.10 m (Near = 1.95 m, Far = 2.05 m from observer) |
| Colors | R/G balanced |
| Delayed field depth | Near and Far balanced |
| Swaps | None |
| Trials/session | 128 |

| Session | N | Notes |
|---------|---|-------|
| 260325_1831 | 128 | Session 1 |
| 260325_1914 | 126 | Session 2 |
| **Combined** | **254** | |

⚠️ Pre-fix asset (no `_v2` suffix). No Z/CZ swaps run here so depth-swap artifact is irrelevant.
**Key result**: Far cueing +62.2pp***, Near cueing −26.1pp, interaction z=8.12 (p<.0001).

---

### DepthBothPlanes / DepthSwap (early, brief)

Asset: `Exp_DepthBothPlanes` / `Exp_DepthSwap` — TSV experimentName: `DepthBothPlanes` / `DepthSwap`

| Session | Experiment | N | Notes |
|---------|-----------|---|-------|
| 260325_2013 | DepthBaseline | 128 | 0.03 m depth — same asset, lower depth parameter |
| 260326_0550 | DepthBothPlanes | — | Brief exploratory session |
| 260326_0821 | DepthSwap | — | Brief early depth-swap attempt, pre-fix |

⚠️ 260326_0821 is pre-fix with 100% depth swap (Z condition) — contaminated by transform.forward artifact. Not used in analyses.

---

### DepthSwapCtrl

Asset: `Exp_DepthSwapCtrl` — TSV experimentName: `DepthSwapCtrl_005m` (pre-fix) / `DepthSwapCtrl_005m_v2` (post-fix)

| Parameter | Value |
|-----------|-------|
| Aperture radius | 3.5° |
| Dots/field | 63 |
| Density | 1.64 dots/°² |
| Dot excl. radius | 1.1° (Type A) |
| Depth separation | 0.05 m (Near = 1.975 m, Far = 2.025 m) |
| Colors | Both fields RED (same color) |
| Delayed field depth | Near and Far balanced |
| Swaps | N + ZdA + ZdB |
| linkDepthColor | 0 |
| Trials/session | 192 (32/cell × 6 cells: 3 swaps × 2 depth planes) |

Swap definitions: **N** = nothing at tStart; **ZdA** = coherent subfields (S0+S2) exchange depth — cued translator moves to opposite plane; **ZdB** = incoherent subfields (S1+S3) exchange depth — cued translator stays in onset plane.

**Binocular sessions** (experimentName: `DepthSwapCtrl_005m`):

| Session | N | Notes |
|---------|---|-------|
| 260330_1853 | 192 | S1 |
| 260331_0621 | 192 | S2 — ⚠️ anomalous near-zero cueing across all conditions |
| 260401_1313 | 192 | S3 |
| 260401_1349 | 192 | S4 |
| 260401_1541 | 192 | S5 — ⚠️ fatigue (4th session same day) |
| 260401_1705 | 192 | S6 — ⚠️ fatigue |
| **Binocular total** | **1152** | |

**Monocular sessions**:

| Session | Eye | N | Notes |
|---------|-----|---|-------|
| 260330_2012 | R (L closed) | 192 | — floaters in R eye |
| 260331_1530 | R (L closed) | 192 | |
| 260331_1705 | L (R closed) | 192 | |
| 260331_1734 | L (R closed) | 192 | |
| **Monocular total** | | **769** | (5 trials excluded) |

⚠️ All sessions are pre-fix (`DepthSwapCtrl_005m`, no `_v2`). ZdA/ZdB are 50% depth swaps; artifact is present but attenuated (~26% UP in wrong responses vs 50% for 100% swap). The ZdB > ZdA cueing dissociation survives.
Sessions 260330_1619 through 260330_1849 (same day, earlier): likely aborted setup runs.
**Key result**: ZdA collapses to 0.0pp monocularly (purely stereoscopic); Near inversion is binocular only.

---

### DepthParam (Parametric Depth Separation)

Assets: `Exp_DepthParam_003m / 005m / 010m / 015m` — TSV experimentName: `DepthParam_003m` etc.

| Parameter | Value |
|-----------|-------|
| Aperture radius | 3.5° |
| Dots/field | 63 |
| Density | 1.64 dots/°² |
| Dot excl. radius | 1.1° (Type A) |
| Colors | R/G balanced |
| Swaps | None |
| Delayed field depth | Near and Far balanced |
| Trials/session | 128 (32/cell) |

| Session | Depth sep | Disparity at 2 m | N | Notes |
|---------|-----------|-----------------|---|-------|
| 260402_0716 | 0.03 m | ~1.5 arcmin | 128 | |
| 260402_0757 | 0.05 m | ~2.5 arcmin | 128 | |
| 260402_0624 | 0.10 m | ~5.2 arcmin | 128 | |
| 260402_0656 | 0.15 m | ~7.9 arcmin | 128 | |

⚠️ Single session per depth — underpowered (32 trials/cell). Second sessions planned but not collected.
⚠️ Pre-fix assets, but no depth swaps at tStart → artifact does not apply.
**Key result**: Near cueing crosses zero between 0.03 m (+12.5pp) and 0.05 m (−9.4pp). Far cueing locked at ~+47pp across all depths.

Sessions 260402_0549, 260402_0610, 260402_0618, 260402_1559 also present — likely aborted/setup runs.

---

### BothFar

Asset: `Exp_BothFar_005m` — Session: 260411_1225

Both fields placed on the Far side of fixation (depthBias offsets both planes forward). Depth separation 0.05 m, planes at +0.05 m and +0.10 m from fixation. Includes Z swap condition. Pre-fix asset; Z condition contamination attenuated at 0.05 m total swap magnitude.

---

### DepthColorLinked

Asset: `Exp_DepthColorLinked` — TSV experimentName: `DepthColorLinked_005m` (pre-fix) / `DepthColorLinked_005m_v2` (post-fix)

| Parameter | Value |
|-----------|-------|
| Aperture radius | 3.5° |
| Dots/field | 63 |
| Density | 1.64 dots/°² |
| Dot excl. radius | 1.1° (Type A) |
| Depth separation | 0.05 m |
| Colors | Near = Red (#CC3333), Far = Green (#228B22) — linked to depth (linkDepthColor=1) |
| Delayed field depth | Near and Far balanced |
| Swaps | ZdA + ZdB only (no N baseline) |
| Trials/session | 256 |

Swap definitions (color follows depth at tStart): **ZdA** (= ZdCoh when CUED) — coherent subfields (S0+S2) change depth+color; **ZdB** (= ZdNoi when CUED) — incoherent subfields (S1+S3) change depth+color, cued translator unchanged.

| Session | Exp in TSV | N | Notes |
|---------|-----------|---|-------|
| 260404_0940 | DepthColorLinked_005m | 256 | S1; strong ZdNoi > ZdCoh |
| 260404_1123 | DepthColorLinked_005m | 256 | S2; flatter |
| 260406_1001 | DepthColorLinked_005m | 256 | S3 |
| 260406_1034 | DepthColorLinked_005m | 256 | S4 |
| **Combined** | | **1024** | |

⚠️ All sessions pre-fix (no `_v2`). ZdA/ZdB are 50% swaps → artifact attenuated (~26/22% UP in wrong responses). Cueing dissociation (ZdNoi vs ZdCoh) is the primary finding; absolute UP accuracy at 90° heading should be treated with caution.
**Key result**: ZdNoi +25.8pp***, ZdCoh +7.0pp†; UNCUED flat — disruption is object-specific, not scene-level.

---

### DecoupledDots

Assets: `Exp_DecoupledDots_005m` (delayTranslator=1) + `Exp_DecoupledDots_Inv_005m` (delayTranslator=0; labels inverted in analysis)
TSV experimentName: `DecoupledDots_005m` (pre-fix) / `DecoupledDots_005m_v2` (post-fix)

⚠️ **Asset drift**: `Exp_DecoupledDots_005m.asset` on disk currently reads `experimentName: DecoupledDots_010m_v2` with `depthSeparation_m: 0.1` — it has been edited since data collection. All pilot data used 0.05 m. Do not trust current asset file; check the TSV `Experiment` column instead.

| Parameter | Value at time of data collection |
|-----------|----------------------------------|
| Aperture radius | 3.5° |
| Dots/field | 63 |
| Density | 1.64 dots/°² |
| Dot excl. radius | 1.1° (Type A) |
| Depth separation | 0.05 m |
| Colors | R/G balanced |
| linkDepthColor | 0 — color and depth swap independently |
| Delayed field depth | Near and Far balanced |
| Swaps | N + C + Z + CZ (2×2 color/depth factorial) |
| Trials/session | 512 |

Swap definitions: **N** = no swap; **C** = color only swaps at tStart; **Z** = depth only swaps at tStart; **CZ** = both swap.

**Pre-fix sessions** (experimentName: `DecoupledDots_005m`):

| Session | Variant | N valid | Notes |
|---------|---------|---------|-------|
| 260406_1532 | Normal | 514 | S1 |
| 260406_1754 | Inv | 512 | S2 (labels inverted) |
| 260407_0643 | Inv | 512 | S3 (labels inverted) |
| 260407_0731 | Normal | 513 | S4 — ⚠️ elevated UNCUED baseline; cueing only +4.8pp n.s. |
| **Pre-fix total** | | **2051** | |

⚠️⚠️ **ALL pre-fix sessions contaminated by transform.forward depth bug.** Z and CZ trials received ~19°/sec upward impulse at tStart (8.2× the translation signal). F1×F2 interaction (+32.7pp***) **cannot be trusted**. F1 dot cueing and F4 Near/Far asymmetry are clean (N and C conditions unaffected).
Sessions 260406_1708 and 260406_1711: likely aborted runs from same day.

**Post-fix session** (experimentName: `DecoupledDots_005m_v2`; bug fixed 2026-04-11):

| Session | N valid | Notes |
|---------|---------|-------|
| 260413_1846 | 512 | Single clean session |

Post-fix GLM: F1 dot cueing **+27.3pp*** (confirmed clean); F1×F2 collapses to **+7.8pp n.s.** More sessions needed to resolve the interaction. F4 Near/Far direction intact.
Sessions 260413_1118 through 260413_1814: development/artifact testing runs, not scientific data.

**Post-fix with disparity sign bug** (experimentName: `DecoupledDots_005m_v2`):

| Session | N | Notes |
|---------|---|-------|
| 260415_2242 | 512 | ⚠️ Disparity SIGN inverted — Near/Far labels encode opposite percept. Overall cueing valid; Near/Far breakdown excluded. |

Sessions 260415_2226, 260415_2235, 260415_2348: development runs around sign-bug discovery/fix.

---

## S&B Replication — Ap 2.0° radius

Matches Stoner & Blanc (2010) aperture and dot count exactly.

| Parameter | Value |
|-----------|-------|
| Aperture radius | 2.0° |
| Dots/field | 63 |
| Density | 5.01 dots/°² (matches S&B) |
| Dot excl. radius | 0.396° (Type B) |
| Translation duration | 44 ms |
| Swaps | N + MC |
| Repeats/stimulus | 4 → ~256 trials/session |

| Asset | Trans (ms) | Sessions | Notes |
|-------|-----------|----------|-------|
| `Exp_StonerBlanc_Replication` | 44 | 260430_1312, 260430_1512 | |
| `Exp_StonerBlanc_Replication_HighDens` | 80 | 260507_1312 | ⚠️ 1 session only, underpowered |

---

## S&B Larger Aperture — Ap 3.5° radius, 192 dots/field

Same dot density as S&B (~5 dots/°²) but larger aperture. Type B fixation except LargeFix variant.

| Parameter | Value |
|-----------|-------|
| Aperture radius | 3.5° |
| Dots/field | 192 |
| Density | 4.99 dots/°² |
| Dot excl. radius | 0.396° (Type B) — except LargeFix: 1.1° (Type A) |
| Swaps | N + MC |
| Repeats/stimulus | 4 → ~256 trials/session |

| Asset | Trans (ms) | Dot excl. radius | Sessions |
|-------|-----------|-----------------|----------|
| `Exp_StonerBlanc_Replication_Ap35` | 44 | 0.396° | 260501_0752, 260501_0949 |
| `Exp_StonerBlanc_Ap35_80ms` | 80 | 0.396° | 260501_1420, 260501_1608 |
| `Exp_StonerBlanc_Ap35_LargeFix` | 44 | 1.1° | 260502_0638, 260502_0729 |

---

## Density Parametric Series — Ap 3.5° radius, N only

All conditions: N (no swap) baseline only. 8 repeats/stimulus → ~512 trials/session.

| Parameter | Value |
|-----------|-------|
| Aperture radius | 3.5° |
| Dot excl. radius | 1.1° (Type A) |
| Depth | 0 (2D) |
| Swaps | None |
| Repeats/stimulus | 8 → ~512 trials/session |

| Asset | Dots/field | Density (dots/°²) | Session |
|-------|-----------|------------------|---------|
| `Exp_DensityCompare_VRDots` | 63 | 1.64 | 260421_1541 |
| `Exp_DensityCompare_HighDens` | 173 | 4.50 | 260422_0708 |
| `Exp_DensityCompare_Peak` | 500 | 13.0 | 260422_1431 |
| `Exp_DensityCompare_UltraHigh` | 1000 | 26.0 | 260422_1733 |

Key result: cueing Δpp flat ~+34pp across 63–500 dots; drops to +25pp at 1000 (CUED arm falls, UNCUED stable).

---

## Density + Swap Series — Ap 3.5° radius, dot excl. 1.1°

| Asset | Dots/field | Density (dots/°²) | Conditions | Trans (ms) | Sessions |
|-------|-----------|------------------|-----------|-----------|----------|
| `Exp_DensityCompare_Peak_ColorMotionSwap` | 500 | 13.0 | N + MC | 80 | 260423_1053 |
| `Exp_DensityCompare_UltraHigh_ColorMotionSwap` | 1000 | 26.0 | N + MC | 80 | 260502_1304 |
| `Exp_DensityCompare_Peak_Simult` | 500 | 13.0 | N only, delayedOnset=0 ms | 80 | 260423_0725 |
| `Exp_NoContinuity_Peak_ColorMotionSwap` | 500 | 13.0 | N + MC, replot coherent dots at tStart | 80 | 260504_1121/1122/1327/1329/1608 |

Key results: Peak (500 dots) MC cueing +16.8pp*** — survives swap; UltraHigh (1000) MC cueing +0.8pp n.s. — abolished; Simult Δ = −1.6pp n.s. — confirms onset timing is causal.

---

## SubfieldSwap / Catek Series — Ap 1.65° radius

Catek-matched parameters (Catek et al. 2022).

| Parameter | Value |
|-----------|-------|
| Aperture radius | 1.65° |
| Dots/field | 43 |
| Density | 5.03 dots/°² |
| Dot excl. radius | 0.5° (Type C) |
| Depth | 0 (2D) |
| Translation duration | 80 ms |
| Repeats/stimulus | 2 → ~512 trials/session |

Condition codes: **N** = no swap; **D** = full subfield dot reassignment; **Da** = partial swap A; **Db** = partial swap B; **M** = motion swap only; **C** = color swap only; **MC** = motion + color swap.

| Asset | Conditions | Sessions |
|-------|-----------|----------|
| `Exp_SubfieldSwap_CatekExact` | N + D + Da + Db | 260424_1801 and earlier |
| `Exp_SubfieldSwap_CatekExact_NDb` | N + Db | 260427_0707/1003/1217, 260514_1611 |
| `Exp_SubfieldSwap_CatekExact_NMoCol` | N + M + C + MC | 260515_0848, 260517_1243/1322/1432/1522 |
| `Exp_SubfieldSwap_MCvsDb_Ap165` | MC + Db (no N baseline) | 260429_1031 and MCvsDb sessions |

Key result (NMoCol, 5 sessions pooled): N=+10.0pp*, M=+15.3pp***, C=+17.5pp***, MC=+14.7pp***. Factor analysis: F1 (onset cue) only significant; F2 (color), F3 (competing rotation) null.

---

## Aperture Sweep — N + D + Da + Db, ~5 dots/°² across apertures

Dot density matched across apertures. Dot exclusion radius scales proportionally (~31% of aperture radius). Tests Da/Db collapse threshold.

| Asset | Ap radius | Dots/field | Density (dots/°²) | Dot excl. radius | Sessions |
|-------|-----------|-----------|------------------|-----------------|----------|
| `Exp_SubfieldSwap_AperSweep_Ap165` | 1.65° | 43 | 5.03 | 0.52° | 260428_1001 |
| `Exp_SubfieldSwap_AperSweep_Ap25` | 2.5° | 98 | 4.99 | 0.79° | 260429_1252 |
| `Exp_SubfieldSwap_AperSweep_Ap35` | 3.5° | 192 | 4.99 | 1.1° | 260427_1554/2007, 260428_0703 |

Key result: Da/Db collapse (R≈1) at Ap 3.5°; Da/Db survive (R≈1.6) at Ap 1.65°. Threshold between 1.65° and 2.5° radius.

---

## Replot Series — Ap 3.5° radius, 500 dots/field, N only, dot excl. 1.1°

Tests which field's dot-identity continuity drives the cueing effect. Assets require the `replotNonTranslatingAtTStart` C# field added 2026-05-17 (requires Unity rebuild).

| Asset | What is replotted at tStart | Sessions |
|-------|---------------------------|----------|
| `Exp_PeakDensity_NoReplot_v1` | Nothing — full continuity | (= DensityCompare_Peak) |
| `Exp_PeakDensity_ReplotTranslating_v1` | Coherent dots of translating field | (= NoContinuity sessions 260504_112x) |
| `Exp_PeakDensity_ReplotNonTranslating_v1` | All dots of non-translating field | **No data — priority** |
| `Exp_PeakDensity_ReplotBoth_v1` | All dots of both fields | **No data — priority** |
