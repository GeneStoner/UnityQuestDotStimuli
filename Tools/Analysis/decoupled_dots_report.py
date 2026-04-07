#!/usr/bin/env python3
"""
decoupled_dots_report.py

Comprehensive 4-page PDF report of DecoupledDots results (all 4 sessions, n≈2051).

Page 1 — Three-factor overview
  Summary bar chart (Dot / Depth / Color cueing Δ) + key numbers table

Page 2 — Factor performance: raw % correct
  Cued vs Uncued arm for each of the 3 factors (absolute % correct)

Page 3 — Full 8-condition breakdown by swap type
  CUED and UNCUED × N / C / Z / CZ with depth-swap cost annotations

Page 4 — Dot × Depth head-to-head
  2×2 conflict figure + 8-condition disruptiveness breakdown

Output: Agents/Figures/decoupled_dots_report.pdf
"""

import csv, math, os, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import chi2_contingency

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv", False),
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv", False),
]
SESSION_LABELS = ['S1: 260406_1532 (DT)',
                  'S2: 260406_1754 (DTinv)',
                  'S3: 260407_0643 (DTinv)',
                  'S4: 260407_0731 (DT) ⚠']

FIG_DIR = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/")
OUT_PDF = os.path.join(FIG_DIR, "decoupled_dots_report.pdf")

CHANCE = 1 / 8

DEPTH_FIELD_CUED = {
    'CUED':   {'N': True,  'C': True,  'Z': False, 'CZ': False},
    'UNCUED': {'N': False, 'C': False, 'Z': True,  'CZ': True},
}
COLOR_FIELD_CUED = {
    'CUED':   {'N': True,  'C': False, 'Z': True,  'CZ': False},
    'UNCUED': {'N': False, 'C': True,  'Z': False, 'CZ': True},
}

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

def pct(k, n):
    return k/n*100 if n > 0 else 0.0

# ── Load ───────────────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

raw = {(c,s): [0,0] for c in ('CUED','UNCUED') for s in ('N','C','Z','CZ')}
n_total = 0

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
        n_total += 1

print(f"Loaded {n_total} valid trials")

def pool(*pairs):
    k = sum(raw[p][0] for p in pairs)
    n = sum(raw[p][1] for p in pairs)
    return k, n

# Derived aggregates
dot_cu   = pool(('CUED','N'),   ('CUED','C'),   ('CUED','Z'),   ('CUED','CZ'))
dot_un   = pool(('UNCUED','N'), ('UNCUED','C'),  ('UNCUED','Z'), ('UNCUED','CZ'))
dep_cu   = pool(('CUED','N'),   ('CUED','C'),   ('UNCUED','Z'), ('UNCUED','CZ'))
dep_un   = pool(('CUED','Z'),   ('CUED','CZ'),  ('UNCUED','N'), ('UNCUED','C'))
col_cu   = pool(('CUED','N'),   ('CUED','Z'),   ('UNCUED','C'), ('UNCUED','CZ'))
col_un   = pool(('CUED','C'),   ('CUED','CZ'),  ('UNCUED','N'), ('UNCUED','Z'))

cell_2x2 = {
    'both':       pool(('CUED','N'),   ('CUED','C')),
    'dot_no_dep': pool(('CUED','Z'),   ('CUED','CZ')),
    'dep_no_dot': pool(('UNCUED','Z'), ('UNCUED','CZ')),
    'neither':    pool(('UNCUED','N'), ('UNCUED','C')),
}

# ── Shared style constants ─────────────────────────────────────────────────────
C_CUED    = '#1565C0'
C_UNCUED  = '#E65100'
C_DOT_UN  = '#5B8FD6'
C_DEP_CU  = '#1a6e8b'
C_DEP_UN  = '#7ab8cc'
C_COL_CU  = '#8b5a1a'
C_COL_UN  = '#c49a5e'

C_N  = '#555555'
C_C  = '#7B5EA7'
C_Z  = '#CC3300'
C_CZ = '#FF7744'
SWAP_COLS = {'N': C_N, 'C': C_C, 'Z': C_Z, 'CZ': C_CZ}

YLIM = (0, 72)
YLIM_TIGHT = (0, 65)

# ── Drawing helpers ────────────────────────────────────────────────────────────
def draw_bar(ax, x, k, n, color, width=0.52, alpha=0.88, hatch=None):
    p = pct(k, n)
    lo, hi = wilson_ci(k, n)
    ax.bar(x, p, width, color=color, alpha=alpha, zorder=3,
           edgecolor='white', linewidth=0.5, hatch=hatch)
    ax.errorbar(x, p, yerr=[[p-lo],[hi-p]], fmt='none',
                color='#333', capsize=4, capthick=1.2, lw=1.2, zorder=4)
    if p > 11:
        ax.text(x, p/2, f'{p:.1f}%\nn={n}',
                ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    else:
        ax.text(x, p + 1.2, f'{p:.1f}%', ha='center', va='bottom', fontsize=8, color='#444')
    return p

def style_ax(ax, title='', ylim=YLIM, ylabel='% correct'):
    ax.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=9.5, fontweight='bold', pad=6)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=8.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.35, zorder=0)

def bracket(ax, x1, x2, y, label, color='#333', fs=9.5):
    ax.plot([x1, x1, x2, x2], [y-0.7, y, y, y-0.7], color=color, lw=1.0)
    ax.text((x1+x2)/2, y+0.4, label,
            ha='center', va='bottom', fontsize=fs, color=color, fontweight='bold')

def commentary_box(fig, lines, y_top=0.235, fs=8.5):
    """Place a block of commentary text at the bottom of a figure."""
    ax_t = fig.add_axes([0.05, 0.01, 0.90, y_top])
    ax_t.axis('off')
    ax_t.set_xlim(0, 1)
    ax_t.set_ylim(0, 1)
    # light background box
    from matplotlib.patches import FancyBboxPatch
    ax_t.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle='round,pad=0.01',
                                   fc='#F8F9FA', ec='#CCCCCC', lw=0.8,
                                   transform=ax_t.transAxes))
    y = 0.97
    lh = 1.05 / max(len(lines), 1)
    for line in lines:
        bold = line.startswith('**')
        txt = line.lstrip('* ')
        ax_t.text(0.012, y, txt, transform=ax_t.transAxes,
                  fontsize=fs, va='top', color='#222',
                  fontweight='bold' if bold else 'normal')
        y -= lh

def page_header(fig, title, subtitle=''):
    fig.text(0.5, 0.965, title,
             ha='center', va='top', fontsize=13, fontweight='bold', color='#111')
    if subtitle:
        fig.text(0.5, 0.945, subtitle,
                 ha='center', va='top', fontsize=9, color='#555')

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Three-factor overview
# ══════════════════════════════════════════════════════════════════════════════
def page1(pdf):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')
    page_header(fig,
        'DecoupledDots — Three Cueing Factors: Overview',
        f'All 4 sessions combined  ·  n={n_total} valid trials  ·  8-AFC (chance = 12.5%)')

    gs = gridspec.GridSpec(1, 2, left=0.07, right=0.96, bottom=0.28,
                           top=0.918, wspace=0.38)

    # ── Left: Δpp bar chart ──────────────────────────────────────────────────
    ax_l = fig.add_subplot(gs[0])

    factors = [
        ('Dot\ncueing', dot_cu, dot_un, C_CUED, 'CUED vs UNCUED\n(temporal onset marks translator)'),
        ('Depth-field\ncueing', dep_cu, dep_un, C_DEP_CU,
         'Depth-cued✓ vs Depth-uncued✗\n(translator in correct depth plane)'),
        ('Color-field\ncueing', col_cu, col_un, C_COL_CU,
         'Color-cued✓ vs Color-uncued✗\n(translator color matches delayed field)'),
    ]

    for xi, (lbl, (kc,nc), (ku,nu), col, _) in enumerate(factors):
        eff  = pct(kc,nc) - pct(ku,nu)
        pval = chi2_p(kc,nc,ku,nu)
        s    = stars(pval)
        ax_l.bar(xi, eff, 0.58, color=col, alpha=0.88, zorder=3,
                 edgecolor='white', linewidth=0.5)
        y_s = eff + 1.2 if eff >= 0 else eff - 1.5
        va_s = 'bottom' if eff >= 0 else 'top'
        ax_l.text(xi, y_s, s, ha='center', va=va_s, fontsize=11, color='#222')
        ax_l.text(xi, eff/2 if abs(eff) > 4 else eff+2.5,
                  f'{eff:+.1f}pp', ha='center', va='center',
                  fontsize=9, color='white' if abs(eff)>4 else '#333', fontweight='bold')

    ax_l.axhline(0, color='#888', lw=0.9, ls='--', zorder=2)
    ax_l.set_xticks([0,1,2])
    ax_l.set_xticklabels(['Dot\ncueing', 'Depth-field\ncueing', 'Color-field\ncueing'],
                         fontsize=9.5)
    ax_l.set_ylabel('Δ % correct  (cued − uncued)', fontsize=9)
    ax_l.set_ylim(-5, 26)
    ax_l.set_title('A.  Effect size (Δpp) for each factor', fontsize=10, fontweight='bold', pad=6)
    ax_l.spines['top'].set_visible(False)
    ax_l.spines['right'].set_visible(False)
    ax_l.grid(axis='y', lw=0.4, alpha=0.35, zorder=0)

    # ── Right: key numbers table ──────────────────────────────────────────────
    ax_r = fig.add_subplot(gs[1])
    ax_r.axis('off')
    ax_r.set_title('B.  Key numbers', fontsize=10, fontweight='bold', pad=6)

    headers = ['Factor', 'Cued ✓', 'Uncued ✗', 'Δ pp', 'p']
    col_xs  = [0.0, 0.30, 0.50, 0.70, 0.85]
    rows = []
    for lbl, (kc,nc), (ku,nu), col, defn in factors:
        ec   = pct(kc,nc)
        eu   = pct(ku,nu)
        eff  = ec - eu
        pval = chi2_p(kc,nc,ku,nu)
        rows.append((lbl.replace('\n',' '),
                     f'{ec:.1f}%  (n={nc})',
                     f'{eu:.1f}%  (n={nu})',
                     f'{eff:+.1f}',
                     stars(pval)))

    # Per-session dot cueing breakdown
    rows.append(('','','','',''))
    rows.append(('Per-session dot cueing Δpp','','','',''))

    # load per-session data for table
    per_sess = []
    for (path, invert), slbl in zip(SESSIONS, SESSION_LABELS):
        sr = {(c,s):[0,0] for c in ('CUED','UNCUED') for s in ('N','C','Z','CZ')}
        with open(path, newline='') as f:
            rws = list(csv.DictReader(f, delimiter='\t'))
        for r in rws:
            if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip():
                continue
            if r.get('EndKey','') in ('timeout','skip','requeue'):
                continue
            cond = r['Cond']
            if invert:
                cond = 'UNCUED' if cond=='CUED' else 'CUED'
            swap = r['SwapType']
            if (cond,swap) not in sr:
                continue
            sr[(cond,swap)][0] += int(is_correct(r['TransDeg'],r['RespDeg']))
            sr[(cond,swap)][1] += 1
        kc_s = sum(sr[('CUED',s)][0] for s in ('N','C','Z','CZ'))
        nc_s = sum(sr[('CUED',s)][1] for s in ('N','C','Z','CZ'))
        ku_s = sum(sr[('UNCUED',s)][0] for s in ('N','C','Z','CZ'))
        nu_s = sum(sr[('UNCUED',s)][1] for s in ('N','C','Z','CZ'))
        eff_s = pct(kc_s,nc_s) - pct(ku_s,nu_s)
        pv_s  = chi2_p(kc_s,nc_s,ku_s,nu_s)
        per_sess.append((slbl, eff_s, pv_s))

    for slbl, eff_s, pv_s in per_sess:
        rows.append((slbl, '', '', f'{eff_s:+.1f}', stars(pv_s)))

    y0 = 0.97; lh = 0.076
    for xi, (h, cx) in enumerate(zip(headers, col_xs)):
        ax_r.text(cx, y0, h, transform=ax_r.transAxes,
                  fontsize=8.5, fontweight='bold', va='top', color='#111')
    ax_r.plot([0,1],[y0-lh*0.55]*2, color='#aaa', lw=0.8,
              transform=ax_r.transAxes, clip_on=False)

    for ri, row in enumerate(rows):
        y = y0 - lh*(ri+1) - 0.01
        if all(c=='' for c in row):
            ax_r.plot([0,1],[y+lh*0.35]*2, color='#ddd', lw=0.5,
                      transform=ax_r.transAxes, clip_on=False)
            continue
        is_sess = any(s in row[0] for s in ('260406','260407'))
        for xi, (cell, cx) in enumerate(zip(row, col_xs)):
            fw = 'bold' if xi==0 and not is_sess else 'normal'
            col = '#888' if is_sess and xi==0 else '#222'
            ax_r.text(cx, y, cell, transform=ax_r.transAxes,
                      fontsize=7.5 if is_sess else 8, va='center',
                      color=col, fontweight=fw)

    commentary_box(fig, [
        '** Design: DecoupledDots uses linkDepthColor=0 — depth and color change independently at tStart.',
        '   Four swap conditions (N/C/Z/CZ) × two temporal conditions (CUED/UNCUED) produce a fully orthogonal 2³ factorial over',
        '   three binary factors: (F1) dot cueing (temporal onset), (F2) depth-field cueing, (F3) color-field cueing.',
        '   Each factor is balanced across the other two, so effect estimates are unconfounded.',
        '',
        '** Results at a glance:',
        '   • Dot cueing (+15.4pp ***): the temporal onset cue is the dominant factor. Strongly replicates the Stoner & Blanc (2010)',
        '     object-based attention effect in VR stereoscopic dots.',
        '   • Depth-field cueing (+8.1pp ***): knowing that translation will occur at the same depth where the delayed field first',
        '     appeared provides a significant additional boost. Depth plane identity acts as an attentional anchor across the delay.',
        '   • Color-field cueing (+0.9pp n.s.): field-level color identity carries zero predictive information. This rules out the',
        '     apparent "color effect" seen in the earlier DepthColorLinked experiment — that was entirely a depth confound.',
        '   • S4 (260407_0731) anomalous: dot cueing flat (+4.8pp n.s.), elevated UNCUED throughout. Included without exclusion',
        '     (no pre-defined criterion). The 4-session combined result remains highly significant despite this session.',
    ])

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    print("  Page 1 done")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Factor performance: raw % correct (cued vs uncued)
# ══════════════════════════════════════════════════════════════════════════════
def page2(pdf):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')
    page_header(fig,
        'DecoupledDots — Factor Performance: Raw % Correct',
        'Each panel: the "cued" vs "uncued" arm of one factor  ·  absolute % correct  ·  n≈2051')

    gs = gridspec.GridSpec(1, 3, left=0.07, right=0.97, bottom=0.28,
                           top=0.918, wspace=0.38)

    panel_specs = [
        ('A.  Dot cueing\n(temporal onset)',
         dot_cu, C_CUED, 'Dot-cued ✓\n(CUED)',
         dot_un, C_DOT_UN, 'Dot-uncued ✗\n(UNCUED)'),
        ('B.  Depth-field cueing\n(translator depth plane)',
         dep_cu, C_DEP_CU, 'Depth-cued ✓\n{CUED+N/C, UNCUED+Z/CZ}',
         dep_un, C_DEP_UN, 'Depth-uncued ✗\n{CUED+Z/CZ, UNCUED+N/C}'),
        ('C.  Color-field cueing\n(translator color)',
         col_cu, C_COL_CU, 'Color-cued ✓\n{CUED+N/Z, UNCUED+C/CZ}',
         col_un, C_COL_UN, 'Color-uncued ✗\n{CUED+C/CZ, UNCUED+N/Z}'),
    ]

    for ai, (title, (kc,nc), colc, lc, (ku,nu), colu, lu) in enumerate(panel_specs):
        ax = fig.add_subplot(gs[ai])
        p1 = draw_bar(ax, 0, kc, nc, colc)
        p2 = draw_bar(ax, 1, ku, nu, colu)
        pval = chi2_p(kc,nc,ku,nu)
        eff  = p1 - p2
        y_br = max(p1, p2) + 8
        bracket(ax, 0, 1, y_br,
                f'Δ = {eff:+.1f}pp  {stars(pval)}',
                color='#333')
        ax.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
        ax.text(1.08, CHANCE*100, 'chance\n12.5%', transform=ax.get_yaxis_transform(),
                fontsize=7, color='#999', va='center')
        ax.set_xticks([0,1])
        ax.set_xticklabels([lc, lu], fontsize=8.5)
        style_ax(ax, title=title, ylim=(0,72))

    commentary_box(fig, [
        '** What each panel shows: the "cued" arm = all trials where this factor is working in your favor.',
        '   The "uncued" arm = all trials where it works against you. Because the design is fully orthogonal,',
        '   these arms each contain equal numbers of the other factors in both states — so each Δ is a clean',
        '   main effect of that factor alone.',
        '',
        '** Dot cueing (A):  Dot-cued ✓ = 36.7%  vs  Dot-uncued ✗ = 21.3%  →  Δ = +15.4pp ***',
        '   The largest effect by far. This is the core object-based attention result: the field that starts',
        '   moving later (delayed onset) is better detected as the translator, because attention is drawn to',
        '   the onset-defined object and then remains bound to it through the translation window.',
        '',
        '** Depth-field cueing (B):  Depth-cued ✓ = 33.1%  vs  Depth-uncued ✗ = 25.0%  →  Δ = +8.1pp ***',
        '   The depth plane where the delayed field first appeared serves as an additional attentional anchor.',
        '   When the translating field ends up in that plane, performance is boosted — even after collapsing',
        '   over both CUED and UNCUED trials. Note: the depth-cued ✓ arm is bimodal (very high for CUED+N/C,',
        '   very low for UNCUED+Z/CZ), so the 33.1% average understates the benefit for CUED and the cost for UNCUED.',
        '',
        '** Color-field cueing (C):  Color-cued ✓ = 29.5%  vs  Color-uncued ✗ = 28.6%  →  Δ = +0.9pp n.s.',
        '   Exactly null. Field-level color identity (red vs green) carries no information for performance.',
        '   The earlier apparent "color effect" in DepthColorLinked was entirely a depth confound.',
    ])

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    print("  Page 2 done")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Full 8-condition breakdown
# ══════════════════════════════════════════════════════════════════════════════
def page3(pdf):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')
    page_header(fig,
        'DecoupledDots — All 8 Conditions: % Correct by Cond × SwapType',
        'N = no swap  ·  C = color swap only  ·  Z = depth swap only  ·  CZ = color + depth swap')

    gs = gridspec.GridSpec(1, 2, left=0.07, right=0.97, bottom=0.28,
                           top=0.918, wspace=0.10)

    SWAP_ORDER = ['N','C','Z','CZ']
    swap_labels_full = {
        'N':  'N\n(no swap)',
        'C':  'C\n(color only)',
        'Z':  'Z\n(depth only)',
        'CZ': 'CZ\n(col+dep)',
    }

    for gi, (cond, ax_idx) in enumerate([('CUED',0), ('UNCUED',1)]):
        ax = fig.add_subplot(gs[ax_idx])
        col_main = C_CUED if cond=='CUED' else C_UNCUED

        kn, nn = raw[(cond,'N')]
        ref_pct = pct(kn, nn)

        bar_ps = []
        for si, swap in enumerate(SWAP_ORDER):
            k, n = raw[(cond, swap)]
            col = SWAP_COLS[swap]
            hatch = '//' if swap in ('C','CZ') else None
            p = draw_bar(ax, si, k, n, col, width=0.60, alpha=0.88, hatch=hatch)
            bar_ps.append(p)

            # Cost vs N annotation (skip N itself)
            if swap != 'N':
                cost = p - ref_pct
                pv = chi2_p(k,n,kn,nn)
                col_ann = C_Z if swap in ('Z','CZ') else C_C
                ax.text(si, max(p, ref_pct) + 6,
                        f'{cost:+.0f}pp\nvs N\n{stars(pv)}',
                        ha='center', va='bottom', fontsize=7.5,
                        color=col_ann, fontweight='bold')

        # Dashed reference line at N baseline
        ax.axhline(ref_pct, color='#555555', lw=1.0, ls=':', zorder=2, alpha=0.7)
        ax.text(-0.4, ref_pct + 0.8, f'N={ref_pct:.1f}%', fontsize=8, color='#555')

        ax.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
        ax.set_xticks(range(4))
        ax.set_xticklabels([swap_labels_full[s] for s in SWAP_ORDER], fontsize=9)
        ax.set_ylabel('% correct' if gi==0 else '', fontsize=9.5)
        if gi == 1:
            ax.set_yticklabels([])
        style_ax(ax,
                 title=f'{"A" if gi==0 else "B"}.  {cond}\n(temporal onset '
                       f'{"marks" if cond=="CUED" else "does NOT mark"} the translator)',
                 ylim=(0,72))

        # Cond label banner
        col_banner = '#D0E4FF' if cond=='CUED' else '#FFE8D0'
        ax.set_facecolor(col_banner)
        ax.patch.set_alpha(0.25)

        # Shaded region for depth-swap conditions
        ax.axvspan(1.55, 3.45, alpha=0.06, color=C_Z, zorder=0)
        ax.text(2.5, 68.5, '← depth swaps →', ha='center', fontsize=8,
                color=C_Z, style='italic')

    # Shared legend
    patches = [
        mpatches.Patch(color=C_N,  label='N — no swap (baseline)'),
        mpatches.Patch(color=C_C,  label='C — color swap only', hatch='//'),
        mpatches.Patch(color=C_Z,  label='Z — depth swap only'),
        mpatches.Patch(color=C_CZ, label='CZ — color + depth swap', hatch='//'),
    ]
    fig.legend(handles=patches, fontsize=8.5, ncol=4,
               loc='upper center', bbox_to_anchor=(0.5, 0.926),
               framealpha=0.9, handlelength=2.0)

    commentary_box(fig, [
        '** CUED group (A) — dot cue marks the translator:',
        '   N (+35.9%) and C (+37.5%): high performance — the translator is the cued field AND in the right depth plane.',
        '   C ≈ N: swapping color alone does not disrupt performance at all (Δ = +1.6pp n.s. vs N).',
        '   Z (+10.9%) and CZ (+12.5%): performance drops ~25pp relative to N — the depth swap is massively disruptive,',
        '   even though the temporal onset cue still correctly marks the translator. The translator is now in the wrong',
        '   depth plane, competing with the wrong-field dots that moved into the original (cued) depth plane.',
        '   CZ ≈ Z: adding color to the depth swap makes no additional difference (Δ ≈ 2pp n.s.).',
        '',
        '** UNCUED group (B) — dot cue marks the wrong field:',
        '   N (+12.4%) and C (+14.0%): modestly above chance — no temporal onset benefit, but no disruption either.',
        '   Z (+1.9%) and CZ (+7.0%): performance drops 5–10pp vs N. The depth swap here moves the wrong-field',
        '   translator into the "correct" depth plane, but this provides no net benefit — the disruption cost',
        '   of the swap outweighs any depth-identity advantage. UNCUED+Z falls closest to chance (14.4%).',
        '   Key asymmetry: the depth swap costs ~25pp in CUED but only ~5–10pp in UNCUED, because it directly',
        '   disrupts the cued translator signal in CUED but only affects the non-cued translator in UNCUED.',
    ])

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    print("  Page 3 done")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Dot × Depth head-to-head
# ══════════════════════════════════════════════════════════════════════════════
def page4(pdf):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')
    page_header(fig,
        'DecoupledDots — Dot Cueing vs Depth-field Cueing: Head-to-Head',
        'When the two factors conflict, which wins?')

    gs = gridspec.GridSpec(1, 2, left=0.06, right=0.97, bottom=0.28,
                           top=0.918, wspace=0.40, width_ratios=[1, 1.3])

    # ── Panel A: 2×2 ─────────────────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0])

    cell_order  = ['both','dot_no_dep','dep_no_dot','neither']
    cell_colors = {'both':'#2c4f8c','dot_no_dep':C_CUED,'dep_no_dot':C_DEP_CU,'neither':'#999'}
    cell_labels = {
        'both':       'Dot ✓  Depth ✓\n(CUED+N/C)',
        'dot_no_dep': 'Dot ✓  Depth ✗\n(CUED+Z/CZ)',
        'dep_no_dot': 'Dot ✗  Depth ✓\n(UNCUED+Z/CZ)',
        'neither':    'Dot ✗  Depth ✗\n(UNCUED+N/C)',
    }

    bv = []
    for xi, cell in enumerate(cell_order):
        k, n = cell_2x2[cell]
        bv.append(draw_bar(ax_a, xi, k, n, cell_colors[cell], width=0.60))

    # Conflict bracket
    k1,n1 = cell_2x2['dot_no_dep']; k2,n2 = cell_2x2['dep_no_dot']
    bracket(ax_a, 1, 2, max(bv[1],bv[2])+9,
            f'Δ = {pct(k1,n1)-pct(k2,n2):+.1f}pp  {stars(chi2_p(k1,n1,k2,n2))}  ← conflict',
            color='#CC3300', fs=9.5)

    # Aligned bracket
    k1,n1 = cell_2x2['both']; k2,n2 = cell_2x2['neither']
    bracket(ax_a, 0, 3, max(bv[0],bv[3])+9,
            f'Δ = {pct(k1,n1)-pct(k2,n2):+.1f}pp  {stars(chi2_p(k1,n1,k2,n2))}  ← aligned',
            color='#1a6e8b', fs=9.5)

    ax_a.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
    ax_a.text(3.42, CHANCE*100+0.3, 'chance', fontsize=8, color='#999')
    ax_a.set_xticks(range(4))
    ax_a.set_xticklabels([cell_labels[c] for c in cell_order], fontsize=8.5)
    style_ax(ax_a, title='A.  2×2: Dot × Depth-field cueing\n(collapsing over color swap)', ylim=(0,74))

    # ── Panel B: 8-condition disruptiveness ───────────────────────────────────
    ax_b = fig.add_subplot(gs[1])

    SWAP_ORDER = ['N','C','Z','CZ']
    bar_w = 0.38; gap = 0.05; grp_gap = 0.65
    all_xs = []; all_lbls = []

    for gi, cond in enumerate(['CUED','UNCUED']):
        x_base = gi * (4*(bar_w+gap) + grp_gap)
        kn,nn  = raw[(cond,'N')]
        ref    = pct(kn,nn)

        for si, swap in enumerate(SWAP_ORDER):
            x = x_base + si*(bar_w+gap)
            k, n = raw[(cond,swap)]
            p = draw_bar(ax_b, x, k, n, SWAP_COLS[swap], width=bar_w,
                         hatch=('//' if swap in ('C','CZ') else None))
            all_xs.append(x); all_lbls.append(swap)

            if swap != 'N':
                cost = p - ref
                pv   = chi2_p(k,n,kn,nn)
                ax_b.text(x, max(p,ref)+5,
                           f'{cost:+.0f}pp\n{stars(pv)}',
                           ha='center', va='bottom', fontsize=7,
                           color=C_Z if swap in ('Z','CZ') else '#888',
                           fontweight='bold' if swap in('Z','CZ') else 'normal')

        # N reference dashed line
        x_start = x_base - bar_w*0.5
        x_end   = x_base + 3*(bar_w+gap) + bar_w*0.5
        ax_b.plot([x_start,x_end],[ref,ref], color='#555', lw=0.9, ls=':', alpha=0.7)
        ax_b.text(x_start-0.05, ref+0.5, f'N', fontsize=8, color='#555', ha='right')

        # depth-swap shaded region
        xz  = x_base + 2*(bar_w+gap)
        xcz = x_base + 3*(bar_w+gap)
        ax_b.axvspan(xz-bar_w*0.55, xcz+bar_w*0.55, alpha=0.07, color=C_Z, zorder=0)

        # Cond label
        xmid = x_base + 1.5*(bar_w+gap)
        ax_b.text(xmid, -5, cond, ha='center', va='top', fontsize=10, fontweight='bold',
                  color=C_CUED if cond=='CUED' else C_UNCUED)

    ax_b.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
    ax_b.set_xticks(all_xs)
    ax_b.set_xticklabels(all_lbls, fontsize=8.5)
    ax_b.set_ylim(0, 74)
    ax_b.set_xlim(all_xs[0]-bar_w, all_xs[-1]+bar_w*2)
    style_ax(ax_b, title='B.  Depth-swap cost: all 8 conditions\n(Δ vs N baseline labeled above depth-swap bars)',
             ylim=(0,74))
    legend_patches = [
        mpatches.Patch(color=C_N,  label='N  no swap'),
        mpatches.Patch(color=C_C,  label='C  color only', hatch='//'),
        mpatches.Patch(color=C_Z,  label='Z  depth only'),
        mpatches.Patch(color=C_CZ, label='CZ color+depth', hatch='//'),
    ]
    ax_b.legend(handles=legend_patches, fontsize=8, loc='upper right',
                framealpha=0.9, handlelength=1.8)

    commentary_box(fig, [
        '** Panel A — 2×2 (collapsing over color swap, which has no effect):',
        '   Both ✓  (CUED+N/C):    49.2%  — temporal onset AND depth plane both working for you: highest performance.',
        '   Dot✓ Depth✗ (CUED+Z/CZ): 24.2%  — temporal onset helps, depth plane works against: strong drop but still above chance.',
        '   Dot✗ Depth✓ (UNCUED+Z/CZ): 17.0% — depth plane is "correct," but no temporal onset cue: performance below the',
        '                                        "neither" cell. The depth swap disruption cost outweighs the depth identity benefit.',
        '   Neither (UNCUED+N/C):  25.7%  — neither cue working: near chance, but slightly above (residual signal?).',
        '',
        '** The direct conflict: Dot✓/Depth✗ (24.2%) vs Dot✗/Depth✓ (17.0%) → Δ = +7.3pp **.',
        '   Dot cueing wins when the two factors are pitted against each other.',
        '',
        '** Panel B — Depth-swap cost breakdown:',
        '   CUED+Z vs N: −25.0pp ***  |  CUED+CZ vs N: −23.4pp ***   → depth swap massively disrupts the cued translator.',
        '   UNCUED+Z vs N: −10.5pp ** |  UNCUED+CZ vs N: −5.4pp n.s. → smaller cost when wrong field is swapped.',
        '   CZ ≈ Z throughout: adding color to the depth swap makes no additional difference. Color is inert.',
        '   Crucially, UNCUED+Z/CZ (the "Depth✓" conditions) fall BELOW the UNCUED+N/C (Neither) baseline,',
        '   confirming that depth identity alone cannot rescue performance when the temporal onset cue is absent.',
    ])

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    print("  Page 4 done")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Pairwise cued-arm comparisons
# ══════════════════════════════════════════════════════════════════════════════
def page5(pdf):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')
    page_header(fig,
        'DecoupledDots — Pairwise Comparison of Factor "Cued" Arms',
        'Each panel: absolute % correct when each factor is working in your favor')

    gs = gridspec.GridSpec(1, 3, left=0.07, right=0.97, bottom=0.28,
                           top=0.918, wspace=0.38)

    arms = {
        'dot':   (dot_cu,  C_CUED,   'Dot-cued ✓\n(CUED)'),
        'depth': (dep_cu,  C_DEP_CU, 'Depth-cued ✓\n(correct plane)'),
        'color': (col_cu,  C_COL_CU, 'Color-cued ✓\n(matching color)'),
    }

    panels = [
        ('D.  Dot-cued  vs  Depth-cued\n(favored arm of each factor)', 'dot',   'depth'),
        ('E.  Dot-cued  vs  Color-cued',                                'dot',   'color'),
        ('F.  Depth-cued  vs  Color-cued',                              'depth', 'color'),
    ]

    for ai, (title, a1, a2) in enumerate(panels):
        ax = fig.add_subplot(gs[ai])
        (k1,n1), col1, lbl1 = arms[a1]
        (k2,n2), col2, lbl2 = arms[a2]
        p1 = draw_bar(ax, 0, k1, n1, col1)
        p2 = draw_bar(ax, 1, k2, n2, col2)
        pval = chi2_p(k1,n1,k2,n2)
        bracket(ax, 0, 1, max(p1,p2)+8,
                f'Δ = {p1-p2:+.1f}pp  {stars(pval)}', color='#333')
        ax.axhline(CHANCE*100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
        ax.set_xticks([0,1])
        ax.set_xticklabels([lbl1, lbl2], fontsize=9)
        style_ax(ax, title=title, ylim=(0,72))

    commentary_box(fig, [
        '** These panels compare absolute performance in the "favored arm" of each factor —',
        '   i.e., when a given factor is working for you, how well do you do?',
        '',
        '** D: Dot-cued (36.7%) vs Depth-cued (33.1%) — small difference, and this comparison is somewhat',
        '   confounded: the depth-cued ✓ arm mixes very high CUED+N/C trials (~49%) with very low UNCUED+Z/CZ',
        '   trials (~17%), averaging to 33.1%. Meanwhile dot-cued spans 23–50% (all CUED trials).',
        '   The ~3.6pp gap is not significant here, but the EFFECT SIZES clearly differ: dot Δ = +15.4pp vs',
        '   depth Δ = +8.1pp (see pages 1–2). Panel D alone does not cleanly isolate the factor strength.',
        '   The 2×2 on page 4 is the cleaner head-to-head.',
        '',
        '** E: Dot-cued (36.7%) vs Color-cued (29.5%) — ~7pp gap, likely significant.',
        '   Color-cued ✓ ≈ Color-uncued ✗ ≈ 29% (see page 2, panel C): the color arm carries no signal.',
        '   The dot-cued arm outperforms the color-cued arm simply because the dot cue is informative',
        '   and color is not.',
        '',
        '** F: Depth-cued (33.1%) vs Color-cued (29.5%) — ~3.6pp gap.',
        '   Depth outperforms color as a cueing dimension. Together with the null color result (page 2C),',
        '   this confirms that depth plane identity — not color identity — is the feature that anchors',
        '   the attentional object across the onset-to-translation delay.',
    ])

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    print("  Page 5 done")

# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
os.makedirs(FIG_DIR, exist_ok=True)
print(f"\nBuilding report PDF → {OUT_PDF}")
with PdfPages(OUT_PDF) as pdf:
    page1(pdf)
    page2(pdf)
    page3(pdf)
    page4(pdf)
    page5(pdf)
    pdf.infodict()['Title']   = 'DecoupledDots — Comprehensive Results Report'
    pdf.infodict()['Author']  = 'VRDots analysis pipeline'
    pdf.infodict()['Subject'] = ('Three cueing factors: dot (temporal onset), '
                                 'depth-field, color-field')

print(f"\nDone. Saved: {OUT_PDF}")
