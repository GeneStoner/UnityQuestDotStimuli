"""
Translation-detector response (CUED vs UNCUED) computed with the VERIFIED
port of attentionModel.m — the figure that replaces the hand-rolled
translation_response.png on the website.

R(θ = 0°, t): the normalized population response at the translation direction,
over the whole trial.  The zoom panel on the 40 ms window was dropped (GS,
2026-08-19): it magnified the same two traces and the separation is already
plain in the full-trial view, with the peak values reported in the footer.
σ = 1 to
match the activity-maps cascade (rh_activity_maps.py).  A fixed attentional
gain on the cued direction, with no adaptation, yields the cued advantage.

Run:  /usr/bin/python3 rh_translation_response.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END
from drive_figure import DIR_TRANS
from sb_rh_verified import run_sb_rh_with_sigma, THETA_PREFS

GREEN, RED = "#2E8B57", "#C0392B"

# R&H's published default normalization constant (matches rh_activity_maps.py).
SIGMA = 1e-6


def main():
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    idx = int(np.argmin(np.abs(THETA_PREFS - DIR_TRANS)))

    Rc = run_sb_rh_with_sigma("cued",   False, t, SIGMA)[idx, :]
    Ru = run_sb_rh_with_sigma("uncued", False, t, SIGMA)[idx, :]
    win = (t >= T_TRANS_START) & (t < T_TRANS_END)
    pc, pu = float(Rc[win].max()), float(Ru[win].max())
    bias = (pc / pu - 1.0) * 100.0

    fig, ax = plt.subplots(1, 1, figsize=(11.0, 4.6))

    ax.plot(t, Rc, color=GREEN, lw=2.0,
            label="CUED   (delayed/cued field translates)")
    ax.plot(t, Ru, color=RED, lw=2.0, ls="--",
            label="UNCUED (first-on/uncued field translates)")
    ax.axvspan(T_TRANS_START, T_TRANS_END, color="gray", alpha=0.18, zorder=0)
    ax.axvline(T_FIELD2_ON, color="black", lw=0.6, alpha=0.5)
    ytop = max(Rc.max(), Ru.max())
    ax.text(T_FIELD2_ON + 12, ytop * 0.9, "delayed onset (Field 2 appears)",
            fontsize=9, color="#555", va="top")
    ax.text((T_TRANS_START + T_TRANS_END) / 2, Rc.min() + 0.02,
            "40 ms translation", fontsize=9, color="#555",
            ha="center", va="bottom")
    ax.set_xlim(0, t[-1])
    ax.set_xlabel("Time (ms)", fontsize=11)
    ax.set_ylabel(r"$R(\theta=0°,\, t)$   (translation detector)", fontsize=11)
    ax.set_title("Translation-detector response over the full trial duration",
                 loc="left", fontsize=11.5, fontweight="bold")
    ax.legend(fontsize=10, loc="upper left")

    fig.text(0.5, 0.005,
             f"Peak R(0°):  CUED = {pc:.3f},   UNCUED = {pu:.3f}      "
             f"(cued / uncued − 1) = {bias:+.2f}%      "
             f"[verified R&H port, σ = {SIGMA:.0e}]",
             ha="center", fontsize=11, fontweight="bold")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    out = "rh_translation_response.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}   CUED={pc:.3f}  UNCUED={pu:.3f}  bias={bias:+.2f}%")


if __name__ == "__main__":
    main()
