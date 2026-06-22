"""
Confirmation figure: our Python port of attentionModel.m reproduces ALL nine
Reynolds & Heeger (2009) published figures, overlaid on the authors' own MATLAB
output.  Numeric PASS/FAIL (machine-precision agreement) is in compare_figures.py;
this renders the visual side-by-side.

3x3 grid, one panel per R&H figure.  Solid line = our Python port; open circles
= the authors' MATLAB ground truth.

Run from this directory:  /usr/bin/python3 rh_replication_figure.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from compare_figures import (
    run_figure2A, run_figure2B, run_figure3C, run_figure3F,
    run_figure4C, run_figure4E, run_figure5C, run_figure6C, run_figure7C,
    _load_csv,
)

BLUE, RED, GRAY = "#1f77b4", "#d62728", "#555555"   # Att away, Att RF, Att away (7C)


def crf_panel(ax, runner, csv, title):
    contrasts, unatt, att = runner()
    m = _load_csv(csv)
    ax.semilogx(contrasts, unatt, color=BLUE, lw=2.0)
    ax.semilogx(contrasts, att,   color=RED,  lw=2.0)
    ax.semilogx(m["contrast"], m["unattCRF"], "o", mfc="none", mec=BLUE, ms=6, mew=1.3)
    ax.semilogx(m["contrast"], m["attCRF"],   "o", mfc="none", mec=RED,  ms=6, mew=1.3)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Contrast", fontsize=8)
    ax.set_ylabel("Response", fontsize=8)
    ax.tick_params(labelsize=7)


def tc_panel(ax, runner, csv, title):
    theta, unatt, att = runner()
    m = _load_csv(csv)
    ax.plot(theta, unatt, color=BLUE, lw=2.0)
    ax.plot(theta, att,   color=RED,  lw=2.0)
    ax.plot(m["theta"], m["unattCRF"], "o", mfc="none", mec=BLUE, ms=5, mew=1.2, markevery=2)
    ax.plot(m["theta"], m["attCRF"],   "o", mfc="none", mec=RED,  ms=5, mew=1.2, markevery=2)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Preferred orientation (°)", fontsize=8)
    ax.set_ylabel("Response", fontsize=8)
    ax.tick_params(labelsize=7)


def f7c_panel(ax):
    ori, pv, pn, pa, vv, nn, va = run_figure7C()
    m = _load_csv("figure7c_matlab.csv")
    ax.plot(ori, pv, color=RED,  lw=2.0)
    ax.plot(ori, pn, color=BLUE, lw=2.0)
    ax.plot(ori, pa, color=GRAY, lw=2.0)
    for col, c in [("pair_att_var", RED), ("pair_att_null", BLUE), ("pair_att_away", GRAY)]:
        ax.plot(m["orientation"], m[col], "o", mfc="none", mec=c, ms=5, mew=1.2, markevery=2)
    ax.set_title("Figure 7C", fontsize=11, fontweight="bold")
    ax.set_xlabel("Stimulus orientation (°)", fontsize=8)
    ax.set_ylabel("Response", fontsize=8)
    ax.tick_params(labelsize=7)


def main():
    fig, axes = plt.subplots(3, 3, figsize=(13.5, 11.0))
    crf_panel(axes[0, 0], run_figure2A, "figure2a_matlab.csv", "Figure 2A")
    crf_panel(axes[0, 1], run_figure2B, "figure2b_matlab.csv", "Figure 2B")
    crf_panel(axes[0, 2], run_figure3C, "figure3c_matlab.csv", "Figure 3C")
    crf_panel(axes[1, 0], run_figure3F, "figure3f_matlab.csv", "Figure 3F")
    crf_panel(axes[1, 1], run_figure4C, "figure4c_matlab.csv", "Figure 4C")
    crf_panel(axes[1, 2], run_figure4E, "figure4e_matlab.csv", "Figure 4E")
    tc_panel (axes[2, 0], run_figure5C, "figure5c_matlab.csv", "Figure 5C")
    tc_panel (axes[2, 1], run_figure6C, "figure6c_matlab.csv", "Figure 6C")
    f7c_panel(axes[2, 2])

    handles = [
        Line2D([0], [0], color=RED,  lw=2, label="attended (Python port)"),
        Line2D([0], [0], color=BLUE, lw=2, label="unattended (Python port)"),
        Line2D([0], [0], marker="o", mfc="none", mec="#333", ls="none", ms=6,
               label="authors' MATLAB output"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, fontsize=10,
               frameon=False, bbox_to_anchor=(0.5, 0.985))
    fig.suptitle("Replication of Reynolds & Heeger (2009) — our Python port vs. the authors' MATLAB",
                 fontsize=13.5, fontweight="bold", y=0.955)
    fig.text(0.5, 0.004,
             "All nine published figures reproduced to machine precision "
             "(max relative error < 1e-14; numeric check in compare_figures.py).",
             ha="center", fontsize=9.5, color="#444")
    fig.tight_layout(rect=[0, 0.02, 1, 0.93])
    fig.savefig("rh_replication.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote rh_replication.png")


if __name__ == "__main__":
    main()
