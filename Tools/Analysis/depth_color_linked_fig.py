#!/usr/bin/env python3
"""
depth_color_linked_fig.py — Analysis & figure for DepthColorLinked_005m

Session: 260404_0940  (n=256, both ZdA=ZdCoh + ZdB=ZdNoi, R/G balanced)

Main 2×2 design:
  F1 Dot Cueing  : CUED vs UNCUED  (does delayed dot field translate?)
  F2 Depth Cueing: YES vs NO       (does translation occur at the depth
                                    where cued field appeared?)
    Depth YES = CUED+ZdNoi  OR  UNCUED+ZdCoh
    Depth NO  = CUED+ZdCoh  OR  UNCUED+ZdNoi

Secondary factors (post-hoc, 32 trials/cell before pooling):
  TransDepth : Near vs Far  (depth of translating field during translation)
  TransColor : R vs G       (color of translating field during translation)

Output: Agents/Figures/depth_color_linked_results.png
"""

import csv, collections, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser(
    "~/Library/Application Support/ThatsRandom/VRDotsDataFiles")
OUT_PATH = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/depth_color_linked_results.png")

SESSIONS = ['260404_0940', '260404_1123', '260406_1001']

# ── Stats helpers ─────────────────────────────────────────────────────────────
def normal_cdf(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def z_test(k1, n1, k2, n2):
    p1, p2 = k1/n1, k2/n2
    pp = (k1+k2)/(n1+n2)
    se = math.sqrt(max(pp*(1-pp)*(1/n1+1/n2), 1e-12))
    z = (p1-p2)/se
    return z, 1 - normal_cdf(z)

def z_vs_chance(k, n, chance=1/8):
    p = k/n
    se = math.sqrt(max(chance*(1-chance)/n, 1e-12))
    return (p-chance)/se

def wilson_ci(k, n, z=1.96):
    p = k/n; d = 1 + z**2/n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c-hw, c+hw

def stars(p):
    return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else '†' if p < .1 else 'n.s.'

def sig_vs_chance(k, n, chance=1/8):
    zv = z_vs_chance(k, n, chance)
    p = 1 - normal_cdf(zv)
    return stars(p), p

# ── Factor derivation ─────────────────────────────────────────────────────────
def depth_cue_yes(cond, swap):
    """Depth Cueing = YES when translation occurs at the depth the cued
    field occupied (i.e., translator is at DFD during translation window).

    Derivation:
      CUED+ZdNoi: S0 (translator=cued) stays at DFD → YES
      CUED+ZdCoh: S0 swaps from DFD to opp(DFD) at T_S → translator at opp(DFD) → NO
      UNCUED+ZdCoh: S0 swaps from opp(DFD) to DFD at T_S → translator at DFD → YES
      UNCUED+ZdNoi: S0 stays at opp(DFD) → NO
    """
    return (cond == 'CUED') != (swap == 'ZdA')   # XNOR(cond==CUED, swap==ZdB)

def trans_depth_label(cond, swap, dfd):
    """Depth of translating field DURING the translation window."""
    if depth_cue_yes(cond, swap):
        return dfd                        # translator at DFD
    else:
        return 'F' if dfd == 'N' else 'N' # translator at opp(DFD)

def trans_color_label(trans_dep, dfd, dfc):
    """Color of translating field during translation window.
    Near plane = same color as near field.
    DFD color and opp color:
      if trans_dep == dfd → trans color = dfc
      else → opp(dfc)
    """
    if trans_dep == dfd:
        return dfc
    return 'G' if dfc == 'R' else 'R'

# ── Data loading ──────────────────────────────────────────────────────────────
def load(sid):
    path = os.path.join(DATA_DIR, f"vr_dots_session_{sid}.tsv")
    with open(path, newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def is_correct(td, rd):
    d = (float(rd)-float(td)+360) % 360
    return (360-d if d > 180 else d) <= 22.5

def load_all():
    rows = []
    for sid in SESSIONS:
        try:
            rows.extend(load(sid))
        except FileNotFoundError:
            print(f"WARNING: {sid} not found")
    return rows

# ── Aggregate ─────────────────────────────────────────────────────────────────
CHANCE = 1/8

def analyze():
    rows = load_all()
    valid = [r for r in rows
             if r.get('TransDeg') and r.get('RespDeg')
             and r.get('EndKey','') not in ('timeout','skip','requeue')]

    # Main 2×2: Dot Cueing × Depth Cueing
    main22 = collections.defaultdict(lambda: [0,0])
    # By swap×cond (raw cells, same data different labeling)
    by_swap_cond = collections.defaultdict(lambda: [0,0])
    # Secondary: TransDepth
    by_trans_depth = collections.defaultdict(lambda: [0,0])
    # Secondary: TransColor
    by_trans_color = collections.defaultdict(lambda: [0,0])
    # 2×2 × TransDepth
    main_by_tdep = collections.defaultdict(lambda: [0,0])

    for r in valid:
        cond  = r['Cond']
        swap  = r['SwapType']
        dfd   = r['DelayedFieldDepth']
        dfc   = r['DelayedFieldColor']
        td    = r['TransDeg']
        rd    = r['RespDeg']
        corr  = int(is_correct(td, rd))

        dep_cue = 'YES' if depth_cue_yes(cond, swap) else 'NO'
        tdep    = trans_depth_label(cond, swap, dfd)
        tcolor  = trans_color_label(tdep, dfd, dfc)

        main22[(cond, dep_cue)][0] += corr
        main22[(cond, dep_cue)][1] += 1

        by_swap_cond[(swap, cond)][0] += corr
        by_swap_cond[(swap, cond)][1] += 1

        by_trans_depth[(cond, dep_cue, tdep)][0] += corr
        by_trans_depth[(cond, dep_cue, tdep)][1] += 1

        by_trans_color[(cond, dep_cue, tcolor)][0] += corr
        by_trans_color[(cond, dep_cue, tcolor)][1] += 1

        main_by_tdep[(cond, dep_cue, tdep)][0] += corr
        main_by_tdep[(cond, dep_cue, tdep)][1] += 1

    return {
        'n_valid': len(valid),
        'main22': dict(main22),
        'by_swap_cond': dict(by_swap_cond),
        'by_trans_depth': dict(by_trans_depth),
        'by_trans_color': dict(by_trans_color),
    }

# ── Plotting helpers ───────────────────────────────────────────────────────────
C_CUED   = '#1a6b1a'   # dark green — Dot Cueing factor
C_UNCUED = '#888888'
C_DEP_Y  = '#1a3a8b'   # dark blue — Depth Cueing YES
C_DEP_N  = '#aa2222'   # dark red — Depth Cueing NO
C_NEAR   = '#CC3333'   # near = red dots
C_FAR    = '#228B22'   # far = green dots

def acc_pp(k, n): return (k/n - CHANCE) * 100
def ci_pp(k, n):
    lo, hi = wilson_ci(k, n)
    return (lo - CHANCE)*100, (hi - CHANCE)*100

def draw_bar(ax, x, k, n, color, width=0.35, alpha=1.0, label=None):
    pp = acc_pp(k, n)
    lo, hi = ci_pp(k, n)
    bar = ax.bar(x, pp, width, color=color, alpha=alpha, zorder=3,
                 label=label, edgecolor='white', linewidth=0.5)
    ax.errorbar(x, pp, yerr=[[pp-lo],[hi-pp]], fmt='none',
                color='#333', capsize=3, capthick=1, lw=1, zorder=4)
    return pp

def sig_label(ax, x, y_top, k, n, ref_k=None, ref_n=None):
    """Draw significance label. If ref_k/ref_n: z-test vs ref. Else vs chance."""
    if ref_k is not None:
        _, p = z_test(k, n, ref_k, ref_n)
        s = stars(p)
    else:
        s, p = sig_vs_chance(k, n)
    ax.text(x, y_top + 1, s, ha='center', va='bottom', fontsize=7, color='#333')

def style_ax(ax, title='', ylim=(-15, 60), ylabel=True):
    ax.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=9, fontweight='bold', pad=4)
    if ylabel:
        ax.set_ylabel('% correct above chance', fontsize=7.5)
    ax.tick_params(labelsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(axis='y', which='minor', lw=0.3, alpha=0.4, zorder=0)
    ax.grid(axis='y', which='major', lw=0.5, alpha=0.5, zorder=0)

import matplotlib.ticker

# ── Main figure ───────────────────────────────────────────────────────────────
def make_figure(data):
    n_valid = data['n_valid']
    m22     = data['main22']
    bsc     = data['by_swap_cond']
    btd     = data['by_trans_depth']

    fig = plt.figure(figsize=(13, 10))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.975,
        f'DepthColorLinked_005m — Sessions 260404_0940 + 1123 + 260406_1001   (n={n_valid} trials)',
        ha='center', va='top', fontsize=12, fontweight='bold', color='#111')
    fig.text(0.5, 0.950,
        'Near plane = Red   •   Far plane = Green   •   depth = 0.05 m   •   8-AFC',
        ha='center', va='top', fontsize=8.5, color='#555')

    gs = gridspec.GridSpec(2, 3, top=0.915, bottom=0.09,
                           left=0.07, right=0.97,
                           hspace=0.48, wspace=0.38)

    # ── Panel A: Main 2×2 ─────────────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0:2])

    # 4 grouped bars: [CUED+YES, CUED+NO] | [UNCUED+YES, UNCUED+NO]
    positions = [0.0, 0.45, 1.1, 1.55]
    labels_x  = ['Depth✓\n(ZdNoi)', 'Depth✗\n(ZdCoh)', 'Depth✓\n(ZdCoh)', 'Depth✗\n(ZdNoi)']
    keys      = [('CUED','YES'), ('CUED','NO'), ('UNCUED','YES'), ('UNCUED','NO')]
    colors    = [C_DEP_Y, C_DEP_N, C_DEP_Y, C_DEP_N]
    alphas    = [1.0, 1.0, 0.65, 0.65]

    ymax = -100
    for xi, (pos, key, col, alp) in enumerate(zip(positions, keys, colors, alphas)):
        k, n = m22.get(key, [0, 1])
        pp = draw_bar(ax_a, pos, k, n, col, width=0.38, alpha=alp)
        lo, hi = ci_pp(k, n)
        sig_label(ax_a, pos, max(pp, hi) if n > 0 else 5, k, n)
        ymax = max(ymax, hi)

    # Group brackets
    ax_a.annotate('', xy=(0.45+0.19, -13), xytext=(-0.19, -13),
                  arrowprops=dict(arrowstyle='-', color=C_CUED, lw=1.8))
    ax_a.annotate('', xy=(1.55+0.19, -13), xytext=(1.1-0.19, -13),
                  arrowprops=dict(arrowstyle='-', color=C_UNCUED, lw=1.8))
    ax_a.text(0.225, -15.5, 'DOT CUED', ha='center', fontsize=8,
              color=C_CUED, fontweight='bold')
    ax_a.text(1.325, -15.5, 'DOT UNCUED', ha='center', fontsize=8,
              color=C_UNCUED, fontweight='bold')

    ax_a.set_xticks(positions)
    ax_a.set_xticklabels(labels_x, fontsize=7.5)
    style_ax(ax_a, title='A.  Main 2×2: Dot Cueing × Depth Cueing', ylim=(-18, 65))

    # Cueing effect annotations (Depth YES vs NO within each Dot condition)
    for x1, x2, cond_label, y_ann in [(0.0, 0.45, 'CUED', 55), (1.1, 1.55, 'UNCUED', 55)]:
        k1,n1 = m22.get((cond_label,'YES'), [0,1])
        k2,n2 = m22.get((cond_label,'NO'),  [0,1])
        if n1>0 and n2>0:
            _, p = z_test(k1, n1, k2, n2)
            pp1, pp2 = acc_pp(k1,n1), acc_pp(k2,n2)
            diff = pp1 - pp2
            ax_a.annotate('', xy=(x2, y_ann-4), xytext=(x1, y_ann-4),
                          arrowprops=dict(arrowstyle='<->', color='#444', lw=0.8))
            ax_a.text((x1+x2)/2, y_ann, f'Δ{diff:+.1f}pp  {stars(p)}',
                      ha='center', fontsize=7, color='#444')

    # ── Panel B: By SwapType×Cond (raw labeling) ─────────────────────────────
    ax_b = fig.add_subplot(gs[0, 2])
    swap_pos = {'ZdA': {'CUED': 0.0, 'UNCUED': 0.5},
                'ZdB': {'CUED': 1.1, 'UNCUED': 1.6}}
    swap_colors = {'ZdA': '#883300', 'ZdB': '#226622'}
    swap_labels  = {'ZdA': 'ZdCoh', 'ZdB': 'ZdNoi'}
    cond_alphas  = {'CUED': 1.0, 'UNCUED': 0.6}

    handles_b = []
    for swap in ['ZdA', 'ZdB']:
        for cond in ['CUED', 'UNCUED']:
            k, n = bsc.get((swap, cond), [0,1])
            pos = swap_pos[swap][cond]
            col = swap_colors[swap]
            pp  = draw_bar(ax_b, pos, k, n, col, width=0.42,
                           alpha=cond_alphas[cond])
            lo, hi = ci_pp(k, n)
            sig_label(ax_b, pos, max(pp, hi), k, n)
        xm = (swap_pos[swap]['CUED'] + swap_pos[swap]['UNCUED']) / 2
        ax_b.text(xm, -15.5, swap_labels[swap], ha='center', fontsize=8,
                  fontweight='bold', color=swap_colors[swap])

    # Tick labels
    all_pos = [swap_pos[s][c] for s in ['ZdA','ZdB'] for c in ['CUED','UNCUED']]
    ax_b.set_xticks(all_pos)
    ax_b.set_xticklabels(['C','U','C','U'], fontsize=7.5)
    style_ax(ax_b, title='B.  By SwapType × Cond', ylim=(-18, 65), ylabel=False)

    # ── Panel C: By TransDepth, within 2×2 ────────────────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])
    c_cells = [
        ('CUED','YES','N'), ('CUED','YES','F'),
        ('CUED','NO','N'),  ('CUED','NO','F'),
    ]
    u_cells = [
        ('UNCUED','YES','N'), ('UNCUED','YES','F'),
        ('UNCUED','NO','N'),  ('UNCUED','NO','F'),
    ]
    dep_colors = {'N': C_NEAR, 'F': C_FAR}
    dep_labels = {'N': 'Near', 'F': 'Far'}

    for ci, (cells, x_offset, dot_label, dot_col, dot_alp) in enumerate([
        (c_cells, 0.0, 'CUED',   C_CUED, 1.0),
        (u_cells, 2.2, 'UNCUED', C_UNCUED, 0.65),
    ]):
        for bi, (cond, dep_cue, tdep) in enumerate(cells):
            k, n = btd.get((cond, dep_cue, tdep), [0, 1])
            x = x_offset + bi * 0.5
            # Hatch for Depth✗
            hatch = '//' if dep_cue == 'NO' else None
            col   = dep_colors[tdep]
            pp    = acc_pp(k, n) if n > 0 else 0
            lo, hi = ci_pp(k, n) if n > 0 else (0, 0)
            ax_c.bar(x, pp, 0.42, color=col, alpha=dot_alp, hatch=hatch,
                     zorder=3, edgecolor='white', linewidth=0.5)
            if n > 0:
                ax_c.errorbar(x, pp, yerr=[[pp-lo],[hi-pp]], fmt='none',
                              color='#333', capsize=3, capthick=1, lw=1, zorder=4)

        # Group label
        xm = x_offset + 0.75
        ax_c.annotate('', xy=(x_offset+1.42+0.21, -13), xytext=(x_offset-0.21, -13),
                      arrowprops=dict(arrowstyle='-', color=dot_col, lw=1.5))
        ax_c.text(xm, -15.5, dot_label, ha='center', fontsize=7.5,
                  color=dot_col, fontweight='bold')

    ax_c.set_xticks([0, 0.5, 1.0, 1.5, 2.2, 2.7, 3.2, 3.7])
    ax_c.set_xticklabels(
        ['D✓\nNr','D✓\nFr','D✗\nNr','D✗\nFr',
         'D✓\nNr','D✓\nFr','D✗\nNr','D✗\nFr'], fontsize=6.5)
    # Legend patches
    near_patch = mpatches.Patch(color=C_NEAR, label='Near translation')
    far_patch  = mpatches.Patch(color=C_FAR,  label='Far translation')
    dep_no_patch = mpatches.Patch(facecolor='#ccc', hatch='//', edgecolor='#888',
                                  label='Depth Cueing ✗')
    ax_c.legend(handles=[near_patch, far_patch, dep_no_patch],
                fontsize=6, loc='upper right', framealpha=0.9)
    style_ax(ax_c, title='C.  TransDepth split within 2×2', ylim=(-18, 65))

    # ── Panel D: Summary cueing effects ────────────────────────────────────────
    ax_d = fig.add_subplot(gs[1, 1])

    # Cueing effects: Depth YES − Depth NO, for CUED and UNCUED
    # Also: CUED − UNCUED within Depth YES and Depth NO
    eff_labels = ['F1: CUED\nvs UNCUED\n(both Dep)',
                  'F2: Depth✓\nvs Depth✗\n(both Cond)',
                  'F1 × F2:\ninteraction']

    def eff(k1, n1, k2, n2):
        return acc_pp(k1,n1) - acc_pp(k2,n2), z_test(k1,n1,k2,n2)[1]

    # F1: (CUED,YES) + (CUED,NO) vs (UNCUED,YES) + (UNCUED,NO)
    cy_k, cy_n = m22.get(('CUED','YES'), [0,1])
    cn_k, cn_n = m22.get(('CUED','NO'), [0,1])
    uy_k, uy_n = m22.get(('UNCUED','YES'), [0,1])
    un_k, un_n = m22.get(('UNCUED','NO'), [0,1])

    f1_eff, f1_p = eff(cy_k+cn_k, cy_n+cn_n, uy_k+un_k, uy_n+un_n)
    f2_eff, f2_p = eff(cy_k+uy_k, cy_n+uy_n, cn_k+un_k, cn_n+un_n)
    # Interaction: (CY-CN) - (UY-UN)
    cy_pp = acc_pp(cy_k, cy_n); cn_pp = acc_pp(cn_k, cn_n)
    uy_pp = acc_pp(uy_k, uy_n); un_pp = acc_pp(un_k, un_n)
    int_eff = (cy_pp - cn_pp) - (uy_pp - un_pp)

    effs    = [f1_eff, f2_eff, int_eff]
    eff_ps  = [f1_p, f2_p, None]
    eff_col = [C_CUED, C_DEP_Y, '#7744aa']

    xs = [0, 0.7, 1.4]
    for x, ef, ep, ec, lbl in zip(xs, effs, eff_ps, eff_col, eff_labels):
        col = ec if ef >= 0 else '#cc4444'
        ax_d.bar(x, ef, 0.55, color=col, alpha=0.85, zorder=3,
                 edgecolor='white', linewidth=0.5)
        y_txt = ef + 1 if ef >= 0 else ef - 1
        va    = 'bottom' if ef >= 0 else 'top'
        s_lbl = stars(ep) if ep is not None else '—'
        ax_d.text(x, y_txt, s_lbl, ha='center', va=va, fontsize=8, color='#333')

    ax_d.set_xticks(xs)
    ax_d.set_xticklabels(eff_labels, fontsize=6.5)
    ax_d.set_ylabel('Effect size (pp above chance diff.)', fontsize=7)
    style_ax(ax_d, title='D.  Main effects summary', ylim=(-25, 60), ylabel=False)
    ax_d.set_ylabel('Δ pp', fontsize=7.5)

    # ── Panel E: Overall accuracy table ────────────────────────────────────────
    ax_e = fig.add_subplot(gs[1, 2])
    ax_e.axis('off')

    table_rows = []
    headers = ['Condition', 'k', 'n', '%corr', '+chance', 'sig']
    for (cond, dep_cue), (k, n) in sorted(m22.items()):
        dep_label = 'Depth✓' if dep_cue=='YES' else 'Depth✗'
        swap_label = ('ZdNoi' if (cond=='CUED' and dep_cue=='YES') or
                                  (cond=='UNCUED' and dep_cue=='NO') else 'ZdCoh')
        row_label = f"{cond[:1]}+{dep_label}\n({swap_label})"
        s, p = sig_vs_chance(k, n)
        table_rows.append([row_label, str(k), str(n),
                           f'{k/n*100:.1f}%', f'+{acc_pp(k,n):.1f}pp', s])

    # Also total
    all_k = sum(v[0] for v in m22.values())
    all_n = sum(v[1] for v in m22.values())
    s_all, _ = sig_vs_chance(all_k, all_n)
    table_rows.append(['TOTAL', str(all_k), str(all_n),
                       f'{all_k/all_n*100:.1f}%', f'+{acc_pp(all_k,all_n):.1f}pp', s_all])

    col_widths = [0.34, 0.1, 0.1, 0.14, 0.16, 0.1]
    xs_t = np.cumsum([0] + col_widths[:-1])
    y0 = 0.92
    lh = 0.13

    # Header
    for xi, (h, xpos) in enumerate(zip(headers, xs_t)):
        ax_e.text(xpos, y0, h, transform=ax_e.transAxes,
                  fontsize=7.5, fontweight='bold', va='top', color='#222')

    ax_e.plot([0, 1], [y0 - lh*0.5]*2, color='#aaa', lw=0.8,
              transform=ax_e.transAxes, clip_on=False)

    row_colors = ['#EEF8EE', '#FFFAEE', '#EEF2FF', '#F5F5F5', '#EEEEEE']
    for ri, row in enumerate(table_rows):
        y = y0 - lh*(ri+1) - 0.02
        bg = row_colors[ri % len(row_colors)]
        ax_e.axhspan(y - lh*0.45, y + lh*0.55, xmin=0, xmax=1,
                     facecolor=bg, alpha=0.5, transform=ax_e.transAxes)
        for xi, (cell, xpos) in enumerate(zip(row, xs_t)):
            ax_e.text(xpos + 0.01, y, cell,
                      transform=ax_e.transAxes,
                      fontsize=6.8, va='center', color='#222')

    ax_e.set_title('E.  Accuracy table', fontsize=9, fontweight='bold', pad=4)

    # ── Footer ─────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.02,
        'Error bars: 95% Wilson CI.  Stars vs chance (12.5%): †p<.1  *p<.05  **p<.01  ***p<.001  |  '
        'Depth Cueing YES: translator at DFD during translation.  '
        'CUED+ZdNoi  &  UNCUED+ZdCoh = Depth✓;  CUED+ZdCoh  &  UNCUED+ZdNoi = Depth✗',
        ha='center', va='bottom', fontsize=6, color='#666',
        wrap=True)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {OUT_PATH}")
    return fig

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    data = analyze()

    # Print summary
    n = data['n_valid']
    m = data['main22']
    print(f"\nSession: 260404_0940   n={n}")
    print(f"{'Condition':<22} {'k':>4} {'n':>4}  {'%corr':>6}  {'pp>chance':>9}")
    print('─'*55)
    order = [('CUED','YES'), ('CUED','NO'), ('UNCUED','YES'), ('UNCUED','NO')]
    swap_names = {('CUED','YES'):'ZdNoi', ('CUED','NO'):'ZdCoh',
                  ('UNCUED','YES'):'ZdCoh', ('UNCUED','NO'):'ZdNoi'}
    for key in order:
        k, n_c = m.get(key, [0,1])
        label = f"{key[0]}  Depth{'✓' if key[1]=='YES' else '✗'}  ({swap_names[key]})"
        s, _ = sig_vs_chance(k, n_c)
        print(f"  {label:<20} {k:>4} {n_c:>4}  {k/n_c*100:>6.1f}%  "
              f"{(k/n_c-1/8)*100:>+7.1f}pp  {s}")

    # Main effects
    cy_k,cy_n = m.get(('CUED','YES'),[0,1])
    cn_k,cn_n = m.get(('CUED','NO'),[0,1])
    uy_k,uy_n = m.get(('UNCUED','YES'),[0,1])
    un_k,un_n = m.get(('UNCUED','NO'),[0,1])
    print()
    f1_eff = (cy_k+cn_k)/(cy_n+cn_n) - (uy_k+un_k)/(uy_n+un_n)
    _, f1_p = z_test(cy_k+cn_k,cy_n+cn_n,uy_k+un_k,uy_n+un_n)
    f2_eff = (cy_k+uy_k)/(cy_n+uy_n) - (cn_k+un_k)/(cn_n+un_n)
    _, f2_p = z_test(cy_k+uy_k,cy_n+uy_n,cn_k+un_k,cn_n+un_n)
    print(f"F1 Dot Cueing effect:   {f1_eff*100:+.1f}pp  {stars(f1_p)} (p={f1_p:.3f})")
    print(f"F2 Depth Cueing effect: {f2_eff*100:+.1f}pp  {stars(f2_p)} (p={f2_p:.3f})")

    make_figure(data)
