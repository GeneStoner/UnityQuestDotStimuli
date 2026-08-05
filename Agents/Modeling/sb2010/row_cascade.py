"""
Row-cascade figure for the motion-competition model.

Two rows — CUED and UNCUED (the two distinct cases the four trial types
reduce to, since A=B and C=D at the input).  Four columns read left -> right
as the computation itself:

    1. Stimulus input   — the three direction channels (binary)
    2. Adapting responses (Eq 4-5)
    3. Competition       — inhibition I = R1+R2  vs  excitation E
    4. Detector output   — R_TD

Convention (locked, matches the trajectory / S&B Fig 3): GREEN = the
translating (test) field's rotation channel — the one interrupted during the
window; RED = the steady competitor; BLUE = the translation / excitation.

Run:  /usr/bin/python3 row_cascade.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from web_figures import INK, INK2, ACCENT, CUED, UNCUED, GRID, WIN, _style_axes  # noqa: F401
from parameters import (
    T_END, T_TRANS_START, T_TRANS_END, T_FIELD2_ON, W_TRANS, W_ROT,
)
from stimulus import channels_for_trial, channels_have_gap
from model import simulate_adapting_channel, translation_detector

GREEN, RED, BLUE = CUED, UNCUED, ACCENT


def compute(cond, dt=1.0):
    t = np.arange(0.0, T_END + dt, dt)
    s_cw, s_ccw, s_tr = channels_for_trial(cond, False)
    R_cw, _ = simulate_adapting_channel(s_cw, t)
    R_ccw, _ = simulate_adapting_channel(s_ccw, t)
    R_tr, _ = simulate_adapting_channel(s_tr, t)
    cw_gap, _ccw_gap = channels_have_gap(cond, False)
    # the gapping channel is the translating (test) field
    if cw_gap:
        transl_in, comp_in = s_cw(t), s_ccw(t)
        transl_R, comp_R = R_cw, R_ccw
    else:
        transl_in, comp_in = s_ccw(t), s_cw(t)
        transl_R, comp_R = R_ccw, R_cw
    return dict(
        t=t, tr_in=s_tr(t), transl_in=transl_in, comp_in=comp_in,
        transl_R=transl_R, comp_R=comp_R, R_tr=R_tr,
        I=W_ROT * (R_cw + R_ccw), E=W_TRANS * R_tr,
        R_TD=translation_detector(R_tr, R_cw, R_ccw),
    )


def _peak(t, y):
    m = (t >= T_TRANS_START) & (t <= T_TRANS_END + 120)
    return float(y[m].max())


def _ax(ax):
    _style_axes(ax)
    ax.axvspan(T_TRANS_START, T_TRANS_END, **WIN)
    ax.set_xlim(0, T_END)


CW_, TRANS_, CCW_ = 2, 1, 0


def _draw_input(ax, cond):
    """Column 1 in the direction-bar format (matches the trajectory / input
    figures).  Rows = CW / TRANS / CCW; role-coloured bars: GREEN = the
    translating field's rotation (gaps during the window), RED = the
    competitor's rotation (steady), BLUE = the translation."""
    _ax(ax)
    ax.grid(False)
    for y in (CW_, TRANS_, CCW_):
        ax.axhline(y, color=GRID, lw=1.0, zorder=0)
    ax.set_ylim(-0.6, 2.6)
    ax.set_yticks([CCW_, TRANS_, CW_])
    ax.set_yticklabels(["Up", "TRANS", "Down"])
    ts, te, T0 = T_TRANS_START, T_TRANS_END, T_FIELD2_ON
    transl_onset = T0 if cond == "cued" else 0
    comp_onset = 0 if cond == "cued" else T0
    bw = 7.0
    ax.plot([transl_onset, ts], [CW_, CW_], color=INK, lw=bw,
            solid_capstyle="butt", zorder=3)            # translating rotation
    ax.plot([te, T_END], [CW_, CW_], color=INK, lw=bw,
            solid_capstyle="butt", zorder=3)            # ... resumes after gap
    ax.plot([comp_onset, T_END], [CCW_, CCW_], color=INK, lw=bw,
            solid_capstyle="butt", zorder=3)            # competitor rotation
    ax.plot([ts, te], [TRANS_, TRANS_], color=INK, lw=bw,
            solid_capstyle="butt", zorder=3)            # translation


def main():
    data = {c: compute(c) for c in ("cued", "uncued")}
    Imax = max(d["I"].max() for d in data.values()) * 1.12
    Rmax = 105
    Pmax = max(_peak(d["t"], d["R_TD"]) for d in data.values()) * 1.3

    fig, axes = plt.subplots(2, 4, figsize=(15, 6.3), sharex=True)
    titles = ["Stimulus input", "Adapting responses  (Hz)",
              "Competition:  I  vs  E", "Detector output  $R_{TD}$"]
    rows = ["CUED", "UNCUED"]

    for i, cond in enumerate(("cued", "uncued")):
        d = data[cond]; t = d["t"]

        # 1 — stimulus input (direction-bar format)
        _draw_input(axes[i, 0], cond)
        axes[i, 0].annotate(rows[i], xy=(-0.42, 0.5), xycoords="axes fraction",
                            rotation=90, ha="center", va="center",
                            fontsize=13, fontweight="bold", color=INK)

        # 2 — adapting responses
        ax = axes[i, 1]; _ax(ax)
        ax.plot(t, d["comp_R"], color=INK, lw=2.4)
        ax.plot(t, d["transl_R"], color=INK, lw=2.4, ls=(0, (4, 2)))
        ax.plot(t, d["R_tr"], color=BLUE, lw=2.0)
        ax.set_ylim(0, Rmax)
        lev = _peak(t, d["comp_R"])    # surviving competitor ~ the inhibition
        ax.annotate(f"competitor\n≈ {lev:.0f}", xy=(T_TRANS_END, lev),
                    xytext=(T_TRANS_END + 150, lev + (20 if cond == "cued" else -2)),
                    fontsize=8.5, color=INK, va="center",
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.1))

        # 3 — competition: inhibition vs excitation
        ax = axes[i, 2]; _ax(ax)
        ax.plot(t, d["I"], color=INK, lw=2.4)
        ax.plot(t, d["E"], color=BLUE, lw=2.0, ls="--")
        ax.set_ylim(0, Imax)

        # 4 — detector output
        ax = axes[i, 3]; _ax(ax)
        ax.fill_between(t, 0, d["R_TD"], color=BLUE, alpha=0.16, lw=0)
        ax.plot(t, d["R_TD"], color=BLUE, lw=2.4)
        ax.set_ylim(0, Pmax)
        pk = _peak(t, d["R_TD"])
        ax.text(T_TRANS_END + 60, pk, f"{pk:.0f}", fontsize=11,
                color=INK, va="center", fontweight="bold")

        if i == 1:
            for j in range(4):
                axes[i, j].set_xlabel("time  (ms)")

    for j, ti in enumerate(titles):
        axes[0, j].set_title(ti, fontsize=11.5, fontweight="bold", pad=8)

    # legends
    axes[0, 2].legend(handles=[
        Line2D([0], [0], color=INK, lw=2.4, label="$I=R_1{+}R_2$"),
        Line2D([0], [0], color=BLUE, lw=2.0, ls="--", label="$E$")],
        fontsize=8.5, loc="upper left", frameon=False)

    fig.tight_layout()
    fig.savefig("row_cascade.png", dpi=160, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    bias = (_peak(data["cued"]["t"], data["cued"]["R_TD"]) /
            _peak(data["uncued"]["t"], data["uncued"]["R_TD"]) - 1) * 100
    print(f"wrote row_cascade.png   (cued/uncued bias = +{bias:.1f}%)")


if __name__ == "__main__":
    main()
