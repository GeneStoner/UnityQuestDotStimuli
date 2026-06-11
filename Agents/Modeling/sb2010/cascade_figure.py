"""
Reynolds & Heeger (2009) Fig. 1 — style cascade visualization.

The four cascade layers are each portrayed as a 2D field over
(preferred direction × time), drawn at the same panel size and on the
same grayscale colormap.  This matches the visual idiom of R&H Fig. 1,
where stimulus drive, attention field, suppressive drive, and the
normalized output are all overlaid on the same 2D layout.

Two pages are produced:

    rh_cascade_noswap.png   CUED  and  UNCUED  with no motion swap
    rh_cascade_swap.png     CUED  and  UNCUED  with motion swap

Time window: from delayed onset (t = T_FIELD2_ON = 750 ms) onward,
consistent with the rest of the R&H-layered figures since the fixed
attention field is standing in for the SB 2010 adaptation-based cueing.

Run with:
    /usr/bin/python3 cascade_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END
from drive_figure import stimulus_drive_field
from rh_figure import attention_field, SIGMA_NORM


# Cascade-layer order and titles
LAYER_ORDER  = ['E', 'A', 'S', 'R']
LAYER_TITLES = {
    'E': r'Stimulus drive   $E(\theta, t)$',
    'A': r'Attention field  $A(\theta)$',
    'S': r'Suppressive drive  $S(t) = \langle E \cdot A \rangle_\theta$',
    'R': r'Normalized output  $R = (E \cdot A) / (S + \sigma)$',
}


def compute_cascade(theta_prefs_deg, t, condition, motion_swap):
    """Compute all four cascade layers as 2D fields (N_pref × N_t).

    A is constant in time → broadcast across the time axis.
    S is constant in θ at each t → broadcast across the direction axis.
    """
    E = stimulus_drive_field(theta_prefs_deg, t, condition, motion_swap)
    A_vec = attention_field(theta_prefs_deg)
    A_2d = np.broadcast_to(A_vec[:, None], E.shape)
    EA = E * A_vec[:, None]
    S_1d = EA.mean(axis=0)                                    # pool over θ
    S_2d = np.broadcast_to(S_1d[None, :], E.shape)
    R = EA / (S_1d[None, :] + SIGMA_NORM)
    return dict(E=E, A=A_2d, S=S_2d, R=R)


def _imshow_panel(ax, mat, vmax, t):
    """One heatmap panel.  Returns the imshow handle."""
    theta_prefs = np.arange(0.0, 360.0, 1.0)
    im = ax.imshow(
        mat,
        extent=[t[0], t[-1], theta_prefs[0], theta_prefs[-1]],
        origin='lower', aspect='auto',
        cmap='gray_r', vmin=0, vmax=vmax,
    )
    ax.axvline(T_TRANS_START, color='#C0392B', lw=0.6, alpha=0.85)
    ax.axvline(T_TRANS_END,   color='#C0392B', lw=0.6, alpha=0.85)
    ax.set_yticks([0, 90, 180, 270])
    ax.set_yticklabels(['Right\n(0°)', 'Up\n(90°)', 'Left\n(180°)',
                        'Down\n(270°)'])
    ax.tick_params(labelsize=8)
    return im


def render_page(cascades, vmaxes, out_path, page_title):
    """cascades: list of (column_label, layers_dict) — one per column."""
    dt = 1.0
    t_full = np.arange(0.0, T_END + dt, dt)
    mask = t_full >= T_FIELD2_ON
    t = t_full[mask]

    n_rows = len(LAYER_ORDER)
    n_cols = len(cascades)

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(11.0, 14.0),
        sharex=True, sharey=True,
    )
    plt.subplots_adjust(
        left=0.16, right=0.91, top=0.93, bottom=0.05,
        hspace=0.42, wspace=0.10,
    )

    for col, (col_label, layers) in enumerate(cascades):
        for row, name in enumerate(LAYER_ORDER):
            ax = axes[row, col]
            mat = layers[name][:, mask] if layers[name].shape[1] != len(t) \
                  else layers[name]
            im = _imshow_panel(ax, mat, vmaxes[name], t)

            if row == 0:
                ax.set_title(col_label, fontsize=12, fontweight='bold')
            if col == 0:
                ax.set_ylabel(LAYER_TITLES[name], fontsize=10.5,
                              labelpad=12)
            if row == n_rows - 1:
                ax.set_xlabel('Time (ms)', fontsize=10.5)

    # Per-row colorbars on the right
    for row, name in enumerate(LAYER_ORDER):
        last_ax = axes[row, -1]
        pos = last_ax.get_position()
        cax = fig.add_axes([pos.x1 + 0.02, pos.y0, 0.014, pos.height])
        # Dummy imshow to obtain a mappable with the right vmax
        sm = plt.cm.ScalarMappable(cmap='gray_r',
                                   norm=plt.Normalize(vmin=0, vmax=vmaxes[name]))
        cb = fig.colorbar(sm, cax=cax)
        cb.ax.tick_params(labelsize=8)
        cb.set_label(name, fontsize=10)

    fig.suptitle(page_title, fontsize=13.5, fontweight='bold', y=0.99)
    fig.savefig(out_path, dpi=160, bbox_inches='tight', facecolor='white')
    print(f"Saved {out_path}")
    plt.close(fig)


ALL_CONDITIONS = [
    ('CUED, no swap',   'cued',   False),
    ('UNCUED, no swap', 'uncued', False),
    ('CUED, swap',      'cued',   True),
    ('UNCUED, swap',    'uncued', True),
]


def main():
    dt = 1.0
    t_full = np.arange(0.0, T_END + dt, dt)
    mask = t_full >= T_FIELD2_ON
    theta_prefs = np.arange(0.0, 360.0, 1.0)

    # Compute all 4 cascades; restrict each layer to delayed-onset onward
    all_cascades = {}
    for label, cond, swap in ALL_CONDITIONS:
        layers_full = compute_cascade(theta_prefs, t_full, cond, swap)
        layers = {k: v[:, mask] for k, v in layers_full.items()}
        all_cascades[(cond, swap)] = (label, layers)

    # Global per-layer vmaxes so both pages share scales
    vmaxes = {
        name: max(c[1][name].max() for c in all_cascades.values())
        for name in LAYER_ORDER
    }

    render_page(
        cascades=[all_cascades[('cued',   False)],
                  all_cascades[('uncued', False)]],
        vmaxes=vmaxes,
        out_path='rh_cascade_noswap.png',
        page_title=('Page 1.  Reynolds–Heeger cascade — '
                    'CUED vs UNCUED, no motion swap'),
    )
    render_page(
        cascades=[all_cascades[('cued',   True)],
                  all_cascades[('uncued', True)]],
        vmaxes=vmaxes,
        out_path='rh_cascade_swap.png',
        page_title=('Page 2.  Reynolds–Heeger cascade — '
                    'CUED vs UNCUED, with motion swap'),
    )


if __name__ == '__main__':
    main()
