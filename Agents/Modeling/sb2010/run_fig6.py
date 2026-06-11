"""
Reproduce the four delayed-onset conditions of Fig. 6 of Stoner & Blanc
(2010), ignoring color (the model is direction-only).

Conditions:
    A  CUED,   no swap     (delayed field translates, no direction reversal)
    C  UNCUED, no swap     (first-on field translates)
    D  CUED,   swap        (delayed field translates; non-translating field
                            reverses direction at translation onset)
    B  UNCUED, swap        (first-on translates; non-translating reverses)

(Letters above match the paper's panel labels.)

For each condition we simulate the two direction-selective adapting
channels (CW, CCW), drive the translation detector, and read off the
peak R_TD during the 40 ms translation window.

Headline prediction of the motion-competition model: the cued/uncued
bias should REVERSE with motion swap.  Specifically the inputs are
identical between (CUED, swap) and (UNCUED, no swap), and between
(UNCUED, swap) and (CUED, no swap), so the predicted R_TDs follow suit.

Headline empirical finding: no such reversal — cued > uncued in both
swap conditions.  That refutes the motion-competition account.

Run with:
    /usr/bin/python3 run_fig6.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from parameters import T_END, T_TRANS_START, T_TRANS_END
from stimulus import channels_for_trial
from model import simulate_adapting_channel, translation_detector


CONDITIONS = [
    # (label, condition, motion_swap, color)
    ("CUED\nno swap",   'cued',   False, '#2E8B57'),  # green
    ("UNCUED\nno swap", 'uncued', False, '#C0392B'),  # red
    ("CUED\nswap",      'cued',   True,  '#1F77B4'),  # blue
    ("UNCUED\nswap",    'uncued', True,  '#FF7F0E'),  # orange
]


def run_one(condition, motion_swap, dt=0.5):
    """Simulate one trial type. Returns (t, R_cw, R_ccw, R_TD)."""
    t = np.arange(0.0, T_END + dt, dt)
    stim_cw, stim_ccw, c_trans = channels_for_trial(condition, motion_swap)
    R_cw,  _ = simulate_adapting_channel(stim_cw,  t)
    R_ccw, _ = simulate_adapting_channel(stim_ccw, t)
    C = c_trans(t)
    R_TD = translation_detector(C, R_cw, R_ccw)
    return t, R_cw, R_ccw, R_TD


def peak_in_window(t, signal, t_start, t_end):
    mask = (t >= t_start) & (t < t_end)
    return float(signal[mask].max())


def main():
    results = []
    for label, condition, swap, color in CONDITIONS:
        t, R_cw, R_ccw, R_TD = run_one(condition, swap)
        peak = peak_in_window(t, R_TD, T_TRANS_START, T_TRANS_END)
        results.append({
            'label': label, 'condition': condition, 'swap': swap,
            'color': color, 't': t, 'R_cw': R_cw, 'R_ccw': R_ccw,
            'R_TD': R_TD, 'peak': peak,
        })

    # --- print summary -----------------------------------------------------
    by_key = {(r['condition'], r['swap']): r for r in results}
    p_cued_ns   = by_key[('cued',   False)]['peak']
    p_uncued_ns = by_key[('uncued', False)]['peak']
    p_cued_sw   = by_key[('cued',   True )]['peak']
    p_uncued_sw = by_key[('uncued', True )]['peak']

    bias_ns = (p_cued_ns / p_uncued_ns - 1) * 100
    bias_sw = (p_cued_sw / p_uncued_sw - 1) * 100

    print("S&B 2010 Fig. 6 reproduction — motion-competition model, four conditions")
    print("  Peak R_TD during the 40-ms translation window:")
    print(f"    A  CUED,   no swap : {p_cued_ns:6.3f}")
    print(f"    C  UNCUED, no swap : {p_uncued_ns:6.3f}")
    print(f"    D  CUED,   swap    : {p_cued_sw:6.3f}")
    print(f"    B  UNCUED, swap    : {p_uncued_sw:6.3f}")
    print()
    print(f"  Bias no-swap (cued / uncued - 1): {bias_ns:+.1f}%")
    print(f"  Bias swap    (cued / uncued - 1): {bias_sw:+.1f}%")
    print()
    print("  Model predicts a REVERSAL of the bias with motion swap.")
    print("  Data refute this: cued > uncued in both no-swap AND swap.")
    print()
    # Sanity check: input-equivalences
    print("  Input-equivalence sanity check (peaks should match):")
    print(f"    (CUED,   no swap) vs (UNCUED, swap): "
          f"{p_cued_ns:.3f} vs {p_uncued_sw:.3f}   "
          f"diff = {abs(p_cued_ns - p_uncued_sw):.4f}")
    print(f"    (UNCUED, no swap) vs (CUED,   swap): "
          f"{p_uncued_ns:.3f} vs {p_cued_sw:.3f}   "
          f"diff = {abs(p_uncued_ns - p_cued_sw):.4f}")

    # --- plot --------------------------------------------------------------
    fig = plt.figure(figsize=(12, 8.5))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.35, wspace=0.25,
                          left=0.07, right=0.97, top=0.93, bottom=0.08)

    # Panel A: R_TD time courses, zoomed to translation window region
    ax = fig.add_subplot(gs[0, :])
    for r in results:
        ax.plot(r['t'], r['R_TD'], color=r['color'], lw=1.8,
                label=r['label'].replace('\n', ' / '))
    ax.axvspan(T_TRANS_START, T_TRANS_END, color='lightgray', alpha=0.5, zorder=0)
    ax.set_xlim(T_TRANS_START - 80, T_TRANS_END + 80)
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel(r'$R_{TD}(t)$')
    ax.set_title('A. Translation detector response over the translation window',
                 loc='left', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right', ncol=2)

    # Panel B: bar chart of peaks, paired by no-swap vs swap
    ax = fig.add_subplot(gs[1, 0])
    xs = np.arange(2)
    width = 0.35
    cued_peaks   = [p_cued_ns,   p_cued_sw  ]
    uncued_peaks = [p_uncued_ns, p_uncued_sw]
    ax.bar(xs - width/2, cued_peaks,   width, color='#2E8B57', label='CUED')
    ax.bar(xs + width/2, uncued_peaks, width, color='#C0392B', label='UNCUED')
    for x, val in zip(xs - width/2, cued_peaks):
        ax.text(x, val, f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    for x, val in zip(xs + width/2, uncued_peaks):
        ax.text(x, val, f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    ax.set_xticks(xs)
    ax.set_xticklabels(['no swap', 'motion swap'])
    ax.set_ylabel('Peak ' + r'$R_{TD}$')
    ax.set_title('B. Peak R_TD — model predicts reversal',
                 loc='left', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')

    # Panel C: biases as a function of swap
    ax = fig.add_subplot(gs[1, 1])
    biases = [bias_ns, bias_sw]
    bar_colors = ['#2E8B57' if b > 0 else '#C0392B' for b in biases]
    ax.bar(['no swap', 'motion swap'], biases, color=bar_colors, width=0.5)
    for x, val in enumerate(biases):
        offs = 1.5 if val >= 0 else -3.5
        ax.text(x, val + offs, f'{val:+.1f}%', ha='center', va='center',
                fontsize=11, fontweight='bold')
    ax.axhline(0, color='black', lw=0.8)
    ax.set_ylabel('(CUED / UNCUED − 1) × 100%')
    ax.set_title('C. Cued vs uncued bias (model prediction)',
                 loc='left', fontsize=12, fontweight='bold')
    ymax = max(abs(b) for b in biases) * 1.4
    ax.set_ylim(-ymax, ymax)

    out = 'fig6_reproduction.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    print(f"\n  Figure saved to: {out}")


if __name__ == '__main__':
    main()
