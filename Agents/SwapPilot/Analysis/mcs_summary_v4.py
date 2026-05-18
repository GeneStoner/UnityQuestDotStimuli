"""
MCS Summary v4 — graph page, landscape, horizontal bars.
All fixes: chance=12.5%, smaller stripe, no timestamp labels,
dataset names clear of swap labels, simple legend outside bars.
"""
import pandas as pd, numpy as np, matplotlib, glob
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

def find_tsv(bn):
    hits = glob.glob(f"/tmp/**/{bn}", recursive=True)
    return hits[0] if hits else None

def load(bn):
    p = find_tsv(bn)
    if not p: raise FileNotFoundError(bn)
    return pd.read_csv(p, sep="\t")

def add_correct(df):
    df = df.copy()
    df["Correct"] = (df["RespDeg"] == df["TransDeg"]).astype(float)
    return df

def flip_db(df):
    df = df.copy()
    m = df["SwapType"] == "Db"
    df.loc[m, "Cond"] = df.loc[m, "Cond"].map({"CUED":"UNCUED","UNCUED":"CUED"})
    return df

def cue_stats(c, u):
    p1, p2 = c.mean(), u.mean()
    n1, n2 = len(c), len(u)
    pp = (c.sum() + u.sum()) / (n1 + n2)
    se = np.sqrt(pp*(1-pp)*(1/n1+1/n2))
    z  = (p1-p2)/se if se > 0 else 0
    p  = 2*(1-stats.norm.cdf(abs(z)))
    return dict(cued=p1*100, uncued=p2*100, delta=(p1-p2)*100,
                n_c=n1, n_u=n2, z=z, p=p)

def compute(df, swaps):
    out = {}
    for sw in swaps:
        sub = df[df["SwapType"]==sw]
        if not len(sub): continue
        out[sw] = cue_stats(sub[sub["Cond"]=="CUED"]["Correct"],
                             sub[sub["Cond"]=="UNCUED"]["Correct"])
    return out

def sig(p):
    if p<0.001: return "***"
    if p<0.01:  return "**"
    if p<0.05:  return "*"
    if p<0.1:   return "†"
    return "n.s."

# ── load data ─────────────────────────────────────────────────────────────────
df_cm  = add_correct(load("vr_dots_session_260423_1053.tsv"))
df_sb  = pd.concat([add_correct(load("vr_dots_session_260430_1312.tsv")),
                    add_correct(load("vr_dots_session_260430_1512.tsv"))], ignore_index=True)
df_md  = flip_db(pd.concat([add_correct(load("vr_dots_session_260429_0748.tsv")),
                             add_correct(load("vr_dots_session_260429_0951.tsv")),
                             add_correct(load("vr_dots_session_260429_1031.tsv"))], ignore_index=True))
df_ce  = flip_db(pd.concat([add_correct(load("vr_dots_session_260427_0707.tsv")),
                             add_correct(load("vr_dots_session_260427_1003.tsv"))], ignore_index=True))
df_ndb = flip_db(add_correct(load("vr_dots_session_260427_1217.tsv")))
df_hd  = flip_db(add_correct(load("vr_dots_session_260427_1423.tsv")))

N_pool = pd.concat([df_ce[df_ce["SwapType"]=="N"],
                    df_ndb[df_ndb["SwapType"]=="N"]], ignore_index=True)

res_cm  = compute(df_cm,  ["N","MC"])
res_sb  = compute(df_sb,  ["N","MC"])
res_md  = compute(df_md,  ["MC","Db"])
res_md["N"] = cue_stats(N_pool[N_pool["Cond"]=="CUED"]["Correct"],
                         N_pool[N_pool["Cond"]=="UNCUED"]["Correct"])
res_ce  = compute(df_ce,  ["N","D","Da","Db"])
res_ndb = compute(df_ndb, ["N","Db"])
res_hd  = compute(df_hd,  ["N","D","Da","Db"])

# ── dataset definitions — no timestamps, clean labels ─────────────────────────
# Order within each group: N first, then swap conditions, Da never adjacent to N
DATASETS = [
    ("DenseCM\nAp 3.5°  500/field  80 ms",
     [("N", res_cm["N"]), ("MC", res_cm["MC"])]),

    ("S&B Replication\nAp 2.0°  63/field  44 ms",
     [("N", res_sb["N"]), ("MC", res_sb["MC"])]),

    ("MCvsDb  Ap 1.65°\n43/field  80 ms",
     [("N", res_md["N"]), ("MC", res_md["MC"]), ("Db", res_md["Db"])]),

    ("CatekExact  Ap 1.65°\n43/field  80 ms",
     [("N", res_ce["N"]), ("Db", res_ce["Db"]), ("Da", res_ce["Da"])]),

    ("CatekExact NDb  Ap 1.65°\n43/field  80 ms",
     [("N", res_ndb["N"]), ("Db", res_ndb["Db"])]),

    ("HighDens  Ap 3.5°\n173/field  80 ms",
     [("N", res_hd["N"]), ("Db", res_hd["Db"]), ("Da", res_hd["Da"])]),
]

SWAP_COLOR = {"N":"#2ca02c","MC":"#1f77b4","Db":"#d62728","D":"#9467bd","Da":"#ff7f0e"}

# ── y-axis layout: each condition = 1 unit, 1.6-unit gap between datasets ─────
ROW_H  = 1.0
DS_GAP = 1.6

rows     = []   # (y_base, ds_label, sw, result)
ds_spans = []   # (y_top, y_bot, ds_label) for shading and group labels
y = 0.0
for ds_label, conditions in DATASETS:
    y_top = y - 0.25
    for sw, r in conditions:
        rows.append((y, ds_label, sw, r))
        y += ROW_H
    ds_spans.append((y_top, y - ROW_H + 0.25, ds_label))
    y += DS_GAP

total_y = y - DS_GAP + ROW_H
BAR_H   = 0.52

# ── figure: wider left margin for dataset labels ──────────────────────────────
fig, (ax_d, ax_a) = plt.subplots(
    1, 2, figsize=(17, 11), facecolor="white",
    gridspec_kw={"width_ratios": [1, 1.55], "wspace": 0.10})
fig.patch.set_facecolor("white")
fig.subplots_adjust(left=0.22, right=0.97, top=0.91, bottom=0.08)

for ax in (ax_d, ax_a):
    ax.set_facecolor("white")
    ax.set_ylim(-0.8, total_y + 0.5)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11.5)
    ax.tick_params(axis="x", labelsize=11)

# ── alternating shading per dataset ──────────────────────────────────────────
for i, (y_top, y_bot, _) in enumerate(ds_spans):
    shade = "#eef2ff" if i % 2 == 0 else "#fff5ee"
    for ax in (ax_d, ax_a):
        ax.axhspan(y_top, y_bot, color=shade, alpha=0.60, zorder=0)

# ── dataset labels: placed to the LEFT of the figure using fig.text ───────────
# Convert each dataset's y-midpoint from data coords → figure coords
# We'll place them manually using ax_d's transform, far enough left
for i, (y_top, y_bot, ds_label) in enumerate(ds_spans):
    ymid = (y_top + y_bot) / 2
    ax_d.text(-0.32, ymid, ds_label,
              ha="left", va="center", fontsize=10, linespacing=1.45,
              fontweight="bold",
              transform=ax_d.get_yaxis_transform(), clip_on=False)

# ── Y-tick labels: swap type shown on BOTH panels ────────────────────────────
yticks  = [r[0] + ROW_H/2 for r in rows]
ylabels = [r[2] for r in rows]

ax_d.set_yticks(yticks)
ax_d.set_yticklabels(ylabels, fontsize=12, fontweight="bold")
ax_d.yaxis.tick_left()

ax_a.set_yticks(yticks)
ax_a.set_yticklabels(ylabels, fontsize=12, fontweight="bold")
ax_a.yaxis.tick_left()

# ── LEFT panel: Δpp horizontal bars ──────────────────────────────────────────
ax_d.set_xlim(-25, 48)
ax_d.axvline(0, color="black", lw=1.2, zorder=2)
ax_d.set_xlabel("CUED − UNCUED  (percentage points)", fontsize=12, labelpad=6)
ax_d.set_title("Cueing Effect  Δpp", fontsize=14, fontweight="bold", pad=10)

for y_base, _, sw, r in rows:
    yc  = y_base + ROW_H/2
    col = SWAP_COLOR[sw]
    d   = r["delta"]
    ax_d.barh(yc, d, height=BAR_H, color=col, alpha=0.88, zorder=3, left=0)
    gap  = 0.8 if d >= 0 else -0.8
    ha   = "left" if d >= 0 else "right"
    ax_d.text(d + gap, yc, f"{sig(r['p'])}  {d:+.1f}pp",
              va="center", ha=ha, fontsize=10, fontweight="bold",
              color=col, zorder=4)

leg_d = [mpatches.Patch(color=SWAP_COLOR[s], label=s) for s in ["N","MC","Db","Da"]]
ax_d.legend(handles=leg_d, fontsize=11, loc="lower right",
            title="Swap type", title_fontsize=11, framealpha=0.92)

# ── RIGHT panel: CUED% and UNCUED% ───────────────────────────────────────────
ax_a.set_xlim(0, 105)
ax_a.axvline(12.5, color="#888888", lw=1.3, ls="--", alpha=0.75, zorder=1)
ax_a.text(12.5, -0.55, "chance\n12.5%", ha="center", va="bottom",
          fontsize=9, color="#666666")
ax_a.set_xlabel("% Correct", fontsize=12, labelpad=6)
ax_a.set_title("Absolute Accuracy:  CUED  vs  UNCUED", fontsize=14,
               fontweight="bold", pad=10)

BH2 = BAR_H * 0.44   # each sub-bar height

# Thin swap-type stripe at the left edge of each row (20% smaller than v4)
STRIPE_W = 1.4   # data units wide (was ~1.75 equivalent before)

for y_base, _, sw, r in rows:
    yc  = y_base + ROW_H/2
    col = SWAP_COLOR[sw]
    # colored stripe — swap type indicator
    ax_a.barh(yc, STRIPE_W, height=BAR_H * 0.80, color=col,
              alpha=0.90, zorder=5, left=0)
    # CUED bar (upper sub-slot)
    ax_a.barh(yc - BH2/2 - 0.02, r["cued"],   height=BH2,
              color="#1a3a6b", alpha=0.80, zorder=3, left=0)
    # UNCUED bar (lower sub-slot)
    ax_a.barh(yc + BH2/2 + 0.02, r["uncued"], height=BH2,
              color="#7a2020", alpha=0.80, zorder=3, left=0)
    # value labels at bar tips
    ax_a.text(r["cued"]   + 0.8, yc - BH2/2 - 0.02,
              f"{r['cued']:.1f}%",   va="center", ha="left",
              fontsize=9.5, color="#1a3a6b", zorder=6)
    ax_a.text(r["uncued"] + 0.8, yc + BH2/2 + 0.02,
              f"{r['uncued']:.1f}%", va="center", ha="left",
              fontsize=9.5, color="#7a2020", zorder=6)

# Minimal legend — CUED and UNCUED only, anchored above the plot
leg_a = [
    mpatches.Patch(color="#1a3a6b", label="CUED"),
    mpatches.Patch(color="#7a2020", label="UNCUED"),
    plt.Line2D([0],[0], color="#888", ls="--", lw=1.5, label="Chance  12.5%"),
]
ax_a.legend(handles=leg_a, fontsize=11, framealpha=0.92,
            loc="upper right",
            bbox_to_anchor=(1.0, 1.0),
            title="", borderpad=0.8)

# ── main title ────────────────────────────────────────────────────────────────
fig.suptitle(
    "VRDots — MC and Db Conditions: All MCS Sessions  (2026-04-30)\n"
    "Db trials: CUED/UNCUED labels flipped to onset-cue convention  |  "
    "Accuracy window: exact match (8AFC)",
    fontsize=11.5, y=0.995, va="top", color="#333333")

# ── save ─────────────────────────────────────────────────────────────────────
out = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"
fig.savefig(f"{out}/mcs_summary_v4_graphs.png", dpi=150,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{out}/mcs_summary_v4_graphs.pdf",
            bbox_inches="tight", facecolor="white")
print("Saved mcs_summary_v4_graphs.png / .pdf")
