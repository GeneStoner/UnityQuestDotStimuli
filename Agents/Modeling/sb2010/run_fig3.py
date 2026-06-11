"""
Reproduce Fig. 3 of Stoner & Blanc (2010).

Runs the motion-competition model on the no-motion-swap delayed-onset
design for CUED and UNCUED conditions, and computes the predicted bias
in the translation detector's response. Paper reports ~21%.

Outputs
-------
- console: peak R_TD for each condition + bias percentage
- fig3_reproduction.png: 5-panel reproduction of Fig. 3 A–E

Run from this directory with Apple's Python 3.9 (which has the analysis
packages; see [[laptop-setup]] memory):

    /usr/bin/python3 run_fig3.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # headless rendering — saves PNG without a display
import matplotlib.pyplot as plt

from parameters import (
    T_END, T_TRANS_START, T_TRANS_END,
)
from stimulus import stim_field1, stim_field2, translation_input
from model import simulate_adapting_channel, translation_detector


def run_condition(condition, dt=0.5):
    """Simulate the model for one condition ('cued' or 'uncued').

    Returns (t, R_field1, R_field2, R_TD)  — all arrays sampled at dt ms.
    """
    t = np.arange(0.0, T_END + dt, dt)

    # Closures binding the chosen condition (solve_ivp passes scalar t).
    f1 = lambda tt: stim_field1(tt, condition)
    f2 = lambda tt: stim_field2(tt, condition)

    R_field1, _ = simulate_adapting_channel(f1, t)
    R_field2, _ = simulate_adapting_channel(f2, t)

    C_trans = translation_input(t)
    R_TD = translation_detector(C_trans, R_field1, R_field2)

    return t, R_field1, R_field2, R_TD


def peak_in_window(t, signal, t_start, t_end):
    """Maximum of `signal` over the half-open window [t_start, t_end)."""
    mask = (t >= t_start) & (t < t_end)
    return float(signal[mask].max())


def main():
    # --- run both conditions ------------------------------------------------
    t_c, R1_c, R2_c, RTD_c = run_condition('cued')
    t_u, R1_u, R2_u, RTD_u = run_condition('uncued')

    # --- summarize ----------------------------------------------------------
    peak_c = peak_in_window(t_c, RTD_c, T_TRANS_START, T_TRANS_END)
    peak_u = peak_in_window(t_u, RTD_u, T_TRANS_START, T_TRANS_END)
    bias_pct = (peak_c / peak_u - 1.0) * 100.0

    print("S&B 2010 Fig. 3 reproduction — motion-competition model, no-swap conditions")
    print(f"  Translation detector peak response during translation window:")
    print(f"    CUED   : {peak_c:.3f}")
    print(f"    UNCUED : {peak_u:.3f}")
    print(f"  Bias (cued / uncued - 1): {bias_pct:.1f}%")
    print(f"  Paper reports ~21%.")

    # --- plot ---------------------------------------------------------------
    fig, axes = plt.subplots(3, 2, figsize=(11, 9))

    def shade_trans(ax):
        ax.axvspan(T_TRANS_START, T_TRANS_END, color='lightgray',
                   alpha=0.5, zorder=0)

    # Panel A — CUED adapting responses
    ax = axes[0, 0]
    ax.plot(t_c, R1_c, color='#2E8B57', label='first-on')
    ax.plot(t_c, R2_c, color='#C0392B', label='delayed')
    shade_trans(ax)
    ax.set_title('A. CUED — adapting rotation responses')
    ax.set_ylabel('R (Hz)')
    ax.set_xlim(t_c[0], t_c[-1])
    ax.legend(fontsize=8, loc='upper right')

    # Panel B — UNCUED adapting responses
    ax = axes[0, 1]
    ax.plot(t_u, R1_u, color='#2E8B57', label='first-on')
    ax.plot(t_u, R2_u, color='#C0392B', label='delayed')
    shade_trans(ax)
    ax.set_title('B. UNCUED — adapting rotation responses')
    ax.set_xlim(t_u[0], t_u[-1])
    ax.legend(fontsize=8, loc='upper right')

    # Panel C — CUED translation-detector inputs
    C_trans_c = translation_input(t_c)
    ax = axes[1, 0]
    ax.plot(t_c, R1_c + R2_c, color='black', label='Inhibition (R1+R2)')
    ax.plot(t_c, C_trans_c / 4.0, color='#1F4E79', linestyle='--',
            label='Excitation (×1/4)')
    shade_trans(ax)
    ax.set_title('C. CUED — translation detector inputs')
    ax.set_ylabel('Drive')
    ax.set_xlim(t_c[0], t_c[-1])
    ax.legend(fontsize=8, loc='upper right')

    # Panel D — UNCUED translation-detector inputs
    C_trans_u = translation_input(t_u)
    ax = axes[1, 1]
    ax.plot(t_u, R1_u + R2_u, color='black', label='Inhibition (R1+R2)')
    ax.plot(t_u, C_trans_u / 4.0, color='#1F4E79', linestyle='--',
            label='Excitation (×1/4)')
    shade_trans(ax)
    ax.set_title('D. UNCUED — translation detector inputs')
    ax.set_xlim(t_u[0], t_u[-1])
    ax.legend(fontsize=8, loc='upper right')

    # Panel E — R_TD time course (both conditions)
    ax = axes[2, 0]
    ax.plot(t_c, RTD_c, color='#2E8B57', label='CUED')
    ax.plot(t_u, RTD_u, color='#C0392B', label='UNCUED')
    shade_trans(ax)
    ax.set_title('E. Translation detector response R_TD(t)')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('R_TD')
    # Zoom to the translation window plus a small margin
    ax.set_xlim(T_TRANS_START - 100, T_TRANS_END + 100)
    ax.legend(fontsize=8, loc='upper right')

    # Panel F — Bar chart of peaks (the headline result)
    ax = axes[2, 1]
    bars = ax.bar(['CUED', 'UNCUED'], [peak_c, peak_u],
                  color=['#2E8B57', '#C0392B'])
    for bar, val in zip(bars, [peak_c, peak_u]):
        ax.text(bar.get_x() + bar.get_width() / 2, val,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    ax.set_title(f'F. Peak R_TD — model bias = {bias_pct:.1f}%  '
                 f'(paper: ~21%)')
    ax.set_ylabel('Peak R_TD during translation window')

    fig.tight_layout()
    out_path = 'fig3_reproduction.png'
    fig.savefig(out_path, dpi=120)
    print(f"\n  Figure saved to: {out_path}")


if __name__ == '__main__':
    main()
