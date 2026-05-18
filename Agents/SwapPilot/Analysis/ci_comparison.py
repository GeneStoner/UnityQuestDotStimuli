"""
ci_comparison.py
Shows two types of confidence intervals on the Δpp estimates:
  (A) Binomial CI  — treats all trials as independent
  (B) Session CI   — treats sessions as the replication unit (t-distribution)

These answer different questions:
  Binomial CI: "How precisely have I estimated the mean of THIS pooled dataset?"
  Session CI:  "How much would this estimate shift if I ran different sessions?"

For a single-observer paradigm, Session CI is the correct one for
generalising beyond the specific sessions collected.
"""
import glob, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

OUT = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"

# ── helpers ───────────────────────────────────────────────────────────────────

def find_tsv(bn):
    hits = glob.glob(f"/tmp/**/{bn}", recursive=True)
    return hits[0] if hits else None

def load(bn):
    return pd.read_csv(find_tsv(bn), sep="\t")

def add_correct(df):
    df = df.copy()
    df["Correct"] = (df["RespDeg"] == df["TransDeg"]).astype(float)
    return df

def flip_db(df):
    df = df.copy()
    m = df["SwapType"] == "Db"
    df.loc[m, "Cond"] = df.loc[m, "Cond"].map({"CUED": "UNCUED", "UNCUED": "CUED"})
    return df

def sess_delta(sdf, sw):
    sub = sdf[sdf["SwapType"] == sw]
    if not len(sub): return None
    c = sub[sub["Cond"]=="CUED"]["Correct"]
    u = sub[sub["Cond"]=="UNCUED"]["Correct"]
    return (c.mean() - u.mean()) * 100, len(c), len(u)

def binomial_ci(deltas_info):
    """95% CI on pooled delta using normal approximation (all trials independent)."""
    all_c = np.concatenate([d[0] for d in deltas_info])
    all_u = np.concatenate([d[1] for d in deltas_info])
    p1, p2 = all_c.mean(), all_u.mean()
    delta  = (p1 - p2) * 100
    pp = (all_c.sum() + all_u.sum()) / (len(all_c) + len(all_u))
    se = math.sqrt(pp*(1-pp)*(1/len(all_c)+1/len(all_u))) * 100 if 0<pp<1 else 0
    ci_half = 1.96 * se
    return delta, ci_half, len(all_c), len(all_u)

def session_ci(sess_deltas):
    """95% CI based on between-session variability (t-distribution, df=n-1)."""
    vals = [v for v in sess_deltas if v is not None]
    n    = len(vals)
    mean = np.mean(vals)
    if n < 2:
        return mean, None, n   # no CI possible
    sd   = np.std(vals, ddof=1)
    se   = sd / math.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=n-1)
    return mean, t_crit * se, n

# ── load data ─────────────────────────────────────────────────────────────────

sess_ce = [flip_db(add_correct(load("vr_dots_session_260427_0707.tsv"))),
           flip_db(add_correct(load("vr_dots_session_260427_1003.tsv"))),
           flip_db(add_correct(load("vr_dots_session_260427_1217.tsv")))]

sess_sb20 = [add_correct(load("vr_dots_session_260430_1312.tsv")),
             add_correct(load("vr_dots_session_260430_1512.tsv"))]

sess_sb35 = [add_correct(load("vr_dots_session_260501_0752.tsv")),
             add_correct(load("vr_dots_session_260501_0949.tsv"))]

sess_sb35_80 = [add_correct(load("vr_dots_session_260501_1420.tsv")),
                add_correct(load("vr_dots_session_260501_1608.tsv"))]

sess_dense = [add_correct(load("vr_dots_session_260423_1053.tsv"))]

DATASETS = [
    ("CatekExact\nAp 1.65°",     sess_ce,      "Db"),
    ("S&B Repl.\nAp 2.0°",       sess_sb20,    "MC"),
    ("S&B Ap 3.5°\n44 ms",       sess_sb35,    "MC"),
    ("S&B Ap 3.5°\n80 ms",       sess_sb35_80, "MC"),
    ("DenseCM\nAp 3.5°",         sess_dense,   "MC"),
]

COND_COLORS = {"N": "#2ca02c", "SW": "#1f77b4"}
SESS_COLORS = ["#e67e22", "#8e44ad", "#16a085", "#c0392b", "#2980b9"]

# ── compute ───────────────────────────────────────────────────────────────────

rows = []   # one entry per (dataset, condition)
for ds_label, sess_list, swap_key in DATASETS:
    for cond_key, cond_label in [("N", "N"), ("SW", swap_key.replace("Db","Db≡MC"))]:
        sk = "N" if cond_key == "N" else swap_key

        # per-session delta values
        s_deltas = []
        s_raw    = []   # (cued_arr, uncued_arr) for binomial CI
        for sdf in sess_list:
            result = sess_delta(sdf, sk)
            if result is None:
                s_deltas.append(None)
            else:
                d, nc, nu = result
                s_deltas.append(d)
                sub = sdf[sdf["SwapType"]==sk]
                s_raw.append((sub[sub["Cond"]=="CUED"]["Correct"].values,
                               sub[sub["Cond"]=="UNCUED"]["Correct"].values))

        binom_delta, binom_half, nc_tot, nu_tot = binomial_ci(s_raw)
        sess_mean, sess_half, n_sess = session_ci(s_deltas)

        rows.append(dict(
            ds_label=ds_label, cond_key=cond_key, cond_label=cond_label,
            binom_delta=binom_delta, binom_half=binom_half,
            sess_mean=sess_mean, sess_half=sess_half,
            n_sess=n_sess, nc_tot=nc_tot, nu_tot=nu_tot,
            s_deltas=[v for v in s_deltas if v is not None],
        ))

# ── figure ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(16, 9), facecolor="white",
                         gridspec_kw=dict(wspace=0.08, left=0.22, right=0.97,
                                          top=0.88, bottom=0.18))

titles = ["(A)  Binomial 95% CI\n(treats all trials as independent)",
          "(B)  Session-based 95% CI\n(treats each session as one observation)"]

XLIM   = (-30, 70)
ROW_H  = 1.0
DS_GAP = 0.6
BAR_H  = 0.42

# build y layout
y_centers = []
ds_midpoints = {}
y = 0.0
prev_ds = None
for r in rows:
    if r["ds_label"] != prev_ds:
        if prev_ds is not None:
            y += DS_GAP
        prev_ds = r["ds_label"]
    y_centers.append(y)
    ds_midpoints.setdefault(r["ds_label"], []).append(y)
    y += ROW_H

total_y = y

shades = ["#f0f4ff", "#fff8ee", "#f0fff0", "#e8f8ff", "#ffeef8"]
ds_list = list(dict.fromkeys(r["ds_label"] for r in rows))

for ax_idx, ax in enumerate(axes):
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(*XLIM)
    ax.set_ylim(-0.6, total_y + 0.4)
    ax.invert_yaxis()
    ax.axvline(0, color="black", lw=1.2, zorder=2)
    ax.set_xlabel("CUED − UNCUED  (Δpp)", fontsize=12, labelpad=8)
    ax.set_title(titles[ax_idx], fontsize=12, fontweight="bold",
                 pad=10, loc="center")
    ax.tick_params(axis="x", labelsize=11)

    # shaded dataset bands
    for ds_i, ds in enumerate(ds_list):
        ys = ds_midpoints[ds]
        ax.axhspan(ys[0]-0.35, ys[-1]+0.35, color=shades[ds_i], alpha=0.65, zorder=0)

    # dataset labels (left panel only)
    if ax_idx == 0:
        for ds_i, ds in enumerate(ds_list):
            ys = ds_midpoints[ds]
            ymid = np.mean(ys)
            ax.text(-0.28, ymid, ds,
                    ha="left", va="center", fontsize=9.5, fontweight="bold",
                    linespacing=1.4, transform=ax.get_yaxis_transform(), clip_on=False)

    # y-tick labels
    ax.set_yticks(y_centers)
    ax.set_yticklabels([r["cond_label"] for r in rows],
                       fontsize=11, fontweight="bold")
    if ax_idx == 1:
        ax.set_yticklabels([])

    for yi, r in zip(y_centers, rows):
        col = COND_COLORS[r["cond_key"]]

        if ax_idx == 0:
            # Binomial CI
            delta = r["binom_delta"]
            half  = r["binom_half"]
            ax.barh(yi, delta, height=BAR_H, color=col, alpha=0.80, zorder=3)
            ax.errorbar(delta, yi, xerr=half, fmt="none",
                        color="black", lw=2.0, capsize=5, capthick=1.8, zorder=5)
            # annotation
            n_txt = f"n={r['nc_tot']+r['nu_tot']} trials"
            ax.text(delta + (half+1.5 if delta>=0 else -half-1.5), yi,
                    f"±{half:.1f}pp\n{n_txt}",
                    ha="left" if delta>=0 else "right",
                    va="center", fontsize=8.5, color="#333", zorder=6)

        else:
            # Session CI
            delta = r["sess_mean"]
            half  = r["sess_half"]
            n_s   = r["n_sess"]
            ax.barh(yi, delta, height=BAR_H, color=col, alpha=0.80, zorder=3)

            # individual session dots
            s_vals = r["s_deltas"]
            jitter = np.linspace(-BAR_H*0.25, BAR_H*0.25, len(s_vals)) if len(s_vals)>1 else [0]
            for si, (sv, jit) in enumerate(zip(s_vals, jitter)):
                ax.plot(sv, yi+jit, "o", color="white", markersize=6.5, zorder=7)
                ax.plot(sv, yi+jit, "o", color=SESS_COLORS[si],
                        markersize=5.5, zorder=8, alpha=0.95,
                        markeredgecolor="black", markeredgewidth=0.6)

            if half is not None:
                ax.errorbar(delta, yi, xerr=half, fmt="none",
                            color="black", lw=2.0, capsize=5, capthick=1.8, zorder=6)
                df_val = n_s - 1
                t_crit = stats.t.ppf(0.975, df=df_val)
                ax.text(delta + (half+1.5 if delta>=0 else -half-1.5), yi,
                        f"±{half:.1f}pp\n(n={n_s} sess, t={t_crit:.1f})",
                        ha="left" if delta>=0 else "right",
                        va="center", fontsize=8.5, color="#333", zorder=9)
            else:
                ax.text(delta + 1.5, yi,
                        f"n=1 sess\n(no CI)", ha="left", va="center",
                        fontsize=8.5, color="#888", style="italic", zorder=9)

# ── shared legend ─────────────────────────────────────────────────────────────

leg_handles = [
    mpatches.Patch(color=COND_COLORS["N"],  label="N  (no swap)"),
    mpatches.Patch(color=COND_COLORS["SW"], label="MC / Db≡MC"),
    plt.Line2D([0],[0], color="black", lw=2, marker="|", markersize=8,
               markeredgewidth=2, label="95% CI"),
]
for si in range(3):
    leg_handles.append(
        plt.Line2D([0],[0], marker="o", color="w",
                   markerfacecolor=SESS_COLORS[si],
                   markeredgecolor="black", markeredgewidth=0.6,
                   markersize=7, label=f"Session {si+1}"))

axes[1].legend(handles=leg_handles, fontsize=9.5, loc="lower right",
               framealpha=0.92, title="Legend", title_fontsize=10)

# ── interpretation box ────────────────────────────────────────────────────────

interpretation = (
    "How to read these plots:\n\n"
    "(A) Binomial CI  answers: 'Is the cueing effect different from 0 in this pooled dataset?'\n"
    "     — Narrow because it assumes all N≈200–500 trials are independent observations.\n"
    "     — Correct for a null-hypothesis test against chance, but ignores session-to-session noise.\n\n"
    "(B) Session CI  answers: 'Would a new session likely show the same effect?'\n"
    "     — Each session is treated as one data point (the correct unit for a single observer).\n"
    "     — t-critical for n=2 sessions is 12.7; for n=3 sessions is 4.3 → CIs are wide.\n"
    "     — Wide CI = genuine uncertainty; a few unusual sessions dominate the estimate.\n"
    "     — This is the CI to report when comparing two different parameter conditions\n"
    "       collected in separate sessions."
)

fig.text(0.03, 0.13, interpretation,
         ha="left", va="top", fontsize=9.5,
         fontfamily="monospace",
         bbox=dict(boxstyle="round,pad=0.6", fc="#f8f8f8", ec="#aaa", lw=1.2))

fig.suptitle(
    "VRDots — Confidence Intervals: Binomial (trial-level) vs Session-based (replication-level)\n"
    "Both show 95% CI  |  session dots = individual session Δpp  |  bars = mean of pooled (A) or sessions (B)",
    fontsize=11, y=0.975, va="top", color="#333")

fig.savefig(f"{OUT}/ci_comparison.png", dpi=150,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{OUT}/ci_comparison.pdf",
            bbox_inches="tight", facecolor="white")
print("Saved ci_comparison.png / .pdf")
