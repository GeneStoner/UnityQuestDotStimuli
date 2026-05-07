"""
param_regression.py  (updated 2026-05-02)
Weighted least squares: stimulus parameters → accuracy outcomes.
Now n=6 experiments (added LargeFix Ap3.5°); CatekExact uses 2-session pool
from CatekExact_v1 only (1217/NDb_v1 excluded).

Weighting: 1/SE²  (binomial SE on each pooled estimate).
Predictors z-scored before fitting.
≤2 predictors due to n=6.

Outcomes (% correct or pp):
  Absolute: cued_N, uncued_N, cued_MC, uncued_MC
  Cueing:   delta_N, delta_MC
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from itertools import combinations
import glob, math, pandas as pd
from scipy import stats

OUT = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"

# ── load data from TSVs ───────────────────────────────────────────────────────

def find(bn):
    hits = glob.glob(f"/tmp/**/{bn}", recursive=True)
    return hits[0] if hits else None

def load(bn):
    return pd.read_csv(find(bn), sep="\t")

def add_correct(df):
    df = df.copy()
    df = df[df["RespDeg"] != -1]
    df["Correct"] = (((df["RespDeg"]-df["TransDeg"])+360)%360).apply(
        lambda d: d if d<=180 else d-360).abs() <= 67.5
    return df

def flip_db(df):
    df = df.copy()
    m = df["SwapType"]=="Db"
    df.loc[m,"Cond"] = df.loc[m,"Cond"].map({"CUED":"UNCUED","UNCUED":"CUED"})
    return df

def pool_stat(dfs, swap):
    """Pooled mean and binomial SE for a swap condition across sessions."""
    df = pd.concat(dfs, ignore_index=True)
    sub = df[df["SwapType"]==swap]
    c = sub[sub["Cond"]=="CUED"]["Correct"]
    u = sub[sub["Cond"]=="UNCUED"]["Correct"]
    p1, p2 = c.mean(), u.mean()
    nc, nu = len(c), len(u)
    # SE on each proportion
    se_c = math.sqrt(p1*(1-p1)/nc) if nc > 0 else 0
    se_u = math.sqrt(p2*(1-p2)/nu) if nu > 0 else 0
    # SE on delta (sum of variances, independent)
    pp = (c.sum()+u.sum())/(nc+nu)
    se_d = math.sqrt(pp*(1-pp)*(1/nc+1/nu)) if 0<pp<1 else 1e-6
    return dict(
        cued=p1*100, se_cued=se_c*100,
        uncued=p2*100, se_uncued=se_u*100,
        delta=(p1-p2)*100, se_delta=se_d*100,
        nc=nc, nu=nu
    )

SESSIONS = [
    dict(label="CatekExact\n1.65°/80ms",
         dfs=[flip_db(add_correct(load("vr_dots_session_260427_0707.tsv"))),
              flip_db(add_correct(load("vr_dots_session_260427_1003.tsv")))],
         swap="Db",
         ap_diam=1.65, duration=80., density=20.1, excl_abs=0.50),
    dict(label="S&B\n2.0°/44ms",
         dfs=[add_correct(load("vr_dots_session_260430_1312.tsv")),
              add_correct(load("vr_dots_session_260430_1512.tsv"))],
         swap="MC",
         ap_diam=2.0, duration=44., density=20.1, excl_abs=0.396),
    dict(label="S&B\n3.5°/44ms\nSmFix",
         dfs=[add_correct(load("vr_dots_session_260501_0752.tsv")),
              add_correct(load("vr_dots_session_260501_0949.tsv"))],
         swap="MC",
         ap_diam=3.5, duration=44., density=20.0, excl_abs=0.396),
    dict(label="S&B\n3.5°/80ms\nSmFix",
         dfs=[add_correct(load("vr_dots_session_260501_1420.tsv")),
              add_correct(load("vr_dots_session_260501_1608.tsv"))],
         swap="MC",
         ap_diam=3.5, duration=80., density=20.0, excl_abs=0.396),
    dict(label="LargeFix\n3.5°/44ms",
         dfs=[add_correct(load("vr_dots_session_260502_0638.tsv")),
              add_correct(load("vr_dots_session_260502_0729.tsv"))],
         swap="MC",
         ap_diam=3.5, duration=44., density=20.0, excl_abs=1.10),
    dict(label="DenseCM\n3.5°/80ms",
         dfs=[add_correct(load("vr_dots_session_260423_1053.tsv"))],
         swap="MC",
         ap_diam=3.5, duration=80., density=52.0, excl_abs=1.10),
]

# compute outcomes and derived params
for s in SESSIONS:
    r_n  = pool_stat(s["dfs"], "N")
    r_sw = pool_stat(s["dfs"], s["swap"])
    s.update(r_n=r_n, r_sw=r_sw)
    ap_r = s["ap_diam"] / 2   # actual radius (yaml value is diameter)
    s["excl_ratio"] = s["excl_abs"] / ap_r

N = len(SESSIONS)

# ── predictor arrays ──────────────────────────────────────────────────────────

ap_diam    = np.array([s["ap_diam"]    for s in SESSIONS])
duration   = np.array([s["duration"]   for s in SESSIONS])
density    = np.array([s["density"]    for s in SESSIONS])
excl_abs   = np.array([s["excl_abs"]   for s in SESSIONS])
excl_ratio = np.array([s["excl_ratio"] for s in SESSIONS])

preds      = [ap_diam, duration, density, excl_abs, excl_ratio]
pred_names = ["ap_diam", "duration", "density", "excl_abs", "excl_ratio"]

# outcome arrays + SE arrays
def get_outcome(key, se_key):
    y   = np.array([s["r_n" if "N" in key or "delta_N" in key else "r_sw"][key]   for s in SESSIONS])
    se  = np.array([s["r_n" if "N" in key or "delta_N" in key else "r_sw"][se_key] for s in SESSIONS])
    return y, se

cued_N,    se_cued_N    = np.array([s["r_n"]["cued"]    for s in SESSIONS]), \
                          np.array([s["r_n"]["se_cued"]  for s in SESSIONS])
uncued_N,  se_uncued_N  = np.array([s["r_n"]["uncued"]  for s in SESSIONS]), \
                          np.array([s["r_n"]["se_uncued"] for s in SESSIONS])
cued_MC,   se_cued_MC   = np.array([s["r_sw"]["cued"]   for s in SESSIONS]), \
                          np.array([s["r_sw"]["se_cued"]  for s in SESSIONS])
uncued_MC, se_uncued_MC = np.array([s["r_sw"]["uncued"] for s in SESSIONS]), \
                          np.array([s["r_sw"]["se_uncued"] for s in SESSIONS])
delta_N,   se_delta_N   = np.array([s["r_n"]["delta"]   for s in SESSIONS]), \
                          np.array([s["r_n"]["se_delta"]  for s in SESSIONS])
delta_MC,  se_delta_MC  = np.array([s["r_sw"]["delta"]  for s in SESSIONS]), \
                          np.array([s["r_sw"]["se_delta"] for s in SESSIONS])

OUTCOMES = {
    "cued_N":    (cued_N,    se_cued_N),
    "uncued_N":  (uncued_N,  se_uncued_N),
    "cued_MC":   (cued_MC,   se_cued_MC),
    "uncued_MC": (uncued_MC, se_uncued_MC),
    "delta_N":   (delta_N,   se_delta_N),
    "delta_MC":  (delta_MC,  se_delta_MC),
}

# ── WLS helpers ───────────────────────────────────────────────────────────────

def zscore(x):
    return (x - x.mean()) / (x.std() + 1e-12)

def wls(X, y, w):
    """Weighted OLS with intercept. w = 1/SE². Returns coefs, yhat, R²_weighted."""
    W  = np.diag(w)
    Xb = np.column_stack([np.ones(len(y)), X])
    # coef = (Xb'W Xb)^-1 Xb'W y
    XtW  = Xb.T @ W
    coef = np.linalg.lstsq(XtW @ Xb, XtW @ y, rcond=None)[0]
    yhat = Xb @ coef
    # weighted R²
    ybar_w = np.average(y, weights=w)
    ss_res = np.sum(w * (y - yhat)**2)
    ss_tot = np.sum(w * (y - ybar_w)**2)
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0.
    return coef, yhat, r2

def best_single(y, se):
    w = 1 / (se**2 + 1e-6)
    best = None
    for p, pn in zip(preds, pred_names):
        X = zscore(p).reshape(-1,1)
        coef, yhat, r2 = wls(X, y, w)
        if best is None or r2 > best["r2"]:
            best = dict(pname=pn, X=X, coef=coef, yhat=yhat, r2=r2, w=w)
    return best

def best_pair(y, se):
    w = 1 / (se**2 + 1e-6)
    best = None
    for (p1,n1),(p2,n2) in combinations(zip(preds,pred_names),2):
        X = np.column_stack([zscore(p1), zscore(p2)])
        coef, yhat, r2 = wls(X, y, w)
        if best is None or r2 > best["r2"]:
            best = dict(pnames=(n1,n2), X=X, coef=coef, yhat=yhat, r2=r2, w=w)
    return best

# ── print summary ─────────────────────────────────────────────────────────────

print("="*65)
print("WEIGHTED SINGLE-PREDICTOR MODELS  (weights = 1/SE²)")
print("="*65)
for yname, (y, se) in OUTCOMES.items():
    w = 1/(se**2+1e-6)
    print(f"\n── {yname} ──")
    best_r2 = max(wls(zscore(p).reshape(-1,1), y, w)[2] for p in preds)
    for p, pn in zip(preds, pred_names):
        X = zscore(p).reshape(-1,1)
        coef, yhat, r2 = wls(X, y, w)
        marker = " ◄" if abs(r2-best_r2)<1e-6 else ""
        print(f"  {pn:12s}  wR²={r2:.3f}  coef={coef[1]:+.2f}{marker}")

# ── figure ────────────────────────────────────────────────────────────────────

SHORT = [s["label"] for s in SESSIONS]
EXP_COLORS = ["#e74c3c","#3498db","#27ae60","#f39c12","#9b59b6","#1abc9c"]

OUTCOME_GROUPS = [
    [("cued_N",  "#2ca02c", "CUED N"),
     ("uncued_N","#74c476", "UNCUED N")],
    [("cued_MC", "#1f77b4", "CUED MC"),
     ("uncued_MC","#6baed6","UNCUED MC")],
    [("delta_N", "#2ca02c", "Δ N  (CUED−UNCUED)"),
     ("delta_MC","#1f77b4", "Δ MC")],
]

fig = plt.figure(figsize=(18, 14), facecolor="white")
fig.subplots_adjust(hspace=0.52, wspace=0.32,
                    left=0.06, right=0.97, top=0.93, bottom=0.06)

gs_outer = gridspec.GridSpec(3, 1, figure=fig, hspace=0.52)

for grp_idx, group in enumerate(OUTCOME_GROUPS):
    gs_inner = gridspec.GridSpecFromSubplotSpec(
        1, 2, subplot_spec=gs_outer[grp_idx], wspace=0.30)

    for sub_idx, (yname, col, ylabel) in enumerate(group):
        ax = fig.add_subplot(gs_inner[sub_idx])
        y, se = OUTCOMES[yname]
        w = 1/(se**2+1e-6)

        bp = best_pair(y, se)
        bs = best_single(y, se)
        yhat_pair   = bp["yhat"]
        yhat_single = bs["yhat"]

        ax.set_facecolor("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        x_pos = np.arange(N)

        # error bars (±1.96 SE = 95% binomial CI)
        ax.errorbar(x_pos, y, yerr=1.96*se, fmt="none",
                    color="#aaa", lw=1.4, capsize=4, capthick=1.2, zorder=2)

        # observed dots
        for i, (xi, yi, sei) in enumerate(zip(x_pos, y, se)):
            ax.plot(xi, yi, "o", color=EXP_COLORS[i],
                    markersize=9, zorder=4, markeredgecolor="white",
                    markeredgewidth=0.8)

        # single-predictor fit line (sorted by predictor value for clean line)
        px = bs["X"].flatten()
        sort_idx = np.argsort(px)
        ax.plot(x_pos[sort_idx], yhat_single[sort_idx],
                "--", color=col, lw=1.6, alpha=0.7, zorder=3,
                label=f"best 1-pred ({bs['pname']})\nwR²={bs['r2']:.2f}")

        # 2-predictor predicted as open squares
        ax.plot(x_pos, yhat_pair, "s", color=col,
                markersize=7, alpha=0.85, zorder=3,
                markeredgecolor="black", markeredgewidth=0.8,
                label=f"best 2-pred ({'+'.join(bp['pnames'])})\nwR²={bp['r2']:.2f}")

        if "delta" not in yname:
            ax.axhline(12.5, color="#ccc", ls="--", lw=1)
            ax.set_ylim(20, 105)
        else:
            ax.axhline(0, color="#ccc", lw=1)
            ax.set_ylim(-5, 50)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(SHORT, fontsize=7.5, linespacing=1.2)
        ax.set_ylabel("% correct" if "delta" not in yname else "Δpp", fontsize=10)
        ax.set_title(ylabel, fontsize=11, fontweight="bold", color=col, pad=6)
        ax.legend(fontsize=8, loc="upper right", framealpha=0.88,
                  handlelength=1.5)

# experiment colour legend
leg_handles = [
    plt.Line2D([0],[0], marker="o", color="w",
               markerfacecolor=EXP_COLORS[i], markersize=9,
               markeredgecolor="white", label=SHORT[i].replace("\n"," "))
    for i in range(N)
]
fig.legend(handles=leg_handles, fontsize=9, loc="lower center",
           ncol=N, title="Experiment (coloured dots)", title_fontsize=9,
           bbox_to_anchor=(0.5, 0.005), framealpha=0.92)

fig.suptitle(
    "Weighted regression: stimulus parameters → accuracy outcomes\n"
    "Weights = 1/SE²  (binomial)  |  dots = observed ±95% CI  |  "
    "dashed = best 1-predictor fit  |  squares = best 2-predictor predicted",
    fontsize=11, y=0.995, va="top")

fig.savefig(f"{OUT}/param_regression.png", dpi=150,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{OUT}/param_regression.pdf",
            bbox_inches="tight", facecolor="white")
print("\nSaved param_regression.png / .pdf")
