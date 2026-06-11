"""
Show the model's motion-channel inputs across the four delayed-onset
conditions of Stoner & Blanc (2010), Mode 1 (binary).

The motion-competition model has three input channels:

    Left  :  CW  rotation        — locally, dots move leftward in the RF
    Right :  CCW rotation        — locally, dots move rightward in the RF
    Up    :  brief translation   — assumed direction for the demo

These three labels are an idealization that's a reasonable approximation
for any one small RF: a global rotation locally produces a single
translational direction.

The point of the figure: the model has NO field-identity channel.  It
sees only direction-of-motion.  Consequently the trial types pair up:

    (CUED,   no swap)  ≡  (UNCUED, swap)     same Left/Right/Up inputs
    (UNCUED, no swap)  ≡  (CUED,   swap)     same Left/Right/Up inputs

Identical inputs → identical model outputs → predicted reversal of the
cued/uncued bias under motion swap.

Run with:
    /usr/bin/python3 inputs_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from parameters import T_END, T_TRANS_START, T_TRANS_END
from stimulus import channels_for_trial


CONDITIONS = [
    # (column label, condition, motion_swap, group color for the column frame)
    ("CUED\nno swap",   'cued',   False, '#2E8B57'),
    ("UNCUED\nno swap", 'uncued', False, '#C0392B'),
    ("CUED\nswap",      'cued',   True,  '#C0392B'),
    ("UNCUED\nswap",    'uncued', True,  '#2E8B57'),
]

CHANNEL_INFO = [
    # (display name, color, max amplitude expected)
    ('Left\n(CW rotation)',   '#8E44AD', 50),
    ('Right\n(CCW rotation)', '#16A085', 50),
    ('Up\n(translation)',     '#D35400', 25),
]


def main():
    fig, axes = plt.subplots(
        3, 4,
        figsize=(13.0, 7.0),
        sharex=True, sharey='row',
        gridspec_kw=dict(hspace=0.30, wspace=0.18),
    )

    dt = 0.5
    t = np.arange(0.0, T_END + dt, dt)

    for col, (col_label, condition, swap, frame_color) in enumerate(CONDITIONS):
        stim_cw, stim_ccw, c_trans = channels_for_trial(condition, swap)
        signals = [stim_cw(t), stim_ccw(t), c_trans(t)]

        for row, ((ch_label, ch_color, ymax), signal) in enumerate(
                zip(CHANNEL_INFO, signals)):
            ax = axes[row, col]
            # Just the outline of the input — step trace.
            ax.plot(t, signal, color=ch_color, linewidth=1.6,
                    drawstyle='steps-post')
            ax.axvspan(T_TRANS_START, T_TRANS_END,
                       color='gray', alpha=0.18, zorder=0)
            ax.set_xlim(0, T_END)
            ax.set_ylim(-4, 60)
            ax.set_yticks([0, 25, 50])
            ax.tick_params(labelsize=8)

            if col == 0:
                ax.set_ylabel(ch_label, fontsize=10.5)
            if row == 0:
                ax.set_title(col_label, fontsize=11, fontweight='bold',
                             color=frame_color)
            if row == 2:
                ax.set_xlabel('Time (ms)', fontsize=10)

            # Draw a colored frame around the axes to flag equivalence
            for spine in ax.spines.values():
                spine.set_edgecolor(frame_color)
                spine.set_linewidth(1.5)

    fig.suptitle(
        "Motion-channel inputs across the four delayed-onset trial types  "
        "(Mode 1, binary)",
        fontsize=12.5, fontweight='bold', y=0.995,
    )

    fig.text(
        0.5, 0.945,
        "Columns sharing a frame color have IDENTICAL Left/Right/Up inputs — "
        "and hence identical model outputs.\n"
        "Green-framed pair: (CUED, no swap) ≡ (UNCUED, swap).   "
        "Red-framed pair: (UNCUED, no swap) ≡ (CUED, swap).",
        ha='center', va='top', fontsize=10, color='#333',
    )

    fig.text(
        0.005, 0.5,
        "Input strength  (dimensionless stimulus units, per S&B 2010 App. A)",
        ha='left', va='center', rotation=90, fontsize=10, color='#555',
    )

    fig.subplots_adjust(top=0.86, bottom=0.08, left=0.10, right=0.98)

    out = 'inputs_figure.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    print(f"Saved {out}")


if __name__ == '__main__':
    main()
