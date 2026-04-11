#!/usr/bin/env python3
"""
fixation_plane_hypothesis.py
-----------------------------
Write-up PDF: Fixation plane as an attentional plane — evaluation of the
hypothesis that a standing Far > Near bias arises from fixation-based
depth attention, and how it interacts with the onset-cue attentional plane.

Output:
  Agents/WriteUps/fixation_plane_hypothesis.pdf
  Agents/SwapPilot/WriteUps/fixation_plane_hypothesis.pdf
"""

import datetime, os, textwrap as _tw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

_HERE   = os.path.dirname(os.path.abspath(__file__))
BASE_WU = os.path.normpath(os.path.join(_HERE, '../../Agents/WriteUps'))
BASE_SP = os.path.normpath(os.path.join(_HERE, '../../Agents/SwapPilot/WriteUps'))
os.makedirs(BASE_WU, exist_ok=True)
os.makedirs(BASE_SP, exist_ok=True)

OUT_PDFS = [
    os.path.join(BASE_WU, 'fixation_plane_hypothesis.pdf'),
    os.path.join(BASE_SP, 'fixation_plane_hypothesis.pdf'),
]

# ── Colour palette ─────────────────────────────────────────────────────────────
C_HEAD  = '#1a3a8b'
C_BODY  = '#111111'
C_DIM   = '#555555'
C_RULE  = '#bbbbbb'
C_FAR   = '#2255aa'
C_NEAR  = '#993333'
C_FIX   = '#336633'
C_HL    = '#f5f0e0'      # highlight box background

FF_SERIF = 'serif'
FF_SANS  = 'sans-serif'
FF_MONO  = 'monospace'

def hline(fig, y, lw=0.6, color=C_RULE):
    fig.add_artist(plt.Line2D([0.07, 0.93], [y, y],
                              transform=fig.transFigure,
                              color=color, lw=lw, clip_on=False))

def footer(fig, page_n, n_pages):
    fig.text(0.07, 0.030, f'Fixation-plane attentional hypothesis · VRDots pilot · {DATE_STR}',
             ha='left', va='bottom', fontsize=7, color=C_DIM, fontfamily=FF_SANS)
    fig.text(0.93, 0.030, f'{page_n} / {n_pages}',
             ha='right', va='bottom', fontsize=7, color=C_DIM, fontfamily=FF_SANS)
    hline(fig, 0.042, lw=0.4)

def page_title(fig, title, subtitle=None):
    fig.text(0.07, 0.945, title, ha='left', va='top',
             fontsize=14, fontweight='bold', color=C_HEAD, fontfamily=FF_SERIF)
    if subtitle:
        fig.text(0.07, 0.915, subtitle, ha='left', va='top',
                 fontsize=9, color=C_DIM, fontfamily=FF_SANS)
    hline(fig, 0.905 if subtitle else 0.930)

def body_text(fig, x, y, text, width=88, fontsize=9.5, lh=0.019,
              color=C_BODY, style='normal', indent=0.0):
    """Wrap and render a paragraph at (x, y), return y after last line."""
    for line in _tw.wrap(text, width=width):
        fig.text(x + indent, y, line, ha='left', va='top',
                 fontsize=fontsize, color=color, style=style,
                 fontfamily=FF_SERIF)
        y -= lh
    return y

def section_head(fig, x, y, text, fontsize=10.5):
    fig.text(x, y, text, ha='left', va='top',
             fontsize=fontsize, fontweight='bold', color=C_HEAD, fontfamily=FF_SERIF)
    return y - 0.028

# ══════════════════════════════════════════════════════════════════════════════
# Page 1 — Context + hypothesis statement
# ══════════════════════════════════════════════════════════════════════════════
P1_INTRO = (
    "The DecoupledDots and DepthColorLinked experiments consistently produce a "
    "Far\u202f>\u202fNear performance asymmetry of approximately 15\u202fpp "
    "(DecoupledDots GLM F4 AME: \u221215.3\u202fpp for Near; p\u202f<\u202f.001). "
    "The translating field is identified more reliably when it occupies the Far depth plane than the Near "
    "depth plane, regardless of swap condition. This asymmetry is absent under monocular viewing, "
    "establishing a binocular/stereoscopic origin. "
    "The mechanism, however, is unresolved."
)

P1_PREV = (
    "Prior discussion focused on the onset-cued surface as the primary attentional plane. "
    "The delayed-onset field captures exogenous attention, establishing a depth representation "
    "that the observer tracks across the cue interval. By analogy with the "
    "\u2018attended object extends attention behind it\u2019 principle, the cued plane could "
    "preferentially propagate attentional weight toward objects at greater depth\u2014i.e., "
    "toward Far when the cued field occupies the Near plane, and further beyond Far when the "
    "cued field is in the Far plane. This cue-locked account predicts that the Far\u202f>\u202fNear "
    "gap should be larger in the CUED arm, and possibly absent or reversed in the UNCUED arm."
)

P1_NEW = (
    "The present note evaluates an additional, non-mutually-exclusive hypothesis: "
    "the fixation plane itself functions as a persistent attentional depth anchor. "
    "In stereoscopic VR, the fixation cross is rendered at a specific virtual depth. "
    "The two dot fields flank this depth symmetrically in disparity magnitude: "
    "the Near field carries crossed disparity, the Far field carries uncrossed disparity. "
    "If attentional weight extends preferentially behind the fixation plane\u2014just as it "
    "may extend behind the cued object\u2019s plane\u2014the Far field should receive a "
    "standing attentional advantage that is present on every trial, independent of which "
    "field was cued by temporal onset. This would manifest as a Far\u202f>\u202fNear "
    "advantage in the UNCUED arm as well as the CUED arm."
)

P1_COMPAT = (
    "The two mechanisms are compatible and potentially additive. "
    "The onset-cue mechanism is trial-by-trial and cue-locked; the fixation mechanism "
    "is structural and present throughout every trial. When the Far field happens to be "
    "cued, both mechanisms favour the same field. When the Near field is cued, "
    "the onset-cue mechanism favours Near while the fixation mechanism continues to "
    "pull toward Far, creating partial opposition."
)

# ══════════════════════════════════════════════════════════════════════════════
# Page 2 — Predictions + compatibility with existing data
# ══════════════════════════════════════════════════════════════════════════════

# Table data: [prediction, cue-locked account, fixation-plane account, existing data]
PRED_TABLE = [
    # header
    ['Prediction', 'Cue-locked\naccount', 'Fixation-plane\naccount', 'Existing data'],
    # rows
    ['Far\u202f>\u202fNear in UNCUED arm',
     'No (cue absent)',
     'Yes (fixation\nbias always on)',
     'Check cell means\n\u2192 diagnostic'],
    ['Far\u202f>\u202fNear larger in CUED arm\nthan UNCUED arm',
     'Yes (cue amplifies)',
     'Partial (cue adds\nto standing bias)',
     'F1\u00d7F4 interaction\nin GLM \u2192 diagnostic'],
    ['Asymmetry grows with\ndepth separation',
     'Ambiguous',
     'Yes if bias\nis signal-driven',
     'DepthParam data\n\u2192 consistent'],
    ['Asymmetry absent\nmonocularly',
     'Yes (no disparity\nfor depth repr.)',
     'Yes (no crossed/\nuncrossed disparity)',
     'Confirmed'],
    ['Asymmetry shifts when\nfixation depth moved',
     'No (onset-cue\ndetermines plane)',
     'Yes (direction\ntracks fixation)',
     'Not yet collected'],
    ['At very short SOA,\nFar\u202f>\u202fNear persists\n(before cue matures)',
     'No (cue not yet\nestablished)',
     'Yes (fixation\nbias present from t=0)',
     'SOA experiment\npending'],
]

P2_INTERP = (
    "The critical diagnostic in existing data is the UNCUED arm. "
    "Under a purely cue-locked account, the UNCUED arm should show no Far\u202f>\u202fNear "
    "effect: without an onset cue, there is no attentional depth plane to extend from. "
    "If Far\u202f>\u202fNear is present in the UNCUED trials\u2014regardless of swap condition\u2014"
    "that is positive evidence for a standing structural bias, consistent with the fixation-plane "
    "hypothesis (or with a sensory confound; see p.\u202f3). "
    "The F1\u202f\u00d7\u202fF4 interaction term in the GLM addresses the second row of the table: "
    "if the interaction is significant and positive, the Far advantage is amplified by the onset "
    "cue, suggesting both mechanisms contribute. If F1\u202f\u00d7\u202fF4 is near zero while the "
    "F4 main effect is large, the fixation-plane account needs no additional cue-locked component."
)

# ══════════════════════════════════════════════════════════════════════════════
# Page 3 — Complications + mechanism framing
# ══════════════════════════════════════════════════════════════════════════════

P3_VERGENCE = (
    "A sensory confound must be considered before attributing the Far\u202f>\u202fNear gap to "
    "attentional depth weighting. Crossed disparity (Near) and uncrossed disparity (Far) are "
    "not perceptually symmetric. Fusional vergence is known to be faster and more accurate "
    "for small uncrossed disparities than for matched crossed disparities, particularly under "
    "sustained viewing. In VR, the vergence\u2013accommodation conflict adds further asymmetry: "
    "the display is at a fixed optical distance while vergence tracks virtual depth. "
    "Objects rendered with uncrossed disparity (Far) require less additional vergence effort "
    "relative to the resting fixation distance, and may be more stably fused. "
    "If the Far plane is simply cleaner stereoscopically, motion direction detection would "
    "be easier there without any attentional mechanism. "
    "This confound is difficult to rule out entirely, but the fact that the asymmetry "
    "\u2018grows\u2019 with depth separation\u2014rather than flattening as perceptual fusion "
    "becomes more difficult at larger disparities\u2014is at least weakly inconsistent with "
    "a simple sensory-quality account."
)

P3_PHYSIO = (
    "At the neural level, near-zero and far-tuned disparity neurons are not distributed "
    "symmetrically in early visual areas. In macaque V1 and MT, the population of "
    "far-tuned (uncrossed-disparity) cells is somewhat larger and shows higher signal-to-noise "
    "than near-tuned cells at moderate disparities. If the Far dot field drives a larger "
    "or more reliable population response in motion-sensitive areas, the downstream "
    "readout for direction discrimination would be more accurate independently of attention. "
    "This is a neural-population account rather than a vergence-comfort account, but both "
    "are sensory rather than attentional. Neither can be ruled out with the current data."
)

P3_INTERACTION = (
    "The additive structure expected if both mechanisms operate simultaneously is: "
    "CUED\u202f\u00b7\u202fFar is optimal (onset-cue + fixation bias both favour Far), "
    "CUED\u202f\u00b7\u202fNear and UNCUED\u202f\u00b7\u202fFar occupy intermediate positions "
    "(one mechanism favours, one does not), and UNCUED\u202f\u00b7\u202fNear is worst "
    "(neither mechanism favours). A purely cue-locked account with no fixation mechanism "
    "predicts UNCUED\u202f\u00b7\u202fFar\u202f\u2248\u202fUNCUED\u202f\u00b7\u202fNear "
    "(chance-level and equal). "
    "If the observed UNCUED cells show a Far advantage, that ordering directly falsifies "
    "the purely cue-locked account."
)

P3_OPPOSITE = (
    "It is also worth noting the possibility of an opposing interaction. "
    "If the fixation plane\u2019s attentional bias toward Far is strong, then when the Near "
    "field is cued by onset, the fixation mechanism actively works against the trial\u2019s "
    "informative cue. This would predict that CUED\u202f\u00b7\u202fNear should be "
    "disproportionately impaired relative to a simple additive prediction. "
    "In other words, the onset cue\u2019s benefit for Near should be smaller than its "
    "benefit for Far\u2014exactly a positive F1\u202f\u00d7\u202fF4 interaction. "
    "Checking whether the observed F1\u202f\u00d7\u202fF4 coefficient is positive, negative, "
    "or near zero is therefore the primary internal test available in the existing dataset."
)

# ══════════════════════════════════════════════════════════════════════════════
# Page 4 — Critical experiments + summary
# ══════════════════════════════════════════════════════════════════════════════

EXPTS = [
    (
        '1 — Check UNCUED Near vs. Far in existing data  [can do now]',
        'Split existing DecoupledDots and DepthColorLinked data by F4 '
        'within the UNCUED arm only. If Far\u202f>\u202fNear is present there '
        '(ideally collapsing across swap conditions to maximise n), that is the first '
        'positive evidence for a standing fixation bias. The F1\u202f\u00d7\u202fF4 '
        'interaction in the GLM provides the complementary evidence that the fixation '
        'bias and onset-cue mechanism interact.'
    ),
    (
        '2 — Fixation-depth manipulation  [new experiment]',
        'Render the fixation cross at the Near plane depth for one block and at the '
        'Far plane depth for another. Everything else (dot fields, depth separation, '
        'swap conditions) is unchanged. '
        'Fixation-plane hypothesis predicts: Far\u202f>\u202fNear advantage should '
        'weaken when fixation is moved to Far depth (the fixation plane is no longer '
        '"behind" the Far field), and possibly reverse when fixation is moved beyond '
        'Far (Far is now the "near" side of fixation). '
        'This is the cleanest test. Can be added as an extra condition within a '
        'DepthSwapCtrl session (no new experiment spec required, just a fixation '
        'depth parameter).'
    ),
    (
        '3 — SOA manipulation  [already planned]',
        'Vary the delay between Field B onset and translation onset. '
        'At very short SOAs the onset-cue attentional representation has not matured; '
        'the CUED\u202f\u00b7\u202fNear advantage should be small. '
        'But if a fixation-based Far bias is structural, the Far\u202f>\u202fNear gap '
        'in the UNCUED arm should be flat across SOA, while the CUED arm shows '
        'an SOA-dependent component. Crossing SOA with Far/Near plane would '
        'decompose the two contributions.'
    ),
    (
        '4 — Zero-disparity baseline  [already noted as needed]',
        'A no-depth session (disparity = 0 for both fields, rendered at fixation plane) '
        'would establish the flat baseline. Any Far\u202f>\u202fNear gap in the stereoscopic '
        'conditions is then attributable to the depth manipulation specifically. '
        'Without this anchor it remains ambiguous whether Far is advantaged or Near is '
        'penalised. The fixation-plane hypothesis predicts that as soon as disparity is '
        'introduced, performance splits: Far rises above baseline, Near falls below, '
        'or both. The monocular sessions are the closest available proxy for this '
        'baseline; they show the gap collapses under monocular viewing, consistent '
        'with a disparity-dependent mechanism.'
    ),
]

P4_SUMMARY = (
    "The fixation-plane hypothesis offers a parsimonious account of the Far\u202f>\u202fNear "
    "asymmetry as a standing structural bias, present on every trial and reflecting either "
    "attentional weighting toward objects behind the fixation plane, a physiological asymmetry "
    "in uncrossed-vs.-crossed disparity processing, or a vergence-comfort advantage for Far. "
    "It is compatible with\u2014and potentially additive with\u2014the onset-cue attentional "
    "plane mechanism. The key distinction is whether the asymmetry is present in the UNCUED arm "
    "(fixation or sensory) or only in the CUED arm (cue-locked). "
    "This can be checked in existing data immediately. "
    "The fixation-depth manipulation experiment would provide the cleanest causal test."
)


# ══════════════════════════════════════════════════════════════════════════════
# Rendering helpers
# ══════════════════════════════════════════════════════════════════════════════

def new_fig():
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    return fig

def render_paras(fig, x, y, paras, width=88, fontsize=9.5, lh=0.019, gap=0.018,
                 color=C_BODY):
    for para in paras:
        y = body_text(fig, x, y, para, width=width, fontsize=fontsize,
                      lh=lh, color=color)
        y -= gap
    return y

# ══════════════════════════════════════════════════════════════════════════════
# Page makers
# ══════════════════════════════════════════════════════════════════════════════

def make_p1(pdf):
    fig = new_fig()
    page_title(fig,
               'Fixation Plane as an Attentional Plane',
               'Evaluation of a second depth-attention mechanism in VRDots  \u00b7  '
               f'GS  \u00b7  {DATE_STR}')

    y = 0.875
    y = section_head(fig, 0.07, y, 'Background: the Far\u202f>\u202fNear asymmetry')
    y = body_text(fig, 0.07, y, P1_INTRO, width=90)
    y -= 0.022

    y = section_head(fig, 0.07, y, 'Prior account: the onset-cued plane as attentional anchor')
    y = body_text(fig, 0.07, y, P1_PREV, width=90)
    y -= 0.022

    y = section_head(fig, 0.07, y, 'New hypothesis: the fixation plane as attentional anchor')
    y = body_text(fig, 0.07, y, P1_NEW, width=90)
    y -= 0.022

    y = section_head(fig, 0.07, y, 'Compatibility of the two mechanisms')
    y = body_text(fig, 0.07, y, P1_COMPAT, width=90)
    y -= 0.025

    # Schematic box
    ax = fig.add_axes([0.07, 0.060, 0.86, 0.155])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_facecolor(C_HL)
    for spine in ax.spines.values(): spine.set_edgecolor(C_RULE); spine.set_linewidth(0.7)
    ax.set_xticks([]); ax.set_yticks([])

    ax.text(0.015, 0.92, 'Attentional weight schematic (depth axis, top\u202f=\u202fFar)',
            va='top', fontsize=8, color=C_DIM, fontfamily=FF_SANS, style='italic')

    rows = [
        ('Onset-cue mechanism:',
         'cue-locked  \u2192  attentional plane = cued field\u2019s depth  \u2192  weight extends behind cued field',
         C_BODY),
        ('Fixation-plane mechanism:',
         'structural  \u2192  attentional plane = fixation depth  \u2192  weight extends toward Far (every trial)',
         C_FIX),
        ('Combined (Far cued):',
         'both mechanisms favour Far  \u2192  maximum advantage',
         C_FAR),
        ('Combined (Near cued):',
         'onset-cue favours Near; fixation-plane favours Far  \u2192  partial opposition',
         C_NEAR),
    ]
    ry = 0.73
    for label, desc, col in rows:
        ax.text(0.015, ry, label, va='top', fontsize=8.5, color=col,
                fontweight='bold', fontfamily=FF_SERIF)
        ax.text(0.240, ry, desc, va='top', fontsize=8.5, color=C_BODY,
                fontfamily=FF_SERIF)
        ry -= 0.185

    footer(fig, 1, 4)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def make_p2(pdf):
    fig = new_fig()
    page_title(fig,
               'Predictions and Existing Data',
               'What each account predicts and where existing data bears on it')

    # ── Table ──────────────────────────────────────────────────────────────────
    ax = fig.add_axes([0.05, 0.520, 0.90, 0.360])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')

    col_xs  = [0.00, 0.38, 0.58, 0.79]   # left edges of 4 columns
    col_ws  = [0.38, 0.20, 0.21, 0.21]
    n_rows  = len(PRED_TABLE)
    row_h   = 1.0 / n_rows

    for ri, row in enumerate(PRED_TABLE):
        y_bot = 1.0 - (ri + 1) * row_h
        y_top = y_bot + row_h
        y_mid = (y_bot + y_top) / 2

        is_hdr = (ri == 0)
        bg = '#dce6f7' if is_hdr else ('#f0f4fb' if ri % 2 == 0 else 'white')
        rect = plt.Rectangle((0, y_bot), 1, row_h,
                              facecolor=bg, edgecolor=C_RULE, linewidth=0.5,
                              transform=ax.transAxes, clip_on=False)
        ax.add_patch(rect)

        for ci, (cell, cx, cw) in enumerate(zip(row, col_xs, col_ws)):
            fw = 'bold' if is_hdr else 'normal'
            fs = 8 if is_hdr else 8
            col_txt = C_HEAD if is_hdr else C_BODY
            # colour-code account columns
            if not is_hdr:
                if ci == 1: col_txt = '#555555'
                if ci == 2: col_txt = C_FIX
                if ci == 3: col_txt = '#7a4400'
            # multi-line: split on \n
            lines = cell.split('\n')
            n_ln  = len(lines)
            for li, ln in enumerate(lines):
                ly = y_mid + (n_ln - 1) * 0.012 - li * 0.024
                ax.text(cx + 0.010, ly, ln,
                        ha='left', va='center',
                        fontsize=fs, fontweight=fw,
                        color=col_txt, fontfamily=FF_SERIF,
                        transform=ax.transAxes)

    # column header underline
    ax.plot([0, 1], [1 - row_h, 1 - row_h],
            color=C_HEAD, lw=1.0, transform=ax.transAxes)

    fig.text(0.07, 0.873,
             'Table 1.  Predictions of the two accounts and what existing data can address.',
             ha='left', va='top', fontsize=8, color=C_DIM, style='italic',
             fontfamily=FF_SANS)
    hline(fig, 0.513)

    y = 0.495
    y = section_head(fig, 0.07, y, 'Interpretation')
    y = body_text(fig, 0.07, y, P2_INTERP, width=90)

    footer(fig, 2, 4)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def make_p3(pdf):
    fig = new_fig()
    page_title(fig,
               'Complications and Mechanism Alternatives',
               'Sensory confounds, neural-population account, interaction structure')

    y = 0.875

    y = section_head(fig, 0.07, y, '1 — Vergence-comfort confound')
    y = body_text(fig, 0.07, y, P3_VERGENCE, width=90)
    y -= 0.020

    y = section_head(fig, 0.07, y, '2 — Neural-population asymmetry (sensory, not attentional)')
    y = body_text(fig, 0.07, y, P3_PHYSIO, width=90)
    y -= 0.020

    y = section_head(fig, 0.07, y, '3 — Additive structure of the two attentional mechanisms')
    y = body_text(fig, 0.07, y, P3_INTERACTION, width=90)
    y -= 0.020

    y = section_head(fig, 0.07, y, '4 — Possible opposing interaction')
    y = body_text(fig, 0.07, y, P3_OPPOSITE, width=90)
    y -= 0.030

    # Summary box
    ax = fig.add_axes([0.07, 0.060, 0.86, 0.120])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_facecolor(C_HL)
    for spine in ax.spines.values(): spine.set_edgecolor(C_RULE); spine.set_linewidth(0.7)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.015, 0.88,
            'Internal test available now: inspect F1\u202f\u00d7\u202fF4 coefficient from '
            'existing GLM and split UNCUED arm by Far/Near.',
            va='top', fontsize=9, color=C_FIX, fontweight='bold', fontfamily=FF_SERIF)
    ax.text(0.015, 0.50,
            'Positive F4 main effect + near-zero F1\u202f\u00d7\u202fF4  \u2192  '
            'standing fixation-plane bias (or sensory confound), independent of cue.',
            va='top', fontsize=8.5, color=C_BODY, fontfamily=FF_SERIF)
    ax.text(0.015, 0.15,
            'Positive F4 main effect + positive F1\u202f\u00d7\u202fF4  \u2192  '
            'additive: fixation bias enhanced by onset cue; both mechanisms contribute.',
            va='top', fontsize=8.5, color=C_BODY, fontfamily=FF_SERIF)

    footer(fig, 3, 4)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def make_p4(pdf):
    fig = new_fig()
    page_title(fig,
               'Critical Experiments and Summary',
               'What to do next to test the fixation-plane hypothesis')

    y = 0.875
    for i, (title, desc) in enumerate(EXPTS):
        y = section_head(fig, 0.07, y, title, fontsize=10)
        y = body_text(fig, 0.07, y, desc, width=90, fontsize=9.5)
        y -= 0.020 if i < len(EXPTS) - 1 else 0.028
        if y < 0.22:
            break

    hline(fig, y - 0.010)
    y -= 0.030

    y = section_head(fig, 0.07, y, 'Summary')
    body_text(fig, 0.07, y, P4_SUMMARY, width=90)

    footer(fig, 4, 4)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    for out_path in OUT_PDFS:
        with PdfPages(out_path) as pdf:
            make_p1(pdf)
            make_p2(pdf)
            make_p3(pdf)
            make_p4(pdf)
        print(f'Saved: {out_path}')

if __name__ == '__main__':
    main()
