# VRDots — Next Steps
*Prepared 2026-04-09. Single observer (GS) pilot stage.*

---

## The gating question

Everything downstream depends on one finding: **does the F1×F2 conjunction replicate in a second observer?** Three thousand trials of consistent GS data establish the finding; they do not establish its generality. No amount of parametric characterization in GS changes this situation. If the conjunction generalizes, the project is publishable. If it does not, the n=1 phenomenon is still interesting but the interpretation changes fundamentally.

**Getting a second observer into the headset on existing assets is therefore the highest-return action available, requiring zero new development.**

---

## Priority 1 — Second observer

### Step 0: Stereo and task screening (before any swap session)

Per Catak et al. (2022) — see `catak2022_fixation_methods.md`:

- **DepthCheck session** (`Exp_DepthCheck_005m`): confirm observer can perceive the 0.05m depth separation. If performance is at chance, increase depth or investigate IPD calibration before proceeding.
- **Practice criterion**: >25% correct heading identification (2× chance) on a no-swap baseline block before entering the swap experiment.
- **Equiluminance calibration** (if running R/G two-color conditions): HFF task to match red and green luminance on the Quest display. Not needed for all-red DepthSwapCtrl.
- **Nonius line vergence check**: confirm observer can use the nonius lines to verify vergence before trial initiation. Consider making nonius alignment a software-enforced gate (trial does not start until observer confirms alignment), rather than relying on observer self-report.

### Step 1: DepthSwapCtrl binocular (50% swaps)

**Asset**: `Exp_DepthSwapCtrl` — all-red, N/ZdA/ZdB, 0.05m depth, binocular.

**Why this first**: Cleanest design — no color confound, no 4-way factorial to power up. The ZdA-kills / ZdB-enhances dissociation is the smoking gun for object-specific depth tracking. Three conditions × CUED/UNCUED × Near/Far are achievable in 1–2 sessions (~384 trials each). This is the core replication target.

**Target**: n ≥ 384 valid trials binocular. If ZdA and ZdB dissociation replicates in direction, the main finding is established in a second observer.

### Step 2: DecoupledDots confirmatory session (100% swaps)

**Asset**: `Exp_DecoupledDots_005m` — one session to confirm color null (F3 ≈ 0) and depth effect (F2) in the second observer. Not needed for the core replication, but closes the loop on the color-vs-depth dissociation. Run after Step 1.

---

## Priority 2 — DepthParam second sessions (GS, no new development)

All parametric claims about the Far > Near asymmetry as a function of depth separation rest on n=32/cell (single sessions, 2026-04-02). The crossover region — where Near cueing transitions from positive to penalized — is between 0.03 and 0.05m but is not precisely located. Wilson 95% CIs at n=32 are ±~15–20pp, wide enough that the shape of the parametric function is unresolved.

**Immediate targets**: second sessions at **0.05m** and **0.10m** — the two depths that straddle the crossover. Two sessions each at these depths doubles power and either confirms or destabilizes the parametric story.

**Longer term**: fine-grained sweep (0.033 / 0.038 / 0.042 / 0.047m) to locate the crossover precisely and test whether it maps to stereoacuity threshold at 2m. Wait until n ≥ 64/cell at 0.05m and 0.10m first.

---

## Priority 3 — SOA manipulation

### What it tests

The cue-to-translation SOA is currently fixed at ~293ms (22 frames at 75Hz) in all experiments. This was chosen because prior 2D work on these stimuli showed it produces near-maximum cueing effects. **The effect of SOA on the overall cueing magnitude is therefore already known for zero-disparity conditions** and its replication in VRDots would be unsurprising.

The novel and diagnostic target is the **interaction of SOA with the Far > Near asymmetry** — specifically, whether the gap between Far and Near cueing changes across SOA values. This is what dissociates the two current mechanistic accounts of the asymmetry:

**Gradient migration account**: The Far > Near asymmetry is a *dynamic* process. During the delay interval, attention drifts from the cued depth plane toward Far, driven by a continuous asymmetric gradient. At short SOA, migration has not had time to occur: Near cueing should be approximately as strong as Far cueing (the gradient hasn't eroded the Near cue's effectiveness yet). As SOA lengthens, Near cueing weakens and Far cueing stays strong or strengthens — the gap grows.

**Bounded-window account** (GS, introspective): The asymmetry is *structural* — it is a property of attentional allocation geometry at the moment of selection, not something that builds up during the delay. Near-attending always leaks into Far because there is nothing beyond Near to bound the window; Far-attending is bounded because nothing lies beyond it in the display. Prediction: the Far > Near gap is approximately SOA-invariant.

These are genuine divergent predictions from a single, easy manipulation.

### Implementation

Minimal development: add new ExperimentSpec assets at 3–4 SOA values (e.g., 150ms / 300ms / 600ms / 900ms), keeping all other parameters fixed. No C# changes required. Run within-observer (GS or second observer) in separate blocks.

### Expected results

- **Overall cueing effect**: will vary with SOA in a known inverted-U or monotone-increasing function (consistent with 2D prior data). Not the primary target.
- **Far > Near gap**: this is the primary target. If it shrinks at short SOA (and recovers at long SOA), gradient migration is supported. If it is stable across SOA values, bounded-window or a fixed disparity-processing asymmetry (Calabro & Vaina 2011 — MT population anisotropy) is supported.

This is also the first published SOA function in a stereoscopic surface-based cueing paradigm — it has inherent novelty independent of its mechanistic payoff.

---

## Priority 4 — Fixation-depth reversal

### What it tests

Currently: fixation at 2.0m; Near plane at 1.975m (crossed disparity, in front of fixation); Far plane at 2.025m (uncrossed disparity, beyond fixation).

The **vergence/gradient account** says the Far > Near asymmetry is fixation-centered: attention spreads more easily beyond the fixation plane (toward Far) than in front of it (toward Near). Moving fixation to the current Near depth (1.975m) should re-anchor the gradient — Near becomes the fixation plane, Far becomes further-beyond — and the asymmetry should weaken or reverse.

The **disparity-driven account** says the asymmetry is intrinsic to the cortical representation of crossed (Near) vs. uncrossed (Far) disparities — an MT or V1/V2 population-level property that does not depend on where the observer is fixating. Under this account, moving fixation depth does not reverse the asymmetry because the disparity signs of the planes are unchanged.

### Implementation

Minor change to fixation target depth in the asset. Run the same N/ZdA/ZdB design at fixation depths of 1.975m and 2.025m (the current Near and Far planes). No C# changes required. Chen et al. (2012) did a fixation-depth manipulation in a reflexive attention paradigm and found no reversal (supporting disparity-drive); a VRDots version would be the first test in a sustained surface-selection context.

---

## On 100% vs. 50% swaps going forward

The 100% swap design (DecoupledDots N/C/Z/CZ) has served its purpose: it established cleanly that color is null (F3 = 0) and that the depth effect (F2) is real. That question is answered for GS.

**50% swaps (ZdA/ZdB) are the right tool for everything remaining**, for three reasons:

1. **Mechanistic clarity**: The object-specificity argument is most direct in the 50% design. ZdNoi and ZdCoh are perfectly matched for total scene disruption — only which dots change differs. The 100% design does not provide this matched comparison.
2. **Dose-response already ruled out**: DepthColorLinked (50% swap, ZdCoh) produces approximately the same disruption as DecoupledDots (100% swap, Z). Increasing to 100% buys nothing beyond what you already have.
3. **Efficiency**: Three conditions (N/ZdA/ZdB) vs. four (N/C/Z/CZ) means faster power accumulation per session, especially important for second observers.

The one scenario justifying return to 100% swaps: if a second observer shows anomalous color effects in DepthSwapCtrl, a confirmatory DecoupledDots session would localize whether the anomaly is depth-specific or color-confounded. Otherwise, use 50%.

---

## Summary table

| Priority | Experiment | Asset | New dev? | Scientific payoff |
|---|---|---|---|---|
| 1a | Second observer — DepthSwapCtrl binocular | Existing | None | Generalizability of F1×F2 — gating for publication |
| 1b | Second observer — DecoupledDots | Existing | None | Color-null replication |
| 2 | GS DepthParam second sessions (0.05m + 0.10m) | Existing | None | Nail parametric crossover |
| 3 | SOA manipulation (N/ZdA/ZdB at 4 SOAs) | New assets | New ExperimentSpec assets only | Dissociate gradient migration vs. bounded window; first published stereo SOA function |
| 4 | Fixation-depth reversal | New asset | Minor | Vergence-driven vs. disparity-driven asymmetry |
| 5 | Second observer at DepthParam (0.05m + 0.10m) | Existing | None | Generalize parametric claims |
| 6 | Fine-grained depth sweep (0.033–0.047m) | New assets | New ExperimentSpec assets only | Locate crossover, test stereoacuity link |

---

## What is NOT a priority right now

- **Endogenous color Design B** (block instruction + 50/50 validity): scientifically interesting but a large step away from the established findings. Better positioned as a second paper once the depth story is replicated and consolidated. Design is complete — see `endogenous_color_design.md`.
- **Three-plane display** (critical test of attentional topology vs. Calabro & Vaina): highest mechanistic value but requires Unity development (new depth-plane layer). Deferred until the core findings are replicated.
- **ERP/MEG**: compelling for neural localization but requires a lab with the infrastructure. Long-term goal.

---

*Document created 2026-04-09. Update as sessions are completed and priorities shift.*
