"""
Faithful cued-translation stimulus + V1/MT model.

Stimulus (matches the real paradigm, no rotation):
 - two transparent dot fields in OPPOSITE horizontal motion (A left, B right),
 - field B delayed onset = the CUE,
 - at test, ONE field briefly translates in the ORTHOGONAL direction (up or down)
   at 50% coherence -- this is the judged motion,
 - optional motion SWAP of the base directions at test.

Model:
 - each dot carries an ADAPTATION state (grows with time present) -> the long-present
   (uncued) field is adapted, the delayed (cued) field is fresh.
 - V1 = motion energy in 4 direction channels (R,U,L,D), gain = 1/(1+adapt), per dot.
 - MT = one hypercolumn pooling V1 over space -> 4 direction channels.
 - TRANSLATION DETECTOR = MT up/down channels (read out U vs D).

Because the cued field's dots are less adapted, its brief translation drives the MT
up/down detector more strongly -> the cueing effect, and it does not depend on the
base direction, so it survives the swap.

This module: simulate trials, train the U/D read-out across a density range, and plot
the MT translation-detector response for cued vs uncued (and vs density).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(0)
HERE = os.path.dirname(os.path.abspath(__file__)); FIGS = HERE + "/figs"
R_AP = 10.0
DIRS = np.array([0, np.pi/2, np.pi, 3*np.pi/2])       # R, U, L, D  (idx 0,1,2,3)
RIGHT, UP, LEFT, DOWN = 0, 1, 2, 3
T, T_ON, T_TEST0, T_TEST1 = 60, 12, 38, 48            # timeline (frames)
BETA, DECAY = 0.22, 0.02
COH = 0.5


def make_field(n):
    pts = []
    while len(pts) < n:
        p = np.random.uniform(-R_AP, R_AP, 2)
        if p[0]**2 + p[1]**2 < 0.95*R_AP**2:
            pts.append(p)
    return np.array(pts)


def simulate(n_dots, translate="cued", signal=UP, swap=False, keep_traj=False):
    """Return V1 (T,4), MT (T,4) time courses (and dot trajectory if asked)."""
    posA, posB = make_field(n_dots), make_field(n_dots)
    aA, aB = np.zeros(n_dots), np.zeros(n_dots)                # per-dot adaptation
    cohB = np.random.rand(n_dots) < COH                         # coherent subset (if B translates)
    cohA = np.random.rand(n_dots) < COH
    V1 = np.zeros((T, 4)); MT = np.zeros((T, 4)); traj = []
    for t in range(T):
        baseA, baseB = LEFT, RIGHT
        if swap and t >= T_TEST0:
            baseA, baseB = RIGHT, LEFT
        dirA = np.full(n_dots, baseA); dirB = np.full(n_dots, baseB)
        testing = T_TEST0 <= t < T_TEST1
        if testing:
            tf = translate
            if tf == "cued":       # B is cued (delayed)
                dirB = np.where(cohB, signal, np.random.randint(0, 4, n_dots))
            else:                  # A is uncued (first-on)
                dirA = np.where(cohA, signal, np.random.randint(0, 4, n_dots))
        present_B = t >= T_ON
        # adaptation grows while present
        aA = aA + BETA - DECAY*aA
        if present_B:
            aB = aB + BETA - DECAY*aB
        gA = 1.0/(1.0+aA); gB = 1.0/(1.0+aB)
        v = np.zeros(4)
        for d in range(4):
            v[d] += gA[dirA == d].sum()
            if present_B:
                v[d] += gB[dirB == d].sum()
        V1[t] = v; MT[t] = v                                   # MT = pooled V1 (one hypercolumn)
        if keep_traj:
            velA = 0.30*np.array([np.cos(DIRS[baseA]), np.sin(DIRS[baseA])])
            posA = posA + velA
            posA[:, 0] = ((posA[:, 0]+R_AP) % (2*R_AP))-R_AP
            if present_B:
                if testing:
                    ang = np.where(cohB, DIRS[signal], np.random.rand(n_dots)*2*np.pi)
                    posB = posB + 0.42*np.stack([np.cos(ang), np.sin(ang)], 1)
                else:
                    velB = 0.30*np.array([np.cos(DIRS[baseB]), np.sin(DIRS[baseB])])
                    posB = posB + velB
                    posB[:, 0] = ((posB[:, 0]+R_AP) % (2*R_AP))-R_AP
            eB = np.empty(0)
            traj.append((posA.copy(), posB.copy() if present_B else np.empty((0, 2)),
                         gA.copy(), gB.copy() if present_B else eB, testing))
    return (V1, MT, traj) if keep_traj else (V1, MT)


def detector(MT, signal=UP):
    """MT translation-detector readout at the test window: signal-channel minus its opposite."""
    opp = {UP: DOWN, DOWN: UP}[signal]
    return MT[T_TEST0:T_TEST1, signal].mean() - MT[T_TEST0:T_TEST1, opp].mean()


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    densities = [15, 30, 60, 120]
    curves = {}
    for sw in [True, False]:
        cc, uc = [], []
        print(f"MT translation detector, {'SWAP' if sw else 'NO-SWAP'} (cued vs uncued):")
        for n in densities:
            dc = np.mean([detector(simulate(n, "cued", UP, swap=sw)[1]) for _ in range(40)])
            du = np.mean([detector(simulate(n, "uncued", UP, swap=sw)[1]) for _ in range(40)])
            cc.append(dc); uc.append(du)
            print(f"  density {n:3d}:  cued {dc:6.2f}  uncued {du:6.2f}  ratio {dc/max(du,1e-3):.2f}x")
        curves[sw] = (cc, uc)
    cued_curve, unc_curve = curves[True]

    # time course at one density
    n = 60
    mtC = np.mean([simulate(n, "cued", UP, swap=True)[1] for _ in range(60)], 0)
    mtU = np.mean([simulate(n, "uncued", UP, swap=True)[1] for _ in range(60)], 0)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    ax[0].plot(mtC[:, UP]-mtC[:, DOWN], "-o", ms=3, color="#d1495b", label="CUED field translates")
    ax[0].plot(mtU[:, UP]-mtU[:, DOWN], "-s", ms=3, color="#3f88c5", label="UNCUED field translates")
    ax[0].axvspan(T_TEST0, T_TEST1, color="gold", alpha=0.2); ax[0].axvline(T_ON, color="gray", ls=":")
    ax[0].axhline(0, color="gray", lw=.8); ax[0].set_xlabel("frame"); ax[0].set_ylabel("MT translation detector (up − down)")
    ax[0].legend(); ax[0].set_title(f"Detector time course (density {n})")
    ax[1].plot(densities, curves[True][0], "-o", color="#d1495b", label="cued, swap")
    ax[1].plot(densities, curves[True][1], "-s", color="#3f88c5", label="uncued, swap")
    ax[1].plot(densities, curves[False][0], "--o", color="#d1495b", mfc="w", label="cued, no-swap")
    ax[1].plot(densities, curves[False][1], "--s", color="#3f88c5", mfc="w", label="uncued, no-swap")
    ax[1].set_xlabel("dots per field (density)"); ax[1].set_ylabel("MT detector response (test window)")
    ax[1].legend(fontsize=8); ax[1].set_title("Cued vs uncued vs density (swap & no-swap)")
    fig.tight_layout(); p = os.path.join(FIGS, "real_detector.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p)
