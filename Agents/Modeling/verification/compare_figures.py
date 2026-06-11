"""
Reproduce every R&H 2009 figure-reproduction scenario in Python (using
port_attention_model.py) and diff against the MATLAB ground truth
exported by export_figures.m.

Run from this directory:
    /usr/bin/python3 compare_figures.py

Prints a one-line PASS/FAIL summary per figure plus the max abs and
max rel differences.
"""

import csv
import os
import sys

import numpy as np

from port_attention_model import attention_model, make_gaussian


# ---------------------------------------------------------------------------
# Shared sampling
# ---------------------------------------------------------------------------

X     = np.arange(-200, 201, dtype=float)
THETA = np.arange(-180, 181, dtype=float)

N_CONTRASTS    = 9   # matches numContrasts in MATLAB
N_ORIENTATIONS = 9   # matches numOrientations in MATLAB


def _outer_gauss(theta_center, x_center, theta_width, x_width):
    """makeGaussian(theta, θc, σθ, 1) * makeGaussian(x, xc, σx, 1)"""
    return (make_gaussian(THETA, theta_center, theta_width, height=1)[:, None] *
            make_gaussian(X,     x_center,     x_width,     height=1)[None, :])


def _logspace_contrasts(c_lo, c_hi, n):
    return 10.0 ** np.linspace(np.log10(c_lo), np.log10(c_hi), n)


def _idx_theta(value):
    return int(np.where(THETA == value)[0][0])


def _idx_x(value):
    return int(np.where(X == value)[0][0])


# ---------------------------------------------------------------------------
# Per-figure runners
# ---------------------------------------------------------------------------

def run_figure2A():
    stim_width, AxWidth = 3, 30
    c_range = (1e-5, 1)
    s1 = _outer_gauss(0, 100, 1, stim_width)
    s2 = _outer_gauss(0, -100, 1, stim_width)
    contrasts = _logspace_contrasts(*c_range, N_CONTRASTS)
    j, i = _idx_theta(0), _idx_x(100)
    att = np.zeros(N_CONTRASTS); unatt = np.zeros(N_CONTRASTS)
    for k, c in enumerate(contrasts):
        stim = c * s1 + c * s2
        R1 = attention_model(X, THETA, stim, Ax=100, AxWidth=AxWidth)
        R2 = attention_model(X, THETA, stim, Ax=-100, AxWidth=AxWidth)
        att[k]   = R1[j, i]
        unatt[k] = R2[j, i]
    return contrasts, unatt, att


def run_figure2B():
    stim_width, AxWidth = 5, 3
    c_range = (1e-5, 1)
    s1 = _outer_gauss(0, 100, 1, stim_width)
    s2 = _outer_gauss(0, -100, 1, stim_width)
    contrasts = _logspace_contrasts(*c_range, N_CONTRASTS)
    j, i = _idx_theta(0), _idx_x(100)
    att = np.zeros(N_CONTRASTS); unatt = np.zeros(N_CONTRASTS)
    for k, c in enumerate(contrasts):
        stim = c * s1 + c * s2
        R1 = attention_model(X, THETA, stim, Ax=100, AxWidth=AxWidth)
        R2 = attention_model(X, THETA, stim, Ax=-100, AxWidth=AxWidth)
        att[k]   = R1[j, i]
        unatt[k] = R2[j, i]
    return contrasts, unatt, att


def run_figure3C():
    stim_width, AxWidth = 5, 30
    baselineMod, baselineUnmod = 5e-7, 5
    c_range = (1e-5, 1)
    s1 = _outer_gauss(0, 100, 1, stim_width)
    s2 = _outer_gauss(0, -100, 1, stim_width)
    contrasts = _logspace_contrasts(*c_range, N_CONTRASTS)
    j, i = _idx_theta(0), _idx_x(100)
    att = np.zeros(N_CONTRASTS); unatt = np.zeros(N_CONTRASTS)
    for k, c in enumerate(contrasts):
        stim = c * s1 + c * s2
        R1 = attention_model(X, THETA, stim, Ax=100, AxWidth=AxWidth,
                             baselineMod=baselineMod, baselineUnmod=baselineUnmod)
        R2 = attention_model(X, THETA, stim, Ax=-100, AxWidth=AxWidth,
                             baselineMod=baselineMod, baselineUnmod=baselineUnmod)
        att[k]   = R1[j, i]
        unatt[k] = R2[j, i]
    return contrasts, unatt, att


def run_figure3F():
    stim_width, AxWidth = 7, 7
    baselineMod, baselineUnmod = 5e-7, 0
    c_range = (1e-5, 1)
    s1 = _outer_gauss(0, 100, 1, stim_width)
    s2 = _outer_gauss(0, -100, 1, stim_width)
    contrasts = _logspace_contrasts(*c_range, N_CONTRASTS)
    j, i = _idx_theta(0), _idx_x(100)
    att = np.zeros(N_CONTRASTS); unatt = np.zeros(N_CONTRASTS)
    for k, c in enumerate(contrasts):
        stim = c * s1 + c * s2
        R1 = attention_model(X, THETA, stim, Ax=100, AxWidth=AxWidth,
                             baselineMod=baselineMod, baselineUnmod=baselineUnmod)
        R2 = attention_model(X, THETA, stim, Ax=-100, AxWidth=AxWidth,
                             baselineMod=baselineMod, baselineUnmod=baselineUnmod)
        att[k]   = R1[j, i]
        unatt[k] = R2[j, i]
    return contrasts, unatt, att


def run_figure4C():
    stim_width, AxWidth, AthetaWidth, Apeak = 5, 5, 20, 5
    c_range = (1e-4, 0.1)
    s1 = _outer_gauss(0,    90, 1, stim_width)
    s2 = _outer_gauss(180, 110, 1, stim_width)
    s3 = _outer_gauss(0,   -90, 1, stim_width)
    s4 = _outer_gauss(180,-110, 1, stim_width)
    contrasts = _logspace_contrasts(*c_range, N_CONTRASTS)
    RF_center = int(round(np.mean([90, 110])))
    j, i = _idx_theta(0), _idx_x(RF_center)
    fixed = 0.01
    att = np.zeros(N_CONTRASTS); unatt = np.zeros(N_CONTRASTS)
    for k, c in enumerate(contrasts):
        stim = c * s1 + fixed * s2 + c * s3 + fixed * s4
        R1 = attention_model(X, THETA, stim, Apeak=Apeak,
                             Ax=110, AxWidth=AxWidth,
                             Atheta=180, AthetaWidth=AthetaWidth)
        R2 = attention_model(X, THETA, stim, Apeak=Apeak,
                             Ax=-110, AxWidth=AxWidth,
                             Atheta=180, AthetaWidth=AthetaWidth)
        att[k]   = R1[j, i]
        unatt[k] = R2[j, i]
    return contrasts, unatt, att


def run_figure4E():
    stim_width, AxWidth, AthetaWidth, Apeak = 5, 5, 20, 5
    c_range = (1e-4, 0.1)
    s1 = _outer_gauss(0,    90, 1, stim_width)
    s2 = _outer_gauss(180, 110, 1, stim_width)
    s3 = _outer_gauss(0,   -90, 1, stim_width)
    s4 = _outer_gauss(180,-110, 1, stim_width)
    contrasts = _logspace_contrasts(*c_range, N_CONTRASTS)
    RF_center = int(round(np.mean([90, 110])))
    j, i = _idx_theta(0), _idx_x(RF_center)
    att = np.zeros(N_CONTRASTS); unatt = np.zeros(N_CONTRASTS)
    for k, c in enumerate(contrasts):
        stim = c * s1 + c * s2 + c * s3 + c * s4
        # Att preferred in RF (stim1)
        R1 = attention_model(X, THETA, stim, Apeak=Apeak,
                             Ax=90, AxWidth=AxWidth,
                             Atheta=0, AthetaWidth=AthetaWidth)
        # Att null in RF (stim2)
        R2 = attention_model(X, THETA, stim, Apeak=Apeak,
                             Ax=110, AxWidth=AxWidth,
                             Atheta=180, AthetaWidth=AthetaWidth)
        att[k]   = R1[j, i]
        unatt[k] = R2[j, i]
    return contrasts, unatt, att


def run_figure5C():
    stim_width, AxWidth = 10, 10
    s1 = _outer_gauss(0, 100, 1, stim_width)
    s2 = _outer_gauss(0, -100, 1, stim_width)
    # The MATLAB code reads: stim = contrast * stim1 * contrast + stim2
    # with contrast=1, so it's just s1 + s2
    stim = s1 + s2
    R1 = attention_model(X, THETA, stim, Ax=100, AxWidth=AxWidth)
    R2 = attention_model(X, THETA, stim, Ax=-100, AxWidth=AxWidth)
    i = _idx_x(100)
    att  = R1[:, i]
    unatt = R2[:, i]
    return THETA.copy(), unatt, att


def run_figure6C():
    stim_width, AxWidth, AthetaWidth = 10, 30, 60
    s1 = _outer_gauss(0, 100, 1, stim_width)
    s2 = _outer_gauss(0, -100, 1, stim_width)
    stim = s1 + s2
    # Attend to fixation: Ax=0, no Atheta
    R1 = attention_model(X, THETA, stim, Ax=0, AxWidth=AxWidth)
    # Attend stim 2 with cross-shape attention
    R2 = attention_model(X, THETA, stim, Ashape='cross',
                         Ax=-100, AxWidth=AxWidth,
                         Atheta=0, AthetaWidth=AthetaWidth)
    i = _idx_x(100)
    att  = R1[:, i]
    unatt = R2[:, i]
    return THETA.copy(), unatt, att


def run_figure7C():
    stim_width, AxWidth, AthetaWidth, Apeak = 5, 5, 45, 5
    stim_c1, stim_c2 = 93, 107
    att_away_loc = -100
    RF_center = int(round(np.mean([stim_c1, stim_c2])))

    j = _idx_theta(0)
    i = _idx_x(RF_center)

    orientations = np.linspace(-180, 180, N_ORIENTATIONS)
    pair_att_vars, pair_att_nulls, pair_att_aways = [], [], []
    Var_att_vars, Null_att_nulls, Var_att_aways  = [], [], []

    for ori1 in orientations:
        ori2 = 180.0
        s1 = _outer_gauss(ori1, stim_c1, 1, stim_width)
        s2 = _outer_gauss(ori2, stim_c2, 1, stim_width)
        pair = s1 + s2

        Rpair_var = attention_model(X, THETA, pair, Apeak=Apeak,
                                    Ax=stim_c1, AxWidth=AxWidth,
                                    Atheta=ori1, AthetaWidth=AthetaWidth)
        Rpair_null = attention_model(X, THETA, pair, Apeak=Apeak,
                                     Ax=stim_c2, AxWidth=AxWidth,
                                     Atheta=ori2, AthetaWidth=AthetaWidth)
        Rpair_away = attention_model(X, THETA, pair, Apeak=Apeak,
                                     Ax=att_away_loc, AxWidth=AxWidth,
                                     Atheta=np.nan)
        Rvar_var = attention_model(X, THETA, s1, Apeak=Apeak,
                                   Ax=stim_c1, AxWidth=AxWidth,
                                   Atheta=ori1, AthetaWidth=AthetaWidth)
        Rnull_null = attention_model(X, THETA, s2, Apeak=Apeak,
                                     Ax=stim_c2, AxWidth=AxWidth,
                                     Atheta=ori2, AthetaWidth=AthetaWidth)
        Rvar_away = attention_model(X, THETA, s1, Apeak=Apeak,
                                    Ax=att_away_loc, AxWidth=AxWidth,
                                    Atheta=np.nan)

        pair_att_vars.append(Rpair_var[j, i])
        pair_att_nulls.append(Rpair_null[j, i])
        pair_att_aways.append(Rpair_away[j, i])
        Var_att_vars.append(Rvar_var[j, i])
        Null_att_nulls.append(Rnull_null[j, i])
        Var_att_aways.append(Rvar_away[j, i])

    return (orientations,
            np.array(pair_att_vars),  np.array(pair_att_nulls),
            np.array(pair_att_aways), np.array(Var_att_vars),
            np.array(Null_att_nulls), np.array(Var_att_aways))


# ---------------------------------------------------------------------------
# CSV I/O and comparison helpers
# ---------------------------------------------------------------------------

def _load_csv(path):
    """Returns column name → numpy array."""
    cols = {}
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k, v in row.items():
                cols.setdefault(k, []).append(float(v))
    return {k: np.array(v) for k, v in cols.items()}


def _diff(py_arr, mat_arr):
    abs_diff = py_arr - mat_arr
    with np.errstate(divide='ignore', invalid='ignore'):
        rel_diff = abs_diff / mat_arr
        rel_diff = np.where(np.isfinite(rel_diff), rel_diff, 0.0)
    return float(np.max(np.abs(abs_diff))), float(np.max(np.abs(rel_diff)))


def _verdict(max_rel, tol=1e-10):
    return 'PASS' if max_rel < tol else 'FAIL'


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

# Each entry: figure label, Python runner, MATLAB CSV path,
# list of (label, py-array, matlab-column-name)
def crf_entry(label, runner, csv_name):
    def make():
        contrasts, unatt, att = runner()
        mat = _load_csv(csv_name)
        return [
            ('contrast', contrasts, mat['contrast']),
            ('unattCRF', unatt,     mat['unattCRF']),
            ('attCRF',   att,       mat['attCRF']),
        ]
    return label, make, csv_name


def tc_entry(label, runner, csv_name):
    def make():
        theta, unatt, att = runner()
        mat = _load_csv(csv_name)
        return [
            ('theta',    theta, mat['theta']),
            ('unattCRF', unatt, mat['unattCRF']),
            ('attCRF',   att,   mat['attCRF']),
        ]
    return label, make, csv_name


def f7c_entry():
    def make():
        ori, pv, pn, pa, vv, nn, va = run_figure7C()
        mat = _load_csv('figure7c_matlab.csv')
        return [
            ('orientation',   ori, mat['orientation']),
            ('pair_att_var',  pv,  mat['pair_att_var']),
            ('pair_att_null', pn,  mat['pair_att_null']),
            ('pair_att_away', pa,  mat['pair_att_away']),
            ('Var_att_var',   vv,  mat['Var_att_var']),
            ('Null_att_null', nn,  mat['Null_att_null']),
            ('Var_att_away',  va,  mat['Var_att_away']),
        ]
    return 'Figure 7C', make, 'figure7c_matlab.csv'


ENTRIES = [
    crf_entry('Figure 2A', run_figure2A, 'figure2a_matlab.csv'),
    crf_entry('Figure 2B', run_figure2B, 'figure2b_matlab.csv'),
    crf_entry('Figure 3C', run_figure3C, 'figure3c_matlab.csv'),
    crf_entry('Figure 3F', run_figure3F, 'figure3f_matlab.csv'),
    crf_entry('Figure 4C', run_figure4C, 'figure4c_matlab.csv'),
    crf_entry('Figure 4E', run_figure4E, 'figure4e_matlab.csv'),
    tc_entry ('Figure 5C', run_figure5C, 'figure5c_matlab.csv'),
    tc_entry ('Figure 6C', run_figure6C, 'figure6c_matlab.csv'),
    f7c_entry(),
]


def main():
    print(f'\n{"figure":<12s}  {"array":<16s}  '
          f'{"max abs":>14s}  {"max rel":>14s}   verdict')
    print('-' * 78)
    overall = 'PASS'
    for label, builder, csv_path in ENTRIES:
        if not os.path.exists(csv_path):
            print(f'{label:<12s}  (no {csv_path} — skipping)')
            overall = 'FAIL'
            continue
        diffs = builder()
        figure_verdict = 'PASS'
        for col, py, mat in diffs:
            ma, mr = _diff(py, mat)
            v = _verdict(mr)
            if v == 'FAIL':
                figure_verdict = 'FAIL'
                overall = 'FAIL'
            print(f'{label:<12s}  {col:<16s}  {ma:14.4e}  {mr:14.4e}     {v}')
        print(f'{"":<12s}  {"":<16s}  {"":>14s}  {"":>14s}   '
              f'-> {figure_verdict}')
        print()
    print('=' * 78)
    print(f'OVERALL: {overall}')
    return 0 if overall == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
