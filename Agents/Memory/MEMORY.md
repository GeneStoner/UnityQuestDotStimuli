# VRDots Project Working Document

See linked files for full details:
- [vrdots-project.md](vrdots-project.md) — architecture, stimulus design, data formats, pilot results
- [swap-conditions.md](swap-conditions.md) — all swap implementations (Motion, Color, Dots50, Depth Z, Depth50 Zd, ZdA, ZdB)
- [verification-system.md](verification-system.md) — Methods A/B/C for trajectory verification
- [open-questions.md](open-questions.md) — open empirical questions and pending design decisions
- [factor-analysis.md](factor-analysis.md) — 3-factor chi-square framework: dot cueing, depth-field cueing, depth field (Near/Far)
- [agent-literature.md](agent-literature.md) — Literature/Theory agent: scope, activation, outputs → `VRDots/Agents/Literature/`
- [agent-packaging.md](agent-packaging.md) — Packaging agent: scope, activation (NOT YET ACTIVE), outputs → `VRDots/Agents/Packaging/`
- [agent-modeling.md](agent-modeling.md) — Modeling agent: PINNED, computational model of VRDots stimuli/behavior (future)
- [reference_stonerBlanc2010_pdf.md](reference_stonerBlanc2010_pdf.md) — Local PDF path + page numbers for all figures in Stoner & Blanc 2010
- [feedback_labeling_convention.md](feedback_labeling_convention.md) — CRITICAL: Near/Far labels in VRDots = delayed field depth; user wants translating field depth framing
- [observer_gs_vergence.md](observer_gs_vergence.md) — GS has esophoria + prism glasses; may explain Far > Near asymmetry as vergence-comfort confound
- [decoupled_dots_glm.md](decoupled_dots_glm.md) — KEY RESULT: DecoupledDots GLM1+GLM2; F1×F2 synergy (+32.7pp***); color null; Near penalty −15pp
- [depthcolorlinked_glm.md](depthcolorlinked_glm.md) — KEY RESULT: DepthColorLinked GLM; F1×F2 +16.5pp**; object-specific disruption confirmed; disparity neuron question

- [feedback_traj_convention.md](feedback_traj_convention.md) — CRITICAL: CUED/UNCUED trajectory panels must be visually identical except during translation window
- [decoupled_traj_status.md](decoupled_traj_status.md) — ALL traj/trace figures DONE for DecoupledDots + DepthColorLinked; label convention resolved (translator-centric)
- `Agents/Literature/next_steps.md` — **CANONICAL NEXT STEPS**: prioritized experiment roadmap; second observer is gating step; SOA + fixation-depth reversal experiments explained; 50% swaps going forward
- `Agents/Packaging/lab_transfer_guide.md` — lab transfer guide for new collaborators (two-part: GS prep + receiving lab requirements)
- `Agents/Packaging/collaborator_brief_HK.md` — shareable summary + setup guide for Dr. Hulusi K.
- [endogenous_color_design.md](endogenous_color_design.md) — **NEXT EXPERIMENT (lower priority)**: Design B protocol (block instruction + 50/50 validity + simultaneous onset); analysis bridge; Step 0 prerequisite

## Quick Reference
- **Project**: `/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/`
- **Repo**: `https://github.com/GeneStoner/UnityQuestDotStimuli.git`
- **Branch**: `wip/quest-pilot` (uncommitted changes as of 2026-03-30)
- **Version**: 0.2.0
- **Data (Quest)**: `/sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/`
- **Data (Mac)**: `/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/`
- **Analysis**: `VRDots/Tools/Analysis/` (~40 Python scripts; canonical set in `Agents/SwapPilot/Analysis/`)
- **Current results package**: `VRDots/Agents/SwapPilot/` (figures + writeups + scripts for both swap experiments)
- **Unity Input**: Must use "Both" (Active Input Handling) — code uses legacy Input + new Input System
- **ADB pull**: `adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ /tmp/quest_pull/`

## ⚠️ DATA INTEGRITY FLAG (2026-04-11)
Unity asset bug produced jerky motion artifact during depth swaps (Z/CZ conditions). Bug now fixed by programmer. F2 magnitude and F1×F2 interaction are suspect across DecoupledDots, DepthColorLinked, BothFar. DepthSwapCtrl also partially afflicted via a different asset (ZdA/ZdB comparisons suspect). F1 (cueing) and F4 (Near/Far) from N-condition data are NOT affected. Every experiment with a depth swap condition needs at least one clean replication. See open-questions.md for full list.

## Current Status (2026-04-11 — BothFar experiment)
- **NEW**: BothFar_005m session 260411_1225 run — both dot fields behind fixation (Less-Far=+0.05m, More-Far=+0.10m uncrossed). n=512.
- **KEY FINDING**: F1×F4 dissociation (+17.8pp): CUED prefers More-Far (+35.9pp vs +30.5pp), UNCUED REVERSES to prefer Less-Far (+11.5pp*** vs −0.8pp n.s., Δ=+12.3pp*).
- **INTERPRETATION**: UNCUED structural mechanism defaults to MINIMUM DISPARITY from fixation, not "extends beyond fixation toward more uncrossed". Both BothFar Less-Far preference and standard Far preference fit minimum-vergence-demand rule. CUED enhances the more extreme/salient plane in both experiments.
- **F2 SURVIVES**: Depth continuity disruption ~17pp (N vs Z in CUED) — independent of whether planes straddle fixation.
- **RULES OUT**: Simple "attentional gradient extends monotonically toward more uncrossed disparity" as the UNCUED structural mechanism.
- **NEW**: `Agents/Literature/bothfar_results.md` — full BothFar write-up.
- **UPDATED**: `beyond_account_provisional.md` (Section 3b added, Section 7 table extended, bottom line revised).
- **UPDATED**: `open-questions.md` (item 20 added; item 2 cross-referenced).
- **Data**: `/tmp/quest_pull4/files/vr_dots_session_260411_1225.tsv`

## Current Status (2026-04-09 — late session: theory, packaging, lab transfer)
- **NEW**: Bounded-depth-window hypothesis (GS, introspective) documented — attentional spotlight extends "beyond" attended plane; Near leaks into Far; Far is bounded. Documented in `depth_ior_hypothesis.md` (new section) and `theory_doc.md` §9.8. Key tension: DepthParam shows asymmetry GROWS with depth separation, but leakage account predicts it should SHRINK (planes more segregable). SOA experiment is the critical dissociation vs. gradient migration.
- **NEW**: `Agents/Literature/next_steps.md` — prioritized experiment roadmap: (1) second observer on DepthSwapCtrl, (2) DepthParam second sessions at 0.05m+0.10m, (3) SOA manipulation, (4) fixation-depth reversal. Use 50% swaps (ZdA/ZdB) going forward — 100% swaps served their purpose.
- **NEW**: `Agents/Packaging/lab_transfer_guide.md` — full two-part guide for sharing VRDots with other labs: what GS must do (repo, Inspector wiring, build verification) + what receiving lab needs (hardware, Meta dev account, Unity 6000.2.7f2 + Android Build Support, ADB, Python).
- **NEW**: `Agents/Packaging/collaborator_brief_HK.md` — shareable document for Dr. Hulusi K. (co-author, Catak et al. 2022): paradigm overview, DecoupledDots + DepthColorLinked findings with figure references, what he needs to collect data in Turkey. Editable markdown; convert to Word with pandoc.
- **LIT AGENT REVIEW**: Two new lit agent docs reviewed: `depth_ordering_lit_review.md` (transparent motion depth rivalry — strong quality) and `depth_experiments_intro.md` (near paper-quality prose). Key issue: "Calabro & Vaina (2011) J Neurophysiol 105:200 [PMID 21068268]" — attribution was previously unconfirmed; lit agent committed to this name. Verify before using in write-ups. Also: timing error in depth_ordering_lit_review §6 (says 300ms window for depth-order assignment, but depth information available >1000ms from trial onset).
- **EYE TRACKING DECISION**: Quest Pro eye tracking (1° accuracy) too coarse to verify vergence at 2.5 arcmin disparity level. Behavioral approach (Catak fixation screening + nonius lines as software-enforced gate) is more appropriate. Defer Quest Pro investment unless gaze-contingent display needed.
- **data_musing.md**: correction banner added — "Near reversal" language throughout is old-labeling artifact; correct reading = Far > Near translation performance gap.
- **Packaging agent**: NOW ACTIVE — `Agents/Packaging/` has content (lab_transfer_guide.md, collaborator_brief_HK.md).

## Current Status (2026-04-09 — DepthColorLinked analysis + SwapPilot package)
- **DONE**: DepthColorLinked (50% swap) full analysis — n=1024 (4 sessions), GLM, trajectory figure, write-up
- **KEY FINDING**: ZdNoi=+25.8pp*** vs ZdCoh=+7.0pp† — disruption object-specific not scene-level (ZdNoi/ZdCoh matched for total depth change); F1×F2=+16.5pp** dominates; UNCUED flat
- **DONE**: `Agents/Literature/depthcolorlinked_results.md` + `Agents/WriteUps/depthcolorlinked_results.pdf`
- **DONE**: `Agents/Literature/glm2_explainer.md` + `.pdf` — log-odds, interactions, AMEs explained
- **DONE**: `Agents/SwapPilot/` — curated package: 15 figures + 6 writeups + 14 scripts + README
- **NEW THEORY QUESTION**: Disparity-tuned neurons vs perceived depth order — does F2 require actual binocular disparity or would monocular-cue-based depth ordering suffice?
- **RESOLVED**: Row label convention = translator-centric throughout all figures
- **DATA**: DecoupledDots `/tmp/quest_pull3/files/`; DepthColorLinked `/tmp/quest_pull2/files/`
- **NEXT EXPERIMENT**: Endogenous color Design B (see endogenous_color_design.md)

## Current Status (2026-04-08)
- **NEW (2026-04-07)**: Sessions 260407_0643 + 260407_0731 (S3+S4) run; now 4 sessions total (n=2051 combined)
- **NEW (2026-04-07)**: `decoupled_dots_factor_performance.py` — 6-panel figure comparing cued vs uncued arm for each factor + pairwise comparisons; saved to `Agents/Figures/decoupled_dots_factor_performance.png/pdf`
- **NEW (2026-04-07)**: S4 (260407_0731) anomalous — dot cueing flat (+4.8pp n.s.); elevated UNCUED (all swaps ~25–34%); included without exclusion
- **NEW (2026-04-08)**: `Agents/Literature/document_index.md` updated comprehensively; `document_index.pdf` generated via reportlab; covers all 12 assets, 24 sessions, all figures/writeups/scripts
- **DONE (2026-04-08)**: 4×4 DecoupledDots trajectory figure — `decoupled_dots_traj.py` rewritten (Stoner & Blanc line style; rows=N/C/Z/CZ; cols=CUED-Near/Far/UNCUED-Near/Far); output `Agents/Figures/decoupled_dots_traj.png`
- **NEW (2026-04-08)**: Literary agent session — 5 new lit files: `color_cueing_review.md`, `color_model_conjecture.md`, `vergence_latency_note.md`, `endogenous_color_hillyard.md`, `endogenous_color_summary_and_design.md`
- **KEY THEORY (2026-04-08)**: M-pathway carries motion+disparity but NOT color → exogenous onset enters M-pathway → F2 (depth) structurally > F3 (color); see `color_model_conjecture.md`
- **NEXT EXPERIMENT (2026-04-08)**: Endogenous color Design B — block instruction ("attend RED") + 50/50 validity + simultaneous onset; Step 0 (verify percept) first; see `endogenous_color_design.md` + `endogenous_color_summary_and_design.md`
- **Data path S3/S4**: `/tmp/quest_pull3/files/` (S3=260407_0643, S4=260407_0731)

## Current Status (2026-04-06)
- **NEW (2026-04-06)**: `Exp_DecoupledDots_005m` + `Exp_DecoupledDots_Inv_005m` — two complementary sessions (n=1026 combined), linkDepthColor=0, swaps N/C/Z/CZ
- **NEW (2026-04-06)**: GLM (logistic regression) on 3 factors: Dot cueing +22.3pp***, Depth-field cueing +12.5pp***, Color-field cueing +0.0pp n.s.
- **KEY FINDING (2026-04-06)**: Color is null; depth drives the field-cueing effect. DepthColorLinked "color effect" was a depth confound.
- **NEW (2026-04-06)**: `decoupled_dots_combined_analysis.py` now produces all 3 figures (S1, S2, combined) each with dot/depth/color panels. `decoupled_dots_glm.py` produces coefficient figure.
- **NEW (2026-04-06)**: `Agents/Literature/decoupled_dots_results.md` — full write-up for literature agent

## Current Status (2026-04-04)
- **NEW (2026-04-04)**: `Exp_DepthColorLinked` experiment — ZdA+ZdB, Near=Red, Far=Green, 256 trials, `linkDepthColor=1`, `includeNoSwapBaseline=0`
- **NEW (2026-04-04)**: Two sessions run: 260404_0940 (S1, strong dissociation) + 260404_1123 (S2, flatter)
- **NEW (2026-04-04)**: Combined results (n=512): F1 Dot Cueing=+20.3pp***, F2 Depth Cueing=+7.0pp*
- **NEW (2026-04-04)**: CUED+ZdNoi=+37.5pp***, CUED+ZdCoh=+22.7pp***, UNCUED both ~+10pp
- **NEW (2026-04-04)**: `depth_color_linked_writeup.pdf` (3 pages: trajectories+design, results, interpretation) in `Agents/WriteUps/`
- **NEW (2026-04-04)**: `depth_color_linked_traj.py` — 8-panel frame-by-frame trajectories with R/G depth-color coding
- **NEW (2026-04-04)**: `Agents/WriteUps/red_green_motion_lit.pdf` — 3-page lit summary: red vs green in suprathreshold motion; key finding: no known red > green advantage; green likely photopically brighter at equal RGB on Quest; red attentional salience is real but attention-stage not motion-stage
- **UPDATED (2026-04-04)**: `depthparam_trajectories.py` now follows Fig 1B convention — green dashed = delayed Field B, red solid = non-delayed Field A; CUED top row, UNCUED bottom row; columns by translating depth (Far left, Near right); continuous lines not scatter markers
- **NEW (2026-04-04)**: `ExpSpecTestPhase.cs` — added `linkDepthColor` and `includeNoSwapBaseline` serialized fields
- **NEW (2026-04-02)**: ZdA and ZdB swap conditions implemented (SwapFlags.Depth50A=32, Depth50B=64)
- **NEW (2026-04-02)**: `Exp_DepthSwapCtrl` asset — N/ZdA/ZdB, both fields red, 0.05m depth, 192 trials
- **NEW (2026-04-02)**: `Exp_DepthParam_003m/005m/010m/015m` assets — R/G balanced, no swap, 128 trials each
- **NEW (2026-04-02)**: `factor_traj_labeled.py` — 12-panel factor-labeled trajectories (all N/ZdA/ZdB × CUED/UNCUED × Near/Far)
- **NEW (2026-04-02)**: `Agents/Figures/depthparam_by_trans_depth.png` — DepthParam data by translating depth; KEY FIGURE
- **NEW (2026-04-02)**: `Agents/Figures/labeling_comparison.png` — old vs new Near/Far labeling comparison
- SwapFlags enum: None=0, Motion=1, Color=2, Dots50=4, Depth=8, Depth50=16, Depth50A=32, Depth50B=64
- Same-color experiments: use `balanceDelayedFieldColor=false` + COLOR_RED trials; `nonDelayedColor` forced = `delayedColor` in code
- **TODO**: more DepthColorLinked sessions (n=64→128/cell); second sessions at each DepthParam depth; color-only swap experiment; second observer at 0.05m + 0.10m
- **DONE (inconclusive)**: heading × depth reanalysis at n=16/cell — noise dominated; needs second sessions
- **RESOLVED**: Near/Far labeling — all analysis now uses translating-field-depth convention throughout

## Nonius Lines & Vergence (added 2026-03-27)
- **Binocular nonius lines**: working on Quest — toggle `showNoniusLines` on `SmoothFixation`
- **True dichoptic NOT possible** via Unity shader APIs with Oculus XR Plugin on Android
- **Path to dichoptic**: OVR Compositor Layers (Meta XR SDK) — deferred
- **Field A preview**: sub0+sub1 shown static at frame-0 during WaitingForStart
- **NoniusLine.shader** in Always Included Shaders (required for Quest builds)
- **Active Fixation_Controller**: `SmoothFixation` under Main Camera

## Pilot Results Summary
| Session | Experiment | depthSep | Overall Cueing | Near Cueing | Far Cueing | Notes |
|---------|-----------|----------|---------------|-------------|------------|-------|
| 260323_1534 | Baseline | — | 50.0pp | — | — | Pre-v0.2.0 |
| 260324_0716 | Baseline | — | 28.1pp | — | — | Cursor-jump issues |
| 260324_1010 | MotionSwap | — | 27.1pp→15.7pp | — | — | 100% swap reduces cueing |
| 260325_1039 | Dots50Swap | — | 30.4pp→34.4pp | — | — | 50% swap does NOT reduce cueing |
| 260325_1831 | DepthBaseline | 0.10m | +27.5pp | −4.9pp | +59.4pp | Depth planes clear |
| 260325_1914 | DepthBaseline | 0.10m | +8.6pp | −46.9pp | +65.1pp | Depth planes clear |
| 260325_2013 | DepthBaseline | 0.03m | +16.6pp | +13.7pp | +19.4pp | Depth barely perceptible |
| 260326_1649 | DepthSwap50_005m | 0.05m | +40.3pp | +28pp (est) | +53pp (est) | Zd: +35.9pp; N: +44.8pp |
| 260330_1853 | DepthSwapCtrl_005m | 0.05m | +34.3pp | +20.8pp* | +47.9pp*** | N=+34pp**, ZdA=+12pp n.s., ZdB=+56pp*** |
| 260330_2012 | DepthSwapCtrl_005m | 0.05m | +12.2pp | +16.4pp n.s. | +8.3pp n.s. | **Monocular, L eye closed / R eye active** |
| 260331_0621 | DepthSwapCtrl_005m | 0.05m | — | — | — | Binocular session 2 |
| 260331_1530 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular R-eye #2, L eye closed / R eye active** |
| 260331_1705 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular L-eye #1, R eye closed / L eye active** |
| 260331_1734 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular L-eye #2, R eye closed / L eye active** |
| 260402_0624 | DepthParam_010m | 0.10m | +46.9pp | −21.9pp | +46.9pp | R/G, no swap, session 1 (n=32/cell) |
| 260402_0656 | DepthParam_015m | 0.15m | +56.2pp | −25.0pp | +46.9pp | R/G, no swap, session 1 (n=32/cell) |
| 260402_0716 | DepthParam_003m | 0.03m | +29.7pp | +12.5pp n.s. | +46.9pp | R/G, no swap, session 1 (n=32/cell) |
| 260402_0757 | DepthParam_005m | 0.05m | +18.8pp | −9.4pp | +46.9pp | R/G, no swap, session 1 (n=32/cell) |
| 260404_0940 | DepthColorLinked_005m | 0.05m | — | — | — | S1: ZdNoi=+47pp, ZdCoh=+19pp |
| 260404_1123 | DepthColorLinked_005m | 0.05m | — | — | — | S2: flatter; UNCUED elevated |
| 260406_1001 | DepthColorLinked_005m | 0.05m | — | — | — | S3 |
| 260406_1034 | DepthColorLinked_005m | 0.05m | — | — | — | S4 |
| **DCL combined** | DepthColorLinked_005m | 0.05m | ZdNoi=+25.8pp*** | — | — | **n=1024; ZdCoh=+7.0pp†; GLM F1×F2=+16.5pp** |
| 260411_1225 | BothFar_005m | 0.05m+0.10m | +27.8pp*** | Less-Far=+30.5pp*** | More-Far=+35.9pp*** | **UNCUED REVERSAL**: UNCUED Less-Far=+11.5pp***, More-Far=−0.8pp; F1×F4=+17.8pp; F2 survives ~17pp |

## Key Findings (DepthColorLinked, n=1024, 2026-04-09)
- **ZdNoi=+25.8pp*** vs ZdCoh=+7.0pp†** — disruption when coherent translator changes depth+color
- **UNCUED arm flat** (21.9% vs 23.4%) — depth+color continuity useless without dot cue
- **GLM**: F1×F2=+16.5pp**, main effects null, Near penalty −21.4pp*** — same structure as DecoupledDots
- **Object-specific**: ZdNoi and ZdCoh matched for total scene depth change; disruption tracks coherent object identity not scene disruption level
- **Color vs depth resolved by DecoupledDots**: color is null; the F2 effect here is entirely depth

## Key Findings (DepthSwapCtrl, 2026-03-30)
- **ZdA kills cueing**: +12.5pp n.s. (vs N=+34pp**). Cued dot changes depth plane at tStart.
- **ZdB enhances cueing**: +56.2pp***. Cued dot stays in plane; only non-coh changes depth.
- **ZdA/ZdB are matched for disruption count** — difference is specifically whether COHERENT translator changes plane
- **Far > Near** (binocular N): Far=+56pp**, Near=+12pp n.s. N-Far collapses monocularly → stereoscopic in origin
- **Monocular sessions**: 2× R-eye (L closed, n=385) + 2× L-eye (R closed, n=384) = n=769 pooled
- **Master summary** (bino n=384 vs all mono n=769):
  - Dot cueing: +19.8pp*** bino → +7.1pp* mono (attenuated but survives)
  - Depth-field cueing: +12.5pp* bino → +7.1pp* mono (survives with larger n)
  - Near/Far: +9.4pp† bino → +1.2pp n.s. mono (entirely stereoscopic)
- L-eye sessions have higher overall accuracy (44%) than R-eye (36%) — floaters in R eye visible
- Session-to-session variance in monocular cueing is large at n=192; need more data
- **Geometric confound**: depth change of 0.05m at 2m induces positional shift of 0–5 arcmin per eye (scales with eccentricity), up to 49% of translation distance at aperture edge. In ZdA, coherent translator gets this spurious shift; in ZdB only the non-coh does. Both depth-plane grouping and monocular confound accounts are viable — need R-eye test to dissociate.

## Key Gotchas
- ADB unauthorized: toggle Developer Mode off/on in Meta Horizon phone app
- thumbstickDeadzone too high -> silent canceled responses
- Skip menu auto-fires if no input delay (trigger held from scene transition)
- Fixation crosshair arms extend to 1.0deg, exclusion radius must be >= 1.1deg
- Swap toggles default false — must use correct experiment asset
- DirectionalFeedbackSpot needs responseController ref in Inspector
- Translation is 80ms (set in assets), code default was 40ms (now fixed)
- Near = −depthOffset_m along transform.forward, Far = +depthOffset_m (verified in Quest)
- CUED = delayed dots translate (NOT depth plane) — easy to confuse when implementing new swaps
- Unity Library cache can hold stale ScriptableObject values — Reimport may not fix; code-level override preferred
- `balanceDelayedFieldColor=false` path now uses COLOR_RED trials and forces nonDelayedColor=delayedColor
