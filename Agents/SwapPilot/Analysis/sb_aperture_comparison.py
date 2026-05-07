"""
sb_aperture_comparison.py
Four-experiment comparison: CatekExact Ap1.65, S&B Ap2.0, S&B Ap3.5, DenseCM Ap3.5
Shows N and MC/Db cueing effects + absolute accuracy, with parameter table below.
Ordered by aperture size ascending, then DenseCM (matched aperture, higher density).

Aperture areas use corrected values (yaml apertureRadius_deg is a DIAMETER; ÷2 in C#).
  Ap1.65: radius=0.825°, area=2.14 deg²
  Ap2.0:  radius=1.00°,  area=3.14 deg²
  Ap3.5:  radius=1.75°,  area=9.62 deg²
"""
import glob, math
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy import stats

OUT = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"

# ── helpers ──────────────────────────────────────────────────────────────────

def find_tsv(bn):
    hits = glob.glob(f"/tmp/**/{bn}", recursive=True)
    return hits[0] if hits else None

def load(bn):
    p = find_tsv(bn)
    if not p:
        raise FileNotFoundError(f"TSV not found: {bn}")
    return pd.read_csv(p, sep="\t")

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

def cue_stats(cued_correct, uncued_correct):
    p1, p2 = cued_correct.mean(), uncued_correct.mean()
    n1, n2 = len(cued_correct), len(uncued_correct)
    pp = (cued_correct.sum() + uncued_correct.sum()) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1/n1 + 1/n2)) if pp > 0 and pp < 1 else 1e-9
    z  = (p1 - p2) / se
    p  = 2 * (1 - stats.norm.cdf(abs(z)))
    return dict(cued=p1*100, uncued=p2*100, delta=(p1-p2)*100,
                se_delta=se*100, n_c=n1, n_u=n2, z=z, p=p)

def compute_swap(df, swap):
    sub = df[df["SwapType"] == swap]
    if not len(sub):
        return None
    return cue_stats(sub[sub["Cond"]=="CUED"]["Correct"],
                     sub[sub["Cond"]=="UNCUED"]["Correct"])

def sig(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.1:   return "†"
    return "n.s."

# ── load data ─────────────────────────────────────────────────────────────────
# Per-session dfs kept separately for session-level scatter overlay

sess_ce = [
    flip_db(add_correct(load("vr_dots_session_260427_0707.tsv"))),   # SubfieldSwap_CatekExact_v1
    flip_db(add_correct(load("vr_dots_session_260427_1003.tsv"))),   # SubfieldSwap_CatekExact_v1
    # 1217 excluded: SubfieldSwap_CatekExact_NDb_v1 (different asset — N+Db only)
]
df_ce = pd.concat(sess_ce, ignore_index=True)

# MCvsDb_Ap165: MC + Db (no N baseline); same Ap1.65°, disc 0.85°, excl 0.50°
sess_mcdb_raw = [
    add_correct(load("vr_dots_session_260429_0748.tsv")),
    add_correct(load("vr_dots_session_260429_0951.tsv")),
    add_correct(load("vr_dots_session_260429_1031.tsv")),
]
sess_mcdb_db = [flip_db(s) for s in sess_mcdb_raw]
df_mcdb    = pd.concat(sess_mcdb_raw, ignore_index=True)
df_mcdb_db = pd.concat(sess_mcdb_db, ignore_index=True)

sess_sb20 = [
    add_correct(load("vr_dots_session_260430_1312.tsv")),
    add_correct(load("vr_dots_session_260430_1512.tsv")),
]
df_sb20 = pd.concat(sess_sb20, ignore_index=True)

sess_sb35 = [
    add_correct(load("vr_dots_session_260501_0752.tsv")),
    add_correct(load("vr_dots_session_260501_0949.tsv")),
]
df_sb35 = pd.concat(sess_sb35, ignore_index=True)

sess_sb35_80 = [
    add_correct(load("vr_dots_session_260501_1420.tsv")),
    add_correct(load("vr_dots_session_260501_1608.tsv")),
]
df_sb35_80 = pd.concat(sess_sb35_80, ignore_index=True)

sess_dense = [add_correct(load("vr_dots_session_260423_1053.tsv"))]
df_dense   = sess_dense[0]

sess_lf = [
    add_correct(load("vr_dots_session_260502_0638.tsv")),
    add_correct(load("vr_dots_session_260502_0729.tsv")),
]
df_lf = pd.concat(sess_lf, ignore_index=True)

# ── compute stats ─────────────────────────────────────────────────────────────
# DATASETS: list of dicts, each with 'label' and 'rows' (list of swap-row dicts).
# Each row dict: swap, disp, df (pooled for that swap), sess (per-session list).
# This supports MCvsDb showing both MC and Db rows under one dataset label.

def sess_delta(sdf, sw):
    sub = sdf[sdf["SwapType"] == sw]
    if not len(sub): return None
    c = sub[sub["Cond"]=="CUED"]["Correct"].mean()
    u = sub[sub["Cond"]=="UNCUED"]["Correct"].mean()
    return (c - u) * 100

DATASETS = [
    dict(label="CatekExact\nAp 1.65°", rows=[
        dict(swap="N",  disp="N",     df=df_ce, sess=sess_ce),
        dict(swap="Db", disp="Db≡MC", df=df_ce, sess=sess_ce),
    ]),
    dict(label="MCvsDb\nAp 1.65°", rows=[
        dict(swap="MC", disp="MC", df=df_mcdb,    sess=sess_mcdb_raw),
        dict(swap="Db", disp="Db", df=df_mcdb_db, sess=sess_mcdb_db),
    ]),
    dict(label="S&B Replication\nAp 2.0°", rows=[
        dict(swap="N",  disp="N",  df=df_sb20, sess=sess_sb20),
        dict(swap="MC", disp="MC", df=df_sb20, sess=sess_sb20),
    ]),
    dict(label="S&B Ap 3.5°\n44 ms", rows=[
        dict(swap="N",  disp="N",  df=df_sb35, sess=sess_sb35),
        dict(swap="MC", disp="MC", df=df_sb35, sess=sess_sb35),
    ]),
    dict(label="S&B Ap 3.5°\n80 ms", rows=[
        dict(swap="N",  disp="N",  df=df_sb35_80, sess=sess_sb35_80),
        dict(swap="MC", disp="MC", df=df_sb35_80, sess=sess_sb35_80),
    ]),
    dict(label="LargeFix Ap 3.5°\n44 ms", rows=[
        dict(swap="N",  disp="N",  df=df_lf, sess=sess_lf),
        dict(swap="MC", disp="MC", df=df_lf, sess=sess_lf),
    ]),
    dict(label="DenseCM\nAp 3.5°", rows=[
        dict(swap="N",  disp="N",  df=df_dense, sess=sess_dense),
        dict(swap="MC", disp="MC", df=df_dense, sess=sess_dense),
    ]),
]

def row_col(swap):
    return SWAP_COLOR["N"] if swap == "N" else SWAP_COLOR["SW"]

# compute stats for every row in every dataset
for ds in DATASETS:
    ds["n_sessions"] = len(ds["rows"][0]["sess"])
    ds["n_trials"]   = 0
    for row in ds["rows"]:
        r = compute_swap(row["df"], row["swap"])
        row["stats"]       = r
        row["sess_deltas"] = [sess_delta(s, row["swap"]) for s in row["sess"]]
        row["n_trials"]    = r["n_c"] + r["n_u"] if r else 0
        ds["n_trials"]    += row["n_trials"]

# ── figure layout ─────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(15, 15), facecolor="white")
gs  = GridSpec(2, 2, figure=fig,
               height_ratios=[3.6, 1.0],
               hspace=0.32, wspace=0.12,
               left=0.28, right=0.97, top=0.93, bottom=0.05)

ax_d = fig.add_subplot(gs[0, 0])   # Δpp
ax_a = fig.add_subplot(gs[0, 1])   # absolute accuracy
ax_t = fig.add_subplot(gs[1, :])   # parameter table

for ax in (ax_d, ax_a):
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

SWAP_COLOR = {"N": "#2ca02c", "SW": "#1f77b4"}
ROW_H  = 1.0
DS_GAP = 1.4
BAR_H  = 0.45

rows = []      # (y, ds_label, row_dict)
ds_spans = []
y = 0.0
shades = ["#f0f4ff", "#e8e4ff", "#fff8ee", "#f0fff0", "#e8f8ff", "#fff0f8", "#ffeef8"]
for i, ds in enumerate(DATASETS):
    y_top = y - 0.3
    for row in ds["rows"]:
        if row["stats"] is not None:
            rows.append((y, ds["label"], row))
            y += ROW_H
    ds_spans.append((y_top, y - ROW_H + 0.3, ds["label"], i))
    y += DS_GAP

total_y = y - DS_GAP + ROW_H

for ax in (ax_d, ax_a):
    ax.set_ylim(-0.8, total_y + 0.3)
    ax.invert_yaxis()
    for y_top, y_bot, _, i in ds_spans:
        ax.axhspan(y_top, y_bot, color=shades[i], alpha=0.70, zorder=0)
    ax.tick_params(axis="y", length=0, labelsize=11)
    ax.tick_params(axis="x", labelsize=11)

# dataset labels left of figure
for y_top, y_bot, ds_label, _ in ds_spans:
    ymid = (y_top + y_bot) / 2
    ax_d.text(-0.30, ymid, ds_label,
              ha="left", va="center", fontsize=9.5, linespacing=1.4,
              fontweight="bold",
              transform=ax_d.get_yaxis_transform(), clip_on=False)

yticks  = [r[0] + ROW_H/2 for r in rows]
ylabels = [r[2]["disp"] for r in rows]   # swap display label
for ax in (ax_d, ax_a):
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=12, fontweight="bold")
    ax.yaxis.tick_left()

# ── LEFT: Δpp ─────────────────────────────────────────────────────────────────

ax_d.set_xlim(-8, 48)
ax_d.axvline(0, color="black", lw=1.2, zorder=2)
ax_d.set_xlabel("CUED − UNCUED  (pp)", fontsize=12, labelpad=6)
ax_d.set_title("Cueing Effect  Δpp", fontsize=13, fontweight="bold", pad=8)

for y_base, _, row in rows:
    yc  = y_base + ROW_H/2
    col = row_col(row["swap"])
    r   = row["stats"]
    d   = r["delta"]
    ax_d.barh(yc, d, height=BAR_H, color=col, alpha=0.88, zorder=3, left=0)
    ci = 1.96 * r["se_delta"]
    ax_d.errorbar(d, yc, xerr=ci, fmt="none",
                  color="black", lw=1.6, capsize=4, capthick=1.3, zorder=6)
    gap = ci + 0.8 if d >= 0 else -(ci + 0.8)
    ha  = "left" if d >= 0 else "right"
    label = f"{sig(r['p'])}  {d:+.1f}pp\n(z={r['z']:.2f}, n={r['n_c']+r['n_u']})"
    ax_d.text(d + gap, yc, label,
              va="center", ha=ha, fontsize=9, color=col, zorder=4)

# per-session scatter dots + lines connecting rows within same session
dot_pos = {}   # (ds_label, sess_idx, swap) -> (x, y)
SESS_COLORS = ["#e67e22", "#8e44ad", "#16a085", "#c0392b", "#2980b9"]

for y_base, ds_label, row in rows:
    yc     = y_base + ROW_H/2
    col    = row_col(row["swap"])
    deltas = [d for d in row["sess_deltas"] if d is not None]
    if not deltas:
        continue
    jitter = np.linspace(-BAR_H*0.25, BAR_H*0.25, len(deltas))
    for i, (d_sess, jit) in enumerate(zip(deltas, jitter)):
        ax_d.plot(d_sess, yc + jit, "D", color="white",
                  markersize=7, zorder=8)
        ax_d.plot(d_sess, yc + jit, "D", color=col,
                  markersize=6, zorder=9, alpha=1.0,
                  markeredgecolor="black", markeredgewidth=0.8)
        dot_pos[(ds_label, i, row["swap"])] = (d_sess, yc + jit)

# Connect row[0] ↔ row[1] dots for same session within each dataset
for ds in DATASETS:
    if len(ds["rows"]) < 2:
        continue
    swap0 = ds["rows"][0]["swap"]
    swap1 = ds["rows"][1]["swap"]
    for i in range(ds["n_sessions"]):
        k0 = (ds["label"], i, swap0)
        k1 = (ds["label"], i, swap1)
        if k0 in dot_pos and k1 in dot_pos:
            x0, y0 = dot_pos[k0]
            x1, y1 = dot_pos[k1]
            ax_d.plot([x0, x1], [y0, y1], "-",
                      color=SESS_COLORS[i % len(SESS_COLORS)],
                      lw=1.4, alpha=0.70, zorder=5)

leg_d = [
    mpatches.Patch(color=SWAP_COLOR["N"],  label="N  (no swap)"),
    mpatches.Patch(color=SWAP_COLOR["SW"], label="MC / Db≡MC  (swap)"),
    plt.Line2D([0],[0], marker="D", color="w", markerfacecolor="#555",
               markeredgecolor="black", markersize=6, label="individual sessions"),
    plt.Line2D([0],[0], color="black", lw=1.6, marker="|", markersize=7,
               markeredgewidth=1.6, label="95% CI  (binomial)"),
]
ax_d.legend(handles=leg_d, fontsize=9.5, loc="upper center",
            bbox_to_anchor=(0.5, -0.07), ncol=2,
            title="Condition", title_fontsize=10, framealpha=0.92)

# ── RIGHT: absolute accuracy ───────────────────────────────────────────────────

ax_a.set_xlim(0, 108)
ax_a.axvline(12.5, color="#888", lw=1.2, ls="--", alpha=0.7, zorder=1)
ax_a.text(12.5, -0.55, "chance\n12.5%", ha="center", va="bottom",
          fontsize=8.5, color="#666")
ax_a.set_xlabel("% Correct", fontsize=12, labelpad=6)
ax_a.set_title("Absolute Accuracy:  CUED  vs  UNCUED", fontsize=13,
               fontweight="bold", pad=8)

BH2      = BAR_H * 0.42
STRIPE_W = 1.2

for y_base, _, row in rows:
    yc  = y_base + ROW_H/2
    col = row_col(row["swap"])
    r   = row["stats"]
    ax_a.barh(yc, STRIPE_W, height=BAR_H * 0.82, color=col,
              alpha=0.90, zorder=5, left=0)
    ax_a.barh(yc - BH2/2 - 0.02, r["cued"],   height=BH2,
              color="#1a3a6b", alpha=0.82, zorder=3)
    ax_a.barh(yc + BH2/2 + 0.02, r["uncued"], height=BH2,
              color="#7a2020", alpha=0.82, zorder=3)
    ax_a.text(r["cued"]   + 0.8, yc - BH2/2 - 0.02,
              f"{r['cued']:.1f}%", va="center", ha="left", fontsize=9.5, color="#1a3a6b")
    ax_a.text(r["uncued"] + 0.8, yc + BH2/2 + 0.02,
              f"{r['uncued']:.1f}%", va="center", ha="left", fontsize=9.5, color="#7a2020")

leg_a = [
    mpatches.Patch(color="#1a3a6b", label="CUED"),
    mpatches.Patch(color="#7a2020", label="UNCUED"),
    plt.Line2D([0],[0], color="#888", ls="--", lw=1.5, label="Chance 12.5%"),
]
ax_a.legend(handles=leg_a, fontsize=10, framealpha=0.92,
            loc="upper center", bbox_to_anchor=(0.5, -0.07),
            ncol=3, borderpad=0.8)

# ── BOTTOM: parameter table ────────────────────────────────────────────────────

ax_t.axis("off")

col_labels = [
    "Experiment", "Ap\ndiam.", "Ap area\n(deg²)",
    "Dots/\nfield", "Density\n(dots/deg²)", "Trans.\ndur.", "Swap\ncond.",
    "Fix disc\ndiam.", "Excl.\nradius", "Excl/Ap\nratio", "Sessions\n(n trials)"
]

# corrected radii: yaml value ÷ 2
A165 = math.pi * 0.825**2   # 2.14
A200 = math.pi * 1.00**2    # 3.14
A350 = math.pi * 1.75**2    # 9.62

# excl/ap ratio = exclusion_radius / aperture_radius (fraction of aperture blocked)
def ds_n(i): return DATASETS[i]["n_sessions"]
def ds_t(i): return DATASETS[i]["n_trials"]
def ds_sw(i): return "+".join(r["disp"] for r in DATASETS[i]["rows"])

table_data = [
    ["CatekExact",
     "1.65°", f"{A165:.2f}", "43", f"{43/A165:.1f}",
     "80 ms", ds_sw(0),
     "0.85°", "0.50°", f"{0.50/0.825:.2f}",
     f"{ds_n(0)}  (N={ds_t(0)})"],
    ["MCvsDb  Ap 1.65°",
     "1.65°", f"{A165:.2f}", "43", f"{43/A165:.1f}",
     "80 ms", ds_sw(1),
     "0.85°", "0.50°", f"{0.50/0.825:.2f}",
     f"{ds_n(1)}  (N={ds_t(1)})  no N baseline"],
    ["S&B Replication",
     "2.0°",  f"{A200:.2f}", "63", f"{63/A200:.1f}",
     "44 ms", ds_sw(2),
     "0.40°", "0.396°", f"{0.396/1.00:.2f}",
     f"{ds_n(2)}  (N={ds_t(2)})"],
    ["S&B  Ap 3.5°  44 ms",
     "3.5°",  f"{A350:.2f}", "192", f"{192/A350:.1f}",
     "44 ms", ds_sw(3),
     "0.40°", "0.396°", f"{0.396/1.75:.2f}",
     f"{ds_n(3)}  (N={ds_t(3)})"],
    ["S&B  Ap 3.5°  80 ms",
     "3.5°",  f"{A350:.2f}", "192", f"{192/A350:.1f}",
     "80 ms", ds_sw(4),
     "0.40°", "0.396°", f"{0.396/1.75:.2f}",
     f"{ds_n(4)}  (N={ds_t(4)})"],
    ["LargeFix Ap 3.5°",
     "3.5°",  f"{A350:.2f}", "192", f"{192/A350:.1f}",
     "44 ms", ds_sw(5),
     "1.80°", "1.10°", f"{1.10/1.75:.2f}",
     f"{ds_n(5)}  (N={ds_t(5)})"],
    ["DenseCM",
     "3.5°",  f"{A350:.2f}", "500", f"{500/A350:.1f}",
     "80 ms", ds_sw(6),
     "1.80°", "1.10°", f"{1.10/1.75:.2f}",
     f"{ds_n(6)}  (N={ds_t(6)})  no N baseline"],
]

tbl = ax_t.table(
    cellText=table_data,
    colLabels=col_labels,
    loc="center",
    cellLoc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)
tbl.scale(1.0, 2.1)

# header
FIX_COL_IDX = [7, 8, 9]   # Fix disc, Excl radius, Excl/Ap ratio columns
for j in range(len(col_labels)):
    tbl[0, j].set_facecolor("#2c3e50")
    tbl[0, j].set_text_props(color="white", fontweight="bold")
# highlight fixation columns in header
for j in FIX_COL_IDX:
    tbl[0, j].set_facecolor("#7b3f00")

row_colors = ["#f0f4ff", "#e8e4ff", "#fff8ee", "#f0fff0", "#e8f8ff", "#fff0f8", "#ffeef8"]
for i, color in enumerate(row_colors):
    for j in range(len(col_labels)):
        tbl[i+1, j].set_facecolor(color)
    # tint fixation columns
    for j in FIX_COL_IDX:
        tbl[i+1, j].set_facecolor("#fff0e0")

ax_t.set_title(
    "Experiment Parameters  —  corrected aperture area: actual radius = yaml apertureRadius_deg ÷ 2  "
    "|  Db CUED/UNCUED labels flipped to onset-cue convention  "
    "|  orange cols = fixation/exclusion zone",
    fontsize=9, color="#555", pad=4)

# ── title & save ──────────────────────────────────────────────────────────────

fig.suptitle(
    "VRDots — N vs MC/Db Cueing: Aperture, Duration & Density Comparison  (GS, 2026-05)\n"
    "Accuracy window ±67.5°  |  CatekExact uses Db (noise-half swap ≡ MC in consequence)",
    fontsize=11.5, y=0.995, va="top", color="#333")

fig.savefig(f"{OUT}/sb_aperture_comparison.png", dpi=150,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{OUT}/sb_aperture_comparison.pdf",
            bbox_inches="tight", facecolor="white")
print("Saved sb_aperture_comparison.png / .pdf")
