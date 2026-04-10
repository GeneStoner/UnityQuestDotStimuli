# SwapPilot — Current Results Package
*Assembled 2026-04-09 · Single observer (GS)*

This folder contains the canonical figures, write-ups, and analysis scripts
for the two completed swap pilot experiments. All files are copies of the
current versions from their canonical locations.

---

## Experiments covered

### Exp_DecoupledDots_005m  (100% swap, depth and color decoupled)
- **Asset**: `Exp_DecoupledDots_005m` + `Exp_DecoupledDots_Inv_005m`
- **Design**: 4 swap conditions × CUED/UNCUED × Near/Far; `linkDepthColor=0`
- **Swaps**: N (none), C (color only), Z (depth only), CZ (color+depth)
- **n**: 2051 trials across 4 sessions
- **Data path**: `/tmp/quest_pull3/files/` (S1–S4)

| Session | Label | Asset | n valid |
|---------|-------|-------|---------|
| 260406_1532 | S1 | DecoupledDots_005m | 514 |
| 260406_1754 | S2 | DecoupledDots_Inv_005m (labels inverted) | 512 |
| 260407_0643 | S3 | DecoupledDots_Inv_005m (labels inverted) | 512 |
| 260407_0731 | S4 | DecoupledDots_005m (anomalous — flat cueing) | 513 |

### Exp_DepthColorLinked_005m  (50% swap, depth+color always linked)
- **Asset**: `Exp_DepthColorLinked_005m`
- **Design**: 2 swap conditions × CUED/UNCUED × Near/Far; `linkDepthColor=1`
- **Swaps**: ZdA (coherent subfields S0+S2 swap), ZdB (noise subfields S1+S3 swap)
- **Near=Red, Far=Green** (fixed throughout)
- **n**: 1024 trials across 4 sessions
- **Data path**: `/tmp/quest_pull2/files/`

| Session | Label | n valid |
|---------|-------|---------|
| 260404_0940 | S1 | 256 |
| 260404_1123 | S2 | 256 |
| 260406_1001 | S3 | 256 |
| 260406_1034 | S4 | 256 |

---

## Key findings summary

**DecoupledDots:**
- Dot cueing × Depth-field cueing interact synergistically (F1×F2 AME = +32.7pp ***)
- Color-field cueing is null (F3 AME = +0.9pp, p=.64) across all model specs
- Near-plane penalty: −15.3pp *** (stereoscopic origin — absent monocularly)
- Additive GLM1 was misleading; GLM2 shows all signal in F1×F2 conjunction

**DepthColorLinked:**
- ZdNoi (translator stable): cueing = +25.8pp ***
- ZdCoh (translator changes plane): cueing = +7.0pp †  →  Δ = −18.8pp
- GLM: same structure as DecoupledDots — F1×F2 AME = +16.5pp **, main effects null
- ZdNoi and ZdCoh matched for total scene depth change; disruption is object-specific
- Near-plane penalty: −21.4pp ***

**Cross-experiment:**
- 50% coherent-dot swap (DepthColorLinked ZdCoh) ≈ 100% depth swap (DecoupledDots Z) in disruption magnitude — rules out dose-response; effect is specifically about coherent-object depth identity

---

## Figures  (`Figures/`)

### DecoupledDots
| File | Description |
|------|-------------|
| `decoupled_dots_traj.pdf` | **Canonical trajectory figure** — 4×4 grid (rows=N/C/Z/CZ, cols=Dot✓✗×Near/Far); Stoner & Blanc line style; Dot/Depth/Color✓✗ title boxes |
| `decoupled_dots_depth_color_2x2.pdf` | **Main data figure** — 2×2 depth×color grid; CUED/UNCUED bars per cell; cueing Δ brackets; depth and color marginals |
| `decoupled_dots_glm2.pdf` | **GLM2 figure** — 2-page PDF: (1) forest plot log-odds + AME pp, (2) predicted vs observed by condition |
| `decoupled_dots_per_condition_2x2.pdf` | Per-condition 2×2 accuracy (all 4 swap × CUED/UNCUED × Near/Far) |
| `decoupled_dots_factor_performance.pdf` | 6-panel factor breakdown — CUED vs UNCUED for each factor level |
| `decoupled_N_traces.pdf` | Dot cloud traces — N condition (no swap) |
| `decoupled_C_traces.pdf` | Dot cloud traces — C condition (color swap) |
| `decoupled_Z_traces.pdf` | Dot cloud traces — Z condition (depth swap) |
| `decoupled_CZ_traces.pdf` | Dot cloud traces — CZ condition (depth+color swap) |
| `decoupled_dots_combined_s1s2s3s4.png` | Combined 4-session performance overview |
| `decoupled_dots_session_comparison.png` | Per-session comparison (shows S4 anomaly) |

### DepthColorLinked
| File | Description |
|------|-------------|
| `depth_color_linked_traj.pdf` | **Canonical trajectory figure** — 2×4 grid (rows=ZdNoi/ZdCoh, cols=Dot✓✗×Near/Far); 4 subfield symbols; T(c)/T(n) separated; Field B onset annotation |
| `depthcolorlinked_cueing.pdf` | **Main data figure** — ZdNoi vs ZdCoh panels; 4 bars/panel (CUED/UNCUED × Near/Far); cueing Δ brackets; right strip cueing effect |
| `depthcolorlinked_glm.pdf` | **GLM figure** — 2-page PDF: (1) forest plot log-odds + AME pp, (2) predicted vs observed |

### Cross-experiment
| File | Description |
|------|-------------|
| `depth_disruption_comparison.pdf` | Cueing disruption by swap type across DSC/DCL/DD experiments |

---

## Write-ups  (`WriteUps/`)

| File | Description |
|------|-------------|
| `decoupled_dots_results.pdf` | **Primary DecoupledDots write-up** — design, raw results, GLM1, GLM2, interpretation, lit context |
| `decoupled_dots_results.md` | Markdown source for above |
| `glm2_explainer.pdf` | **GLM2 explainer** — log-odds vs % correct, interaction model, coefficient table, AMEs, plain-language summary |
| `glm2_explainer.md` | Markdown source for above |
| `depthcolorlinked_results.pdf` | **DepthColorLinked write-up** — design, raw results, GLM, comparison to DecoupledDots, mechanism |
| `depthcolorlinked_results.md` | Markdown source for above |

---

## Analysis scripts  (`Analysis/`)

Scripts are copies for reference. **Run from** `VRDots/Tools/Analysis/` (relative paths).
Data loaded from `/tmp/quest_pull2/` (DCL) and `/tmp/quest_pull3/` (DD).

### DecoupledDots
| Script | Purpose |
|--------|---------|
| `decoupled_dots_combined_analysis.py` | Main combined analysis; all 4 sessions; per-session + combined figures |
| `decoupled_dots_glm.py` | GLM1 — additive logistic regression (3 factors: F1/F2/F3) |
| `decoupled_dots_glm2.py` | GLM2 — logistic with interactions; 2-page forest plot PDF |
| `decoupled_dots_traj.py` | Trajectory figure (4×4, Stoner & Blanc line style) |
| `decoupled_dots_depth_color_2x2.py` | Depth×color 2×2 data figure |
| `decoupled_N_traces.py` | Dot cloud traces for N condition |
| `decoupled_C_traces.py` | Dot cloud traces for C condition |
| `decoupled_Z_traces.py` | Dot cloud traces for Z condition |
| `decoupled_CZ_traces.py` | Dot cloud traces for CZ condition |
| `depth_disruption_comparison.py` | Cross-experiment cueing disruption comparison |
| `decoupled_dots_results_pdf.py` | Markdown→PDF renderer (supports --in-md / --out-pdf args) |

### DepthColorLinked
| Script | Purpose |
|--------|---------|
| `depthcolorlinked_cueing_figure.py` | Main cueing figure (ZdNoi/ZdCoh × Near/Far) |
| `depthcolorlinked_glm.py` | GLM — logistic with F1/F2/F3 interactions; 2-page PDF |
| `depth_color_linked_traj.py` | Trajectory figure (2×4; 4 subfield symbols; T(c)/T(n) split) |

---

## What is NOT in this folder (available in canonical locations)

- **All earlier/superseded figures** — `Agents/Figures/` (many older versions)
- **DepthSwapCtrl data** (all-red, no color, monocular/binocular comparison) — see `Agents/WriteUps/depth_swapctrl_writeup.pdf`
- **DepthParam data** (depth separation parameter sweep) — see `Agents/WriteUps/depthparam_writeup.pdf`
- **Baseline/MotionSwap data** — see `Agents/WriteUps/baseline_writeup.pdf`, `swap_writeup.pdf`
- **Literature documents** — `Agents/Literature/` (theory, color model conjecture, vergence notes, etc.)
- **Unity assets** — `Assets/ExperimentConfigs/` in repo
- **Raw data** — `/tmp/quest_pull2/files/` (DCL) and `/tmp/quest_pull3/files/` (DD)
