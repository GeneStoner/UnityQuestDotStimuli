"""
Parameters for the Stoner & Blanc (2010) motion-competition model.

All values taken directly from Appendix A of the paper.

Reference: Stoner, G. R., & Blanc, G. (2010). Exploring the mechanisms
underlying surface-based stimulus selection. Vision Research, 50(2), 229-241.
"""

# ---------------------------------------------------------------
# Stage 1: adapting rotation responses (Eqs 4-5 of the paper)
# ---------------------------------------------------------------

TAU = 20.0          # ms   — response time constant
TAU_ADAPT = 1000.0  # ms   — adaptation time constant
W_ADAPT = 1.25      #      — adaptation strength (key knob)

# Naka-Rushton in the numerator of Eq 4:
#   N(x) = NR_MAX * [x]+² / (NR_SEMISAT² + [x]+²)
NR_MAX = 100.0      #      — Naka-Rushton numerator coefficient
NR_SEMISAT = 10.0   #      — semisaturation constant

# ---------------------------------------------------------------
# Stage 2: translation detector (Eqs 1-3 of the paper)
#   E = Σ W⁺ⱼ · Cⱼ
#   I = Σ W⁻ⱼ · Cⱼ
#   R_TD = K * E / (E + I + σ)
# ---------------------------------------------------------------

K = 100.0           #      — max firing rate of translation detector
SIGMA = 1.0         #      — semisaturation / normalization floor
                    #        (per Krekelberg & Albright 2005)
W_TRANS = 1.0       #      — excitatory weight for translation input
W_ROT = 1.0         #      — inhibitory weight for each rotation input
                    #        (assumed equal for both directions)

# ---------------------------------------------------------------
# Stimulus amplitudes (Mode 1 = binary inputs, per Fig. 3 of paper)
# ---------------------------------------------------------------

STIM_ROTATION = 50.0     # value when a rotation is present (else 0)
STIM_TRANSLATION = 25.0  # value when a translation is present (else 0)
                         # half of rotation because only ~50% of dots
                         # translate coherently

# ---------------------------------------------------------------
# Trial timing (ms) — from Section 2.3 of the paper
# ---------------------------------------------------------------

T_SOLO = 750.0      # field 1 alone before field 2 appears
T_PRETRANS = 300.0  # both fields rotating before translation
T_TRANS = 40.0      # translation duration (3 frames at 75 Hz)
T_POST = 500.0      # post-translation rotation

# Derived phase boundaries
T_FIELD2_ON = T_SOLO                       # 750  ms — field 2 appears
T_TRANS_START = T_SOLO + T_PRETRANS        # 1050 ms — translation begins
T_TRANS_END = T_TRANS_START + T_TRANS      # 1090 ms — translation ends
T_END = T_TRANS_END + T_POST               # 1590 ms — trial ends
