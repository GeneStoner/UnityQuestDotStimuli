"""
Toy point-set model, figures A and B — two side-by-side V1 RFs, one dot in each.

Composition follows `fig_modelI_stimulus.png` (SurfaceSelectionModel repo,
LatestTurkey/ToyModel/): the stimulus disc, a large MT receptive field, and inside
it TWO adjacent V1 RFs — the left holding a RED dot, the right a GREEN dot. Palette
and conventions follow Figure 2 of the website's computational section
(`mt_rf_figure.py`), since these are destined for the same page.

  A  the stimulus, the MT RF, and the two V1 RFs with one dot in each.
  B  those two V1 RFs magnified, with each dot's trajectory over the pre-probe
     rotation and the probe itself.

RF SIZE — fixed, NOT scaled with eccentricity (GS: for the toy model we do not
scale), and drawn at the UPPER END of what can still honestly be called a V1
receptive field, because this is a schematic:

    sigma = 0.24 deg   ->   RF diameter 2*sigma = 0.48 deg   at E = 1 deg

Just under the ceiling, so the two RF circles carry a visible gap rather than
touching (RF_GAP_DEG). The ceiling itself is 0.52 deg, where two independent
human estimates agree: Dumoulin & Wandell (2008) pRF, sigma = 0.1 + 0.15*E; and
Freeman & Simoncelli (2011) V1 pooling, s = 0.26*E. For scale, at the same
eccentricity Dow 1981 cRF is 0.13, `hcps_rfrule('small')` (= the MT patch the
model runs) is 0.24, and 'large' is 0.38. Absolute limit ~0.65 (5x cRF, top of
the summation-field range); past that the figure would be depicting V2 pooling
or an fMRI population, not V1. See Agents/SwapPilot/WriteUps/v1_rf_sizes.md.

CONTAINMENT — the model's central assumption, checked rather than assumed. The
dot's whole extent, not just its centre, must stay inside one RF for the pre-probe
rotation AND the probe. Windows: 100 ms rotation + 40 ms probe.

    non-translating dot   straight run of omega*E*(PRE+PROBE)      = 0.1979 deg
    translating dot       L-path, hypot(rotation, translation)     = 0.1678 deg
    + dot diameter (Minkowski sum with a disc)                     + 0.03 deg
    ------------------------------------------------------------------------
    required 0.2279 deg   vs   RF 0.48 deg      ->  margin 2.11x

⚠️ THE DRAWN PAIR IS SELECTED, NOT TYPICAL. At 0.48 deg an RF holds ~0.91 dots
per field on average, so P(the other surface also intrudes) ~ 60%. A point-set
seeing exactly one surface is the exception at this RF size — which is precisely
why `hcps_twops.m` has to SEARCH for such pairs across layout seeds rather than
assume them. Any caption must not imply purity is generic.

Turning is CHEAPER than going straight, so the binding case is the dot that keeps
rotating through the probe. The script asserts the fit, so it cannot regress.

Numbers, all sourced:
  omega    81 deg/s     rotation speed (Stoner & Blanc 2010)
  probe    40 ms        parameters.T_TRANS (3 frames @ 75 Hz)
  probe v  2.26 deg/s   hcpsDefaults.probeDegPerSec
  dot      0.03 deg     S&B (1 CRT pixel); VRDots uses 0.08 — see
                        Agents/SwapPilot/WriteUps/stimulus_specs_website_experiments.md
  density  5 dots/deg^2/field (S&B 2010)

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
DENSITY      = 5.0                  # dots / deg^2 / field
N_DOTS       = int(round(DENSITY * np.pi * (APERTURE_DEG**2 - EXCL_DEG**2)))
DOT_DIAM_DEG = 0.03                 # S&B dot; VRDots = 0.08

# ── the RFs: FIXED size, not scaled with eccentricity ──
ECC_DEG      = 1.0                  # the MT patch's own eccentricity
SIGMA_DEG    = 0.24                 # just under the upper end of realistic V1 at E=1:
                                    # Dumoulin pRF (0.1+0.15E) and Freeman&Simoncelli
                                    # V1 pooling (0.26E) both cap at 2*sigma = 0.52.
                                    # 0.19 -> hcps_rfrule('large'); 0.12 -> 'small'
RF_GAP_DEG   = 0.05                 # clear gap so the two RF circles do not touch
RF_DIAM_DEG  = 2 * SIGMA_DEG
RF_R_DEG     = SIGMA_DEG
_SEP         = RF_DIAM_DEG + RF_GAP_DEG      # centre-to-centre
RF_LEFT      = (ECC_DEG - _SEP / 2, 0.0)
RF_RIGHT     = (ECC_DEG + _SEP / 2, 0.0)
MT_R_DEG     = 0.95                 # the MT RF enclosing both, as in fig_modelI;
                                    # must exceed RF_R_DEG*3 = 0.78 to contain them

# ── motion ──
OMEGA_DEG_S  = 81.0
PROBE_DEG_S  = 2.26
PRE_MS       = 100.0                # pre-probe rotation shown (GS, 2026-08-18)
TRANS_MS     = 40.0
TRACE_MS     = 100.0                # trace length for the background field dots

TRANSLATING_FIELD = "cued"          # "cued" (green) or "uncued" (red)


# ═══════════════════════════════════════════════════════ containment ══
def rot_arc(ms, E=ECC_DEG):
    return np.radians(OMEGA_DEG_S) * E * (ms / 1000.0)


def required_translating():
    return float(np.hypot(rot_arc(PRE_MS), PROBE_DEG_S * TRANS_MS / 1000.0))


def required_straight():
    return rot_arc(PRE_MS + TRANS_MS)


def required_whole_dot():
    return max(required_translating(), required_straight()) + DOT_DIAM_DEG


# ═══════════════════════════════════════════════════════════ helpers ══
def _field(n, seed):
    rng = np.random.default_rng(seed)
    ang = rng.uniform(0, 2 * np.pi, n)
    rs = np.sqrt(rng.uniform(EXCL_DEG**2, (APERTURE_DEG - 0.04)**2, n))
    return np.column_stack([rs * np.cos(ang), rs * np.sin(ang)])


def _clear_of_rfs(pts, pad=0.05):
    keep = []
    for p in pts:
        dl = np.hypot(p[0] - RF_LEFT[0], p[1] - RF_LEFT[1])
        dr = np.hypot(p[0] - RF_RIGHT[0], p[1] - RF_RIGHT[1])
        if dl > RF_R_DEG + pad and dr > RF_R_DEG + pad:
            keep.append(p)
    return np.array(keep)


def _arc_motion(ax, p, fix, sense, color, lw=1.7, head=8, sweep_deg=None):
    p = np.asarray(p, float); fix = np.asarray(fix, float)
    rvec = p - fix
    R = np.hypot(*rvec)
    th0 = np.degrees(np.arctan2(rvec[1], rvec[0]))
    s = -1.0 if sense == "CW" else 1.0
    ths = np.radians(np.linspace(th0, th0 + s * sweep_deg, 16))
    xs = fix[0] + R * np.cos(ths); ys = fix[1] + R * np.sin(ths)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=4)
    ax.add_patch(FancyArrowPatch((xs[-2], ys[-2]), (xs[-1], ys[-1]),
                 arrowstyle="-|>", mutation_scale=head, color=color, lw=0, zorder=4))


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


def _rf_trajectory(rf_c, sense, translates):
    """The dot's path through pre-probe rotation + probe, centred in its RF.

    Used by BOTH figures, so the short trajectory drawn at stimulus scale in A is
    literally the same path B magnifies. Centring uses the minimum enclosing
    circle (endpoints as diameter — the L's corner lies on it, Thales), which
    gives symmetric margin; only the path's position in the RF is a display
    choice, its shape is exact.
    """
    pre = _rotation_path(rf_c, sense, PRE_MS)
    p_switch = pre[-1]
    during = (_translation_path(p_switch, TRANS_MS) if translates
              else _rotation_path(p_switch, sense, TRANS_MS))
    full = np.vstack([pre, during])
    shift = np.asarray(rf_c, float) - (full[0] + full[-1]) / 2.0
    pre, during = pre + shift, during + shift
    span = float(np.hypot(*(full[-1] - full[0]))) + DOT_DIAM_DEG
    return pre, during, span


# ═════════════════════════════════════════════════ A — the stimulus ══
def fig_A(out="ps_two_rf_A.png", show_traj=False):
    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    ax.set_aspect("equal"); ax.axis("off")
    lim = APERTURE_DEG + 0.5
    ax.set_xlim(-lim, lim + 2.3); ax.set_ylim(-lim, lim)

    ax.add_patch(Circle((0, 0), APERTURE_DEG, facecolor="#fafafa",
                        edgecolor=INK, lw=1.6, zorder=0))

    # the MT receptive field — the large pooling field of fig_modelI
    ax.add_patch(Circle((ECC_DEG, 0.0), MT_R_DEG, facecolor="#e7e5e1",
                        edgecolor="none", zorder=1))

    sweep = OMEGA_DEG_S * TRACE_MS / 1000.0
    g = _clear_of_rfs(_field(N_DOTS, seed=11))
    r = _clear_of_rfs(_field(N_DOTS, seed=12))
    for p in g:
        ax.scatter(*p, s=7, color=GREEN, zorder=3)
        _arc_motion(ax, p, (0, 0), "CW", GREEN, lw=1.1, head=6, sweep_deg=sweep)
    for p in r:
        ax.scatter(*p, s=7, color=RED, zorder=3)
        _arc_motion(ax, p, (0, 0), "CCW", RED, lw=1.1, head=6, sweep_deg=sweep)

    # the two V1 RFs, side by side, FIXED size
    for c in (RF_LEFT, RF_RIGHT):
        ax.add_patch(Circle(c, RF_R_DEG, facecolor=SURFACE, edgecolor=INK,
                            lw=1.8, zorder=6))

    # one dot in each RF, at TRUE angular size.
    #   show_traj=False -> a static snapshot: just the two dots
    #   show_traj=True  -> the SAME short path B magnifies, drawn at stimulus scale
    for rf_c, colour, sense, role in [(RF_LEFT, RED, "CCW", "uncued"),
                                      (RF_RIGHT, GREEN, "CW", "cued")]:
        if show_traj:
            pre, during, _ = _rf_trajectory(rf_c, sense,
                                            role == TRANSLATING_FIELD)
            ax.plot(pre[:, 0], pre[:, 1], color=colour, lw=1.3, alpha=0.55,
                    solid_capstyle="round", zorder=7)
            ax.plot(during[:, 0], during[:, 1], color=colour, lw=2.0,
                    solid_capstyle="round", zorder=7)
            ax.add_patch(FancyArrowPatch(during[-2], during[-1],
                         arrowstyle="-|>", mutation_scale=8, color=colour,
                         lw=0, zorder=7))
            head = pre[0]
        else:
            head = rf_c
        ax.add_patch(Circle(head, DOT_DIAM_DEG / 2, facecolor=colour,
                            edgecolor="none", zorder=8))

    ax.plot(0, 0, marker="+", ms=12, mew=2.2, color=INK, zorder=9)

    ax.annotate("Area MT RF", xy=(ECC_DEG + MT_R_DEG * 0.72, MT_R_DEG * 0.72),
                xytext=(APERTURE_DEG + 0.45, 1.15), ha="left", va="center",
                fontsize=10.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0, shrinkB=3))
    ax.annotate("Area V1 RFs", xy=(RF_RIGHT[0] + RF_R_DEG, 0.0),
                xytext=(APERTURE_DEG + 0.45, 0.30), ha="left", va="center",
                fontsize=10.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0, shrinkB=3))

    ax.legend(handles=[
        Line2D([0], [0], color=GREEN, lw=2.2, label="CW field  (cued / delayed)"),
        Line2D([0], [0], color=RED, lw=2.2, label="CCW field  (uncued / first-on)")],
        loc="upper right", frameon=False, fontsize=9)

    sub = ("one dot in each of two V1 RFs — with its short trajectory" if show_traj
           else "one dot in each of two V1 RFs")
    ax.set_title(f"A · Two counter-rotating fields, {sub}",
                 fontsize=12, color=INK, pad=8)
    lam = DENSITY * np.pi * RF_R_DEG**2
    ax.text(0, -lim + 0.30,
            f"V1 RF {RF_DIAM_DEG:.2f}° diameter (σ {SIGMA_DEG:g}°) at {ECC_DEG:g}° — fixed, not "
            f"scaled with eccentricity · dots {DOT_DIAM_DEG:g}° · {DENSITY:g} dots/deg²/field",
            ha="center", va="bottom", fontsize=8.5, color=INK2)
    ax.text(0, -lim + 0.13,
            f"A point-set seeing one surface only is a SELECTED configuration: at this RF size "
            f"an RF holds ~{lam:.2f} dots/field, so the other surface intrudes ~{1-np.exp(-lam):.0%} "
            f"of the time",
            ha="center", va="bottom", fontsize=8, color=INK2, style="italic")

    fig.tight_layout()
    fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# ══════════════════════════════════════ B — the RFs magnified, trajs ══
def fig_B(out="ps_two_rf_B.png"):
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.9))
    specs = [
        (axes[0], RF_LEFT,  RED,   "CCW", "uncued",
         "left V1 RF · red dot", "CCW field — first-on (uncued)"),
        (axes[1], RF_RIGHT, GREEN, "CW",  "cued",
         "right V1 RF · green dot", "CW field — delayed-onset (cued)"),
    ]
    for ax, rf_c, colour, sense, role, panel_lab, sub in specs:
        ax.set_aspect("equal"); ax.axis("off")
        pad = RF_R_DEG * 0.40
        ax.set_xlim(rf_c[0] - RF_R_DEG - pad, rf_c[0] + RF_R_DEG + pad)
        ax.set_ylim(rf_c[1] - RF_R_DEG - pad, rf_c[1] + RF_R_DEG + pad * 1.4)
        ax.add_patch(Circle(rf_c, RF_R_DEG, facecolor=SURFACE, edgecolor=INK,
                            lw=2.0, zorder=1))

        translates = (role == TRANSLATING_FIELD)
        pre = _rotation_path(rf_c, sense, PRE_MS)
        p_switch = pre[-1]
        during = (_translation_path(p_switch, TRANS_MS) if translates
                  else _rotation_path(p_switch, sense, TRANS_MS))
        full = np.vstack([pre, during])
        # centre the path's minimum enclosing circle (endpoints as diameter — the
        # corner of the L lies on it, Thales) on the RF centre: symmetric margin
        shift = np.asarray(rf_c, float) - (full[0] + full[-1]) / 2.0
        pre, during = pre + shift, during + shift
        p0, p_switch = pre[0], pre[-1]
        span = float(np.hypot(*(full[-1] - full[0]))) + DOT_DIAM_DEG

        ax.plot(pre[:, 0], pre[:, 1], color=colour, lw=2.0, alpha=0.55,
                solid_capstyle="round", zorder=3)
        ax.plot(during[:, 0], during[:, 1], color=colour, lw=3.4,
                solid_capstyle="round", zorder=4)
        ax.add_patch(FancyArrowPatch(during[-2], during[-1], arrowstyle="-|>",
                     mutation_scale=17, color=colour, lw=0, zorder=5))
        ax.add_patch(Circle(p0, DOT_DIAM_DEG / 2, facecolor=colour,
                            edgecolor="none", zorder=6))
        ax.add_patch(Circle(p_switch, DOT_DIAM_DEG / 2, facecolor="white",
                            edgecolor=colour, lw=1.6, zorder=6))

        note = ("rotation replaced by\nrightward translation" if translates
                else "rotation continues\nunchanged")
        ax.text(rf_c[0], rf_c[1] + RF_R_DEG + pad * 0.5, note, ha="center",
                va="bottom", fontsize=9.5, color=colour, fontweight="bold")
        ax.text(rf_c[0], rf_c[1] - RF_R_DEG - pad * 0.5,
                f"dot + path spans {span:.3f}° in a {RF_DIAM_DEG:.2f}° RF "
                f"({RF_DIAM_DEG/span:.2f}× margin)",
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
    fig.suptitle("B · The same two V1 RFs, magnified — dot trajectories through the probe",
                 fontsize=12.5, color=INK, y=0.99)
    fig.text(0.5, 0.055,
             f"rotation {OMEGA_DEG_S:g}°/s ({np.radians(OMEGA_DEG_S)*ECC_DEG:.2f}°/s tangential "
             f"at {ECC_DEG:g}°) · translation {PROBE_DEG_S:g}°/s · RF {RF_DIAM_DEG:.2f}° diameter, fixed",
             ha="center", va="bottom", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    need = required_whole_dot()
    print(f"N_DOTS per field   = {N_DOTS}   ({DENSITY} dots/deg^2/field)")
    print(f"RF                 = {RF_DIAM_DEG:.3f} deg diameter (sigma {SIGMA_DEG}), FIXED")
    print(f"eccentricity       = {ECC_DEG} deg, tangential {np.radians(OMEGA_DEG_S)*ECC_DEG:.3f} deg/s\n")
    print("CONTAINMENT (whole dot, not just its centre):")
    print(f"  non-translating (straight) {required_straight():.4f}   <- binding")
    print(f"  translating     (L-path)   {required_translating():.4f}")
    print(f"  + dot {DOT_DIAM_DEG:g}              = {need:.4f}")
    print(f"  RF provides                {RF_DIAM_DEG:.4f}  -> margin {RF_DIAM_DEG/need:.2f}x")
    assert need < RF_DIAM_DEG, "whole dot does not fit inside the RF"
    lam = DENSITY * np.pi * RF_R_DEG**2
    print(f"\nPURITY (the drawn pair is SELECTED, not typical):")
    print(f"  dots per field per RF = {lam:.3f}"
          f"  -> P(other surface intrudes) = {1-np.exp(-lam):.0%}")
    print()
    fig_A("ps_two_rf_A_static.png", show_traj=False)
    fig_A("ps_two_rf_A_traj.png",   show_traj=True)
    fig_B()
