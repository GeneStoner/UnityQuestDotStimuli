"""
Feature-trajectory figure laid out to match Stoner & Blanc (2010) Fig. 4
(top two rows only — the delayed-onset cued/uncued conditions; the
common-onset neutral row E/F is omitted).

Reuses the LOCKED trajectory convention from web_figures._traj_panel
(line style = identity / dotted = translator, colour = dot colour,
row = CW/TRANS/CCW) — nothing about the convention is re-derived here.

S&B Fig. 4 panel mapping (see their Table 1):
    A  no-swap,  delayed translates ("cued",   old motion)
    B  swap,     ("uncued", old motion)   <- uncued motion-swap trajectory
    C  no-swap,  ("uncued", new motion)
    D  swap,     ("cued",   new motion)   <- cued   motion-swap trajectory
The motion swap turns a cued (delayed-dots) translation into the
functional uncued case, so the cued-swap trajectory sits in D (bottom)
and the uncued-swap trajectory in B (top).  Cued/uncued row labels are
dropped; the caption carries the explanation.

Run:  /usr/bin/python3 traj_figure_sb4.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from web_figures import _traj_panel, INK, INK2, ROW_TICKS, ROW_LABELS

# (row, col, letter, cue, motion_swap)
PANELS = [
    (0, 0, "A", "CUED",   False),
    (0, 1, "B", "UNCUED", True),
    (1, 0, "C", "UNCUED", False),
    (1, 1, "D", "CUED",   True),
]
COL_TITLES = ["No-motion-swap", "Motion-swap"]


def fig_traj_sb4(out="web_model_traj_sb4.png"):
    fig, axes = plt.subplots(2, 2, figsize=(11, 5.4), sharex=True)
    for row, col, letter, cue, swap in PANELS:
        ax = axes[row, col]
        _traj_panel(ax, cue, motion_swap=swap, color_swap=False, field_color=INK)
        # Single-RF (left) interpretation: relabel rotation/translation rows as
        # local motion directions, matching the de-identified input figure.
        ax.set_yticks(ROW_TICKS)
        ax.set_yticklabels(ROW_LABELS)
        # panel letter + cued/uncued label, top-left inside the axes
        cue_label = "cued" if cue == "CUED" else "uncued"
        ax.text(0.015, 0.93, f'{letter}: "{cue_label}"', transform=ax.transAxes,
                fontsize=11, fontweight="bold", color=INK, va="top", ha="left")
        if row == 0:
            ax.set_title(COL_TITLES[col], fontsize=13, fontweight="bold",
                         pad=10, color=INK)
        if row == 1:
            ax.set_xlabel("time  (ms)")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    fig_traj_sb4()
