"""
Translation-detector response over the full trial duration — CUED vs UNCUED.

The "translation detector" here is the model neuron whose preferred
direction matches the upward translation:  θ_pref = 90°.

Its response is the divisively-normalized R&H output:

    R(θ=90°, t) = E(90°, t) · A(90°) / ( S(t) + σ )

The figure plots R(90°, t) over t ∈ [0, T_END] for the CUED and UNCUED
conditions (no motion swap), with the 750-ms delayed-onset marker and
the 40-ms translation window highlighted.

The key insight: with a *constant* attention bias at Right (0°), the
two rotation channels' inputs are mirror-symmetric across the attended
direction.  Cued and uncued differ only in which mirror-symmetric
configuration is present during translation.  The numerator E·A at
θ=90° is therefore the same in both conditions — but the suppressive
drive S(t) differs because the attention field is asymmetric.

Run with:
    /usr/bin/python3 translation_response_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END
from rh_fig1_style import compute_cascade_centered, THETA_PREFS_DEG
from drive_figure import DIR_TRANS


def main():
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    # Translation detector: model neuron whose preferred direction matches
    # the translation channel (currently 0° = Right after the direction
    # remapping that puts CW/CCW rotations on the Up/Down axis).
    idx_trans = int(np.argmin(np.abs(THETA_PREFS_DEG - DIR_TRANS)))

    # Run cascade for both conditions, no motion swap
    results = {}
    for cond in ('cued', 'uncued'):
        layers = compute_cascade_centered(t, cond, motion_swap=False)
        results[cond] = {
            'R_up': layers['R'][idx_trans, :],
            'S':    layers['S'][0, :],   # S is constant in θ; row 0 = the full S(t)
        }

    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.0], hspace=0.35,
                          left=0.09, right=0.97, top=0.93, bottom=0.08)

    # --- Top panel: translation-detector response over full duration -----
    ax = fig.add_subplot(gs[0])
    ax.plot(t, results['cued']  ['R_up'], color='#2E8B57', lw=2.0,
            label='CUED   (delayed/cued field translates)')
    ax.plot(t, results['uncued']['R_up'], color='#C0392B', lw=2.0,
            linestyle='--',
            label='UNCUED (first-on/uncued field translates)')
    ax.axvspan(T_TRANS_START, T_TRANS_END, color='gray', alpha=0.18,
               zorder=0)
    ax.axvline(T_FIELD2_ON, color='black', lw=0.8, alpha=0.6)
    ymin, ymax = ax.get_ylim()
    ax.text(T_FIELD2_ON + 8, ymax * 0.9, 'delayed onset (Field 2 appears)',
            fontsize=9, color='#555', va='top')
    ax.text((T_TRANS_START + T_TRANS_END) / 2, ymax * 0.05,
            '40 ms translation', fontsize=9, color='#555',
            ha='center', va='bottom')
    ax.set_xlim(0, t[-1])
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel(r'$R(\theta = 0°, t)$    (translation-detector response)')
    ax.set_title('A.  Translation-detector response over the full trial duration',
                 loc='left', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')

    # --- Bottom panel: zoomed view around the translation window ---------
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(t, results['cued']  ['R_up'], color='#2E8B57', lw=2.0,
             label='CUED')
    ax2.plot(t, results['uncued']['R_up'], color='#C0392B', lw=2.0,
             linestyle='--', label='UNCUED')
    ax2.axvspan(T_TRANS_START, T_TRANS_END, color='gray', alpha=0.18)
    ax2.set_xlim(T_TRANS_START - 60, T_TRANS_END + 100)
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel(r'$R(\theta = 0°, t)$')
    ax2.set_title('B.  Zoom on the 40-ms translation window',
                  loc='left', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10, loc='upper right')

    # Annotate peak values
    peak_cued = float(results['cued']['R_up'].max())
    peak_uncued = float(results['uncued']['R_up'].max())
    diff_pct = (peak_cued / peak_uncued - 1.0) * 100.0
    fig.text(0.5, 0.005,
             f'Peak R(0°): CUED = {peak_cued:.3f},  '
             f'UNCUED = {peak_uncued:.3f}     '
             f'(cued / uncued − 1) = {diff_pct:+.2f}%',
             ha='center', va='bottom', fontsize=10.5,
             color='#222', fontweight='bold')

    out = 'translation_response.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    print(f'Saved {out}')
    print(f"  Peak R(0°): cued={peak_cued:.4f}, uncued={peak_uncued:.4f}, "
          f"bias={diff_pct:+.2f}%")


if __name__ == '__main__':
    main()
