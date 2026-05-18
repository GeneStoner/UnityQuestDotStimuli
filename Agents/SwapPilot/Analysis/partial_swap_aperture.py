"""
partial_swap_aperture.py
N / D / Da / Db (+ MC where available) cueing effects across aperture sizes.
Pools all full sessions per asset group; 95% binomial CI error bars; per-session diamonds.

Label flips applied before analysis (onset-cue convention):
  Da: Sub0 (always-on) does coherent translation in booking-CUED → labels swapped
  Db: same issue confirmed → labels swapped
  Both confirmed via 2D trace stimulus from asset parameters + C# motion code.

AperSweep sessions: multi-duration sweeps (20/40/65/90/130/178/250/350 ms target).
  Filtered to 88.889 ms (= 8 frames @ 90 Hz, closest to the 80 ms used elsewhere).

Two figures saved:
  Page 1 — Partial swap conditions (N / D / Da / Db ± MC)
  Page 2 — N vs MC (Stoner-Blanc replication series + density / continuity variants)
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

APERSWEEP_DUR_MS = 88.889   # 8 frames @ 90 Hz — closest AperSweep bin to 80 ms

# ── helpers ───────────────────────────────────────────────────────────────────

def find(bn):
    hits = glob.glob(f"/tmp/**/{bn}", recursive=True)
    return hits[0] if hits else None

def load(bn, dur_filter=None):
    p = find(bn)
    if not p: raise FileNotFoundError(bn)
    df = pd.read_csv(p, sep="\t")
    if dur_filter is not None:
        df = df[np.isclose(df["PresentedDurMs"], dur_filter, atol=0.5)]
    df = df[df["RespDeg"] != -1].copy()
    df["Correct"] = (df["RespDeg"] == df["TransDeg"]).astype(float)
    return df

def flip_labels(df):
    """Flip CUED/UNCUED for Da and Db to restore onset-cue convention."""
    df = df.copy()
    for sw in ("Da", "Db"):
        m = df["SwapType"] == sw
        df.loc[m, "Cond"] = df.loc[m, "Cond"].map({"CUED": "UNCUED", "UNCUED": "CUED"})
    return df

def cue_stats(df_pool, swap):
    sub = df_pool[df_pool["SwapType"] == swap]
    if not len(sub): return None
    c = sub[sub["Cond"] == "CUED"]["Correct"]
    u = sub[sub["Cond"] == "UNCUED"]["Correct"]
    if not len(c) or not len(u): return None
    p1, p2 = c.mean(), u.mean()
    n1, n2 = len(c), len(u)
    pp = (c.sum() + u.sum()) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1/n1 + 1/n2)) if 0 < pp < 1 else 1e-9
    z  = (p1 - p2) / se
    pv = 2 * (1 - stats.norm.cdf(abs(z)))
    return dict(delta=(p1-p2)*100, ci95=1.96*se*100,
                cued=p1*100, uncued=p2*100,
                z=z, p=pv, n=n1+n2)

def sig(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.1:   return "†"
    return "n.s."

def sess_delta(sdf, swap):
    sub = sdf[sdf["SwapType"] == swap]
    if not len(sub): return None
    c = sub[sub["Cond"] == "CUED"]["Correct"].mean()
    u = sub[sub["Cond"] == "UNCUED"]["Correct"].mean()
    if np.isnan(c) or np.isnan(u): return None
    return (c - u) * 100

def load_sessions(filenames, dur_filter=None):
    raw  = [load(bn, dur_filter) for bn in filenames]
    flpd = [flip_labels(s) for s in raw]
    return raw, flpd

# ── condition colours / display ───────────────────────────────────────────────

COND_COLOR = {
    "N":  "#2ca02c",
    "D":  "#e8901a",
    "Da": "#d62728",
    "Db": "#1f77b4",
    "MC": "#9467bd",
}
COND_DISP = {
    "N":  "N   (no swap)",
    "D":  "D   (noise-half swap)",
    "Da": "Da  (coherent-half swap, flipped)",
    "Db": "Db  (full subfield swap, flipped)",
    "MC": "MC  (motion+color swap)",
}

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 DATASETS — Partial swap conditions (N / D / Da / Db ± MC)
# ══════════════════════════════════════════════════════════════════════════════

P1 = []

# 1. CatekExact Ap1.65° — 80 ms, 43 dots, 2 full sessions (NDb session excluded: n=64, N=0.0pp)
raw, flpd = load_sessions([
    "vr_dots_session_260427_0707.tsv",
    "vr_dots_session_260427_1003.tsv",
])
P1.append(dict(
    label="CatekExact\nAp 1.65°\n80 ms · 43 dots",
    note="≈Catek replication (80 vs 133 ms; same aperture, density)",
    ap="1.65°", df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "D", "Da", "Db"],
))

# 2. MCvsDb Ap1.65° — sanity check MC≈Db, 3 sessions
raw, flpd = load_sessions([
    "vr_dots_session_260429_0748.tsv",
    "vr_dots_session_260429_0951.tsv",
    "vr_dots_session_260429_1031.tsv",
])
P1.append(dict(
    label="MCvsDb\nAp 1.65°\n80 ms · 43 dots",
    note="Sanity: MC vs Db (Catek M+C did not run combined)",
    ap="1.65°", df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["MC", "Db"],
))

# 3. HighDens Ap3.5° — 80 ms, 173 dots  [AperSweep dropped: single-bin n too small]
raw, flpd = load_sessions(["vr_dots_session_260427_1423.tsv"])
P1.append(dict(
    label="HighDens\nAp 3.5°\n80 ms · 173 dots",
    note="1 session; elevated density",
    ap="3.5°", df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "D", "Da", "Db"],
))

# 7. Catek Ap3.5° — 80 ms, 43 dots (no Db condition)
raw, flpd = load_sessions(["vr_dots_session_260424_1801.tsv"])
P1.append(dict(
    label="Catek\nAp 3.5°\n80 ms · 43 dots",
    note="1 full session; no Db condition in asset",
    ap="3.5°", df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "D", "Da"],
))

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 DATASETS — N vs MC (StonerBlanc replication series + density variants)
# ══════════════════════════════════════════════════════════════════════════════

P2 = []

# 8. StonerBlanc_Replication_v1 — 44 ms, Ap2.0° (r=2.0°), 63 dots/field, 2 sessions
raw, flpd = load_sessions([
    "vr_dots_session_260430_1312.tsv",
    "vr_dots_session_260430_1512.tsv",
])
P2.append(dict(
    label="S&B Replication\nAp 2.0° · 44 ms\n63 dots/field",
    note="StonerBlanc_Replication_v1; Ap2.0° (r=2.0°), 63 dots/field, 44 ms",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "MC"],
))

# 9. StonerBlanc_Replication_Ap35_v1 — 44 ms, Ap3.5°, 2 sessions
raw, flpd = load_sessions([
    "vr_dots_session_260501_0752.tsv",
    "vr_dots_session_260501_0949.tsv",
])
P2.append(dict(
    label="S&B Replication\nAp 3.5° · 44 ms\n(Ap35_v1)",
    note="StonerBlanc_Replication_Ap35_v1; 44 ms",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "MC"],
))

# 10. StonerBlanc_Ap35_80ms — 78 ms, Ap3.5°, 2 sessions
raw, flpd = load_sessions([
    "vr_dots_session_260501_1420.tsv",
    "vr_dots_session_260501_1608.tsv",
])
P2.append(dict(
    label="S&B Ap35\nAp 3.5° · 78 ms",
    note="StonerBlanc_Ap35_80ms_v1; 78 ms (7 fr @ 90 Hz)",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "MC"],
))

# 11. StonerBlanc_Ap35_LargeFix — 44 ms, large fixation, 2 sessions
raw, flpd = load_sessions([
    "vr_dots_session_260502_0638.tsv",
    "vr_dots_session_260502_0729.tsv",
])
P2.append(dict(
    label="S&B LargeFix\nAp 3.5° · 44 ms",
    note="StonerBlanc_Ap35_LargeFix_v1; large fixation marker",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "MC"],
))

# 12. DensityPeak_CM — 500 dots, Ap3.5°, 1 session
raw, flpd = load_sessions(["vr_dots_session_260423_1053.tsv"])
P2.append(dict(
    label="DensityPeak+CM\nAp 3.5° · 80 ms\n500 dots",
    note="DensityCompare_Peak_ColorMotionSwap_v1",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "MC"],
))

# 12b. Simult Onset Control — 500 dots, Ap3.5°, 1 full session (0721=9 trials, 1033=2 trials excluded)
raw, flpd = load_sessions(["vr_dots_session_260423_0725.tsv"])
P2.append(dict(
    label="Simult Onset\nAp 3.5° · 80 ms\n500 dots (onset=0)",
    note="DensityCompare_Peak_Simult_v1; delayedOnset=0ms; sanity check — no temporal cue",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N"],
))

# 13. UltraHigh_CM — 1000 dots, Ap3.5°, 1 session
raw, flpd = load_sessions(["vr_dots_session_260502_1304.tsv"])
P2.append(dict(
    label="UltraHigh+CM\nAp 3.5° · 80 ms\n1000 dots",
    note="DensityCompare_UltraHigh_ColorMotionSwap_v1",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "MC"],
))

# 14. NoContinuity — 500 dots, Ap3.5°, 2 full sessions (1121/1327 aborted)
raw, flpd = load_sessions([
    "vr_dots_session_260504_1122.tsv",
    "vr_dots_session_260504_1608.tsv",
])
P2.append(dict(
    label="NoContinuity\nAp 3.5° · 80 ms\n500 dots",
    note="NoContinuity_Peak_ColorMotionSwap_v1; replotTranslatingAtTStart=true",
    df=pd.concat(flpd, ignore_index=True), sess=flpd,
    swaps=["N", "MC"],
))

# ── compute stats ─────────────────────────────────────────────────────────────

for ds in P1 + P2:
    ds["stats"]       = {sw: cue_stats(ds["df"], sw) for sw in ds["swaps"]}
    ds["sess_deltas"] = {sw: [sess_delta(s, sw) for s in ds["sess"]] for sw in ds["swaps"]}
    ds["n_sessions"]  = len(ds["sess"])

# ── figure factory ────────────────────────────────────────────────────────────

ROW_H  = 0.85
DS_GAP = 1.0
BAR_H  = 0.38
SHADES = ["#f0f4ff","#e8e4ff","#fff8f0","#f0fff0","#e8fff8","#fff8ee","#fce8ff","#f0f8ff"]
SESS_COLORS = ["#e67e22","#8e44ad","#16a085","#c0392b","#2980b9"]


def build_figure(datasets, title, xlim=(-52, 72)):
    rows = []
    ds_spans = []
    y = 0.0
    for i, ds in enumerate(datasets):
        y_top = y - 0.25
        for sw in ds["swaps"]:
            r = ds["stats"][sw]
            if r is not None:
                rows.append((y, ds["label"], sw, r, ds))
                y += ROW_H
        ds_spans.append((y_top, y - ROW_H + 0.25, ds["label"], i))
        y += DS_GAP

    total_y = y - DS_GAP + ROW_H
    fig, ax = plt.subplots(figsize=(13, total_y * 0.55 + 2.5), facecolor="white")
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(-0.6, total_y + 0.3)
    ax.invert_yaxis()

    for y_top, y_bot, _, i in ds_spans:
        ax.axhspan(y_top, y_bot, color=SHADES[i % len(SHADES)], alpha=0.65, zorder=0)

    for y_top, y_bot, ds_label, _ in ds_spans:
        ymid = (y_top + y_bot) / 2
        ax.text(-0.28, ymid, ds_label,
                ha="left", va="center", fontsize=9.5, fontweight="bold",
                linespacing=1.35, transform=ax.get_yaxis_transform(), clip_on=False)

    yticks  = [r[0] + ROW_H/2 for r in rows]
    ylabels = [COND_DISP[r[2]] for r in rows]
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=10)
    ax.yaxis.tick_left()

    ax.set_xlim(*xlim)
    ax.axvline(0, color="black", lw=1.2, zorder=2)
    ax.set_xlabel("CUED − UNCUED  (pp)  [onset-cue convention; Da and Db labels flipped]",
                  fontsize=11, labelpad=6)
    ax.set_title(title, fontsize=11, pad=8)
    ax.tick_params(axis="x", labelsize=10)

    dot_pos = {}
    for y_base, ds_label, sw, r, ds in rows:
        yc  = y_base + ROW_H / 2
        col = COND_COLOR[sw]
        d   = r["delta"]

        ax.barh(yc, d, height=BAR_H, color=col, alpha=0.82, zorder=3, left=0)
        ax.errorbar(d, yc, xerr=r["ci95"], fmt="none",
                    color="black", lw=1.5, capsize=4, capthick=1.2, zorder=6)

        gap = r["ci95"] + 0.8 if d >= 0 else -(r["ci95"] + 0.8)
        ha  = "left" if d >= 0 else "right"
        ax.text(d + gap, yc,
                f"{sig(r['p'])}  {d:+.1f}pp  (n={r['n']})",
                va="center", ha=ha, fontsize=8.5, color=col, zorder=4)

        deltas = [v for v in ds["sess_deltas"][sw] if v is not None]
        if not deltas:
            continue
        jitter = np.linspace(-BAR_H * 0.28, BAR_H * 0.28, len(deltas))
        for si, (dv, jit) in enumerate(zip(deltas, jitter)):
            ax.plot(dv, yc + jit, "D", color="white", markersize=7, zorder=8)
            ax.plot(dv, yc + jit, "D", color=col,
                    markersize=6, zorder=9, markeredgecolor="black", markeredgewidth=0.8)
            dot_pos[(ds_label, si, sw)] = (dv, yc + jit)

    for ds in datasets:
        swaps = [sw for sw in ds["swaps"] if ds["stats"][sw] is not None]
        for si in range(ds["n_sessions"]):
            xs, ys = [], []
            for sw in swaps:
                k = (ds["label"], si, sw)
                if k in dot_pos:
                    xs.append(dot_pos[k][0]); ys.append(dot_pos[k][1])
            if len(xs) > 1:
                ax.plot(xs, ys, "-", color=SESS_COLORS[si % len(SESS_COLORS)],
                        lw=1.2, alpha=0.55, zorder=5)

    all_conds = list(dict.fromkeys(sw for _, _, sw, _, _ in rows))
    leg_handles = [
        mpatches.Patch(color=COND_COLOR[sw], label=COND_DISP[sw])
        for sw in all_conds
    ] + [
        plt.Line2D([0],[0], marker="D", color="w", markerfacecolor="#555",
                   markeredgecolor="black", markersize=6, label="individual sessions"),
        plt.Line2D([0],[0], color="black", lw=1.5, marker="|", markersize=7,
                   markeredgewidth=1.5, label="95% CI (binomial)"),
    ]
    ax.legend(handles=leg_handles, fontsize=9, loc="lower right",
              framealpha=0.92, handlelength=1.5, ncol=2)

    fig.subplots_adjust(left=0.30, right=0.97, top=0.93, bottom=0.07)
    return fig


# ── Page 1 ────────────────────────────────────────────────────────────────────
fig1 = build_figure(
    P1,
    "Partial Swap Cueing Effects — Page 1: N / D / Da / Db across Aperture Sizes\n"
    "AperSweep filtered to 88.9 ms bin  |  bars = pooled Δpp  |  ◆ = individual sessions  |  "
    "error bars = 95% CI",
)
fig1.savefig(f"{OUT}/partial_swap_aperture_p1.png", dpi=150, bbox_inches="tight", facecolor="white")
fig1.savefig(f"{OUT}/partial_swap_aperture_p1.pdf", bbox_inches="tight", facecolor="white")
print("Saved partial_swap_aperture_p1.png/.pdf")

# ── Page 2 ────────────────────────────────────────────────────────────────────
fig2 = build_figure(
    P2,
    "Partial Swap Cueing Effects — Page 2: N vs MC (Stoner-Blanc replication + density / continuity)\n"
    "bars = pooled Δpp  |  ◆ = individual sessions  |  error bars = 95% CI",
)
fig2.savefig(f"{OUT}/partial_swap_aperture_p2.png", dpi=150, bbox_inches="tight", facecolor="white")
fig2.savefig(f"{OUT}/partial_swap_aperture_p2.pdf", bbox_inches="tight", facecolor="white")
print("Saved partial_swap_aperture_p2.png/.pdf")

# ── summary table ─────────────────────────────────────────────────────────────
for page, datasets in [("PAGE 1", P1), ("PAGE 2", P2)]:
    print(f"\n── {page} ──")
    print(f"{'Dataset':35s}  {'Sw':3s}  {'Δpp':>7s}  {'±95CI':>6s}  {'sig':5s}  {'n':>5s}")
    print("-" * 68)
    for ds in datasets:
        for sw in ds["swaps"]:
            r = ds["stats"][sw]
            if r:
                print(f"{ds['label'].replace(chr(10),' '):35s}  {sw:3s}  "
                      f"{r['delta']:+7.1f}  {r['ci95']:6.1f}  {sig(r['p']):5s}  {r['n']:5d}")
        print()
