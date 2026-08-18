"""
Toy point-set model, figures A and B — two side-by-side V1 RFs, one dot in each.

Composition follows `fig_modelI_stimulus.png` (SurfaceSelectionModel repo,
LatestTurkey/ToyModel/): the stimulus disc, a large MT receptive field, and inside
it TWO adjacent V1 RFs — one holding a RED dot, one a GREEN dot. Palette and
conventions follow Figure 2 of the website's computational section
(`mt_rf_figure.py`), since these are destined for the same page.

  A  the stimulus, the MT RF, and the two V1 RFs with one dot in each.
  B  those two V1 RFs magnified, with each dot's real trajectory over the
     pre-probe rotation and the probe itself.

THE PAIR IS FOUND, NOT MANUFACTURED
-----------------------------------
Earlier versions placed the two RFs at a chosen eccentricity and then DELETED any
background dot that fell near them, which cleared a 4.4% hole in the display right
where the reader looks hardest — and quietly contradicted the figure's own caveat
that the other surface usually intrudes.

Now nothing is deleted. `_find_pure_pair` generates the two dot fields, moves them
through the whole window, and SEARCHES eccentricity x angle x layout seed for a
pair of adjacent RF-sized regions satisfying, on EVERY sampled frame:

    left RF   exactly one dot of field A (red, uncued), and it is the SAME dot
              throughout; no dot of field B ever enters
    right RF  exactly one dot of field B (green, cued), same dot throughout;
              no dot of field A ever enters

Identity persistence matters: "exactly one dot per frame" alone would permit one
dot leaving as another arrives, which is not the configuration the model relies on.
This is the same thing `hcps_twops.m` does on the real rotating stimulus, in
miniature. Every other dot is drawn exactly where it falls.

RF SIZE — fixed, NOT scaled with eccentricity (GS: not for the toy model), drawn
at the upper end of what can still honestly be called a V1 receptive field:

    sigma = 0.24 deg   ->   RF diameter 2*sigma = 0.48 deg

Just under the 0.52 ceiling where two independent human estimates agree — Dumoulin
& Wandell (2008) pRF (sigma = 0.1 + 0.15*E) and Freeman & Simoncelli (2011) V1
pooling (s = 0.26*E) — leaving a visible gap between the two circles. For scale at
E = 1: Dow 1981 cRF 0.13, `hcps_rfrule('small')` (= the MT patch the model runs)
0.24, 'large' 0.38. Absolute limit ~0.65 (5x cRF); past that the figure would be
depicting V2 pooling or an fMRI population. See WriteUps/v1_rf_sizes.md.

DENSITY — 3.0 dots/deg^2/field, BELOW the experiment's 5.0 (S&B 2010, matched by
the VRDots replication at 5.01 full-disk). Lowered deliberately, per GS, because
this is a schematic: at 5.0 a pair with exactly one persistent dot each exists in
only ~4 of 40 layouts, and the trajectory figure becomes unreadably dense. At 3.0
it is ~19 of 60 and the display stays legible. Still inside the broad S(lambda)
plateau documented in v1_rf_sizes.md, so nothing qualitative changes.

Numbers, all sourced:
  omega    81 deg/s     rotation speed (Stoner & Blanc 2010)
  probe    40 ms        parameters.T_TRANS (3 frames @ 75 Hz)
  pre      100 ms       rotation shown before the probe (GS); = hcps_twops default
  probe v  2.26 deg/s   hcpsDefaults.probeDegPerSec
  dot      0.03 deg     S&B (1 CRT pixel); VRDots uses 0.08

Run:  /usr/bin/python3 ps_two_rf_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.lines import Line2D

from web_figures import INK, INK2, BORDER, ACCENT, CUED, UNCUED, SURFACE

GREEN, RED = CUED, UNCUED           # green = cued/delayed, red = uncued/first-on

# ── stimulus, in DEGREES throughout ──
APERTURE_DEG = 2.0                  # 4 deg stimulus, S&B 2010
EXCL_DEG     = 0.47                 # near-fixation exclusion (matches Figure 2)
DENSITY      = 3.0                  # dots/deg^2/field — BELOW the experiment's 5.0,
                                    # deliberately; see the docstring
N_DOTS       = int(round(DENSITY * np.pi * (APERTURE_DEG**2 - EXCL_DEG**2)))
DOT_DIAM_DEG = 0.03                 # S&B dot; VRDots = 0.08

# ── the RFs: FIXED size, not scaled with eccentricity ──
SIGMA_DEG    = 0.24
RF_GAP_DEG   = 0.05                 # clear gap so the two RF circles do not touch
RF_DIAM_DEG  = 2 * SIGMA_DEG
RF_R_DEG     = SIGMA_DEG
_SEP         = RF_DIAM_DEG + RF_GAP_DEG      # centre-to-centre
MT_R_DEG     = 0.95                 # the MT RF enclosing both, as in fig_modelI.
                                    # Set by eye to fit the pair — the one quantity
                                    # in this figure without a literature source.

# ── motion ──
OMEGA_DEG_S  = 81.0
PROBE_DEG_S  = 2.26
PRE_MS       = 100.0
TRANS_MS     = 40.0

TRANSLATING_FIELD = "cued"          # "cued" (green) or "uncued" (red)

# ── the search ──
SEARCH_SEEDS   = range(1, 200)
SEARCH_FRAMES  = 21                 # frames sampled across the whole window
SEARCH_ECC     = np.arange(0.70, 1.61, 0.05)
SEARCH_ANG_DEG = np.arange(-40, 41, 5)


# ═══════════════════════════════════════════════════════════ helpers ══
def _field(n, rng):
    """Area-uniform dot positions in the annulus, in degrees."""
    ang = rng.uniform(0, 2 * np.pi, n)
    rs = np.sqrt(rng.uniform(EXCL_DEG**2, (APERTURE_DEG - 0.04)**2, n))
    return np.column_stack([rs * np.cos(ang), rs * np.sin(ang)])


def _rotation_path(p0, sense, ms, n=64):
    p0 = np.asarray(p0, float)
    R = np.hypot(*p0); th0 = np.arctan2(p0[1], p0[0])
    s = -1.0 if sense == "CW" else 1.0
    sweep = np.radians(OMEGA_DEG_S * ms / 1000.0) * s
    ths = th0 + np.linspace(0.0, sweep, n)
    return np.column_stack([R * np.cos(ths), R * np.sin(ths)])


def _translation_path(p0, ms, n=32, direction=(1.0, 0.0)):
    p0 = np.asarray(p0, float); d = np.asarray(direction, float)
    dist = PROBE_DEG_S * ms / 1000.0
    ts = np.linspace(0.0, 1.0, n)[:, None]
    return p0[None, :] + ts * dist * d[None, :]


def _dot_trajectory(p0, sense, translates):
    """Any dot's path: PRE_MS of rigid rotation, then TRANS_MS of either the
    rightward probe (if its field translates) or continued rotation.

    One definition for every dot in the figure, so nothing can silently use a
    different convention from anything else. Paths are NEVER re-positioned — each
    dot is drawn where it actually is.
    """
    pre = _rotation_path(p0, sense, PRE_MS)
    during = (_translation_path(pre[-1], TRANS_MS) if translates
              else _rotation_path(pre[-1], sense, TRANS_MS))
    return pre, during


def _positions_at(p0, sense, translates, t_s):
    """Whole field's positions at time t_s (seconds into the shown window)."""
    s = -1.0 if sense == "CW" else 1.0
    pre_s = PRE_MS / 1000.0
    th = s * np.radians(OMEGA_DEG_S) * min(t_s, pre_s)
    c, si = np.cos(th), np.sin(th)
    p = np.column_stack([p0[:, 0] * c - p0[:, 1] * si,
                         p0[:, 0] * si + p0[:, 1] * c])
    if t_s > pre_s:
        dt = t_s - pre_s
        if translates:
            p = p + np.array([PROBE_DEG_S * dt, 0.0])
        else:
            th2 = s * np.radians(OMEGA_DEG_S) * dt
            c2, s2 = np.cos(th2), np.sin(th2)
            p = np.column_stack([p[:, 0] * c2 - p[:, 1] * s2,
                                 p[:, 0] * s2 + p[:, 1] * c2])
    return p


def _find_pure_pair(seeds=SEARCH_SEEDS):
    """Search layouts for two adjacent RF-sized regions, each holding exactly one
    dot of ONE surface — the same dot — for every frame of the window, with no
    intrusion from the other surface. Returns None if no layout qualifies.
    """
    ts = np.linspace(0.0, (PRE_MS + TRANS_MS) / 1000.0, SEARCH_FRAMES)
    for seed in seeds:
        rng = np.random.default_rng(seed)
        A = _field(N_DOTS, rng)                     # red, CCW, uncued
        B = _field(N_DOTS, rng)                     # green, CW, cued
        trA = (TRANSLATING_FIELD == "uncued")
        trB = (TRANSLATING_FIELD == "cued")
        PA = [_positions_at(A, "CCW", trA, t) for t in ts]
        PB = [_positions_at(B, "CW", trB, t) for t in ts]
        for ecc in SEARCH_ECC:
            for ang in np.radians(SEARCH_ANG_DEG):
                cx, cy = ecc * np.cos(ang), ecc * np.sin(ang)
                Lc = np.array([cx - _SEP / 2, cy])
                Rc = np.array([cx + _SEP / 2, cy])
                inAL = [set(np.where(np.hypot(*(pa - Lc).T) < RF_R_DEG)[0]) for pa in PA]
                inBR = [set(np.where(np.hypot(*(pb - Rc).T) < RF_R_DEG)[0]) for pb in PB]
                if any(len(s_) != 1 for s_ in inAL): continue
                if any(len(s_) != 1 for s_ in inBR): continue
                iA = set.intersection(*inAL)        # SAME dot on every frame
                iB = set.intersection(*inBR)
                if not iA or not iB: continue
                if any((np.hypot(*(pb - Lc).T) < RF_R_DEG).any() for pb in PB): continue
                if any((np.hypot(*(pa - Rc).T) < RF_R_DEG).any() for pa in PA): continue
                return dict(seed=seed, A=A, B=B, Lc=Lc, Rc=Rc,
                            iA=iA.pop(), iB=iB.pop(),
                            ecc=float(ecc), ang=float(np.degrees(ang)))
    return None


# ── run the search once, at import; everything downstream reads its result ──
PAIR = _find_pure_pair()
if PAIR is None:
    raise RuntimeError("no layout gave a persistent one-dot-each pair; "
                       "lower DENSITY or widen SEARCH_SEEDS")
FIELD_A, FIELD_B = PAIR["A"], PAIR["B"]
RF_LEFT, RF_RIGHT = tuple(PAIR["Lc"]), tuple(PAIR["Rc"])
IDX_A, IDX_B = PAIR["iA"], PAIR["iB"]
MT_C = ((RF_LEFT[0] + RF_RIGHT[0]) / 2, (RF_LEFT[1] + RF_RIGHT[1]) / 2)
ECC_DEG = float(np.hypot(*MT_C))


# ═══════════════════════════════════════════════════════ containment ══
def _excursion(path, rf_c):
    """Furthest the dot's EDGE gets from the RF centre, over the whole path."""
    d = np.hypot(*(np.asarray(path) - np.asarray(rf_c)).T)
    return float(d.max()) + DOT_DIAM_DEG / 2


def _selected(which):
    """(start position, colour, sense, translates, RF centre) for a chosen dot."""
    if which == "left":
        return (FIELD_A[IDX_A], RED, "CCW", TRANSLATING_FIELD == "uncued", RF_LEFT)
    return (FIELD_B[IDX_B], GREEN, "CW", TRANSLATING_FIELD == "cued", RF_RIGHT)


# ═══════════════════════════════════════════════════════════ drawing ══
def _draw_trajectory(ax, pre, during, colour, lw_pre, lw_during, head, z):
    ax.plot(pre[:, 0], pre[:, 1], color=colour, lw=lw_pre, alpha=0.55,
            solid_capstyle="round", zorder=z)
    ax.plot(during[:, 0], during[:, 1], color=colour, lw=lw_during,
            solid_capstyle="round", zorder=z)
    ax.add_patch(FancyArrowPatch(during[-2], during[-1], arrowstyle="-|>",
                 mutation_scale=head, color=colour, lw=0, zorder=z))


# ═════════════════════════════════════════════════ A — the stimulus ══
def fig_A(out="ps_two_rf_A.png", show_traj=False):
    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    ax.set_aspect("equal"); ax.axis("off")
    lim = APERTURE_DEG + 0.5
    ax.set_xlim(-lim, lim + 2.3); ax.set_ylim(-lim, lim)

    ax.add_patch(Circle((0, 0), APERTURE_DEG, facecolor="#fafafa",
                        edgecolor=INK, lw=1.6, zorder=0))
    ax.add_patch(Circle(MT_C, MT_R_DEG, facecolor="#e7e5e1",
                        edgecolor="none", zorder=1))

    # EVERY dot, exactly where it falls — nothing is cleared
    for pts, colour, sense, role in [(FIELD_B, GREEN, "CW", "cued"),
                                     (FIELD_A, RED, "CCW", "uncued")]:
        translates = (role == TRANSLATING_FIELD)
        for p in pts:
            if show_traj:
                pre, during = _dot_trajectory(p, sense, translates)
                _draw_trajectory(ax, pre, during, colour,
                                 lw_pre=0.9, lw_during=1.6, head=5, z=3)
            ax.add_patch(Circle(p, DOT_DIAM_DEG / 2, facecolor=colour,
                                edgecolor="none", zorder=4))

    # the two V1 RFs — found, not placed
    for c in (RF_LEFT, RF_RIGHT):
        ax.add_patch(Circle(c, RF_R_DEG, facecolor="none", edgecolor=INK,
                            lw=1.8, zorder=6))

    # the two selected dots, redrawn on top so they read as the chosen pair
    for which in ("left", "right"):
        p0, colour, sense, translates, rf_c = _selected(which)
        if show_traj:
            pre, during = _dot_trajectory(p0, sense, translates)
            _draw_trajectory(ax, pre, during, colour,
                             lw_pre=1.3, lw_during=2.2, head=8, z=7)
        ax.add_patch(Circle(p0, DOT_DIAM_DEG / 2, facecolor=colour,
                            edgecolor="none", zorder=8))

    ax.plot(0, 0, marker="+", ms=12, mew=2.2, color=INK, zorder=9)

    ax.annotate("Area MT RF", xy=(MT_C[0] + MT_R_DEG * 0.72, MT_C[1] + MT_R_DEG * 0.72),
                xytext=(APERTURE_DEG + 0.45, 1.15), ha="left", va="center",
                fontsize=10.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0, shrinkB=3))
    ax.annotate("Area V1 RFs", xy=(RF_RIGHT[0] + RF_R_DEG, RF_RIGHT[1]),
                xytext=(APERTURE_DEG + 0.45, 0.30), ha="left", va="center",
                fontsize=10.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0, shrinkB=3))

    handles = [Line2D([0], [0], color=GREEN, lw=2.2, label="CW field  (cued / delayed)"),
               Line2D([0], [0], color=RED, lw=2.2, label="CCW field  (uncued / first-on)")]
    if show_traj:
        handles += [Line2D([0], [0], color=INK2, lw=1.1, alpha=0.55,
                           label=f"{PRE_MS:g} ms before the probe"),
                    Line2D([0], [0], color=INK2, lw=2.2,
                           label=f"{TRANS_MS:g} ms probe window")]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=9)

    sub = ("one dot in each of two V1 RFs — with its trajectory" if show_traj
           else "one dot in each of two V1 RFs")
    ax.set_title(f"A · Two counter-rotating fields, {sub}", fontsize=12, color=INK, pad=8)
    ax.text(0, -lim + 0.30,
            f"V1 RF {RF_DIAM_DEG:.2f}° diameter (σ {SIGMA_DEG:g}°) at {ECC_DEG:.2f}° — fixed, "
            f"not scaled with eccentricity · dots {DOT_DIAM_DEG:g}° · "
            f"{DENSITY:g} dots/deg²/field ({N_DOTS} per field)",
            ha="center", va="bottom", fontsize=8.5, color=INK2)
    ax.text(0, -lim + 0.13,
            f"The pair is FOUND, not placed: layout seed {PAIR['seed']} searched for two "
            f"adjacent RFs each holding the same single dot of one surface, with no intruder, "
            f"on every frame. No dot is hidden.",
            ha="center", va="bottom", fontsize=8, color=INK2, style="italic")

    fig.tight_layout()
    fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# ══════════════════════════════════════ B — the RFs magnified, trajs ══
def fig_B(out="ps_two_rf_B.png"):
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.9))
    specs = [(axes[0], "left",  "left V1 RF · red dot",   "CCW field — first-on (uncued)"),
             (axes[1], "right", "right V1 RF · green dot", "CW field — delayed-onset (cued)")]

    for ax, which, panel_lab, sub in specs:
        p0, colour, sense, translates, rf_c = _selected(which)
        ax.set_aspect("equal"); ax.axis("off")
        pad = RF_R_DEG * 0.40
        ax.set_xlim(rf_c[0] - RF_R_DEG - pad, rf_c[0] + RF_R_DEG + pad)
        ax.set_ylim(rf_c[1] - RF_R_DEG - pad, rf_c[1] + RF_R_DEG + pad * 1.4)
        ax.add_patch(Circle(rf_c, RF_R_DEG, facecolor=SURFACE, edgecolor=INK,
                            lw=2.0, zorder=1))

        pre, during = _dot_trajectory(p0, sense, translates)
        _draw_trajectory(ax, pre, during, colour, 2.0, 3.4, 17, z=4)
        ax.add_patch(Circle(p0, DOT_DIAM_DEG / 2, facecolor=colour,
                            edgecolor="none", zorder=6))
        ax.add_patch(Circle(pre[-1], DOT_DIAM_DEG / 2, facecolor="white",
                            edgecolor=colour, lw=1.6, zorder=6))

        note = ("rotation replaced by\nrightward translation" if translates
                else "rotation continues\nunchanged")
        ax.text(rf_c[0], rf_c[1] + RF_R_DEG + pad * 0.5, note, ha="center",
                va="bottom", fontsize=9.5, color=colour, fontweight="bold")

        exc = _excursion(np.vstack([pre, during]), rf_c)
        ax.text(rf_c[0], rf_c[1] - RF_R_DEG - pad * 0.5,
                f"dot stays within {exc:.3f}° of centre — RF radius {RF_R_DEG:.2f}° "
                f"({RF_R_DEG/exc:.2f}× margin)",
                ha="center", va="top", fontsize=9, color=INK2)
        ax.set_title(f"{panel_lab}\n{sub}", fontsize=11, color=INK, pad=6)

    fig.legend(handles=[
        Line2D([0], [0], color=INK2, lw=2.0, alpha=0.55,
               label=f"{PRE_MS:g} ms before the probe"),
        Line2D([0], [0], color=INK2, lw=3.4, label=f"{TRANS_MS:g} ms probe window"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
               markeredgecolor=INK2, markersize=8, label="probe onset")],
        loc="lower center", ncol=3, frameon=False, fontsize=9.5,
        bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("B · The same two V1 RFs, magnified — real dot trajectories through the probe",
                 fontsize=12.5, color=INK, y=0.99)
    fig.text(0.5, 0.055,
             f"rotation {OMEGA_DEG_S:g}°/s ({np.radians(OMEGA_DEG_S)*ECC_DEG:.2f}°/s tangential "
             f"at {ECC_DEG:.2f}°) · translation {PROBE_DEG_S:g}°/s · RF {RF_DIAM_DEG:.2f}° "
             f"diameter, fixed · paths are where the dots actually are, not re-centred",
             ha="center", va="bottom", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    lam = DENSITY * np.pi * RF_R_DEG**2
    print(f"density        {DENSITY} dots/deg^2/field  ({N_DOTS} per field)"
          f"   [experiment is 5.0]")
    print(f"RF             {RF_DIAM_DEG:.3f} deg diameter (sigma {SIGMA_DEG}), FIXED")
    print(f"\nPAIR FOUND by search — not placed:")
    print(f"  layout seed  {PAIR['seed']}")
    print(f"  centres      L {RF_LEFT[0]:+.3f},{RF_LEFT[1]:+.3f}   "
          f"R {RF_RIGHT[0]:+.3f},{RF_RIGHT[1]:+.3f}")
    print(f"  eccentricity {ECC_DEG:.3f} deg, polar angle {PAIR['ang']:+.0f} deg")
    print(f"  dots         field A #{IDX_A} (red, left), field B #{IDX_B} (green, right)")
    print(f"  guarantee    same dot in each RF on all {SEARCH_FRAMES} sampled frames,"
          f" no intruder from the other surface")
    print(f"\nCONTAINMENT of the found dots (edge, not centre):")
    for which in ("left", "right"):
        p0, colour, sense, tr, rf_c = _selected(which)
        pre, during = _dot_trajectory(p0, sense, tr)
        exc = _excursion(np.vstack([pre, during]), rf_c)
        print(f"  {which:5s}  reaches {exc:.4f} deg from centre, RF radius "
              f"{RF_R_DEG:.4f}  -> margin {RF_R_DEG/exc:.2f}x")
        assert exc < RF_R_DEG, f"{which} dot leaves its RF"
    print(f"\nCONTEXT: mean dots per field per RF = {lam:.3f}"
          f"  -> P(other surface intrudes) = {1-np.exp(-lam):.0%}, so this pair is rare")
    print()
    fig_A("ps_two_rf_A_static.png", show_traj=False)
    fig_A("ps_two_rf_A_traj.png",   show_traj=True)
    fig_B()
