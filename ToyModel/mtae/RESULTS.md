# MT autoencoder toy — results log

# ===== RESUME HERE: POINT-SET MODEL, 2 V1 HC -> 1 MT HC (2026-07-07 night, ps_pointset.py) =====
The CORRECT implementation GS asked for, replacing the flawed per-token ps_wire.py. This is the
point-set model's SEGREGATED idealization (= ps_seg / SFN poster): because at the V1 cRF scale the
S&B stimulus has ~0.1-0.2 dots/cRF/field, each active V1 hypercolumn is dominated by ONE surface, so
the two transparent surfaces are TWO V1 hypercolumns (A=first-on, B=delayed/cued), 8 directions each,
feeding ONE MT hypercolumn. NO oracle tagging — surface identity is the hypercolumn; cooperation is a
legitimate within-HC pool. Faithful engine: PSP = K(=ff^p) * FB(like-to-like MT->V1) * Coop(1+CoopL*
E_s, E_s = SLOW saturating within-HC pool) / Norm(global recurrent); MT = Reynolds-Heeger competition
P_d^2/(sigM^2+sum P^2). Read-out = MT[UP]-MT[DOWN] over test window.
RESULT (cue = delayed-onset feature adaptation; the physically-correct cue, = GS's spec):
  coop OFF (CoopL=0):  no-swap +0.013   swap +0.006   (weak, feature-based)
  coop ON  (CoopL=8):  no-swap +0.166   swap +0.037   (cooperation amplifies ~13x; SWAP SURVIVES +)
  cued/uncued RATIO survives well: ~1.9x no-swap, ~2.3x swap (both fields more suppressed under swap
  so the DIFFERENCE shrinks, but the ratio is preserved). Fig figs/ps_pointset.png.
MECHANISM (correct, no cheat): delayed onset -> B less adapted -> B wins the within-HC cooperative
  winner-take-all; the SLOW non-directional pool E_B carries B's dominance THROUGH the base->translation
  (and swap) direction change -> cued>uncued survives. MT competition converts it to a read-out
  difference (the attended/dominant non-translating surface suppresses the other's translation).
KEY FINDING (why adaptation, not attention, is the cue): the pure directional-attention account
  (cue='attend', no adaptation) REVERSES under swap (CoopL=0: +0.031 -> -0.031) AND cooperation CANNOT
  rescue it (-0.026) -- because the FIRST-ON field wins the cooperative head-start (it builds E during
  the solo period before B appears). Adaptation is NECESSARY: it suppresses the first-on field so the
  cooperative WTA binds the CUED (delayed) surface. Vindicates the delayed-onset-via-adaptation spec.
⚠️ HONEST CAVEAT (do not overclaim): swap-survival DIFFERENCE (+0.037) is ~0.22x no-swap (+0.166),
  weaker than ps_seg's ~1.0 (which used clean attention + no head-start). Here swap coincides with test
  onset, so under swap BOTH non-translating fields go fresh and globally suppress via MT competition,
  shrinking absolute magnitudes. Ratio survives; difference is small. To strengthen: separate swap from
  test onset (let swapped base motion register first), or a cleaner attention+adaptation regime. TUNING
  is not fully explored. Params: BETA_AD=0.3 DECAY_AD=0.05 TAU_E=10 KSAT=0.6 CoopL=8 sigM=0.3.
NEXT (check w/ GS): (1) strengthen swap survival (swap-before-test timing); (2) spatial version (many
  cRF hypercolumns, moving dots) -- the documented motion-following-cooperation gap; (3) density knob.

# ===== HAND-WIRED PS **RETRACTED / FLAWED** (2026-07-07 night, ps_wire.py) =====
⛔ The "CONFIRMED" claim below is WRONG. GS caught two fatal flaws; diagnostics (ps_wire_diag.py)
confirm both. DO NOT cite ps_wire.py's 1.35x as a result.
 FLAW 1 — the "cooperative lateral" is NOT a lateral: ctxA/ctxB are SEPARATE PER-DOT arrays, so each
   dot's translation is boosted by its OWN field's context. That is oracle surface-tagging; it assumes
   the very segmentation the model was supposed to produce. Replace it with a REAL spatial lateral
   (V1 RF cells pooling BOTH intermingled fields) and the advantage COLLAPSES to ~1.0 (even inverts:
   0.92-0.99x, ps_wire_diag.py part B). The base motions are separable by direction (A=left,B=right)
   only WHILE horizontal; during the translation the judged dots move UP, so their base direction is
   gone -> routing the cued base bias to the cued up-motion REQUIRES token/trajectory tracking = the
   segmentation itself. Same lesson as slot-vs-distributed AE: binding is the hard part, not a gain.
 FLAW 2 — the SWAP is a no-op: it flips only the horizontal base dirs, but the U-D detector never
   reads horizontal channels, and the bias is precomputed per-dot pre-swap. det is IDENTICAL to 2
   decimals swap vs no-swap (ps_wire_diag.py part A). "Survives swap" was vacuous; the swap tests
   nothing as coded. A real swap test needs the readout to depend on what the swap changes.
 SO: ps_wire.py does not demonstrate object-based cueing on the faithful stimulus. Kept for the
 record + the honest negative (a genuine spatial lateral fails). figs/ps_wire_*.png/gif show the
 (flawed) per-token version. NEXT if resumed: either (a) give the model a real binding/segmentation
 stage (slots / trajectory tracking) and let cooperation ride on THAT, or (b) redesign the swap so it
 actually perturbs the readout. Check with GS on direction.
--- original (WRONG) claim, retained for context: ---
# ===== HAND-WIRED PS CONFIRMED (2026-07-07 night, ps_wire.py) =====
DONE — the agreed next step. Hand-wired PS model on the faithful stimulus (NO training), reusing
real_stim's geometry/timeline. Confirms the cued translation-detector advantage directly and it
SURVIVES THE SWAP. Files: ps_wire.py (model + figs), ps_wire_anim.py (animation).

THE THREE HAND-SET PS CONNECTIONS + the key design choice that makes cooperation load-bearing:
 - DIRECTION-SPECIFIC adaptation carried by the dots: only the HORIZONTAL base channel adapts. The
   test translation (UP) is a FRESH direction, so the UP channel is EQUALLY un-adapted for BOTH
   fields. => the onset/adaptation asymmetry lives ONLY in the base channel and CANNOT reach the UP
   detector on its own. (This is why adaptation alone gives NO cued advantage in this readout — the
   coop-OFF ablation proves it, ratio 1.0.)
 - LIKE-TO-LIKE MULTIPLICATIVE FEEDBACK (MT dir d -> V1 dir d): amplifies the cued field's stronger
   (less-adapted) base channel more, so the bias it hands off is bigger.
 - COOPERATIVE LATERAL carrying base->orthogonal: each surface's sustained horizontal base motion
   builds a persistent per-dot context ctx (low-pass of its feedback-amplified base gain); when the
   dot then translates, its UP contribution is multiplied by (1 + COOPG*ctx). ctx is larger for the
   un-adapted CUED surface => its translation is amplified. This is the ONLY path the base bias
   reaches UP, so the cooperation IS the mechanism (GS was right; my earlier "MT-adaptation can't"
   was wrong — it does, THROUGH the connection).

RESULT (density 60, COOPG=8, FBG=0.6, cue delay T_ON=20; reps-averaged MT detector U-D):
   coop OFF:  no-swap cued/uncued 0.98x   swap 1.01x     (adaptation alone => no cued advantage)
   coop ON :  no-swap 1.29x               swap 1.31x     (cued > uncued, SURVIVES SWAP)
 Cued advantage scales with cue delay and COOPG (T_ON 12->26, COOPG 4->16 => 1.05x .. 1.99x); it is
 the onset-driven base-adaptation ratio, transferred to UP by cooperation. Swap survival is because
 ctx is built from horizontal motion BEFORE the swap and travels with the surface's dots.
WHY IT SURVIVES SWAP (vs the failed direction-adaptation-only intuition): the carried bias is
 surface/token-bound (per-dot ctx), not tied to the absolute base direction, so flipping the base
 dirs at test does not erase it.
FIGS: figs/ps_wire_detector.png (time course + coop-OFF/ON x swap bars + density sweep),
 figs/ps_wire_v1mt.png (V1 4-dir maps + MT bars, cued vs uncued, shows UP-channel transfer),
 figs/ps_wire_anim.gif (animated dots + V1 UP map + MT bars, cued vs uncued, swap trial).
⏸ CHECKPOINT (GS asked to confirm before expanding scope). Options next: (a) tie the density knob to
 crowding of the base channel (denser => base context saturates/normalizes => weaker transfer);
 (b) retrain the connections with an objective that actually rewards attending the cued field
 (mix swap/no-swap to close the adaptation shortcut, + stability fix) and compare learned vs
 hand-wired kernels; (c) map ctx/coop onto the AE decoder (learned like-to-like + cooperation).

# ===== FAITHFUL-STIMULUS THREAD (2026-07-07 late) =====
Goal: model's INPUT = the real stimulus (no rotation): two fields OPPOSITE horizontal motion,
delayed-onset cue, ONE field briefly translates in the ORTHOGONAL (up/down) direction at 50%
coherence; motion swap; density range. Read out a TRANSLATION DETECTOR in MT (up/down).

Stimulus movies: dot_movie3.gif (2D dots, correct), stim_viz.png (1D raster). real_anim.gif =
animated stimulus + V1 (dot size = gain) + MT bars, SWAP vs NO-SWAP.

WHAT WORKS (real_stim.py, MECHANISTIC, not trained): DOT/surface-level adaptation (delayed field's
dots less adapted) -> MT translation detector responds ~1.2x more to CUED than UNCUED translation,
SAME with and without swap, across density 15-120 (figs/real_detector.png). Clean, graded effect.

WHAT FAILED (real_train.py, GS spec = MT direction-adaptation + mult feedback + TRAINED lateral):
training unstable + chance detection + NO cued advantage. ⚠️ I (Fable) OVERSTATED this as "MT
adaptation can't do it" -- GS correctly pushed back: the PS model (adaptation + like-to-like feedback
+ cooperation) DOES work; cooperation transfers the base-motion bias to the translation. My TRAINING
just never found those connections because (a) BPTT unstable, (b) "detect U/D" objective gives ZERO
pressure for a cued advantage (detection works regardless of which field). Training-setup failure,
NOT a mechanism claim. RETRACTED the overstatement.

NEXT STEP (agreed direction): HAND-WIRE the PS connections (MT direction-adaptation + like-to-like
MULTIPLICATIVE feedback + cooperative lateral that carries base->translation) on the faithful
stimulus, and show the MT translation-detector CUED advantage + swap survival directly (confirm what
we already know works). THEN, only if wanted, retrain with an objective that actually rewards
attending the cued field (like mixing swap/no-swap forced cooperation earlier) + stability fix.
Files: real_stim.py, real_anim.py, real_train.py (failed), dot_movie*.py, stim_viz.py.

# ===== CUED-SWAP / TRAINED-CONNECTIONS THREAD (2026-07-07, ps_train.py) =====
Question (GS): the PS model (hand-designed V1 cooperation linking successive motions) gives a
cued-swap effect. Does a TRAINED network find that solution, a different one, or none?
Setup: ONE MT hypercolumn (D=2 dir units) + FIXED feature adaptation + L=32 V1 positions; trainable
2x2 ff/fb/lat matrices. Trial = two fields, one delayed (cued=B), motion swap mid-trial. Objective:
after the swap, MT signals the CUED object's motion (cross-entropy; also gives larger response,
4.6x, but CE overshoots the "reasonable amplification" spec).
FINDINGS:
- Trained on SWAP-only: 100%, BUT it's the ADAPTATION SHORTCUT, not tracking. The delayed onset
  makes the cued object's post-swap direction = the more-adapted direction, so "amplify the more-
  adapted dir" scores 100%. Proof: same model on NO-SWAP trials (cued = fresh/less-adapted dir)
  scores 0% -- systematically picks the wrong one. Shortcut confirmed (this is GS's "co-occurs with
  larger response to the other field" confound: cued perfectly confounded with adaptation asymmetry).
- **Trained 50/50 SWAP + NO-SWAP (closes the shortcut): the network is FORCED to discover V1
  cooperation.** WITH trainable V1 lateral: 100% swap AND 100% no-swap. WITHOUT lateral (control):
  100% swap / 0% no-swap -- cannot beat the shortcut. So V1 cross-direction lateral coupling is
  NECESSARY and EMERGES from training = a PS-like solution, learned not hand-wired.
- NUANCE (GS predicted "different solution"): learned cross-direction lateral is INHIBITORY
  (off-diag -0.73/-2.03, coopg 2.33), not PS's FACILITATORY cooperation. Same structural motif
  (V1 lateral links successive motions), opposite sign.
- Mechanism: when a dot's motion flips at the swap, cross-direction V1 coupling makes a position-
  specific signature that survives pooling to the single MT hypercolumn -> swap becomes detectable.
- Files: ps_train.py (trainable), ps_v1coop.py (hand-designed PS control, fixed connections),
  mt1_adapt.py (adaptation mechanism demo), mt1_headB.py (readout-memory route, set aside).
## ==========================================================================

## ===== TL;DR: TRANSLATION-DOMAIN ACCOMPLISHMENTS (as of 2026-07-07) =====
Headline: a concrete, tested REFINEMENT of Cavanagh's "attention for free from autoencoding" —
it holds ONLY for an OBJECT-FACTORED code, not a plain distributed autoencoder.
1. Reconstruction target settled: reconstruct V1/positional (motion inferred), NOT pre-computed
   motion energy (which pre-solves separation). (recon.py)
2. A plain AE genuinely USES motion, not per-frame copying: temporal scramble -> 6.5x worse. (recon.py)
3. Recurrent V1<->MT scaffold (FF+FB+lateral, divisive-norm settling) built + STABLE across wide
   gain; structured feedback measurably reshapes settled V1 (leverage 12-90%); cooperation floods
   without inhibition. (recurrent_scaffold.py, leverage_check.py)
4. NEGATIVE (pivotal): distributed recurrent AE reconstructs/denoises well (structure corr 0.83-0.87)
   but gives only WEAK cueing (~0.10) -- additive OR multiplicative feedback. Reconstruction alone
   does NOT buy object-based selection. (head_a_recon.py, cue_probe.py)
5. POSITIVE (pivotal): OBJECT-FACTORED (slot) code gives selection FOR FREE -- one-slot readout
   selectivity ~0.77 overall, ~1.0 for well-separated directions, NO attention training. So
   FACTORIZATION, not attention training, is the missing ingredient. (slot_ae.py)
6. Common-fate limit (intrinsic, every model): selectivity scales with angular separation
   (10deg->0.08 ... 90deg->0.95 ... 180deg->~1.0). Surfaces that move alike can't be factored.
7. ROBUST to non-separable/noisy motion: per-dot direction jitter -> graceful degradation
   (0deg->1.0, 30deg->0.81, 60deg->0.45), not collapse. (stress_slot.py)
Rotation is the frontier (fails; needs MST-like or iterative routing) -- see flow_slot section.
OPEN in translation: fold slots into the recurrent scaffold; head B on swap cueing; connect to
behavioral data (density knob etc.).
## =====================================================================

Premise: Cavanagh et al. (2023) propose object-based attention's feedback
specificity is a byproduct of an autoencoder reconstructing its own early-visual
input. GS instantiation: "MT" = coarse, direction-tuned bottleneck trained
unsupervised to reproduce a V1 motion-energy population from two overlapping
transparent dot surfaces. No surface labels supplied — the bet is that training
implicitly encodes the common-fate statistic.

## Setup (`mtae.py`)
- V1 input: (D=8 dir channels, 32x32) synthetic motion energy; each dot = spatial
  Gaussian blob (sigma 0.9) x von Mises direction tuning (kappa 2.5). Circular aperture R=14.
- MT bottleneck: conv AE, 32->8 spatial (4x coarser RFs), 16 channels. Pure masked-MSE reconstruction.
- Cueing readout: measure each MT unit's preferred direction from single-surface probes
  (post-hoc, NOT built in); gate MT code to units near the cued direction; decode;
  score selectivity = corr(recon|cueA, surfA) - corr(recon|cueA, surfB), averaged over both cues.

## Run 1 (2026-07-07, seed 0, 3000 steps, ~50s MPS)
- Reconstruction: loss 0.050 -> 0.002. Clean (see figs/recon.png).
- **Cueing works: selectivity = +0.55 @ density 35.** Direction-defined cue pulls out one
  transparent surface (figs/cueing.png). Core Cavanagh/GS claim confirmed in principle:
  unsupervised MT-AE supports surface-selective feedback with no a-priori assignment.
- **Density does NOT collapse cueing** (figs/density.png): selectivity flat-to-rising
  0.38 (n=10) -> 0.59 (n=120); recon MSE rises but selectivity doesn't fall.
- **Diagnostic — selectivity tracks angular separation, not density:**
  sep 15deg -> +0.02, 30 -> +0.07, 45 -> +0.15, 60 -> +0.25, 90 -> +0.45, 120 -> +0.59, 180 -> +0.69.

## Interpretation
The "segmentation" here is **trivial / inherited from V1**: opposed surfaces already live
in different V1 direction channels, so the bottleneck just preserves that separability.
No binding is being learned or stressed -> density can't break it. Selectivity is a pure
function of how distinct the two directions are (0 at 15deg). This is why the density
collapse seen in the VRDots data is NOT reproduced.

## What's missing to get the density knob (next fork)
The model needs density to *interact* with separation. Candidates, most-promising first:
1. **Divisive normalization / motion-opponency in the V1 front-end** so dense opposed
   fields mutually suppress (cf. handoff note "break ps_extract per-RF normalization at
   high density"). Makes crowding degrade the direction code itself.
2. **Position-recovery readout** — demand recovery of *which dots* at their actual
   locations, not just direction-band energy; coarse MT can't place individual dots at
   high density (MT RF vs dot spacing).
3. **Tighter reconstruction reserve** — smaller bottleneck so high density exceeds capacity.

Open question for GS: which of these is the intended physical meaning of the density
collapse? That choice drives the next model version.

---

# recon.py — plain reconstruction AE on the dot-IMAGE stack (2026-07-07)

Rebuilt with the right target (per prior discussion): input = T=5-frame stack of the
dot luminance image (positions, NOT motion energy); two overlapping surfaces, coherent
random-direction translation at 1.2 px/frame; 48x48, R=20, 40 dots/surface (medium).
Coarse 'MT' bottleneck 48->24->12, 24 channels. Masked-MSE reconstruction of the stack.

- Trained ~4000 steps (~8 min MPS). **Held-out recon error = 2.4% variance unexplained**
  on fresh unseen seeds. figs/recon_examples.png (6 fresh clips), figs/recon_frames.png
  (per-frame, motion visibly tracked).

## Temporal-scramble test (scramble_test.py) — IS it using motion? YES.
- ordered recon error 0.024; frame-shuffled recon error 0.156 -> **6.5x worse, worse on
  100% of clips.** figs/scramble.png: scrambled recon is smeared/ghosted.
- Conclusion: the bottleneck compresses via a smooth-motion prior (position+velocity),
  not per-frame copying. Motion is genuinely in the latent -> desired 'MT' behavior.

## Next: does the latent factor by SURFACE (common fate)?
That is the property needed for object-based cueing. Probe ideas: (a) two-surface vs
single-surface latents; (b) can we read out / manipulate one surface's velocity from the
code; (c) latent traversal along a velocity direction.

---

# recurrent_scaffold.py — recurrent V1<->MT scaffold, STABILITY milestone (2026-07-07)

Direction reset (GS): move from the feedforward AE to a RECURRENT V1<->MT network with
all three connection types (feedforward V1->MT, feedback MT->V1, lateral V1->V1 & MT->MT),
both levels = direction hypercolumns. This is the shared substrate for two future arms:
head A = reconstruction (recurrent AE), head B = task/bias ("translational edge for the
delayed/cued field", cue-injected, supervised). Compare learned feedback+lateral kernels
between arms, and vs the PS model's hand-wiring. Recurrence also buys the cueing TIME COURSE.

This step = stability only, NO training. Leaky settling + Heeger divisive normalization
as stabilizer. Untrained small-random conv weights.
- **Settles stably across gain 0.5-4.0**: rel-delta -> ~1e-7 by iter 60, crosses 1e-3 ~iter 20,
  no oscillation/blow-up, max activity pinned ~0.62. figs/recurrent_settle.png.
- **Caveat (honest):** activity is pinned ~0.62 independent of gain and settled V1 ~= the
  drive -> divisive normalization currently DOMINATES; feedback+lateral barely reshape the
  fixed point. Fine for a stability milestone, but the recurrent pathway needs real leverage
  once we train (else FB/lateral do nothing). Watch: normalization sigma, weight scale,
  residual/leak alpha, and whether trained weights grow enough to matter.

## Leverage check (leverage_check.py) — CONFIRMED (2026-07-07)
Installed structured (untrained) kernels: like-to-like feedforward + feedback, same-direction
cooperative lateral (Gaussian, no self-center). Swept recurrent gain, measured departure of
settled V1 from the gain=0 baseline (divnorm(drive)).
- **Recurrence has strong, controllable leverage:** reshape 12% (gain0.5) -> 29% (1.0) ->
  54% (2.0) -> 75% (4.0) -> 90% (8.0). figs/leverage.png.
- **All gains are STABLE**, not just the low ones: the gain>=4 "UNSTABLE" flags were a
  60-step-cutoff artifact. At 300 steps every gain converges monotonically (gain8:
  1.7e-3 -> 2.2e-4) with bounded, *shrinking* activity. Divisive normalization prevents
  blow-up throughout; higher gain just settles slower.
- **Functional signature:** cooperative lateral SPREADS/fills-in activity between dots (the
  PS cooperative spread); feedback enhances. At high gain it OVER-fills (washes out dot
  structure -> uniform blob). Preview: pure same-direction excitation spreads unboundedly
  (only normalization checks it); we'll likely want cross-direction suppression / surround
  to bound the spread to real surface structure -- probably learned during training.
- **Operating window for training:** gain ~1-2, sigma ~1, ~60-150 settling steps.

# head_a_recon.py — recurrent denoising AE, FIRST TRY = FLOODS (2026-07-07)
Denoising/completion: degraded V1 drive (drop 40% dots + occlude patch) -> reconstruct clean
V1 motion-energy hypercolumn, through recurrent settling (gain 1.5, 20 steps), PS-flavored init.
- **FAILED to complete.** Settled V1 = near-uniform blob filling aperture (figs/headA_fillin.png);
  held-out completion error 0.585; training loss barely moved (0.032->0.027).
- Diagnosis: OVER-FILL / flooding — cooperative spread with no counterbalancing inhibition
  floods; MSE-to-sparse-target then prefers a safe smooth field (blur local min). Same failure
  as high-gain leverage test.
- Kernels (figs/headA_kernels.png): training mostly PRESERVED like-to-like init, added only a
  little cross-direction suppression in feedback (MT dir0 -> V1 dir5/6 negative). Did NOT learn
  enough inhibition to stop the flood.
- Cueing +0.219 NOT trustworthy given broken reconstruction (likely trivial direction-band
  energy correlation, not location-specific).
- LESSON: leverage regime (strong cooperation) != completion regime. Need suppression to SHAPE
  the spread. Fixes to consider: (a) lower gain / longer settle; (b) build in / encourage
  inhibitory surround + cross-direction opponency; (c) loss that penalizes flooding (e.g. match
  sparsity / correlation loss instead of raw MSE); (d) make MT bottleneck tighter so completion
  must be selective. NEXT DECISION: which fix.

# head_a fixes 1+2 (gain 1.0, gentler task, correlation loss) — 2026-07-07
- **Reconstruction FIXED:** flooding gone; settled V1 shows dot structure + fills occlusions;
  held-out structure corr 0.83. figs/headA_fillin.png.
- **Lateral connectivity FLIPPED to inhibition:** same-dir spatial kernel now has a NEGATIVE
  center (lateral inhibition / sharpening), opposite of the cooperative init. figs/headA_kernels.png.
  So this regime reconstructs by SHARPENING (suppress background), NOT PS-style cooperative spread.
- **Cueing weak-for-free.** Fair probe (cue_probe.py; measured MT channel direction tuning,
  |R| up to 0.79, then clamp aligned channels, sweep strength): peaks +0.119 +/- 0.112 at
  strength 1.0 -- ~1 SD, and cue-A vs cue-B reconstructions barely differ (figs/headA_cueing.png).
- **KEY DIAGNOSIS (next hypothesis):** feedback is currently ADDITIVE (Iv = s + gain*(lat+fb)).
  Additive feedback floods when strong, grips weakly when moderate -> the recon-vs-cueing tension.
  PS model + Cavanagh use MULTIPLICATIVE feedback x feedforward ("downward multiplicative input x
  feedforward stimulation", GS): feedback enhances ONLY already-driven units -> non-flooding AND
  selective. Likely the missing ingredient for cueing to emerge for free. NEXT: multiplicative fb.

## NOTE (GS, 2026-07-07): additive feedback under a nonlinearity ~ partly multiplicative
With a nonlinear activation (we have ReLU + divisive normalization), additive feedback into
the current is NOT purely additive in its effect on output -- near threshold, drive+feedback
is supra-additive, approaching multiplication. So "additive vs multiplicative" is a soft
distinction, and a FUTURE option is to let the model TRAIN the interaction/connection type
(learn a gate between additive and multiplicative) rather than us choosing. For now we test
the explicit multiplicative form as the cleaner manipulation.
Consequence noted: a purely multiplicative gain on the drive CANNOT fill an occluded region
(0 drive x gain = 0) -- that is the generative role (predictive-coding), distinct from the
attentional-gain role. So for the multiplicative test we DROP occlusion and use denoising
(dropout + additive noise), the setting where multiplicative gain is the right tool.

# Multiplicative feedback (2026-07-07) — did NOT rescue cueing
Iv = s*(1 + gain*relu(fb)) + gain*lateral; denoising task (dropout+noise, no occlusion).
- Reconstruction slightly better: structure corr 0.866.
- **Fair cueing still WEAK: peaks +0.092 at strength 4 (plateaus); cue-A ~= cue-B recon
  (figs/headA_cueing.png).** MT direction tuning came out weak too (|R| several ~0).
- Actually WEAKER than additive-with-occlusion (+0.119). Likely because multiplicative feedback
  OUTSOURCES "where" to the drive (0 drive x gain = 0), so it never learns location-specific
  reprojection -> a top-down MT clamp yields diffuse gain, not selective.

## PIVOTAL INTERIM FINDING
Across additive/multiplicative x with/without occlusion, RECONSTRUCTION-ONLY training buys only
weak object-based cueing (~0.1, ~1 SD). Attention does NOT robustly emerge "for free" here.
Diagnosis: reconstructing BOTH surfaces together does not REQUIRE the code to be separable into
one surface -- nothing in the loss rewards selectability. Our MT is a distributed direction map,
not an object-FACTORED code. Cavanagh's "activate the object node" quietly assumes an
object-factored representation we don't have.
Caveats: small net, 2500 steps, proxy cueing readout (boost direction-aligned MT channels).

## FORK (for GS)
(a) Force selectability unsupervised: object-FACTORED / slot bottleneck (K slots compete to
    explain dots) -> tests whether factorization is the missing ingredient for for-free attention.
(b) Go to head B (train for the cued bias) -> establishes the supervised upper bound + contrast;
    story becomes "reconstruction gives the representation but not the selection."
(c) Rework the cueing inference op (proxy readout may under-measure).
Lean: (a) is the most interesting -- it directly tests whether "for free" attention needs an
object-factored code rather than a plain AE.

## HEAD B DESIGN CONSTRAINT (GS, 2026-07-07) — train on SWAP cueing, not basic cueing
The BASIC cueing effect (cued surface read out better) emerges trivially from normalization /
adaptation (already documented) -> a model reproducing it proves nothing about object-based
attention. Head B must train on the SWAP cueing effect (identity surviving a feature swap, e.g.
MC), which is what discriminates object-based accounts. Bias source is a design choice: candidate
= ADAPTATION giving the advantage (delayed/cued field less adapted -> higher gain). Decide bias
before building head B.

# slot_ae.py — OBJECT-FACTORED bottleneck (fork a) — CONFIRMED (2026-07-07)
Slots factor by VELOCITY (surfaces overlap in space). Each slot = separable component:
direction profile w_k(dir) x density map d_k(x,y); recon = Σ_k d_k ⊗ w_k, K=2. Reconstruction
only; "attend surface k" = read out slot k. No attention training, no cue injection.
- Reconstruction frac-var 0.115. Training ~90s.
- **One-slot readout selectivity +0.765 +/- 0.371 — vs ~+0.10 for the distributed recurrent AE.**
  figs/slot_readout.png (hard/similar-dir seeds), figs/slot_separated.png (clean, well-separated).
- **Selectivity scales with angular separation** (slot_probe.py): 10°→0.08, 45°→0.60, 90°→0.95,
  135°→1.07, 180°→1.04. Near-perfect one-slot recovery for opposed/well-separated surfaces;
  degrades to 0 as directions converge = intrinsic common-fate limit (same axis as model 1).

## CONCLUSION (the pivotal result of this thread)
Cavanagh's "object-based attention emerges for FREE from autoencoding" holds ONLY if the code is
OBJECT-FACTORED. A plain distributed reconstruction AE does NOT give selection (~0.10, additive or
multiplicative fb) because reconstructing both surfaces together never requires separability. Give
the bottleneck object structure (slots competing by common-fate velocity) and selection appears for
free (~1.0 at good separation), with NO attention training. So factorization, not attention
training, is the missing ingredient -- a concrete refinement of the Cavanagh claim, in the
transparent-motion setting.
CAVEAT: our motion energy is exactly separable (dir ⊗ density) and each surface is exactly one
component, so the separable-slot bottleneck is matched to the stimulus by construction -- proves the
PRINCIPLE, but the ease is partly built in. Stress next with non-separable energy (speed spread,
noise, >2 surfaces, K != #surfaces).

# slot stress test — NON-separable energy (stress_slot.py) — ROBUST (2026-07-07)
Broke exact separability: each dot within a surface gets its own direction theta_surf+N(0,jit),
so a surface is a broadened non-rank-1 mixture the separable slot can only approximate. Trained on
jitter range [0,40deg].
- **Factoring degrades GRACEFULLY, does not collapse** (sep fixed 120deg):
  jitter 0->1.01, 10->1.01, 20->0.89, 30->0.81, 40->0.71, 60->0.45. figs/slot_stress.png.
- Separation-dependence preserved under 25deg jitter (20deg->0.07 ... 135deg->0.90).
- Breaks only when within-surface spread (~60deg) approaches between-surface separation = genuine
  indistinguishability, NOT a model artifact.
- CONCLUSION: the exact-separability caveat is largely DISPELLED — the slot factoring result is
  robust to substantial non-separability. Object-factored code -> for-free selection survives.
- HARDER stresses still open (genuinely break the single-direction-per-slot decoder): ROTATION
  (position-dependent local direction = the real VRDots cueing-period motion; needs a slot with a
  velocity FIELD, not one global direction), and K != #surfaces (capacity mismatch).

# flow_slot.py — ROTATION stress test — TRANSLATION factors, ROTATION does NOT (2026-07-07)
Upgraded each slot to a RIGID FLOW: translation (vx,vy) + rotation (omega); local direction at
each (x,y) derived from the flow. Tested on two COUNTER-ROTATING transparent fields (the VRDots
cue-period stimulus).
- **Translation control: WORKS** — opposed-translation selectivity 1.01 (180deg), 0.59 (90deg);
  infers correct translation sign (slotA vx +0.6, slotB -0.54). Same as original slot AE.
- **Counter-rotation: FAILS** — selectivity only ~0.10-0.15 (vs ~0.9 translation); reconstruction
  poor (frac-var ~0.47); model infers omega~0 for BOTH slots and explains counter-rotation with
  TRANSLATION (figs/flow_slot_field.png quiver). Same-sense rotation control = 0 (correct: only
  speed distinguishes them, no speed channel).
- Fixes tried, did NOT help: rotation-heavy training (70% counter-rot), CoordConv (position
  channels so encoder can form curl moments). Failure is robust + rotation-SPECIFIC.
- DIAGNOSIS (two layers):
  (1) mechanical: global mean-pool is curl-blind (rotation averages to ~0 net flow); CoordConv
      alone insufficient.
  (2) fundamental: factoring rotation needs a POSITION-DEPENDENT, globally-consistent direction
      judgment ("is this local direction the CCW or CW tangent HERE?"). Local direction alone is
      uninformative (same direction = CCW at one position, CW at another). Locally, counter-rotation
      looks exactly like counter-TRANSLATION; only across-space variation reveals rotation. This is
      chicken-and-egg (need omega to route dots, need routing to estimate omega) -> a feedforward
      encoder falls into the translation local optimum.
- INTERPRETATION (nice): this IS the MT vs MST division of labor. A velocity (MT-like) slot handles
  translation but not rotation; rotation needs MST-like complex-motion/curl templates OR iterative
  flow-consistency (EM-style / Slot-Attention) routing. A real finding, not just a failed run.
- WHAT IT WOULD TAKE (next, GS decision): (i) recurrent/iterative slot routing (hypothesize omega ->
  route by flow agreement -> re-estimate, repeat), or (ii) explicit rotational/expansion (MST)
  motion templates as slot primitives.

# slot_recurrent.py — SLOTS FOLDED INTO THE RECURRENT SCAFFOLD (2026-07-07)
MT level = K=2 object-factored slots (independent per-slot density + direction profile, like
slot_ae), inferred from the current V1 estimate each settling step; slots project back to V1 as
feedback; V1 relaxes toward reconciling drive + slot reconstruction. Cue = boost one slot's
feedback contribution.
- Two failed attempts first (instructive):
  (1) softmax-over-K competition -> SYMMETRIC COLLAPSE (both slots identical, selectivity exactly 0).
  (2) loss on settled V1 -> loss FLAT / byte-identical across archs: divnorm settling pins V1 ~=
      normalized(drive), washes out slot feedback, slots get no gradient. FIX: put the loss on the
      SLOT RECONSTRUCTION (pred = sum of slots), so slots are directly responsible for the output.
- WORKS: loss 0.038->0.020; factoring selectivity +0.39 +/- 0.36 (weaker than feedforward slot_ae
  0.77 -- recurrent inference noisier -- but genuinely factoring).
- **KEY PAYOFF: DYNAMIC CUEING with a TIME COURSE** (figs/slot_recurrent.png): cueing one slot makes
  the cued surface's V1 enhancement BUILD UP over settling steps 0.07 -> peak ~0.19 (step ~9) ->
  ~0.16, while no-cue baseline stays ~0. Final cued +0.157 vs baseline +0.003. A feedforward slot
  AE cannot produce this temporal build-up -- it's what the recurrent fold unlocks, and it connects
  to the behavioral cueing build-up / onset asymmetry.
- OPEN: factoring weaker + slot readouts dim vs feedforward; could iterate (more settling, better
  slot inference). But the fold objective is met: recurrent + factored + dynamic cueing.

## Next on this scaffold
1. DONE - leverage confirmed.
2. Attach head A (reconstruction loss over settling) — recurrent AE; pull out + PLOT the
   learned feedback/lateral kernels (deferred AE payoff). Check whether training learns the
   cross-direction suppression the leverage test says is needed.
3. Attach head B (cue input + biased-target loss) for the translational-edge task.
4. Compare kernels A vs B vs PS. Consider PS-flavored initialization (structured kernels above
   are a ready starting point).
