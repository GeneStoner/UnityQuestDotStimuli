"""
Layered Reynolds & Heeger (2009) computation on top of the
direction-tuned 'stimulus drive' from drive_figure.py.

Architecture, per preferred direction θ and time t:

    E(θ, t)   stimulus drive               — 3 binary inputs through von Mises
                                             tuning (already in drive_figure)
    A(θ)      attention field              — constant in time, fixed advantage
                                             at rightward (0°).  This stands in
                                             for the SB 2010 adaptation-based
                                             cueing advantage (we may
                                             reintroduce adaptation later).
    S(t)      suppressive drive            — pool of E·A over ALL preferred
                                             directions, one value per time
    R(θ, t)   normalized output            — (E · A) / (S + σ)

Time window: from delayed onset (t = 750 ms) onward, since the fixed
attention field is replacing the SB pre-trial adaptation build-up.

Run with:
    /usr/bin/python3 rh_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END
from drive_figure import stimulus_drive_field


# ---------- Attention field ----------------------------------------------

ATTN_PEAK     = 2.0    # multiplicative gain at the attended direction
ATTN_BASELINE = 1.0    # gain far away from the attended direction
ATTN_DIR_DEG  = -90.0  # attended direction (Down = CCW rotation = the
                       # cued / delayed field's local motion)
ATTN_KAPPA    = 2.0    # von Mises concentration of the attention field

# ---------- Normalization ------------------------------------------------

SIGMA_NORM = 1.0       # semisaturation in the divisive normalization


def attention_field(theta_prefs_deg,
                    peak=ATTN_PEAK, baseline=ATTN_BASELINE,
                    attn_dir=ATTN_DIR_DEG, kappa=ATTN_KAPPA):
    """von Mises bump in [baseline, peak]: A(attn_dir) = peak; A → baseline far away."""
    diff_rad = np.radians(theta_prefs_deg - attn_dir)
    raw = np.exp(kappa * np.cos(diff_rad))
    norm = (raw - np.exp(-kappa)) / (np.exp(kappa) - np.exp(-kappa))
    return baseline + (peak - baseline) * norm


CONDITIONS = [
    ("CUED, no swap",   'cued',   False),
    ("UNCUED, no swap", 'uncued', False),
    ("CUED, swap",      'cued',   True),
    ("UNCUED, swap",    'uncued', True),
]


def main():
    # --- time grid: start at delayed onset --------------------------------
    dt = 1.0
    t_full = np.arange(0.0, T_END + dt, dt)
    mask = t_full >= T_FIELD2_ON
    t = t_full[mask]
    theta_prefs = np.arange(0.0, 360.0, 1.0)

    # --- attention field (single curve, same for all conditions) ----------
    A_vec = attention_field(theta_prefs)
    A_col = A_vec[:, None]

    # --- per-condition layers ---------------------------------------------
    layers = []
    for label, cond, swap in CONDITIONS:
        E_full = stimulus_drive_field(theta_prefs, t_full, cond, swap)
        E = E_full[:, mask]
        EA = E * A_col
        # Suppressive drive: pool over all preferred directions (mean)
        S = EA.mean(axis=0)
        R = EA / (S[None, :] + SIGMA_NORM)
        layers.append(dict(label=label, E=E, EA=EA, S=S, R=R))

    # --- shared color scales for cross-condition comparability ------------
    E_vmax = max(layer['E'].max() for layer in layers)
    R_vmax = max(layer['R'].max() for layer in layers)

    # --- figure scaffolding ----------------------------------------------
    fig = plt.figure(figsize=(13.5, 12.0))
    gs = fig.add_gridspec(
        4, 4,
        height_ratios=[0.85, 1.5, 1.5, 1.25],
        hspace=0.42, wspace=0.16,
        left=0.07, right=0.96, top=0.93, bottom=0.06,
    )

    # ------ Row 1: attention field A(θ)  (single panel, full width) ------
    ax = fig.add_subplot(gs[0, :])
    ax.plot(theta_prefs, A_vec, color='black', lw=2)
    ax.axhline(ATTN_BASELINE, color='gray', lw=0.6, linestyle='--')
    ax.set_xticks([0, 90, 180, 270, 360])
    ax.set_xticklabels(['Right (0°)', 'Up (90°)', 'Left (180°)',
                        'Down (270°)', '360°'])
    ax.set_xlabel('Preferred direction')
    ax.set_ylabel('Attention gain  A(θ)')
    ax.set_xlim(0, 360)
    ax.set_ylim(ATTN_BASELINE - 0.2, ATTN_PEAK + 0.2)
    ax.set_title(
        'A.  Attention field — constant rightward advantage  '
        f'(peak={ATTN_PEAK:.1f}, baseline={ATTN_BASELINE:.1f}, κ={ATTN_KAPPA:.1f})',
        loc='left', fontsize=11.5, fontweight='bold',
    )

    # Helper for the imshow rows
    def show_heatmap(ax, mat, vmax, ylabel_text, show_xlabel):
        im = ax.imshow(
            mat,
            extent=[t[0], t[-1], theta_prefs[0], theta_prefs[-1]],
            origin='lower', aspect='auto',
            cmap='gray_r', vmin=0, vmax=vmax,
        )
        ax.axvline(T_TRANS_START, color='#C0392B', lw=0.6, alpha=0.85)
        ax.axvline(T_TRANS_END,   color='#C0392B', lw=0.6, alpha=0.85)
        if ylabel_text:
            ax.set_ylabel(ylabel_text, fontsize=10.5)
            ax.set_yticks([0, 90, 180, 270, 360])
            ax.set_yticklabels(['R', 'U', 'L', 'D', '360°'])
        else:
            ax.set_yticks([])
        if show_xlabel:
            ax.set_xlabel('Time (ms)', fontsize=10.5)
        ax.tick_params(labelsize=8)
        return im

    # ------ Row 2: stimulus drive E(θ, t) -------------------------------
    for col, layer in enumerate(layers):
        ax = fig.add_subplot(gs[1, col])
        im = show_heatmap(
            ax, layer['E'], E_vmax,
            ylabel_text='Pref. dir.\n(stimulus drive E)' if col == 0 else None,
            show_xlabel=False,
        )
        ax.set_title(layer['label'], fontsize=10.5, fontweight='bold')
    # Colorbar for E row
    cbar_ax = fig.add_axes([0.965, 0.51, 0.012, 0.18])
    fig.colorbar(im, cax=cbar_ax).set_label('E', fontsize=9)

    # ------ Row 3: output R(θ, t) = (E·A) / (S + σ) ----------------------
    for col, layer in enumerate(layers):
        ax = fig.add_subplot(gs[2, col])
        im = show_heatmap(
            ax, layer['R'], R_vmax,
            ylabel_text='Pref. dir.\n(output R)' if col == 0 else None,
            show_xlabel=False,
        )
    # Colorbar for R row
    cbar_ax = fig.add_axes([0.965, 0.27, 0.012, 0.18])
    fig.colorbar(im, cax=cbar_ax).set_label('R', fontsize=9)

    # ------ Row 4: suppressive drive S(t) — one panel, all conditions --
    ax_S = fig.add_subplot(gs[3, :])
    gray_levels = ['#222222', '#666666', '#222222', '#666666']
    line_styles  = ['-',       '-',       '--',       '--']
    for layer, color, ls in zip(layers, gray_levels, line_styles):
        ax_S.plot(t, layer['S'], color=color, ls=ls, lw=1.6,
                  label=layer['label'])
    ax_S.axvspan(T_TRANS_START, T_TRANS_END, color='#C0392B',
                 alpha=0.12, zorder=0)
    ax_S.set_xlim(t[0], t[-1])
    ax_S.set_xlabel('Time (ms)', fontsize=10.5)
    ax_S.set_ylabel('Suppressive drive  S(t)')
    ax_S.set_title(
        'B.  Suppressive drive — mean of (E · A) over all preferred directions',
        loc='left', fontsize=11.5, fontweight='bold',
    )
    ax_S.legend(fontsize=9, loc='upper right', ncol=2)

    fig.suptitle(
        "Reynolds–Heeger normalization layer (fixed rightward attention) — "
        "stimulus drive, attention field, suppressive pool, normalized output\n"
        "Shown from delayed onset (t = 750 ms) onward.  The constant attention "
        "field is standing in for the SB 2010 adaptation-based cueing advantage.",
        fontsize=12.5, fontweight='bold', y=0.995,
    )

    out = 'rh_figure.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    print(f"Saved {out}")


if __name__ == '__main__':
    main()
