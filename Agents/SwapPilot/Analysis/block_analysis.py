"""
block_analysis.py
Within-session block analysis: split each session into 4 sequential blocks,
compute delta (CUED - UNCUED) per block for N and MC/Db conditions.
Shows intra-session drift and compares to inter-session spread.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import glob, math
from scipy import stats

OUT = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"

def find_tsv(bn):
    hits = glob.glob(f"/tmp/**/{bn}", recursive=True)
    return hits[0] if hits else None

def load(bn):
    return pd.read_csv(find_tsv(bn), sep="\t")

def add_correct(df):
    df = df.copy()
    df["Correct"] = (((df["RespDeg"] - df["TransDeg"]) + 360) % 360).apply(
        lambda d: d if d <= 180 else d - 360).abs() <= 67.5
    return df

def flip_db(df):
    df = df.copy()
    m = df["SwapType"] == "Db"
    df.loc[m, "Cond"] = df.loc[m, "Cond"].map({"CUED": "UNCUED", "UNCUED": "CUED"})
    return df

def block_deltas(df, swap, n_blocks=4):
    """Split trials of given swap type into n_blocks sequential blocks, return delta per block."""
    sub = df[df["SwapType"] == swap].copy().reset_index(drop=True)
    if len(sub) < n_blocks * 4:
        return None, None, None
    block_size = len(sub) // n_blocks
    deltas, ses, ns = [], [], []
    for b in range(n_blocks):
        chunk = sub.iloc[b*block_size : (b+1)*block_size]
        c = chunk[chunk["Cond"] == "CUED"]["Correct"]
        u = chunk[chunk["Cond"] == "UNCUED"]["Correct"]
        if not len(c) or not len(u):
            deltas.append(np.nan); ses.append(np.nan); ns.append(0)
            continue
        p1, p2 = c.mean(), u.mean()
        delta = (p1 - p2) * 100
        # binomial SE on delta
        pp = (c.sum() + u.sum()) / (len(c) + len(u))
        se = math.sqrt(pp*(1-pp)*(1/len(c)+1/len(u))) * 100 if 0 < pp < 1 else 0
        deltas.append(delta); ses.append(se); ns.append(len(c)+len(u))
    return np.array(deltas), np.array(ses), np.array(ns)

# ── session registry ──────────────────────────────────────────────────────────
# (dataset_label, session_label, filename, swap_key, needs_flip)

SESSIONS = [
    # CatekExact (SubfieldSwap_CatekExact_v1 only; 1217 excluded — NDb_v1 different asset)
    ("CatekExact\nAp 1.65°",  "0707", "vr_dots_session_260427_0707.tsv", "Db", True),
    ("CatekExact\nAp 1.65°",  "1003", "vr_dots_session_260427_1003.tsv", "Db", True),
    # S&B Ap2.0
    ("S&B Replication\nAp 2.0°", "1312", "vr_dots_session_260430_1312.tsv", "MC", False),
    ("S&B Replication\nAp 2.0°", "1512", "vr_dots_session_260430_1512.tsv", "MC", False),
    # S&B Ap3.5 44ms
    ("S&B Ap 3.5°\n44 ms",    "0752", "vr_dots_session_260501_0752.tsv", "MC", False),
    ("S&B Ap 3.5°\n44 ms",    "0949", "vr_dots_session_260501_0949.tsv", "MC", False),
    # S&B Ap3.5 80ms
    ("S&B Ap 3.5°\n80 ms",    "1420", "vr_dots_session_260501_1420.tsv", "MC", False),
    ("S&B Ap 3.5°\n80 ms",    "1608", "vr_dots_session_260501_1608.tsv", "MC", False),
    # DenseCM
    ("DenseCM\nAp 3.5°",      "1053", "vr_dots_session_260423_1053.tsv", "MC", False),
]

# ── load and compute ──────────────────────────────────────────────────────────

data = []
for ds_label, sess_label, bn, swap_key, do_flip in SESSIONS:
    df = add_correct(load(bn))
    if do_flip:
        df = flip_db(df)
    dn, se_n, nn = block_deltas(df, "N")
    ds, se_s, ns = block_deltas(df, swap_key)
    swap_disp = "Db≡MC" if swap_key == "Db" else "MC"
    data.append(dict(ds_label=ds_label, sess_label=sess_label,
                     swap_disp=swap_disp,
                     delta_N=dn, se_N=se_n, n_N=nn,
                     delta_SW=ds, se_SW=se_s, n_SW=ns))

# ── figure ────────────────────────────────────────────────────────────────────

DATASETS = sorted(set(d["ds_label"] for d in data),
                  key=lambda x: ["CatekExact\nAp 1.65°",
                                 "S&B Replication\nAp 2.0°",
                                 "S&B Ap 3.5°\n44 ms",
                                 "S&B Ap 3.5°\n80 ms",
                                 "DenseCM\nAp 3.5°"].index(x))

N_DS   = len(DATASETS)
N_BLOCKS = 4
BLOCK_X  = np.arange(1, N_BLOCKS + 1)

# Session colours — consistent within a dataset
SESS_PALETTE = ["#e74c3c", "#3498db", "#27ae60", "#f39c12", "#9b59b6"]

fig, axes = plt.subplots(N_DS, 2, figsize=(14, 3.2 * N_DS),
                         facecolor="white", sharex=True)
fig.subplots_adjust(hspace=0.55, wspace=0.30,
                    left=0.10, right=0.97, top=0.94, bottom=0.04)

for row, ds_label in enumerate(DATASETS):
    sess_data = [d for d in data if d["ds_label"] == ds_label]

    for col, (key, label_str) in enumerate([("delta_N", "N  (no swap)"),
                                             ("delta_SW", "MC / Db≡MC")]):
        ax = axes[row, col]
        ax.set_facecolor("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.axhline(0, color="#bbb", lw=1, ls="--")

        # grey band = ±1 binomial SE expected at typical n~32/condition
        # just show reference SE range with a shaded region
        ref_se = 5.7   # sqrt(2)*SE ≈ sqrt(2)*0.04*100 for p≈0.7, n≈32
        ax.axhspan(-ref_se, ref_se, color="#ddd", alpha=0.35, zorder=0,
                   label="±1 binomial SE (n≈32/cond)")

        for si, sd in enumerate(sess_data):
            deltas = sd[key]
            ses    = sd["se_" + key.split("_")[1]]
            if deltas is None:
                continue
            col_s = SESS_PALETTE[si % len(SESS_PALETTE)]
            ax.errorbar(BLOCK_X, deltas, yerr=ses,
                        fmt="-o", color=col_s, lw=1.8, markersize=5,
                        capsize=3, capthick=1.2, alpha=0.88,
                        label=sd["sess_label"])
            # annotate session mean
            mean_d = np.nanmean(deltas)
            ax.axhline(mean_d, color=col_s, lw=0.8, ls=":", alpha=0.5)

        ax.set_xlim(0.5, N_BLOCKS + 0.5)
        ax.set_xticks(BLOCK_X)
        ax.set_xticklabels([f"B{i}" for i in BLOCK_X], fontsize=9)
        ax.set_ylabel("Δpp  (CUED−UNCUED)", fontsize=9)
        ax.set_ylim(-45, 65)
        ax.axhline(0, color="black", lw=0.8)

        # inter-session SD annotation
        all_means = [np.nanmean(sd[key]) for sd in sess_data if sd[key] is not None]
        if len(all_means) > 1:
            isd = np.std(all_means, ddof=1)
            ax.text(0.97, 0.97, f"inter-sess SD={isd:.1f}pp",
                    transform=ax.transAxes, ha="right", va="top",
                    fontsize=8, color="#555",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7))

        cond_col = "#2ca02c" if key == "delta_N" else "#1f77b4"
        ax.set_title(f"{label_str}", fontsize=10, fontweight="bold",
                     color=cond_col, pad=4)

        if col == 0:
            ax.text(-0.22, 0.5, ds_label, transform=ax.transAxes,
                    ha="right", va="center", fontsize=9.5, fontweight="bold",
                    linespacing=1.4)

        if row == 0:
            leg = ax.legend(title="session", fontsize=8, title_fontsize=8,
                            loc="upper left", framealpha=0.85,
                            handlelength=1.5)
        elif row == len(DATASETS)-1 and col == 0:
            # grey band legend entry once
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[:1], ["±1 binom. SE ref."],
                      fontsize=8, loc="lower left", framealpha=0.85)

fig.suptitle(
    "Within-session block analysis — cueing effect Δpp across 4 sequential blocks\n"
    "Each line = one session  |  error bars = ±1 binomial SE per block  "
    "|  grey band = ±1 SE reference (n≈32/cond)  |  dotted = session mean",
    fontsize=10.5, y=0.995, va="top", color="#333")

fig.savefig(f"{OUT}/block_analysis.png", dpi=150,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{OUT}/block_analysis.pdf",
            bbox_inches="tight", facecolor="white")
print("Saved block_analysis.png / .pdf")
