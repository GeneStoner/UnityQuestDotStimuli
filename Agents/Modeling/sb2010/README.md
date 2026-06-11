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
  cued > uncued bias of **+54.7 %** (paper reports ~21 % using a different
  summary metric; qualitative result matches). PNG: `fig3_reproduction.png`.
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

### R&H normalization layer (no adaptation)
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

## Open threads

1. **Verification against R&H Fig 1 / Fig 4 published cases.** Pick one
   of R&H's canonical attention regimes (small attention field with
   small stim → response gain; large with large → contrast gain; etc.)
   and confirm our normalization machinery reproduces the predicted
   bias pattern parameter-for-parameter. This is the next planned step.
2. **Add adaptation back in** alongside the fixed attention field, and
   see how the two mechanisms combine.
3. **Compare metrics.** The current bias (+54.7 % in SB Fig 3 reproduction,
   vs paper's ~21 %) likely reflects "peak of R_TD" vs the paper's
   different summary (mean or integral over the translation window).
   Confirm which.
4. **Connect to VRDots empirical data.** Once the model side is solid,
   use it as a falsification target / prior for the experimental
   cued/uncued biases recorded in `Agents/SwapPilot/`.
