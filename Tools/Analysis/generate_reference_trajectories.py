#!/usr/bin/env python3
"""
Generate reference feature trajectory diagrams for VRDots swap conditions.

Shows the intended per-frame, per-subfield motion type, color, and depth plane.
Each condition is a dual-panel plot: top = motion type, bottom = depth plane.

Conditions shown:
  - No-Swap (N)             — baseline with depth separation
  - Motion-Swap (M)         — rotation directions swap at tStart (100%)
  - 50% Dot-Swap (D)        — sub1↔sub3 exchange field membership at tStart
  - Depth-Swap (Z)          — ALL depth planes exchange at tStart (100%)
  - 50% Depth-Swap (Zd)     — S0↔S2 exchange depth planes at tStart;
                               Near group (S0,S3): S0 translates coherently,
                               S3 translates non-coherently (both Near);
                               Far group (S1,S2): rotate only; rotation
                               follows new depth-plane membership
  - Dot+Depth-Swap (DZ)     — 50% dot swap + 100% depth swap at tStart

Uses a canonical CUED trial:
  Rot0 (aRot=CW, bRot=CCW), DelayedFieldColor=R, DelayedFieldDepth=Near
  Field A (sub0,sub1) = Green, CW, Far
  Field B (sub2,sub3) = Red, CCW, Near
  CUED => Field B translates during [tStart,tEnd)

  Translation coherence assignment:
    No-swap / M / Z / DZ:  sub2=Linear(coh), sub3=NonCoh   (original B members)
    D:                      sub2=Linear(coh), sub1=NonCoh   (sub1 swapped into B)
    Zd:                     sub0=Linear(coh,Near), sub3=NonCoh(Near);
                            sub1,sub2 rotate in Far (rotation follows depth plane)

Modeled after Stoner & Blanc (2010, Vision Research) Figure 5.

Usage:  python3 generate_reference_trajectories.py [output_path.png]
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── timing (frames, matching actual spec: 75Hz, 750/300/80/400 ms) ──
ONSET   = 56   # Field B appears  (750ms @ 75Hz)
T_START = 78   # translation onset (750 + 300 ms)
T_END   = 84   # translation offset  (80ms @ 75Hz = 6 frames)
TOTAL   = 114  # total frames        (+ 400ms post = 30 frames)

# ── motion type codes — ordered so translations sit between the two rotations ──
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4

# ── depth plane codes (match StimulusConditionsLibrary.DepthPlane) ──
NEAR, FAR = 1, 2

# ── colors ───────────────────────────────────────────────────────
RED, GREEN = "R", "G"


def build_trajectory(swap_type):
    """
    Return (mt, colors, depth) arrays of shape (TOTAL, 4).
    mt: int motion-type codes;  colors: object array of 'R'/'G';
    depth: int depth-plane codes (NEAR/FAR).
    """
    N = TOTAL
    mt     = np.zeros((N, 4), dtype=int)
    colors = np.empty((N, 4), dtype=object)
    depth  = np.zeros((N, 4), dtype=int)

    aRot, bRot   = CW, CCW
    ndCol, dCol  = GREEN, RED        # non-delayed / delayed field color

    # Depth assignment: DelayedFieldDepth=Near → Field B=Near, Field A=Far
    aDepth, bDepth = FAR, NEAR

    # Parse swap flags — check Zd before Z so "Zd" doesn't also trigger full Z
    has_Zd = "Zd" in swap_type
    has_M  = "M"  in swap_type
    has_D  = "D"  in swap_type
    has_Z  = "Z"  in swap_type and not has_Zd

    for f in range(N):
        swapped = f >= T_START

        # ── base field assignments ──────────────────────────────
        # Start with default membership
        # sub0,sub1 = Field A;  sub2,sub3 = Field B
        sub_rot   = [aRot, aRot, bRot, bRot]
        sub_col   = [ndCol, ndCol, dCol, dCol]
        sub_depth = [aDepth, aDepth, bDepth, bDepth]

        # Track which field each subfield belongs to for translation
        # field_is_B[s] = True if subfield s is in Field B
        field_is_B = [False, False, True, True]

        # ── motion swap (M): rotation directions exchange at tStart ──
        if has_M and swapped:
            sub_rot = [bRot, bRot, aRot, aRot]

        # ── 50% dot swap (D): sub1↔sub3 exchange membership at tStart ──
        if has_D and swapped:
            # sub1 → Field B, sub3 → Field A
            field_is_B[1] = True
            field_is_B[3] = False

            # Rotation follows new field (but M swap may have already flipped)
            if has_M:
                # M+D: both swaps active
                sub_rot[0] = bRot    # sub0: Field A, but M-swapped → bRot
                sub_rot[1] = aRot    # sub1: now Field B, M-swapped → aRot
                sub_rot[2] = aRot    # sub2: Field B, M-swapped → aRot
                sub_rot[3] = bRot    # sub3: now Field A, M-swapped → bRot
            else:
                sub_rot[1] = bRot    # sub1: now Field B rotation
                sub_rot[3] = aRot    # sub3: now Field A rotation

            # Color follows new field membership
            sub_col[1] = dCol       # sub1: now Field B color
            sub_col[3] = ndCol      # sub3: now Field A color

            # Depth follows new field membership (before Z swap)
            sub_depth[1] = bDepth   # sub1: now Field B depth
            sub_depth[3] = aDepth   # sub3: now Field A depth

        # ── depth swap (Z): ALL depth planes exchange at tStart ──
        if has_Z and swapped:
            for s in range(4):
                sub_depth[s] = FAR if sub_depth[s] == NEAR else NEAR

        # ── 50% depth swap (Zd): S0↔S2 exchange depth planes at tStart ──
        # Near group (S0, S3): rotation = aRot; Far group (S1, S2): rotation = bRot
        # S0 brings its Field A rotation (aRot) to Near → Near group = aRot
        # S2 brings its Field B rotation (bRot) to Far  → Far group  = bRot
        if has_Zd and swapped:
            sub_depth[0] = bDepth   # S0 (Field A, Far) → Near
            sub_depth[2] = aDepth   # S2 (Field B, Near) → Far
            sub_rot[1]   = bRot     # S1: stays Far, reverses aRot → bRot
            sub_rot[3]   = aRot     # S3: stays Near, takes Near-group rotation (aRot)
            # sub_rot[0] already aRot; sub_rot[2] already bRot — no change needed
            # Color follows depth-plane: Near-group = ndCol (S0 brings), Far-group = dCol (S2 brings)
            sub_col[1]   = dCol     # S1: stays Far → adopts Far-group color (Field B color)
            sub_col[3]   = ndCol    # S3: stays Near → adopts Near-group color (Field A color)

        # ── translation override during [tStart, tEnd) ──────────
        if T_START <= f < T_END:
            if has_Zd:
                # Translation follows delayed dots (sub2, sub3) regardless of depth plane
                sub_rot[2] = LINEAR   # sub2: coherent (now Far)
                sub_rot[3] = NONCOH   # sub3: non-coherent (stays Near)
            else:
                for s in range(4):
                    if field_is_B[s]:
                        if has_D and s == 1:
                            sub_rot[s] = NONCOH  # D: swapped-in member → noise
                        elif has_D and s == 2:
                            sub_rot[s] = LINEAR  # D: original member → coherent
                        elif not has_D and s == 2:
                            sub_rot[s] = LINEAR
                        elif not has_D and s == 3:
                            sub_rot[s] = NONCOH
                        else:
                            pass

        mt[f]     = sub_rot
        colors[f] = sub_col
        depth[f]  = sub_depth

        # Delayed onset: sub2/sub3 (Field B) not visible before ONSET
        if f < ONSET:
            colors[f, 2] = None
            colors[f, 3] = None
            mt[f, 2] = 0
            mt[f, 3] = 0
            depth[f, 2] = 0
            depth[f, 3] = 0

    return mt, colors, depth


# ── plotting ─────────────────────────────────────────────────────

CMAP = {"R": "#CC3333", "G": "#228B22"}
SPECS = [
    {"marker": "o", "filled": True,  "s": 22, "lw": 1.0},   # S0: filled circles
    {"marker": "s", "filled": False, "s": 48, "lw": 1.5},   # S1: unfilled squares
    {"marker": "^", "filled": True,  "s": 26, "lw": 1.0},   # S2: filled triangles
    {"marker": "D", "filled": False, "s": 56, "lw": 1.5},   # S3: unfilled diamonds
]


def _scatter_subfields(ax, data_arr, color_arr):
    """Plot subfield traces with colored markers on axes."""
    nF, nS = data_arr.shape
    sample_every = max(1, nF // 25)
    sample_frames = list(range(0, nF, sample_every))
    if sample_frames[-1] != nF - 1:
        sample_frames.append(nF - 1)

    for s in range(nS):
        sp = SPECS[s % len(SPECS)]
        ax.plot(np.arange(nF), data_arr[:, s], color="#D0D0D0", linewidth=0.5, zorder=1)

        xs, ys, cs = [], [], []
        for f in sample_frames:
            if color_arr is not None and f < color_arr.shape[0]:
                c = CMAP.get(str(color_arr[f, s]))
                if c is None:
                    continue
            else:
                c = "#666666"
            xs.append(f)
            ys.append(data_arr[f, s])
            cs.append(c)
        if not xs:
            continue
        if sp["filled"]:
            ax.scatter(xs, ys, marker=sp["marker"], c=cs,
                       edgecolors="none", s=sp["s"], zorder=3 + s)
        else:
            ax.scatter(xs, ys, marker=sp["marker"], facecolors="none",
                       edgecolors=cs, s=sp["s"], linewidths=sp["lw"], zorder=3 + s)


def _add_phase_markers(ax):
    """Add onset/translation phase lines and shading."""
    ax.axvspan(T_START, T_END, alpha=0.08, color="blue")
    ax.axvline(ONSET, ls=":", color="gray", lw=0.8)
    ax.axvline(T_START, ls="--", color="blue", lw=0.8)
    ax.axvline(T_END, ls="--", color="blue", lw=0.8)


def _add_legend(ax):
    """Add subfield identity legend."""
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray",
               markersize=6, linestyle="None", label="S0 (FieldA)"),
        Line2D([0], [0], marker="s", color="w", markeredgecolor="gray",
               markerfacecolor="none", markersize=7, markeredgewidth=1.5,
               linestyle="None", label="S1 (FieldA)"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="gray",
               markersize=6, linestyle="None", label="S2 (FieldB)"),
        Line2D([0], [0], marker="D", color="w", markeredgecolor="gray",
               markerfacecolor="none", markersize=7, markeredgewidth=1.5,
               linestyle="None", label="S3 (FieldB)"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=7)


def plot_dual_panel(ax_mt, ax_depth, mt_arr, color_arr, depth_arr, title=""):
    """Plot motion type (top) and depth plane (bottom) for one condition."""

    # ── motion type panel ──
    _scatter_subfields(ax_mt, mt_arr, color_arr)
    ax_mt.set_ylabel("motion type", fontsize=9)
    ax_mt.set_title(title, fontsize=10)
    ax_mt.set_yticks([1, 2, 3, 4])
    ax_mt.set_yticklabels(["CW rot", "Trans (coh)", "Trans (noise)", "CCW rot"], fontsize=8)
    ax_mt.set_ylim(0.5, 4.5)
    ax_mt.tick_params(axis='both', labelsize=8)
    ax_mt.set_xticklabels([])  # shared x-axis, labels on bottom panel
    _add_phase_markers(ax_mt)
    _add_legend(ax_mt)

    # ── depth plane panel ──
    _scatter_subfields(ax_depth, depth_arr, color_arr)
    ax_depth.set_xlabel("frame", fontsize=9)
    ax_depth.set_ylabel("depth plane", fontsize=9)
    ax_depth.set_yticks([1, 2])
    ax_depth.set_yticklabels(["Near", "Far"], fontsize=8)
    ax_depth.set_ylim(0.5, 2.5)
    ax_depth.tick_params(axis='both', labelsize=8)
    _add_phase_markers(ax_depth)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "reference_trajectories.png"

    swap_types = [
        ("N",  "No-Swap"),
        ("M",  "Motion-Swap (100%)"),
        ("D",  "50% Dot-Swap"),
        ("Z",  "Depth-Swap (100%)"),
        ("Zd", "50% Depth-Swap"),
        ("DZ", "50% Dot-Swap + Depth-Swap (100%)"),
    ]

    n = len(swap_types)
    # Use nested gridspec: outer grid separates condition groups with generous
    # spacing; inner grid keeps motion+depth panels tight within each group.
    fig = plt.figure(figsize=(16, 6.0 * n))
    outer = gridspec.GridSpec(n, 1, hspace=0.45)

    for i, (code, label) in enumerate(swap_types):
        mt_arr, color_arr, depth_arr = build_trajectory(code)

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[i],
            height_ratios=[3, 1.5], hspace=0.08)
        ax_mt    = fig.add_subplot(inner[0])
        ax_depth = fig.add_subplot(inner[1], sharex=ax_mt)

        coh_note = {
            "N":  "trans: S2=coh(Near), S3=noise(Near)",
            "M":  "trans: S2=coh(Near), S3=noise(Near)",
            "D":  "trans: S2=coh(Near), S1=noise(Near)  [S1 swapped into B]",
            "Z":  "trans: S2=coh(Far),  S3=noise(Far)   [all depths flipped]",
            "Zd": "trans: S2=coh(Far/R), S3=noise(Near/G)  [S0↔S2 swap depth; color follows plane: Near=G, Far=R]",
            "DZ": "trans: S2=coh(Far),  S1=noise(Far)   [dot-swap + all depths flipped]",
        }.get(code, "")
        title = (
            f"{label}  (Swap={code})\n"
            f"CUED  Rot0  DelField=R/Near   "
            f"FieldA(S0,S1)=Green/CW/Far   FieldB(S2,S3)=Red/CCW/Near\n"
            f"{coh_note}   onset={ONSET}  tStart={T_START}  tEnd={T_END}"
        )
        plot_dual_panel(ax_mt, ax_depth, mt_arr, color_arr, depth_arr, title=title)

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
