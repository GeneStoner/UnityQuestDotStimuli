# Stimulus Specifications: Website Experiments

Generated 2026-07-27. Source: Unity `.asset` files in `Assets/ExperimentSpecs/` + `StimulusBuilder.cs`.

---

## Critical notes before reading the table

**Dot placement is in the annulus, not the full disk.**  
`StimulusBuilder.cs` calls `UniformAnnulus(rng, ApertureRadiusMeters, exclusionRadiusMeters)` for initial placement and all respawns. Dots are never placed in the central excluded zone. Therefore **`dotsPerField` = visible dots** — no hidden dots near fixation.

**Density on the website is reported using the full-disk area** (matching S&B's convention, where there was no exclusion zone). The effective density in the *visible annulus* is slightly higher; both figures are given below.

**Coherence: 50% per field** (confirmed in `collab-stimulus-comparison.md`). Half the dots in the translating field move coherently in the target direction; the other half are distributed randomly across the remaining 7 directions.

**Tangential speed distribution** assumes uniform area distribution in the annulus (the exact distribution produced by `UniformAnnulus`). For a dot at eccentricity *r*, tangential speed = ω × r, where ω = 81°/s. The statistics below are analytic for this distribution:
- v_min = ω × r_inner
- v_max = ω × r_outer
- v_median = ω × √[(r_outer² + r_inner²) / 2]
- v_mean = ω × 2(r_outer³ − r_inner³) / [3(r_outer² − r_inner²)]

---

## Parameters shared by all VRDots experiments

| Parameter | Value |
|---|---|
| Simulation rate | 90 Hz |
| Virtual viewing distance | 2.0 m |
| Dot size | 0.08° diameter |
| Rotation speed | 81°/s |
| Translation speed | 2.26°/s |
| Delayed onset | 750 ms |
| Pre-translation rotation | 300 ms |
| Dot colors | Red (0.8, 0.2, 0.2) · Green (0.133, 0.545, 0.133) |
| Depth plane | Both fields coplanar (zero disparity) |
| Rendering | Binocular (Meta Quest 3) |

---

## Stoner & Blanc (2010) original — for comparison

From the paper (not VRDots; included for cross-reference).

| Parameter | Value |
|---|---|
| Aperture | 4.0° diameter (2.0° radius) |
| Exclusion zone | None (point fixation) |
| Dot size | 0.03° (1 pixel on CRT) |
| Dots per field | ~63 |
| Dot density | 5.0 dots/deg² (full disk) |
| Rotation speed | 81°/s |
| Translation speed | 2.26°/s |
| Translation duration | 40 ms (3 frames at 75 Hz) |
| Coherence | 40–55% (variable) |
| Delayed onset | 750 ms |
| Pre-translation | 300 ms |
| Display | Trinitron CRT, 75 Hz, 57 cm |

Tangential speed range: 0 (center) – 162°/s (aperture edge); mean/median not well-defined without knowing fixation exclusion zone.

---

## VRDots S&B Replication
**Asset:** `Exp_StonerBlanc_Replication` (experimentName: `StonerBlanc_Replication_v1`)

| Parameter | Value |
|---|---|
| Aperture radius | 2.0° (4.0° diameter) |
| Exclusion zone radius | 0.396° |
| Visible annulus | 0.396° – 2.0° |
| Annulus area | 12.07 deg² |
| Full-disk area | 12.57 deg² |
| Dots per field | 63 |
| Dot density (annulus) | **5.22 dots/deg²** |
| Dot density (full disk) | 5.01 dots/deg² (matches S&B) |
| Translation duration | 44 ms (4 frames at 90 Hz) |
| Fixation style | Ring-and-crosshair (fixationScaleFactor 0.222) |
| Tangential speed — min | 32.1°/s |
| Tangential speed — max | 162.0°/s |
| Tangential speed — median | 116.8°/s |
| Tangential speed — mean | 111.5°/s |

---

## VRDots Çatak Replication
**Asset:** `Exp_SubfieldSwap_CatekExact_NMoCol` (experimentName: `SubfieldSwap_CatekExact_NMoCol_v1`)  
Also applies to: `Exp_SubfieldSwap_CatekExact`, `Exp_SubfieldSwap_CatekExact_NDb`, `Exp_SubfieldSwap_MCvsDb_Ap165`, `Exp_DensityCompare_Catek` — all share identical aperture/fixation parameters.

| Parameter | Value |
|---|---|
| Aperture radius | 1.65° (3.3° diameter) |
| Exclusion zone radius | 0.5° |
| Visible annulus | 0.5° – 1.65° |
| Annulus area | 7.77 deg² |
| Full-disk area | 8.55 deg² |
| Dots per field | 43 |
| Dot density (annulus) | **5.54 dots/deg²** |
| Dot density (full disk) | 5.03 dots/deg² (matches Çatak) |
| Translation duration | 80 ms |
| Fixation style | Ring-and-crosshair (fixationScaleFactor 0.47) |
| Tangential speed — min | 40.5°/s |
| Tangential speed — max | 133.7°/s |
| Tangential speed — median | 98.7°/s |
| Tangential speed — mean | 95.4°/s |

**Çatak et al. (2022) original (for comparison):** aperture 1.65° radius, 43 dots/field, 5 dots/deg², dot size 0.05°, translation 133 ms (0.30° displacement), 60 Hz CRT at 57 cm.

---

## Density Parametric Series
**Assets:** `Exp_DensityCompare_VRDots` (N=63), `Exp_DensityCompare_HighDens` (N=173), `Exp_DensityCompare_Peak` (N=500), `Exp_DensityCompare_UltraHigh` (N=1000)

All four conditions share identical aperture, fixation, and timing parameters:

| Parameter | Value |
|---|---|
| Aperture radius | 3.5° (7.0° diameter) |
| Exclusion zone radius | 1.1° |
| Visible annulus | 1.1° – 3.5° |
| Annulus area | 34.68 deg² |
| Full-disk area | 38.48 deg² |
| Translation duration | 80 ms |
| Fixation style | Large ring-and-crosshair (no fixationScaleFactor field — uses defaults) |
| Tangential speed — min | 89.1°/s |
| Tangential speed — max | 283.5°/s |
| Tangential speed — median | 210.1°/s |
| Tangential speed — mean | 203.2°/s |

Dot counts and densities by condition:

| Condition label | Dots/field | Density (annulus) | Density (full disk) |
|---|---|---|---|
| VeryLow | 20 | 0.58 dots/deg² | 0.52 dots/deg² |
| VRDots (Low) | 63 | 1.82 dots/deg² | 1.64 dots/deg² |
| HighDens (Medium) | 173 | 4.99 dots/deg² | 4.50 dots/deg² |
| Peak | 500 | 14.42 dots/deg² | 13.00 dots/deg² |
| VeryHigh | 750 | 21.63 dots/deg² | 19.49 dots/deg² |
| UltraHigh | 1000 | 28.84 dots/deg² | 25.99 dots/deg² |

*The density series shown on the website uses VRDots, HighDens, Peak, and UltraHigh (N=63/173/500/1000). VeryLow and VeryHigh were collected but are not on the public page.*

---

## High-Density Swap Experiments
**Assets:** `Exp_DensityCompare_Peak_ColorMotionSwap` (N=500), `Exp_DensityCompare_UltraHigh_ColorMotionSwap` (N=1000)

Same aperture and fixation as the density series (3.5° radius, excl 1.1°), same timing (80 ms translation). Adds combined motion+color swap (MC) condition alongside no-swap (N).

| Parameter | Peak MC | UltraHigh MC |
|---|---|---|
| Dots per field | 500 | 1000 |
| Density (annulus) | 14.42 dots/deg² | 28.84 dots/deg² |
| Density (full disk) | 13.00 dots/deg² | 25.99 dots/deg² |
| Tangential speeds | same as density series above | same as density series above |

---

## Aperture Sweep (not on public website; included for completeness)
**Assets:** `Exp_SubfieldSwap_AperSweep_Ap165`, `Exp_SubfieldSwap_AperSweep_Ap25`, `Exp_SubfieldSwap_AperSweep_Ap35`

All use the same dot density target (~5 dots/deg²) and 80 ms translation.

| Asset | Ap radius | Excl radius | Dots/field | Density (annulus) | v_min | v_max | v_median | v_mean |
|---|---|---|---|---|---|---|---|---|
| AperSweep Ap165 | 1.65° | 0.52° | 43 | 5.58/deg² | 42.1 | 133.7 | 99.1 | 95.8 °/s |
| AperSweep Ap25 | 2.5° | 0.79° | 98 | 5.54/deg² | 64.0 | 202.5 | 150.2 | 145.2 °/s |
| AperSweep Ap35 | 3.5° | 0.396° | 192 | 5.05/deg² | 32.1 | 283.5 | 201.7 | 191.2 °/s |

*Note: AperSweep Ap165 uses excl 0.52° (not 0.5° like CatekExact), giving a slightly different tangential speed min.*

---

## StonerBlanc_Replication_HighDens (not on public website)
**Asset:** `Exp_StonerBlanc_Replication_HighDens`

Same aperture as the S&B replication (2.0° radius, excl 0.396°) but 327 dots/field (~27 dots/deg²). Tests whether the cueing advantage persists at high density in the smaller aperture.

| Parameter | Value |
|---|---|
| Aperture radius | 2.0° |
| Exclusion zone radius | 0.396° |
| Dots per field | 327 |
| Density (annulus) | 27.08 dots/deg² |
| Translation duration | 80 ms |
| Tangential speeds (min/max/median/mean) | 32.1 / 162.0 / 116.8 / 111.5 °/s |

---

## Notes for modeling

- **The 1.1° exclusion zone in density experiments is very large** — it removes the innermost ~10% of the area. The minimum eccentricity for dots in those experiments is 1.1°, minimum tangential speed 89.1°/s. If models are sensitive to speed range or eccentricity distribution, this matters.

- **All VRDots experiments use 90 Hz**; one stimulus frame = 11.1 ms. Translation durations of 44 ms and 80 ms correspond to 4 and 7.2 frames respectively (80 ms is rounded — actual = 7 or 8 frames depending on implementation).

- **Translation displacement:** at 2.26°/s × 44 ms = 0.099° (S&B replication); at 2.26°/s × 80 ms = 0.181° (all others). Çatak's original: 2.26°/s × 133 ms = 0.30°.

- **Dot size relative to aperture:** 0.08° dot diameter in apertures ranging 3.3°–7.0°. At peak density (500 dots in 3.5° Ap), dots can overlap substantially.

- **Dot density unit clarification for modeling:** if using the annulus area (recommended — this is where dots actually live), use the "density (annulus)" column above. The "density (full disk)" column matches website and paper figures but slightly underestimates the actual packing.
