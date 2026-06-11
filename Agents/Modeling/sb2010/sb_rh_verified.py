"""
Apply the verified R&H math to our SB time-domain case.

Strategy
--------
Substitute time for the spatial RF-center axis (x → t) and feed the
SB binary stimulus into the verified port of attentionModel.m
(Agents/Modeling/verification/port_attention_model.py).

What this verifies
------------------
Our hand-rolled R&H layer in rh_figure.py uses von Mises tuning,
mean-over-θ for the suppressive pool, and no spatial-axis machinery.
The published R&H model uses Gaussian tuning kernels and convolutional
suppressive pooling along both axes. This script applies the *published*
math to the SB case, with kernels and attention parameters chosen to
match (qualitatively) our hand-rolled choices:

    EthetaWidth = 42°    (Gaussian σ; FWHM matches von Mises κ=2)
    ExWidth     = 0.5 ms (essentially instantaneous; no temporal blur)
    IthetaWidth = 360°   (uniform pool over all directions — same as
                          our "mean over θ" choice)
    IxWidth     = 0.5 ms (essentially instantaneous suppression)
    AthetaWidth = 42°
    Atheta      = −90°   (Down = CCW = cued/delayed direction)
    Apeak/Abase = 2 / 1  (same as our hand-rolled attention bump)
    sigma       = 1.0    (same as SIGMA_NORM in rh_figure.py)

If the verified-math prediction matches our hand-rolled +37.3% cued
bias, our SB R&H implementation has been faithful to the published
model up to the kernel-shape choice (Gaussian vs von Mises) and the
normalization-pool implementation (convolution vs simple mean).

Run with:
    /usr/bin/python3 sb_rh_verified.py
"""

import os
import sys
import numpy as np

# Make the verified port importable.
HERE  = os.path.dirname(os.path.abspath(__file__))
VERIF = os.path.normpath(os.path.join(HERE, '..', 'verification'))
sys.path.insert(0, VERIF)
from port_attention_model import attention_model  # noqa: E402

from parameters import (
    T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END,
)
from stimulus import channels_for_trial
from drive_figure import DIR_CW, DIR_CCW, DIR_TRANS


# --- direction axis (matches rh_figure.py) ---------------------------------
THETA_PREFS = np.arange(-180.0, 180.0, 1.0)
N_THETA     = len(THETA_PREFS)


# --- R&H kernel widths -----------------------------------------------------
ETHETA_WIDTH = 42.0    # Gaussian σ in θ (deg) — FWHM matches von Mises κ=2
ET_WIDTH     = 0.5     # Gaussian σ in t (ms) — essentially impulse
ITHETA_WIDTH = 360.0   # uniform direction pool
IT_WIDTH     = 0.5     # essentially instantaneous suppression


# --- attention field -------------------------------------------------------
ATHETA_WIDTH = 42.0    # same width as orientation tuning
ATTN_DIR_DEG = -90.0   # Down = CCW = cued/delayed direction
APEAK        = 2.0
ABASE        = 1.0

# --- normalization ---------------------------------------------------------
SIGMA_NORM = 1.0


def build_sb_stimulus(t, condition, motion_swap):
    """Build (N_theta, N_t) stimulus matrix.

    Non-zero only at the three SB channel directions (delta-like in θ).
    """
    stim_cw_fn, stim_ccw_fn, c_trans_fn = channels_for_trial(condition,
                                                              motion_swap)
    S_cw    = stim_cw_fn(t)
    S_ccw   = stim_ccw_fn(t)
    S_trans = c_trans_fn(t)

    stimulus = np.zeros((N_THETA, len(t)))
    idx_cw    = int(np.argmin(np.abs(THETA_PREFS - DIR_CW)))
    idx_ccw   = int(np.argmin(np.abs(THETA_PREFS - DIR_CCW)))
    idx_trans = int(np.argmin(np.abs(THETA_PREFS - DIR_TRANS)))
    stimulus[idx_cw,    :] = S_cw
    stimulus[idx_ccw,   :] = S_ccw
    stimulus[idx_trans, :] = S_trans
    return stimulus


def run_sb_rh(condition, motion_swap, t):
    """Compute R(θ, t) for one SB trial type using the verified R&H math.

    We pass a centred ``x`` coordinate to attention_model so the Gaussian
    temporal kernel sits in the middle of its array (this is the
    convention attentionModel.m and upConv assume).
    """
    stim = build_sb_stimulus(t, condition, motion_swap)
    N_t = len(t)
    # Centre 0 at the middle of the array so the temporal kernel is
    # properly centred (mimics how Figure4C.m uses x = -200:200).
    x_centred = np.arange(N_t, dtype=float) - N_t // 2

    R = attention_model(
        x_centred, THETA_PREFS, stim,
        ExWidth=ET_WIDTH, EthetaWidth=ETHETA_WIDTH,
        IxWidth=IT_WIDTH, IthetaWidth=ITHETA_WIDTH,
        Ax=np.nan, Atheta=ATTN_DIR_DEG,
        AxWidth=ET_WIDTH, AthetaWidth=ATHETA_WIDTH,
        Apeak=APEAK, Abase=ABASE,
        sigma=SIGMA_NORM,
    )
    return R


def translation_peak(R, t):
    """Peak R at the translation direction (θ = DIR_TRANS = 0°) during the
    40 ms translation window."""
    idx_trans = int(np.argmin(np.abs(THETA_PREFS - DIR_TRANS)))
    mask = (t >= T_TRANS_START) & (t < T_TRANS_END)
    return float(R[idx_trans, mask].max())


def run_sb_rh_with_sigma(condition, motion_swap, t, sigma):
    """Variant of run_sb_rh that lets us sweep sigma without globals."""
    stim = build_sb_stimulus(t, condition, motion_swap)
    N_t = len(t)
    x_centred = np.arange(N_t, dtype=float) - N_t // 2
    R = attention_model(
        x_centred, THETA_PREFS, stim,
        ExWidth=ET_WIDTH, EthetaWidth=ETHETA_WIDTH,
        IxWidth=IT_WIDTH, IthetaWidth=ITHETA_WIDTH,
        Ax=np.nan, Atheta=ATTN_DIR_DEG,
        AxWidth=ET_WIDTH, AthetaWidth=ATHETA_WIDTH,
        Apeak=APEAK, Abase=ABASE,
        sigma=sigma,
    )
    return R


def make_figure(t, sweep_data, sigma_for_timecourse):
    """Render the headline figure: translation-detector time course at one
    σ (deep in R&H's normalization-driven regime) plus a σ sweep curve."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    idx_trans = int(np.argmin(np.abs(THETA_PREFS - DIR_TRANS)))

    R_c = run_sb_rh_with_sigma('cued',   False, t, sigma_for_timecourse)
    R_u = run_sb_rh_with_sigma('uncued', False, t, sigma_for_timecourse)
    R_c_t = R_c[idx_trans, :]
    R_u_t = R_u[idx_trans, :]
    in_trans = (t >= T_TRANS_START) & (t < T_TRANS_END)
    pc = float(R_c_t[in_trans].max())
    pu = float(R_u_t[in_trans].max())
    bias = (pc / pu - 1.0) * 100.0

    fig, axes = plt.subplots(2, 1, figsize=(11.5, 9.0))

    # --- Top: R(θ=0°, t) for cued vs uncued at chosen σ -------------------
    ax = axes[0]
    ax.plot(t, R_c_t, color='#2E8B57', lw=2.0,
            label=f'CUED   (peak = {pc:.2f})')
    ax.plot(t, R_u_t, color='#C0392B', lw=2.0, linestyle='--',
            label=f'UNCUED (peak = {pu:.2f})')
    ax.axvspan(T_TRANS_START, T_TRANS_END, color='gray', alpha=0.18,
               zorder=0)
    ax.axvline(T_FIELD2_ON, color='black', lw=0.6, alpha=0.55)
    ymax_for_text = max(R_c_t.max(), R_u_t.max())
    ax.text(T_FIELD2_ON + 12, ymax_for_text * 0.92,
            'delayed onset', fontsize=9, color='#555', va='top')
    ax.text((T_TRANS_START + T_TRANS_END) / 2, ymax_for_text * 0.04,
            '40 ms translation', fontsize=9, color='#555',
            ha='center', va='bottom')
    ax.set_xlim(0, t[-1])
    ax.set_xlabel('Time (ms)', fontsize=11)
    ax.set_ylabel(r'$R(\theta=0°, t)$    (translation detector)',
                  fontsize=11)
    ax.set_title(
        f'A.  Translation-detector response — verified R&H math on SB stimulus  '
        f'(σ = {sigma_for_timecourse:.0e},  bias = {bias:+.2f}%)',
        loc='left', fontsize=11.5, fontweight='bold',
    )
    ax.legend(fontsize=10, loc='upper left')

    # --- Bottom: σ sweep ---------------------------------------------------
    ax = axes[1]
    sigma_arr = np.array([row[0] for row in sweep_data])
    bias_arr  = np.array([row[3] for row in sweep_data])
    ax.semilogx(sigma_arr, bias_arr, 'o-', color='black', lw=1.7,
                markersize=8, zorder=3, label='verified R&H math on SB')
    ax.axhline(37.31, color='#1F77B4', linestyle='--', linewidth=1.4,
               label='hand-rolled rh_figure.py: +37.31%')
    ax.axhline(bias_arr[-1], color='#7B7B7B', linestyle=':',
               linewidth=1.2,
               label=f'verified asymptote: {bias_arr[-1]:+.2f}%')
    ax.set_xlabel(r'Normalization semisaturation  $\sigma$', fontsize=11)
    ax.set_ylabel(r'Cued bias  $(R_{\rm cued} / R_{\rm uncued} - 1) \times 100\%$',
                  fontsize=11)
    ax.set_title(
        'B.  σ sweep — bias rises with smaller σ, matching the hand-rolled '
        'prediction near σ ≈ 0.01 and asymptoting deep in the normalization-driven regime',
        loc='left', fontsize=11.5, fontweight='bold',
    )
    ax.legend(fontsize=9.5, loc='lower left')
    ax.grid(True, alpha=0.3, which='both')

    fig.tight_layout()
    out = 'sb_rh_verified.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    print(f'\nSaved figure to {out}')


def main():
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    print(f'time grid: {len(t)} points at dt={dt} ms\n')

    print('Parameters:')
    print(f'  EthetaWidth = {ETHETA_WIDTH}° (Gaussian σ; ~FWHM of von Mises κ=2)')
    print(f'  ExWidth     = {ET_WIDTH} ms (instantaneous)')
    print(f'  IthetaWidth = {ITHETA_WIDTH}° (uniform pool over θ)')
    print(f'  IxWidth     = {IT_WIDTH} ms (instantaneous suppression)')
    print(f'  AthetaWidth = {ATHETA_WIDTH}°,   Atheta = {ATTN_DIR_DEG}°')
    print(f'  Apeak/Abase = {APEAK}/{ABASE}\n')

    # σ sweep — operating-regime control.
    sigmas = [1.0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-6]
    sweep = []
    print(f'{"sigma":>10s}  {"peak R cued":>14s}  '
          f'{"peak R uncued":>14s}  {"bias %":>10s}')
    print('-' * 60)
    for sigma in sigmas:
        R_c = run_sb_rh_with_sigma('cued',   False, t, sigma)
        R_u = run_sb_rh_with_sigma('uncued', False, t, sigma)
        pc = translation_peak(R_c, t)
        pu = translation_peak(R_u, t)
        bias = (pc / pu - 1.0) * 100.0
        sweep.append((sigma, pc, pu, bias))
        print(f'{sigma:10.0e}  {pc:14.4f}  {pu:14.4f}  {bias:+9.2f}%')

    print()
    print('Hand-rolled rh_figure.py reports +37.31% (von Mises tuning, mean-θ pool, σ=1).')

    # Headline figure: time course at R&H's published default σ=1e-6
    # plus the full σ sweep.
    make_figure(t, sweep, sigma_for_timecourse=1e-6)


if __name__ == '__main__':
    main()
