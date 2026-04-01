---
name: VRDots Swap Conditions
description: All swap condition implementations — Motion, Color, Dots50, Depth (Z), Depth50 (Zd), ZdA, ZdB
type: project
---

## Status: Motion, Color, Dots50, Depth (Z), Depth50 (Zd), ZdA, ZdB all implemented.

## SwapFlags Enum (ExperimentSpec.cs)
```
[Flags] enum SwapFlags {
    None     = 0,
    Motion   = 1 << 0,  // "M"   — rotation directions swap
    Color    = 1 << 1,  // "C"   — field colors swap
    Dots50   = 1 << 2,  // "D"   — 50% dots swap field membership
    Depth    = 1 << 3,  // "Z"   — depth planes swap (100%)
    Depth50  = 1 << 4,  // "Zd"  — S0↔S2 swap depth planes; color follows plane (legacy)
    Depth50A = 1 << 5,  // "ZdA" — S0↔S2 swap; both translators land in Far; cued dot moves plane
    Depth50B = 1 << 6,  // "ZdB" — S1↔S3 swap; both translators in Near; cued dot stays in plane
}
```

Code mapping: N=None, M=Motion, C=Color, D=Dots50, Z=Depth, Zd=Depth50, ZdA=Depth50A, ZdB=Depth50B

## Swap Mechanics

### Motion Swap (M)
- At tStart: rotation directions exchange between all subfields
- Non-translating field immediately shows new direction
- Translation override masks translating subfields during [tStart, tEnd)
- Post-translation: both fields in swapped directions

### Color Swap (C)
- At tStart: field colors exchange (A gets delayedColor, B gets nonDelayedColor)
- Persists through and after translation

### 50% Dot Swap (D)
- At tStart: sub1 and sub3 exchange field membership
- Default membership: [A, A, B, B]. After swap: [A, B, B, A]
- Colors + rotation roles + depth follow field membership
- Translation: CUED = delayed dots (sub2, sub3) translate regardless of swap
  - CUED+D: Field B={sub2,sub1} → sub2=Linear, sub1=NonCoherent
  - UNCUED+D: Field A={sub0,sub3} → sub0=Linear, sub3=NonCoherent

### Depth Swap / 100% (Z)
- At tStart: depth planes exchange between ALL subfields
- Analogous to color swap but for stereo depth
- Depth follows field membership (affected by Dots50 swap)
- Perceptually very disruptive at 0.10m — both CUED and UNCUED collapse to near-chance
- Requires depthSeparation_m > 0 to be visible

### 50% Depth Swap (Zd) — added 2026-03-26
- At tStart: S0↔S2 exchange depth planes only (50% of dots physically move)
- S0 (Field A, Far) → Near; S2 (Field B, Near) → Far
- Rotation follows new depth-plane grouping:
  - Near group (S0, S3): rotation = aRot; Far group (S1, S2): rotation = bRot
  - S1 reverses (aRot→bRot); S3 reverses (bRot→aRot)
- Color follows depth-plane group (Near=nonDelayedColor, Far=delayedColor)
- Translation: CUED = delayed dots (sub2, sub3) translate — same as all conditions
- Inspector toggle: `includeDepthPartialSwaps`
- Result at 0.05m: cueing survives (+35.9pp***); attenuation only 8.9pp n.s.

### ZdA (Depth50A) — added 2026-03-30
- At tStart: S0↔S2 exchange depth planes. **Cued dot (S2) moves Near→Far.**
- Depth assignments after swap: S0→Near, S1→Far, S2→Far, S3→Near
- Rotation follows depth-plane group: Near(S0,S3)=curARot, Far(S1,S2)=curBRot
- **No color-follows-plane** (both fields same color in DepthSwapCtrl)
- Translation: CUED→S2(Linear/Far)+S1(NonCoh/Far); UNCUED→S0(Linear/Near)+S3(NonCoh/Near)
- Both translating dots end up in the SAME depth plane (Far for CUED, Near for UNCUED)
- Purpose: cued dot changes depth plane, pitting retinal position vs. depth-plane identity
- Inspector toggle: `includeDepth50ASwaps`
- ZdA and ZdB are **mutually exclusive per trial** — power-set filters out ZdA+ZdB combined

### ZdB (Depth50B) — added 2026-03-30
- At tStart: S1↔S3 exchange depth planes. **Cued dot (S2) stays Near.**
- Depth assignments after swap: S0→Far, S1→Near, S2→Near, S3→Far
- Rotation follows depth-plane group: Near(S1,S2)=curBRot, Far(S0,S3)=curARot
- **No color-follows-plane** (both fields same color in DepthSwapCtrl)
- Translation: CUED→S2(Linear/Near)+S1(NonCoh/Near); UNCUED→S0(Linear/Far)+S3(NonCoh/Far)
- Both translating dots end up in same depth plane (Near for CUED, Far for UNCUED)
- Purpose: control for ZdA — same number of depth swaps but cued dot stays in its plane
- Inspector toggle: `includeDepth50BSwaps`

### ZdA vs ZdB Design Rationale
Both conditions swap exactly 2 dots' depth planes and involve 2 rotation reversals — matched
for disruption. The ONLY difference: in ZdA the coherent (cued) translator changes depth plane;
in ZdB only the non-coherent distractor does. This controls for disruption per se.

### Geometric confound (ZdA/ZdB)
Depth change of 0.05m at 2m induces monocular positional shifts of 0–5 arcmin (scales with
eccentricity), up to 49% of the translation distance (10.8 arcmin) at aperture edge (3.5°).
In ZdA: coherent translator gets this spurious shift. In ZdB: only non-coh gets it.
This confound is present monocularly and could partially explain ZdA's cueing reduction.

### Stereo Depth System
- `depthSeparation_m` on ExperimentSpec: Z offset in meters. 0 = no depth
- `balanceDelayedFieldDepth`: if true, Near/Far balanced (doubles trials)
- `delayedFieldDepthCode` on PlannedTrial: 0=DEPTH_NEAR, 1=DEPTH_FAR
- `depthByFrame[]` on SubfieldTracks: per-frame DepthPlane (Fixation/Near/Far)
- StimulusBuilder.ApplyDepthOffsets(): shifts dots along viewing axis
  - Near = -depthOffset_m along transform.forward
  - Far = +depthOffset_m along transform.forward

### Same-Color Experiments (DepthSwapCtrl)
- `balanceDelayedFieldColor=false`: all trials use COLOR_RED
- `nonDelayedColor` forced = `delayedColor` in BuildEffectiveCondition when !balanceDelayedFieldColor
- This bypasses Unity Library cache staleness on rgbaGreen
- rgbaGreen value in asset is irrelevant for same-color experiments

### Swap Generation
Power-set algorithm with ZdA+ZdB mutual exclusion filter:
```csharp
int bothAB = (int)SwapFlags.Depth50A | (int)SwapFlags.Depth50B;
swapValues.RemoveAll(v => (v & bothAB) == bothAB);
```

## Key Design Principle: CUED = delayed dots translate
CUED is always defined by which dots translate, NOT by which depth plane the translation
is in. Delayed-onset dots (sub2, sub3) translating = CUED, regardless of swap type.

## Experiment Assets (Assets/ExperimentSpecs/)
| Asset | experimentName | depthSep | balanceDepth | Swaps | Trials |
|-------|---------------|----------|--------------|-------|--------|
| Exp_Baseline | Baseline | 0 | — | none | 64 |
| Exp_MotionSwap | MotionSwap | 0 | — | Motion | 128 |
| Exp_AllSwaps | AllSwaps | 0 | — | Motion+Color | 256 |
| Exp_Dots50Swap | Dots50Swap | 0 | — | Dots50 | 128 |
| Exp_DepthCheck_005m | DepthCheck_005m | 0.05m | false | none | 64 |
| Exp_DepthBaseline | DepthBaseline | 0.10m | true | none | 128 |
| Exp_DepthBothPlanes | DepthBothPlanes | 0.10m | true | none | 128 |
| Exp_DepthSwap | DepthSwap | 0.10m | true | Depth(Z) | 256 |
| Exp_DepthSwap50 | DepthSwap50_005m | 0.05m | true | Depth50(Zd) | 256 |
| **Exp_DepthSwapCtrl** | **DepthSwapCtrl_005m** | **0.05m** | **true** | **ZdA+ZdB** | **192** |

## Pilot Results
- Motion swap (100%): reduces cueing 27.1pp → 15.7pp
- Dots50 swap (50%): no effect 30.4pp → 34.4pp
- Depth 0.10m: massive Near/Far reversal — depth dominates
- Depth 0.05m N: both planes positive (Near=+33pp**, Far=+56pp***) — sweet spot
- Depth50 Zd 0.05m: cueing survives (+35.9pp***) — object-based, not depth-plane
- **ZdA 0.05m**: cueing +12.5pp n.s. — cued dot changing depth kills the effect
- **ZdB 0.05m**: cueing +56.2pp*** — cued dot staying in plane enhances the effect
- **Monocular (L eye)**: all effects attenuated; possibly confounded by right eye floaters

## TODO
- Right-eye-closed monocular replication (cleaner test)
- Triple-check ZdA/ZdB stimulus correctness (depth assignments, rotation groups)
- More DepthSwapCtrl sessions (n=16/cell is underpowered)
- Update analyze_vr_dots_v2.py for depth columns (backburner)
