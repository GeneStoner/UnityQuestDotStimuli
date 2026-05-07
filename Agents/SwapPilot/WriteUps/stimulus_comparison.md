# Stimulus Parameter Comparison
**Stoner & Blanc (2010) · Catek et al. (2022) · VRDots (current build, 2026-04-21)**

---

## Parameter Updates — 2026-04-21

| Field | Value |
|---|---|
| Assets changed | `Exp_DecoupledDots_005m.asset`, `Exp_DecoupledDots_005m_Simult.asset`, `UpToDateScene.unity` |
| Viewing distance | ~~1.5 m~~ → **2.0 m** |
| Rationale | Quest 3 pancake lens focal plane ≈ 2.0 m. Previous 1.5 m created ~0.5 m vergence–accommodation mismatch. All other spec assets were already at 2.0 m. Binocular disparity for ±0.05 m depth separation at 2.0 m ≈ 5.3 arcmin — clearly perceptible and within Panum's fusional area. |
| Depth separation | ~~0.05 m~~ → **0.10 m** (increased to compensate for reduced disparity at 2.0 m) |
| experimentName updated | ~~DecoupledDots_005m_v2~~ → **DecoupledDots_010m_v2** (and Simult variant) |
| Binocular disparity | ~~~4.7 arcmin (1.5 m / 0.05 m)~~ → **~5.2 arcmin (2.0 m / 0.10 m)** — approximately matched |
| Scene GOs moved | SmoothFixation and DirectionalFeedbackSpot: z = 1.5 → 2.0 m (camera-local). DirectionalFeedbackSpot fallback viewDistance_m: 1.3 → 2.0. |
| Requires rebuild | Yes — reload scene and assets, then build APK before next session. |

---

## Platform & Display

| Parameter | Stoner & Blanc (2010) | Catek et al. (2022) | VRDots (2026) |
|---|---|---|---|
| Platform | CRT — Trinitron E500 | CRT — Mitsubishi 2070sb | **VR HMD — Meta Quest 3** |
| Refresh rate | 75 Hz | 60 Hz | 90 Hz |
| View distance | 57 cm | 57 cm | **2.0 m (virtual)** ~~was 1.5 m~~ |
| Display focal plane | 57 cm (screen surface) | 57 cm (screen surface) | ~2.0 m (Quest 3 pancake lens) ✓ now matched |
| Vergence–accommodation conflict | none | none | minimal at 2.0 m ✓ |
| Head restraint | Chin + forehead rest | Chinrest | **None (head-mounted)** |
| Luminance calibration | Yes (photometry implied) | Yes (SpectroCAL) | **No (no cd/m² on Quest)** |
| Environment | Dark, quiet room | Dark room | Controlled by headset |

---

## Dot Stimulus Geometry

| Parameter | Stoner & Blanc (2010) | Catek et al. (2022) | VRDots (2026) |
|---|---|---|---|
| Aperture diameter | 4.0° | 3.3° | **7.0° (~2× S&B)** |
| Aperture area | ~12.6 sq° | ~8.6 sq° | **~38.5 sq° (~3–4×)** |
| Dot diameter | 0.03° (1 pixel) | 0.05° | 0.08° |
| Dot density | 5.0 dots/sq° | 5.0 dots/sq° | **1.6 dots/sq°** |
| Dots per field (total) | ~63 (density × area) | ~43 (density × area) | 63 (set explicitly) |
| Rotation speed | 81°/sec | 81°/sec | 81°/sec ✓ |
| Translation speed | not in excerpt | 2.26°/sec | 2.26°/sec ✓ |
| Coherence (%) | not in excerpt | 60% | **not set in spec asset** |
| Stereo depth separation | none (2D) | none (2D) | **±0.10 m** ~~was ±0.05 m~~ |
| Binocular disparity (per plane) | — | — | **~5.2 arcmin** ~~was ~4.7 arcmin at 1.5 m / 0.05 m~~ |

---

## Trial Timing

| Event | Stoner & Blanc (2010) | Catek et al. (2022) | VRDots (2026) |
|---|---|---|---|
| Trial initiation | Subject key-press | Subject key-press | Trigger press ✓ |
| Pre-stimulus fixation | not specified | 500–1000 ms (variable) | Subject-paced (WaitingForStart) |
| Field A alone (delayed onset) | not in excerpt | 750 ms | 750 ms ✓ |
| Both fields rotating (pre-trans) | not in excerpt | 300 ms | 300 ms ✓ |
| Translation duration | not in excerpt | 133 ms (~8 frames @ 60 Hz) | **80 ms (~7 frames @ 90 Hz)** |
| Translation displacement | — | ~0.30° (133 ms × 2.26°/s) | **~0.18° (80 ms × 2.26°/s)** |
| Post-translation period | not in excerpt | 500 ms | 400 ms |
| Total active stimulus | — | ~1683 ms | ~1530 ms |

---

## Fixation Target

| Element | Stoner & Blanc (2010) | Catek et al. (2022) | VRDots (2026) |
|---|---|---|---|
| Style | Yellow dot only | Bull's eye + crosshair | Bull's eye + crosshair |
| Outer disc diameter | 0.40° (the spot itself) | 0.60° | 1.0° (~1.7× Catek) |
| Inner dot / circle diameter | — | 0.24° | 0.40° (= S&B spot size) |
| Crosshair | none | yes (thickness not reported) | yes, 0.12° thick, 2.0° total span |
| Crosshair justification | — | Thaler et al. (2013) | follows Catek / Thaler |
| Color | Yellow | not reported | White |
| Exclusion zone | not specified | not specified | 1.1° radius |

---

## Dot Colors & Equiluminance

| Parameter | Stoner & Blanc (2010) | Catek et al. (2022) | VRDots (2026) |
|---|---|---|---|
| Red luminance | 43.6 cd/m² | 19.7 cd/m² (max gun) | **RGBA (0.80, 0.20, 0.20) — no cd/m²** |
| Green luminance | 50.0 cd/m² | adjusted via HFP | **RGBA (0.13, 0.55, 0.13) — no cd/m²** |
| Equiluminance method | HFP (Ives 1912) | HFP (Ives 1912) | HFP (Ives 1912) |
| HFP flicker rate | not specified | 60 Hz | **20 Hz** |
| HFP stimulus shape | not specified | 2°×2° square | annulus (0.5°–2.0° radius) |
| HFP trials | not specified | 10 repeats, averaged | 20 trials, averaged |

---

## Open Issues

### ✓ Viewing distance / vergence–accommodation conflict — RESOLVED
Changed from 1.5 m → 2.0 m in `Exp_DecoupledDots_005m.asset`, `Exp_DecoupledDots_005m_Simult.asset`, and scene GOs (SmoothFixation, DirectionalFeedbackSpot) moved to z = 2.0 m (2026-04-21). All spec assets now at 2.0 m.

### 1. Dot density — major parametric gap [CRITICAL]
S&B and Catek both use **5 dots/sq°**. VRDots uses **1.6 dots/sq°** — roughly 3× sparser. The explicit dot count (63/field) matches S&B's count, but the aperture was enlarged ~2× in diameter without scaling up the dot count. To match reference density at our 7° aperture: ~192 dots/field would be needed. This changes the signal-to-noise ratio of the global motion percept and limits direct quantitative comparisons.

### 2. No absolute luminance calibration on Quest [CRITICAL]
S&B and Catek both used photometers to verify display luminance in cd/m². Meta Quest 3 display luminance cannot be calibrated in situ — output varies with headset fit, IPD, and lens position, and the display uses a non-linear pipeline. VRDots HFP gives relative isoluminance but absolute values and display gamma are unknown. Comparability with prior cd/m²-based stimuli is limited.

### 3. Translation duration / displacement mismatch [CRITICAL]
Catek (and likely S&B) use **133 ms → 0.30° displacement** at 2.26°/s. VRDots uses **80 ms → 0.18° displacement** — 40% less travel. In frame count both are ~7–8 frames, making the rendering similar, but observers receive a substantially weaker kinematic signal. The choice should be documented with justification (e.g., 90 Hz frame budget) and the effect on cueing strength acknowledged.

### 4. Aperture size — 2× linear, ~4.5× area [MODERATE]
S&B: 4.0°, Catek: 3.3°, VRDots: 7.0°. The larger aperture may improve immersiveness in VR but changes the spatial scale of global motion pooling. With the current dot count (63/field), the aperture expansion compounds the density issue above. If maintained, the choice should be explicitly justified.

### 5. Coherence not defined in spec asset [MODERATE]
Catek specifies 60% coherence (remaining 40% distributed equally across the other 7 directions). VRDots has no *coherence_pct* field in `ExperimentSpec`; the value is in `StimulusBuilder.cs` and needs to be verified, documented, and added to the spec asset as an explicit parameter.

### 6. HFP flicker rate — 20 Hz vs 60 Hz [MODERATE]
Catek used 60 Hz flicker on a 60 Hz monitor (alternating every frame). VRDots uses 20 Hz. Isoluminance estimates are flicker-rate dependent. Whether 20 Hz and 60 Hz yield the same isoluminance point across different display technologies is not guaranteed and should be acknowledged in methods.

### 7. Translation speed not confirmed in S&B [MODERATE]
The 2.26°/s value appears in Catek and is used in VRDots, but the provided S&B excerpt does not list it. The full S&B paper should be checked to confirm this is the original value.

### 8. Fixation target ~1.7× larger than Catek [MINOR]
VRDots outer disc: 1.0°; Catek: 0.6°; S&B: 0.4° dot. The enlargement is reasonable for VR legibility but exceeds the Thaler et al. (2013) dimensions that Catek cited as optimal for fixation stability.

### 9. No fixation monitoring or online screening [MINOR]
Catek ran an extensive fixation training/screening session (exclusion criterion: <25% above chance on central fixation detection). S&B used chin + forehead rest. VRDots has no eye-tracker, no online fixation rejection, and no equivalent screening procedure. Fixation compliance is behavioral only.

### 10. Post-translation period — 400 ms vs 500 ms [MINOR]
Catek specifies 500 ms post-translation rotation. VRDots uses 400 ms (hardcoded in `MakeTrial()`). Should be made configurable in the spec asset rather than hardcoded, and the discrepancy noted in methods.

---

## Rationale: Virtual Viewing Distance (2.0 m)

### 1. Quest 3 optical design and the focal plane constraint
The Meta Quest 3 uses a pancake (folded-optics) lens system whose effective optical focal plane is approximately 2.0 m. At this virtual distance, the vergence demand imposed by binocular disparity and the accommodation demand imposed by the optics are approximately equal, minimising the VAC. Placing the stimulus at 2.0 m is therefore the principled choice for this hardware: it follows directly from the display's optical specification rather than from an arbitrary or convenience-based decision.

### 2. Stereo disparity at 2.0 m
For a depth plane offset by Δd = 0.05 m from fixation at viewing distance D = 2.0 m, with IPD = 63 mm:

```
δ ≈ IPD × Δd / [D × (D + Δd)] × (180/π × 60) ≈ 5.3 arcmin
```

This value is well above the stereo-acuity threshold (typically 0.5–1.0 arcmin) and well within Panum's fusional area (~6–10 arcmin foveal, larger in periphery). The disparity for the second depth plane (±0.10 m separation) is approximately 10.5 arcmin, also within the fusional range.

### 3. Comparison with prior work
Replicating the 57 cm viewing distance from prior work would be inadvisable: it would place the virtual scene ~1.4 m in front of the Quest 3 focal plane (severe VAC), and at 57 cm the 0.05 m depth separation would produce ~19 arcmin per eye — exceeding the fusional range for many observers.

### 4. Vergence posture and fatigue
At 2.0 m, vergence angle ≈ 1.8° (for IPD = 63 mm), which is close to the physiological resting vergence of most observers (~1–2°), minimising tonic vergence demand across a session.

### 5. Angular subtense
All stimulus parameters are specified in degrees of visual angle, so the angular geometry is identical regardless of viewing distance. Changing virtual viewing distance affects only the physical size of rendered objects (in metres) and the binocular disparity magnitude.

---

## References
- Banks, M. S., Read, J. C. A., Allison, R. S., & Watt, S. J. (2012). Stereoscopy and the human visual system. *SMPTE Motion Imaging Journal*, 121(4), 24–43.
- Hoffman, D. L., et al. (2008). Vergence–accommodation conflicts hinder visual performance and cause visual fatigue. *Journal of Vision*, 8(3), 33.
- Howard, I. P., & Rogers, B. J. (1995). *Binocular Vision and Stereopsis*. Oxford University Press.
- Lambooij, M., et al. (2009). Visual discomfort and visual fatigue of stereoscopic displays: A review. *Journal of Imaging Science and Technology*, 53(3).
- Schor, C. M. (1979). The relationship between fusional vergence eye movements and fixation disparity. *Vision Research*, 19(12), 1359–1367.
- Schor, C., & Tyler, C. W. (1981). Spatio-temporal properties of Panum's fusional area. *Vision Research*, 21(5), 683–692.
- Thaler, L., et al. (2013). What is the best fixation target? *Vision Research*, 76, 31–42.

---
*VRDots build: branch wip/quest-pilot. Spec assets updated 2026-04-21 (viewDistance_m 1.5→2.0 m).*
*References: Stoner & Blanc (2010) J. Vis.; Catek et al. (2022) Cortex 151:89–104.*
