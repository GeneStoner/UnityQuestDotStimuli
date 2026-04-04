#!/usr/bin/env python3
"""
writeup_index.py — VRDots write-up index.
Generates a single-page US Letter PDF listing all pilot write-ups,
the experiments they cover, sessions, and key findings.

Output: Agents/WriteUps/writeup_index.pdf
"""

import os, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

OUT_PDF = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/writeup_index.pdf")

PW, PH = 8.5, 11
DPI = 150

def lh(pt, spacing=1.55):
    return (pt / 72 * DPI * spacing) / (PH * DPI)

# ── Entry definitions ─────────────────────────────────────────────────────────
# (filename, title, pages, sessions_str, key_finding)
ENTRIES = [
    (
        "baseline_writeup.pdf",
        "Baseline — No Depth, No Swap",
        2,
        "260323_1534 (pre-v0.2.0)  ·  260324_0716 (v0.2.0)",
        "+50 pp cueing (S1); +28 pp (S2, cursor-jump artifact). "
        "Red/green accuracy asymmetry in S1 likely reflects imperfect isoluminance. "
        "Both sessions confirm reliable delayed-onset cueing in VR."
    ),
    (
        "swap_writeup.pdf",
        "Flat Swap Conditions — Motion Swap & Dots50 Swap",
        2,
        "260324_1010 (MotionSwap)  ·  260325_1039 (Dots50Swap)",
        "Motion Swap (100%) attenuates cueing from ~27 pp → ~16 pp. "
        "Dots50 Swap (50% noise-subfield reassignment) produces no attenuation (~34 pp). "
        "Temporal onset asymmetry alone provides residual cueing benefit."
    ),
    (
        "depth_baseline_writeup.pdf",
        "Depth Baseline — No Swap, 0.03 m & 0.10 m",
        2,
        "260325_1831, 260325_1914 (0.10 m)  ·  260325_2013 (0.03 m)",
        "At 0.10 m: Far translation +19–28 pp**; Near translation near chance "
        "(2D signal masked by large disparity). At 0.03 m: Far +24 pp*, Near +9 pp n.s. "
        "Near-plane floor motivates DepthParam sweep."
    ),
    (
        "depth_swapctrl_writeup.pdf",
        "Depth Swap Control — ZdA / ZdB / N, 0.05 m",
        3,
        "260330_1853, 260331_0621, 260401_1313, 260401_1349, 260401_1541, 260401_1705 (bino)\n"
        "260330_2012, 260331_1530 (mono-R)  ·  260331_1705, 260331_1734 (mono-L)",
        "ZdA (coherent dot changes depth plane): +12 pp n.s. binocular, 0 pp monocular. "
        "ZdB (noise dot changes plane): +16 pp** binocular, +12 pp* monocular. "
        "N (no swap): +10 pp* binocular. "
        "Far > Near (binocular N); Near/Far difference entirely stereoscopic (disappears monocularly)."
    ),
    (
        "depthparam_writeup.pdf",
        "Depth Parameter Sweep — 0.03 / 0.05 / 0.10 / 0.15 m",
        2,
        "260402_0624 (0.10 m)  ·  260402_0656 (0.15 m)\n"
        "260402_0716 (0.03 m)  ·  260402_0757 (0.05 m)",
        "Far translation cueing: +47 pp across all depths (consistent). "
        "Near translation cueing: negative or near zero at all depths — "
        "Near-plane performance floor persists even at 0.03 m. "
        "Depth separation does not recover Near cueing; floor is likely a stereo-motion masking effect."
    ),
]

# ── Colour palette ────────────────────────────────────────────────────────────
ROW_COLORS = ['#EEF2F8', '#FFFFFF', '#EEF2F8', '#FFFFFF', '#EEF2F8']
ACCENT     = '#1a3a6b'
SUBTEXT    = '#444444'
ENTRY_SEP  = '#CCCCCC'

# ── Build figure ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(PW, PH))
fig.patch.set_facecolor('white')
LMAR = 0.07; RMAR = 0.93; TXT_W = RMAR - LMAR
WRAP_W = 110

y = 0.968

# Title
fig.text(0.50, y, 'VRDots Pilot — Write-Up Index',
         ha='center', va='top', fontsize=14, fontweight='bold', color='#111111')
y -= lh(14, 1.3) + 0.004

fig.text(0.50, y, 'All pilot sessions  ·  n = 1 observer  ·  Meta Quest 3  ·  2026-03-23 – 2026-04-02',
         ha='center', va='top', fontsize=7.5, color='#666666')
y -= lh(7.5, 1.3) + 0.012

# Divider
fig.add_artist(plt.Line2D([LMAR, RMAR], [y, y],
    transform=fig.transFigure, color='#999999', lw=1.0))
y -= 0.008

# Column headers
col_x = [LMAR, LMAR+0.30, LMAR+0.55, LMAR+0.63]
for cx, hdr in zip(col_x, ['File  ·  Title', 'Sessions', 'Pages', 'Key Findings']):
    fig.text(cx, y, hdr, ha='left', va='top', fontsize=7.5,
             fontweight='bold', color=ACCENT)
y -= lh(7.5, 1.4) + 0.004

fig.add_artist(plt.Line2D([LMAR, RMAR], [y, y],
    transform=fig.transFigure, color='#AAAAAA', lw=0.7))
y -= 0.006

# ── Entries ───────────────────────────────────────────────────────────────────
for ei, (fname, title, pages, sessions, finding) in enumerate(ENTRIES):
    row_top = y

    # Measure finding text height (widest column, takes most space)
    finding_wrap = textwrap.wrap(finding, width=48)
    session_wrap = sessions.split('\n')  # may have embedded \n
    title_wrap   = textwrap.wrap(title,  width=32)

    n_lines = max(len(title_wrap) + 1, len(session_wrap), len(finding_wrap))
    row_h   = n_lines * lh(7.5) + 0.014

    # Background band
    ax_bg = fig.add_axes([LMAR, y - row_h, TXT_W, row_h])
    ax_bg.set_facecolor(ROW_COLORS[ei % 2])
    ax_bg.axis('off')
    for sp in ax_bg.spines.values():
        sp.set_visible(False)

    # Filename (bold) + title
    fig.text(LMAR + 0.005, y - 0.004,
             fname, ha='left', va='top', fontsize=7.5,
             fontweight='bold', color='#111111')
    fig.text(LMAR + 0.005, y - 0.004 - lh(7.5, 1.3),
             '\n'.join(title_wrap), ha='left', va='top',
             fontsize=6.5, color=SUBTEXT, linespacing=1.4)

    # Sessions
    fig.text(LMAR + 0.30, y - 0.004,
             '\n'.join(session_wrap), ha='left', va='top',
             fontsize=6.5, color=SUBTEXT, linespacing=1.4)

    # Pages
    fig.text(LMAR + 0.55, y - 0.004,
             str(pages), ha='center', va='top', fontsize=7.5, color='#333333')

    # Finding
    fig.text(LMAR + 0.63, y - 0.004,
             '\n'.join(finding_wrap), ha='left', va='top',
             fontsize=6.5, color='#222222', linespacing=1.4)

    y -= row_h

    # Separator
    fig.add_artist(plt.Line2D([LMAR, RMAR], [y, y],
        transform=fig.transFigure, color=ENTRY_SEP, lw=0.5))
    y -= 0.004

# ── Footer ────────────────────────────────────────────────────────────────────
y -= 0.008
fig.add_artist(plt.Line2D([LMAR, RMAR], [y, y],
    transform=fig.transFigure, color='#999999', lw=0.8))
y -= 0.008

fig.text(LMAR, y,
    'Scripts: Tools/Analysis/  ·  '
    'Output: Agents/WriteUps/  ·  '
    'Registry: Tools/Analysis/sessions_registry.csv',
    ha='left', va='top', fontsize=6.5, color='#888888')

print(f"Bottom y = {y:.3f}")

with PdfPages(os.path.expanduser(OUT_PDF)) as pdf:
    pdf.savefig(fig, dpi=DPI, facecolor='white')

print(f"Saved: {OUT_PDF}")
