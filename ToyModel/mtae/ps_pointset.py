"""
POINT-SET model on the faithful cued-translation stimulus: 2 V1 hypercolumns -> 1 MT hypercolumn.

NOT the HC/PS point-set model (pointset/hcps_grid.m). This has no colour hypercolumn, so it cannot
speak to where the attentional bias enters -- the Model III / Model IV question, which turns on what
the bias does to an attribute that was never cued. Its FB term is like-to-like MT->V1 STIMULUS
feedback, not a top-down bias; do not read it as the bias term (Agents/Modeling/bias_locus.pdf p.1).

This is GS's spatially-extended point-set model COLLAPSED to its segregated idealization (= ps_seg):
because at the V1 cRF scale (~0.16 deg) the S&B stimulus has ~0.1-0.2 dots/cRF/field, each active
V1 hypercolumn is dominated by ONE surface. So the two transparent surfaces are represented by TWO
V1 hypercolumns (A = first-on, B = delayed/cued), each an 8-direction population, both feeding ONE
MT hypercolumn. NO per-dot oracle tagging: the surface identity is carried by the hypercolumn, and
the cooperation is a legitimate WITHIN-hypercolumn pool.

Faithful point-set engine (per V1 hypercolumn s, direction d):
    tau dX_{s,d}/dt = -X_{s,d} + PSP_{s,d}
    PSP_{s,d} = K_{s,d} * FB_{s,d} * Coop_s / Norm
      K       = expansive feedforward  (Gaussian/von-Mises-tuned drive)^p,  p=2
      FB      = 1 + fbg * M_d           like-to-like MT->V1 multiplicative feedback
      Coop_s  = 1 + CoopL * E_s         WITHIN-hypercolumn cooperation; E_s is a SLOW (tauE) leaky
                                        integrator of the hypercolumn's total activity (non-directional)
      Norm    = 1 + bNorm * sum_{s,d} X  global recurrent divisive normalization (self-bounding)
MT: P_d = sum_s X_{s,d};  Reynolds-Heeger motion competition M_d = P_d^2/(sigM^2 + mtComp*sum_k P_k^2).
Read-out: MT translation detector = M[UP] - M[DOWN] over the test window.

Cue for the cued surface B (delayed) -- two COMPETING accounts (never stacked, per S&B vs R&H):
  cue='adapt'  : feature-specific adaptation. B's onset is delayed so its direction cells are less
                 adapted -> stronger during the base period -> bigger E_B.
  cue='attend' : FEATURE-based directional bias on B's base direction (RIGHT), applied to BOTH
                 hypercolumns -- see biasVec below. It favours B only because B is the field whose
                 drive peaks at RIGHT, so the surface selectivity is EMERGENT, not addressed. This
                 is NOT the point-set Bias term, and this docstring claimed the opposite until
                 2026-08-20; the code has always been feature-based. Because the bias follows the
                 DIRECTION, it transfers to A under the motion swap -- which is exactly why the
                 coop-OFF headline below reverses.

Headline the model makes: with cooperation OFF the cueing is feature-based and REVERSES under the
motion swap; with slow within-HC cooperation ON it is object-based and SURVIVES the swap. The slow
non-directional pool E_s is what carries the cued surface's dominance through the base->translation
(and swap) direction change.

Run:  /usr/bin/python3 ps_pointset.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(0)
HERE = os.path.dirname(os.path.abspath(__file__)); FIGS = HERE + "/figs"
D = 8
THETA = np.arange(D) * (2*np.pi/D)                         # 0,45,...,315 deg
RIGHT, UP, LEFT, DOWN = 0, 2, 4, 6                          # direction-cell indices
DIRLAB = ["R", "UR", "U", "UL", "L", "DL", "D", "DR"]
T, T_ON, T_TEST0, T_TEST1 = 60, 20, 38, 48
COH = 0.5

# --- model parameters ---
KAPPA = 2.5          # von Mises tuning width of the feedforward drive
P_EXP = 2.0          # expansive feedforward exponent
ALPHA = 0.4          # V1 Euler step dt/tau
FBG = 0.5            # like-to-like MT->V1 feedback gain
TAU_E = 10.0         # SLOW cooperative-pool time constant (frames) -> carry-forward across the swap
KSAT = 0.6           # cooperative-gain saturation (engine's Ksat): locks the WTA without runaway
BNORM = 0.10         # global recurrent normalization strength
SIGM = 0.30          # MT R&H semisaturation
MTCOMP = 1.0         # MT competition strength
COOP_ON = 8.0        # cooperation gain used for the "coop ON" comparison
# cue strengths
BETA_AD, DECAY_AD = 0.3, 0.05   # feature-specific adaptation (cue='adapt')
BIAS_AMP = 2.0                  # feature-based directional attention on cued field's base dir (cue='attend')


def vm(dir_idx):
    """von Mises drive profile peaked (=1) at direction dir_idx, over the 8 cells."""
    return np.exp(KAPPA*(np.cos(THETA - THETA[dir_idx]) - 1.0))


UNIFORM = np.ones(D)/D


def surface_drive(base_dir, translating, testing):
    """Feedforward drive profile (length D) for one surface this frame."""
    if testing and translating:
        return COH*vm(UP) + (1.0-COH)*UNIFORM        # 50% coherent up-translation + incoherent
    return vm(base_dir)


def simulate(translate="cued", swap=False, coopL=1.5, cue="adapt", keep=False):
    """One trial. translate: 'cued' (delayed B translates) or 'uncued' (first-on A translates)."""
    Xa = np.zeros(D); Xb = np.zeros(D)                # V1 hypercolumns A, B
    aa = np.zeros(D); ab = np.zeros(D)                # feature-specific adaptation
    Ea = 0.0; Eb = 0.0                                # slow cooperative pools (non-directional)
    M = np.zeros(D)                                   # MT hypercolumn
    MT = np.zeros((T, D)); rec = []
    for t in range(T):
        baseA, baseB = LEFT, RIGHT
        if swap and t >= T_TEST0:
            baseA, baseB = RIGHT, LEFT
        testing = T_TEST0 <= t < T_TEST1
        transA = testing and (translate == "uncued")
        transB = testing and (translate == "cued")
        present_B = t >= T_ON

        driveA = surface_drive(baseA, transA, testing)
        driveB = surface_drive(baseB, transB, testing) if present_B else np.zeros(D)

        # feature-specific adaptation (cue='adapt'): grows with drive, reduces gain
        aa = aa + BETA_AD*driveA - DECAY_AD*aa
        if present_B:
            ab = ab + BETA_AD*driveB - DECAY_AD*ab
        if cue == "adapt":
            gA = 1.0/(1.0+aa); gB = 1.0/(1.0+ab)
            biasVec = np.ones(D)
        else:                                          # cue='attend': FEATURE-BASED directional
            gA = gB = 1.0                              # attention on the cued field's base direction
            biasVec = np.ones(D); biasVec[RIGHT] = 1.0 + BIAS_AMP   # (RIGHT = B's base dir)

        ffA = driveA*gA*biasVec
        ffB = driveB*gB*biasVec
        Ka = ffA**P_EXP; Kb = ffB**P_EXP               # expansive feedforward

        FB = 1.0 + FBG*M                                # like-to-like MT->V1 feedback
        # within-HC cooperation (slow pool), saturating so the WTA locks without runaway
        CoopA = 1.0 + coopL*(Ea/(1.0+Ea/KSAT))
        CoopB = 1.0 + coopL*(Eb/(1.0+Eb/KSAT))
        Norm = 1.0 + BNORM*(Xa.sum() + Xb.sum())        # global recurrent normalization

        PSPa = Ka*FB*CoopA/Norm
        PSPb = Kb*FB*CoopB/Norm
        Xa = Xa + ALPHA*(-Xa + PSPa)
        Xb = Xb + ALPHA*(-Xb + PSPb)
        Xa = np.maximum(Xa, 0.0); Xb = np.maximum(Xb, 0.0)

        # MT pooling + Reynolds-Heeger motion competition across directions
        Pd = Xa + Xb
        M = Pd**2 / (SIGM**2 + MTCOMP*(Pd**2).sum())
        MT[t] = M

        # advance the SLOW non-directional cooperative pools
        Ea = Ea + (1.0/TAU_E)*(Xa.sum() - Ea)
        Eb = Eb + (1.0/TAU_E)*(Xb.sum() - Eb)

        if keep:
            rec.append((Xa.copy(), Xb.copy(), M.copy(), Ea, Eb))
    if keep:
        return MT, rec
    return MT


def detector(MT):
    return MT[T_TEST0:T_TEST1, UP].mean() - MT[T_TEST0:T_TEST1, DOWN].mean()


def cued_uncued(coopL, cue, swap):
    c = detector(simulate("cued", swap, coopL, cue))
    u = detector(simulate("uncued", swap, coopL, cue))
    return c, u


# ---------------------------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print("POINT-SET model  (2 V1 hypercolumns -> 1 MT hypercolumn, faithful engine)\n")
    for cue in ("adapt", "attend"):
        print(f"=== cue = {cue} ===")
        print("            coop OFF (CoopL=0)          coop ON (slow within-HC)")
        for swap in (False, True):
            c0, u0 = cued_uncued(0.0, cue, swap)
            c1, u1 = cued_uncued(COOP_ON, cue, swap)
            print(f"  {'SWAP  ' if swap else 'noswap':6s}  cued {c0:6.3f} unc {u0:6.3f} "
                  f"({c0-u0:+.3f})     cued {c1:6.3f} unc {u1:6.3f} ({c1-u1:+.3f})")
        print()

    # ---- FIGURE: object-based (cooperation) survives swap; feature-based (no coop) reverses ----
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
    # (a) bar chart: cued-uncued difference, coop OFF vs ON, no-swap vs swap (cue=adapt)
    cue = "adapt"
    conds = [("no-swap", False), ("swap", True)]
    off = [cued_uncued(0.0, cue, sw) for _, sw in conds]
    on = [cued_uncued(COOP_ON, cue, sw) for _, sw in conds]
    x = np.arange(2); w = 0.35
    ax[0].bar(x-w/2, [c-u for c, u in off], w, color="#b0b0b0", label="coop OFF (feature-based)")
    ax[0].bar(x+w/2, [c-u for c, u in on], w, color="#2a9d8f", label="coop ON (object-based)")
    ax[0].axhline(0, color="k", lw=.8); ax[0].set_xticks(x); ax[0].set_xticklabels([c for c, _ in conds])
    ax[0].set_ylabel("cued − uncued  (MT translation detector)")
    ax[0].set_title("Cooperation makes cueing survive the swap\n(cue = delayed-onset adaptation)")
    ax[0].legend(fontsize=8)
    # (b) CoopL sweep: swap survival grows with cooperation
    coops = np.linspace(0, 12, 13)
    ns = [cued_uncued(cl, "adapt", False) for cl in coops]
    sw = [cued_uncued(cl, "adapt", True) for cl in coops]
    ax[1].plot(coops, [c-u for c, u in ns], "-o", ms=3, color="#264653", label="no-swap")
    ax[1].plot(coops, [c-u for c, u in sw], "-s", ms=3, color="#e76f51", label="swap")
    ax[1].axhline(0, color="gray", lw=.8); ax[1].set_xlabel("cooperation gain  CoopL")
    ax[1].set_ylabel("cued − uncued"); ax[1].legend(fontsize=8)
    ax[1].set_title("Swap reverses without cooperation,\nsurvives as CoopL grows")
    # (c) MT detector time course, cued vs uncued, SWAP, coop ON
    mtc = simulate("cued", True, COOP_ON, "adapt"); mtu = simulate("uncued", True, COOP_ON, "adapt")
    ax[2].plot(mtc[:, UP]-mtc[:, DOWN], "-o", ms=3, color="#d1495b", label="CUED translates")
    ax[2].plot(mtu[:, UP]-mtu[:, DOWN], "-s", ms=3, color="#3f88c5", label="UNCUED translates")
    ax[2].axvspan(T_TEST0, T_TEST1, color="gold", alpha=0.2); ax[2].axvline(T_ON, color="gray", ls=":")
    ax[2].axhline(0, color="gray", lw=.8); ax[2].set_xlabel("frame")
    ax[2].set_ylabel("MT translation detector (up − down)")
    ax[2].legend(fontsize=8); ax[2].set_title("MT detector — SWAP trial, cooperation ON")
    fig.tight_layout(); p = os.path.join(FIGS, "ps_pointset.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("figure ->", p)
