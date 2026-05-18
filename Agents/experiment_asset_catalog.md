# VRDots Experiment Asset Catalog

Assets used within the last 3 months. All run on Meta Quest 3, single observer (G.S.).
Common parameters unless noted: rotation 81°/s, translation 2.26°/s, 750 ms delayed onset, 300 ms pre-translation, 8AFC direction judgment.

---

## S&B Replication — Ap 2.0° radius, 63 dots/field

Matches Stoner & Blanc (2010) aperture and dot count exactly. Small fixation (excl 0.396°, sf=0.222).

| Asset | Conditions | Trans (ms) | Sessions |
|---|---|---|---|
| `Exp_StonerBlanc_Replication` | N + MC | 44 | 260430_1312, 260430_1512 |
| `Exp_StonerBlanc_Replication_HighDens` | N + MC | 80 | 260507_1312 (1 session, underpowered) |

---

## S&B Larger Aperture — Ap 3.5° radius, 192 dots/field

Same dot density as S&B (~5/°²) but larger aperture. Small fixation (excl 0.396°, sf=0.222) except LargeFix variant.

| Asset | Conditions | Trans (ms) | Sessions |
|---|---|---|---|
| `Exp_StonerBlanc_Replication_Ap35` | N + MC | 44 | 260501_0752, 260501_0949 |
| `Exp_StonerBlanc_Ap35_80ms` | N + MC | 80 | 260501_1420, 260501_1608 |
| `Exp_StonerBlanc_Ap35_LargeFix` | N + MC | 44 | 260502_0638, 260502_0729 (large fixation, excl 1.1°) |

---

## Density Parametric Series — Ap 3.5° radius, N only, large fixation (excl 1.1°)

All conditions: N (no swap) baseline only. 8 repeats/stimulus → ~512 trials/session.

| Asset | Dots/field | Density (dots/°²/field) | Sessions |
|---|---|---|---|
| `Exp_DensityCompare_VRDots` | 63 | 1.8 | 260421_1541 |
| `Exp_DensityCompare_HighDens` | 173 | 5.0 | 260422_0708 |
| `Exp_DensityCompare_Peak` | 500 | 14 | 260422_1431 |
| `Exp_DensityCompare_UltraHigh` | 1000 | 29 | 260422_1733 |

Key result: Δpp flat ~+34 pp across 63–500 dots, drops to +25 pp at 1000 (CUED arm falls, UNCUED stable).

---

## Density + Swap Series — Ap 3.5° radius, large fixation (excl 1.1°)

| Asset | Dots/field | Conditions | Trans (ms) | Sessions |
|---|---|---|---|---|
| `Exp_DensityCompare_Peak_ColorMotionSwap` | 500 | N + MC | 80 | 260423_1053 |
| `Exp_DensityCompare_UltraHigh_ColorMotionSwap` | 1000 | N + MC | 80 | 260502_1304 |
| `Exp_DensityCompare_Peak_Simult` | 500 | N only, delayedOnset=0 ms | 80 | 260423_0725 (control) |
| `Exp_NoContinuity_Peak_ColorMotionSwap` | 500 | N + MC, replot translating field coherent dots at tStart | 80 | 260504_1121/1122/1327/1329/1608 |

Key results:
- Peak (500): MC cueing +16.8 pp *** — survives swap
- UltraHigh (1000): MC cueing +0.8 pp n.s. — abolished
- Simult: Δ = −1.6 pp n.s. — confirms onset timing is causal

---

## SubfieldSwap / Catek Series — Ap 1.65° radius, 43 dots/field, small fixation (excl 0.5°, sf=0.47)

Catek-matched parameters (Catek et al. 2022). 80 ms translation. 2 repeats/stimulus → ~512 trials/session.

Condition codes: **N** = no swap; **D** = full subfield dot reassignment; **Da** = partial swap variant A; **Db** = partial swap variant B; **M** = motion swap only; **C** = color swap only; **MC** = combined motion+color swap.

| Asset | Conditions | Sessions |
|---|---|---|
| `Exp_SubfieldSwap_CatekExact` | N + D + Da + Db | 260424_1801 and earlier |
| `Exp_SubfieldSwap_CatekExact_NDb` | N + Db | 260427_0707/1003/1217, 260514_1611 |
| `Exp_SubfieldSwap_CatekExact_NMoCol` | N + M + C + MC (separately) | 260515_0848, 260517_1243/1322/1432/1522 |
| `Exp_SubfieldSwap_MCvsDb_Ap165` | MC + Db (no N baseline) | 260429_1031 and MCvsDb sessions |

Key result (NMoCol, 5 sessions pooled): N=+10.0pp*, M=+15.3pp***, C=+17.5pp***, MC=+14.7pp*** — all conditions survive. 2³ factor analysis: F1 (onset cue) only significant; F2 (color), F3 (competing rotation) null.

---

## Aperture Sweep — Ap 1.65° / 2.5° / 3.5° radius, N + D + Da + Db

Identical dot density (5/°²/field) across apertures. Tests Da/Db collapse threshold.

| Asset | Ap radius | Dots/field | Excl radius | Sessions |
|---|---|---|---|---|
| `Exp_SubfieldSwap_AperSweep_Ap165` | 1.65° | 43 | 0.52° | 260428_1001 |
| `Exp_SubfieldSwap_AperSweep_Ap25` | 2.5° | 98 | 0.79° | 260429_1252 |
| `Exp_SubfieldSwap_AperSweep_Ap35` | 3.5° | 192 | 1.1° | 260427_1554/2007, 260428_0703 |

Key result: Da/Db collapse (R≈1) at Ap 3.5° radius; Da/Db survive (R≈1.6) at Ap 1.65° radius. Threshold between 1.65° and 2.5° radius diameter.

---

## Replot Series — Ap 3.5° radius, 500 dots/field, N only, large fixation (excl 1.1°)

Tests which field's dot-identity continuity drives the cueing effect. All new assets require a Unity rebuild (new C# field `replotNonTranslatingAtTStart` added 2026-05-17).

| Asset | What is replotted at tStart | Data status |
|---|---|---|
| `Exp_PeakDensity_NoReplot_v1` | Nothing — full continuity | **Existing data** (= DensityCompare_Peak sessions) |
| `Exp_PeakDensity_ReplotTranslating_v1` | Coherent dots of translating field only | **Existing data** (= NoContinuity sessions 260504_112x) |
| `Exp_PeakDensity_ReplotNonTranslating_v1` | All dots of non-translating (competing) field | **No data — priority** |
| `Exp_PeakDensity_ReplotBoth_v1` | All dots of both fields (total discontinuity) | **No data — priority** |

---

*Last updated: 2026-05-18*
