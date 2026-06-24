"""
PROTOTYPE: amplitude-vs-time traces of the key non-constant variables of the
two models, side by side — R&H normalization (bias = attention) vs S&B
motion-competition (bias = adaptation), CUED vs UNCUED.

S&B traces use the EXACT discrete detector quantities (matching the original
S&B plots row_cascade.py / web_model_adapting_inputs.py):
    drive  E = W_TRANS · R_T            (translation excitation)
    supp   I = W_ROT · (R_1 + R_2)      (rotation inhibition — NOT incl. E)
    resp   R = K·E / (E + I + σ)        (translation detector; +32.9%, 61 vs 46)
NOT the von-Mises-spread map slices (which leak rotation tails into θ=0 and
give the wrong +24%).

R&H traces are read at θ=0 from the verified-port cascade (its native
population output).

Run:  /usr/bin/python3 model_traces_compare.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parameters import (T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END,
                        W_TRANS, W_ROT)
from rh_activity_maps import cascade as rh_cascade
from sb_rh_verified import THETA_PREFS
from stimulus import channels_for_trial
from model import simulate_adapting_channel, translation_detector

GREEN, RED = "#2E8B57", "#C0392B"
IDX0_RH = int(np.argmin(np.abs(THETA_PREFS)))
T = np.arange(0.0, T_END + 1.0, 1.0)


def rh_traces(cond):
    d = rh_cascade(cond, False, T)
    return {"drive": d["Eraw"][IDX0_RH, :],
            "supp":  d["I"][IDX0_RH, :],
            "resp":  d["R"][IDX0_RH, :]}


def sb_traces(cond):
    s_cw, s_ccw, s_tr = channels_for_trial(cond, False)
    R_cw, _ = simulate_adapting_channel(s_cw, T)
    R_ccw, _ = simulate_adapting_channel(s_ccw, T)
    R_tr, _ = simulate_adapting_channel(s_tr, T)
    return {"drive": W_TRANS * R_tr,
            "supp":  W_ROT * (R_cw + R_ccw),
            "resp":  translation_detector(R_tr, R_cw, R_ccw)}


def _panel(ax, yc, yu, ylabel, title=None, annotate=False):
    ax.plot(T, yc, color=GREEN, lw=2.1, label="cued")
    ax.plot(T, yu, color=RED, lw=2.1, ls="--", label="uncued")
    ax.axvspan(T_TRANS_START, T_TRANS_END, color="0.85", alpha=0.7, zorder=0)
    ax.axvline(T_FIELD2_ON, color="0.6", lw=0.7)
    ax.set_xlim(T[0], T[-1]); ax.margins(y=0.12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=11.5, fontweight="bold")
    if annotate:
        win = (T >= T_TRANS_START) & (T < T_TRANS_END)
        pc, pu = float(yc[win].max()), float(yu[win].max())
        ax.text(0.97, 0.06, f"peak {pc:.0f} vs {pu:.0f}  (+{(pc/pu-1)*100:.0f}%)",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
                fontweight="bold", color="#333")


def main():
    cols = [("R&H — bias = attention", rh_traces("cued"), rh_traces("uncued")),
            ("S&B — bias = adaptation", sb_traces("cued"), sb_traces("uncued"))]
    rows = [("drive", "Stimulus drive  $E$"),
            ("supp",  "Suppressive drive  $I$"),
            ("resp",  "Population response  $R$")]

    fig, axes = plt.subplots(3, 2, figsize=(11.5, 8.6), sharex=True)
    for j, (ctitle, dc, du) in enumerate(cols):
        for i, (rkey, ylabel) in enumerate(rows):
            _panel(axes[i, j], dc[rkey], du[rkey],
                   ylabel if j == 0 else None,
                   title=ctitle if i == 0 else None,
                   annotate=(rkey == "resp"))

    for ax in axes[2, :]:
        ax.set_xlabel("time  (ms)")
    axes[0, 1].legend(fontsize=9.5, loc="upper left")
    fig.suptitle("Key non-constant variables over time — R&H vs S&B  "
                 "(same normalization circuit, different bias source)",
                 fontsize=12.5, fontweight="bold", y=0.975)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig("model_traces_compare.png", dpi=160, facecolor="white")
    plt.close(fig)

    # console verification against the original S&B detector numbers
    sc, su = sb_traces("cued"), sb_traces("uncued")
    win = (T >= T_TRANS_START) & (T < T_TRANS_END)
    pc, pu = sc["resp"][win].max(), su["resp"][win].max()
    print(f"wrote model_traces_compare.png")
    print(f"  S&B detector: cued {pc:.1f}, uncued {pu:.1f}, "
          f"bias +{(pc/pu-1)*100:.1f}%  (should match row_cascade 61/46, +32.9%)")


if __name__ == "__main__":
    main()
