"""
Population 'stimulus drive' à la Reynolds & Heeger (2009), but with the
RF-center axis replaced by time.

We pass the three binary stimulus inputs (left = CW rotation, right = CCW
rotation, up = translation) through a population of direction-selective
neurons spanning the preferred-direction circle, and plot the resulting
drive as a heatmap with y = preferred direction and x = time.

Conventions
-----------
Direction angle in degrees, vision convention:
    0°    = right
    90°   = up
    180°  = left
    270°  = down

Stimulus → motion direction mapping:
    Left   stimulus channel  (CW rotation)   → motion at 180°
    Right  stimulus channel  (CCW rotation)  → motion at   0°
    Up     stimulus channel  (translation)   → motion at  90°

Tuning curve: von Mises (circular Gaussian).
    f(θ_pref, θ_stim) = exp( κ · cos(θ_stim − θ_pref) )

We pick κ = 2 by default → FWHM ≈ 98°, broad but in the ballpark of
direction-selective MT neurons.  Easy to tighten if desired.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from parameters import T_END, T_TRANS_START, T_TRANS_END
from stimulus import channels_for_trial


# Stimulus → motion direction map (degrees, vision convention with
# 0° = right, 90° = up, ±180° = left, −90° = down).
#
# Each of the three input channels is idealized as a single local motion
# direction in an RF positioned so that:
#   - the two opposite rotation directions become "Up" and "Down"
#   - the brief translation runs to the "Right" (placed at the y-axis
#     centre so it doesn't get split at the wraparound edges)
DIR_CW    =  90.0   # CW rotation channel  → Up
DIR_CCW   = -90.0   # CCW rotation channel → Down
DIR_TRANS =   0.0   # translation channel  → Right (centred on the y-axis)

# Back-compat aliases for code that hasn't been updated yet.
DIR_LEFT  = DIR_CW
DIR_RIGHT = DIR_CCW
DIR_UP    = DIR_TRANS

# Tuning concentration (von Mises κ).  κ=2 → FWHM ≈ 98°.
KAPPA = 2.0


def tuning(theta_pref_deg, theta_stim_deg, kappa=KAPPA):
    """von Mises tuning weight at preferred direction θ_pref for a stimulus
    moving in direction θ_stim.  Both in degrees, scalars or arrays.

    Peak value = exp(κ); minimum value (antipreferred) = exp(−κ).
    """
    diff = np.radians(np.asarray(theta_stim_deg) - np.asarray(theta_pref_deg))
    return np.exp(kappa * np.cos(diff))


def stimulus_drive_field(theta_prefs_deg, t, condition, motion_swap=False,
                         kappa=KAPPA):
    """Drive on a grid of (preferred direction × time).

    Returns
    -------
    drive : array of shape (len(theta_prefs_deg), len(t))
    """
    stim_cw, stim_ccw, c_trans = channels_for_trial(condition, motion_swap)
    S_cw    = stim_cw(t)
    S_ccw   = stim_ccw(t)
    S_trans = c_trans(t)

    w_cw    = tuning(theta_prefs_deg, DIR_CW,    kappa)[:, None]
    w_ccw   = tuning(theta_prefs_deg, DIR_CCW,   kappa)[:, None]
    w_trans = tuning(theta_prefs_deg, DIR_TRANS, kappa)[:, None]

    return (w_cw    * S_cw[None, :]
            + w_ccw   * S_ccw[None, :]
            + w_trans * S_trans[None, :])


# S&B (2010) Fig. 4 layout (top two rows, A-D), with the swap column's rows
# flipped relative to the no-swap column: the motion swap turns a cued
# (delayed-dots) translation into the functional uncued case, so the
# cued-swap panel sits at D (bottom) and the uncued-swap panel at B (top).
#   (row, col, letter, condition, motion_swap)
PANELS = [
    (0, 0, "A", "cued",   False),
    (0, 1, "B", "uncued", True),
    (1, 0, "C", "uncued", False),
    (1, 1, "D", "cued",   True),
]
COL_TITLES = ["No-motion-swap", "Motion-swap"]


def main():
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    theta_prefs = np.arange(0.0, 360.0, 1.0)   # 1° resolution → 360 neurons

    panels = []
    for row, col, letter, condition, swap in PANELS:
        d = stimulus_drive_field(theta_prefs, t, condition, swap)
        panels.append((row, col, letter, d))

    vmax = max(d.max() for *_, d in panels)
    vmin = 0.0

    fig, axes = plt.subplots(
        2, 2,
        figsize=(13, 9),
        sharex=True, sharey=True,
        gridspec_kw=dict(hspace=0.18, wspace=0.10),
    )

    for row, col, letter, d in panels:
        ax = axes[row, col]
        im = ax.imshow(
            d,
            extent=[t[0], t[-1], theta_prefs[0], theta_prefs[-1]],
            origin='lower',
            aspect='auto',
            cmap='gray_r',
            vmin=vmin, vmax=vmax,
        )
        ax.axvline(T_TRANS_START, color='white', lw=0.6, alpha=0.6)
        ax.axvline(T_TRANS_END,   color='white', lw=0.6, alpha=0.6)
        ax.set_yticks([0, 90, 180, 270, 360])
        ax.set_yticklabels(['Right\n(0°)', 'Up\n(90°)', 'Left\n(180°)',
                            'Down\n(270°)', '360°'])
        # Light reference lines at the stimulus directions
        for y in (0, 90, 180):
            ax.axhline(y, color='white', lw=0.4, alpha=0.35)
        # Panel letter, top-left, on a small white tag so it reads over the map
        ax.text(0.02, 0.96, letter, transform=ax.transAxes,
                fontsize=15, fontweight='bold', color='black',
                va='top', ha='left',
                bbox=dict(boxstyle='round,pad=0.22', facecolor='white',
                          edgecolor='none', alpha=0.85))
        # Column header on the top row only
        if row == 0:
            ax.set_title(COL_TITLES[col], fontsize=13, fontweight='bold',
                         pad=10)

    for ax in axes[1, :]:
        ax.set_xlabel('Time (ms)', fontsize=11)
    for ax in axes[:, 0]:
        ax.set_ylabel('Preferred direction', fontsize=11)

    fig.colorbar(
        im, ax=axes, shrink=0.85, pad=0.02,
        label='Stimulus drive  (dim.less)',
    )

    out = 'drive_figure.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    print(f"Saved {out}")


if __name__ == '__main__':
    main()
