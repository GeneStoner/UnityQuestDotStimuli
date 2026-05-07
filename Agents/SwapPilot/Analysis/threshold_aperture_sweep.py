"""
threshold_aperture_sweep.py
===========================
Psychometric threshold analysis for the SubfieldSwap aperture-sweep experiment.

Usage
-----
    python3 threshold_aperture_sweep.py [TSV_PATH ...]

If no paths are given, the script looks for all TSV files matching the
AperSweep experiment name pattern under /tmp/quest_pull_apersweep/.

Reads TSV files produced by the Unity CsvLogger (variable-duration sessions
that include PresentedDurMs and PresentedDurFrames columns).

For each (aperture, condition, cueing) cell it:
  1. Bins trials by presented duration (frame-quantized values).
  2. Fits a Weibull psychometric function in log-duration space.
  3. Extracts the 62.5% correct threshold T (midpoint above chance 12.5%).
  4. Computes the cueing ratio R = T_UNCUED / T_CUED (>1 means UNCUED needs
     longer duration to reach criterion → robust cueing).
  5. Plots:
       - Panel A: raw accuracy vs duration per condition × cueing (one column
         per aperture, one row per swap type).
       - Panel B: R vs aperture for each swap type (the key summary).

Output
------
    Agents/SwapPilot/Figures/threshold_aperture_sweep.png
    Agents/SwapPilot/Figures/threshold_aperture_sweep.pdf
"""

import sys
import glob
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm

# ── Config ─────────────────────────────────────────────────────────────────────
DEFAULT_GLOB = '/tmp/quest_pull_apersweep/vr_dots_session_*.tsv'

# Apertures in the sweep (radius, deg) — used for ordering and labels
APERTURES = [1.0, 1.65, 2.5, 3.5]

CONDITIONS = ['N', 'D', 'Da', 'Db']
COND_LABELS = {'N': 'N (no swap)', 'D': 'D (noise-half)',
               'Da': 'Da (coh-half)', 'Db': 'Db (full swap)'}

CUED_COL   = '#1a3a8b'
UNCUED_COL = '#884400'

# Psychometric criterion: fraction correct above chance for threshold extraction
# 8AFC chance = 0.125; criterion = 0.125 + 0.5*(1−0.125) = 0.5625
CHANCE = 1 / 8
CRITERION = CHANCE + 0.5 * (1 - CHANCE)   # = 0.5625


# ── Psychometric function (Weibull in log-duration space) ─────────────────────
def weibull(log_t, log_alpha, beta):
    """
    Weibull CDF on log10(duration) axis.
    P(correct) = chance + (1 - chance) * (1 - exp(-((t/alpha)^beta)))
    where t = 10^log_t, alpha = 10^log_alpha.
    """
    return CHANCE + (1 - CHANCE) * (1 - np.exp(-np.power(10, beta * (log_t - log_alpha))))


DUR_MIN_MS = 20.0    # shortest tested duration
DUR_MAX_MS = 350.0   # longest tested duration

def fit_weibull(durations_ms, correct):
    """
    Fit Weibull to (duration, correct) arrays.
    Returns (log10_T62, log10_alpha, beta, pcov, extrapolated) or None on failure.
    log10_T62 is the threshold at CRITERION performance.
    extrapolated=True when T falls outside the tested duration range.

    Constraints:
      log_alpha in [1.0, 2.7]  →  alpha in [10ms, 500ms]  (keeps fit anchored near data)
      beta      in [0.5, 5.0]  →  realistic psychometric slopes for duration tasks
    """
    if len(durations_ms) < 5:
        return None
    log_t = np.log10(np.asarray(durations_ms, dtype=float))
    y     = np.asarray(correct, dtype=float)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            p0   = [np.log10(np.median(durations_ms)), 1.5]
            popt, pcov = curve_fit(weibull, log_t, y, p0=p0,
                                   bounds=([1.0, 0.5], [2.7, 5.0]),
                                   maxfev=5000)
        log_alpha, beta = popt
        inner = -np.log(1 - (CRITERION - CHANCE) / (1 - CHANCE))
        log_T = log_alpha + np.log10(inner) / beta
        T_ms  = 10 ** log_T
        extrapolated = T_ms < DUR_MIN_MS or T_ms > DUR_MAX_MS
        return log_T, log_alpha, beta, pcov, extrapolated
    except Exception:
        return None


# ── Data loading ───────────────────────────────────────────────────────────────
def load_sessions(paths):
    dfs = []
    for p in paths:
        try:
            df = pd.read_csv(p, sep='\t')
            dfs.append(df)
        except Exception as e:
            print(f'  Warning: could not load {p}: {e}')
    if not dfs:
        raise RuntimeError('No sessions loaded.')
    df = pd.concat(dfs, ignore_index=True)
    df['correct'] = (df['TransDeg'] == df['RespDeg']).astype(int)
    df['err_rad'] = np.deg2rad(((df['RespDeg'] - df['TransDeg'] + 180) % 360) - 180)

    # Invert CUED/UNCUED labels for Da and Db (isCued=True in C# means always-on dots translate)
    mask = df['SwapType'].isin(['Da', 'Db'])
    df.loc[mask, 'Cond'] = df.loc[mask, 'Cond'].map({'CUED': 'UNCUED', 'UNCUED': 'CUED'})

    # Duration column: prefer PresentedDurMs if available, else fall back to
    # reconstructing from frames (TransStartFrame, TransEndFrame) and simHz.
    if 'PresentedDurMs' in df.columns:
        df['dur_ms'] = df['PresentedDurMs'].astype(float)
    elif 'TransStartFrame' in df.columns and 'TransEndFrame' in df.columns:
        # Assume 90 Hz
        df['dur_ms'] = (df['TransEndFrame'] - df['TransStartFrame']) / 90.0 * 1000.0
    else:
        raise KeyError('Cannot find duration information in TSV columns.')

    # Infer aperture from experimentName
    def parse_aperture(name):
        name = str(name)
        if 'Ap1_' in name or 'Ap1.0' in name or 'Ap10' in name:
            return 1.0
        if 'Ap165' in name or 'Ap1.65' in name or 'Ap16' in name:
            return 1.65
        if 'Ap25' in name or 'Ap2.5' in name or 'Ap2_5' in name:
            return 2.5
        if 'Ap35' in name or 'Ap3.5' in name or 'Ap3_5' in name:
            return 3.5
        # Also handle CatekExact / HighDens if mixed in
        if 'CatekExact' in name:
            return 1.65
        if 'HighDens' in name or 'Catek_' in name:
            return 3.5
        return np.nan

    df['aperture'] = df['Experiment'].apply(parse_aperture)
    n_unknown = df['aperture'].isna().sum()
    if n_unknown > 0:
        print(f'  Warning: {n_unknown} rows have unrecognised aperture from Experiment name.')
    return df


# ── Per-cell binning and fitting ───────────────────────────────────────────────
def analyse_cell(sub):
    """Given a DataFrame for one (aperture, cond, cue) cell, bin by duration and fit."""
    if len(sub) < 5:
        return None
    # Round durations to 1 ms to collapse within-frame variation
    sub = sub.copy()
    sub['dur_bin'] = sub['dur_ms'].round(0).astype(int)
    grouped = sub.groupby('dur_bin')['correct'].agg(['mean', 'count', 'sum']).reset_index()
    grouped.columns = ['dur_ms', 'p_corr', 'n', 'k']

    # Fit
    result = fit_weibull(grouped['dur_ms'].values, grouped['p_corr'].values)
    return dict(
        grouped=grouped,
        log_T=result[0] if result else np.nan,
        T_ms=10 ** result[0] if result else np.nan,
        log_alpha=result[1] if result else np.nan,
        beta=result[2] if result else np.nan,
        extrapolated=result[4] if result else True,
    )


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    # Collect TSV paths
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        paths = sorted(glob.glob(DEFAULT_GLOB))
    if not paths:
        print(f'No TSV files found. Pass paths as arguments or put files in {DEFAULT_GLOB}')
        return
    print(f'Loading {len(paths)} session(s)...')
    df = load_sessions(paths)

    present_apers = sorted(df['aperture'].dropna().unique())
    print(f'Apertures found: {present_apers}')
    print(f'Conditions found: {sorted(df["SwapType"].unique())}')
    print(f'Total trials: {len(df)}')

    # ── Fit all cells ─────────────────────────────────────────────────────────
    cells = {}
    for ap in present_apers:
        for cond in CONDITIONS:
            for cue in ['CUED', 'UNCUED']:
                sub = df[(df['aperture'] == ap) & (df['SwapType'] == cond) & (df['Cond'] == cue)]
                result = analyse_cell(sub)
                cells[(ap, cond, cue)] = result

    # ── Figure A: raw psychometric curves ─────────────────────────────────────
    n_ap   = len(present_apers)
    n_cond = len(CONDITIONS)

    figA, axsA = plt.subplots(n_cond, n_ap, figsize=(4 * n_ap, 3.5 * n_cond),
                              sharey=True, sharex=False)
    figA.patch.set_facecolor('#f7f7f7')
    if n_cond == 1: axsA = axsA[np.newaxis, :]
    if n_ap   == 1: axsA = axsA[:, np.newaxis]

    t_fine = np.logspace(np.log10(15), np.log10(420), 200)

    for ci, cond in enumerate(CONDITIONS):
        for ai, ap in enumerate(present_apers):
            ax = axsA[ci, ai]
            ax.set_facecolor('white')
            ax.axhline(CHANCE,     color='gray', ls=':', lw=0.8, alpha=0.5)
            ax.axhline(CRITERION,  color='gray', ls='--', lw=0.8, alpha=0.5)

            for cue, col in [('CUED', CUED_COL), ('UNCUED', UNCUED_COL)]:
                r = cells.get((ap, cond, cue))
                if r is None:
                    continue
                g = r['grouped']
                ax.scatter(g['dur_ms'], g['p_corr'], s=g['n'] * 1.2,
                           color=col, alpha=0.8, zorder=3,
                           label=f'{cue} (n={g["n"].sum()})')
                if not np.isnan(r['log_T']):
                    y_fit = weibull(np.log10(t_fine), r['log_alpha'], r['beta'])
                    ax.plot(t_fine, y_fit, color=col, lw=1.8)
                    # Extrapolated thresholds shown dashed+hollow; in-range shown solid
                    extrap = r.get('extrapolated', False)
                    ax.axvline(r['T_ms'], color=col,
                               ls=':' if extrap else '--', lw=1.2, alpha=0.6)

            ax.set_xscale('log')
            ax.set_ylim(0, 1.02)
            ax.set_xlim(15, 420)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if ci == 0:
                ax.set_title(f'{ap}° aperture', fontsize=9, fontweight='bold')
            if ai == 0:
                ax.set_ylabel(COND_LABELS[cond], fontsize=8)
            if ci == n_cond - 1:
                ax.set_xlabel('Duration (ms)', fontsize=8)
            if ci == 0 and ai == 0:
                ax.legend(fontsize=6, loc='upper left')

    figA.suptitle('SubfieldSwap Aperture Sweep — Psychometric curves\n'
                  'Dashed vertical = threshold T₀.₅₆; dashed horizontal = chance (12.5%) and criterion (56.25%)',
                  fontsize=10, fontweight='bold')
    figA.tight_layout(rect=[0, 0, 1, 0.95])

    # ── Figure B: cueing ratio R = T_UNCUED / T_CUED vs aperture ─────────────
    figB, axB = plt.subplots(1, 1, figsize=(7, 5))
    figB.patch.set_facecolor('#f7f7f7')
    axB.set_facecolor('white')

    COND_COLORS = {'N': '#333333', 'D': '#1a6e1a', 'Da': '#c03000', 'Db': '#8800aa'}
    COND_MARKERS = {'N': 'o', 'D': 's', 'Da': '^', 'Db': 'D'}

    for cond in CONDITIONS:
        xs, ys, extrap_flags = [], [], []
        for ap in present_apers:
            rc = cells.get((ap, cond, 'CUED'))
            ru = cells.get((ap, cond, 'UNCUED'))
            if rc is None or ru is None: continue
            Tc = rc.get('T_ms', np.nan)
            Tu = ru.get('T_ms', np.nan)
            if np.isnan(Tc) or np.isnan(Tu) or Tc <= 0: continue
            R = Tu / Tc
            xs.append(ap)
            ys.append(R)
            extrap_flags.append(rc.get('extrapolated', False) or ru.get('extrapolated', False))
        if xs:
            axB.plot(xs, ys, '-', color=COND_COLORS[cond], lw=2,
                     label=COND_LABELS[cond])
            for xi, yi, ex in zip(xs, ys, extrap_flags):
                marker = 'x' if ex else COND_MARKERS[cond]
                ms     = 10  if ex else 8
                axB.plot(xi, yi, marker=marker, color=COND_COLORS[cond],
                         ms=ms, mew=2 if ex else 1.5)

    axB.axhline(1.0, color='gray', ls='--', lw=1.2, alpha=0.7,
                label='R=1 (no cueing advantage)')
    axB.set_xlabel('Aperture radius (°)', fontsize=11)
    axB.set_ylabel('Cueing ratio  R = T_UNCUED / T_CUED', fontsize=11)
    axB.set_title('Cueing ratio vs aperture (R>1 → cueing advantage)\n'
                  'Criterion = 56.25% correct (midpoint above 12.5% chance)',
                  fontsize=10, fontweight='bold')
    axB.legend(fontsize=9)
    axB.set_xticks(APERTURES)
    axB.set_xticklabels([f'{a}°' for a in APERTURES])
    axB.spines['top'].set_visible(False)
    axB.spines['right'].set_visible(False)
    figB.tight_layout()

    # ── Console table ─────────────────────────────────────────────────────────
    print(f'\n{"Aperture":>10}  {"Cond":>5}  {"T_CUED_ms":>11}  {"T_UNCUED_ms":>13}  {"R=Tu/Tc":>10}  note')
    print('-' * 72)
    for ap in present_apers:
        for cond in CONDITIONS:
            rc = cells.get((ap, cond, 'CUED'))
            ru = cells.get((ap, cond, 'UNCUED'))
            Tc = rc.get('T_ms', np.nan) if rc else np.nan
            Tu = ru.get('T_ms', np.nan) if ru else np.nan
            R  = Tu / Tc if (not np.isnan(Tc) and not np.isnan(Tu) and Tc > 0) else np.nan
            ex_c = rc.get('extrapolated', False) if rc else False
            ex_u = ru.get('extrapolated', False) if ru else False
            note = ('*extrap-C' if ex_c else '') + ('  *extrap-U' if ex_u else '')
            print(f'{ap:>10.2f}°  {cond:>5}  {Tc:>11.1f}  {Tu:>13.1f}  {R:>10.3f}  {note}')

    # ── Save ──────────────────────────────────────────────────────────────────
    BASE = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/'
    out_A = BASE + 'threshold_aperture_sweep_curves.png'
    out_B = BASE + 'threshold_aperture_sweep_ratio.png'
    figA.savefig(out_A, dpi=160, bbox_inches='tight')
    figA.savefig(out_A.replace('.png', '.pdf'), bbox_inches='tight')
    figB.savefig(out_B, dpi=160, bbox_inches='tight')
    figB.savefig(out_B.replace('.png', '.pdf'), bbox_inches='tight')
    print(f'\nSaved:\n  {out_A}\n  {out_B}')


if __name__ == '__main__':
    main()
