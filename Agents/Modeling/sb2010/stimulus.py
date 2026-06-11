"""
Time courses of stimulus inputs for Stoner & Blanc (2010) — Mode 1
(binary amplitudes).  Covers both the no-motion-swap and motion-swap
conditions of Experiment 1.

The model has two direction-selective adapting channels: CW and CCW.
At each moment, each channel's input is binary: STIM_ROTATION if any
field is currently rotating in its preferred direction, else 0.

Trial types (ignoring color and the common-onset neutral control):

    (cued,   no swap):   delayed field (field 2) translates; non-translating
                         field continues its original direction
    (uncued, no swap):   first-on field (field 1) translates; same convention
    (cued,   swap):      same translation, but the non-translating field
                         reverses direction at translation onset and stays
                         reversed; the translating field, after translation,
                         assumes the OTHER field's pre-translation direction
    (uncued, swap):      mirror of the above

In Mode 1 (binary), the direction-channel inputs depend ONLY on which
channel has its 40-ms "gap" during the translation window.  Working out
each case (see Fig. 4 of the paper):

    (cued,   no swap)  ->  CCW gap, CW continuous
    (uncued, no swap)  ->  CW  gap, CCW continuous
    (cued,   swap)     ->  CW  gap, CCW continuous   <- same as (uncued, no swap)
    (uncued, swap)     ->  CCW gap, CW continuous    <- same as (cued, no swap)

That equivalence is the entire point of the experiment: the motion-
competition model can't tell the two "same" trial types apart, so it
predicts that motion swaps fully reverse the cued/uncued performance
bias.  The data refute that prediction.
"""

import numpy as np

from parameters import (
    STIM_ROTATION, STIM_TRANSLATION,
    T_FIELD2_ON, T_TRANS_START, T_TRANS_END,
)


# ----------------------------------------------------------------------
# Direction-channel inputs (the model's actual inputs)
# ----------------------------------------------------------------------

def channels_have_gap(condition, motion_swap=False):
    """Returns (cw_has_gap, ccw_has_gap) for the trial type.

    True means the channel's stimulus drops to 0 during the 40-ms
    translation window.
    """
    if condition not in ('cued', 'uncued'):
        raise ValueError(
            f"condition must be 'cued' or 'uncued', got {condition!r}"
        )
    # Table from the module docstring.
    if condition == 'cued'   and not motion_swap: return False, True
    if condition == 'uncued' and not motion_swap: return True,  False
    if condition == 'cued'   and     motion_swap: return True,  False
    if condition == 'uncued' and     motion_swap: return False, True


def channels_for_trial(condition, motion_swap=False):
    """Build callable (stim_cw, stim_ccw, c_trans) for the trial.

    All three are scalar-in/scalar-out callables suitable for solve_ivp.
    They also accept numpy arrays elementwise (useful for plotting).
    """
    cw_gap, ccw_gap = channels_have_gap(condition, motion_swap)

    def stim_cw(t):
        t = np.asarray(t, dtype=float)
        on = np.where(t >= 0.0, STIM_ROTATION, 0.0)
        if cw_gap:
            on = np.where(
                (t >= T_TRANS_START) & (t < T_TRANS_END),
                0.0, on,
            )
        return float(on) if on.ndim == 0 else on

    def stim_ccw(t):
        t = np.asarray(t, dtype=float)
        on = np.where(t >= T_FIELD2_ON, STIM_ROTATION, 0.0)
        if ccw_gap:
            on = np.where(
                (t >= T_TRANS_START) & (t < T_TRANS_END),
                0.0, on,
            )
        return float(on) if on.ndim == 0 else on

    def c_trans(t):
        t = np.asarray(t, dtype=float)
        val = np.where(
            (t >= T_TRANS_START) & (t < T_TRANS_END),
            STIM_TRANSLATION, 0.0,
        )
        return float(val) if val.ndim == 0 else val

    return stim_cw, stim_ccw, c_trans


# ----------------------------------------------------------------------
# Backwards-compat shims for the original run_fig3.py "field" API.
#
# In no-motion-swap conditions, the CW channel is fed exclusively by the
# first-on field (field 1), and the CCW channel exclusively by the
# delayed field (field 2).  These shims let earlier code keep working.
# ----------------------------------------------------------------------

def stim_field1(t, condition):
    """First-on field's contribution to the CW channel (no-swap only)."""
    stim_cw, _, _ = channels_for_trial(condition, motion_swap=False)
    return stim_cw(t)


def stim_field2(t, condition):
    """Delayed field's contribution to the CCW channel (no-swap only)."""
    _, stim_ccw, _ = channels_for_trial(condition, motion_swap=False)
    return stim_ccw(t)


def translation_input(t):
    """Translation input — identical across all 4 trial types."""
    t = np.asarray(t, dtype=float)
    val = np.where(
        (t >= T_TRANS_START) & (t < T_TRANS_END),
        STIM_TRANSLATION, 0.0,
    )
    return float(val) if val.ndim == 0 else val
