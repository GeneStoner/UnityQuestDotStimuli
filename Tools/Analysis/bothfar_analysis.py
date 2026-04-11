"""
BothFar_005m — Single session analysis
Session: 260411_1225
Design: Both depth planes behind fixation (+0.05m and +0.10m)
        DelayedFieldDepth N = less-far (+0.05m), F = more-far (+0.10m)
        Swaps: N / C / Z / CZ  ×  CUED / UNCUED  ×  Less-Far / More-Far
        linkDepthColor = 0
Observer: GS
n ≈ 513 valid trials

Session notes (GS, 2026-04-11):
  - Jerky motion artifact: again noticed on subset of trials; perceived as upward (or downward/oblique).
    Not new — present in prior sessions. Trace analysis motivated partly to investigate this.
    Not clearly a new problem introduced by BothFar design.
  - Depth separation: on some portions of some trials, red and green dots did not appear well-separated
    in depth. May accompany depth swaps (Z and CZ conditions), consistent with transient vergence
    disruption at tStart when planes reassign. Worth flagging for interpretation of Z/CZ conditions.
  - Direction uncertainty: many trials where motion was perceived but exact direction unclear (8AFC
    inherently difficult). Observer reports frustration with fine direction discrimination.
"""

import os, csv, collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import chi2_contingency

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSION_PATH = '/tmp/quest_pull4/files/vr_dots_session_260411_1225.tsv'
OUT_DIR = os.path.join(os.path.dirname(__file__),
                       '../../Agents/SwapPilot/Figures')
OUT_PDF  = os.path.join(OUT_DIR, 'bothfar_analysis.pdf')

# Relabel for figures: N = Less-Far (+0.05m), F = More-Far (+0.10m)
DEPTH_LABEL = {'N': 'Less-Far\n(+0.05m)', 'F': 'More-Far\n(+0.10m)'}
DEPTH_SHORT  = {'N': 'LF (+0.05m)', 'F': 'MF (+0.10m)'}

CHANCE = 1/8
SWAP_ORDER = ['N', 'C', 'Z', 'CZ']
SWAP_COLORS = {'N': '#444444', 'C': '#e08000', 'Z': '#1a6bb5', 'CZ': '#9b2eaa'}

# ── Stats helpers ───────────────────────────────────────────────────────────────
def wilson_ci(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k/n
    denom = 1 + z**2/n
    centre = (p + z**2/(2*n)) / denom
    half   = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return max(0, centre - half), min(1, centre + half)

def pct(k, n):
    return 0.0 if n == 0 else k/n*100

def pp(k, n):
    return 0.0 if n == 0 else (k/n - CHANCE)*100

def pp_ci(k, n):
    lo, hi = wilson_ci(k, n)
    return (lo - CHANCE)*100, (hi - CHANCE)*100

def chi2_p(table):
    with np.errstate(divide='ignore', invalid='ignore'):
        _, p, _, _ = chi2_contingency(table, correction=False)
    return p

def sig_str(p):
    if p < .001: return '***'
    if p < .01:  return '**'
    if p < .05:  return '*'
    if p < .1:   return '†'
    return 'n.s.'

# ── Load data ──────────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def load():
    with open(SESSION_PATH, newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    valid = [r for r in rows
             if r.get('TransDeg','').strip()
             and r.get('RespDeg','').strip()
             and r.get('EndKey','') not in ('timeout', 'skip', 'requeue')
             and r.get('RespIndex','').strip() != '-1']
    for r in valid:
        r['correct'] = int(is_correct(r['TransDeg'], r['RespDeg']))
    return valid

# ── Aggregate ──────────────────────────────────────────────────────────────────
def aggregate(data):
    # (cond, swap, depth) -> [k, n]
    cell = collections.defaultdict(lambda: [0, 0])
    # (cond, swap) -> [k, n]
    by_swap = collections.defaultdict(lambda: [0, 0])
    # (cond, depth) -> [k, n]
    by_depth = collections.defaultdict(lambda: [0, 0])
    # (cond,) -> [k, n]
    overall = collections.defaultdict(lambda: [0, 0])

    for r in data:
        c  = r['Cond']
        sw = r['SwapType']
        dp = r['DelayedFieldDepth']  # N=Less-Far, F=More-Far
        k  = r['correct']
        cell[(c, sw, dp)][0] += k;  cell[(c, sw, dp)][1] += 1
        by_swap[(c, sw)][0]  += k;  by_swap[(c, sw)][1]  += 1
        by_depth[(c, dp)][0] += k;  by_depth[(c, dp)][1] += 1
        overall[c][0]        += k;  overall[c][1]        += 1

    return cell, by_swap, by_depth, overall

# ── Print summary ──────────────────────────────────────────────────────────────
def print_summary(data, cell, by_swap, by_depth, overall):
    n_valid = len(data)
    print(f"\n{'='*60}")
    print(f"BothFar_005m  —  Session 260411_1225")
    print(f"n valid trials: {n_valid}  (target 512)")
    print(f"{'='*60}\n")

    print("OVERALL:")
    for c in ['CUED', 'UNCUED']:
        k, n = overall[c]
        print(f"  {c:8s}: {pct(k,n):.1f}%  ({pp(k,n):+.1f}pp above chance)  n={n}")

    print("\nBY SWAP CONDITION:")
    for sw in SWAP_ORDER:
        kc, nc = by_swap[('CUED', sw)]
        ku, nu = by_swap[('UNCUED', sw)]
        delta = pp(kc,nc) - pp(ku,nu)
        print(f"  {sw:3s}  CUED={pct(kc,nc):.1f}% ({pp(kc,nc):+.1f}pp) n={nc}   "
              f"UNCUED={pct(ku,nu):.1f}% ({pp(ku,nu):+.1f}pp) n={nu}   "
              f"Δ={delta:+.1f}pp")

    print("\nBY DEPTH PLANE (translating-field depth):")
    print("  (N = Less-Far +0.05m,  F = More-Far +0.10m)")
    for dp, lbl in [('N','Less-Far'), ('F','More-Far')]:
        kc, nc = by_depth[('CUED', dp)]
        ku, nu = by_depth[('UNCUED', dp)]
        delta = pp(kc,nc) - pp(ku,nu)
        print(f"  {lbl:10s}  CUED={pct(kc,nc):.1f}% ({pp(kc,nc):+.1f}pp) n={nc}   "
              f"UNCUED={pct(ku,nu):.1f}% ({pp(ku,nu):+.1f}pp) n={nu}   "
              f"Δ={delta:+.1f}pp")

    # Chi2: depth × accuracy for CUED and UNCUED trials
    tc = [[by_depth[('CUED','N')][0], by_depth[('CUED','N')][1]-by_depth[('CUED','N')][0]],
          [by_depth[('CUED','F')][0], by_depth[('CUED','F')][1]-by_depth[('CUED','F')][0]]]
    tu = [[by_depth[('UNCUED','N')][0], by_depth[('UNCUED','N')][1]-by_depth[('UNCUED','N')][0]],
          [by_depth[('UNCUED','F')][0], by_depth[('UNCUED','F')][1]-by_depth[('UNCUED','F')][0]]]
    p_cued   = chi2_p(tc)
    p_uncued = chi2_p(tu)
    print(f"\n  Chi2 Less-Far vs More-Far: CUED p={p_cued:.3f} {sig_str(p_cued)}   "
          f"UNCUED p={p_uncued:.3f} {sig_str(p_uncued)}")

    print("\nCELL TABLE (CUED/UNCUED × swap × depth):")
    print(f"  {'':4s}  {'Less-Far (+0.05m)':^28s}  {'More-Far (+0.10m)':^28s}")
    print(f"  {'Swap':4s}  {'CUED':>12s}  {'UNCUED':>12s}  {'CUED':>12s}  {'UNCUED':>12s}")
    for sw in SWAP_ORDER:
        vals = []
        for dp in ['N', 'F']:
            for c in ['CUED', 'UNCUED']:
                k, n = cell[(c, sw, dp)]
                vals.append(f"{pct(k,n):5.1f}% (n={n})")
        print(f"  {sw:4s}  {vals[0]:>14s}  {vals[1]:>14s}  {vals[2]:>14s}  {vals[3]:>14s}")

# ── Figure ─────────────────────────────────────────────────────────────────────
def make_figure(data, cell, by_swap, by_depth, overall):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.82, bottom=0.18, wspace=0.38)
    fig.suptitle('BothFar_005m  —  Session 260411_1225  (both planes behind fixation)',
                 fontsize=10, fontweight='bold', y=0.96)

    CUED_C   = '#1a6bb5'
    UNCUED_C = '#aaaaaa'
    W = 0.32

    # ── Panel 1: Overall + by swap ─────────────────────────────────────────────
    ax = axes[0]
    ax.set_title('By swap condition', fontsize=9)
    ax.axhline(0, color='black', lw=0.7, ls='--')
    ax.axhline((1-CHANCE)*100, color='#cccccc', lw=0.5, ls=':')

    xs = np.arange(len(SWAP_ORDER))
    for i, sw in enumerate(SWAP_ORDER):
        for j, (c, col) in enumerate([('CUED', CUED_C), ('UNCUED', UNCUED_C)]):
            k, n = by_swap[(c, sw)]
            y = pp(k, n)
            lo, hi = pp_ci(k, n)
            x = xs[i] + (j-0.5)*W
            ax.bar(x, y, W*0.9, color=col, alpha=0.85, zorder=3)
            ax.plot([x,x], [lo, hi], color='black', lw=1.2, zorder=4)
            ax.plot(x, lo, '_', color='black', ms=4, zorder=4)
            ax.plot(x, hi, '_', color='black', ms=4, zorder=4)

    ax.set_xticks(xs)
    ax.set_xticklabels(SWAP_ORDER, fontsize=9)
    ax.set_ylabel('% correct above chance (pp)', fontsize=8)
    ax.set_xlabel('Swap condition', fontsize=8)
    ax.tick_params(labelsize=8)

    p1 = mpatches.Patch(color=CUED_C, label='CUED')
    p2 = mpatches.Patch(color=UNCUED_C, label='UNCUED')
    ax.legend(handles=[p1,p2], fontsize=7.5, loc='upper right')

    # ── Panel 2: By depth plane (CUED/UNCUED × LF/MF) ─────────────────────────
    ax = axes[1]
    ax.set_title('By depth plane\n(N=Less-Far +0.05m, F=More-Far +0.10m)', fontsize=9)
    ax.axhline(0, color='black', lw=0.7, ls='--')

    depth_labels = ['Less-Far\n(+0.05m)', 'More-Far\n(+0.10m)']
    xs2 = np.arange(2)
    for j, (c, col) in enumerate([('CUED', CUED_C), ('UNCUED', UNCUED_C)]):
        for i, dp in enumerate(['N', 'F']):
            k, n = by_depth[(c, dp)]
            y = pp(k, n)
            lo, hi = pp_ci(k, n)
            x = xs2[i] + (j-0.5)*W
            ax.bar(x, y, W*0.9, color=col, alpha=0.85, zorder=3)
            ax.plot([x,x], [lo, hi], color='black', lw=1.2, zorder=4)
            ax.plot(x, lo, '_', color='black', ms=4, zorder=4)
            ax.plot(x, hi, '_', color='black', ms=4, zorder=4)
            ax.text(x, y + (1 if y >= 0 else -2), f'n={n}',
                    ha='center', va='bottom', fontsize=6.5)

    ax.set_xticks(xs2)
    ax.set_xticklabels(depth_labels, fontsize=8.5)
    ax.set_ylabel('% correct above chance (pp)', fontsize=8)
    ax.tick_params(labelsize=8)
    ax.legend(handles=[p1,p2], fontsize=7.5, loc='upper right')

    # Add cueing delta annotations
    for i, dp in enumerate(['N', 'F']):
        kc, nc = by_depth[('CUED', dp)]
        ku, nu = by_depth[('UNCUED', dp)]
        delta = pp(kc,nc) - pp(ku,nu)
        ymax = max(pp(kc,nc), pp(ku,nu))
        p_val = chi2_p([[kc, nc-kc], [ku, nu-ku]])
        ax.annotate(f'Δ={delta:+.1f}pp\n{sig_str(p_val)}',
                    xy=(xs2[i], ymax+2), ha='center', fontsize=7.5,
                    color='#222222')

    # ── Panel 3: CUED 2×4 grid (swap × depth) ─────────────────────────────────
    ax = axes[2]
    ax.set_title('CUED arm: swap × depth plane', fontsize=9)
    ax.axhline(0, color='black', lw=0.7, ls='--')

    xs3 = np.arange(len(SWAP_ORDER))
    depth_plot = [('N', '#3a7dca', 'Less-Far'), ('F', '#c04040', 'More-Far')]
    bars3 = []
    for j, (dp, col, lbl) in enumerate(depth_plot):
        ys, los, his, ns = [], [], [], []
        for sw in SWAP_ORDER:
            k, n = cell[('CUED', sw, dp)]
            ys.append(pp(k,n))
            lo, hi = pp_ci(k,n)
            los.append(lo); his.append(hi)
            ns.append(n)
        x = xs3 + (j-0.5)*W
        b = ax.bar(x, ys, W*0.9, color=col, alpha=0.85, zorder=3, label=lbl)
        bars3.append(b)
        for xi, (y, lo, hi, n) in enumerate(zip(ys, los, his, ns)):
            ax.plot([x[xi],x[xi]], [lo, hi], color='black', lw=1.2, zorder=4)
            ax.plot(x[xi], lo, '_', color='black', ms=4, zorder=4)
            ax.plot(x[xi], hi, '_', color='black', ms=4, zorder=4)

    ax.set_xticks(xs3)
    ax.set_xticklabels(SWAP_ORDER, fontsize=9)
    ax.set_ylabel('% correct above chance (pp)', fontsize=8)
    ax.set_xlabel('Swap condition (CUED only)', fontsize=8)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7.5, loc='upper right')

    return fig

# ── Notes page ────────────────────────────────────────────────────────────────
def make_notes_page():
    fig = plt.figure(figsize=(8.5, 6))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])
    ax.axis('off')

    title = 'BothFar_005m — Session Notes (GS, 2026-04-11)'
    ax.text(0.5, 0.97, title, transform=ax.transAxes,
            ha='center', va='top', fontsize=11, fontweight='bold')

    notes = [
        ('Design', (
            'Both depth fields placed behind fixation: Less-Far = +0.05m, More-Far = +0.10m '
            '(both uncrossed disparity). Swaps: N / C / Z / CZ. linkDepthColor = 0. '
            'Same structure as DecoupledDots_005m except no field crosses the fixation plane.'
        )),
        ('Jerky motion artifact', (
            'Again observed on a subset of trials — perceived as predominantly upward, '
            'occasionally downward or oblique. This is not new; it has been present in prior sessions '
            '(DecoupledDots, DepthColorLinked). Trace figures were partly motivated to investigate this. '
            'Tentative read: the percept is a rotation-burst artifact (rotational motion briefly '
            'dominates the direction report), not a stimulus rendering error per se. '
            'No evidence it is specific to BothFar. Warrants further investigation but is likely '
            'an observer-side perceptual effect rather than a new stimulus artifact.'
        )),
        ('Depth separation during swaps', (
            'On some portions of some trials, the red and green dot fields did not appear '
            'well-separated in depth. This was most noticeable during or just after depth swaps '
            '(Z and CZ conditions). Consistent with a transient vergence disruption at tStart '
            'when depth planes reassign — the visual system may need a brief period to re-establish '
            'correct vergence to the new plane positions. This is particularly relevant for Z/CZ '
            'interpretation: some of the deficit may reflect not just loss of depth-identity '
            'continuity, but also a transient period of reduced depth salience.'
        )),
        ('Direction uncertainty', (
            'Many trials perceived as showing motion but with uncertain exact direction (8AFC, '
            'chance = 12.5%). Observer reports frustration with fine direction discrimination. '
            'This is expected and consistent with prior sessions — the task is inherently noisy '
            'at threshold-level stimulation. Not specific to BothFar.'
        )),
        ('Key question for this session', (
            'Does the Less-Far/More-Far asymmetry mirror the old Near/Far asymmetry? '
            'If the fixation-plane hypothesis is correct, both planes are now beyond the fixation '
            'anchor, so the structural bias should be absent or reversed (favouring Less-Far, '
            'the plane closer to fixation). If the asymmetry persists in the same direction '
            '(More-Far > Less-Far), that would suggest it is not primarily a fixation-plane effect '
            'but rather a vergence-comfort effect tied to absolute depth (esophoria account).'
        )),
    ]

    y = 0.90
    for heading, body in notes:
        ax.text(0.0, y, heading + ':', transform=ax.transAxes,
                ha='left', va='top', fontsize=9, fontweight='bold', color='#222222')
        y -= 0.03
        # wrap body text
        words = body.split()
        line, lines = '', []
        for w in words:
            test = (line + ' ' + w).strip()
            if len(test) > 105:
                lines.append(line)
                line = w
            else:
                line = test
        if line: lines.append(line)
        for l in lines:
            ax.text(0.02, y, l, transform=ax.transAxes,
                    ha='left', va='top', fontsize=8, color='#333333')
            y -= 0.028
        y -= 0.015

    ax.text(0.5, 0.01, f'Data: {SESSION_PATH}',
            transform=ax.transAxes, ha='center', va='bottom',
            fontsize=6.5, color='#888888')
    return fig

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    data = load()
    print(f"Loaded {len(data)} valid trials from {SESSION_PATH}")

    cell, by_swap, by_depth, overall = aggregate(data)
    print_summary(data, cell, by_swap, by_depth, overall)

    os.makedirs(OUT_DIR, exist_ok=True)
    with PdfPages(OUT_PDF) as pdf:
        fig = make_figure(data, cell, by_swap, by_depth, overall)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        fig2 = make_notes_page()
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)

    print(f"\nSaved → {OUT_PDF}")

if __name__ == '__main__':
    main()
