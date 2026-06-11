"""
Faithful Python port of Heeger & Reynolds' attentionModel.m (R&H 2009).

The MATLAB function has signature

    R = attentionModel(x, theta, stimulus, [param/value pairs])

This module exposes the same model as `attention_model(x, theta,
stimulus, **kwargs)`.

Math
----
Stimulation field and suppressive field are separable 2D Gaussians.
Attention field is the (optionally normalized) outer product of x and θ
Gaussians, rescaled to peak `Apeak` with baseline `Abase`.

    E_raw      = stimulus ⊛ (E_x ⊗ E_θ)        + baselineMod
    A          = attention field (see attention_field())
    E          = A · E_raw
    I          = E ⊛ (I_x ⊗ I_θ)
    R          = E / (I + σ) + baselineUnmod

Convolution boundary handling, matching conv2sepYcirc.m:
    along the x  axis  (columns of `stimulus`): zero-pad
    along the θ axis  (rows    of `stimulus`): circular

For a Gaussian "kernel" or "field" we use the same helper as makeGaussian.m:

    g(x; μ, σ) = (1 / (σ√(2π))) · exp(-(x-μ)² / (2σ²))           (height=None)
    g(x; μ, σ, h) = h · exp(-(x-μ)² / (2σ²))                      (height=h)
"""

from typing import Optional

import numpy as np
from scipy.ndimage import convolve1d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_gaussian(space: np.ndarray, center: float, width: float,
                  height: Optional[float] = None) -> np.ndarray:
    """Port of makeGaussian.m.

    Without ``height``: unit-volume normpdf with mean=center, std=width.
    With    ``height``: same Gaussian re-scaled so its peak equals ``height``.
    """
    space = np.asarray(space, dtype=float)
    g = np.exp(-0.5 * ((space - center) / width) ** 2) / (width * np.sqrt(2 * np.pi))
    if height is not None:
        g = height * width * np.sqrt(2 * np.pi) * g
    return g


def conv2sep_y_circ(im: np.ndarray, rowfilt: np.ndarray,
                    colfilt: np.ndarray) -> np.ndarray:
    """Port of conv2sepYcirc.m, matching MATLAB's *fallback* behavior.

    ``im`` is (N_θ, N_x).

    In principle, conv2sepYcirc requests zero-boundary along x and
    circular-boundary along θ. In practice, the pure-MATLAB ``upConv.m``
    fallback (which is what runs on Apple Silicon, where the 2009 MEX
    binaries don't load) uses REFLECT1 for both axes regardless of the
    requested boundary mode. The MEX warning message reads
    "Using REFLECT1 edge-handling (use MEX code for other options)".

    We mirror that behavior here so the Python port is bit-for-bit
    comparable with the actual MATLAB output we have. If/when we get
    the MEX recompiled, this can be split into the two requested modes
    (zero for x, circular for θ).
    """
    # rowfilt along x (axis=1), reflect1 boundary
    tmp = convolve1d(im, np.asarray(rowfilt).ravel(),
                     axis=1, mode='mirror')
    # colfilt along θ (axis=0), reflect1 boundary
    result = convolve1d(tmp, np.asarray(colfilt).ravel(),
                        axis=0, mode='mirror')
    return result


# ---------------------------------------------------------------------------
# Attention field
# ---------------------------------------------------------------------------

def _build_attention_field(x, theta, *, Ax, Atheta, AxWidth, AthetaWidth,
                            Apeak, Abase, Ashape):
    """Construct A(θ, x).

    Mirrors the MATLAB block:
        attnGainX     = makeGaussian(x,     Ax, AxWidth, 1)
        attnGainTheta = makeGaussian(theta, 0,  AthetaWidth, 1)
        impulse       = (theta == Atheta)              (column delta)
        tmp           = impulse * attnGainX            (outer product)
        attnGain      = conv2sepYcirc(tmp, [1], attnGainTheta)
        attnGain      = (Apeak - Abase) * attnGain + Abase
    """
    x_is_nan     = (Ax     is None) or (isinstance(Ax,     float) and np.isnan(Ax))
    theta_is_nan = (Atheta is None) or (isinstance(Atheta, float) and np.isnan(Atheta))

    if x_is_nan and theta_is_nan:
        return np.ones((len(theta), len(x)))

    # x component
    if x_is_nan:
        attnGainX = np.ones_like(x, dtype=float)
    else:
        attnGainX = make_gaussian(x, Ax, AxWidth, height=1.0)
        if Ashape == 'cross':
            attnGainX = (Apeak - Abase) * attnGainX + Abase

    # θ component
    if theta_is_nan:
        attnGainTheta = np.ones_like(theta, dtype=float)
        Atheta_resolved = 0
    else:
        attnGainTheta = make_gaussian(theta, 0.0, AthetaWidth, height=1.0)
        if Ashape == 'cross':
            attnGainTheta = (Apeak - Abase) * attnGainTheta + Abase
        Atheta_resolved = Atheta

    # Impulse delta at θ = Atheta
    impulse = (theta == Atheta_resolved).astype(float).reshape(-1, 1)
    tmp = impulse * attnGainX.reshape(1, -1)

    # rowfilt = [1] (no spatial smoothing), colfilt = attnGainTheta (circular)
    attnGain = conv2sep_y_circ(tmp, np.array([1.0]), attnGainTheta)
    attnGain = (Apeak - Abase) * attnGain + Abase
    return attnGain


# ---------------------------------------------------------------------------
# Main model
# ---------------------------------------------------------------------------

def attention_model(x: np.ndarray, theta: np.ndarray, stimulus: np.ndarray,
                    *,
                    ExWidth: float = 5,
                    EthetaWidth: float = 60,
                    IxWidth: float = 20,
                    IthetaWidth: float = 360,
                    Ax: Optional[float] = None,
                    Atheta: Optional[float] = None,
                    AxWidth: Optional[float] = None,
                    AthetaWidth: Optional[float] = None,
                    Apeak: float = 2.0,
                    Abase: float = 1.0,
                    Ashape: str = 'oval',
                    sigma: float = 1e-6,
                    baselineMod: float = 0.0,
                    baselineUnmod: float = 0.0,
                    ) -> np.ndarray:
    """R&H 2009 normalization model of attention — Python port.

    Parameters and defaults are taken verbatim from attentionModel.m.
    ``Ax`` or ``Atheta`` left as None (or NaN) means attention is spread
    evenly along that dimension.

    Returns
    -------
    R : ndarray of shape (len(theta), len(x))
    """
    x = np.asarray(x, dtype=float)
    theta = np.asarray(theta, dtype=float)
    if AxWidth is None:
        AxWidth = ExWidth
    if AthetaWidth is None:
        AthetaWidth = EthetaWidth

    # Stimulation and suppressive field kernels (unit-volume Gaussians)
    ExKernel     = make_gaussian(x,     0.0, ExWidth)
    IxKernel     = make_gaussian(x,     0.0, IxWidth)
    EthetaKernel = make_gaussian(theta, 0.0, EthetaWidth)
    IthetaKernel = make_gaussian(theta, 0.0, IthetaWidth)

    # Attention field
    A = _build_attention_field(
        x, theta,
        Ax=Ax, Atheta=Atheta,
        AxWidth=AxWidth, AthetaWidth=AthetaWidth,
        Apeak=Apeak, Abase=Abase, Ashape=Ashape,
    )

    # Stimulus drive
    Eraw = conv2sep_y_circ(stimulus, ExKernel, EthetaKernel) + baselineMod
    E    = A * Eraw

    # Suppressive drive
    I = conv2sep_y_circ(E, IxKernel, IthetaKernel)

    # Normalization
    R = E / (I + sigma) + baselineUnmod
    return R
