"""
Depth-swap upward-motion artifact — comprehensive analysis
==========================================================

KEY FINDING:
The 100% depth swap (Z, CZ conditions) produces a systematic UPWARD motion percept
that contaminates direction reports in ~40–60% of trials. This is a STIMULUS ARTIFACT,
not perceptual noise. Observer GS's reports of "jerky upward motion" are confirmed by
the response data.

DIRECTION CONVENTION (code uses math convention, not compass):
  TransDeg/RespDeg = 0  → RIGHTWARD  (Cos(0)=1, Sin(0)=0 → +X in local space)
  TransDeg/RespDeg = 90 → UPWARD     (Cos(90)=0, Sin(90)=1 → +Y in local space)
  TransDeg/RespDeg = 180 → LEFTWARD
  TransDeg/RespDeg = 270 → DOWNWARD

THE ARTIFACT:
  In Z/CZ conditions, at tStart ALL dots simultaneously jump ±depthOffset_m along
  StimulusBuilder.transform.forward. If transform.forward is not perfectly aligned with
  the camera's optical axis (i.e., it has an upward pitch component), this creates a
  brief apparent translational impulse in the upward direction that dominates the
  direction percept.

MECHANISM:
  StimulusBuilder.ApplyDepthOffsets() shifts every dot along transform.forward * z.
  If transform.forward is pitched upward by angle θ relative to the camera's line of
  sight, the depth change of ±0.10m produces an apparent vertical displacement of:
    Δy_screen = 0.10m × sin(θ) / viewDistance
  For θ ≈ 5–10°: Δy ≈ 0.25–0.5°. This occurs in a single frame (~13ms at 75Hz),
  producing an apparent velocity of ~20–40°/sec — much faster than the translation
  signal (2.26°/sec). It is an impulse that precedes and dominates the signal.

EVIDENCE:
  1. UP (RespDeg=90) share of wrong responses: N=4%, C=7%, Z=50%, CZ=51%
  2. Consistent across sessions, RotCfg (0 vs 1), CUED/UNCUED, DelayedFieldDepth
  3. For td=270 (DOWN motion), Z condition: 60.9% of responses = UP (wrong direction)
  4. For td=90 (UP motion), Z condition: accuracy ELEVATED vs N (45.3% vs 35.9%)
     because artifact and signal align
  5. BothFar (depth change = 0.05m): UP bias = 44% — smaller than DD (50%) but
     larger than expected for pure linear scaling, suggesting some threshold effect
  6. DCL ZdA/ZdB (only 50% of dots swap): UP bias = 26% — reduced, consistent with
     smaller total depth-change impulse

IMPACT ON RESULTS:
  The cueing ADVANTAGE (CUED − UNCUED) is largely preserved because the artifact
  affects both arms equally (CUED UP-wrong=51%, UNCUED UP-wrong=49%). However:
  - Absolute accuracy in Z/CZ is depressed for all non-UP headings
  - Absolute accuracy in Z/CZ is inflated for the UP heading (td=90)
  - The apparent depth-swap disruption is larger than the true effect
  - N=64/condition does not allow clean heading-stratified analysis

PROPOSED FIX:
  Replace `transform.forward` in StimulusBuilder.ApplyDepthOffsets() with the
  camera's actual forward direction (Camera.main.transform.forward) or the
  per-dot view vector. This ensures depth offsets are applied along the true
  viewing axis regardless of the StimulusBuilder's orientation in world space.
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
DD_SESSIONS = [
    ('/tmp/quest_pull3/files/vr_dots_session_260406_1532.tsv', False, 'S1'),
    ('/tmp/quest_pull3/files/vr_dots_session_260406_1754.tsv', True,  'S2'),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv', True,  'S3'),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv', False, 'S4'),
]
BF_SESSION  = '/tmp/quest_pull4/files/vr_dots_session_260411_1225.tsv'
DCL_SESSIONS = [
    '/tmp/quest_pull2/files/vr_dots_session_260404_0940.tsv',
    '/tmp/quest_pull2/files/vr_dots_session_260404_1123.tsv',
    '/tmp/quest_pull2/files/vr_dots_session_260406_1001.tsv',
    '/tmp/quest_pull2/files/vr_dots_session_260406_1034.tsv',
]
OUT_DIR = os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures')
OUT_PDF  = os.path.join(OUT_DIR, 'depth_swap_artifact.pdf')

DIRS     = [0, 45, 90, 135, 180, 225, 270, 315]
DIR_NAMES = {0: 'RT', 45: 'UR', 90: 'UP', 135: 'UL',
             180: 'LT', 225: 'DL', 270: 'DN', 315: 'DR'}
CHANCE = 1/8
UP_DEG = 90   # the artifact direction in math convention

# ── Helpers ────────────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def wilson_ci(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k/n
    denom = 1 + z**2/n
    c = (p + z**2/(2*n))/denom
    h = z*np.sqrt(p*(1-p)/n + z**2/(4*n**2))/denom
    return max(0, c-h), min(1, c+h)

def load_session(path, invert=False):
    rows = []
    try:
        with open(path, newline='') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if r.get('RespIndex','').strip() == '-1': continue
                if r.get('EndKey','') in ('timeout','skip','requeue'): continue
                if invert:
                    r['Cond'] = 'UNCUED' if r['Cond']=='CUED' else 'CUED'
                r['correct'] = int(is_correct(r['TransDeg'], r['RespDeg']))
                rows.append(r)
    except FileNotFoundError:
        pass
    return rows

# ── Load data ──────────────────────────────────────────────────────────────────
dd_rows = []
for path, inv, _ in DD_SESSIONS:
    dd_rows.extend(load_session(path, inv))

bf_rows = load_session(BF_SESSION)

dcl_rows = []
for path in DCL_SESSIONS:
    dcl_rows.extend(load_session(path))

print(f"Loaded: DD n={len(dd_rows)}, BF n={len(bf_rows)}, DCL n={len(dcl_rows)}")

# ── Helper: UP bias summary ────────────────────────────────────────────────────
def up_bias_stats(rows):
    """For each swap condition: fraction of WRONG responses that are UP (90°)."""
    by_sw = collections.defaultdict(lambda: [0, 0])  # [n_up_wrong, n_wrong]
    by_sw_all = collections.defaultdict(lambda: [0, 0])  # [n_up, n_total]
    for r in rows:
        sw = r['SwapType']
        rd = int(float(r['RespDeg']))
        correct = r['correct']
        by_sw_all[sw][1] += 1
        if rd == UP_DEG:
            by_sw_all[sw][0] += 1
        if not correct:
            by_sw[sw][1] += 1
            if rd == UP_DEG:
                by_sw[sw][0] += 1
    return by_sw, by_sw_all

# ── Confusion matrix ───────────────────────────────────────────────────────────
def confusion(rows, swap_filter=None):
    conf = np.zeros((8, 8), dtype=int)
    for r in rows:
        if swap_filter and r['SwapType'] not in swap_filter:
            continue
        td = int(float(r['TransDeg']))
        rd = int(float(r['RespDeg']))
        ti = DIRS.index(td)
        ri = DIRS.index(rd)
        conf[ti][ri] += 1
    return conf

# ── Figure 1: Response distribution & UP bias ──────────────────────────────────
def make_fig1(dd_rows, bf_rows, dcl_rows):
    fig = plt.figure(figsize=(14, 9))
    fig.suptitle('Depth-swap upward motion artifact — response direction analysis',
                 fontsize=11, fontweight='bold', y=0.98)

    # Panel A: fraction of WRONG responses = UP, by condition, for DD
    ax1 = fig.add_axes([0.06, 0.55, 0.27, 0.35])
    wrong_dd = [r for r in dd_rows if not r['correct']]
    up_bias_dd = {}
    for sw in ['N','C','Z','CZ']:
        sub = [r for r in wrong_dd if r['SwapType']==sw]
        n = len(sub)
        k = sum(1 for r in sub if int(float(r['RespDeg']))==UP_DEG)
        lo, hi = wilson_ci(k, n)
        up_bias_dd[sw] = (k/n if n>0 else 0, lo, hi, n)

    colors = {'N':'#444', 'C':'#e08000', 'Z':'#1a6bb5', 'CZ':'#9b2eaa'}
    xs = np.arange(4)
    for i, sw in enumerate(['N','C','Z','CZ']):
        y, lo, hi, n = up_bias_dd[sw]
        ax1.bar(xs[i], y*100, 0.6, color=colors[sw], alpha=0.85, zorder=3)
        ax1.plot([xs[i],xs[i]], [lo*100,hi*100], 'k-', lw=1.5, zorder=4)
        ax1.plot(xs[i], lo*100, 'k_', ms=5, zorder=4)
        ax1.plot(xs[i], hi*100, 'k_', ms=5, zorder=4)
        ax1.text(xs[i], y*100+1.5, f'n={n}', ha='center', fontsize=7)
    ax1.axhline(12.5, color='gray', lw=0.8, ls='--', label='chance (12.5%)')
    ax1.set_xticks(xs); ax1.set_xticklabels(['N','C','Z','CZ'], fontsize=10)
    ax1.set_ylabel('% wrong responses = UP (90°)', fontsize=8)
    ax1.set_title('A. UP bias in wrong responses\n(DecoupledDots, n=2048)', fontsize=9)
    ax1.set_ylim(0, 70); ax1.tick_params(labelsize=8)
    ax1.legend(fontsize=7, loc='upper left')

    # Panel B: per-session UP bias in Z condition
    ax2 = fig.add_axes([0.39, 0.55, 0.27, 0.35])
    session_labels = ['S1\nnorm','S2\ninv','S3\ninv','S4\nnorm']
    session_data = []
    for (path, inv, slbl), (path2, inv2, label) in zip(DD_SESSIONS, zip(
            [p for p,_,_ in DD_SESSIONS],
            [i for _,i,_ in DD_SESSIONS],
            session_labels)):
        sr = load_session(path, inv2)
        sw_wrong = [r for r in sr if r['SwapType']=='Z' and not r['correct']]
        n = len(sw_wrong)
        k = sum(1 for r in sw_wrong if int(float(r['RespDeg']))==UP_DEG)
        lo, hi = wilson_ci(k, n)
        session_data.append((k/n if n>0 else 0, lo, hi, n))

    for i, (y, lo, hi, n) in enumerate(session_data):
        ax2.bar(i, y*100, 0.6, color='#1a6bb5', alpha=0.8, zorder=3)
        ax2.plot([i,i],[lo*100,hi*100],'k-',lw=1.5,zorder=4)
        ax2.text(i, y*100+1.5, f'n={n}', ha='center', fontsize=7)
    ax2.axhline(12.5, color='gray', lw=0.8, ls='--')
    ax2.set_xticks(range(4)); ax2.set_xticklabels(session_labels, fontsize=8)
    ax2.set_ylabel('% wrong = UP (90°)', fontsize=8)
    ax2.set_title('B. Per-session: UP bias in Z\ncondition wrong responses', fontsize=9)
    ax2.set_ylim(0, 80); ax2.tick_params(labelsize=8)

    # Panel C: UP bias by RotCfg × swap
    ax3 = fig.add_axes([0.72, 0.55, 0.26, 0.35])
    for j, rotcfg in enumerate(['0', '1']):
        sub = [r for r in dd_rows if r['RotCfg']==rotcfg and not r['correct']]
        ys = []
        for sw in ['N','C','Z','CZ']:
            ssub = [r for r in sub if r['SwapType']==sw]
            n = len(ssub)
            k = sum(1 for r in ssub if int(float(r['RespDeg']))==UP_DEG)
            ys.append(k/n*100 if n>0 else 0)
        xs3 = np.arange(4) + (j-0.5)*0.35
        col = '#2060aa' if j==0 else '#aa6020'
        ax3.bar(xs3, ys, 0.32, color=col, alpha=0.8, label=f'RotCfg={rotcfg}', zorder=3)
    ax3.axhline(12.5, color='gray', lw=0.8, ls='--')
    ax3.set_xticks(np.arange(4)); ax3.set_xticklabels(['N','C','Z','CZ'], fontsize=10)
    ax3.set_ylabel('% wrong = UP', fontsize=8)
    ax3.set_title('C. UP bias by rotation config\n(rotation direction invariance)', fontsize=9)
    ax3.set_ylim(0, 70); ax3.legend(fontsize=8); ax3.tick_params(labelsize=8)

    # Panel D: accuracy by heading for N vs Z (CUED arm only)
    ax4 = fig.add_axes([0.06, 0.07, 0.42, 0.37])
    for sw, col, ls in [('N','#444','o-'), ('Z','#1a6bb5','s--')]:
        sub = [r for r in dd_rows if r['SwapType']==sw and r['Cond']=='CUED']
        accs, los, his = [], [], []
        for td in DIRS:
            s2 = [r for r in sub if int(float(r['TransDeg']))==td]
            k = sum(r['correct'] for r in s2); n = len(s2)
            accs.append(k/n*100 if n>0 else 0)
            lo, hi = wilson_ci(k,n)
            los.append(lo*100); his.append(hi*100)
        xs4 = np.arange(8)
        ax4.plot(xs4, accs, ls, color=col, ms=7, lw=1.5, label=f'{sw} cond.')
        ax4.fill_between(xs4, los, his, color=col, alpha=0.12)
    # Highlight UP direction
    ax4.axvline(DIRS.index(UP_DEG), color='red', lw=0.8, ls=':', alpha=0.7)
    ax4.text(DIRS.index(UP_DEG)+0.1, 2, 'UP\n(artifact)', fontsize=7, color='red')
    ax4.axhline(12.5, color='gray', lw=0.7, ls='--', alpha=0.7)
    ax4.set_xticks(np.arange(8))
    ax4.set_xticklabels([DIR_NAMES[d] for d in DIRS], fontsize=8.5)
    ax4.set_ylabel('% correct (CUED)', fontsize=8)
    ax4.set_title('D. Accuracy by heading: N vs Z (CUED arm)\n'
                  'UP heading (90°) elevated in Z; DOWN (270°) severely impaired',
                  fontsize=9)
    ax4.legend(fontsize=9); ax4.tick_params(labelsize=8)
    ax4.set_ylim(0, 65)

    # Panel E: UP bias scaling — DD vs BothFar vs DCL
    ax5 = fig.add_axes([0.58, 0.07, 0.38, 0.37])
    # Compute UP bias in wrong responses for each experiment/condition
    datasets = [
        ('DD N\n(0m)', [r for r in dd_rows if r['SwapType']=='N' and not r['correct']], '#444444'),
        ('DD Z\n(0.10m)', [r for r in dd_rows if r['SwapType']=='Z' and not r['correct']], '#1a6bb5'),
        ('BF Z\n(0.05m)', [r for r in bf_rows if r['SwapType']=='Z' and not r['correct']], '#4499dd'),
        ('DCL ZdA\n(~50%)', [r for r in dcl_rows if r['SwapType']=='ZdA' and not r['correct']], '#44aa44'),
        ('DCL ZdB\n(~50%)', [r for r in dcl_rows if r['SwapType']=='ZdB' and not r['correct']], '#228822'),
    ]
    for i, (lbl, rows, col) in enumerate(datasets):
        n = len(rows)
        k = sum(1 for r in rows if int(float(r['RespDeg']))==UP_DEG)
        lo, hi = wilson_ci(k, n)
        ax5.bar(i, k/n*100 if n>0 else 0, 0.6, color=col, alpha=0.85, zorder=3)
        ax5.plot([i,i],[lo*100,hi*100],'k-',lw=1.5,zorder=4)
        ax5.plot(i,lo*100,'k_',ms=5,zorder=4); ax5.plot(i,hi*100,'k_',ms=5,zorder=4)
        ax5.text(i, k/n*100+1.5 if n>0 else 1.5, f'n={n}', ha='center', fontsize=7)
    ax5.axhline(12.5, color='gray', lw=0.8, ls='--', label='chance')
    ax5.set_xticks(range(5)); ax5.set_xticklabels([d[0] for d in datasets], fontsize=8)
    ax5.set_ylabel('% wrong = UP (90°)', fontsize=8)
    ax5.set_title('E. UP bias by experiment / depth change magnitude\n'
                  'BF = BothFar (both planes beyond fixation)',
                  fontsize=9)
    ax5.set_ylim(0, 70); ax5.legend(fontsize=7); ax5.tick_params(labelsize=8)

    return fig

# ── Figure 2: Confusion matrices ───────────────────────────────────────────────
def make_fig2(dd_rows):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle('Response confusion matrices — N condition vs Z condition (DecoupledDots)',
                 fontsize=10, fontweight='bold')
    fig.subplots_adjust(wspace=0.35, left=0.08, right=0.97, top=0.88, bottom=0.12)

    col_labels = [DIR_NAMES[d] for d in DIRS]

    for ax, sw, title in [(axes[0],'N','No swap (N)'), (axes[1],'Z','Depth swap (Z)')]:
        conf = confusion(dd_rows, [sw])
        # Normalize by row
        norm = conf.astype(float)
        row_sums = norm.sum(axis=1, keepdims=True)
        norm = np.where(row_sums>0, norm/row_sums, 0) * 100

        im = ax.imshow(norm, vmin=0, vmax=65, cmap='Blues', aspect='auto')
        plt.colorbar(im, ax=ax, shrink=0.8, label='% responses')

        for i in range(8):
            for j in range(8):
                val = norm[i,j]
                col_txt = 'white' if val > 40 else 'black'
                # Mark diagonal
                weight = 'bold' if i==j else 'normal'
                ax.text(j, i, f'{val:.0f}', ha='center', va='center',
                        fontsize=7.5, color=col_txt, fontweight=weight)

        # Highlight UP column (j = index of UP_DEG = 90)
        up_col = DIRS.index(UP_DEG)
        ax.axvline(up_col-0.5, color='red', lw=1.5, alpha=0.6)
        ax.axvline(up_col+0.5, color='red', lw=1.5, alpha=0.6)

        ax.set_xticks(range(8)); ax.set_xticklabels(col_labels, fontsize=8.5)
        ax.set_yticks(range(8)); ax.set_yticklabels([DIR_NAMES[d] for d in DIRS], fontsize=8.5)
        ax.set_xlabel('Response direction', fontsize=9)
        ax.set_ylabel('True direction (TransDeg)', fontsize=9)
        ax.set_title(f'{title}\n(red = UP column)', fontsize=9)

    return fig

# ── Figure 3: Mechanism diagram + impact assessment ───────────────────────────
def make_fig3():
    fig = plt.figure(figsize=(11, 7.5))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.05, 0.05, 0.90, 0.90])
    ax.axis('off')

    def line(y, text, size=9, weight='normal', color='#222222', indent=0):
        ax.text(indent, y, text, transform=ax.transAxes,
                ha='left', va='top', fontsize=size, fontweight=weight, color=color)

    y = 0.98
    line(y, 'Depth-swap artifact: mechanism and impact on results', 11, 'bold', '#111111')
    y -= 0.05

    sections = [
        ('MECHANISM', [
            'When depth swap occurs at tStart (Z and CZ conditions), all 4 subfields simultaneously',
            'change depth-plane assignment. StimulusBuilder.ApplyDepthOffsets() then shifts each dot',
            'by ±depthOffset_m along transform.forward. If transform.forward is not aligned with the',
            'camera\'s optical axis (e.g., because the StimulusBuilder is pitched slightly upward in',
            'world space while the camera is looking straight ahead or slightly downward), this depth',
            'change has a component in the screen-vertical direction.',
            '',
            'For a pitch angle θ ≈ 5–10°, a 0.10m depth change produces:',
            '  Δy_screen = 0.10 × sin(θ) / 2.0m ≈ 0.25–0.5° apparent upward displacement',
            '  Delivered in 1 frame (~13ms at 75Hz) → apparent velocity ≈ 20–40 deg/sec',
            '  Translation signal = 2.26 deg/sec over 80ms = 0.18° total',
            '  → The artifact impulse is ~100–200× faster than the signal and precedes it.',
        ]),
        ('EVIDENCE', [
            '• UP (90°) share of wrong responses: N=4%, C=7%, Z=50%, CZ=51%  (DD, n=2048)',
            '• Consistent across sessions (37–59% per session), RotCfg 0 vs 1 (52% vs 47%),',
            '  CUED vs UNCUED (51% vs 49%), DelayedFieldDepth N vs F (48% vs 52%)',
            '• For TransDeg=270 (DOWN): Z condition produces 60.9% UP responses → observer',
            '  correctly perceives motion, but artifact overrides direction',
            '• For TransDeg=90 (UP): Z condition accuracy = 45.3% vs N = 35.9% (artifact HELPS)',
            '• BothFar (depth change = 0.05m): UP bias = 44% (reduced vs 50% but still large)',
            '• DCL ZdA/ZdB (50% of dots swap): UP bias = 26% (further reduced)',
            '• Bias absent in N, C conditions (no depth swap) → definitively tied to ApplyDepthOffsets',
        ]),
        ('IMPACT ON CUEING RESULTS', [
            '• Cueing advantage (CUED − UNCUED Δ) is PRESERVED: artifact affects both arms equally.',
            '  Z: CUED UP-wrong = 51%, UNCUED UP-wrong = 49% — nearly identical.',
            '  → The depth continuity effect on cueing is real, not an artifact.',
            '',
            '• Absolute accuracy in Z/CZ is underestimated for non-UP headings and overestimated',
            '  for the UP heading. The average across all 8 headings is deflated because UP trials',
            '  (1/8 of all trials) have inflated accuracy that does not offset the 7/8 deflated.',
            '',
            '• The apparent magnitude of depth disruption may be inflated: the Z→N accuracy drop',
            '  includes both (a) the true depth-identity disruption and (b) the artifact\'s misdirection.',
            '  These are impossible to separate at current data without heading-stratified analysis.',
        ]),
        ('PROPOSED FIX', [
            'In StimulusBuilder.ApplyDepthOffsets(), replace:',
            '    Vector3 zVec = transform.forward * z;',
            'with:',
            '    Vector3 camFwd = Camera.main != null ? Camera.main.transform.forward : transform.forward;',
            '    Vector3 zVec = camFwd * z;',
            '',
            'This ensures depth offsets are applied along the camera\'s actual optical axis regardless',
            'of the StimulusBuilder\'s world-space orientation. Should be tested in-headset before',
            'collecting new data — verify that the depth percept (Near/Far separation) is preserved.',
        ]),
    ]

    for section_title, lines_list in sections:
        line(y, section_title, 9.5, 'bold', '#1a1a6b')
        y -= 0.03
        for l in lines_list:
            if l == '':
                y -= 0.012
            else:
                line(y, l, 8, indent=0.02)
                y -= 0.025
        y -= 0.015

    return fig

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    with PdfPages(OUT_PDF) as pdf:
        fig1 = make_fig1(dd_rows, bf_rows, dcl_rows)
        pdf.savefig(fig1, bbox_inches='tight')
        plt.close(fig1)

        fig2 = make_fig2(dd_rows)
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)

        fig3 = make_fig3()
        pdf.savefig(fig3, bbox_inches='tight')
        plt.close(fig3)

    print(f"\nSaved → {OUT_PDF}")

    # Print key numbers
    print("\n=== KEY NUMBERS ===")
    print("UP (90°) share of wrong responses by swap condition (DecoupledDots):")
    wrong = [r for r in dd_rows if not r['correct']]
    for sw in ['N','C','Z','CZ']:
        sub = [r for r in wrong if r['SwapType']==sw]
        n = len(sub); k = sum(1 for r in sub if int(float(r['RespDeg']))==UP_DEG)
        print(f"  {sw}: {k/n*100:.1f}%  (n_wrong={n})")

    print("\nAccuracy by heading in Z (CUED), corrected direction labels:")
    sub_z = [r for r in dd_rows if r['SwapType']=='Z' and r['Cond']=='CUED']
    sub_n = [r for r in dd_rows if r['SwapType']=='N' and r['Cond']=='CUED']
    print(f"  {'Heading':>10s}  {'N acc':>7s}  {'Z acc':>7s}  {'Z UP%':>8s}")
    for td in DIRS:
        zs = [r for r in sub_z if int(float(r['TransDeg']))==td]
        ns = [r for r in sub_n if int(float(r['TransDeg']))==td]
        zacc = sum(r['correct'] for r in zs)/max(1,len(zs))*100
        nacc = sum(r['correct'] for r in ns)/max(1,len(ns))*100
        zup  = sum(1 for r in zs if int(float(r['RespDeg']))==UP_DEG)/max(1,len(zs))*100
        print(f"  {DIR_NAMES[td]:>10s} ({td:3d}°):  {nacc:5.1f}%   {zacc:5.1f}%   {zup:6.1f}% UP")

if __name__ == '__main__':
    main()
