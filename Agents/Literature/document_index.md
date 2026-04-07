# VRDots Document Index
*Last updated: 2026-04-06*

---

## Empirical Results (chronological)

| File | Location | Contents |
|------|----------|----------|
| `baseline_writeup.pdf` | WriteUps/ | Early baseline cueing effect (pre-depth) |
| `swap_writeup.pdf` | WriteUps/ | Motion swap + Dots50 swap — 100% swap reduces cueing, 50% doesn't |
| `depth_baseline_writeup.pdf` | WriteUps/ | First depth experiments — Far>Near asymmetry emerges |
| `depth_swapctrl_writeup.pdf` | WriteUps/ | DepthSwapCtrl: ZdA kills cueing, ZdB enhances; monocular vs binocular |
| `depthparam_writeup.pdf` | WriteUps/ | Parametric depth: Far cueing saturated at all depths, Near crosses zero ~0.05m |
| `depth_color_linked_writeup.pdf` | WriteUps/ | DepthColorLinked: depth+color linked, apparent color effect (confounded with depth) |
| `depth_color_linked_conditions.pdf` | WriteUps/ | Full condition enumeration for DepthColorLinked asset |
| `decoupled_dots_results.md` | Literature/ | **PRIMARY CURRENT RESULTS DOC** — DecoupledDots GLM: dot cueing +22pp***, depth-field cueing +12.5pp***, color-field cueing +0pp n.s. |

---

## DecoupledDots Design & Analysis

| File | Location | Contents |
|------|----------|----------|
| `depth_color_design.pdf` | WriteUps/ | Design rationale for decoupling color from depth |
| `depth_color_decoupled_design.pdf` | WriteUps/ | DecoupledDots full design spec (N/C/Z/CZ × CUED/UNCUED) |
| `depth_color_decoupled_traj.pdf` | WriteUps/ | Trajectory diagrams for all N/C/Z/CZ conditions |
| `decoupled_three_conds.pdf` | WriteUps/ | Early 3-condition analysis |
| `decoupled_four_conds.pdf` | WriteUps/ | Full 4-condition (N/C/Z/CZ) analysis |
| `decoupled_50pct_analysis.pdf` | WriteUps/ | Why 50% partial swaps are impossible while keeping clean depth planes |
| `s1s2_swap_analysis.pdf` | WriteUps/ | Why S1↔S2 full attribute swap is valid but functionally null |

---

## Literature Reviews & Conjecture

| File | Location | Contents |
|------|----------|----------|
| `red_green_motion_lit.pdf` | WriteUps/ | Red vs green in suprathreshold motion — no known red>green advantage |
| `color_cueing_review.md` | Literature/ | Color in exogenous attention literature |
| `color_model_conjecture.md` | Literature/ | Theoretical conjecture on why color-field cueing = 0 |
| `vergence_latency_note.md` | Literature/ | Why the F2 depth effect is neural disparity, not vergence-mediated (80ms translation < vergence latency ~70–85ms) |
| `depth_ior_hypothesis.md` | Literature/ | DepthParam theory: gradient migration account, 5 predictions, IOR abandoned |
| `programmer_critique_gradient_migration.md` | Literature/ | Critique and suggested tests of gradient migration account |
| `modeling_lit.md` | Literature/ | Computational/modeling literature (motion coherence, normalization, object-based attention models) |
| `integrated_review.md` | Literature/ | Broad literature review integrating VRDots findings |
| `theory_doc.md` | Literature/ | Running theory document: key constructs, predictions, how findings fit |

---

## Running Logs & Reference

| File | Location | Contents |
|------|----------|----------|
| `experiment_status.md` | Literature/ | Running log of all sessions and results across all experiments |
| `pilot_results_summary.md` | Literature/ | Pilot results summary (earlier sessions) |
| `data_musing.md` | Literature/ | Exploratory observations and hypotheses |
| `factor_labeled_trajectories.md` | Literature/ | Factor assignments (F1/F2/F3) for all N/ZdA/ZdB conditions — authoritative reference |
| `historical_comparison.md` | Literature/ | Comparison to prior literature |
| `catak2022_fixation_methods.md` | Literature/ | Fixation methods paper notes |
| `pending_papers.md` | Literature/ | Papers to read/integrate |
| `writeup_index.pdf` | WriteUps/ | Earlier index (partially superseded by this file) |

---

## Key Finding Summary (as of 2026-04-06)

**DecoupledDots GLM** (n=1026, logistic regression, additive):

| Factor | LPM | Odds Ratio | p |
|--------|-----|-----------|---|
| Dot cueing (temporal onset) | +22.3pp | **OR=3.07** | *** |
| Depth-field cueing (translator in correct depth plane) | +12.5pp | **OR=1.89** | *** |
| Color-field cueing (translator matches delayed field color) | +0.0pp | **OR=1.00** | n.s. |

Baseline (UNCUED+CZ) = 12.5% ≈ chance. Near-floor baseline means pp effects underestimate underlying signal strength — odds ratios are the appropriate effect size measure.
