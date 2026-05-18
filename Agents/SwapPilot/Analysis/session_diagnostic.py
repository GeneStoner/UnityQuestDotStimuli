"""
session_diagnostic.py
Detailed response-direction analysis for two Ap35_80ms sessions.
Shows polar error distributions + accuracy bars side by side.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

OUT = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"

def load_and_prep(path):
    df = pd.read_csv(path, sep="\t")
    df = df[df["RespDeg"] != -1].copy()
    df["err"] = (((df["RespDeg"] - df["TransDeg"]) + 360) % 360).apply(
        lambda d: d if d <= 180 else d - 360)
    df["Correct"] = (df["RespDeg"] == df["TransDeg"]).astype(float)
    return df

s1 = load_and_prep("/tmp/quest_pull_sb35_80ms_v2/vr_dots_session_260501_1420.tsv")
s2 = load_and_prep("/tmp/quest_pull_sb35_80ms_v2/vr_dots_session_260501_1608.tsv")

SESSIONS = [("Session 1  14:20", s1), ("Session 2  16:08", s2)]
SWAPS    = ["N", "MC"]
CONDS    = ["CUED", "UNCUED"]
ERRORS   = [-180, -135, -90, -45, 0, 45, 90, 135, 180]   # 8-AFC bins (±22.5° each)
ANGLES   = np.radians(ERRORS)

COND_COL = {"CUED": "#1a3a6b", "UNCUED": "#7a2020"}
SWAP_COL = {"N": "#2ca02c", "MC": "#1f77b4"}

# ── layout: 3 rows × 4 cols ───────────────────────────────────────────────────
# Row 0: accuracy bars (one per session × swap)
# Row 1-2: polar error histograms (session × cond × swap)

fig = plt.figure(figsize=(16, 14), facecolor="white")
fig.patch.set_facecolor("white")

gs_outer = gridspec.GridSpec(3, 1, figure=fig,
                              height_ratios=[1.0, 2.2, 2.2],
                              hspace=0.45,
                              left=0.06, right=0.97, top=0.93, bottom=0.04)

# ── Row 0: accuracy bars ──────────────────────────────────────────────────────

ax_bar = fig.add_subplot(gs_outer[0])
ax_bar.set_facecolor("white")
ax_bar.spines["top"].set_visible(False)
ax_bar.spines["right"].set_visible(False)

labels  = ["S1 N", "S1 MC", "S2 N", "S2 MC"]
x       = np.array([0, 1, 3, 4])
width   = 0.38

for xi, (sess_label, df), sw in zip([0,1,3,4],
    [(l,d) for l,d in SESSIONS for _ in SWAPS],
    SWAPS * 2):
    for ci, cond in enumerate(CONDS):
        sub = df[(df["SwapType"]==sw) & (df["Cond"]==cond)]
        pct = sub["Correct"].mean() * 100
        col = COND_COL[cond]
        off = -width/2 if cond=="CUED" else width/2
        ax_bar.bar(xi + off, pct, width=width, color=col, alpha=0.82)
        ax_bar.text(xi + off, pct + 1.2, f"{pct:.1f}",
                    ha="center", va="bottom", fontsize=8, color=col)

ax_bar.axhline(12.5, color="#aaa", ls="--", lw=1)
ax_bar.set_xticks([0, 1, 3, 4])
ax_bar.set_xticklabels(["S1\nN", "S1\nMC", "S2\nN", "S2\nMC"], fontsize=11)
ax_bar.set_ylabel("% Correct", fontsize=11)
ax_bar.set_ylim(0, 105)
ax_bar.set_xlim(-0.8, 4.8)

# divider between sessions
ax_bar.axvline(2, color="#bbb", ls=":", lw=1.5)

# delta annotations
for xi, (sess_label, df), sw in zip([0,1,3,4],
    [(l,d) for l,d in SESSIONS for _ in SWAPS],
    SWAPS * 2):
    c = df[(df["SwapType"]==sw)&(df["Cond"]=="CUED")]["Correct"].mean()*100
    u = df[(df["SwapType"]==sw)&(df["Cond"]=="UNCUED")]["Correct"].mean()*100
    ax_bar.text(xi, 97, f"Δ={c-u:+.1f}pp", ha="center", fontsize=9,
                fontweight="bold", color=SWAP_COL[sw])

leg = [plt.Rectangle((0,0),1,1, color=COND_COL["CUED"],   alpha=0.82, label="CUED"),
       plt.Rectangle((0,0),1,1, color=COND_COL["UNCUED"], alpha=0.82, label="UNCUED")]
ax_bar.legend(handles=leg, fontsize=10, loc="upper left", framealpha=0.9)
ax_bar.set_title("Accuracy by condition  (S1=14:20, S2=16:08)", fontsize=12,
                 fontweight="bold", pad=6)

# ── Rows 1-2: polar response-error histograms ─────────────────────────────────

for row_idx, (sess_label, df) in enumerate(SESSIONS):
    gs_inner = gridspec.GridSpecFromSubplotSpec(
        1, 4, subplot_spec=gs_outer[row_idx+1], wspace=0.35)

    col_idx = 0
    for sw in SWAPS:
        for cond in CONDS:
            sub = df[(df["SwapType"]==sw) & (df["Cond"]==cond)]
            errs = sub["err"].values

            # bin into 8 directions (±22.5° windows centred on multiples of 45)
            bins = np.arange(-180-22.5, 180+22.5+1, 45)
            counts, _ = np.histogram(errs, bins=bins)
            # merge -180 and +180 bins (same direction)
            counts[0] += counts[-1]
            counts = counts[:-1]   # now 8 bins: -180,-135,...,135
            angles_plot = np.radians(np.arange(-180, 180, 45))

            ax = fig.add_subplot(gs_inner[col_idx], polar=True)
            ax.set_facecolor("#f9f9f9")

            bar_col = SWAP_COL[sw]
            alpha   = 0.85 if cond=="CUED" else 0.55
            bars = ax.bar(angles_plot, counts,
                          width=np.radians(40), bottom=0,
                          color=bar_col, alpha=alpha, edgecolor="white", lw=0.8)

            # highlight 0-error bar in gold
            zero_idx = list(np.arange(-180,180,45)).index(0)
            bars[zero_idx].set_facecolor("#d4ac0d")
            bars[zero_idx].set_alpha(0.92)

            ax.set_theta_zero_location("E")
            ax.set_theta_direction(1)
            ax.set_xticks(np.radians([0, 45, 90, 135, 180, 225, 270, 315]))
            ax.set_xticklabels(["0°","45°","90°","135°","±180°",
                                  "−135°","−90°","−45°"], fontsize=6.5)
            ax.set_yticks([])
            max_c = max(counts)
            ax.set_ylim(0, max_c * 1.25)

            # annotate correct count
            pct = sub["Correct"].mean()*100
            ax.text(0, max_c*1.15, f"{pct:.1f}%",
                    ha="center", va="center", fontsize=9,
                    fontweight="bold", color=COND_COL[cond])

            ax.set_title(f"{sw}  {cond}\n(n={len(sub)})",
                         fontsize=9, fontweight="bold", pad=8,
                         color=COND_COL[cond])

            col_idx += 1

    # session row label
    fig.text(0.01, [0.62, 0.30][row_idx], sess_label,
             va="center", ha="left", fontsize=11, fontweight="bold",
             rotation=90, color="#333")

fig.suptitle(
    "StonerBlanc_Ap35_80ms — Response direction analysis\n"
    "Polar plots: response error relative to TransDeg  |  gold bar = correct (0° error)  "
    "|  % shown = exact-match accuracy (8AFC)",
    fontsize=11, y=0.995, va="top", color="#333")

fig.savefig(f"{OUT}/session_diagnostic_ap35_80ms.png", dpi=150,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{OUT}/session_diagnostic_ap35_80ms.pdf",
            bbox_inches="tight", facecolor="white")
print("Saved session_diagnostic_ap35_80ms.png / .pdf")
