"""
Stoner & Blanc (2010) motion-competition model — core dynamics.

Stage 1: adapting rotation responses (Eqs 4-5)

    τ      · dR/dt = -R + NR( Stim(t) - W_adapt · I )
    τ_adapt · dI/dt = -I + R

  where NR(x) = NR_MAX * [x]+² / (NR_SEMISAT² + [x]+²)  is a Naka-Rushton
  sigmoid applied to the positive part of its input. R is firing rate; I
  is a slow internal variable that subtractively attenuates the drive.

Stage 2: translation detector (Eqs 1-3, divisive normalization)

    E    = W_TRANS · C_trans(t)
    I_nm = W_ROT   · R_field1(t)  +  W_ROT · R_field2(t)
    R_TD = K · E / (E + I_nm + σ)

  Note: I_nm (the *normalization* inhibition for the translation detector)
  is unrelated to the per-channel adaptation variable I above. The paper
  reuses the letter I for both; here we name them apart.
"""

import numpy as np
from scipy.integrate import solve_ivp

from parameters import (
    TAU, TAU_ADAPT, W_ADAPT,
    NR_MAX, NR_SEMISAT,
    K, SIGMA, W_TRANS, W_ROT,
)


def naka_rushton(x):
    """N(x) = NR_MAX * [x]+² / (NR_SEMISAT² + [x]+²).
    [x]+ denotes the positive part: max(x, 0).
    Works for scalars and arrays.
    """
    x_pos = np.maximum(x, 0.0)
    return NR_MAX * x_pos**2 / (NR_SEMISAT**2 + x_pos**2)


def _rhs(t, state, stimulus_func):
    """ODE right-hand side for a single adapting rotation channel.
    state = (R, I)
    stimulus_func(t) returns the channel's stimulus amplitude at time t.
    """
    R, I = state
    stim = float(stimulus_func(t))
    drive = stim - W_ADAPT * I
    dR_dt = (-R + naka_rushton(drive)) / TAU
    dI_dt = (-I + R) / TAU_ADAPT
    return [dR_dt, dI_dt]


def simulate_adapting_channel(stimulus_func, t_eval):
    """Solve Stage 1 ODE for one rotation channel over t_eval.

    Returns
    -------
    R : ndarray  — firing rate sampled at t_eval
    I : ndarray  — adaptation variable sampled at t_eval
    """
    sol = solve_ivp(
        _rhs,
        t_span=(t_eval[0], t_eval[-1]),
        y0=[0.0, 0.0],          # both channels start at rest
        t_eval=t_eval,
        args=(stimulus_func,),
        method='RK45',
        max_step=1.0,           # cap step at 1 ms so we don't skip over
                                # abrupt stimulus transitions
        rtol=1e-6,
        atol=1e-9,
    )
    if not sol.success:
        raise RuntimeError(f"ODE solver failed: {sol.message}")
    return sol.y[0], sol.y[1]


def translation_detector(C_trans, R_field1, R_field2):
    """Translation detector instantaneous response (Eq 3).

    All inputs may be scalars or arrays of the same shape.

        E    = W_TRANS · C_trans
        I_nm = W_ROT · (R_field1 + R_field2)
        R_TD = K · E / (E + I_nm + σ)
    """
    E = W_TRANS * C_trans
    I_nm = W_ROT * (R_field1 + R_field2)
    return K * E / (E + I_nm + SIGMA)
