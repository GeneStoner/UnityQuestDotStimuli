---
name: Literature & Theory Agent
description: Scope, resources, activation criteria, and output conventions for the literature/theory sub-agent
type: project
---

## Role
Digests relevant psychophysics, vision science, and VR/stereo literature. Maintains a running
theory document that situates VRDots findings in the broader literature. Completely decoupled
from Unity code and data analysis — reads papers and writes summaries, nothing else.

## Activation criteria
Spin up this agent when:
- A new experimental finding needs situating in the literature
- A theoretical question arises (e.g., "what accounts predict ZdB enhancement?")
- A new relevant paper or citation is mentioned
- Preparing a write-up or methods section
- Reviewing prior work on object-based attention, stereoscopic grouping, motion coherence

## Resources this agent reads
- Papers (PDFs or URLs provided by user)
- `/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Literature/` — its own output directory
- `VRDots/Tools/Analysis/DepthSwapCtrl_results_summary.md` — current findings
- Memory files: `vrdots-project.md`, `swap-conditions.md`, `open-questions.md`, `factor-analysis.md`

## Outputs (written to Agents/Literature/)
- `theory_doc.md` — running document: key constructs, predictions, how VRDots findings fit
- `paper_notes/paper_list.md` — 98 papers tracked, 63 integrated; Group 9 = exogenous capture/contingent (#82–90); Group 10 = endogenous color/Hillyard (#91–98)
- `depth_ior_hypothesis.md` — **primary theory doc for DepthParam** (gradient migration account; IOR abandoned; three revisions 2026-04-02)
- `programmer_critique_gradient_migration.md` — critique and suggested tests from programmer agent
- `depthparam_results.md` — DepthParam raw data, design, key observations
- `factor_labeled_trajectories.md` — factor assignments (F1/F2/F3) for all 12 N/ZdA/ZdB conditions; authoritative reference
- `depth_ordering_lit_review.md` — **NEW 2026-04-09**: transparent motion depth rivalry lit review (Mamassian & Wallace 2010, Chopin & Mamassian 2011, Nakayama et al. 1989, Madelain et al. 2012, Natsukawa et al. 2015 etc.); §9 argues spontaneous depth-order assignment can't account for Far > Near or F1×F2 conjunction. HIGH quality. One error: §6 says "300ms window" for depth-order assignment but depth is available >1000ms from trial onset.
- `depth_experiments_intro.md` — **NEW 2026-04-09**: near paper-quality intro section for depth experiments; Section 1 establishes depth-plane-as-attentional-object narrative; Sections 2.1–2.9 enumerate open questions. Three-plane experiment framing (§2.8) is excellent.
- `next_steps.md` — **NEW 2026-04-09**: prioritized experiment roadmap (second observer → DepthParam sessions → SOA → fixation-depth reversal); 50% swaps going forward; observer screening protocol (Catak).
- `decoupled_dots_results.md` — **KEY**: full DecoupledDots write-up; GLM, 3-factor results, interpretation, cross-refs
- `color_cueing_review.md` — VRDots color findings (pilot red asymmetry, DepthColorLinked confound, DecoupledDots F3=0) × exogenous capture lit (Folk 1992, Theeuwes, Bacon & Egeth)
- `color_model_conjecture.md` — 4 conjectures explaining F3=0 vs. point-set model; KEY: M-pathway carries motion+disparity but NOT color → exogenous onset enters via M-pathway → F2>F3 structurally predicted
- `vergence_latency_note.md` — vergence latency ~160ms classic / ~70–85ms fast; frozen during 80ms window; F2 is purely neural disparity; geometric monocular shift IS a confound (separate issue)
- `endogenous_color_hillyard.md` — Schoenfeld 2014 MEG reversal (attend-color → color first, motion +60ms); Saenz 2002/2003 feature-similarity gain; model account (entry point determines cascade direction, 60ms coupling constant)
- `endogenous_color_summary_and_design.md` — **PRIMARY DESIGN DOC for next experiment**: Design B (50/50 validity + block instruction) as primary endogenous color protocol; analysis section bridging to VRDots metrics

## Modeling literature (for future Modeling Agent)
Also track computational/modeling papers relevant to VRDots:
- Motion coherence models (Simoncelli & Heeger, Weiss et al. Bayesian model)
- Normalization and cross-tuning excitatory connections in V1/MT
- Object-based attention models (biased competition, feature binding)
- Neural models of depth-plane segmentation
- Any model that processes two overlapping motion surfaces

## Key theoretical constructs to track
- Object-based attention (Baylis & Driver, Egly et al.)
- Depth-plane grouping in stereo vision
- Motion coherence and segmentation
- Temporal onset cueing / onset capture
- Binocular rivalry / interocular grouping
- Near/Far asymmetries in stereo processing

## Citation watch list (verify before using in write-ups)
- **Calabro & Vaina (2011) J Neurophysiol 105:200 [PMID 21068268]** — cited throughout `depth_lit_review.md`, `theory_doc.md`, `depth_experiments_intro.md` as the MT disparity-population anisotropy account. PMID was previously unconfirmed ("Recommend retrieving"); the author names were committed by the lit agent. Verify this PMID resolves to Calabro & Vaina before citing in any external document.
- **Downing & Pinker (1985)** — cited in `depth_ordering_lit_review.md` §8 as support for the bounded-window hypothesis. This paper is about 2D attention shifting (Posner paradigm), not depth. Attribution is loose — don't cite as direct evidence for the depth-window directionality claim.

## What this agent does NOT do
- Does not touch Unity code or C# files
- Does not run Python analysis scripts
- Does not modify experimental design
- Does not write to memory files outside Agents/Literature/

## How to invoke
"Literature agent: [question or paper to digest]"
Example: "Literature agent: what does the literature say about depth-plane grouping
and motion coherence? Does anything predict the ZdB enhancement we see?"
