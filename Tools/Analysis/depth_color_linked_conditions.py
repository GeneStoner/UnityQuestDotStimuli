#!/usr/bin/env python3
"""
Enumerate all condition types in Exp_DepthColorLinked.asset.

Key settings:
  linkDepthColor = 1    (depth and color co-vary: whichever field is Near gets Red,
                         Far gets Green — and color changes when depth changes at tStart)
  balanceDelayedFieldColor = 1   (delayed field is Red in half trials, Green in other half)
  balanceDelayedFieldDepth = 1   (delayed field is Near in half trials, Far in other half)
  includeDepth50ASwaps = 1  (ZdA: coherent pair S0↔S2 swap depth planes at tStart)
  includeDepth50BSwaps = 1  (ZdB: noise pair S1↔S3 swap depth planes at tStart)
  includeNoSwapBaseline = 0  (no no-swap baseline)
  includeBothRotationConfigs = 1
  delayTranslator = true (default): Field B (Sub2+Sub3) is the delayed field

Trial count: 2(CUED/UNCUED) × 8(heading) × 2(rotCfg) × 2(DelColor) × 2(DelDepth) × 2(ZdA/ZdB)
           = 256

Output: Agents/WriteUps/depth_color_linked_conditions.pdf
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

OUT = (sys.argv[1] if len(sys.argv) > 1 else
       "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/"
       "Agents/WriteUps/depth_color_linked_conditions.pdf")

RED   = "#CC3333"
GRN   = "#228B22"
BLU   = "#1a3a8b"
DKRED = "#7a0000"
DKGRN = "#004400"
GRY   = "#777777"
BG    = "#F9F9FF"
BGW   = "white"

def T(ax, x, y, s, **kw):
    return ax.text(x, y, s, transform=ax.transAxes, **kw)

def colored_text(ax, x, y, parts, base_kw=None):
    """Draw multiple (text, color) segments inline at (x,y) in axes coords."""
    if base_kw is None:
        base_kw = {}
    fig = ax.get_figure()
    renderer = fig.canvas.get_renderer()
    cur_x = x
    for txt, col in parts:
        t = ax.text(cur_x, y, txt, transform=ax.transAxes,
                    color=col, **base_kw)
        t.draw(renderer)
        bb = t.get_window_extent(renderer=renderer)
        bb_ax = bb.transformed(ax.transAxes.inverted())
        cur_x = bb_ax.x1

def depth_color_str(depth, color, depth_col, color_col, fs=7):
    """Return (depth_str, depth_col, color_str, color_col) parts for inline coloring."""
    return [(depth, depth_col), ("+", "#444"), (color, color_col)]

with PdfPages(OUT) as pdf:

    # ── Page 1: Design Overview ────────────────────────────────────────────────
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # Title
    T(ax, 0.5, 0.978,
      "Exp_DepthColorLinked — All Condition Types",
      ha="center", va="top", fontsize=13, fontweight="bold", color="#111")
    T(ax, 0.5, 0.956,
      "linkDepthColor=1 · ZdA+ZdB · no baseline · n=256 trials · delayTranslator=true (Field B delayed)",
      ha="center", va="top", fontsize=8.5, color="#555", style="italic")

    # ── Factor table ───────────────────────────────────────────────────────────
    y = 0.930
    T(ax, 0.06, y, "Trial count", fontsize=10, fontweight="bold", color=BLU, va="top")
    y -= 0.025
    factors = [
        ("CUED / UNCUED",        "2",  "which subfield is the coherent translator (S2 or S0)"),
        ("Heading",              "×8", "8 translation directions"),
        ("Rotation config",      "×2", "RotA (S0=CW, S2=CCW) vs RotB (S0=CCW, S2=CW)"),
        ("Delayed field color",  "×2", "Field B color = Red or Green"),
        ("Delayed field depth",  "×2", "Field B depth = Near or Far"),
        ("Swap",                 "×2", "ZdA or ZdB (no baseline)"),
        ("= Total",              "256",""),
    ]
    for i, (label, val, note) in enumerate(factors):
        bold = (i == len(factors) - 1)
        bg = "#E8EEF8" if bold else BGW
        box = FancyBboxPatch((0.06, y - 0.018), 0.88, 0.020,
                              boxstyle="square,pad=0", facecolor=bg,
                              edgecolor="#DDD", lw=0.3, transform=ax.transAxes, zorder=1)
        ax.add_patch(box)
        ax.text(0.08, y - 0.004, label, transform=ax.transAxes, fontsize=8,
                fontweight="bold" if bold else "normal", color="#222", va="top", zorder=2)
        ax.text(0.40, y - 0.004, val, transform=ax.transAxes, fontsize=8,
                fontweight="bold" if bold else "normal", color=BLU, va="top", zorder=2)
        ax.text(0.48, y - 0.004, note, transform=ax.transAxes, fontsize=7.5,
                color="#555", va="top", zorder=2)
        y -= 0.022

    y -= 0.008

    # ── linkDepthColor explanation ─────────────────────────────────────────────
    T(ax, 0.06, y, "linkDepthColor=1: what it means", fontsize=10, fontweight="bold",
      color=BLU, va="top")
    y -= 0.025
    box = FancyBboxPatch((0.06, y - 0.058), 0.88, 0.056,
                          boxstyle="round,pad=0.006", facecolor="#FFF9E6",
                          edgecolor="#CC9900", lw=0.8, transform=ax.transAxes, zorder=2)
    ax.add_patch(box)
    lines = [
        "· Each depth plane has one color throughout: the Near plane is always one color, Far always the other.",
        "· When ZdA or ZdB moves a subfield to a new depth plane at tStart, it also changes that subfield's color.",
        "· Result: depth and color change are inseparable — you cannot distinguish which cue drove perception.",
    ]
    for ln in lines:
        ax.text(0.09, y - 0.006, ln, transform=ax.transAxes, fontsize=8,
                color="#333", va="top", zorder=3)
        y -= 0.018
    y -= 0.012

    # ── Terminology box ────────────────────────────────────────────────────────
    T(ax, 0.06, y, "Terminology", fontsize=10, fontweight="bold", color=BLU, va="top")
    y -= 0.025

    terms = [
        ("Field B (delayed)", "Sub2+Sub3, hidden before onset (delayTranslator=true). Appears at t_onset."),
        ("Field A (always)",  "Sub0+Sub1, visible from the start. Rotating (aRot direction)."),
        ("CUED",              "S2 is the coherent translator. Temporal cue (Field B onset) correctly marks translator."),
        ("UNCUED",            "S0 is the coherent translator (in Field A, always present). Temporal cue marks rotator."),
        ("ZdA",               "At tStart: S0↔S2 exchange depth planes (and colors). The two coherent subfields swap."),
        ("ZdB",               "At tStart: S1↔S3 exchange depth planes (and colors). The two noise subfields swap."),
        ("DelB = Near+Red",   "Field B starts in Near plane, Red color. Field A is Far+Green."),
        ("DelB = Near+Green", "Field B starts in Near, Green. Field A is Far+Red. (Inverted depth-color.)"),
        ("DelB = Far+Red",    "Field B starts in Far, Red. Field A is Near+Green. (Inverted depth-color.)"),
        ("DelB = Far+Green",  "Field B starts in Far, Green. Field A is Near+Red. (Standard depth-color, Far delayed.)"),
    ]
    for term, defn in terms:
        ax.text(0.08, y, term + ":", transform=ax.transAxes, fontsize=7.5,
                fontweight="bold", color="#222", va="top")
        ax.text(0.29, y, defn, transform=ax.transAxes, fontsize=7.5,
                color="#444", va="top")
        y -= 0.018

    y -= 0.010

    # ── Depth-color assignment note ────────────────────────────────────────────
    T(ax, 0.06, y,
      "Depth-color assignment across configs (Near=? Far=?):",
      fontsize=8.5, fontweight="bold", color="#333", va="top")
    y -= 0.020
    dcols = [0.07, 0.22, 0.37, 0.52, 0.67]
    dhdrs = ["Config", "DelB", "Field A (always)", "Near plane color", "Far plane color"]
    for x, h in zip(dcols, dhdrs):
        ax.text(x, y, h, transform=ax.transAxes, fontsize=7.5,
                fontweight="bold", color="#333", va="top")
    y -= 0.004
    ax.add_artist(plt.Line2D([0.06, 0.92], [y + 0.012]*2,
                              transform=ax.transAxes, color="#AAA", lw=0.6))
    y -= 0.016
    cfg_rows = [
        ("A", "Near+Red",   "Far+Green",  RED,   GRN),
        ("B", "Near+Green", "Far+Red",    GRN,   RED),
        ("C", "Far+Red",    "Near+Green", GRN,   RED),
        ("D", "Far+Green",  "Near+Red",   RED,   GRN),
    ]
    for cfg, delb, always, near_col, far_col in cfg_rows:
        near_label = "Red" if near_col == RED else "Green"
        far_label  = "Red" if far_col  == RED else "Green"
        ax.text(dcols[0], y, cfg,       transform=ax.transAxes, fontsize=8, fontweight="bold", color="#222", va="top")
        ax.text(dcols[1], y, delb,      transform=ax.transAxes, fontsize=7.5, color="#444", va="top")
        ax.text(dcols[2], y, always,    transform=ax.transAxes, fontsize=7.5, color="#444", va="top")
        ax.text(dcols[3], y, near_label,transform=ax.transAxes, fontsize=8, fontweight="bold", color=near_col, va="top")
        ax.text(dcols[4], y, far_label, transform=ax.transAxes, fontsize=8, fontweight="bold", color=far_col, va="top")
        y -= 0.018

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

    # ── Page 2: Full conditions table ─────────────────────────────────────────
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    T(ax, 0.5, 0.978, "All 16 Condition Types (before ×heading ×rotCfg)",
      ha="center", va="top", fontsize=12, fontweight="bold", color="#111")
    T(ax, 0.5, 0.957,
      "Each row × 2 rotConfigs × 8 headings = 32 trials.  16 rows × 16 = 256 total.",
      ha="center", va="top", fontsize=8.5, color="#555", style="italic")

    y = 0.930

    # Column headers
    col_x = [0.02, 0.09, 0.16, 0.30, 0.44, 0.62, 0.80]
    col_hdrs = ["Cfg", "Swap", "Cued?", "Pre-onset\n(Field A visible)", "Onset adds\n(Field B appears)",
                "What changes\nat tStart", "Translator\nplane+color at tStart"]
    for x, h in zip(col_x, col_hdrs):
        ax.text(x, y, h, transform=ax.transAxes, fontsize=7.5,
                fontweight="bold", color="#333", va="top")
    y -= 0.005
    ax.add_artist(plt.Line2D([0.02, 0.98], [y + 0.014]*2,
                              transform=ax.transAxes, color="#777", lw=0.8))
    y -= 0.020

    # (cfg_label, swap, cued, pre_onset, onset_adds, what_changes, translator_plane, translator_color)
    ROW_H = 0.038
    rows = [
        # Config A: DelB=Near+Red, FieldA=Far+Green, Near=Red, Far=Green
        ("A", "ZdA", "CUED",   "Far+Green",  "Near+Red",  "S0: Far→Near (Green→Red)\nS2: Near→Far (Red→Green)", "Far", "Green"),
        ("A", "ZdA", "UNCUED", "Far+Green",  "Near+Red",  "S0: Far→Near (Green→Red)\nS2: Near→Far (Red→Green)", "Near","Red"),
        ("A", "ZdB", "CUED",   "Far+Green",  "Near+Red",  "S1: Far→Near (Green→Red)\nS3: Near→Far (Red→Green)", "Near","Red"),
        ("A", "ZdB", "UNCUED", "Far+Green",  "Near+Red",  "S1: Far→Near (Green→Red)\nS3: Near→Far (Red→Green)", "Far", "Green"),
        # Config B: DelB=Near+Green, FieldA=Far+Red, Near=Green, Far=Red
        ("B", "ZdA", "CUED",   "Far+Red",    "Near+Green","S0: Far→Near (Red→Green)\nS2: Near→Far (Green→Red)",  "Far", "Red"),
        ("B", "ZdA", "UNCUED", "Far+Red",    "Near+Green","S0: Far→Near (Red→Green)\nS2: Near→Far (Green→Red)",  "Near","Green"),
        ("B", "ZdB", "CUED",   "Far+Red",    "Near+Green","S1: Far→Near (Red→Green)\nS3: Near→Far (Green→Red)",  "Near","Green"),
        ("B", "ZdB", "UNCUED", "Far+Red",    "Near+Green","S1: Far→Near (Red→Green)\nS3: Near→Far (Green→Red)",  "Far", "Red"),
        # Config C: DelB=Far+Red, FieldA=Near+Green, Near=Green, Far=Red
        ("C", "ZdA", "CUED",   "Near+Green", "Far+Red",   "S0: Near→Far (Green→Red)\nS2: Far→Near (Red→Green)",  "Near","Green"),
        ("C", "ZdA", "UNCUED", "Near+Green", "Far+Red",   "S0: Near→Far (Green→Red)\nS2: Far→Near (Red→Green)",  "Far", "Red"),
        ("C", "ZdB", "CUED",   "Near+Green", "Far+Red",   "S1: Near→Far (Green→Red)\nS3: Far→Near (Red→Green)",  "Far", "Red"),
        ("C", "ZdB", "UNCUED", "Near+Green", "Far+Red",   "S1: Near→Far (Green→Red)\nS3: Far→Near (Red→Green)",  "Near","Green"),
        # Config D: DelB=Far+Green, FieldA=Near+Red, Near=Red, Far=Green
        ("D", "ZdA", "CUED",   "Near+Red",   "Far+Green", "S0: Near→Far (Red→Green)\nS2: Far→Near (Green→Red)",  "Near","Red"),
        ("D", "ZdA", "UNCUED", "Near+Red",   "Far+Green", "S0: Near→Far (Red→Green)\nS2: Far→Near (Green→Red)",  "Far", "Green"),
        ("D", "ZdB", "CUED",   "Near+Red",   "Far+Green", "S1: Near→Far (Red→Green)\nS3: Far→Near (Green→Red)",  "Far", "Green"),
        ("D", "ZdB", "UNCUED", "Near+Red",   "Far+Green", "S1: Near→Far (Red→Green)\nS3: Far→Near (Green→Red)",  "Near","Red"),
    ]

    cfg_colors = {"A": "#E8F0FF", "B": "#FFF0E8", "C": "#E8FFE8", "D": "#FFF8E8"}

    for i, (cfg, swap, cued, pre, onset, changes, trans_plane, trans_color) in enumerate(rows):
        bg = cfg_colors[cfg]
        tc = RED if trans_color == "Red" else GRN
        # shade CUED rows slightly darker
        if cued == "CUED":
            bg = bg  # keep
        else:
            # lighten for UNCUED
            bg = "white"
        box = FancyBboxPatch((0.02, y - ROW_H + 0.004), 0.96, ROW_H,
                              boxstyle="square,pad=0", facecolor=bg,
                              edgecolor="#CCC", lw=0.3, transform=ax.transAxes, zorder=1)
        ax.add_patch(box)

        ax.text(col_x[0], y - 0.004, cfg,  transform=ax.transAxes, fontsize=8,
                fontweight="bold", color="#222", va="top", zorder=2)
        ax.text(col_x[1], y - 0.004, swap, transform=ax.transAxes, fontsize=7.5,
                color="#333", va="top", zorder=2)
        cued_col = BLU if cued == "CUED" else "#884400"
        ax.text(col_x[2], y - 0.004, cued, transform=ax.transAxes, fontsize=7.5,
                fontweight="bold" if cued == "CUED" else "normal",
                color=cued_col, va="top", zorder=2)

        # Color the Near/Far labels in pre and onset columns
        for col_idx, text in [(3, pre), (4, onset)]:
            if "Red" in text:
                col_str = RED
            elif "Green" in text:
                col_str = GRN
            else:
                col_str = "#444"
            ax.text(col_x[col_idx], y - 0.004, text, transform=ax.transAxes,
                    fontsize=7.5, color=col_str, va="top", zorder=2)

        ax.text(col_x[5], y - 0.004, changes, transform=ax.transAxes, fontsize=6.5,
                color="#555", va="top", zorder=2, linespacing=1.3)

        trans_str = f"S{'2' if cued == 'CUED' else '0'}: {trans_plane}+{trans_color}"
        ax.text(col_x[6], y - 0.004, trans_str, transform=ax.transAxes,
                fontsize=8, fontweight="bold", color=tc, va="top", zorder=2)

        # Separator between configs
        if i % 4 == 3 and i < len(rows) - 1:
            ax.add_artist(plt.Line2D([0.02, 0.98], [y - ROW_H + 0.003]*2,
                                      transform=ax.transAxes, color="#999", lw=0.6))

        y -= ROW_H + 0.001

    y -= 0.010

    # Key observations
    T(ax, 0.06, y, "Key observations", fontsize=9, fontweight="bold", color=BLU, va="top")
    y -= 0.020

    obs = [
        "1. linkDepthColor = depth and color are ALWAYS co-varied. You cannot know if depth or color drives the effect.",
        "2. Configs A+D: Near=Red, Far=Green. Configs B+C: Near=Green, Far=Red (inverted). Both included.",
        "3. In ZdA, the two COHERENT subfields (S0, S2) swap planes/colors. In ZdB, the two NOISE subfields (S1, S3) swap.",
        "4. In CUED+ZdA, the translator changes depth+color at tStart. In CUED+ZdB, the translator stays in its original plane.",
        "5. CUED: S2 translates (in Field B, appears at onset). UNCUED: S0 translates (in Field A, always visible).",
    ]
    for ob in obs:
        ax.text(0.04, y, ob, transform=ax.transAxes, fontsize=7.5, color="#333", va="top")
        y -= 0.018

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

print(f"Wrote: {OUT}")
