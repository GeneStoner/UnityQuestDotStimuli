"""
Reproduce R&H 2009 Figure 4C in Python using the faithful port of
attentionModel.m, then compare against the MATLAB ground truth
exported by export_figure4c.m.

The Figure4C.m scenario (Martinez-Trujillo & Treue 2002):

    Two stimuli inside the RF:
        stim1 at x = 90,  θ = 0   (preferred orientation, swept contrast)
        stim2 at x = 110, θ = 180 (null orientation,      fixed contrast 0.01)
    Two stimuli contralateral to the RF:
        stim3 at x = -90, θ = 0   (preferred,             swept contrast)
        stim4 at x = -110, θ = 180 (null,                 fixed contrast 0.01)

    Neuron of interest: RF centered at x = 100, prefers θ = 0.

    Two attention conditions, both attending the null orientation:
        Att RF   : Ax = +110 (attending the null stim inside  the RF)
        Att Away : Ax = -110 (attending the null stim contralateral to the RF)

    Sweep contrast of the preferred-orientation stimuli (logarithmic,
    [1e-4 .. 0.1], 9 points).

Run from this directory:
    /usr/bin/python3 compare_figure4c.py
"""

import csv
import os

import numpy as np

from port_attention_model import attention_model, make_gaussian


# --------------------------------------------------------------------------
# Figure 4C parameters, verbatim from Figure4C.m
# --------------------------------------------------------------------------

STIM_WIDTH    = 5
AX_WIDTH      = 5
ATHETA_WIDTH  = 20
A_PEAK        = 5
C_RANGE       = (1e-4, 0.1)
N_CONTRASTS   = 9                # matches numContrasts = 9 in MATLAB

X     = np.arange(-200, 201, dtype=float)            # 401 points
THETA = np.arange(-180, 181, dtype=float)            # 361 points

STIM_CENTER1, STIM_ORI1 =  90.0,   0.0    # in-RF, preferred ori, swept
STIM_CENTER2, STIM_ORI2 = 110.0, 180.0    # in-RF, null,           fixed contrast
STIM_CENTER3, STIM_ORI3 = -90.0,   0.0    # contralateral, preferred, swept
STIM_CENTER4, STIM_ORI4 = -110.0, 180.0   # contralateral, null,    fixed contrast

FIXED_CONTRAST = 0.01

RF_CENTER = int(round(np.mean([STIM_CENTER1, STIM_CENTER2])))   # = 100


def _stim_component(orientation, center):
    """One Gaussian-times-Gaussian stimulus component (peak-height = 1)."""
    return (make_gaussian(THETA, orientation, 1.0, height=1.0)[:, None] *
            make_gaussian(X, center, STIM_WIDTH, height=1.0)[None, :])


def run_figure4c():
    """Reproduce Figure4C: returns (contrasts, unattCRF, attCRF) arrays."""
    stim1 = _stim_component(STIM_ORI1, STIM_CENTER1)
    stim2 = _stim_component(STIM_ORI2, STIM_CENTER2)
    stim3 = _stim_component(STIM_ORI3, STIM_CENTER3)
    stim4 = _stim_component(STIM_ORI4, STIM_CENTER4)

    log_range = np.log10(C_RANGE)
    contrasts = 10.0 ** np.linspace(log_range[0], log_range[1], N_CONTRASTS)

    # Index of the model neuron we read out
    j = int(np.where(THETA == STIM_ORI1)[0][0])   # θ = 0
    i = int(np.where(X == RF_CENTER)[0][0])       # x = 100

    attCRF   = np.zeros(N_CONTRASTS)
    unattCRF = np.zeros(N_CONTRASTS)

    for k, c in enumerate(contrasts):
        # Total stimulus: swept-contrast preferred + fixed-contrast null,
        # both in-RF and contralateral.
        stim = (c * stim1 + FIXED_CONTRAST * stim2
                + c * stim3 + FIXED_CONTRAST * stim4)

        # Att RF: attending null stim inside the RF
        R_attRF = attention_model(
            X, THETA, stim,
            Apeak=A_PEAK,
            Ax=STIM_CENTER2, AxWidth=AX_WIDTH,
            Atheta=STIM_ORI2, AthetaWidth=ATHETA_WIDTH,
        )

        # Att Away: attending the contralateral null stim
        R_attAway = attention_model(
            X, THETA, stim,
            Apeak=A_PEAK,
            Ax=STIM_CENTER4, AxWidth=AX_WIDTH,
            Atheta=STIM_ORI2, AthetaWidth=ATHETA_WIDTH,
        )

        attCRF[k]   = R_attRF[j, i]
        unattCRF[k] = R_attAway[j, i]

    return contrasts, unattCRF, attCRF


def _save_csv(path, contrasts, unattCRF, attCRF):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['contrast', 'unattCRF', 'attCRF'])
        for c, u, a in zip(contrasts, unattCRF, attCRF):
            w.writerow([f'{c:.10e}', f'{u:.10e}', f'{a:.10e}'])


def _load_csv(path):
    """Returns three np.arrays: contrast, unattCRF, attCRF."""
    contrasts = []; unatt = []; att = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contrasts.append(float(row['contrast']))
            unatt.append(float(row['unattCRF']))
            att.append(float(row['attCRF']))
    return np.array(contrasts), np.array(unatt), np.array(att)


def _print_table(label, c, u, a):
    print(f'\n  {label}')
    print(f'  {"contrast":>11s}  {"unattCRF":>12s}  {"attCRF":>12s}  '
          f'{"mod(%)":>8s}')
    for ci, ui, ai in zip(c, u, a):
        mod = 100.0 * (ui - ai) / ui if ui != 0 else float('nan')
        print(f'  {ci:11.4e}  {ui:12.6f}  {ai:12.6f}  {mod:8.2f}')


def main():
    print('Python port of attentionModel.m — running Figure 4C scenario')
    contrasts_py, unatt_py, att_py = run_figure4c()
    py_csv = 'figure4c_python.csv'
    _save_csv(py_csv, contrasts_py, unatt_py, att_py)
    _print_table('Python output:', contrasts_py, unatt_py, att_py)

    matlab_csv = 'figure4c_matlab.csv'
    if not os.path.exists(matlab_csv):
        print(f'\n  (no {matlab_csv} yet — run export_figure4c.m in MATLAB '
              f'to generate the reference, then re-run this script)')
        return

    contrasts_m, unatt_m, att_m = _load_csv(matlab_csv)
    _print_table('MATLAB reference:', contrasts_m, unatt_m, att_m)

    # Diff
    print('\n  Python − MATLAB:')
    print(f'  {"contrast":>11s}  '
          f'{"Δ unattCRF":>14s}  {"Δ attCRF":>14s}  '
          f'{"|rel| unatt":>12s}  {"|rel| att":>12s}')
    for ci, du, dut, da, dat in zip(
            contrasts_py,
            unatt_py - unatt_m,
            unatt_m,
            att_py   - att_m,
            att_m,
            ):
        ru = abs(du / dut) if dut != 0 else float('nan')
        ra = abs(da / dat) if dat != 0 else float('nan')
        print(f'  {ci:11.4e}  {du:14.6e}  {da:14.6e}  '
              f'{ru:12.2e}  {ra:12.2e}')

    max_abs_unatt = float(np.max(np.abs(unatt_py - unatt_m)))
    max_abs_att   = float(np.max(np.abs(att_py - att_m)))
    max_rel_unatt = float(np.max(np.abs((unatt_py - unatt_m) / unatt_m)))
    max_rel_att   = float(np.max(np.abs((att_py - att_m) / att_m)))
    print()
    print(f'  max |abs diff|: unatt = {max_abs_unatt:.4e}, '
          f'att = {max_abs_att:.4e}')
    print(f'  max |rel diff|: unatt = {max_rel_unatt:.4e}, '
          f'att = {max_rel_att:.4e}')


if __name__ == '__main__':
    main()
