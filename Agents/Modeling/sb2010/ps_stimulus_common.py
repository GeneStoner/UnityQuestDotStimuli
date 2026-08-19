"""
Shared stimulus for the two schematics of the computational section.

    mt_rf_figure.py        Figure 2 — the stimulus + an MT receptive field
    ps_two_rf_figure.py    the same picture + two V1 RFs inside that MT RF

Both import `draw_stimulus` from here, and the dot layout is computed ONCE in this
module, so the two stimulus panels cannot drift apart. Flipping between the two
figures shows the V1 RFs arriving and nothing else moving — which is the point.

Composition follows `fig_modelI_stimulus.png` (SurfaceSelectionModel,
LatestTurkey/ToyModel/): stimulus disc, a grey MT RF off to one side of fixation,
large easily-discernible dots. Palette from `web_figures`, so these sit with the
rest of the website set.

NO MOTION IS DRAWN IN THE STIMULUS PANEL. Trajectories appear only in the
blow-ups — the MT RF magnified in Figure 2, the two V1 RFs magnified in the V1
figure. `dot_trajectory` / `draw_trajectory` live here but are called only by
those panels.

THE LAYOUT IS CONSTRUCTED, NOT SEARCHED
---------------------------------------
`build_layout` places, per field:

    1 selected dot   positioned by `_centred_start` so its WHOLE trajectory —
                     pre-probe rotation plus probe — lies inside its V1 RF
    3 filler dots    inside the MT RF but clear of both V1 RFs, equal numbers of
                     each colour so the MT blow-up is about 50/50
    32 pepper dots   over the rest of the display

1 + 3 + 32 = 36 = DENSITY x annulus area, so the construction preserves density
exactly rather than trading it for the arrangement. Every non-selected dot is
verified to clear both V1 RFs at all sampled frames, so each V1 RF really does
hold one dot and only one for the whole window.

Earlier versions searched thousands of random layouts for one that happened to
qualify. That worked, but left dot counts in the MT RF, their colour balance and
how well centred the paths were all hostage to whichever seed came up. Building
it directly fixes all of them at once.

Run either figure script; this module builds the layout on import.
"""

import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.lines import Line2D

from web_figures import INK, INK2, BORDER, ACCENT, CUED, UNCUED, SURFACE

GREEN, RED = CUED, UNCUED           # green = cued/delayed, red = uncued/first-on

# ── stimulus, in DEGREES throughout ──
APERTURE_DEG = 2.0                  # 4 deg stimulus, S&B 2010
EXCL_DEG     = 0.47                 # near-fixation exclusion
DENSITY      = 3.0                  # dots/deg^2/field — below the experiment's 5.0,
                                    # deliberately: this is a schematic and the
                                    # display must stay legible
N_DOTS       = int(round(DENSITY * np.pi * (APERTURE_DEG**2 - EXCL_DEG**2)))
DOT_DIAM_DEG = 0.08                 # VRDots' own dot size. Measurement of
                                    # fig_modelI_stimulus puts its dots at ~2% of
                                    # the aperture diameter, i.e. ~0.08 deg — so
                                    # this matches the template's legibility and
                                    # is still a real number. S&B's own dot is
                                    # 0.03 deg (1 CRT pixel).

# ── the V1 RFs: FIXED size, not scaled with eccentricity ──
SIGMA_DEG    = 0.24                 # 0.48 deg diameter; just under the 0.52 ceiling
RF_GAP_DEG   = 0.05                 # visible gap so the two circles do not touch
RF_DIAM_DEG  = 2 * SIGMA_DEG
RF_R_DEG     = SIGMA_DEG
_SEP         = RF_DIAM_DEG + RF_GAP_DEG

# ── the MT RF: off to one side of fixation, as in fig_modelI_stimulus ──
# PLACED BY ITS OUTER EDGE (GS): the right border sits ON the aperture border, so
# MT_ECC = APERTURE - MT_R. Everything then follows from the radius alone.
#
# WHY NOT BIGGER. The model treats each rotation as locally a translation, which
# only holds while every dot in the RF shares roughly one tangential direction.
# For an RF at eccentricity e with radius R the extreme direction departs from
# vertical by arcsin(R/e), and the RF's inner edge sits at e - R:
#
#     R      ecc    inner edge   max departure from vertical
#    0.60    1.40      0.80            25 deg
#    0.65    1.35      0.70            29 deg     <- here
#    0.70    1.30      0.60            33 deg
#    1.00    1.00      0.00            90 deg     <- reaches fixation; the
#                                                    approximation fails outright
#
# The model's own 2 deg RF at 1 deg eccentricity (HANDOFF_2026-07-27) is the last
# row: it swallows the fovea, where local motion is nowhere near vertical, and
# where the newer experiments — and S&B — exclude dots anyway. 0.65 keeps the
# inner edge at 0.70 deg, clear of the 0.47 deg exclusion zone, and still leaves
# the two V1 RFs sitting inside it with clearance to spare.
MT_R_DEG     = 0.65
MT_ECC_DEG   = APERTURE_DEG - MT_R_DEG
MT_C         = (MT_ECC_DEG, 0.0)

# ── motion ──
OMEGA_DEG_S  = 81.0                 # Stoner & Blanc 2010
PROBE_DEG_S  = 2.26                 # hcpsDefaults.probeDegPerSec
PRE_MS       = 100.0                # rotation shown before the probe; hcps_twops default
TRANS_MS     = 40.0                 # parameters.T_TRANS (3 frames @ 75 Hz)
TRANSLATING_FIELD = "cued"          # "cued" (green) or "uncued" (red)

# ── sampling of the window, used when checking dots against the V1 RFs ──
SEARCH_FRAMES = 21

# How evenly the dots outside the RFs are spread. Best-candidate sampling draws
# SPREAD_K random candidates per dot and keeps the one farthest from those already
# placed. 1 = plain uniform random, which visibly clumps; large values tend to a
# lattice. Measured over the 64 dots outside the MT RF:
#     k=1   spacing CV 0.64   left/right 45/19   (area predicts 36/28)
#     k=6   spacing CV 0.36   left/right 38/26
#     k=14  spacing CV 0.16   left/right 34/30   -- too regular to read as drawn
SPREAD_K      = 6


# ═══════════════════════════════════════════════════════════ geometry ══
def _field(n, rng):
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


def dot_trajectory(p0, sense, translates):
    """PRE_MS of rigid rotation, then TRANS_MS of either the rightward probe (if
    the dot's field translates) or continued rotation. One definition for every
    dot; paths are never re-positioned."""
    pre = _rotation_path(p0, sense, PRE_MS)
    during = (_translation_path(pre[-1], TRANS_MS) if translates
              else _rotation_path(pre[-1], sense, TRANS_MS))
    return pre, during


def _positions_at(p0, sense, translates, t_s):
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


# ═══════════════════════════════════════════════════ BUILD THE LAYOUT ══
# The layout is CONSTRUCTED, not searched (GS: "let's cheat a little"). Earlier
# versions hunted thousands of random layouts for one that happened to put a
# single persistent dot in each V1 RF; that worked but made every other property
# — dot counts in the MT RF, their red/green balance, how well centred the paths
# were — a hostage to whichever seed happened to qualify. Building it directly
# fixes all of them at once, and the construction preserves DENSITY exactly:
#
#     per field:  1 selected  +  3 filler (in the MT RF)  +  32 pepper  =  36
#                 = DENSITY x (annulus area), the same as a random field
#
# The two V1 RFs are placed symmetrically about the MT RF centre rather than
# found, so they are inside it by construction.
RF_LEFT  = (MT_C[0] - _SEP / 2, MT_C[1])
RF_RIGHT = (MT_C[0] + _SEP / 2, MT_C[1])
ECC_DEG  = float(np.hypot(*MT_C))

_TS = np.linspace(0.0, (PRE_MS + TRANS_MS) / 1000.0, SEARCH_FRAMES)


def _centred_start(rf_c, sense, translates, iters=8):
    """The start position whose WHOLE trajectory sits centred in `rf_c`.

    We choose where the dot starts so its real path lands centred — as opposed to
    drawing the path elsewhere and sliding it over, which earlier versions did and
    which misrepresents where the dot actually is. Iterates because the arc is
    struck about fixation, so moving the start changes the path slightly; it is
    nearly straight at this scale, so a few passes converge.
    """
    p = np.asarray(rf_c, float).copy()
    for _ in range(iters):
        pre, during = dot_trajectory(p, sense, translates)
        full = np.vstack([pre, during])
        centre = (full[0] + full[-1]) / 2.0      # min enclosing circle (Thales)
        p = p + (np.asarray(rf_c, float) - centre)
    return p


def _clears_v1(p0, sense, translates):
    """True if this dot never overlaps either V1 RF, at any sampled frame. Applied
    to every non-selected dot, so each V1 RF really does hold one dot and only
    one throughout — the property the whole figure depends on."""
    keep = RF_R_DEG + DOT_DIAM_DEG / 2
    pts = np.asarray(p0, float)[None, :]
    for t in _TS:
        q = _positions_at(pts, sense, translates, t)[0]
        if (np.hypot(q[0] - RF_LEFT[0], q[1] - RF_LEFT[1]) < keep or
                np.hypot(q[0] - RF_RIGHT[0], q[1] - RF_RIGHT[1]) < keep):
            return False
    return True


def _sample_spread(n_each, rng, accept, senses, k=None, tries=4000):
    """Blue-noise sampling: place 2 x `n_each` dots (alternating colour) so the
    UNION of the two fields is evenly spread, while each position is still drawn
    at random.

    Independent uniform sampling clumps — that is correct for a real stimulus and
    wrong for an illustration, where a chance run of dots on one side reads as a
    property of the display rather than of the draw. For each new dot we take `k`
    random candidates and keep whichever lies farthest from everything already
    placed (Mitchell's best-candidate). Spacing against BOTH fields, not each
    separately, is what keeps the union even rather than only each colour.

    `k` sets how far from uniform it stays: k=1 is plain random, large k tends to
    a lattice. 14 is enough to remove visible clumping while still looking drawn.
    """
    k = SPREAD_K if k is None else k
    placed = []
    out = {"A": [], "B": []}
    for i in range(2 * n_each):
        which = "A" if i % 2 == 0 else "B"
        sense, translates = senses[which]
        best_p, best_d = None, -1.0
        for _ in range(k):
            for _ in range(tries):
                r = np.sqrt(rng.uniform(EXCL_DEG**2, (APERTURE_DEG - 0.04)**2))
                a = rng.uniform(0, 2 * np.pi)
                p = np.array([r * np.cos(a), r * np.sin(a)])
                if accept(p) and _clears_v1(p, sense, translates):
                    break
            else:
                raise RuntimeError("could not place a dot in this region")
            d = (min(np.hypot(*(p - q)) for q in placed) if placed else np.inf)
            if d > best_d:
                best_d, best_p = d, p
        placed.append(best_p)
        out[which].append(best_p)
    return out["A"], out["B"]


def build_layout(seed=7):
    """One dot in each V1 RF, an equal number of each colour elsewhere inside the
    MT RF, then the rest peppered over the stimulus at the same density."""
    rng = np.random.default_rng(seed)
    trA = (TRANSLATING_FIELD == "uncued")       # red  = field A = CCW = uncued
    trB = (TRANSLATING_FIELD == "cued")         # green = field B = CW = cued

    # 1. the two selected dots, positioned so their paths lie inside their RFs
    a0 = _centred_start(RF_LEFT, "CCW", trA)
    b0 = _centred_start(RF_RIGHT, "CW", trB)

    # 2. equal numbers of each colour inside the MT RF but outside the V1 RFs
    mt_area = np.pi * MT_R_DEG**2 - 2 * np.pi * RF_R_DEG**2
    n_fill = int(round(DENSITY * mt_area))
    in_mt = lambda p: np.hypot(p[0] - MT_C[0], p[1] - MT_C[1]) < MT_R_DEG - DOT_DIAM_DEG / 2
    senses = {"A": ("CCW", trA), "B": ("CW", trB)}
    fill_a, fill_b = _sample_spread(n_fill, rng, in_mt, senses)

    # 3. the rest of the display, same density
    n_pep = N_DOTS - 1 - n_fill
    out_mt = lambda p: np.hypot(p[0] - MT_C[0], p[1] - MT_C[1]) > MT_R_DEG + DOT_DIAM_DEG / 2
    pep_a, pep_b = _sample_spread(n_pep, rng, out_mt, senses)

    A = np.vstack([a0[None, :]] + [np.asarray(fill_a), np.asarray(pep_a)])
    B = np.vstack([b0[None, :]] + [np.asarray(fill_b), np.asarray(pep_b)])
    return A, B, 0, 0, n_fill, n_pep


FIELD_A, FIELD_B, IDX_A, IDX_B, N_FILL, N_PEPPER = build_layout()


def selected(which):
    """(start position, colour, sense, translates, RF centre) for a chosen dot."""
    if which == "left":
        return (FIELD_A[IDX_A], RED, "CCW", TRANSLATING_FIELD == "uncued", RF_LEFT)
    return (FIELD_B[IDX_B], GREEN, "CW", TRANSLATING_FIELD == "cued", RF_RIGHT)


def dots_in(centre, radius):
    """Every dot whose START position lies in a region — used by the blow-ups."""
    out = []
    for pts, colour, sense, role in [(FIELD_B, GREEN, "CW", "cued"),
                                     (FIELD_A, RED, "CCW", "uncued")]:
        translates = (role == TRANSLATING_FIELD)
        for p in pts:
            if np.hypot(p[0] - centre[0], p[1] - centre[1]) < radius:
                out.append((p, colour, sense, translates))
    return out


# ═══════════════════════════════════════════════════════════ drawing ══
def draw_trajectory(ax, pre, during, colour, lw_pre, lw_during, head, z,
                    alpha_pre=0.55):
    """Thin pre-probe segment, thick probe segment, arrowhead at the end."""
    ax.plot(pre[:, 0], pre[:, 1], color=colour, lw=lw_pre, alpha=alpha_pre,
            solid_capstyle="round", zorder=z)
    ax.plot(during[:, 0], during[:, 1], color=colour, lw=lw_during,
            solid_capstyle="round", zorder=z)
    ax.add_patch(FancyArrowPatch(during[-2], during[-1], arrowstyle="-|>",
                 mutation_scale=head, color=colour, lw=0, zorder=z))


def draw_stimulus(ax, show_v1_rfs=False, legend=True):
    """THE shared stimulus panel. Dots only — no motion is drawn here.

    `show_v1_rfs` is the ONLY thing that differs between the two figures.
    """
    ax.set_aspect("equal"); ax.axis("off")
    lim = APERTURE_DEG + 0.14
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)

    ax.add_patch(Circle((0, 0), APERTURE_DEG, facecolor="#fafafa",
                        edgecolor=INK, lw=1.6, zorder=0))
    ax.add_patch(Circle(MT_C, MT_R_DEG, facecolor="#e2e0dc",
                        edgecolor="none", zorder=1))

    for pts, colour in [(FIELD_B, GREEN), (FIELD_A, RED)]:
        for p in pts:
            ax.add_patch(Circle(p, DOT_DIAM_DEG / 2, facecolor=colour,
                                edgecolor="none", zorder=4))

    if show_v1_rfs:
        for c in (RF_LEFT, RF_RIGHT):
            ax.add_patch(Circle(c, RF_R_DEG, facecolor="none", edgecolor=INK,
                                lw=2.0, zorder=6))

    ax.plot(0, 0, marker="+", ms=12, mew=2.2, color=INK, zorder=9)

    ax.annotate("Area MT RF",
                xy=(MT_C[0] + MT_R_DEG * 0.70, MT_C[1] + MT_R_DEG * 0.70),
                xytext=(MT_C[0] + MT_R_DEG * 0.80, APERTURE_DEG - 0.08),
                ha="left", va="bottom", fontsize=10, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0, shrinkB=3))
    if show_v1_rfs:
        ax.annotate("Area V1 RFs", xy=(RF_RIGHT[0] + RF_R_DEG * 0.70,
                                       RF_RIGHT[1] - RF_R_DEG * 0.70),
                    xytext=(MT_C[0] + MT_R_DEG * 0.62,
                            MT_C[1] - MT_R_DEG * 1.30),
                    ha="left", va="top", fontsize=10, color=INK,
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0, shrinkB=3))

    if legend:
        ax.legend(handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=GREEN,
                   markersize=7, label="CW field  (cued / delayed)"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=RED,
                   markersize=7, label="CCW field  (uncued / first-on)")],
            loc="upper left", frameon=False, fontsize=9,
            handletextpad=0.4, borderpad=0.2)


def excursion(path, rf_c):
    """Furthest the dot's EDGE gets from an RF centre, over the whole path."""
    d = np.hypot(*(np.asarray(path) - np.asarray(rf_c)).T)
    return float(d.max()) + DOT_DIAM_DEG / 2


def report():
    from collections import Counter
    ins = dots_in(MT_C, MT_R_DEG)
    c = Counter(col for _, col, _, _ in ins)
    arc = np.radians(OMEGA_DEG_S) * ECC_DEG * PRE_MS / 1000.0
    print(f"density        {DENSITY} dots/deg^2/field ({N_DOTS} per field)"
          f"   [experiment 5.0]")
    print(f"dot            {DOT_DIAM_DEG} deg  [VRDots; S&B is 0.03]")
    print(f"V1 RF          {RF_DIAM_DEG:.2f} deg diameter, fixed")
    print(f"MT RF          r {MT_R_DEG} at ecc {MT_ECC_DEG:.2f}; outer edge "
          f"{MT_ECC_DEG + MT_R_DEG:.2f} = aperture {APERTURE_DEG}, inner edge "
          f"{MT_ECC_DEG - MT_R_DEG:.2f}")
    print(f"               max departure of local motion from vertical: "
          f"{np.degrees(np.arcsin(MT_R_DEG / MT_ECC_DEG)):.0f} deg")
    print(f"\nLAYOUT CONSTRUCTED, not searched:")
    print(f"  per field    1 selected + {N_FILL} filler (in the MT RF) + "
          f"{N_PEPPER} pepper = {1 + N_FILL + N_PEPPER}  (density target {N_DOTS})")
    print(f"  in the MT RF {len(ins)} dots -> green {c[GREEN]}, red {c[RED]}")
    print(f"  V1 RFs       placed symmetrically about the MT RF centre, so inside "
          f"it by construction")
    print(f"  every other dot is verified to clear BOTH V1 RFs at all "
          f"{SEARCH_FRAMES} sampled frames")
    print(f"\nCONTAINMENT of the two selected dots (edge, not centre):")
    for which in ("left", "right"):
        p0, _, sense, tr, rf_c = selected(which)
        pre, during = dot_trajectory(p0, sense, tr)
        exc = excursion(np.vstack([pre, during]), rf_c)
        e = np.hypot(*rf_c)
        print(f"  {which:5s} ecc {e:.3f}  edge reaches {exc:.4f} of RF radius "
              f"{RF_R_DEG:.4f}  -> margin {RF_R_DEG/exc:.2f}x")
        assert exc < RF_R_DEG, f"{which} dot leaves its RF"
    print(f"  pre-probe arc {arc/DOT_DIAM_DEG:.1f} dot-widths at the pair centre")
