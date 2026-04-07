#!/usr/bin/env python3
"""
Trajectory diagrams for all Depth × Color Decoupling conditions.

Page 1 — Primary conditions: translator (S0) varies, companion (S1) = no swap.
Page 2 — Secondary conditions: companion (S1) varies, translator (S0) = no swap.

Each panel: 3 rows — Motion type / Depth plane / Color identity.
Line color = current dot color (Red or Green).
⚠ marks panels where mixed colors occur within a depth plane.

Output: Agents/WriteUps/depth_color_decoupled_traj.pdf
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

OUT = (sys.argv[1] if len(sys.argv) > 1 else
       "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/"
       "Agents/WriteUps/depth_color_decoupled_traj.pdf")

# ── Timing ────────────────────────────────────────────────────────────────────
T_TOT   = 1.000
T_B     = 0.490   # delayed field onset
T_S     = 0.686   # translation start
T_E     = 0.739   # translation end
NF      = 300     # simulation frames
T       = np.linspace(0, T_TOT, NF)

# ── Codes ─────────────────────────────────────────────────────────────────────
CW, TCOH, TNOI, CCW = 3, 2, 1, 0   # motion-type y-values
NEAR, FAR = 0, 1
RED, GRN  = 0, 1

COL_HEX = {RED: "#CC3333", GRN: "#228B22"}
COL_NAME = {RED: "Red", GRN: "Green"}
DEP_NAME = {NEAR: "Near", FAR: "Far"}

# ── Styles per subfield ───────────────────────────────────────────────────────
# marker, ms, filled, lw, ls, alpha
SF_STYLE = {
    0: dict(marker="o", ms=4.5, filled=True,  lw=1.6, ls="-",  alpha=1.0),
    1: dict(marker="s", ms=5.5, filled=False, lw=1.1, ls="--", alpha=1.0),
    2: dict(marker="^", ms=4.0, filled=True,  lw=0.9, ls="-",  alpha=0.45),
    3: dict(marker="D", ms=4.5, filled=False, lw=0.7, ls="--", alpha=0.45),
}
SF_LABEL = {
    0: "S0 ● coh (translator)",
    1: "S1 □ noi (companion)",
    2: "S2 ▲ coh (other field)",
    3: "S3 ◇ noi (other field)",
}

# Marker time-points: sample ~10 positions across trial
_base = np.linspace(0.05, 0.95, 10)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S + T_E) / 2]])))

C_HEAD = "#1a1a6e"


# ── Build arrays for one condition ────────────────────────────────────────────
def build(is_cued, dfd,
          sd_tran=False, sc_tran=False,   # translator: swap depth / swap color
          sd_comp=False, sc_comp=False):  # companion:  swap depth / swap color
    """
    Returns mot, dep, col arrays (NF, 4).
    S0 = primary coherent (translator), S1 = primary noise (companion)
    S2 = secondary coherent, S3 = secondary noise
    Primary field = delayed field if CUED; non-delayed field if UNCUED.
    """
    opp = lambda d: FAR if d == NEAR else NEAR
    col_of = lambda d: RED if d == NEAR else GRN   # Near=Red, Far=Green

    pri_dep = dfd    if is_cued else opp(dfd)
    sec_dep = opp(dfd) if is_cued else dfd
    pri_col = col_of(pri_dep)
    sec_col = col_of(sec_dep)

    pri_on = int(T_B / T_TOT * NF) if is_cued else 0
    sec_on = 0 if is_cued else int(T_B / T_TOT * NF)
    ts = int(T_S / T_TOT * NF)
    te = int(T_E / T_TOT * NF)

    mot = np.full((NF, 4), np.nan)
    dep = np.zeros((NF, 4), dtype=int)
    col = np.zeros((NF, 4), dtype=int)

    pri_rot = CW if is_cued else CCW
    sec_rot = CCW if is_cued else CW

    for f in range(NF):
        # S0 — primary coherent translator
        if f >= pri_on:
            d0 = pri_dep if (f < ts or not sd_tran) else opp(pri_dep)
            c0 = pri_col if (f < ts or not sc_tran) else (GRN if pri_col==RED else RED)
            dep[f, 0] = d0;  col[f, 0] = c0
            mot[f, 0] = TCOH if ts <= f < te else pri_rot
        else:
            dep[f, 0] = pri_dep;  col[f, 0] = pri_col

        # S1 — primary noise companion
        if f >= pri_on:
            d1 = pri_dep if (f < ts or not sd_comp) else opp(pri_dep)
            c1 = pri_col if (f < ts or not sc_comp) else (GRN if pri_col==RED else RED)
            dep[f, 1] = d1;  col[f, 1] = c1
            mot[f, 1] = TNOI if ts <= f < te else pri_rot
        else:
            dep[f, 1] = pri_dep;  col[f, 1] = pri_col

        # S2 — secondary coherent (no swap)
        if f >= sec_on:
            dep[f, 2] = sec_dep;  col[f, 2] = sec_col
            mot[f, 2] = sec_rot
        else:
            dep[f, 2] = sec_dep;  col[f, 2] = sec_col

        # S3 — secondary noise (no swap)
        if f >= sec_on:
            dep[f, 3] = sec_dep;  col[f, 3] = sec_col
            mot[f, 3] = sec_rot
        else:
            dep[f, 3] = sec_dep;  col[f, 3] = sec_col

    return mot, dep, col


def has_mixed(dep, col, ts_frame):
    """Return True if any depth plane contains both Red and Green after tStart."""
    for plane in [NEAR, FAR]:
        for f in range(ts_frame, NF):
            in_plane = [s for s in range(4) if dep[f, s] == plane]
            colors   = {col[f, s] for s in in_plane}
            if len(colors) > 1:
                return True
    return False


def draw_panel(axes, mot, dep, col, is_cued, dfd,
               dots_ok, depth_ok, color_ok, swap_label, analog, mixed):
    """
    axes: tuple of (ax_mot, ax_dep, ax_clr)
    """
    ax_m, ax_d, ax_c = axes
    ts = int(T_S / T_TOT * NF)
    te = int(T_E / T_TOT * NF)

    for s in range(4):
        sty    = SF_STYLE[s]
        lw     = sty["lw"];   ls  = sty["ls"]
        alp    = sty["alpha"]; mk = sty["marker"]
        ms     = sty["ms"];   filled = sty["filled"]

        # Split at T_S to allow line-color change
        segs = [(0, ts), (ts, NF)]
        for start, end in segs:
            if start >= end:
                continue
            t_seg = T[start:end]
            mid   = (start + end) // 2
            c_key = int(col[min(mid, NF-1), s])
            hex_c = COL_HEX[c_key]
            mfc   = hex_c if filled else "none"

            for arr, ax in [(mot, ax_m), (dep, ax_d), (col, ax_c)]:
                y_raw = arr[start:end, s].astype(float)
                if arr is mot:
                    mask = ~np.isnan(y_raw)
                    if mask.sum() < 2:
                        continue
                    ax.plot(t_seg[mask], y_raw[mask],
                            color=hex_c, lw=lw, ls=ls, alpha=alp,
                            solid_capstyle="round")
                    # markers at visible T_MARKS within this segment
                    t_end_val = T[end - 1]
                    t_mk = T_MARKS[(T_MARKS >= T[start]) & (T_MARKS <= t_end_val)]
                    if len(t_mk):
                        y_mk = np.interp(t_mk, t_seg[mask], y_raw[mask])
                        ax.plot(t_mk, y_mk, marker=mk, ms=ms, mew=0.8,
                                mfc=mfc, mec=hex_c, ls="none", alpha=alp)
                else:
                    ax.plot(t_seg, y_raw,
                            color=hex_c, lw=lw, ls=ls, alpha=alp,
                            solid_capstyle="round")
                    t_end_val = T[end - 1]
                    t_mk = T_MARKS[(T_MARKS >= T[start]) & (T_MARKS <= t_end_val)]
                    if len(t_mk):
                        y_mk = np.interp(t_mk, t_seg, y_raw)
                        ax.plot(t_mk, y_mk, marker=mk, ms=ms, mew=0.8,
                                mfc=mfc, mec=hex_c, ls="none", alpha=alp)

    # Phase markers
    for ax in (ax_m, ax_d, ax_c):
        ax.axvspan(T_S, T_E, alpha=0.12, color="steelblue", zorder=0)
        ax.axvline(T_B, color="#AAAAAA", lw=0.7, ls=":")
        ax.axvline(T_S, color="steelblue", lw=0.6, ls="--")

    # Motion axis
    ax_m.set_ylim(-0.4, 3.6)
    ax_m.set_yticks([0, 1, 2, 3])
    ax_m.set_yticklabels(["CCW", "T(n)", "T(c)", "CW"], fontsize=4.5)
    ax_m.tick_params(axis="y", length=2, pad=1)
    ax_m.set_xticks([]); ax_m.tick_params(axis="x", length=0)

    # Depth axis
    ax_d.set_ylim(-0.35, 1.35)
    ax_d.set_yticks([0, 1])
    ax_d.set_yticklabels(["N", "F"], fontsize=4.5)
    ax_d.tick_params(axis="y", length=2, pad=1)
    ax_d.set_xticks([]); ax_d.tick_params(axis="x", length=0)
    ax_d.set_xlim(0, T_TOT)

    # Color axis
    ax_c.set_ylim(-0.35, 1.35)
    ax_c.set_yticks([0, 1])
    ax_c.set_yticklabels(["R", "G"], fontsize=4.5)
    ax_c.tick_params(axis="y", length=2, pad=1)
    ax_c.set_xticks([]); ax_c.tick_params(axis="x", length=0)
    ax_c.set_xlim(0, T_TOT)

    for ax in (ax_m, ax_d, ax_c):
        ax.set_xlim(0, T_TOT)
        for sp in ax.spines.values():
            sp.set_linewidth(0.5)

    # Panel background
    bg = "#EEF8EE" if (dots_ok and depth_ok and color_ok) else \
         "#F5F0FF" if (not dots_ok and not depth_ok and not color_ok) else \
         "#FFFAF0"
    for ax in (ax_m, ax_d, ax_c):
        ax.set_facecolor(bg)

    # Title
    dot_s  = "Dots✓"  if dots_ok  else "Dots✗"
    dep_s  = "Dep✓"   if depth_ok else "Dep✗"
    clr_s  = "Col✓"   if color_ok else "Col✗"
    warn   = "  ⚠" if mixed else ""
    dot_c  = "#1a6b1a" if dots_ok  else "#555"
    dep_c  = "#1a3a8b" if depth_ok else "#aa2222"
    clr_c  = "#aa2222" if color_ok else "#8b1a1a"
    ax_m.set_title(
        f"{dot_s}  {dep_s}  {clr_s}{warn}\n"
        f"{swap_label}",
        fontsize=6.5, pad=3, loc="center",
        fontweight="bold",
        color="#222")
    if mixed:
        ax_m.text(0.98, 0.97, "⚠mixed",
                  transform=ax_m.transAxes,
                  ha="right", va="top", fontsize=5.5,
                  color="#cc4400", fontweight="bold")

    # Analog note
    if analog:
        ax_c.text(0.5, -0.55, analog, transform=ax_c.transAxes,
                  ha="center", va="top", fontsize=5.5, color="#666",
                  style="italic")


# ══════════════════════════════════════════════════════════════════════════════
# Conditions
# ══════════════════════════════════════════════════════════════════════════════
# Compute Dots✓/✗, Depth✓/✗, Color✓/✗ for each condition.
# DFD = NEAR (representative), so cued depth = Near, cued color = Red.
DFD = NEAR

def cue_flags(is_cued, dfd, sd_t, sc_t, sd_c=False, sc_c=False):
    """Return (dots_ok, depth_ok, color_ok, mixed) for the translator."""
    opp = lambda d: FAR if d == NEAR else NEAR
    col_of = lambda d: RED if d == NEAR else GRN
    pri_dep = dfd    if is_cued else opp(dfd)
    pri_col = col_of(pri_dep)

    # After swap, translator depth and color
    post_dep = opp(pri_dep) if sd_t else pri_dep
    post_col = (GRN if pri_col==RED else RED) if sc_t else pri_col

    # "Cued" reference = DFD + col_of(DFD)
    depth_ok = (post_dep == dfd)
    color_ok = (post_col == col_of(dfd))
    dots_ok  = is_cued

    mot, dep, col = build(is_cued, dfd, sd_t, sc_t, sd_c, sc_c)
    ts = int(T_S / T_TOT * NF)
    mixed = has_mixed(dep, col, ts)
    return dots_ok, depth_ok, color_ok, mixed


# Primary page conditions: translator varies, companion = no swap
PRIMARY = [
    # (is_cued, sd_t, sc_t, label, analog)
    (True,  False, False, "CUED + N",    "= N baseline\n(not yet run)"),
    (True,  True,  False, "CUED + ZdA",  "new"),
    (True,  False, True,  "CUED + ZcA",  "new"),
    (True,  True,  True,  "CUED + ZdcA", "= current ZdCoh"),
    (False, False, False, "UNCUED + N",  "= N baseline"),
    (False, True,  False, "UNCUED + ZdA","new"),
    (False, False, True,  "UNCUED + ZcA","new"),
    (False, True,  True,  "UNCUED + ZdcA","= current ZdCoh (UNCUED)"),
]

# Secondary page conditions: companion varies, translator = no swap
SECONDARY = [
    # (is_cued, sd_c, sc_c, label, analog)
    (True,  False, False, "CUED + N",     "= primary N"),
    (True,  True,  False, "CUED + ZdB",   "new"),
    (True,  False, True,  "CUED + ZcB",   "new"),
    (True,  True,  True,  "CUED + ZdcB",  "= current ZdNoi"),
    (False, False, False, "UNCUED + N",   "= primary N"),
    (False, True,  False, "UNCUED + ZdB", "new"),
    (False, False, True,  "UNCUED + ZcB", "new"),
    (False, True,  True,  "UNCUED + ZdcB","= current ZdNoi (UNCUED)"),
]


def make_page(pdf, conditions, page_title, subtitle,
              is_primary=True):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.975, page_title,
             ha="center", va="top", fontsize=12, fontweight="bold", color="#111")
    fig.text(0.5, 0.953, subtitle,
             ha="center", va="top", fontsize=7.5, color="#555", style="italic")
    fig.text(0.5, 0.938,
             "Line color = dot color (Red / Green).  "
             "⚠ = mixed colors within a depth plane after tStart.  "
             "DFD = Near (= Red) shown; Far symmetric.",
             ha="center", va="top", fontsize=6.8, color="#777")

    outer = gridspec.GridSpec(2, 4,
                              top=0.928, bottom=0.045,
                              left=0.06, right=0.97,
                              hspace=0.65, wspace=0.28)

    row_labels = ["CUED\n(delayed field\ntranslates)",
                  "UNCUED\n(non-delayed\ntranslates)"]

    for idx, cond in enumerate(conditions):
        row = idx // 4
        col = idx %  4

        if is_primary:
            is_cued, sd_t, sc_t, lbl, analog = cond
            sd_c = sc_c = False
            dots_ok, depth_ok, color_ok, mixed = cue_flags(is_cued, DFD, sd_t, sc_t)
            mot, dep, col_arr = build(is_cued, DFD, sd_t, sc_t, False, False)
        else:
            is_cued, sd_c, sc_c, lbl, analog = cond
            sd_t = sc_t = False
            # For secondary: translator no-swap → recompute cue flags from companion perspective
            # dots_ok same; depth/color based on translator (which doesn't swap)
            dots_ok, depth_ok, color_ok, mixed = cue_flags(is_cued, DFD, False, False, sd_c, sc_c)
            mot, dep, col_arr = build(is_cued, DFD, False, False, sd_c, sc_c)

        inner = gridspec.GridSpecFromSubplotSpec(
            3, 1, subplot_spec=outer[row, col],
            height_ratios=[3, 1.5, 1.5], hspace=0.08)

        ax_m = fig.add_subplot(inner[0])
        ax_d = fig.add_subplot(inner[1], sharex=ax_m)
        ax_c = fig.add_subplot(inner[2], sharex=ax_m)

        draw_panel((ax_m, ax_d, ax_c),
                   mot, dep, col_arr,
                   is_cued, DFD,
                   dots_ok, depth_ok, color_ok,
                   lbl, analog, mixed)

        # Row labels on left edge
        if col == 0:
            ax_m.set_ylabel(row_labels[row] + "\n\nMotion",
                            fontsize=6, labelpad=3,
                            color="#1a6b1a" if is_cued else "#555555")
            ax_d.set_ylabel("Depth", fontsize=5.5, labelpad=3)
            ax_c.set_ylabel("Color", fontsize=5.5, labelpad=3)

    # Legend
    leg_handles = [
        Line2D([0],[0], color="#888", lw=1.6, ls="-",
               marker="o", ms=5, mfc="#888", mec="#888", label="S0 ● coherent translator"),
        Line2D([0],[0], color="#888", lw=1.1, ls="--",
               marker="s", ms=5.5, mfc="none", mec="#888", label="S1 □ noise companion"),
        Line2D([0],[0], color="#888", lw=0.9, ls="-",  alpha=0.5,
               marker="^", ms=4.5, mfc="#888", mec="#888", label="S2 ▲ other-field coh"),
        Line2D([0],[0], color="#888", lw=0.7, ls="--", alpha=0.5,
               marker="D", ms=4.5, mfc="none", mec="#888", label="S3 ◇ other-field noi"),
        Patch(facecolor="#CC333344", edgecolor="#CC3333", label="Red line = Near plane"),
        Patch(facecolor="#228B2244", edgecolor="#228B22", label="Green line = Far plane"),
        Patch(facecolor="steelblue", alpha=0.15, label="Translation window"),
    ]
    fig.legend(handles=leg_handles,
               loc="lower center", ncol=4, fontsize=6.5,
               frameon=True, framealpha=0.9,
               bbox_to_anchor=(0.5, 0.005))

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
with PdfPages(OUT) as pdf:

    make_page(pdf, PRIMARY,
              "Depth × Color Decoupling — Primary Conditions",
              "Translator (S0) varies · Companion (S1) = no swap throughout",
              is_primary=True)

    make_page(pdf, SECONDARY,
              "Depth × Color Decoupling — Secondary Conditions",
              "Companion (S1) varies · Translator (S0) = no swap throughout",
              is_primary=False)

print(f"Wrote: {OUT}")
