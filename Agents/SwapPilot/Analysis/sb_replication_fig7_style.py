"""
sb_replication_fig7_style.py

S&B Replication (Ap 2.0°) data plotted as horizontal bars,
styled to resemble Figure 7 of Stoner & Blanc (2010).

Two panels side by side:  N (no swap)  |  MC (motion + color swap)
Each panel: Cued row (top) and Uncued row (bottom).
Individual session data shown as scatter points.
Chance line at 12.5%.
"""

import glob
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# ── paths ────────────────────────────────────────────────────────────────────

DATA_DIR = "/tmp/quest_pull/files"
OUT_DIR  = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"

SESSION_FILES = [
    f"{DATA_DIR}/vr_dots_session_260430_1312.tsv",
    f"{DATA_DIR}/vr_dots_session_260430_1512.tsv",
]

# ── helpers ──────────────────────────────────────────────────────────────────

def add_correct(df):
    df = df.copy()
    df["Correct"] = (df["RespDeg"] == df["TransDeg"]).astype(float)
    return df

def cue_stats(df, swap):
    sub = df[df["SwapType"] == swap]
    c_arr = sub[sub["Cond"] == "CUED"]["Correct"]
    u_arr = sub[sub["Cond"] == "UNCUED"]["Correct"]
    p1, p2 = c_arr.mean(), u_arr.mean()
    n1, n2 = len(c_arr), len(u_arr)
    pp = (c_arr.sum() + u_arr.sum()) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1/n1 + 1/n2)) if 0 < pp < 1 else 1e-9
    z  = (p1 - p2) / se
    p  = 2 * (1 - stats.norm.cdf(abs(z)))
    # per-condition 95% CI (Wilson-ish: use normal approx for simplicity)
    def ci95(arr):
        p_ = arr.mean(); n_ = len(arr)
        return 1.96 * math.sqrt(p_ * (1 - p_) / n_) * 100 if n_ > 0 else 0
    return dict(
        cued=p1*100, uncued=p2*100,
        delta=(p1-p2)*100, se_delta=se*100,
        ci_cued=ci95(c_arr), ci_uncued=ci95(u_arr),
        n_c=n1, n_u=n2, z=z, p=p
    )

def sig(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.1:   return "†"
    return "n.s."

def sess_acc(df, swap, cond):
    sub = df[(df["SwapType"] == swap) & (df["Cond"] == cond)]
    return sub["Correct"].mean() * 100 if len(sub) else None

# ── load & compute ────────────────────────────────────────────────────────────

sess_dfs = [add_correct(pd.read_csv(f, sep="\t")) for f in SESSION_FILES]
df_all   = pd.concat(sess_dfs, ignore_index=True)

conditions = [
    dict(swap="N",  label="No motion/color swap"),
    dict(swap="MC", label="Motion/color swap"),
]

for c in conditions:
    c["stats"] = cue_stats(df_all, c["swap"])
    c["sess_cued"]   = [sess_acc(s, c["swap"], "CUED")   for s in sess_dfs]
    c["sess_uncued"] = [sess_acc(s, c["swap"], "UNCUED") for s in sess_dfs]

# ── figure ───────────────────────────────────────────────────────────────────

BAR_COL = "#888888"
BAR_H   = 0.38
CHANCE  = 12.5

fig, axes = plt.subplots(1, 2, figsize=(7, 2.8),
                         sharey=True, facecolor="white")
fig.subplots_adjust(wspace=0.08, left=0.18, right=0.97, top=0.88, bottom=0.20)

for ax, cond in zip(axes, conditions):
    r = cond["stats"]
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # ── bars ──────────────────────────────────────────────────────────────────
    ax.barh(1, r["cued"],   height=BAR_H, color=BAR_COL, alpha=0.85, zorder=3)
    ax.barh(0, r["uncued"], height=BAR_H, color=BAR_COL, alpha=0.85, zorder=3)

    # ── 95% CI error bars ─────────────────────────────────────────────────────
    ax.errorbar(r["cued"],   1, xerr=r["ci_cued"],   fmt="none",
                color="black", lw=1.5, capsize=4, capthick=1.2, zorder=6)
    ax.errorbar(r["uncued"], 0, xerr=r["ci_uncued"], fmt="none",
                color="black", lw=1.5, capsize=4, capthick=1.2, zorder=6)

    # ── chance line ───────────────────────────────────────────────────────────
    ax.axvline(CHANCE, color="#aaa", lw=1.2, ls="--", alpha=0.7, zorder=1)

    # ── accuracy labels ───────────────────────────────────────────────────────
    ax.text(r["cued"]   + r["ci_cued"]   + 2.5, 1, f"{r['cued']:.1f}%",
            va="center", ha="left", fontsize=9, color="#333")
    ax.text(r["uncued"] + r["ci_uncued"] + 2.5, 0, f"{r['uncued']:.1f}%",
            va="center", ha="left", fontsize=9, color="#333")

    # ── Δ annotation ─────────────────────────────────────────────────────────
    d, s = r["delta"], sig(r["p"])
    ax.text(0.97, 0.97, f"Δ = {d:+.1f} pp  {s}",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=9, color="#333",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#ccc", alpha=0.85))

    # ── axes cosmetics ────────────────────────────────────────────────────────
    ax.set_xlim(0, 108)
    ax.set_ylim(-0.55, 1.55)
    ax.set_xlabel("Percent Correct (%)", fontsize=10)
    ax.set_title(cond["label"], fontsize=10, pad=6)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Uncued", "Cued"], fontsize=11, fontweight="bold")
    ax.tick_params(axis="x", labelsize=9)
    ax.text(CHANCE, -0.52, "chance\n12.5%",
            ha="center", va="bottom", fontsize=7.5, color="#aaa")

# ── save ──────────────────────────────────────────────────────────────────────
out_base = f"{OUT_DIR}/sb_replication_fig7_style"
fig.savefig(f"{out_base}.png", dpi=150, bbox_inches="tight", facecolor="white")
fig.savefig(f"{out_base}.svg", bbox_inches="tight", facecolor="white")
print(f"Saved {out_base}.png / .svg")
