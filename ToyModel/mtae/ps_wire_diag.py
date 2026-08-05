"""Diagnostics answering two objections to ps_wire.py:
 A. Is the SWAP condition doing anything to the translation detector?
 B. Does the cued advantage survive a REAL spatial cooperative lateral (V1 RFs that pool BOTH
    fields' intermingled dots), instead of the per-dot/per-token context ps_wire.py uses?
"""
import numpy as np
import ps_wire as P

UP, DOWN, LEFT, RIGHT = P.UP, P.DOWN, P.LEFT, P.RIGHT
T, T_ON, T0, T1 = P.T, P.T_ON, P.T_TEST0, P.T_TEST1
BETA, LAM, COH, G, R = P.BETA, P.LAM, P.COH, P.G, P.R_AP

# --------------------------------------------------------------------------------------------
# A.  Is the swap a no-op?  Same seed, cued translation, swap vs no-swap -> compare MT[UP],MT[DOWN].
print("=== A. Does the swap change the translation detector at all? ===")
for cond in ("cued", "uncued"):
    for sw in (False, True):
        np.random.seed(11)
        mt = P.simulate(60, cond, UP, swap=sw)
        up = mt[T0:T1, UP].mean(); dn = mt[T0:T1, DOWN].mean()
        print(f"  {cond:6s} {'SWAP  ' if sw else 'noswap'}:  MT_up={up:7.2f}  MT_down={dn:6.2f}  det={up-dn:7.2f}")
print("  -> if the two rows per condition are identical, the swap does NOTHING to the readout.\n")


# --------------------------------------------------------------------------------------------
# B.  Real spatial cooperative lateral.  Base-motion context is pooled in V1 RF cells that contain
#     BOTH fields' dots (intermingled).  A translating dot is boosted by the horizontal energy at
#     ITS cell -- which mixes A(left) + B(right).  No per-token tagging.
def simulate_spatial(n_dots, translate="cued", swap=False, coopg=8.0, reps_seed=None):
    posA = P.make_field(n_dots); posB = P.make_field(n_dots)
    aHA = np.zeros(n_dots); aHB = np.zeros(n_dots)
    cohA = np.random.rand(n_dots) < COH; cohB = np.random.rand(n_dots) < COH
    ctxGrid = np.zeros((G, G))                                  # SHARED spatial base-motion context
    MT = np.zeros((T, 4))

    def cell(P_):
        ix = np.clip(((P_[:, 0]+R)/(2*R)*G).astype(int), 0, G-1)
        iy = np.clip(((P_[:, 1]+R)/(2*R)*G).astype(int), 0, G-1)
        return ix, iy

    for t in range(T):
        baseA, baseB = (LEFT, RIGHT) if not (swap and t >= T0) else (RIGHT, LEFT)
        dirA = np.full(n_dots, baseA); dirB = np.full(n_dots, baseB)
        testing = T0 <= t < T1
        if testing:
            if translate == "cued":
                dirB = np.where(cohB, UP, np.random.randint(0, 4, n_dots))
            else:
                dirA = np.where(cohA, UP, np.random.randint(0, 4, n_dots))
        present_B = t >= T_ON
        horizA = (dirA == LEFT) | (dirA == RIGHT); vertA = ~horizA
        horizB = (dirB == LEFT) | (dirB == RIGHT); vertB = ~horizB
        aHA = aHA + np.where(horizA, BETA, 0.0)
        if present_B:
            aHB = aHB + np.where(horizB, BETA, 0.0)
        gHA = 1.0/(1.0+aHA); gHB = 1.0/(1.0+aHB)

        # cooperative boost = SHARED spatial context sampled at each dot's cell (mixes both fields)
        ixA, iyA = cell(posA); ixB, iyB = cell(posB)
        eA = np.where(horizA, gHA, 1.0 + coopg*ctxGrid[ixA, iyA])
        eB = np.where(horizB, gHB, 1.0 + coopg*ctxGrid[ixB, iyB])
        m = np.zeros(4)
        for d in range(4):
            m[d] += eA[dirA == d].sum()
            if present_B:
                m[d] += eB[dirB == d].sum()
        MT[t] = m

        # update the SHARED horizontal-energy grid from BOTH fields' base motion (intermingled)
        newgrid = np.zeros((G, G))
        np.add.at(newgrid, (ixA[horizA], iyA[horizA]), gHA[horizA])
        if present_B:
            np.add.at(newgrid, (ixB[horizB], iyB[horizB]), gHB[horizB])
        ctxGrid = ctxGrid + LAM*(newgrid - ctxGrid)

        # advance positions (base motion; vertical during test)
        stepA = np.where(vertA, P.VT, P.VH)[:, None]
        angA = np.where(vertA, P.DIRS[dirA], P.DIRS[baseA])
        posA = posA + np.stack([np.cos(angA), np.sin(angA)], 1)*stepA
        posA[:, 0] = ((posA[:, 0]+R) % (2*R))-R
        if present_B:
            stepB = np.where(vertB, P.VT, P.VH)[:, None]
            angB = np.where(vertB, P.DIRS[dirB], P.DIRS[baseB])
            posB = posB + np.stack([np.cos(angB), np.sin(angB)], 1)*stepB
            posB[:, 0] = ((posB[:, 0]+R) % (2*R))-R
    return MT


def det(mt):
    return mt[T0:T1, UP].mean() - mt[T0:T1, DOWN].mean()


print("=== B. Cued advantage with a REAL spatial cooperative lateral (intermingled V1 RFs) ===")
print("     (per-token ps_wire.py gives ~1.35x; a genuine spatial lateral cannot tag surfaces)")
for n in (25, 80, 200):
    row = []
    for sw in (False, True):
        c = np.mean([det(simulate_spatial(n, "cued", sw)) for _ in range(120)])
        u = np.mean([det(simulate_spatial(n, "uncued", sw)) for _ in range(120)])
        row.append((c, u))
    (c0, u0), (c1, u1) = row
    print(f"  density {n:4d}:  noswap {c0:7.1f}/{u0:7.1f} ({c0/max(u0,1e-3):.2f}x)   "
          f"swap {c1:7.1f}/{u1:7.1f} ({c1/max(u1,1e-3):.2f}x)")
