#!/usr/bin/env python3
"""
Analysis: Why 50% dot-plane swaps cannot cleanly decouple depth from color
while keeping S0 (coherent translator) fixed.

Output: Agents/WriteUps/decoupled_50pct_analysis.pdf
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

OUT = (sys.argv[1] if len(sys.argv) > 1 else
       "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/"
       "Agents/WriteUps/decoupled_50pct_analysis.pdf")

RED  = "#CC3333"
GRN  = "#228B22"
GRAY = "#888888"
BLU  = "#1a3a8b"
ORG  = "#CC6600"
BG   = "#F9F9FF"

def T(ax, x, y, s, **kw):
    return ax.text(x, y, s, transform=ax.transAxes, **kw)

with PdfPages(OUT) as pdf:

    # ── Page 1: The constraint analysis ───────────────────────────────────────
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # ── Title ─────────────────────────────────────────────────────────────────
    T(ax, 0.5, 0.975,
      "Why 50% Dot-Plane Swaps Cannot Cleanly Decouple Depth × Color",
      ha="center", va="top", fontsize=14, fontweight="bold", color="#111")
    T(ax, 0.5, 0.950,
      "Given: S0 (coherent translator) fixed at Near=Red throughout  ·  "
      "Rule: single color per depth plane at all times",
      ha="center", va="top", fontsize=9, color="#555", style="italic")

    # ── Section 1: Setup ──────────────────────────────────────────────────────
    y = 0.915
    T(ax, 0.06, y, "Starting configuration (Cond 1, no swap)", fontsize=11,
      fontweight="bold", color=BLU, va="top")
    y -= 0.028

    setup = [
        ("S0 ●", "Near", "Red",   "Coherent translator — FIXED throughout",   True),
        ("S1 □", "Near", "Red",   "Noise companion of translator",             False),
        ("S2 ▲", "Far",  "Green", "Coherent rotator",                         False),
        ("S3 ◇", "Far",  "Green", "Noise rotator",                            False),
    ]
    cols = [0.07, 0.16, 0.26, 0.36, 0.50]
    hdrs = ["Subfield", "Depth", "Color", "Role", ""]
    for x, h in zip(cols, hdrs):
        ax.text(x, y, h, transform=ax.transAxes, fontsize=8,
                fontweight="bold", color="#333", va="top")
    y -= 0.005
    ax.add_artist(plt.Line2D([0.06, 0.92], [y + 0.015]*2,
                              transform=ax.transAxes, color="#888", lw=0.8))
    y -= 0.018

    for s, dep, col, role, fixed in setup:
        fc = RED if col == "Red" else GRN
        dc = "#1a3a8b" if dep == "Near" else "#553300"
        ax.text(cols[0], y, s, transform=ax.transAxes, fontsize=8.5, va="top",
                fontweight="bold" if fixed else "normal", color="#222")
        ax.text(cols[1], y, dep, transform=ax.transAxes, fontsize=8.5, va="top", color=dc)
        ax.text(cols[2], y, col, transform=ax.transAxes, fontsize=8.5, va="top",
                fontweight="bold", color=fc)
        ax.text(cols[3], y, role, transform=ax.transAxes, fontsize=8, va="top", color="#444")
        if fixed:
            ax.text(0.88, y, "◄ cannot change",
                    transform=ax.transAxes, fontsize=8, va="top",
                    color=RED, fontweight="bold")
        y -= 0.022

    y -= 0.010

    # ── Section 2: The constraint chain ───────────────────────────────────────
    T(ax, 0.06, y, "The constraint chain", fontsize=11, fontweight="bold",
      color=BLU, va="top")
    y -= 0.030

    chain = [
        ("S0 pinned at Near+Red",
         "Near plane must be Red (S0 is there and is Red)."),
        ("Any dot in Near must be Red",
         "Moving any dot to Near without making it Red → mixed colors in Near plane. ✗"),
        ("Any dot in Far must be Green",
         "Far is the only other plane; it must be a single color. Green is the only option."),
        ("Depth change = forced color change",
         "Moving a dot between planes forces it to adopt the destination plane's color.\n"
         "You cannot independently manipulate depth without also changing color."),
    ]

    for i, (title, body) in enumerate(chain):
        box = FancyBboxPatch((0.06, y - 0.058), 0.88, 0.055,
                             boxstyle="round,pad=0.005",
                             facecolor=BG, edgecolor="#BBBBCC", lw=0.7,
                             transform=ax.transAxes, zorder=2)
        ax.add_patch(box)
        ax.text(0.09, y - 0.008, f"{i+1}.", transform=ax.transAxes,
                fontsize=10, fontweight="bold", color=BLU, va="top", zorder=3)
        ax.text(0.13, y - 0.008, title, transform=ax.transAxes,
                fontsize=9, fontweight="bold", color="#222", va="top", zorder=3)
        ax.text(0.13, y - 0.030, body, transform=ax.transAxes,
                fontsize=8, color="#444", va="top", zorder=3, wrap=True)
        y -= 0.068

    y -= 0.010

    # ── Section 3: All possible partial swaps ─────────────────────────────────
    T(ax, 0.06, y, "All possible partial swaps — outcomes", fontsize=11,
      fontweight="bold", color=BLU, va="top")
    y -= 0.028

    tcols = [0.07, 0.23, 0.36, 0.52, 0.65, 0.78]
    theads = ["Subfields\nchanged", "Change\ntype", "Near\nplane", "Far\nplane",
              "Clean\nplanes?", "Problem"]
    for x, h in zip(tcols, theads):
        ax.text(x, y, h, transform=ax.transAxes, fontsize=7.5,
                fontweight="bold", color="#333", va="top")
    y -= 0.005
    ax.add_artist(plt.Line2D([0.06, 0.97], [y + 0.015]*2,
                              transform=ax.transAxes, color="#888", lw=0.8))
    y -= 0.020

    rows = [
        # (changed, change_type, near_after, far_after, clean, problem)
        ("S1 only",    "depth only\n(Near→Far)",
         "S0(R)",          "S1(R)+S2(G)+S3(G)", "✗", "Far: mixed R+G"),
        ("S1 only",    "color only\n(Red→Grn)",
         "S0(R)+S1(G)",    "S2(G)+S3(G)",        "✗", "Near: mixed R+G"),
        ("S2 only",    "depth only\n(Far→Near)",
         "S0(R)+S1(R)+S2(G)","S3(G)",            "✗", "Near: mixed R+G"),
        ("S2 only",    "color only\n(Grn→Red)",
         "S0(R)+S1(R)",    "S2(R)+S3(G)",        "✗", "Far: mixed R+G"),
        ("S3 only",    "depth only\n(Far→Near)",
         "S0(R)+S1(R)+S3(G)","S2(G)",            "✗", "Near: mixed R+G"),
        ("S3 only",    "color only\n(Grn→Red)",
         "S0(R)+S1(R)",    "S2(G)+S3(R)",        "✗", "Far: mixed R+G"),
        ("S1+S2",      "depth+color",
         "S0(R)+S2(R)",    "S1(G)+S3(G)",        "✓*", "S2 leaves Far; Near has S0+S2\n→ density change, S0 isolated"),
        ("S1+S3",      "any",
         "S0(R)+S1(?)\nor S3(?)",  "—",          "✗", "Cannot recolor without\nmixing planes"),
        ("S2+S3",      "color only\n(Grn→Red)",
         "S0(R)+S1(R)",    "S2(R)+S3(R)",        "✓*", "Both planes Red — color\ndistinction lost"),
        ("S2+S3",      "depth only\n(Far→Near)",
         "S0+S1+S2+S3\n(all Near!)", "—",        "✗", "Far plane empty;\nNear: mixed R+G"),
        ("S2+S3",      "depth+color\n(Far→Near+Red)",
         "all 4 subs (R)", "—",                  "✗", "Far plane empty;\nno depth distinction"),
        ("S1↔S3\n(swap planes)", "depth+color\nboth change",
         "S0(R)+S3(R)",   "S1(G)+S2(G)",         "✓*", "Clean, but depth+color\ntied together — not independent"),
    ]

    for i, (chg, ctyp, near, far, clean, prob) in enumerate(rows):
        bg = "#FFF8F8" if clean == "✗" else "#F0FFF0" if clean == "✓*" else "white"
        row_h = 0.043
        box = FancyBboxPatch((0.06, y - row_h + 0.004), 0.91, row_h,
                             boxstyle="square,pad=0",
                             facecolor=bg, edgecolor="#DDD", lw=0.4,
                             transform=ax.transAxes, zorder=1)
        ax.add_patch(box)
        cc = RED if clean == "✗" else "#228B22" if clean == "✓*" else "#444"
        ax.text(tcols[0], y, chg,   transform=ax.transAxes, fontsize=7,   va="top", color="#222")
        ax.text(tcols[1], y, ctyp,  transform=ax.transAxes, fontsize=7,   va="top", color="#444")
        ax.text(tcols[2], y, near,  transform=ax.transAxes, fontsize=6.5, va="top", color="#333")
        ax.text(tcols[3], y, far,   transform=ax.transAxes, fontsize=6.5, va="top", color="#333")
        ax.text(tcols[4], y, clean, transform=ax.transAxes, fontsize=8,   va="top",
                color=cc, fontweight="bold")
        ax.text(tcols[5], y, prob,  transform=ax.transAxes, fontsize=6.5, va="top", color="#555")
        y -= row_h + 0.003

    y -= 0.010

    # ── Section 4: Conclusion ─────────────────────────────────────────────────
    T(ax, 0.06, y, "Conclusion", fontsize=11, fontweight="bold", color=BLU, va="top")
    y -= 0.030

    concl_box = FancyBboxPatch((0.06, y - 0.100), 0.88, 0.097,
                               boxstyle="round,pad=0.008",
                               facecolor="#FFF9E6", edgecolor="#CC9900", lw=1.0,
                               transform=ax.transAxes, zorder=2)
    ax.add_patch(concl_box)

    lines = [
        ("No viable 50% swap independently manipulates depth OR color while keeping S0 fixed "
         "and both depth planes occupied with a single color each.",
         True, "#111"),
        ("The three ✓* rows above either lose the color distinction (both planes become the same "
         "color), empty one plane, or bundle depth and color changes together (S1↔S3 swap) "
         "— preventing independent decoupling.",
         False, "#333"),
        ("Therefore: 100% whole-field swaps (both fields change together) are the minimal "
         "condition for clean independent Depth × Color manipulation. This is why Conds 1–8 "
         "are designed the way they are.",
         True, "#1a1a6e"),
    ]
    y -= 0.012
    for bold, color_needed, col in [(True, True, "#111"), (False, False, "#333"), (True, True, "#1a1a6e")]:
        pass

    for text, bld, col in lines:
        ax.text(0.09, y, ("• " if not bld else "→ ") + text,
                transform=ax.transAxes, fontsize=8.5,
                fontweight="bold" if bld else "normal",
                color=col, va="top", wrap=True,
                bbox=dict(boxstyle="square,pad=0", fc="none", ec="none"))
        # estimate wrap manually
        y -= 0.026 if len(text) < 120 else 0.038
        y -= 0.006

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

print(f"Wrote: {OUT}")
