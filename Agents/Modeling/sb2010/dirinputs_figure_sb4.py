"""
Direction-of-motion INPUT figure, S&B (2010) Fig. 4 layout (A-D).

This is what the model's direction channels actually receive: the motion
directions present in the display over time, with dot identity removed
(the model pools over which dots carry each direction).  Channel occupancy
is derived from the SAME field-trajectory vertices used by
web_figures._traj_panel, so it is guaranteed consistent with the feature-
trajectory figure's locked convention (green/cued/delayed on the CW row).

Key result it makes visible:
    A (cued no-swap)  ==  B (uncued motion-swap)      [CCW continuous, CW gaps]
    C (uncued no-swap) == D (cued  motion-swap)       [CW continuous, CCW gaps]
The motion swap produces no new directional input — it maps each trial onto
the opposite cue's no-swap input — so the model cannot tell A from B or
C from D, and is forced to predict a reversal.

Run:  /usr/bin/python3 dirinputs_figure_sb4.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from web_figures import (_style_axes, INK, INK2, ACCENT, GRID, WIN,
                         ROW_TICKS, ROW_LABELS)
from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END

CW_, TRANS_, CCW_ = 2, 1, 0


def field_vertices(cue, motion_swap):
    """Reproduce the two field trajectories from web_figures._traj_panel."""
    ts, te, T0 = T_TRANS_START, T_TRANS_END, T_FIELD2_ON
    transl_onset = T0 if cue == "CUED" else 0
    other_onset = 0 if cue == "CUED" else T0
    if not motion_swap:
        g_onset, r_onset = transl_onset, other_onset
        green_v = [(g_onset, CW_), (ts, CW_), (ts, TRANS_),
                   (te, TRANS_), (te, CW_), (T_END, CW_)]
        red_v = [(r_onset, CCW_), (ts, CCW_), (T_END, CCW_)]
    else:
        r_onset, g_onset = transl_onset, other_onset
        red_v = [(r_onset, CCW_), (ts, CCW_), (ts, TRANS_),
                 (te, TRANS_), (te, CW_), (T_END, CW_)]
        green_v = [(g_onset, CW_), (ts, CW_), (ts, CCW_), (T_END, CCW_)]
    return green_v, red_v


def horizontal_intervals(verts):
    """(t0, t1, row) for each horizontal (constant-row) segment."""
    out = []
    for (t0, r0), (t1, r1) in zip(verts[:-1], verts[1:]):
        if r0 == r1 and t1 > t0:
            out.append((t0, t1, r0))
    return out


def channel_occupancy(cue, motion_swap):
    """All (t0, t1, row) intervals where ANY field occupies a direction row."""
    g, r = field_vertices(cue, motion_swap)
    return horizontal_intervals(g) + horizontal_intervals(r)


PANELS = [
    (0, 0, "A", "CUED",   False),
    (0, 1, "B", "UNCUED", True),
    (1, 0, "C", "UNCUED", False),
    (1, 1, "D", "CUED",   True),
]
COL_TITLES = ["No-motion-swap", "Motion-swap"]


def _panel(ax, cue, motion_swap, letter, col, row):
    _style_axes(ax)
    ax.grid(False)
    for y in (CW_, TRANS_, CCW_):
        ax.axhline(y, color=GRID, lw=1.0, zorder=0)
    ax.axvspan(T_TRANS_START, T_TRANS_END, **WIN)
    ax.set_xlim(0, T_END)
    ax.set_ylim(-0.6, 2.6)
    ax.set_yticks(ROW_TICKS)
    ax.set_yticklabels(ROW_LABELS)

    # De-identified twin of the trajectory figure: the SAME panels, but every
    # field's motion direction over time drawn as black, solid, horizontal
    # segments — no colour, no identity (line style), no vertical transitions.
    # Same line weight as _traj_panel (2.6) so the two figures crossfade
    # cleanly when toggled.  This is exactly what the model receives once dot
    # identity is discarded.
    for t0, t1, rrow in channel_occupancy(cue, motion_swap):
        ax.plot([t0, t1], [rrow, rrow], color=INK, lw=2.6,
                solid_capstyle="round", zorder=3)

    cue_label = "cued" if cue == "CUED" else "uncued"
    ax.text(0.015, 0.93, f'{letter}: "{cue_label}"', transform=ax.transAxes,
            fontsize=11, fontweight="bold", color=INK, va="top", ha="left")
    if row == 0:
        ax.set_title(COL_TITLES[col], fontsize=13, fontweight="bold",
                     pad=10, color=INK)
    if row == 1:
        ax.set_xlabel("time  (ms)")


def fig_dirinputs_sb4(out="web_model_input_sb4.png"):
    fig, axes = plt.subplots(2, 2, figsize=(11, 5.4), sharex=True)
    for row, col, letter, cue, swap in PANELS:
        _panel(axes[row, col], cue, swap, letter, col, row)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    fig_dirinputs_sb4()
