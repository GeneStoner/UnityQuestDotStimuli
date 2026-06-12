# SB 2010 motion-competition model — re-implementation and R&H normalization layer

Computational modeling thread, started 2026-06-10. Re-implements the
Stoner & Blanc (2010) motion-competition model from Appendix A of the paper,
verifies it against Fig 3 and Fig 6, then layers a Reynolds & Heeger (2009)
style normalization scheme on top with a fixed attentional gain replacing
adaptation.

The goal is a transparent, parameter-by-parameter scaffold that we can:
(a) confirm against the published results in S&B 2010 and R&H 2009 before
trusting any conclusions; (b) sweep parameters to understand the regime;
(c) eventually plug additional mechanisms (adaptation, surface-identity
tracking, the Stoner 2018 "point-set" feedback model) into.

## Files

### Core model and stimulus
- `parameters.py` — all SB 2010 Appendix A parameters in one place, with
  inline references to the paper.
- `model.py` — SB Stage 1 (adapting rotation channel ODE: Eqs 4–5) and
  Stage 2 (translation-detector divisive normalization: Eqs 1–3).
- `stimulus.py` — direction-channel stimulus time courses for the four
  delayed-onset trial types (CUED / UNCUED × no-swap / motion-swap),
  Mode 1 (binary amplitudes). Each trial type is reduced to "which
  channel has the 40 ms gap during translation."

### S&B 2010 reproductions
- `run_fig3.py` — reproduces Fig. 3 (no-swap, CUED vs UNCUED). Model gives
  cued > uncued bias of **+32.9 %** (paper reports ~21 %). PNG:
  `fig3_reproduction.png`. (Was +54.7 % before the 2026-06-11 translation-
  adaptation fix — see Methods note below.)
- `run_fig6.py` — reproduces Fig. 6 (no-swap and motion-swap, both
  conditions). Confirms the model's predicted **reversal** under motion
  swap: (CUED, no-swap) and (UNCUED, swap) give identical R_TD because the
  direction-channel inputs are identical between those pairs. The paper's
  data refute this reversal; that's S&B's negative result. PNG: `fig6_reproduction.png`.
- `model_diagram.py` — publication-style architecture + equations +
  parameter-table figure. PNG: `model_diagram.png`.
- `inputs_figure.py` — the four trial types' inputs side-by-side, in
  Left/Right/Up channel layout. Color-framed columns flag the input
  equivalence between trial-type pairs. PNG: `inputs_figure.png`.

### R&H normalization on the SB stimulus — canonical (verified)

- **`sb_rh_verified.py` — current canonical R&H-on-SB script.** Uses the
  bit-for-bit-verified port of `attentionModel.m`
  (`../verification/port_attention_model.py`) with time substituted for
  the spatial RF-center axis. Sweeps σ and prints the cued/uncued bias;
  also saves `sb_rh_verified.png`, a 2-panel figure with the
  translation-detector time course at R&H's default σ=1e-6 (bias = +42.94%)
  and a σ sweep showing the operating-regime dependence. **This is the
  file that closes the loop between the published R&H model and our SB
  predictions.** The files below were earlier hand-rolled attempts and
  are superseded.

### R&H normalization layer — earlier hand-rolled attempts (superseded)
- `drive_figure.py` — population stimulus drive `E(θ, t)` via von Mises
  tuning over three input channels. Computes the heatmap shown in
  R&H-style cascades. Also exports `stimulus_drive_field()` for reuse.
  PNG: `drive_figure.png`.
- `rh_figure.py` — adds the attention field `A(θ)`, suppressive pool
  `S(t)`, and normalized output `R = (E·A)/(S+σ)` on top of the drive,
  with a fixed rightward (originally) / Down (after the direction remap)
  attention bias replacing the SB adaptation mechanism. PNG: `rh_figure.png`.
- `cascade_figure.py` — Heeger & Reynolds Fig 1 idiom: cascade layers as
  2D heatmaps for both CUED and UNCUED on two pages (no-swap and swap).
  PNGs: `rh_cascade_noswap.png`, `rh_cascade_swap.png`.
- `rh_fig1_style.py` — single-page R&H Fig 1 layout (plus-sign
  arrangement) with the dynamic stimulus input, attention field, stimulus
  drive, suppressive drive, output, and cascade equations all on one
  page. Two pages: CUED and UNCUED. PNGs: `rh_fig1_style_cued.png`,
  `rh_fig1_style_uncued.png`.
- `translation_response_figure.py` — translation-detector response
  `R(θ=θ_trans, t)` over the full trial duration, comparing CUED vs UNCUED.
  With the fixed attention bias on the cued/CCW direction, the R&H
  normalization layer predicts a **+37.3 %** cued vs uncued bias at the
  peak — entirely through the suppressive pool being asymmetric. PNG:
  `translation_response.png`.

## Methods note (2026-06-11) — translation input is adapted

Per S&B Appendix A: *"These adapting responses constitute the inputs
(i.e. the Cs in Eqs. 1 and 2) to a translation detector modeled by
Eq. 3."* All three Cs — both rotations **and the translation** — are
Eq. 4–5 adapting responses; the detector (Eq. 3) is static and pools
them. The original code adapted only the rotations and fed the
translation input in as a **raw binary box**, which made R_TD snap
on/ramp/drop vertically (unrealistic) and inflated the bias to +54.7 %.
Fix: route the translation input through `simulate_adapting_channel`
too, so `E = W_TRANS · R_trans`. This yields the realistic rise→peak→
decay transient and **+32.9 %** no-swap bias (closer to the paper's
~21 %). Applied in `web_figures.py`, `run_fig3.py`, and `run_fig6.py`.
Peak is now measured over the full transient (window + 120 ms), since
R_TD peaks near translation offset.

## Direction conventions (current)

After the user's "rotations on the Up/Down axis, translation centred"
remapping (2026-06-10):

| Channel | Local motion direction | y-axis angle |
|---|---|---|
| CW rotation (first-on field) | Up    | +90° |
| CCW rotation (delayed field) | Down  | −90° |
| Translation (brief)          | Right |   0° |
| Attention bias               | Down  | −90° (= CCW = cued/delayed direction) |

The y-axis ranges from −180° to +180° so that 0° (Right, the translation
direction) sits at the y-axis centre and doesn't get split at the wraparound.
"Left" wraps at the top/bottom edges; that's the uncued direction so the
split is less critical visually.

The original convention (before the remap) was CW→Left, CCW→Right,
translation→Up. The remap is purely visualization — it does not change
any model behaviour or quantitative predictions.

## Python and run notes

All scripts use Apple's `/usr/bin/python3` (3.9.6) with the analysis
packages installed at the user-site path. See the `laptop-setup` memory
for the alias setup. Run each script from this directory:

```
cd ~/Projects/ObjectBasedAttention/VRDots/Agents/Modeling/sb2010
/usr/bin/python3 run_fig3.py
/usr/bin/python3 run_fig6.py
/usr/bin/python3 rh_fig1_style.py
/usr/bin/python3 translation_response_figure.py
# ...etc
```

## Reference code (Heeger & Reynolds 2009 MATLAB)

`../reference_code/attentionModel/` contains the authors' published
MATLAB implementation, downloaded 2026-06-10 from
<https://www.cns.nyu.edu/heegerlab/?page=software&id=attentionModel>
(mirrored from <https://snl.salk.edu/~reynolds/Normalization_Model_of_Attention>).

Contents include `attentionModel.m` (the main function), helper
functions (`conv2sepYcirc.m`, `rconv2.m`, `makeGaussian.m`, `upConv.*`
from Simoncelli's `matlabPyrTools`), and `Figure2A.m` through
`Figure7C.m` — one script per published figure, driven by
`createFigures.m`.

The included `upConv` MEX binaries are 2009-era Intel/PPC builds and
will not load on Apple Silicon. When we actually run their code, we
must either recompile `upConv.c` or rely on the pure-MATLAB
fallback `upConv.m`.

This is the ground-truth code we will diff against (in structure and
in numerical predictions) once we set up the verification pipeline.

## Open threads

1. **Verification against R&H Fig 1 / Fig 4 published cases.** Pick one
   of R&H's canonical attention regimes (small attention field with
   small stim → response gain; large with large → contrast gain; etc.)
   and confirm our normalization machinery reproduces the predicted
   bias pattern parameter-for-parameter. Plan: run their `Figure4C.m`
   (and others) in MATLAB on the laptop, then build the equivalent
   case in our Python machinery and compare numerically. This is the
   next planned step.
2. **Adaptation-only vs fixed-attention-only**, side by side. These are
   competing accounts of the cueing advantage, not complementary
   mechanisms — we don't stack them.  The SB 2010 model uses adaptation
   alone (no attentional modulation).  Our current R&H layer uses a
   fixed attention bias alone (no adaptation).  Compare them head-to-head
   against the same target data, and consider whether either, neither,
   or both reproduce key behavioural patterns. The Stoner 2018 SFN
   "point-set" feedback model is yet a third alternative to evaluate
   alongside.
3. **Residual bias gap (33 % vs ~21 %).** After the 2026-06-11 fix
   (translation input adapted; see Methods note), the no-swap bias is
   **+32.9 %** vs the paper's ~21 %. The earlier +54.7 % and its
   "peak-vs-mean" explanation were an artifact of feeding the translation
   input in raw. Remaining gap may be the exact peak metric, σ, or timing.
4. **Connect to VRDots empirical data.** Once the model side is solid,
   use it as a falsification target / prior for the experimental
   cued/uncued biases recorded in `Agents/SwapPilot/`.
