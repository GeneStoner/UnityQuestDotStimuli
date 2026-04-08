# VRDots Document Index
*Last updated: 2026-04-07*

---

## Unity Experiment Assets (`Assets/ExperimentSpecs/`)

All assets: 63 dots/field, 3.5° aperture radius, 2.0m view distance, 75 Hz, 80ms translation, 750ms delayed onset, 300ms pre-translation hold, 81°/s rotation, 2.26°/s translation.

| Asset | depthSep | delayTrans | linkDepthColor | Swaps | Notes |
|-------|----------|------------|----------------|-------|-------|
| `Exp_Baseline` | — | 1 | — | None | No-swap baseline; balances R/G color |
| `Exp_MotionSwap` | — | 1 | — | Motion | 100% coherence swap at tStart; balances R/G |
| `Exp_Dots50Swap` | — | 1 | — | Dots50 | 50% dot swap (half switch fields); balances R/G |
| `Exp_DepthBaseline` | 0.10m | 1 | — | None | Depth planes but no swap |
| `Exp_DepthParam_003m` | 0.03m | 1 | — | None | Parametric depth, R/G balanced, no swap |
| `Exp_DepthParam_005m` | 0.05m | 1 | — | None | Parametric depth, R/G balanced, no swap |
| `Exp_DepthParam_010m` | 0.10m | 1 | — | None | Parametric depth, R/G balanced, no swap |
| `Exp_DepthParam_015m` | 0.15m | 1 | — | None | Parametric depth, R/G balanced, no swap |
| `Exp_DepthSwapCtrl` | 0.05m | 1 | — | N/ZdA/ZdB | All-red (no color); ZdA=cued translator changes plane, ZdB=non-cued changes |
| `Exp_DepthColorLinked` | 0.05m | 1 | **1** | ZdA/ZdB | Depth+color always co-occur (linked); no N baseline |
| `Exp_DecoupledDots_005m` | 0.05m | **1** | **0** | N/C/Z/CZ | **PRIMARY**. delayTranslator=1 (delayed field translates = CUED); R/G balanced |
| `Exp_DecoupledDots_Inv_005m` | 0.05m | **0** | **0** | N/C/Z/CZ | **PRIMARY (inverted)**. delayTranslator=0 (always-on field delayed); CUED/UNCUED labels inverted before analysis |

SwapType codes: **N**=nothing, **C**=color only, **Z**=depth only, **CZ**=color+depth; **ZdA**=cued translator depth changes, **ZdB**=non-cued depth changes.

---

## Data Sessions (chronological)

| Session | Asset used | N valid | Key result |
|---------|-----------|---------|------------|
| 260323_1534 | Baseline | ~128 | +50.0pp cueing |
| 260324_0716 | Baseline | ~128 | +28.1pp (cursor-jump issues) |
| 260324_1010 | MotionSwap | ~128 | +27→15pp; motion swap reduces cueing |
| 260325_1039 | Dots50Swap | ~128 | +34pp; 50% swap does NOT reduce cueing |
| 260325_1831 | DepthBaseline 0.10m | ~64 | +27.5pp overall; Far=+59pp, Near=−5pp |
| 260325_1914 | DepthBaseline 0.10m | ~64 | +8.6pp; Far=+65pp, Near=−47pp |
| 260325_2013 | DepthBaseline 0.03m | ~64 | +16.6pp; depth barely perceptible |
| 260326_1649 | DepthSwap50_005m | ~128 | +40.3pp; Zd=+36pp, N=+45pp |
| 260330_1853 | DepthSwapCtrl_005m | 192 | +34pp binocular; N=+34**, ZdA=+12 n.s., ZdB=+56*** |
| 260330_2012 | DepthSwapCtrl_005m | 192 | +12pp **monocular** (R eye); ZdA/ZdB pattern attenuated |
| 260331_0621 | DepthSwapCtrl_005m | 192 | Binocular session 2 |
| 260331_1530 | DepthSwapCtrl_005m | 192 | Monocular R-eye #2 |
| 260331_1705 | DepthSwapCtrl_005m | 192 | Monocular L-eye #1 |
| 260331_1734 | DepthSwapCtrl_005m | 192 | Monocular L-eye #2 |
| 260402_0624 | DepthParam_010m | 128 | +47pp; Far=+47, Near=−22 |
| 260402_0656 | DepthParam_015m | 128 | +56pp; Far=+47, Near=−25 |
| 260402_0716 | DepthParam_003m | 128 | +30pp; Far=+47, Near=+13 |
| 260402_0757 | DepthParam_005m | 128 | +19pp; Far=+47, Near=−9 |
| 260404_0940 | DepthColorLinked_005m | 256 | +19pp; ZdNoi=+47***, ZdCoh=+19*** |
| 260404_1123 | DepthColorLinked_005m | 256 | +21pp; flatter, UNCUED elevated |
| **260406_1532** | **DecoupledDots_005m** | **514** | S1; normal labels |
| **260406_1754** | **DecoupledDots_Inv_005m** | **512** | S2; labels inverted |
| **260407_0643** | **DecoupledDots_Inv_005m** | **512** | S3; labels inverted |
| **260407_0731** | **DecoupledDots_005m** | **513** | S4; anomalous (flat +5pp n.s., elevated UNCUED, included) |

---

## Key Results

### DecoupledDots GLM — S1+S2 combined (n=1026, primary)

| Factor | LPM | Odds Ratio | p |
|--------|-----|-----------|---|
| F1 Dot cueing (temporal onset) | **+22.3pp** | OR=3.07 | *** |
| F2 Depth-field cueing (translator in correct depth plane) | **+12.5pp** | OR=1.89 | *** |
| F3 Color-field cueing (translator matches delayed field color) | **+0.0pp** | OR=1.00 | n.s. |

Baseline (UNCUED+CZ) = 12.5% ≈ chance. OR is the appropriate effect size (baseline near floor).

### DecoupledDots — All 4 sessions combined (n=2051)

| Swap | CUED | UNCUED | Δ | sig |
|------|------|--------|---|-----|
| N | 48.4% | 24.9% | +23.5pp | *** |
| C | 50.0% | 26.5% | +23.5pp | *** |
| Z | 23.4% | 14.4% | +9.0pp | ** |
| CZ | 25.0% | 19.5% | +5.5pp | † |

F1 dot cueing: Δ=+15.4pp χ²=59.01 ***. F2 depth-field: Δ≈+9–12pp **. F3 color: null.
Full 2×4 χ²(7)=148.28 p<10⁻¹⁷.

---

## Figures (`Agents/Figures/`)

### DecoupledDots — Per-session (S1–S4)
| File | Contents |
|------|----------|
| `decoupled_dots_260406_1532.png` | S1 (n=514): dot/depth/color 3-factor panels |
| `decoupled_dots_260406_1754.png` | S2 (n=512, inverted): 3-factor panels |
| `decoupled_dots_260407_0643.png` | S3 (n=512, inverted): 3-factor panels |
| `decoupled_dots_260407_0731.png` | S4 (n=513, anomalous): 3-factor panels; note flat dot cueing |

### DecoupledDots — Combined
| File | Contents |
|------|----------|
| `decoupled_dots_combined.png` | S1+S2 combined (n=1026): all 3-factor panels + summary — **primary analysis figure** |
| `decoupled_dots_combined_s1s2s3s4.png` | All 4 sessions (n=2051): 3-factor combined |
| `decoupled_dots_session_comparison.png` | Side-by-side per-session 3-factor effects; shows S4 anomaly flagged with ⚠ |
| `decoupled_dots_glm.png` | GLM results: observed vs predicted + coefficient bar chart (dot/depth/color ORs) |
| `decoupled_dots_traj.png` | 4×4 grid of frame-by-frame motion trajectories for all N/C/Z/CZ × CUED/UNCUED conditions |

### DecoupledDots — Factor performance (new 2026-04-07)
| File | Contents |
|------|----------|
| `decoupled_dots_factor_performance.png/.pdf` | **6-panel figure** (all 4 sessions, n=2051). Row 1: cued vs uncued bar for each factor (A=dot, B=depth, C=color). Row 2: pairwise cued-arm comparisons (D=dot vs depth, E=dot vs color, F=depth vs color). Wilson 95% CI + χ² brackets. |
| `decoupled_dots_dot_vs_depth.png/.pdf` | **2-panel figure**. Panel A: 2×2 matrix (Dot✓Depth✓/Dot✓Depth✗/Dot✗Depth✓/Dot✗Depth✗) — direct head-to-head, shows dot wins. Panel B: all 8 raw conditions (CUED/UNCUED × N/C/Z/CZ) with depth-swap cost annotations vs N baseline. |
| `decoupled_dots_report.pdf` | **5-page comprehensive report**. P1: 3-factor Δ overview + per-session table. P2: cued vs uncued % correct for each factor. P3: all 8 conditions by swap. P4: 2×2 conflict + 8-condition disruptiveness. P5: pairwise cued-arm comparisons with interpretation. |
| `decoupled_dots_field_cueing.png` | Earlier standalone field-cueing figure (superseded by combined scripts) |

### DecoupledDots — Dot trace visualizations (new 2026-04-07)
| File | Contents |
|------|----------|
| `dot_trace_decoupled_N_CUED.png` | Single aperture view: N/CUED/Near/heading=0°. Shows accumulated dot positions ±6 frames around translation. Filled=Near, Open=Far, Red=FieldB, Green=FieldA, alpha gradient pre→trans→post. |
| `dot_trace_decoupled_multi_near.png` | 2×4 grid: CUED/UNCUED rows × N/C/Z/CZ cols, delayed field=Near. Shows depth and color swaps at tStart as filled↔open and color changes mid-trace. |
| `dot_trace_decoupled_multi_far.png` | Same 2×4 grid, delayed field=Far. |

### DepthSwapCtrl
| File | Contents |
|------|----------|
| `depthswapctrl_all_sessions_bars.png` | Multi-session bars for N/ZdA/ZdB including binocular + monocular sessions |
| `three_factors_bino_vs_mono.png` | F1/F2/F3 effects compared: binocular (n=384) vs all monocular pooled (n=769) |
| `trans_plane_2x2.png` | 2×2 of translating depth plane (Near/Far) × condition (N/ZdA/ZdB) |
| `trans_plane_color.png` | Color-coded translating depth plane breakdown |

### DepthColorLinked
| File | Contents |
|------|----------|
| `depth_color_linked_results.png` | S1+S2 combined results: cueing by ZdNoi/ZdCoh + 3-factor panel |
| `depth_color_linked_traj.png` | Frame-by-frame trajectories with R/G depth-color coding |
| `depth_color_biases.png` | Bias analysis for color-balanced conditions |

### DepthParam
| File | Contents |
|------|----------|
| `depthparam_by_trans_depth.png` | **Key figure**: cueing effect by translating depth plane (Near/Far) across 0.03/0.05/0.10/0.15m — shows Far saturated, Near crosses zero |
| `depthparam_trajectories.png` | Frame-by-frame trajectories; Fig 1B convention (green dashed=delayed FieldB, red solid=non-delayed FieldA) |

### Earlier / General
| File | Contents |
|------|----------|
| `all_experiments_summary.png` | Cross-experiment summary bar chart |
| `baseline_writeup.png` | Baseline cueing figure (pre-depth era) |
| `swap_traj_4subfield.png` | 4-subfield trajectory diagram for motion/dots swap conditions |
| `factor_labeled_trajectories.png` | 12-panel factor-labeled trajectories (N/ZdA/ZdB × CUED/UNCUED × Near/Far) |
| `feature_trajectories_overview.png` | Overview of all swap feature trajectories |
| `flat_permutations.png` | Permutation diagram for balanced swap design |
| `labeling_comparison.png` | Old vs new Near/Far labeling convention comparison |
| `depth_color_swap_traj.png` | Trajectory diagram for depth+color linked swap |

---

## WriteUps (`Agents/WriteUps/`)

| File | Contents |
|------|----------|
| `baseline_writeup.pdf` | Early cueing effect before depth conditions |
| `swap_writeup.pdf` | Motion swap (100% reduces cueing) + Dots50 swap (50% does not) |
| `depth_baseline_writeup.pdf` | First depth experiments; Far>Near asymmetry emerges |
| `depth_swapctrl_writeup.pdf` | DepthSwapCtrl full results: ZdA kills cueing, ZdB enhances; binocular vs monocular |
| `depthparam_writeup.pdf` | Parametric depth separation (0.03–0.15m): Far saturated, Near slope |
| `depth_color_linked_writeup.pdf` | DepthColorLinked: apparent color effect shown to be depth confound in DecoupledDots |
| `depth_color_linked_conditions.pdf` | Full enumeration of all conditions in DepthColorLinked asset |
| `depth_color_design.pdf` | Rationale for decoupling color from depth in DecoupledDots |
| `depth_color_decoupled_design.pdf` | Full design spec for DecoupledDots (N/C/Z/CZ × CUED/UNCUED orthogonal factorial) |
| `depth_color_decoupled_traj.pdf` | Trajectory diagrams for all N/C/Z/CZ conditions |
| `decoupled_three_conds.pdf` | Early 3-condition analysis (before CZ added) |
| `decoupled_four_conds.pdf` | Full 4-condition (N/C/Z/CZ) analysis document |
| `decoupled_50pct_analysis.pdf` | Why 50% partial swaps are geometrically impossible while maintaining clean depth planes |
| `s1s2_swap_analysis.pdf` | Why S1↔S2 full attribute swap is valid but functionally null — confirms design symmetry |
| `red_green_motion_lit.pdf` | Red vs green in suprathreshold motion: no known red>green advantage; green photopically brighter on Quest |
| `writeup_index.pdf` | Earlier index (partially superseded by this file) |

---

## Literature / Theory (`Agents/Literature/`)

| File | Contents |
|------|----------|
| `decoupled_dots_results.md` | **PRIMARY CURRENT RESULTS DOC** — full write-up: design, all sessions, 3-factor results, GLM, interpretation, open questions, relation to literature |
| `experiment_status.md` | Running log of all sessions and results across all experiments |
| `pilot_results_summary.md` | Pilot results summary (early sessions) |
| `pilot_summary.md` | Condensed pilot summary |
| `data_musing.md` | Exploratory observations and hypotheses |
| `factor_labeled_trajectories.md` | Factor assignments (F1/F2/F3) for N/ZdA/ZdB conditions — authoritative reference for DepthSwapCtrl |
| `color_cueing_review.md` | Color in exogenous attention literature; context for F3=0 null result |
| `color_model_conjecture.md` | Theoretical conjecture on why color-field cueing = 0 in DecoupledDots |
| `vergence_latency_note.md` | F2 depth effect is neural disparity, not vergence-mediated (80ms < ~70–85ms vergence latency) |
| `depth_ior_hypothesis.md` | DepthParam theory: gradient migration account, 5 predictions, IOR abandoned |
| `programmer_critique_gradient_migration.md` | Critique and suggested falsifying tests for gradient migration account |
| `modeling_lit.md` | Computational/modeling literature (motion coherence, normalization, object-based attention models) |
| `integrated_review.md` | Broad literature review integrating VRDots findings with prior work |
| `theory_doc.md` | Running theory document: key constructs, predictions, how findings fit |
| `historical_comparison.md` | Comparison to prior literature |
| `depthparam_results.md` | DepthParam-specific results notes |
| `catak2022_fixation_methods.md` | Fixation methods paper notes |
| `endogenous_color_hillyard.md` | Hillyard-lab endogenous color cueing literature notes |
| `endogenous_color_summary_and_design.md` | Summary + possible design for endogenous color cueing follow-up |
| `pending_papers.md` | Papers to read/integrate |
| `paper_notes/` | Directory of individual paper notes |
| `document_index.md` | This file |

---

## Analysis Scripts (`Tools/Analysis/`)

| Script | Purpose |
|--------|---------|
| `decoupled_dots_combined_analysis.py` | Main analysis: per-session (S1–S4) + S1+S2 combined + S1–S4 combined + session comparison figure |
| `decoupled_dots_glm.py` | Logistic regression GLM (3 factors); produces coefficient figure |
| `decoupled_dots_factor_performance.py` | 6-panel figure: cued vs uncued arms + pairwise cued-arm comparisons (all 4 sessions) |
| `decoupled_dots_dot_vs_depth.py` | 2-panel figure: 2×2 dot×depth conflict matrix + all 8 conditions with depth-swap costs |
| `decoupled_dots_report.py` | 5-page comprehensive PDF report with commentary |
| `decoupled_dots_field_cueing.py` | Standalone field-cueing analysis (superseded by combined script) |
| `decoupled_dots_traj.py` | 4×4 frame-by-frame trajectory grid (N/C/Z/CZ × CUED/UNCUED) |
| `plot_dot_traces.py` | Circular aperture dot trace visualization for DepthSwapCtrl (N/ZdA/ZdB); pre=6/post=6 default |
| `plot_dot_traces_decoupled.py` | Circular aperture dot trace visualization for DecoupledDots (N/C/Z/CZ); single-panel or --multi 2×4 grid; pre=6/post=6 default |
| `depthparam_trajectories.py` | DepthParam trajectory figure (Fig 1B convention) |
| `depth_color_linked_analysis.py` | DepthColorLinked results analysis |
| `depth_color_linked_traj.py` | DepthColorLinked frame-by-frame trajectories with R/G coding |
| `gen_hypothetical_traj.py` | Generates hypothetical motion trajectories; reference for motion-kind array logic |
| `factor_traj_labeled.py` | 12-panel factor-labeled trajectories (N/ZdA/ZdB × CUED/UNCUED × Near/Far) |
