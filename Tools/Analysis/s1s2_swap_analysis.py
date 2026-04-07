#!/usr/bin/env python3
"""
Analysis: S1↔S2 full attribute swap — does it work as a 50% partial swap?
Output: Agents/WriteUps/s1s2_swap_analysis.pdf
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

OUT = (sys.argv[1] if len(sys.argv) > 1 else
       "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/"
       "Agents/WriteUps/s1s2_swap_analysis.pdf")

RED  = "#CC3333"
GRN  = "#228B22"
BLU  = "#1a3a8b"
GRY  = "#888888"
BG   = "#F9F9FF"
ORG  = "#CC6600"

def T(ax, x, y, s, **kw):
    return ax.text(x, y, s, transform=ax.transAxes, **kw)

def box(ax, x, y, w, h, fc, ec="#BBBBCC", lw=0.7, zorder=1, style="round,pad=0.006"):
    p = FancyBboxPatch((x, y), w, h, boxstyle=style,
                       facecolor=fc, edgecolor=ec, lw=lw,
                       transform=ax.transAxes, zorder=zorder)
    ax.add_patch(p)

def hline(ax, y, x0=0.06, x1=0.94, color="#BBBBCC", lw=0.7):
    ax.add_artist(plt.Line2D([x0, x1], [y, y],
                              transform=ax.transAxes, color=color, lw=lw))

with PdfPages(OUT) as pdf:

    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # ── Title ─────────────────────────────────────────────────────────────────
    T(ax, 0.5, 0.978,
      "The S1↔S2 Full-Attribute Swap",
      ha="center", va="top", fontsize=14, fontweight="bold", color="#111")
    T(ax, 0.5, 0.956,
      "Does swapping all attributes of S1 and S2 at tStart work as a useful 50% manipulation?",
      ha="center", va="top", fontsize=9, color="#555", style="italic")

    # ── Section 1: Setup ──────────────────────────────────────────────────────
    y = 0.928
    T(ax, 0.06, y, "1.  Reference configuration (UNCUED trial, no swap)",
      fontsize=11, fontweight="bold", color=BLU, va="top")
    y -= 0.028

    box(ax, 0.06, y-0.078, 0.88, 0.076, "#F4F8FF", lw=0.6)

    cols = [0.10, 0.18, 0.30, 0.42, 0.56, 0.70]
    hdrs = ["Sub-\nfield", "Field", "Depth\n+Color", "Motion\nbefore tStart", "Motion\nafter tStart", "Role"]
    for x, h in zip(cols, hdrs):
        ax.text(x, y-0.006, h, transform=ax.transAxes, fontsize=8,
                fontweight="bold", color="#333", va="top")
    y -= 0.005
    hline(ax, y-0.004, x0=0.07, x1=0.93, color="#AAA")
    y -= 0.018

    rows = [
        ("S0", "A", "Near+Red",   RED,  "aRot (coherent)",  "TRANSLATE (Linear)", "Coherent translator"),
        ("S1", "A", "Near+Red",   RED,  "NonCoherent",       "NonCoherent",         "Noise in Field A"),
        ("S2", "B", "Far+Green",  GRN,  "bRot (coherent)",  "bRot (coherent)",     "Coherent rotator"),
        ("S3", "B", "Far+Green",  GRN,  "NonCoherent",       "NonCoherent",         "Noise in Field B"),
    ]
    for sf, fld, dc, dc_col, mot_pre, mot_post, role in rows:
        ax.text(cols[0], y, sf,       transform=ax.transAxes, fontsize=8.5, fontweight="bold", color="#222", va="top")
        ax.text(cols[1], y, fld,      transform=ax.transAxes, fontsize=8,   color="#444", va="top")
        ax.text(cols[2], y, dc,       transform=ax.transAxes, fontsize=8,   color=dc_col, fontweight="bold", va="top")
        ax.text(cols[3], y, mot_pre,  transform=ax.transAxes, fontsize=7.5, color="#444", va="top")
        highlight = sf == "S0"
        ax.text(cols[4], y, mot_post, transform=ax.transAxes, fontsize=7.5,
                color=BLU if highlight else "#444",
                fontweight="bold" if highlight else "normal", va="top")
        ax.text(cols[5], y, role,     transform=ax.transAxes, fontsize=7.5, color=GRY, va="top")
        y -= 0.020

    y -= 0.006

    # ── Section 2: The proposed swap ──────────────────────────────────────────
    T(ax, 0.06, y, "2.  Proposed S1↔S2 full attribute swap at tStart",
      fontsize=11, fontweight="bold", color=BLU, va="top")
    y -= 0.025

    T(ax, 0.08, y,
      "At tStart, S1 takes all of S2's attributes (depth, color, motion type, direction) and vice versa.",
      fontsize=8.5, color="#333", va="top")
    y -= 0.022

    # Before → After table for S1 and S2
    box(ax, 0.06, y-0.112, 0.88, 0.110, "#FFFFF0", ec="#CC9900", lw=0.8)

    # Header row
    hcols = [0.10, 0.26, 0.44, 0.62, 0.80]
    hh = ["Sub-\nfield", "Before tStart", "→", "After tStart", "What changed"]
    for x, h in zip(hcols, hh):
        ax.text(x, y-0.006, h, transform=ax.transAxes, fontsize=8,
                fontweight="bold", color="#333", va="top")
    y -= 0.005
    hline(ax, y-0.004, x0=0.07, x1=0.93, color="#CCA")
    y -= 0.018

    swap_rows = [
        ("S0", "Near+Red  aRot → translate", RED,
         "Near+Red  TRANSLATE", RED,
         "Motion only (normal onset)"),
        ("S1", "Near+Red  NonCoherent noise", RED,
         "Far+Green  bRot coherent", GRN,
         "Depth, color, coherence all change"),
        ("S2", "Far+Green  bRot coherent", GRN,
         "Near+Red  NonCoherent noise", RED,
         "Depth, color, coherence all change"),
        ("S3", "Far+Green  NonCoherent noise", GRN,
         "Far+Green  NonCoherent noise", GRN,
         "Unchanged"),
    ]
    for sf, pre, pre_col, post, post_col, change in swap_rows:
        changed = sf in ("S1", "S2")
        ax.text(hcols[0], y, sf, transform=ax.transAxes, fontsize=8.5,
                fontweight="bold", color="#222", va="top")
        ax.text(hcols[1], y, pre, transform=ax.transAxes, fontsize=7.5,
                color=pre_col, va="top")
        ax.text(hcols[2]+0.005, y, "→", transform=ax.transAxes, fontsize=9,
                color=ORG if changed else GRY,
                fontweight="bold" if changed else "normal", va="top")
        ax.text(hcols[3], y, post, transform=ax.transAxes, fontsize=7.5,
                color=post_col, fontweight="bold" if changed else "normal", va="top")
        ax.text(hcols[4], y, change, transform=ax.transAxes, fontsize=7,
                color=ORG if changed else GRY, va="top")
        y -= 0.022

    y -= 0.010

    # ── Section 3: Validity check ─────────────────────────────────────────────
    T(ax, 0.06, y, "3.  Validity check — single color per depth plane?",
      fontsize=11, fontweight="bold", color=BLU, va="top")
    y -= 0.025

    box(ax, 0.06, y-0.058, 0.88, 0.056, "#F0FFF0", ec="#228B22", lw=0.8)
    checks = [
        ("Near plane after swap:  S0 (Red) + S2 (Red) = Near is Red throughout",   "✓", GRN),
        ("Far plane after swap:   S1 (Green) + S3 (Green) = Far is Green throughout", "✓", GRN),
        ("Single color per plane maintained.",  "", GRN),
    ]
    for txt, mark, col in checks:
        ax.text(0.10, y-0.008, mark + "  " + txt, transform=ax.transAxes,
                fontsize=8.5, color=col, fontweight="bold", va="top")
        y -= 0.018
    y -= 0.008

    # ── Section 4: The problem ────────────────────────────────────────────────
    T(ax, 0.06, y, "4.  The problem — post-onset appearance is identical to no-swap",
      fontsize=11, fontweight="bold", color=RED, va="top")
    y -= 0.025

    T(ax, 0.08, y,
      "Compare what the observer sees after tStart:",
      fontsize=8.5, color="#333", va="top")
    y -= 0.022

    box(ax, 0.06, y-0.082, 0.88, 0.080, "#FFF4F4", ec="#CC3333", lw=0.8)

    tcols = [0.10, 0.30, 0.58]
    ax.text(tcols[0], y-0.006, "Condition",  transform=ax.transAxes, fontsize=8, fontweight="bold", color="#333", va="top")
    ax.text(tcols[1], y-0.006, "Near plane (Red)", transform=ax.transAxes, fontsize=8, fontweight="bold", color=RED, va="top")
    ax.text(tcols[2], y-0.006, "Far plane (Green)", transform=ax.transAxes, fontsize=8, fontweight="bold", color=GRN, va="top")
    y -= 0.005
    hline(ax, y-0.004, x0=0.07, x1=0.93, color="#DDD")
    y -= 0.018

    compare = [
        ("No swap",         "S0 translates  +  S1 noise",  "S2 coherent rotates  +  S3 noise"),
        ("S1↔S2 swap",      "S0 translates  +  S2 noise",  "S1 coherent rotates  +  S3 noise"),
    ]
    for cond, near, far in compare:
        bold = cond == "S1↔S2 swap"
        ax.text(tcols[0], y, cond, transform=ax.transAxes, fontsize=8,
                fontweight="bold" if bold else "normal",
                color=RED if bold else "#444", va="top")
        ax.text(tcols[1], y, near, transform=ax.transAxes, fontsize=7.5, color="#444", va="top")
        ax.text(tcols[2], y, far,  transform=ax.transAxes, fontsize=7.5, color="#444", va="top")
        y -= 0.022

    y -= 0.008
    box(ax, 0.08, y-0.046, 0.84, 0.044, "#FFF0F0", ec="#CC3333", lw=1.0)
    ax.text(0.50, y-0.010,
            "Dots within a plane are physically indistinguishable.\n"
            "The observer cannot tell whether the near-noise is S1 or S2,\n"
            "or whether the coherent rotator in Far is S1 or S2.",
            transform=ax.transAxes, fontsize=8.5, color="#333",
            ha="center", va="top", linespacing=1.5)
    y -= 0.054

    y -= 0.010

    # ── Section 5: Conclusion ─────────────────────────────────────────────────
    T(ax, 0.06, y, "5.  Conclusion",
      fontsize=11, fontweight="bold", color=BLU, va="top")
    y -= 0.025

    box(ax, 0.06, y-0.112, 0.88, 0.110, "#FFF9E6", ec="#CC9900", lw=1.0)

    conclusions = [
        ("✓ Valid:",
         "S1↔S2 swap maintains single color per depth plane — it does not violate the "
         "clean-plane rule.", False),
        ("✗ Useless:",
         "The post-onset stimulus is perceptually identical to no-swap. "
         "The observer sees the same functional structure: Near = translator + noise, "
         "Far = coherent rotator + noise. Only the anonymous labels on the dots change, "
         "which the observer has no access to.", True),
        ("→ Why:",
         "S1 and S2 start in opposite planes. Swapping their attributes just moves "
         "one anonymous noise cloud to Far and promotes it to coherent, while demoting "
         "the existing coherent rotator to noise in Near. "
         "The result is structurally and perceptually equivalent to having done nothing.", False),
        ("→ Bottom line:",
         "Any 50% swap that keeps planes clean either (a) produces a perceptually "
         "invisible rearrangement like this, or (b) changes both depth and color "
         "simultaneously — preventing independent manipulation of either. "
         "This is why 100% whole-field swaps are the minimum workable unit.", True),
    ]
    y -= 0.010
    for label, text, bold in conclusions:
        lc = RED if "✗" in label else (GRN if "✓" in label else BLU)
        ax.text(0.10, y, label, transform=ax.transAxes, fontsize=8.5,
                fontweight="bold", color=lc, va="top")
        ax.text(0.25, y, text, transform=ax.transAxes, fontsize=8,
                color="#222" if bold else "#444",
                fontweight="bold" if bold else "normal",
                va="top", wrap=True,
                bbox=dict(boxstyle="square,pad=0", fc="none", ec="none"))
        y -= 0.025 if len(text) < 100 else 0.030

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

print(f"Wrote: {OUT}")
