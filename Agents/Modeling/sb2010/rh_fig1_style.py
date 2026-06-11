"""
Single-figure rendering of the normalization-model cascade for the CUED
condition, modeled after Reynolds & Heeger (2009) Figure 1.

R&H Fig 1 layout (per the legend):
    Left:    Stimulus cartoon (the visual scene with RF location)
    Middle:  Stimulus drive  E   (the central panel)
    Top:     Attention field A
    Bottom:  Suppressive drive S
    Right:   Output R = (E·A) / (S + σ)

For our adaptation, we keep that "plus-sign" layout but substitute the
TIME axis for R&H's RF-center axis.  All four model layers are 2D
heatmaps over (preferred direction × time), drawn at the same size.

We also shift the preferred-direction axis to [-180°, 180°] so the
attended direction (Right = 0°) sits in the *middle* of the y-axis
rather than splitting at the edges.  Left (±180°) still wraps at the
top/bottom — that's the uncued/first-on direction.

Time window: from delayed onset (t = 750 ms) onward.

Run with:
    /usr/bin/python3 rh_fig1_style.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch

from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END
from drive_figure import (
    stimulus_drive_field, DIR_CW, DIR_CCW, DIR_TRANS, KAPPA,
)
from rh_figure import (
    attention_field, SIGMA_NORM,
    ATTN_PEAK, ATTN_BASELINE, ATTN_DIR_DEG, ATTN_KAPPA,
)
from stimulus import channels_for_trial


# ---------------------------------------------------------------------
# Direction axis: [-180°, 180°] with 0° (Right = attended) in the centre
# ---------------------------------------------------------------------

THETA_PREFS_DEG = np.arange(-180.0, 180.0, 1.0)


def compute_cascade_centered(t, condition, motion_swap):
    """Run the four R&H layers on the centred direction axis."""
    E = stimulus_drive_field(THETA_PREFS_DEG, t, condition, motion_swap)
    A_vec = attention_field(THETA_PREFS_DEG)
    A_2d = np.broadcast_to(A_vec[:, None], E.shape)
    EA = E * A_vec[:, None]
    S_1d = EA.mean(axis=0)
    S_2d = np.broadcast_to(S_1d[None, :], E.shape)
    R = EA / (S_1d[None, :] + SIGMA_NORM)
    return dict(E=E, A=A_2d, S=S_2d, R=R)


def draw_equations(ax):
    """Display the four cascade equations used to compute the responses.

    Notation matches Reynolds & Heeger (2009) but adapted to our setup:
      - θ           = preferred direction of a model neuron
      - t           = time
      - i ∈ {L, R, U} = stimulus directions (Left, Right, Up)
      - θ_i         = direction angle for input i (180°, 0°, 90°)
      - κ           = tuning concentration (von Mises)
      - σ           = normalization semisaturation
    """
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(0.0, 1.00, 'Cascade equations',
            fontsize=12, fontweight='bold',
            transform=ax.transAxes, va='top')

    # Each equation gets ~0.16-0.18 of vertical space (fractions take more).
    # Y coordinates are tops of each text block; mathtext fractions render
    # below their anchor so we keep generous gaps.

    # --- Stimulus drive ----------------------------------------------------
    ax.text(0.0, 0.89,
            r"$E(\theta, t) \,=\, \sum_{i \in \{L, R, U\}} S_i(t)\, w_i(\theta)$",
            fontsize=12, transform=ax.transAxes, va='top')
    ax.text(0.06, 0.78,
            r"$w_i(\theta) \,=\, e^{\,\kappa\, \cos(\theta_i - \theta)}$"
            f"     (κ = {KAPPA:.1f},  $\\theta_L$ = 180°, "
            f"$\\theta_R$ = 0°, $\\theta_U$ = 90°)",
            fontsize=10, color='#444',
            transform=ax.transAxes, va='top')

    # --- Attention field ---------------------------------------------------
    ax.text(0.0, 0.63,
            r"$A(\theta) \,=\, b \,+\, (a - b)\, "
            r"\tilde{w}_{A}(\theta - \theta_{\mathrm{attn}})$",
            fontsize=12, transform=ax.transAxes, va='top')
    ax.text(0.06, 0.52,
            f"a = {ATTN_PEAK:.1f},  b = {ATTN_BASELINE:.1f},  "
            f"$\\theta_{{\\mathrm{{attn}}}}$ = {ATTN_DIR_DEG:.0f}°,  "
            f"κ$_A$ = {ATTN_KAPPA:.1f}",
            fontsize=10, color='#444',
            transform=ax.transAxes, va='top')

    # --- Suppressive drive ------------------------------------------------
    ax.text(0.0, 0.37,
            r"$S(t) \,=\, \langle E(\theta, t)\, A(\theta) \rangle_\theta$",
            fontsize=12, transform=ax.transAxes, va='top')

    # --- Output -----------------------------------------------------------
    ax.text(0.0, 0.22,
            r"$R(\theta, t) \,=\, \dfrac{E(\theta, t)\, A(\theta)}"
            r"{S(t) + \sigma}$"
            f"     (σ = {SIGMA_NORM:.1f})",
            fontsize=12, transform=ax.transAxes, va='top')


def show_heatmap(ax, mat, t, title, ylabel=True, vmax=None):
    """One heatmap in R&H style."""
    if vmax is None:
        vmax = mat.max()
    im = ax.imshow(
        mat,
        extent=[t[0], t[-1], THETA_PREFS_DEG[0], THETA_PREFS_DEG[-1]],
        origin='lower', aspect='auto',
        cmap='gray_r', vmin=0, vmax=vmax,
    )
    ax.axvline(T_TRANS_START, color='#C0392B', lw=0.6, alpha=0.85)
    ax.axvline(T_TRANS_END,   color='#C0392B', lw=0.6, alpha=0.85)
    ax.set_yticks([-180, -90, 0, 90, 180])
    if ylabel:
        ax.set_yticklabels(['Left\n(-180°)', 'Down\n(-90°)', 'Right\n(0°)',
                            'Up\n(90°)', 'Left\n(180°)'])
        ax.set_ylabel('Preferred direction', fontsize=10)
    else:
        ax.set_yticklabels([])
    ax.set_xlabel('Time (ms)', fontsize=10)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.tick_params(labelsize=8)
    return im


def stimulus_input_field(theta_prefs_deg, t, condition, motion_swap,
                          band_halfwidth_deg=6.0):
    """2D field over (preferred direction × time): nonzero only in narrow
    bands at the three stimulus directions (Left = 180°, Right = 0°,
    Up = 90°) when the corresponding binary input is on.

    band_halfwidth_deg controls the visible thickness of each stripe.
    """
    stim_cw_fn, stim_ccw_fn, c_trans_fn = channels_for_trial(condition,
                                                             motion_swap)
    S_cw    = stim_cw_fn(t)     # CW rotation  → Up   (90°)
    S_ccw   = stim_ccw_fn(t)    # CCW rotation → Down (−90°)
    S_trans = c_trans_fn(t)     # translation  → Right (0°)

    field = np.zeros((len(theta_prefs_deg), len(t)))
    for stim_dir, signal in [
        (DIR_CW,    S_cw),
        (DIR_CCW,   S_ccw),
        (DIR_TRANS, S_trans),
    ]:
        # Circular distance from each preferred direction to stim_dir
        diff = ((theta_prefs_deg - stim_dir + 180.0) % 360.0) - 180.0
        in_band = np.abs(diff) <= band_halfwidth_deg
        field[in_band, :] = np.maximum(field[in_band, :], signal[None, :])
    return field


def draw_flow_arrow(fig, ax_from, ax_to, label=None, color='#444'):
    """Draw a connecting arrow between two subplots in figure coordinates."""
    from matplotlib.transforms import blended_transform_factory
    p1 = ax_from.get_position()
    p2 = ax_to.get_position()
    # Determine direction
    if p2.x0 > p1.x1:                     # ax_to is to the right
        x_start, y_start = p1.x1, (p1.y0 + p1.y1) / 2
        x_end,   y_end   = p2.x0, (p2.y0 + p2.y1) / 2
    elif p2.x1 < p1.x0:                   # ax_to is to the left
        x_start, y_start = p1.x0, (p1.y0 + p1.y1) / 2
        x_end,   y_end   = p2.x1, (p2.y0 + p2.y1) / 2
    elif p2.y0 > p1.y1:                   # ax_to is above
        x_start, y_start = (p1.x0 + p1.x1) / 2, p1.y1
        x_end,   y_end   = (p2.x0 + p2.x1) / 2, p2.y0
    else:                                 # ax_to is below
        x_start, y_start = (p1.x0 + p1.x1) / 2, p1.y0
        x_end,   y_end   = (p2.x0 + p2.x1) / 2, p2.y1

    arr = FancyArrowPatch(
        (x_start, y_start), (x_end, y_end),
        transform=fig.transFigure,
        arrowstyle='->,head_width=6,head_length=8',
        color=color, lw=1.5,
        shrinkA=4, shrinkB=4,
    )
    fig.patches.append(arr)
    if label:
        fig.text((x_start + x_end) / 2,
                 (y_start + y_end) / 2 + 0.012,
                 label, ha='center', va='bottom', fontsize=9, color=color,
                 style='italic')


def render_page(condition, motion_swap, out_path, page_title):
    """Render one R&H Fig 1 style page for the given trial type."""
    dt = 1.0
    t_full = np.arange(0.0, T_END + dt, dt)
    mask = t_full >= T_FIELD2_ON
    t = t_full[mask]

    layers_full = compute_cascade_centered(t_full, condition, motion_swap)
    layers = {k: v[:, mask] for k, v in layers_full.items()}
    stim_in = stimulus_input_field(THETA_PREFS_DEG, t, condition, motion_swap)

    # --- Figure scaffold: 3 rows x 3 cols, plus-sign arrangement ---------
    fig = plt.figure(figsize=(14.5, 11.0))
    gs = gridspec.GridSpec(
        3, 3,
        width_ratios=[1.0, 1.1, 1.1],
        height_ratios=[0.8, 1.0, 0.8],
        left=0.06, right=0.96, top=0.92, bottom=0.06,
        hspace=0.55, wspace=0.30,
    )

    ax_A    = fig.add_subplot(gs[0, 1])  # top:    attention field
    ax_stim = fig.add_subplot(gs[1, 0])  # left:   stimulus input (heatmap)
    ax_E    = fig.add_subplot(gs[1, 1])  # centre: stimulus drive
    ax_R    = fig.add_subplot(gs[1, 2])  # right:  output
    ax_S    = fig.add_subplot(gs[2, 1])  # bottom: suppressive drive
    ax_eq   = fig.add_subplot(gs[2, 2])  # bottom-right: equations

    # Stimulus input uses its own vmax so the binary bands are visible.
    # (Earlier we tried sharing E's vmax, but the bands then sit below
    # ~12% gray and disappear into the background.)
    show_heatmap(ax_stim, stim_in, t,
                 title=r'   Stimulus input  $S_i(t)$  '
                       r'(narrow bands at $\theta_L, \theta_R, \theta_U$)',
                 vmax=stim_in.max())
    show_heatmap(ax_A, layers['A'], t,
                 title=r'A.  Attention field  $A(\theta)$',
                 vmax=layers['A'].max())
    show_heatmap(ax_E, layers['E'], t,
                 title=r'B.  Stimulus drive  $E(\theta, t)$',
                 vmax=layers['E'].max())
    show_heatmap(ax_R, layers['R'], t,
                 title=r'D.  Output  $R = (E \cdot A) / (S + \sigma)$',
                 vmax=layers['R'].max())
    show_heatmap(ax_S, layers['S'], t,
                 title=r'C.  Suppressive drive  '
                       r'$S(t) = \langle E \cdot A \rangle_\theta$',
                 vmax=layers['S'].max())
    draw_equations(ax_eq)

    fig.suptitle(page_title, fontsize=14.5, fontweight='bold', y=0.97)

    # Layout-aware arrows showing the data flow.  Drawn after the figure
    # is laid out so subplot positions are settled.
    fig.canvas.draw()
    draw_flow_arrow(fig, ax_stim, ax_E)                  # Stim → E
    draw_flow_arrow(fig, ax_A,    ax_E, color='#888')    # A    ↓ E
    draw_flow_arrow(fig, ax_E,    ax_S, color='#888')    # E    ↓ S
    draw_flow_arrow(fig, ax_E,    ax_R)                  # E    → R

    fig.savefig(out_path, dpi=160, bbox_inches='tight', facecolor='white')
    print(f'Saved {out_path}')
    plt.close(fig)


def main():
    render_page(
        condition='cued', motion_swap=False,
        out_path='rh_fig1_style_cued.png',
        page_title='Normalization-model cascade — CUED, no swap  '
                   '(R&H Fig 1 layout)',
    )
    render_page(
        condition='uncued', motion_swap=False,
        out_path='rh_fig1_style_uncued.png',
        page_title='Normalization-model cascade — UNCUED, no swap  '
                   '(R&H Fig 1 layout)',
    )


if __name__ == '__main__':
    main()
