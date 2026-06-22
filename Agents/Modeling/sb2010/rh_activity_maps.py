"""
R&H 2009 'showActivityMaps' cascade, rendered for the SB delayed-onset
stimulus using the VERIFIED port of attentionModel.m.

This replaces the superseded hand-rolled rh_fig1_style.py.  It emulates the
layout and computation of the authors' own ``attentionModel.m`` activity-map
display (the ``showActivityMaps`` block, subplots 1-5):

    Stimulus | Stimulus drive
    Attention field | Suppressive drive
    Population response | (cascade equations)

Crucially the suppressive drive here is R&H's
    I = conv2sepYcirc(E, IxKernel, IthetaKernel)
i.e. the stimulus drive E (= attention x Eraw) pooled by a broad kernel over
direction (IthetaWidth = 360 deg) and time.  It is therefore present
throughout the trial wherever the rotations drive E -- NOT a translation-only
blip.

Axes follow R&H with time substituted for their spatial RF-center axis:
    x = time (ms)            (their 'Receptive field center')
    y = preferred direction  (their 'Orientation preference')

Grayscale matches MATLAB ``imshow(X,[0,max])`` -- high = white, each panel
scaled to its own maximum.

Run:  /usr/bin/python3 rh_activity_maps.py
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

HERE = os.path.dirname(os.path.abspath(__file__))
VERIF = os.path.normpath(os.path.join(HERE, "..", "verification"))
sys.path.insert(0, VERIF)
from port_attention_model import (          # noqa: E402
    make_gaussian, conv2sep_y_circ, _build_attention_field,
)

from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END  # noqa: E402
from sb_rh_verified import (                # noqa: E402
    build_sb_stimulus, THETA_PREFS,
    ETHETA_WIDTH, ET_WIDTH, ITHETA_WIDTH, IT_WIDTH,
    ATHETA_WIDTH, ATTN_DIR_DEG, APEAK, ABASE,
)

# R&H's published default normalization constant.  With the verified port's
# unit-volume Gaussian kernels this is the meaningful regime (σ=1 would sit in
# a near-un-normalized regime; see rh_translation_response.py).
SIGMA = 1e-6


def cascade(condition, motion_swap, t):
    """Return every stage of the R&H cascade as (N_theta x N_t) fields,
    computed with the verified-port helpers (same math as attentionModel.m)."""
    stim = build_sb_stimulus(t, condition, motion_swap)
    n_t = len(t)
    x = np.arange(n_t, dtype=float) - n_t // 2   # centred, as Figure4C.m does

    ExK  = make_gaussian(x,           0.0, ET_WIDTH)
    IxK  = make_gaussian(x,           0.0, IT_WIDTH)
    EthK = make_gaussian(THETA_PREFS, 0.0, ETHETA_WIDTH)
    IthK = make_gaussian(THETA_PREFS, 0.0, ITHETA_WIDTH)

    A = _build_attention_field(
        x, THETA_PREFS, Ax=np.nan, Atheta=ATTN_DIR_DEG,
        AxWidth=ET_WIDTH, AthetaWidth=ATHETA_WIDTH,
        Apeak=APEAK, Abase=ABASE, Ashape="oval",
    )
    Eraw = conv2sep_y_circ(stim, ExK, EthK)      # stimulus drive (pre-attention)
    E    = A * Eraw                              # after attentional gain
    I    = conv2sep_y_circ(E, IxK, IthK)         # suppressive drive (pooled E)
    R    = E / (I + SIGMA)                        # normalized population response
    return dict(stim=stim, Eraw=Eraw, A=A, E=E, I=I, R=R)


def _map(ax, mat, t, title):
    vmax = mat.max() if mat.max() > 0 else 1.0
    ax.imshow(mat, extent=[t[0], t[-1], THETA_PREFS[0], THETA_PREFS[-1]],
              origin="lower", aspect="auto", cmap="gray", vmin=0, vmax=vmax)
    for tx in (T_TRANS_START, T_TRANS_END):
        ax.axvline(tx, color="#C0392B", lw=0.7, alpha=0.8)
    ax.set_yticks([-180, -90, 0, 90, 180])
    ax.set_yticklabels(["Left\n(±180°)", "Down\n(−90°)", "Right\n(0°)",
                        "Up\n(90°)", "Left\n(180°)"], fontsize=7)
    ax.set_xlabel("Time (ms)", fontsize=9)
    ax.set_ylabel("Preferred direction", fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold")
    ax.tick_params(labelsize=7)


def _equations(ax):
    ax.axis("off")
    ax.text(0.0, 0.98, "Cascade  (Reynolds & Heeger, 2009)", fontsize=11,
            fontweight="bold", va="top", transform=ax.transAxes)
    lines = [
        (0.82, r"$E_{\rm raw}(\theta,t) = \mathrm{stim} \ast (E_x \otimes E_\theta)$"),
        (0.68, r"$A(\theta)$  —  gain bump at $\theta_{\rm attn}$"),
        (0.56, r"$E = A \cdot E_{\rm raw}$"),
        (0.44, r"$I(\theta,t) = E \ast (I_x \otimes I_\theta)$"),
        (0.30, r"$R(\theta,t) = \dfrac{E}{\,I + \sigma\,}$"),
    ]
    for y, s in lines:
        ax.text(0.0, y, s, fontsize=12, va="top", transform=ax.transAxes)
    ax.text(0.0, 0.13,
            f"$E_\\theta\\,\\sigma$={ETHETA_WIDTH:.0f}°, $I_\\theta\\,\\sigma$={ITHETA_WIDTH:.0f}° "
            f"(pool over all θ),\n$\\theta_{{\\rm attn}}$={ATTN_DIR_DEG:.0f}°, "
            f"a/b={APEAK:.0f}/{ABASE:.0f}, σ={SIGMA:.0e}",
            fontsize=8.5, color="#444", va="top", transform=ax.transAxes)


def render(condition, motion_swap, out, page_title):
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    c = cascade(condition, motion_swap, t)

    fig = plt.figure(figsize=(11.0, 10.5))
    gs = gridspec.GridSpec(3, 2, left=0.08, right=0.97, top=0.92, bottom=0.06,
                           hspace=0.42, wspace=0.28)
    _map(fig.add_subplot(gs[0, 0]), c["stim"], t, "Stimulus")
    _map(fig.add_subplot(gs[0, 1]), c["Eraw"], t, "Stimulus drive")
    _map(fig.add_subplot(gs[1, 0]), c["A"],    t, "Attention field")
    _map(fig.add_subplot(gs[1, 1]), c["I"],    t, "Suppressive drive")
    _map(fig.add_subplot(gs[2, 0]), c["R"],    t, "Population response")
    _equations(fig.add_subplot(gs[2, 1]))

    fig.suptitle(page_title, fontsize=13, fontweight="bold", y=0.965)
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


def main():
    render("cued", False, "rh_activity_maps_cued.png",
           "Normalization-model cascade — CUED  (R&H showActivityMaps format)")
    render("uncued", False, "rh_activity_maps_uncued.png",
           "Normalization-model cascade — UNCUED  (R&H showActivityMaps format)")


if __name__ == "__main__":
    main()
