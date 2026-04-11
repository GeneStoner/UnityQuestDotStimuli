# VRDots: Extending Transparent-Surface Selection into Stereoscopic VR
### A brief for Dr. Hulusi Kafaligonul
*Gene Stoner — April 2026*

> **Format note**: This document is plain Markdown. To convert to Word: `pandoc collaborator_brief_HK.md -o collaborator_brief_HK.docx`. Figures are in the `Figures/` folder alongside this document; insert them at the indicated positions when preparing a final version to share.

---

## Background

This work extends the delayed-onset surface-selection paradigm we used in Catak et al. (2022, *Cortex*) into virtual reality, adding stereoscopic depth as a new experimental variable. The core question: **does the attentional object representation that drives surface-based selection incorporate the object's depth-plane membership?**

The basic paradigm is unchanged from Catak et al.: two overlapping random-dot fields share the same aperture and rotate in opposite directions. One field (Field B) has a delayed onset. At a fixed interval after Field B's appearance (~293ms), one of the two fields translates briefly in one of eight directions, and the observer reports the translation direction (8AFC, chance = 12.5%). As in Catak et al., the delayed-onset field is far more likely to be correctly identified when it translates (CUED condition) than when the non-delayed field translates (UNCUED condition) — the temporal onset cueing effect.

The new addition: in a Meta Quest VR headset, the two fields are rendered at slightly different stereoscopic depths. This makes depth-plane membership a stable, manipulable feature of each surface.

---

## Experiment 1: DecoupledDots — disentangling color from depth

### Design

Four swap conditions, run at tStart (the moment translation begins):

| Condition | Color swap | Depth swap |
|-----------|-----------|-----------|
| N (no swap) | — | — |
| C (color only) | Yes | — |
| Z (depth only) | — | Yes |
| CZ (color + depth) | Yes | Yes |

"Swap" means the translating field exchanges one of its properties with the other field at tStart. Color and depth are manipulated independently (`linkDepthColor = 0`), so their contributions can be dissociated cleanly. The two fields are colored red and green; near = one color, far = the other; which is which is counterbalanced.

n = 2051 valid trials across 4 sessions (single observer GS).

### Stimulus design

> **[INSERT: `decoupled_traj_condensed_all.pdf`]**
> *Figure 1. Schematic trajectory figure for all four swap conditions. 4-page PDF, one page per swap condition (N/C/Z/CZ), 16 panels per page (8 rows × CUED/UNCUED). Title boxes indicate which features are continuous (✓) or disrupted (✗) for the cued field.*

The trajectory figure shows the key logic: in the Z and CZ conditions, the translating field changes depth plane at tStart — severing the continuity between the depth-plane representation established during the cue interval and the depth-plane identity of the field that actually translates. In the C condition, only color changes; the translating field stays in the same depth plane throughout.

### Main result

> **[INSERT: `decoupled_dots_depth_color_2x2.pdf`]**
> *Figure 2. Performance (% correct, Wilson 95% CI) for CUED (dark) and UNCUED (light) conditions, organized as a 2×2 grid: columns = depth continuity intact vs. disrupted; rows = color continuity intact vs. disrupted. Cueing advantage (Δ) shown with brackets. Right strip: depth and color marginals.*

The central finding is a strong interaction between temporal onset cueing and depth-plane continuity. The overall cueing advantage is large when the translating field maintains its depth-plane identity (N and C conditions: CUED ≈ 47–48%) and is approximately halved when depth-plane continuity is severed (Z and CZ conditions: CUED ≈ 31–33%). Color disruption alone (C condition) has essentially no effect relative to the no-swap baseline.

### GLM analysis

> **[INSERT: `decoupled_dots_glm2.pdf`]**
> *Figure 3. GLM2 — logistic regression with interactions. Left panel: log-odds coefficients and Average Marginal Effects (pp). Right panel: model-predicted vs. observed accuracy by condition.*

A logistic regression with interaction terms (F1 = dot cueing; F2 = depth-field continuity; F3 = color-field continuity) reveals:

| Factor | Average Marginal Effect | p |
|--------|------------------------|---|
| F1 Dot cueing | +5.8 pp | .053 † |
| F2 Depth continuity | +4.6 pp | .125 n.s. |
| **F1 × F2 interaction** | **+32.7 pp** | **<.001 ****** |
| F3 Color continuity | +0.9 pp | .638 n.s. |
| Near-plane penalty | −15.3 pp | <.001 *** |

The main effects of F1 and F2 are individually near zero; almost the entire signal concentrates in their interaction. **Depth-plane continuity benefits the observer only when combined with the temporal onset cue.** Color is null across all model specifications. The UNCUED arm remains near chance regardless of swap type — depth information alone is not sufficient to drive selection without the onset cue.

---

## Experiment 2: DepthColorLinked — object-specific disruption

### Design

A complementary experiment in which color and depth are always linked (Near = Red, Far = Green throughout). Two swap conditions:

- **ZdNoi** (translator stable): coherent translating dots maintain their depth plane; background incoherent dots change depth
- **ZdCoh** (translator changes): coherent translating dots change depth plane at tStart; background incoherent dots maintain their depth

Critically, **both conditions involve the same total amount of depth change in the scene** (50% of dots in each condition). The only difference is *which* dots change — translator or background.

n = 1024 valid trials across 4 sessions (single observer GS).

### Stimulus design

> **[INSERT: `depthcolorlinked_combined_condensed.pdf`]**
> *Figure 4. Schematic trajectory figure for DepthColorLinked. 2-page PDF (ZdA p.1 / ZdB p.2), 16 panels per page (8 rows × CUED/UNCUED). Four symbols represent the four subfields: filled/open triangles = CCW field (coherent/noise); filled/open circles = CW field (coherent/noise).*

### Main result

> **[INSERT: `depthcolorlinked_cueing.pdf`]**
> *Figure 5. Cueing performance for ZdNoi and ZdCoh conditions, CUED and UNCUED arms, split by Near/Far. Right strip: cueing effect (CUED − UNCUED) with 95% CI.*

| Condition | Cueing effect | p |
|-----------|--------------|---|
| ZdNoi (translator stable) | +25.8 pp | *** |
| ZdCoh (translator changes depth) | +7.0 pp | † |

Disruption when translator changes depth: −18.8 pp. Critically, the UNCUED arm is flat across both conditions (21.9% vs. 23.4%) — the depth change in the scene has no effect when there is no onset cue to bind to.

### GLM

> **[INSERT: `depthcolorlinked_glm.pdf`]**
> *Figure 6. GLM for DepthColorLinked. Same model structure as Experiment 1.*

Same structure as DecoupledDots: F1×F2 dominates (+16.5 pp**), main effects near zero, Near penalty large (−21.4 pp***).

---

## Cross-experiment comparison

> **[INSERT: `depth_disruption_comparison.pdf`]**
> *Figure 7. Cueing disruption by swap type across experiments (DepthSwapCtrl, DepthColorLinked, DecoupledDots). Y-axis: reduction in cueing effect relative to no-swap baseline.*

The DepthColorLinked result rules out a **dose-response** account: a 50% swap (ZdCoh) produces approximately the same disruption as a 100% swap (DecoupledDots Z). The total amount of depth change in the scene is not what matters — what matters is whether the depth change hits the coherent translating object specifically.

---

## Summary of key findings

1. **Depth-plane continuity is a constitutive feature of the attentional object.** When the cued translating surface changes depth plane at the moment of translation, cueing is approximately halved. This is not a general scene-disruption effect — it is specific to the identity of the attended object.

2. **Color is null.** Color swaps alone (condition C, DecoupledDots) produce no measurable disruption. The effect attributed to color in earlier linked experiments was a depth confound.

3. **The conjunction is necessary.** Depth information alone does not drive selection — the UNCUED arm is near chance throughout all depth experiments. The temporal onset cue is necessary; depth-plane identity modulates the *quality* of the selection initiated by the cue, not whether selection occurs at all.

4. **Far > Near asymmetry.** Performance is consistently better when the translating field is in the Far depth plane than the Near plane (approximately −15 to −21 pp Near penalty). This asymmetry is entirely stereoscopic: it disappears under monocular viewing. Its mechanism is unresolved but is a focus of ongoing work (see Open Questions below).

5. **Single observer (GS) throughout.** All findings need replication.

---

## Open questions and next steps

The most urgent priorities are:

- **Second observer** at the core conditions (DepthSwapCtrl binocular, then one DecoupledDots session). This is the gating step for publication — do the findings generalize?
- **SOA manipulation** — varying the delay between field onset and translation onset to test whether the Far > Near asymmetry is dynamic (builds up during the delay) or structural (present at all SOAs).
- **Parametric depth sweep** — second sessions at each tested depth separation to characterize the crossover at which Near cueing transitions from positive to penalized.

---

## Collecting data in your lab: what you would need

### Hardware

- **Meta Quest headset**: Quest 2, Quest 3, or Quest Pro. Quest 3 is preferred (better display, continuous IPD adjustment). Quest 2 is adequate for pilot work.
  - The critical stimulus is stereoscopic depth at ~2.5 arcmin disparity (0.05m separation at 2m). Quest 2 and 3 both support this reliably.
- **USB-C data cable** for transferring data from the headset to your computer (most USB-C cables work; confirm it passes data, not charge-only).
- A Windows or Mac computer for building the app and pulling data.

### Software and accounts

1. **Meta developer account** — free at developer.oculus.com (requires a Meta account and a named organization, also free). Required to enable developer mode on the headset.
2. **Unity Hub + Unity 6000.2.7f2** — the exact version must match. Install from Unity Hub (Installs → Archive tab). During installation, add the **Android Build Support** module (includes NDK/JDK — required for Quest builds).
3. **Android Debug Bridge (ADB)** — included with Android Studio, or available as a standalone platform-tools package. Used to pull data files from the Quest to your computer.
4. **Python 3.9+** with: `numpy`, `scipy`, `pandas`, `matplotlib`, `statsmodels`. Install with: `pip install numpy scipy pandas matplotlib statsmodels`.

### Getting the project

I will add you as a collaborator on the GitHub repository. Once added:

```
git clone -b wip/quest-pilot https://github.com/GeneStoner/UnityQuestDotStimuli.git
```

Open the project in Unity Hub (Add → point to the cloned folder). Unity will import assets on first open (5–20 minutes). All packages install automatically from the Unity registry — no manual package installation needed.

### Building and deploying

1. `File → Build Settings → Android → Switch Platform` (first time only)
2. Connect Quest via USB-C; confirm `adb devices` shows the headset (authorize on headset when prompted)
3. `Build and Run` — Unity builds the APK and installs it directly on the headset
4. On the headset: the app appears under **Unknown Sources** in the App Library

**One critical setting**: `Project Settings → Player → Other Settings → Active Input Handling` must be set to **"Both"**. If it is set to "New Input System" only, input will fail silently.

### Running an experiment

All experiment parameters are stored as configuration files (`ExperimentSpec` assets in `Assets/ExperimentSpecs/`). No code changes are needed to switch between conditions — drag the desired asset into the Inspector slot on the Experiment Manager. The experiments relevant for replication are:

- `Exp_DepthSwapCtrl` — core replication target (ZdA/ZdB, both fields red, binocular)
- `Exp_DecoupledDots_005m` — color vs. depth decoupled factorial
- `Exp_DepthCheck_005m` — brief session to verify observer can perceive the 0.05m depth separation before beginning

The response is via the right-hand controller thumbstick (8 directions). Data saves automatically to the Quest's internal storage at session end.

### Pulling and analyzing data

Pull data from the Quest:

```
adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ /local/destination/
```

Each session produces a tab-separated (.tsv) file. Analysis scripts are included in the project under `Tools/Analysis/` and in the `Agents/SwapPilot/Analysis/` folder. The main entry points are:

- `decoupled_dots_combined_analysis.py` — DecoupledDots sessions
- `analyze_vr_dots_v2.py` — general-purpose session analysis

**Note**: the scripts currently have the data path hardcoded to `/tmp/quest_pull/files/`. Update this to wherever you pulled the data on your machine.

### Observer screening (before main data collection)

Based on the methods in Catak et al. (2022), I recommend the following before beginning:

1. **Stereo check** (`Exp_DepthCheck_005m`): verify the observer can perceive the 0.05m depth separation. If not, increase the depth parameter or check IPD calibration on the headset.
2. **Practice criterion**: observer must achieve >25% correct heading identification (2× chance) on a no-swap baseline block before entering the swap experiment.
3. **IPD calibration**: adjust the Quest's interpupillary distance setting to match the observer. Quest 2 has three physical positions; Quest 3 has continuous motorized adjustment. Incorrect IPD produces vergence mismatch and unreliable depth perception.
4. **Nonius line vergence check**: binocular nonius lines are displayed at the fixation point. Ask observers to confirm the lines appear aligned before initiating each trial — this provides a behavioral check that vergence is approximately correct.

---

## Contact

Gene Stoner  
generstoner@gmail.com  
858-342-7733

Repository: https://github.com/GeneStoner/UnityQuestDotStimuli (branch: `wip/quest-pilot`)

*Figures directory: `Agents/SwapPilot/Figures/` relative to the project root.*
