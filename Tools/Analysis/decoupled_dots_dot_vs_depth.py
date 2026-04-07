#!/usr/bin/env python3
"""
decoupled_dots_dot_vs_depth.py

Two-panel figure:

  Panel A — 2×2: Dot cueing × Depth-field cueing
    Four cells (collapsing over color, all 4 sessions):
      Dot✓  Depth✓  →  CUED   + N/C
      Dot✓  Depth✗  →  CUED   + Z/CZ
      Dot✗  Depth✓  →  UNCUED + Z/CZ
      Dot✗  Depth✗  →  UNCUED + N/C
    Key comparison: the two conflict cells (middle two).

  Panel B — Depth-swap disruptiveness
    All 8 conditions (Cond × SwapType) as % correct, grouped by CUED / UNCUED.
    Depth-swap conditions (Z, CZ) highlighted to show how much the swap costs
    relative to the no-swap baseline (N), and whether adding color (CZ vs Z)
    makes any additional difference.

Output: Agents/Figures/decoupled_dots_dot_vs_depth.png + .pdf
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from scipy.stats import chi2_contingency

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv", False),
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv", False),
]
FIG_DIR = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/")
OUT_PNG = os.path.join(FIG_DIR, "decoupled_dots_dot_vs_depth.png")
OUT_PDF = os.path.join(FIG_DIR, "decoupled_dots_dot_vs_depth.pdf")

CHANCE = 1 / 8

# ── Stats ──────────────────────────────────────────────────────────────────────
def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return (c - hw)*100, (c + hw)*100

def chi2_p(k1, n1, k2, n2):
    _, p, _, _ = chi2_contingency([[k1, n1-k1], [k2, n2-k2]], correction=False)
    return p

def stars(p):
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

# ── Load ───────────────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

# Raw (cond, swap) → [k, n]
raw = {}
for cond in ('CUED', 'UNCUED'):
    for swap in ('N', 'C', 'Z', 'CZ'):
        raw[(cond, swap)] = [0, 0]

for path, invert in SESSIONS:
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    for r in rows:
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip():
            continue
        if r.get('EndKey','') in ('timeout','skip','requeue'):
            continue
        cond = r['Cond']
        if invert:
            cond = 'UNCUED' if cond == 'CUED' else 'CUED'
        swap = r['SwapType']
        if (cond, swap) not in raw:
            continue
        corr = int(is_correct(r['TransDeg'], r['RespDeg']))
        raw[(cond, swap)][0] += corr
        raw[(cond, swap)][1] += 1

def pool(*pairs):
    k = sum(raw[p][0] for p in pairs)
    n = sum(raw[p][1] for p in pairs)
    return k, n

# 2×2 cells
cells = {
    'both':       pool(('CUED','N'),   ('CUED','C')),
    'dot_no_dep': pool(('CUED','Z'),   ('CUED','CZ')),
    'dep_no_dot': pool(('UNCUED','Z'), ('UNCUED','CZ')),
    'neither':    pool(('UNCUED','N'), ('UNCUED','C')),
}

# ── Print ──────────────────────────────────────────────────────────────────────
print("2×2 cells:")
for label, (k,n) in [
    ('Both ✓     (CUED+N/C)',    cells['both']),
    ('Dot✓Dep✗  (CUED+Z/CZ)',   cells['dot_no_dep']),
    ('Dot✗Dep✓  (UNCUED+Z/CZ)', cells['dep_no_dot']),
    ('Neither   (UNCUED+N/C)',   cells['neither']),
]:
    print(f"  {label:<30} {k/n*100:.1f}%  (n={n})")

print()
print("Conflict comparison (Dot✓/Dep✗ vs Dot✗/Dep✓):")
k1,n1 = cells['dot_no_dep']; k2,n2 = cells['dep_no_dot']
p_conf = chi2_p(k1,n1,k2,n2)
print(f"  Δ = {k1/n1*100 - k2/n2*100:+.1f}pp  {stars(p_conf)}")

print()
print("All 8 conditions:")
for cond in ('CUED','UNCUED'):
    for swap in ('N','C','Z','CZ'):
        k,n = raw[(cond,swap)]
        print(f"  {cond:<7} {swap:<3}  {k/n*100:5.1f}%  (n={n})")
    print()

print("Depth-swap cost (Z vs N, CZ vs N):")
for cond in ('CUED','UNCUED'):
    kn,nn = raw[(cond,'N')]
    for swap in ('Z','CZ'):
        ks,ns = raw[(cond,swap)]
        cost = ks/ns*100 - kn/nn*100
        p = chi2_p(ks,ns,kn,nn)
        print(f"  {cond} {swap} vs N:  {cost:+.1f}pp  {stars(p)}")

# ── Colors ─────────────────────────────────────────────────────────────────────
C_N   = '#555555'   # no swap — grey
C_C   = '#7B5EA7'   # color swap only — purple
C_Z   = '#CC3300'   # depth swap — red-orange (disruptive)
C_CZ  = '#FF7744'   # color+depth swap — lighter red-orange

SWAP_COLS = {'N': C_N, 'C': C_C, 'Z': C_Z, 'CZ': C_CZ}
SWAP_HATCHES = {'N': None, 'C': '//', 'Z': None, 'CZ': '//'}

# ── Figure ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 6.5))
fig.patch.set_facecolor('white')
gs = gridspec.GridSpec(1, 2, left=0.06, right=0.97, bottom=0.13,
                       top=0.88, wspace=0.38, width_ratios=[1, 1.35])

# ══════════════════════════════════════════════════════════════════════════════
# Panel A — 2×2
# ══════════════════════════════════════════════════════════════════════════════
ax_a = fig.add_subplot(gs[0])

cell_order  = ['both', 'dot_no_dep', 'dep_no_dot', 'neither']
cell_colors = {
    'both':       '#2c4f8c',
    'dot_no_dep': '#1565C0',
    'dep_no_dot': '#1a6e8b',
    'neither':    '#999999',
}
cell_labels = {
    'both':       'Dot ✓  Depth ✓\n(CUED + N/C)',
    'dot_no_dep': 'Dot ✓  Depth ✗\n(CUED + Z/CZ)',
    'dep_no_dot': 'Dot ✗  Depth ✓\n(UNCUED + Z/CZ)',
    'neither':    'Dot ✗  Depth ✗\n(UNCUED + N/C)',
}

bar_vals_a = []
for xi, cell in enumerate(cell_order):
    k, n = cells[cell]
    p_pct = k/n*100
    lo, hi = wilson_ci(k, n)
    bar_vals_a.append(p_pct)
    ax_a.bar(xi, p_pct, 0.58, color=cell_colors[cell], alpha=0.88, zorder=3,
             edgecolor='white', linewidth=0.5)
    ax_a.errorbar(xi, p_pct, yerr=[[p_pct-lo],[hi-p_pct]], fmt='none',
                  color='#333', capsize=5, capthick=1.3, lw=1.3, zorder=4)
    ax_a.text(xi, p_pct/2, f'{p_pct:.1f}%\n(n={n})',
              ha='center', va='center', fontsize=9, color='white', fontweight='bold')

def bracket(ax, x1, x2, y, label, color='#333'):
    ax.plot([x1, x1, x2, x2], [y-0.8, y, y, y-0.8], color=color, lw=1.1)
    ax.text((x1+x2)/2, y+0.5, label,
            ha='center', va='bottom', fontsize=10, color=color, fontweight='bold')

# Conflict bracket (cells 1 & 2)
k1,n1 = cells['dot_no_dep']; k2,n2 = cells['dep_no_dot']
bracket(ax_a, 1, 2,
        max(bar_vals_a[1], bar_vals_a[2]) + 9,
        f'Δ = {k1/n1*100 - k2/n2*100:+.1f}pp  {stars(chi2_p(k1,n1,k2,n2))}  ◀ conflict',
        color='#CC3300')

# Aligned bracket (cells 0 & 3)
k1,n1 = cells['both']; k2,n2 = cells['neither']
bracket(ax_a, 0, 3,
        max(bar_vals_a[0], bar_vals_a[3]) + 9,
        f'Δ = {k1/n1*100 - k2/n2*100:+.1f}pp  {stars(chi2_p(k1,n1,k2,n2))}  ◀ aligned',
        color='#1a6e8b')

ax_a.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
ax_a.text(3.38, CHANCE*100 + 0.5, 'chance', fontsize=8, color='#999')
ax_a.set_xticks(range(4))
ax_a.set_xticklabels([cell_labels[c] for c in cell_order], fontsize=9)
ax_a.set_ylabel('% correct', fontsize=10)
ax_a.set_ylim(0, 74)
ax_a.set_title('A.  Dot × Depth-field cueing — 2×2\n'
               '(collapsing over color swap)', fontsize=10, fontweight='bold', pad=8)
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)
ax_a.grid(axis='y', lw=0.4, alpha=0.35, zorder=0)

# ══════════════════════════════════════════════════════════════════════════════
# Panel B — All 8 conditions, depth-swap disruptiveness
# ══════════════════════════════════════════════════════════════════════════════
ax_b = fig.add_subplot(gs[1])

SWAP_ORDER = ['N', 'C', 'Z', 'CZ']
group_gap  = 0.55
bar_w      = 0.38
inner_gap  = 0.06

x_ticks = []
x_labels = []
x_shade  = []   # x ranges for Z/CZ shading

for gi, cond in enumerate(['CUED','UNCUED']):
    x_base = gi * (len(SWAP_ORDER) * (bar_w + inner_gap) + group_gap)
    for si, swap in enumerate(SWAP_ORDER):
        x = x_base + si * (bar_w + inner_gap)
        k, n = raw[(cond, swap)]
        p_pct = k/n*100
        lo, hi = wilson_ci(k, n)
        col = SWAP_COLS[swap]
        hatch = SWAP_HATCHES[swap]
        ax_b.bar(x, p_pct, bar_w, color=col, alpha=0.85, zorder=3,
                 edgecolor='white', linewidth=0.5, hatch=hatch)
        ax_b.errorbar(x, p_pct, yerr=[[p_pct-lo],[hi-p_pct]], fmt='none',
                      color='#333', capsize=3.5, capthick=1.1, lw=1.1, zorder=4)
        # % label
        if p_pct > 10:
            ax_b.text(x, p_pct/2, f'{p_pct:.0f}%',
                      ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        else:
            ax_b.text(x, p_pct + 1, f'{p_pct:.0f}%',
                      ha='center', va='bottom', fontsize=8, color='#333')

        if si == 0 or si == len(SWAP_ORDER)-1:
            x_ticks.append(x)
        if si == 1:
            # midpoint of group for cond label
            x_mid = x_base + 1.5 * (bar_w + inner_gap)
            x_labels.append((x_mid, cond))

        # Mark depth-swap conditions with cost arrow
        if swap in ('Z','CZ'):
            x_shade.append(x)

        # Cost annotation: delta from N within same cond
        kn, nn = raw[(cond,'N')]
        cost = p_pct - kn/nn*100
        p_cost = chi2_p(k,n,kn,nn)
        if swap != 'N':
            y_ann = p_pct + (hi - p_pct) + 1.5
            # small cost label above error bar
            ax_b.text(x, y_ann,
                      f'{cost:+.0f}pp\nvs N',
                      ha='center', va='bottom', fontsize=6.5,
                      color=col if swap in ('Z','CZ') else '#888',
                      fontweight='bold' if swap in ('Z','CZ') else 'normal')

# Group x-tick positions: one tick per bar
all_xs = []
all_xlbls = []
for gi, cond in enumerate(['CUED','UNCUED']):
    x_base = gi * (len(SWAP_ORDER) * (bar_w + inner_gap) + group_gap)
    for si, swap in enumerate(SWAP_ORDER):
        x = x_base + si * (bar_w + inner_gap)
        all_xs.append(x)
        all_xlbls.append(swap)

ax_b.set_xticks(all_xs)
ax_b.set_xticklabels(all_xlbls, fontsize=9)

# CUED / UNCUED group labels below
for x_mid, cond in x_labels:
    ax_b.text(x_mid, -5.5, cond,
              ha='center', va='top', fontsize=10, fontweight='bold',
              color='#1565C0' if cond == 'CUED' else '#E65100')

# Shade the depth-swap region lightly within each group
for gi, cond in enumerate(['CUED','UNCUED']):
    x_base = gi * (len(SWAP_ORDER) * (bar_w + inner_gap) + group_gap)
    x_z   = x_base + 2*(bar_w + inner_gap)
    x_cz  = x_base + 3*(bar_w + inner_gap)
    ax_b.axvspan(x_z - bar_w*0.6, x_cz + bar_w*0.6, alpha=0.07, color='#CC3300', zorder=1)

# N baseline annotation per group
for gi, cond in enumerate(['CUED','UNCUED']):
    x_base = gi * (len(SWAP_ORDER) * (bar_w + inner_gap) + group_gap)
    kn, nn = raw[(cond,'N')]
    y_ref = kn/nn*100
    x_end = x_base + 3*(bar_w + inner_gap) + bar_w*0.5
    ax_b.annotate('', xy=(x_end, y_ref), xytext=(x_base - bar_w*0.5, y_ref),
                  arrowprops=dict(arrowstyle='-', color='#555', lw=0.8, linestyle='dashed'))

ax_b.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
ax_b.text(all_xs[-1] + bar_w*0.7, CHANCE*100, 'chance\n12.5%',
          fontsize=7.5, color='#999', va='center')

ax_b.set_ylabel('% correct', fontsize=10)
ax_b.set_ylim(0, 74)
ax_b.set_xlim(all_xs[0] - bar_w, all_xs[-1] + bar_w*2.2)
ax_b.set_title('B.  All 8 conditions — depth-swap disruptiveness\n'
               '(cost labels = Δ vs N baseline within each group)',
               fontsize=10, fontweight='bold', pad=8)
ax_b.spines['top'].set_visible(False)
ax_b.spines['right'].set_visible(False)
ax_b.grid(axis='y', lw=0.4, alpha=0.35, zorder=0)

# Legend
legend_patches = [
    mpatches.Patch(color=C_N,  label='N  — no swap'),
    mpatches.Patch(color=C_C,  label='C  — color swap only', hatch='//'),
    mpatches.Patch(color=C_Z,  label='Z  — depth swap only'),
    mpatches.Patch(color=C_CZ, label='CZ — color + depth swap', hatch='//'),
]
ax_b.legend(handles=legend_patches, fontsize=8, loc='upper right',
            framealpha=0.9, handlelength=1.8)

# ── Suptitle & footnote ────────────────────────────────────────────────────────
fig.suptitle('DecoupledDots — Dot vs Depth-field cueing  (all 4 sessions, n≈2051)',
             fontsize=12, fontweight='bold', y=0.97)
fig.text(0.5, 0.01,
         'Depth-field ✓ = translator ends in depth plane where delayed field first appeared  |  '
         'Error bars: 95% Wilson CI  |  cost labels: Δpp vs N, brackets: two-sided χ²  |  '
         'Shaded region = depth-swap conditions (Z, CZ)',
         ha='center', va='bottom', fontsize=7, color='#555')

os.makedirs(FIG_DIR, exist_ok=True)
fig.savefig(OUT_PNG, dpi=150, bbox_inches='tight', facecolor='white')
fig.savefig(OUT_PDF, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {OUT_PNG}")
print(f"Saved: {OUT_PDF}")
