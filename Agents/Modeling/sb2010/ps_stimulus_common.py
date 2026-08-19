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

THE V1 PAIR IS FOUND, NOT PLACED
--------------------------------
`find_pure_pair` moves both dot fields through the whole window and searches
layout seed x pair-centre offset for two adjacent RF-sized regions where, on every
sampled frame:

    left RF   exactly one dot of field A (red, uncued), the SAME dot throughout,
              wholly inside; no dot of field B overlaps at all
    right RF  the same for field B (green, cued)

Identity persistence is the part that matters: "one dot per frame" alone would
allow one dot leaving as another arrives. Offsets are drawn from a disc of radius
`_PLAY` about `MT_C`, so both V1 RFs sitting inside the MT RF is guaranteed by the
search space rather than arranged by eye. Nothing is deleted from the display.

Run either figure script; this module does the search on import.
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
MT_ECC_DEG   = 1.05
MT_R_DEG     = 0.70                 # 35% of the aperture radius, matching fig_modelI
MT_C         = (MT_ECC_DEG, 0.0)

# ── motion ──
OMEGA_DEG_S  = 81.0                 # Stoner & Blanc 2010
PROBE_DEG_S  = 2.26                 # hcpsDefaults.probeDegPerSec
PRE_MS       = 100.0                # rotation shown before the probe; hcps_twops default
TRANS_MS     = 40.0                 # parameters.T_TRANS (3 frames @ 75 Hz)
TRANSLATING_FIELD = "cued"          # "cued" (green) or "uncued" (red)

# ── the search ──
SEARCH_SEEDS  = range(1, 600)
SEARCH_FRAMES = 21
SEARCH_STEP   = 0.04
_PLAY         = MT_R_DEG - _SEP / 2 - RF_R_DEG   # both V1 RFs stay inside the MT RF
GOOD_ENOUGH   = 1.30
MT_MIN_DOTS   = 7                   # the SAME layout feeds Figure 2's MT-RF blow-up,
                                    # so reject seeds that leave that panel empty.
                                    # This trades against how well centred the V1
                                    # pair is; measured over 599 seeds:
                                    #   min 0 -> best margin 1.40x, but 3 dots
                                    #   min 7 -> 1.31x with 7 dots   <- the knee
                                    #   min 8 -> 1.10x with 9 dots


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


def find_pure_pair(seeds=SEARCH_SEEDS, whole_dot=True):
    """Search for the two-point-set configuration. `whole_dot=True` requires the
    wanted dot to lie WHOLLY inside its RF and rejects any overlap by the other
    surface — stricter than testing centres, and the right test now that dots are
    drawn at a visible size."""
    r_in = RF_R_DEG - DOT_DIAM_DEG / 2 if whole_dot else RF_R_DEG
    r_out = RF_R_DEG + DOT_DIAM_DEG / 2 if whole_dot else RF_R_DEG
    ts = np.linspace(0.0, (PRE_MS + TRANS_MS) / 1000.0, SEARCH_FRAMES)
    offs = [(dx, dy)
            for dx in np.arange(-_PLAY, _PLAY + 1e-9, SEARCH_STEP)
            for dy in np.arange(-_PLAY, _PLAY + 1e-9, SEARCH_STEP)
            if dx * dx + dy * dy <= _PLAY * _PLAY]
    trA = (TRANSLATING_FIELD == "uncued")
    trB = (TRANSLATING_FIELD == "cued")
    best = None
    for seed in seeds:
        rng = np.random.default_rng(seed)
        A = _field(N_DOTS, rng)                     # red, CCW, uncued
        B = _field(N_DOTS, rng)                     # green, CW, cued
        # cheap reject first: this layout also has to populate Figure 2's blow-up
        n_mt = int((np.hypot(*(np.vstack([A, B]) - np.array(MT_C)).T)
                    < MT_R_DEG).sum())
        if n_mt < MT_MIN_DOTS:
            continue
        PA = [_positions_at(A, "CCW", trA, t) for t in ts]
        PB = [_positions_at(B, "CW", trB, t) for t in ts]
        for dx, dy in offs:
            cx, cy = MT_C[0] + dx, MT_C[1] + dy
            Lc = np.array([cx - _SEP / 2, cy]); Rc = np.array([cx + _SEP / 2, cy])
            inAL = [set(np.where(np.hypot(*(pa - Lc).T) < r_in)[0]) for pa in PA]
            if any(len(s_) != 1 for s_ in inAL): continue
            inBR = [set(np.where(np.hypot(*(pb - Rc).T) < r_in)[0]) for pb in PB]
            if any(len(s_) != 1 for s_ in inBR): continue
            iA = set.intersection(*inAL); iB = set.intersection(*inBR)
            if not iA or not iB: continue
            if any((np.hypot(*(pb - Lc).T) < r_out).any() for pb in PB): continue
            if any((np.hypot(*(pa - Rc).T) < r_out).any() for pa in PA): continue
            jA, jB = iA.pop(), iB.pop()
            worst = max(max(np.hypot(*(pa[jA] - Lc)) for pa in PA),
                        max(np.hypot(*(pb[jB] - Rc)) for pb in PB)) + DOT_DIAM_DEG / 2
            margin = RF_R_DEG / worst
            if best is None or margin > best["margin"]:
                best = dict(seed=seed, A=A, B=B, Lc=Lc, Rc=Rc, iA=jA, iB=jB,
                            margin=margin, off=(float(dx), float(dy)),
                            whole_dot=whole_dot)
        if best is not None and best["margin"] >= GOOD_ENOUGH:
            break
    return best


# ── one search, at import; both figures read its result ──
PAIR = find_pure_pair(whole_dot=True)
_STRICT = PAIR is not None
if PAIR is None:                        # documented fallback, per the plan
    PAIR = find_pure_pair(whole_dot=False)
if PAIR is None:
    raise RuntimeError("no layout gave a persistent one-dot-each pair; "
                       "lower DENSITY or widen SEARCH_SEEDS")

FIELD_A, FIELD_B = PAIR["A"], PAIR["B"]
RF_LEFT, RF_RIGHT = tuple(PAIR["Lc"]), tuple(PAIR["Rc"])
IDX_A, IDX_B = PAIR["iA"], PAIR["iB"]
ECC_DEG = float(np.hypot((RF_LEFT[0] + RF_RIGHT[0]) / 2,
                         (RF_LEFT[1] + RF_RIGHT[1]) / 2))


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
    lam = DENSITY * np.pi * RF_R_DEG**2
    print(f"density        {DENSITY} dots/deg^2/field ({N_DOTS} per field)"
          f"   [experiment 5.0]")
    print(f"dot            {DOT_DIAM_DEG} deg  [VRDots; S&B is 0.03]")
    print(f"V1 RF          {RF_DIAM_DEG:.2f} deg diameter, fixed")
    print(f"MT RF          centre {MT_C}, radius {MT_R_DEG}")
    print(f"PAIR           seed {PAIR['seed']}, centre {ECC_DEG:.3f} deg from "
          f"fixation, offset {PAIR['off']} of an allowed {_PLAY:.2f}")
    crit = ("whole dot inside, no overlap by the other surface" if _STRICT
            else "CENTRES only — the strict whole-dot test found nothing")
    print(f"               criterion: {crit}")
    for which in ("left", "right"):
        p0, _, sense, tr, rf_c = selected(which)
        pre, during = dot_trajectory(p0, sense, tr)
        exc = excursion(np.vstack([pre, during]), rf_c)
        print(f"  {which:5s} dot edge reaches {exc:.4f} of RF radius "
              f"{RF_R_DEG:.4f}  -> margin {RF_R_DEG/exc:.2f}x")
        assert exc < RF_R_DEG, f"{which} dot leaves its RF"
    print(f"context        {lam:.2f} dots/field per RF -> other surface intrudes "
          f"{1-np.exp(-lam):.0%} of the time; this pair is rare")
