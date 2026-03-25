#!/usr/bin/env python3
"""
Generate reference feature trajectory diagrams for VRDots swap conditions.

Shows the intended per-frame, per-subfield motion kind and color for:
  - No-Swap (N)
  - Motion-Swap 100% (M)
  - 50% Dot-Swap (D)  [pending C# implementation]

Uses a canonical CUED trial:
  Rot0 (aRot=CW, bRot=CCW), DelayedFieldColor=R
  Field A (sub0,sub1) = Green, CW;  Field B (sub2,sub3) = Red, CCW
  CUED => Field B translates: sub2=Linear, sub3=NonCoherent during [tStart,tEnd)

Modeled after Stoner & Blanc (2010, Vision Research) Figure 5.

Usage:  python3 generate_reference_trajectories.py [output_path.png]
"""

import sys
import math
import numpy as np
import matplotlib.pyplot as plt

# ── timing (frames, matching actual spec: 75Hz, 750/300/80/400 ms) ──
ONSET   = 56   # Field B appears  (750ms @ 75Hz)
T_START = 78   # translation onset (750 + 300 ms)
T_END   = 84   # translation offset  (80ms @ 75Hz = 6 frames)
TOTAL   = 114  # total frames        (+ 400ms post = 30 frames)

# ── motion kind codes (match StimulusConditionsLibrary.MotionKind) ──
CW, CCW, LINEAR, NONCOH = 1, 2, 3, 4

# ── colors ───────────────────────────────────────────────────────
RED, GREEN = "R", "G"


def build_trajectory(swap_type):
    """
    Return (mk, colors) arrays of shape (TOTAL, 4).
    mk: int motion-kind codes;  colors: object array of 'R'/'G'.
    """
    N = TOTAL
    mk     = np.zeros((N, 4), dtype=int)
    colors = np.empty((N, 4), dtype=object)

    aRot, bRot   = CW, CCW
    ndCol, dCol  = GREEN, RED        # non-delayed / delayed field color

    for f in range(N):
        # ── No-Swap ──────────────────────────────────────────────
        if swap_type == "N":
            mk[f] = [aRot, aRot, bRot, bRot]
            colors[f] = [ndCol, ndCol, dCol, dCol]
            if T_START <= f < T_END:
                mk[f, 2] = LINEAR
                mk[f, 3] = NONCOH

        # ── Motion-Swap 100% ─────────────────────────────────────
        elif swap_type == "M":
            swapped = f >= T_START
            cA = bRot if swapped else aRot
            cB = aRot if swapped else bRot
            mk[f] = [cA, cA, cB, cB]
            colors[f] = [ndCol, ndCol, dCol, dCol]
            if T_START <= f < T_END:        # translation overrides B
                mk[f, 2] = LINEAR
                mk[f, 3] = NONCOH

        # ── 50% Dot-Swap ─────────────────────────────────────────
        elif swap_type == "D":
            if f < T_START:
                mk[f] = [aRot, aRot, bRot, bRot]
                colors[f] = [ndCol, ndCol, dCol, dCol]
            else:
                # sub1 <-> sub3 exchange field membership
                # Field A is now {sub0, sub3}; Field B is now {sub2, sub1}
                mk[f, 0] = aRot        # sub0: stays Field A
                mk[f, 1] = bRot        # sub1: now Field B rotation
                mk[f, 2] = bRot        # sub2: stays Field B
                mk[f, 3] = aRot        # sub3: now Field A rotation
                colors[f, 0] = ndCol    # sub0: stays Green
                colors[f, 1] = dCol     # sub1: now Red (Field B)
                colors[f, 2] = dCol     # sub2: stays Red
                colors[f, 3] = ndCol    # sub3: now Green (Field A)
                # Translation override: Field B = {sub2, sub1}
                if T_START <= f < T_END:
                    mk[f, 2] = LINEAR   # sub2: coherent translation
                    mk[f, 1] = NONCOH   # sub1: non-coherent (swapped in)

    return mk, colors


# ── plotting ─────────────────────────────────────────────────────

def plot_motion(ax, mk_arr, color_arr=None, title=""):
    from matplotlib.lines import Line2D

    nF, nS = mk_arr.shape
    sample_every = max(1, nF // 25)
    sample_frames = list(range(0, nF, sample_every))
    if sample_frames[-1] != nF - 1:
        sample_frames.append(nF - 1)

    cmap = {"R": "#CC3333", "G": "#228B22"}
    specs = [
        {"marker": "o", "filled": True,  "s": 22, "lw": 1.0},   # S0: filled circles
        {"marker": "s", "filled": False, "s": 48, "lw": 1.5},   # S1: unfilled squares
        {"marker": "^", "filled": True,  "s": 26, "lw": 1.0},   # S2: filled triangles
        {"marker": "D", "filled": False, "s": 56, "lw": 1.5},   # S3: unfilled diamonds
    ]

    for s in range(nS):
        sp = specs[s % len(specs)]
        ax.plot(np.arange(nF), mk_arr[:, s], color="#D0D0D0", linewidth=0.5, zorder=1)

        xs, ys, cs = [], [], []
        for f in sample_frames:
            if color_arr is not None and f < color_arr.shape[0]:
                c = cmap.get(str(color_arr[f, s]))
                if c is None:
                    continue
            else:
                c = "#666666"
            xs.append(f)
            ys.append(mk_arr[f, s])
            cs.append(c)
        if not xs:
            continue
        if sp["filled"]:
            ax.scatter(xs, ys, marker=sp["marker"], c=cs,
                       edgecolors="none", s=sp["s"], zorder=3 + s)
        else:
            ax.scatter(xs, ys, marker=sp["marker"], facecolors="none",
                       edgecolors=cs, s=sp["s"], linewidths=sp["lw"], zorder=3 + s)

    ax.set_xlabel("frame", fontsize=9)
    ax.set_ylabel("motion kind", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(["CW rot", "CCW rot", "Trans (coh)", "Trans (noise)"], fontsize=8)
    ax.set_ylim(0.5, 4.5)
    ax.axvspan(T_START, T_END, alpha=0.08, color="blue")
    ax.axvline(ONSET, ls=":", color="gray", lw=0.8)
    ax.axvline(T_START, ls="--", color="blue", lw=0.8)
    ax.axvline(T_END, ls="--", color="blue", lw=0.8)
    ax.tick_params(axis='both', labelsize=8)

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
    ax.legend(handles=legend_handles, loc="upper right", fontsize=8)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "reference_trajectories.png"

    swap_types = [
        ("N", "No-Swap"),
        ("M", "Motion-Swap (100%)"),
        ("D", "50% Dot-Swap"),
    ]

    fig, axes = plt.subplots(len(swap_types), 1, figsize=(16, 4.5 * len(swap_types)))

    for i, (code, label) in enumerate(swap_types):
        mk_arr, color_arr = build_trajectory(code)

        title = (
            f"{label}  (Swap={code})\n"
            f"CUED  Rot0 (aRot=CW, bRot=CCW)  DelField=R\n"
            f"Field A (S0,S1)=Green/CW   Field B (S2,S3)=Red/CCW   "
            f"onset={ONSET}  tStart={T_START}  tEnd={T_END}"
        )
        plot_motion(axes[i], mk_arr, color_arr=color_arr, title=title)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
