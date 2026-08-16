"""
Point-set section, figures A and B — the two-V1-cRF picture.

Modelled on mt_rf_figure.py (Figure 2 of the computational section), same palette
and same right-side-RF convention, but the RF is no longer one big MT field: it is
a PAIR of adjacent V1 cRFs, drawn AT TRUE SIZE, with exactly one dot in each.

  A  the stimulus — two counter-rotating transparent fields — with two adjacent
     V1 cRFs side by side just right of fixation. One red dot lands in the left
     cRF, one green dot in the right cRF, and nothing else does. That is the
     point-set premise made visible: at S&B density each cRF is dominated by ONE
     surface, so surface identity can be carried by WHICH cRF responds.

  B  those same two cRFs blown up, showing each dot's trajectory over the 40 ms
     before the translation and the 40 ms of the translation itself.

Geometry / convention (inherited from mt_rf_figure.py, kept identical):
  the cRFs sit directly RIGHT of fixation, so the CW field's local motion is DOWN
  and the CCW field's is UP. The test translation is orthogonal to that axis,
  i.e. RIGHTWARD (the "brief rightward probe" of the HC/PS schematic).

Numbers, all from the repo rather than invented:
  omega        81 deg/s      rotation speed (Stoner & Blanc 2010)
  T_TRANS      40 ms         translation duration (parameters.py; 3 frames @75 Hz)
  probe        2.26 deg/s    translation speed (hcpsDefaults.probeDegPerSec)
  cRF          0.16 deg diameter, sigma 0.08 deg (Dow 1981 at ~1.3 deg ecc)
  density      5 dots/deg^2/field (S&B 2010)

NOTE on which dot translates: the CUED (green / delayed-onset) field translates,
matching the CUED=green convention in web_figures.py. Flip TRANSLATING_FIELD to
"uncued" to swap it.

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

# ── stimulus geometry, in DEGREES throughout (no unit conversion anywhere) ──
APERTURE_DEG = 2.0                  # 4 deg stimulus, S&B 2010
EXCL_DEG     = 0.47                 # near-fixation exclusion (matches Figure 2)
DENSITY      = 5.0                  # dots / deg^2 / field
N_DOTS       = int(round(DENSITY * np.pi * (APERTURE_DEG**2 - EXCL_DEG**2)))

# ── the two V1 cRFs: adjacent, side by side, right of fixation ──
CRF_DIAM_DEG = 0.16                 # Dow 1981 at ~1.3 deg eccentricity
CRF_R_DEG    = CRF_DIAM_DEG / 2.0
ECC_DEG      = 1.33                 # centre of the PAIR
RF_LEFT      = (ECC_DEG - CRF_R_DEG, 0.0)
RF_RIGHT     = (ECC_DEG + CRF_R_DEG, 0.0)

# ── motion ──
OMEGA_DEG_S  = 81.0                 # angular rotation speed
PROBE_DEG_S  = 2.26                 # translation (probe) speed
PRE_MS       = 40.0                 # window shown before the translation
TRANS_MS     = 40.0                 # translation duration (parameters.T_TRANS)
TRACE_MS     = 100.0                # trace length for the background field dots

TRANSLATING_FIELD = "cued"          # "cued" (green) or "uncued" (red)


# ═══════════════════════════════════════════════════════════════════════════
# helpers
# ═══════════════════════════════════════════════════════════════════════════
def _field(n, seed):
    """Area-uniform dot positions in the annulus, in degrees."""
    rng = np.random.default_rng(seed)
    ang = rng.uniform(0, 2 * np.pi, n)
    rs = np.sqrt(rng.uniform(EXCL_DEG**2, (APERTURE_DEG - 0.04)**2, n))
    return np.column_stack([rs * np.cos(ang), rs * np.sin(ang)])


def _clear_of_rfs(pts, pad=0.055):
    """Drop dots that fall in (or near) either cRF, so each cRF holds exactly
    the one dot we place there deliberately."""
    keep = []
    for p in pts:
        dl = np.hypot(p[0] - RF_LEFT[0], p[1] - RF_LEFT[1])
        dr = np.hypot(p[0] - RF_RIGHT[0], p[1] - RF_RIGHT[1])
        if dl > CRF_R_DEG + pad and dr > CRF_R_DEG + pad:
            keep.append(p)
    return np.array(keep)


def _arc_motion(ax, p, fix, sense, color, lw=1.7, head=8, sweep_deg=None):
    """A true arc of the rigid-rotation circle about ``fix`` through ``p``."""
    p = np.asarray(p, float); fix = np.asarray(fix, float)
    rvec = p - fix
    R = np.hypot(*rvec)
    th0 = np.degrees(np.arctan2(rvec[1], rvec[0]))
    s = -1.0 if sense == "CW" else 1.0
    ths = np.radians(np.linspace(th0, th0 + s * sweep_deg, 16))
    xs = fix[0] + R * np.cos(ths)
    ys = fix[1] + R * np.sin(ths)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=4)
    ax.add_patch(FancyArrowPatch((xs[-2], ys[-2]), (xs[-1], ys[-1]),
                 arrowstyle="-|>", mutation_scale=head, color=color, lw=0,
                 zorder=4))


def _rotation_path(p0, sense, ms, n=64):
    """Positions along the rigid rotation about fixation, for ``ms``."""
    p0 = np.asarray(p0, float)
    R = np.hypot(*p0)
    th0 = np.arctan2(p0[1], p0[0])
    s = -1.0 if sense == "CW" else 1.0
    sweep = np.radians(OMEGA_DEG_S * ms / 1000.0) * s
    ths = th0 + np.linspace(0.0, sweep, n)
    return np.column_stack([R * np.cos(ths), R * np.sin(ths)])


def _translation_path(p0, ms, n=32, direction=(1.0, 0.0)):
    """Pure rightward translation for ``ms`` — during the probe the translating
    field's rotation drive is replaced by the translation (see inputs_figure)."""
    p0 = np.asarray(p0, float)
    d = np.asarray(direction, float)
    dist = PROBE_DEG_S * ms / 1000.0
    ts = np.linspace(0.0, 1.0, n)[:, None]
    return p0[None, :] + ts * dist * d[None, :]


# ═══════════════════════════════════════════════════════════════════════════
# A — the stimulus with two adjacent V1 cRFs
# ═══════════════════════════════════════════════════════════════════════════
def fig_A(out="ps_two_rf_A.png"):
    fig, ax = plt.subplots(figsize=(8.4, 6.6))
    ax.set_aspect("equal"); ax.axis("off")
    lim = APERTURE_DEG + 0.55
    # extra room on the right so the callout sits clear of the aperture
    ax.set_xlim(-lim, lim + 2.15); ax.set_ylim(-lim, lim)

    ax.add_patch(Circle((0, 0), APERTURE_DEG, facecolor="#fafafa",
                        edgecolor=BORDER, lw=1.4, zorder=0))

    sweep = OMEGA_DEG_S * TRACE_MS / 1000.0
    g = _clear_of_rfs(_field(N_DOTS, seed=11))
    r = _clear_of_rfs(_field(N_DOTS, seed=12))
    for p in g:
        ax.scatter(*p, s=7, color=GREEN, zorder=3)
        _arc_motion(ax, p, (0, 0), "CW", GREEN, lw=1.15, head=6, sweep_deg=sweep)
    for p in r:
        ax.scatter(*p, s=7, color=RED, zorder=3)
        _arc_motion(ax, p, (0, 0), "CCW", RED, lw=1.15, head=6, sweep_deg=sweep)

    # the two cRFs, at TRUE size, drawn last so they sit on top
    for c in (RF_LEFT, RF_RIGHT):
        ax.add_patch(Circle(c, CRF_R_DEG, facecolor="#eef2f1", edgecolor=INK,
                            lw=1.7, ls=(0, (4, 2.5)), zorder=6))

    # exactly one dot in each cRF: red in the left, green in the right.
    # No motion arcs here — at true cRF scale they only clutter; B shows them.
    ax.scatter(*RF_LEFT, s=24, color=RED, zorder=8)
    ax.scatter(*RF_RIGHT, s=24, color=GREEN, zorder=8)

    ax.plot(0, 0, marker="+", ms=11, mew=2.0, color=INK, zorder=9)

    # callout, placed OUTSIDE the aperture so it never sits on the dot field
    ax.annotate("two adjacent V1 cRFs,\none dot in each — detail in B",
                xy=(ECC_DEG + CRF_R_DEG, 0.0), xycoords="data",
                xytext=(APERTURE_DEG + 0.42, -0.95), textcoords="data",
                ha="left", va="center", fontsize=9.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0,
                                connectionstyle="arc3,rad=-0.18",
                                shrinkA=0, shrinkB=3))

    ax.legend(handles=[
        Line2D([0], [0], color=GREEN, lw=2.2, label="CW field  (cued / delayed)"),
        Line2D([0], [0], color=RED, lw=2.2, label="CCW field  (uncued / first-on)")],
        loc="upper right", frameon=False, fontsize=9)

    ax.set_title("A · Two counter-rotating fields, two adjacent V1 cRFs",
                 fontsize=12, color=INK, pad=8)
    ax.text(0, -lim + 0.20,
            f"cRF {CRF_DIAM_DEG:g}° diameter (σ {CRF_R_DEG:g}°) at {ECC_DEG:g}° "
            f"eccentricity, drawn at true size · {DENSITY:g} dots/deg²/field",
            ha="center", va="bottom", fontsize=8.5, color=INK2)

    fig.tight_layout()
    fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# ═══════════════════════════════════════════════════════════════════════════
# B — the two cRFs magnified, with each dot's trajectory
# ═══════════════════════════════════════════════════════════════════════════
def fig_B(out="ps_two_rf_B.png"):
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.9))

    specs = [
        (axes[0], RF_LEFT,  RED,   "CCW", "uncued",
         "left cRF · red dot", "CCW field — first-on (uncued)"),
        (axes[1], RF_RIGHT, GREEN, "CW",  "cued",
         "right cRF · green dot", "CW field — delayed-onset (cued)"),
    ]

    for ax, rf_c, colour, sense, role, panel_lab, sub in specs:
        ax.set_aspect("equal"); ax.axis("off")
        pad = CRF_R_DEG * 0.42
        ax.set_xlim(rf_c[0] - CRF_R_DEG - pad, rf_c[0] + CRF_R_DEG + pad)
        ax.set_ylim(rf_c[1] - CRF_R_DEG - pad, rf_c[1] + CRF_R_DEG + pad * 1.5)

        ax.add_patch(Circle(rf_c, CRF_R_DEG, facecolor=SURFACE, edgecolor=INK,
                            lw=2.0, ls=(0, (5, 3)), zorder=1))

        translates = (role == TRANSLATING_FIELD)

        # Build the trajectory from the cRF centre, then rigidly re-centre the
        # whole path in the cRF so all 80 ms is visible inside the circle. The
        # path SHAPE is preserved exactly (a rigid shift); only where it sits in
        # the cRF is a display choice — legitimate here because the dot's start
        # position within a cRF is arbitrary anyway.
        pre = _rotation_path(rf_c, sense, PRE_MS)
        p_switch = pre[-1]
        during = (_translation_path(p_switch, TRANS_MS) if translates
                  else _rotation_path(p_switch, sense, TRANS_MS))

        full = np.vstack([pre, during])
        centre = np.array([(full[:, 0].min() + full[:, 0].max()) / 2.0,
                           (full[:, 1].min() + full[:, 1].max()) / 2.0])
        shift = np.asarray(rf_c, float) - centre
        pre = pre + shift
        during = during + shift
        p0, p_switch = pre[0], pre[-1]

        # before the probe
        ax.plot(pre[:, 0], pre[:, 1], color=colour, lw=2.0, alpha=0.55,
                solid_capstyle="round", zorder=3)
        # during the probe
        ax.plot(during[:, 0], during[:, 1], color=colour, lw=3.4,
                solid_capstyle="round", zorder=4)
        ax.add_patch(FancyArrowPatch(during[-2], during[-1], arrowstyle="-|>",
                     mutation_scale=17, color=colour, lw=0, zorder=5))

        # dot at trajectory start; open marker at probe onset
        ax.scatter(*p0, s=52, color=colour, zorder=6)
        ax.scatter(*p_switch, s=46, facecolor="white", edgecolor=colour,
                   lw=1.8, zorder=6)

        note = ("rotation replaced by\nrightward translation"
                if translates else "rotation continues\nunchanged")
        ax.text(rf_c[0], rf_c[1] + CRF_R_DEG + pad * 0.55, note,
                ha="center", va="bottom", fontsize=9.5,
                color=colour, fontweight="bold")

        ax.set_title(f"{panel_lab}\n{sub}", fontsize=11, color=INK, pad=6)

    # shared legend describing the two trajectory segments
    fig.legend(handles=[
        Line2D([0], [0], color=INK2, lw=2.0, alpha=0.55,
               label=f"{PRE_MS:g} ms before the probe"),
        Line2D([0], [0], color=INK2, lw=3.4,
               label=f"{TRANS_MS:g} ms probe window"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
               markeredgecolor=INK2, markersize=8, label="probe onset")],
        loc="lower center", ncol=3, frameon=False, fontsize=9.5,
        bbox_to_anchor=(0.5, -0.02))

    fig.suptitle("B · The same two cRFs, magnified — dot trajectories through the probe",
                 fontsize=12.5, color=INK, y=0.99)
    fig.text(0.5, 0.055,
             f"rotation {OMEGA_DEG_S:g}°/s "
             f"({OMEGA_DEG_S * np.pi / 180 * ECC_DEG:.2f}°/s tangential at {ECC_DEG:g}°) "
             f"· translation {PROBE_DEG_S:g}°/s · cRF {CRF_DIAM_DEG:g}° diameter",
             ha="center", va="bottom", fontsize=8.5, color=INK2)

    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    print(f"N_DOTS per field = {N_DOTS}  (density {DENSITY} dots/deg^2/field)")
    tang = OMEGA_DEG_S * np.pi / 180 * ECC_DEG
    print(f"tangential speed at {ECC_DEG} deg = {tang:.3f} deg/s")
    print(f"  rotation displacement in {TRANS_MS:g} ms = {tang * TRANS_MS/1000:.4f} deg")
    print(f"  probe    displacement in {TRANS_MS:g} ms = "
          f"{PROBE_DEG_S * TRANS_MS/1000:.4f} deg   (cRF diam {CRF_DIAM_DEG} deg)")
    fig_A()
    fig_B()
