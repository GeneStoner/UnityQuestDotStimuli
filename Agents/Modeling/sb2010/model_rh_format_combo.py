"""
PROTOTYPE combo: the Stoner & Blanc motion-competition model in the Reynolds &
Heeger visual-equation FORMAT, for CUED and UNCUED, plus the translation
response R(theta=0, t) whose amplitude matches the theta=0 row of the grayscale
population-response maps.

Both models are the same divisive-normalization circuit
    response = drive / (pooled drive + sigma)
differing only in the bias field: R&H = attention, S&B = adaptation.

Outputs:
  model_rh_format_combo_cued.png     — visual-equation cascade, CUED
  model_rh_format_combo_uncued.png   — visual-equation cascade, UNCUED
  model_rh_format_translation.png    — population maps + R(0,t) line plot

Run:  /usr/bin/python3 model_rh_format_combo.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch

from parameters import T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END, K, SIGMA
from stimulus import channels_for_trial
from model import simulate_adapting_channel, naka_rushton
from drive_figure import tuning, DIR_CW, DIR_CCW, DIR_TRANS

THETA = np.arange(-180.0, 180.0, 1.0)
IDX0 = int(np.argmin(np.abs(THETA - DIR_TRANS)))     # translation direction row
GREEN, RED = "#2E8B57", "#C0392B"


def sb_fields(condition):
    t = np.arange(0.0, T_END + 1.0, 1.0)
    s_cw, s_ccw, s_tr = channels_for_trial(condition, False)
    R_cw, _ = simulate_adapting_channel(s_cw, t)
    R_ccw, _ = simulate_adapting_channel(s_ccw, t)
    R_tr, _ = simulate_adapting_channel(s_tr, t)

    # peak-normalised, moderately sharp tuning so the theta=0 readout reads the
    # translation channel cleanly (broad tuning leaks rotation tails into theta=0
    # and corrupts the detector to +24% instead of the model's +33%)
    KC = 4.0
    w_cw = (tuning(THETA, DIR_CW, KC) / np.exp(KC))[:, None]
    w_ccw = (tuning(THETA, DIR_CCW, KC) / np.exp(KC))[:, None]
    w_tr = (tuning(THETA, DIR_TRANS, KC) / np.exp(KC))[:, None]

    stim = np.zeros((len(THETA), len(t)))
    for d, s in [(DIR_CW, s_cw(t)), (DIR_CCW, s_ccw(t)), (DIR_TRANS, s_tr(t))]:
        diff = ((THETA - d + 180.0) % 360.0) - 180.0
        stim[np.abs(diff) <= 6.0, :] = np.maximum(
            stim[np.abs(diff) <= 6.0, :], s[None, :])

    Eraw = (w_cw * naka_rushton(s_cw(t))[None, :]
            + w_ccw * naka_rushton(s_ccw(t))[None, :]
            + w_tr * naka_rushton(s_tr(t))[None, :])
    E = w_cw * R_cw[None, :] + w_ccw * R_ccw[None, :] + w_tr * R_tr[None, :]

    # adaptation gain field; floored to the pre-onset baseline so empty regions
    # don't flash as "1" (fixes the prototype's lower-left artifact)
    G = np.full_like(Eraw, np.nan)
    m = Eraw > 0.04 * Eraw.max()
    G[m] = np.clip(E[m] / np.maximum(Eraw[m], 1e-6), 0.0, 1.3)
    G[~m] = np.nan                                   # leave blank where no drive

    # suppressive drive = rotation inhibition I = W_ROT(R1+R2) (matches the
    # original S&B plots — NOT incl. the translation channel)
    Sup = np.broadcast_to((R_cw + R_ccw)[None, :], E.shape)
    # S&B detector form R = K E / (E + I + sigma); theta=0 row == translation_detector
    Rpop = K * E / (E + Sup + SIGMA)
    return dict(t=t, stim=stim, Eraw=Eraw, G=G, E=E, Sup=Sup, R=Rpop)


# ---------------------------------------------------------------------------
# visual-equation cascade (R&H Figure-1 layout)
# ---------------------------------------------------------------------------

def _map(ax, mat, t, title, vmax=None):
    if vmax is None:
        vmax = np.nanmax(mat) if np.nanmax(mat) > 0 else 1.0
    cmap = plt.cm.gray.copy(); cmap.set_bad("#dddddd")     # NaN -> light gray
    ax.imshow(mat, extent=[t[0], t[-1], THETA[0], THETA[-1]], origin="lower",
              aspect="auto", cmap=cmap, vmin=0, vmax=vmax)
    for tx in (T_TRANS_START, T_TRANS_END):
        ax.axvline(tx, color="#C0392B", lw=0.6, alpha=0.8)
    ax.set_yticks([-90, 0, 90]); ax.set_yticklabels(["−90", "0", "90"], fontsize=6)
    ax.set_xticks([0, 800, 1600]); ax.set_xticklabels(["0", "800", "1600"], fontsize=6)
    ax.tick_params(length=2, pad=1.5)
    if title:
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=4)


def _arrow(fig, x0, y0, x1, y1, color="#333"):
    fig.patches.append(FancyArrowPatch((x0, y0), (x1, y1), transform=fig.transFigure,
                       arrowstyle="-|>,head_width=4,head_length=8", color=color,
                       lw=1.7, zorder=40))


def _op(fig, x, y, sym):
    fig.text(x, y, sym, ha="center", va="center", fontsize=17, zorder=61,
             bbox=dict(boxstyle="circle,pad=0.3", facecolor="white",
                       edgecolor="black", lw=1.8))


def _elbow(fig, x0, y0, x1, y1, color="#666"):
    fig.patches.append(FancyArrowPatch((x0, y0), (x1, y1), transform=fig.transFigure,
                       connectionstyle="angle,angleA=0,angleB=90,rad=0",
                       arrowstyle="-|>,head_width=4,head_length=8", color=color,
                       lw=1.7, zorder=40))


def render_combo(c, out, vmaxes, cond_label):
    t = c["t"]
    FIG_W, FIG_H = 16.0, 9.0
    PW = 0.125; PH = PW * FIG_W / FIG_H; Rr = 0.024
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    XMUL, XDIV, YMID = 0.40, 0.51, 0.50
    XCOL = XMUL; main_b = YMID - PH / 2; A_B, S_B = 0.700, 0.085

    ax_stim = fig.add_axes([0.040, main_b, PW, PH])
    ax_E = fig.add_axes([0.190, main_b, PW, PH])
    ax_R = fig.add_axes([0.610, main_b, PW, PH])
    ax_A = fig.add_axes([XCOL - PW / 2, A_B, PW, PH])
    ax_S = fig.add_axes([XCOL - PW / 2, S_B, PW, PH])

    _map(ax_stim, c["stim"], t, "Stimulus", vmaxes["stim"])
    _map(ax_E, c["Eraw"], t, "Stimulus drive  $E$", vmaxes["Eraw"])
    _map(ax_A, c["G"], t, "Adaptation  (gain)", vmaxes["G"])
    _map(ax_R, c["R"], t, "Population response  $R$", vmaxes["R"])
    _map(ax_S, c["Sup"], t, "", vmaxes["Sup"])
    fig.text(XCOL, S_B - 0.045, "Suppressive drive  $I$", ha="center", va="top",
             fontsize=10.5, fontweight="bold")
    # mark the translation row (theta = 0) on the response panel
    ax_R.axhline(0, color=GREEN if cond_label == "CUED" else RED, lw=1.0, ls=(0, (3, 2)))

    s_top = S_B + PH
    _arrow(fig, 0.040 + PW, YMID, 0.190 - 0.004, YMID)
    _arrow(fig, 0.190 + PW, YMID, XMUL - Rr, YMID)
    _arrow(fig, XMUL + Rr, YMID, XDIV - Rr, YMID)
    _arrow(fig, XDIV + Rr, YMID, 0.610 - 0.004, YMID)
    _op(fig, XMUL, YMID, "×"); _op(fig, XDIV, YMID, "÷")
    _arrow(fig, XCOL, A_B, XCOL, YMID + Rr, color="#666")
    _arrow(fig, XCOL, YMID - Rr, XCOL, s_top, color="#666")
    fig.text(XCOL - 0.055, (s_top + main_b) / 2, "pool over\ndirection",
             fontsize=8, style="italic", color="#555", ha="center", va="center")
    _elbow(fig, XCOL + PW / 2, S_B + PH / 2, XDIV, YMID - Rr, color="#666")

    fig.suptitle(f"Stoner & Blanc model in the R&H format — bias = adaptation "
                 f"  ({cond_label})", fontsize=12.5, fontweight="bold", y=0.965)
    fig.savefig(out, dpi=160, facecolor="white"); plt.close(fig)
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# population maps + matching translation response
# ---------------------------------------------------------------------------

def render_translation(cc, cu, rv, out):
    t = cc["t"]
    fig = plt.figure(figsize=(10.5, 8.2))
    gs = gridspec.GridSpec(3, 1, height_ratios=[1.0, 1.0, 1.2], hspace=0.30,
                           left=0.10, right=0.97, top=0.93, bottom=0.08)

    for ax, c, lab, col in [(fig.add_subplot(gs[0]), cc, "CUED", GREEN),
                            (fig.add_subplot(gs[1]), cu, "UNCUED", RED)]:
        ax.imshow(c["R"], extent=[t[0], t[-1], THETA[0], THETA[-1]],
                  origin="lower", aspect="auto", cmap="gray", vmin=0, vmax=rv)
        ax.axhline(0, color=col, lw=1.1, ls=(0, (3, 2)))
        ax.axvspan(T_TRANS_START, T_TRANS_END, color="#C0392B", alpha=0.10)
        ax.set_yticks([-90, 0, 90]); ax.set_yticklabels(["−90", "0\n(transl.)", "90"],
                                                        fontsize=7)
        ax.set_ylabel("pref. dir."); ax.set_xticklabels([])
        ax.set_title(f"{lab} — population response $R(\\theta, t)$  "
                     f"(shared grayscale)", loc="left", fontsize=10.5, fontweight="bold")

    ax = fig.add_subplot(gs[2])
    R0c, R0u = cc["R"][IDX0, :], cu["R"][IDX0, :]
    ax.plot(t, R0c, color=GREEN, lw=2.2, label="CUED")
    ax.plot(t, R0u, color=RED, lw=2.2, ls="--", label="UNCUED")
    ax.axvspan(T_TRANS_START, T_TRANS_END, color="0.85", alpha=0.7, zorder=0)
    ax.axvline(T_FIELD2_ON, color="0.5", lw=0.7)
    ax.set_ylim(0, rv); ax.set_xlim(t[0], t[-1])
    ax.set_xlabel("time  (ms)")
    ax.set_ylabel(r"$R(\theta=0,\,t)$")
    win = (t >= T_TRANS_START) & (t < T_TRANS_END)
    pc, pu = float(R0c[win].max()), float(R0u[win].max())
    ax.set_title(f"Translation response = the θ=0 row above   "
                 f"(peak CUED {pc:.1f} vs UNCUED {pu:.1f}, +{(pc/pu-1)*100:.0f}%)",
                 loc="left", fontsize=10.5, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")

    fig.savefig(out, dpi=160, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}  (peak cued {pc:.2f}, uncued {pu:.2f})")


def main():
    cc = sb_fields("cued")
    cu = sb_fields("uncued")
    fields = ["stim", "Eraw", "G", "Sup", "R"]
    vmaxes = {f: float(np.nanmax([np.nanmax(cc[f]), np.nanmax(cu[f])])) for f in fields}

    render_combo(cc, "model_rh_format_combo_cued.png", vmaxes, "CUED")
    render_combo(cu, "model_rh_format_combo_uncued.png", vmaxes, "UNCUED")
    render_translation(cc, cu, vmaxes["R"], "model_rh_format_translation.png")


if __name__ == "__main__":
    main()
