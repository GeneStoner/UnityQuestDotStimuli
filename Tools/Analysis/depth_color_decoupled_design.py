#!/usr/bin/env python3
"""
Condition list for the Depth × Color decoupling experiment.

Extends DepthColorLinked by independently controlling whether the
coherent translator and/or its noise companion changes depth plane
and/or color at translation onset (tStart).

Output: Agents/WriteUps/depth_color_decoupled_design.pdf
"""

import sys, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

OUT = (sys.argv[1] if len(sys.argv) > 1 else
       "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/"
       "Agents/WriteUps/depth_color_decoupled_design.pdf")

PW, PH = 8.5, 11
C_CUED   = "#1a6b1a"
C_UNCUED = "#555555"
C_DEPTH  = "#1a3a8b"
C_COLOR  = "#8b1a1a"
C_BOTH   = "#5a1a8b"
C_N      = "#888888"
C_HEAD   = "#1a1a6e"
C_NEW    = "#cc4400"

def page():
    fig = plt.figure(figsize=(PW, PH))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    return fig, ax

def T(ax, x, y, s, fs=9, bold=False, col="black", ha="left", va="top", italic=False):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs,
            fontweight="bold" if bold else "normal",
            fontstyle="italic" if italic else "normal",
            color=col, fontfamily="sans-serif")

def rule(ax, y, x0=0.07, x1=0.93, col="#aaaaaa", lw=0.7):
    ax.axhline(y, xmin=x0, xmax=x1, color=col, lw=lw)

def wrap(ax, x, y, s, width=95, fs=8.5, col="black", indent=0, lsp=0.032, italic=False):
    for line in textwrap.wrap(s, width):
        T(ax, x + indent, y, line, fs=fs, col=col, italic=italic)
        y -= lsp
    return y - 0.006

def section(ax, y, s):
    T(ax, 0.07, y, s, fs=10, bold=True, col=C_HEAD)
    rule(ax, y - 0.022, col="#BBBBCC", lw=0.9)
    return y - 0.032

def chk(v):
    return "✓" if v else "✗"

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Overview & Factor structure
# ══════════════════════════════════════════════════════════════════════════════
with PdfPages(OUT) as pdf:

    fig, ax = page()
    T(ax, 0.5, 0.965,
      "Depth × Color Decoupling — Experiment Design",
      fs=13, bold=True, col="#111111", ha="center")
    T(ax, 0.5, 0.940,
      "Independent control of depth-plane and color identity for translator and noise companion",
      fs=8.5, col="#555", ha="center", italic=True)

    y = 0.912
    rule(ax, y)
    y -= 0.014

    y = section(ax, y, "Motivation")
    y = wrap(ax, 0.07, y,
        "In DepthColorLinked (current experiment), Near=Red and Far=Green are always linked "
        "(linkDepthColor=1). ZdCoh (ZdA) changes BOTH the depth plane and the color of the "
        "coherent translator simultaneously; ZdNoi (ZdB) changes BOTH for the noise companion. "
        "F2 (Depth Cueing) is therefore confounded with color change — it is impossible to "
        "determine whether the disruption in ZdCoh is driven by depth, color, or both.",
        col="#333")
    y = wrap(ax, 0.07, y,
        "Additional confound in F1 (Dot Cueing): color reversals hit the TARGET in CUED+ZdCoh "
        "but the DISTRACTOR in UNCUED+ZdCoh — the comparison is asymmetric in disruption, "
        "making F1 a conservative underestimate of the true dot-cueing advantage.",
        col="#333")
    y -= 0.010

    y = section(ax, y, "Three independent factors at tStart")

    rows = [
        ("F1", "Dot Cueing",
         "CUED vs UNCUED — does the delayed-onset field translate?",
         C_CUED),
        ("F2", "Depth Swap on translator",
         "Does the coherent translator change depth plane at tStart?  (YES → new depth plane)",
         C_DEPTH),
        ("F3", "Color Swap on translator",
         "Does the coherent translator change color at tStart?  (YES → new color)",
         C_COLOR),
    ]
    for code, name, desc, col in rows:
        T(ax, 0.07, y, code,    fs=8.5, bold=True, col=col)
        T(ax, 0.135, y, name,   fs=8.5, bold=True, col=col)
        T(ax, 0.07, y - 0.024, desc, fs=8, col="#333")
        y -= 0.050

    y -= 0.004
    y = wrap(ax, 0.07, y,
        "The noise companion is held at NO SWAP (neither depth nor color changes) throughout "
        "the primary experiment — this isolates the translator's identity change as the sole "
        "variable. Companion-swap conditions (ZdB-type) are listed separately on page 3 as a "
        "secondary extension.",
        col="#555", italic=False)
    y -= 0.008

    rule(ax, y)
    y -= 0.014

    y = section(ax, y, "Stimulus identity: Near = Red · Far = Green (unchanged)")
    y = wrap(ax, 0.07, y,
        "At trial start the translator occupies depth DFD (Near or Far, balanced) with the "
        "corresponding color (Red or Green). At tStart it may jump to the opposite depth, "
        "switch to the opposite color, both, or neither — as determined by F2 × F3.",
        col="#333")
    y -= 0.006

    # Small diagram of the 2×2 F2×F3 swap options
    T(ax, 0.5, y, "Translator state at tStart  (example: starts Near = Red)",
      fs=8, bold=True, col=C_HEAD, ha="center")
    y -= 0.028

    boxes = [
        (0.15, "Depth NO\nColor NO", "Near+Red\n(no change)", C_N,    "= N baseline"),
        (0.37, "Depth YES\nColor NO", "Far+Red\n(depth only)", C_DEPTH,"= ZdA (new)"),
        (0.59, "Depth NO\nColor YES", "Near+Green\n(color only)", C_COLOR,"= ZcA (new)"),
        (0.81, "Depth YES\nColor YES", "Far+Green\n(both)", C_BOTH,   "= ZdcA = current ZdCoh"),
    ]
    bw, bh = 0.16, 0.095
    for xc, hdr, body, col, note in boxes:
        rect = plt.Rectangle((xc - bw/2, y - bh), bw, bh,
                              facecolor=col+"22", edgecolor=col, lw=1.2,
                              transform=ax.transAxes)
        ax.add_patch(rect)
        T(ax, xc, y - 0.008, hdr,  fs=7,   bold=True, col=col, ha="center")
        T(ax, xc, y - 0.032, body, fs=8,   col="#111",  ha="center")
        T(ax, xc, y - bh + 0.006, note, fs=6.5, col="#555", ha="center", italic=True)

    y -= bh + 0.018

    y = wrap(ax, 0.07, y,
        "DFD is balanced: half the trials start Near=Red, half start Far=Green. "
        "Swap directions are therefore symmetric across the design.",
        col="#555", fs=8)

    T(ax, 0.5, 0.022,
      "VRDots — Depth × Color Decoupling Design.  2026-04-06.",
      fs=7, col="#999", ha="center", italic=True)

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2 — Full primary condition table (F1 × F2 × F3, companion = no swap)
    # ══════════════════════════════════════════════════════════════════════════
    fig, ax = page()
    T(ax, 0.5, 0.965,
      "Primary Conditions  (companion = no swap throughout)",
      fs=13, bold=True, col="#111111", ha="center")
    T(ax, 0.5, 0.940,
      "2 (Dot Cueing) × 2 (Depth Swap) × 2 (Color Swap) = 8 conditions  ×  2 (DFD Near/Far) = 16 cells",
      fs=8.5, col="#555", ha="center", italic=True)

    y = 0.912
    rule(ax, y)
    y -= 0.018

    # Table header
    COL_X = [0.07, 0.19, 0.32, 0.42, 0.52, 0.63, 0.76, 0.88]
    HDRS  = ["#", "Code", "F1 Dots", "F2 Depth\nswap", "F3 Color\nswap",
             "Translator\nat tStart", "Current\nanalog", "Predicted\nperf"]
    for x, h in zip(COL_X, HDRS):
        T(ax, x, y, h, fs=7.5, bold=True, col=C_HEAD)
    y -= 0.038
    rule(ax, y, col="#888888", lw=0.8)
    y -= 0.008

    # (num, cued, depth_swap, color_swap, code, analog, predicted_note)
    CONDITIONS = [
        # ── CUED ──────────────────────────────────────────────────────────────
        (1,  True,  False, False, "CUED + N",    "N baseline\n(not run yet)",
         "High  ~+35pp"),
        (2,  True,  True,  False, "CUED + ZdA",  "New",
         "?  depth only\n disruptive?"),
        (3,  True,  False, True,  "CUED + ZcA",  "New",
         "?  color only\n disruptive?"),
        (4,  True,  True,  True,  "CUED + ZdcA", "= current ZdCoh\n(ZdA+color)",
         "Reduced ~+18pp"),
        # ── UNCUED ────────────────────────────────────────────────────────────
        (5,  False, False, False, "UNCUED + N",   "N baseline\n(not run yet)",
         "Low  ~+10pp"),
        (6,  False, True,  False, "UNCUED + ZdA", "New",
         "?"),
        (7,  False, False, True,  "UNCUED + ZcA", "New",
         "?"),
        (8,  False, True,  True,  "UNCUED + ZdcA","= current ZdCoh\n(UNCUED)",
         "Low  ~+9pp"),
    ]

    ROW_BG = ["#F0F8F0", "#E8F0FF", "#FFF0F0", "#F5F0FF"]
    sep_drawn = False
    for i, (num, cued, d_swap, c_swap, code, analog, pred) in enumerate(CONDITIONS):
        if not cued and not sep_drawn:
            rule(ax, y + 0.005, col="#AAAAAA", lw=0.5)
            y -= 0.004
            sep_drawn = True

        bg_col = ("#EEF8EE" if (not d_swap and not c_swap) else
                  "#E8F0FF" if (d_swap and not c_swap) else
                  "#FFF0F0" if (not d_swap and c_swap) else
                  "#F5F0FF")
        rect = plt.Rectangle((0.065, y - 0.052), 0.865, 0.056,
                              facecolor=bg_col, edgecolor="none",
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)

        dot_col  = C_CUED if cued else C_UNCUED
        dep_col  = C_DEPTH if d_swap else C_N
        clr_col  = C_COLOR if c_swap else C_N

        if d_swap and c_swap:   swap_col = C_BOTH
        elif d_swap:             swap_col = C_DEPTH
        elif c_swap:             swap_col = C_COLOR
        else:                    swap_col = C_N

        # Translator state: what it becomes
        if not d_swap and not c_swap:
            trans_lbl = "keeps depth+color"
        elif d_swap and not c_swap:
            trans_lbl = "→ opp. depth\n  same color"
        elif not d_swap and c_swap:
            trans_lbl = "  same depth\n→ opp. color"
        else:
            trans_lbl = "→ opp. depth\n→ opp. color"

        is_new = "New" in analog
        an_col = C_NEW if is_new else "#444"

        T(ax, COL_X[0], y - 0.008, str(num),       fs=8,   col="#333")
        T(ax, COL_X[1], y - 0.008, code,            fs=7.5, col=dot_col, bold=True)
        T(ax, COL_X[2], y - 0.008, "CUED" if cued else "UNCUED", fs=8, col=dot_col)
        T(ax, COL_X[3], y - 0.008, chk(d_swap),    fs=9,   col=dep_col, bold=True)
        T(ax, COL_X[4], y - 0.008, chk(c_swap),    fs=9,   col=clr_col, bold=True)
        T(ax, COL_X[5], y - 0.006, trans_lbl,       fs=7,   col=swap_col)
        T(ax, COL_X[6], y - 0.006, analog,          fs=7,   col=an_col, italic=is_new)
        T(ax, COL_X[7], y - 0.006, pred,            fs=7,   col="#444")
        y -= 0.060

    y -= 0.012
    rule(ax, y)
    y -= 0.018

    y = section(ax, y, "Predicted patterns by hypothesis")

    hyp_rows = [
        ("Depth-driven",
         "Cond 2 ≈ Cond 4  (ZdA ≈ ZdcA, both disrupted);  Cond 3 ≈ Cond 1  (ZcA ≈ N, both spared).\n"
         "F2 survives when depth changes; F3 null when color changes alone."),
        ("Color-driven",
         "Cond 3 ≈ Cond 4  (ZcA ≈ ZdcA, both disrupted);  Cond 2 ≈ Cond 1  (ZdA ≈ N, spared).\n"
         "F3 survives; F2 null."),
        ("Additive",
         "Cond 4 < Cond 2 < Cond 1  and  Cond 4 < Cond 3 < Cond 1.\n"
         "Both F2 and F3 significant; ZdcA worst."),
        ("Interaction",
         "Cond 2 and Cond 3 each produce partial disruption; Cond 4 disproportionately\n"
         "worse than either alone (depth × color interaction)."),
    ]
    for hyp, desc in hyp_rows:
        T(ax, 0.07, y, hyp + ":", fs=8.5, bold=True, col=C_HEAD)
        y -= 0.022
        for line in desc.split("\n"):
            T(ax, 0.10, y, line, fs=8, col="#333")
            y -= 0.020
        y -= 0.004

    y -= 0.008
    y = section(ax, y, "Trial counts")
    y = wrap(ax, 0.07, y,
        "8 conditions × 2 DFD (Near/Far) = 16 cells.  At 32 trials/cell → 512 trials/session "
        "(same as DepthColorLinked).  Two sessions → n=64/cell, sufficient to detect ≥15pp "
        "differences at α=0.05 with ~80% power.  F1 is now clean: both CUED and UNCUED "
        "sides include N (no swap) and matched swap conditions, eliminating the target-vs-"
        "distractor asymmetry present in the current design.",
        col="#333")

    T(ax, 0.5, 0.022,
      "VRDots — Depth × Color Decoupling Design.  2026-04-06.",
      fs=7, col="#999", ha="center", italic=True)

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 3 — Secondary conditions (companion-swap variants) + full condition matrix
    # ══════════════════════════════════════════════════════════════════════════
    fig, ax = page()
    T(ax, 0.5, 0.965,
      "Secondary Conditions  (companion swap, translator = no swap)",
      fs=13, bold=True, col="#111111", ha="center")
    T(ax, 0.5, 0.940,
      "Mirrors page 2 but varies the noise companion instead of the translator",
      fs=8.5, col="#555", ha="center", italic=True)

    y = 0.912
    rule(ax, y)
    y -= 0.018

    COL_X2 = [0.07, 0.19, 0.32, 0.42, 0.52, 0.63, 0.76, 0.88]
    for x, h in zip(COL_X2, HDRS):
        T(ax, x, y, h, fs=7.5, bold=True, col=C_HEAD)
    y -= 0.038
    rule(ax, y, col="#888888", lw=0.8)
    y -= 0.008

    SEC_CONDITIONS = [
        # companion changes, translator = N (no swap)
        # N is same as primary cond 1/5 — listed for completeness
        (9,  True,  False, False, "CUED + N",     "= primary #1", "same cell"),
        (10, True,  True,  False, "CUED + ZdB",   "New",          "?  companion depth only"),
        (11, True,  False, True,  "CUED + ZcB",   "New",          "?  companion color only"),
        (12, True,  True,  True,  "CUED + ZdcB",  "= current ZdNoi",  "High  ~+35pp"),
        (13, False, False, False, "UNCUED + N",    "= primary #5", "same cell"),
        (14, False, True,  False, "UNCUED + ZdB",  "New",          "?"),
        (15, False, False, True,  "UNCUED + ZcB",  "New",          "?"),
        (16, False, True,  True,  "UNCUED + ZdcB", "= current ZdNoi UNCUED", "Low  ~+11pp"),
    ]

    sep_drawn = False
    for (num, cued, d_swap, c_swap, code, analog, pred) in SEC_CONDITIONS:
        if not cued and not sep_drawn:
            rule(ax, y + 0.005, col="#AAAAAA", lw=0.5)
            y -= 0.004
            sep_drawn = True

        dot_col = C_CUED if cued else C_UNCUED
        dep_col = C_DEPTH if d_swap else C_N
        clr_col = C_COLOR if c_swap else C_N
        if d_swap and c_swap: swap_col = C_BOTH
        elif d_swap:          swap_col = C_DEPTH
        elif c_swap:          swap_col = C_COLOR
        else:                 swap_col = C_N

        if not d_swap and not c_swap:
            trans_lbl = "companion:\nno change"
        elif d_swap and not c_swap:
            trans_lbl = "companion:\n→ opp. depth"
        elif not d_swap and c_swap:
            trans_lbl = "companion:\n→ opp. color"
        else:
            trans_lbl = "companion:\n→ depth+color"

        is_new = "New" in analog
        an_col = C_NEW if is_new else "#444"
        bg_col = ("#EEF8EE" if (not d_swap and not c_swap) else
                  "#E8F0FF" if (d_swap and not c_swap) else
                  "#FFF0F0" if (not d_swap and c_swap) else
                  "#F5F0FF")
        rect = plt.Rectangle((0.065, y - 0.052), 0.865, 0.056,
                              facecolor=bg_col, edgecolor="none",
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)

        T(ax, COL_X2[0], y - 0.008, str(num),        fs=8,   col="#333")
        T(ax, COL_X2[1], y - 0.008, code,             fs=7.5, col=dot_col, bold=True)
        T(ax, COL_X2[2], y - 0.008, "CUED" if cued else "UNCUED", fs=8, col=dot_col)
        T(ax, COL_X2[3], y - 0.008, chk(d_swap),     fs=9,   col=dep_col, bold=True)
        T(ax, COL_X2[4], y - 0.008, chk(c_swap),     fs=9,   col=clr_col, bold=True)
        T(ax, COL_X2[5], y - 0.006, trans_lbl,        fs=7,   col=swap_col)
        T(ax, COL_X2[6], y - 0.006, analog,           fs=7,   col=an_col, italic=is_new)
        T(ax, COL_X2[7], y - 0.006, pred,             fs=7,   col="#444")
        y -= 0.060

    y -= 0.010
    rule(ax, y)
    y -= 0.018

    y = section(ax, y, "Combined primary + secondary: new SwapFlags needed")
    flag_rows = [
        ("Color50A  (ZcA)", "Color swap on coherent translator only (no depth change)", C_COLOR),
        ("Color50B  (ZcB)", "Color swap on noise companion only (no depth change)",     C_COLOR),
        ("Depth50A  (ZdA)", "Depth swap on coherent translator — ALREADY IMPLEMENTED",  C_DEPTH),
        ("Depth50B  (ZdB)", "Depth swap on noise companion — ALREADY IMPLEMENTED",      C_DEPTH),
    ]
    for flag, desc, col in flag_rows:
        T(ax, 0.09,  y, flag, fs=8, bold=True, col=col)
        T(ax, 0.315, y, desc, fs=8, col="#333")
        y -= 0.028

    y -= 0.010
    y = wrap(ax, 0.07, y,
        "ZdcA = Depth50A | Color50A (translator changes both).  "
        "ZdcB = Depth50B | Color50B (companion changes both) = current ZdNoi.  "
        "Bit-combining existing and new flags gives all 16 conditions without new enum values "
        "beyond Color50A and Color50B.",
        col="#555", fs=8)

    y -= 0.008
    y = section(ax, y, "Recommended run order")
    y = wrap(ax, 0.07, y,
        "Phase 1 (primary, 8 conditions): Run 2 sessions (~512 trials each) to answer "
        "depth vs color on the TRANSLATOR. This directly resolves the ZdCoh confound. "
        "Include N (no swap) baseline — currently absent from DepthColorLinked.",
        col="#333")
    y = wrap(ax, 0.07, y,
        "Phase 2 (secondary, 6 new companion conditions): Add ZdB, ZcB to test whether "
        "companion identity also matters. Can be combined with Phase 1 replication for "
        "efficiency (16 conditions × 2 DFD × 16 trials = 512 trials/session).",
        col="#333")
    y = wrap(ax, 0.07, y,
        "Both phases keep Near=Red / Far=Green and depth sep = 0.05 m to maintain "
        "comparability with DepthColorLinked sessions.",
        col="#555", fs=8)

    T(ax, 0.5, 0.022,
      "VRDots — Depth × Color Decoupling Design.  2026-04-06.",
      fs=7, col="#999", ha="center", italic=True)

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

print(f"Wrote: {OUT}")
