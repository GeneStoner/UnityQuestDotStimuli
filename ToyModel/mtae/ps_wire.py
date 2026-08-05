"""
HAND-WIRED PS model on the faithful cued-translation stimulus (no training).

Stimulus (real_stim paradigm, no rotation):
 - two transparent dot fields in OPPOSITE horizontal base motion (A left, B right),
 - field B delayed onset = the CUE,
 - at test, ONE field briefly translates ORTHOGONALLY (up) at 50% coherence -- the judged event,
 - optional motion SWAP of the base directions at test.

PS connections, all HAND-SET (nothing trained):
 1. DIRECTION-SPECIFIC ADAPTATION in the motion units, carried by the moving dots (motion tokens):
    a unit adapts to the direction it is driven in. The two fields move in opposite HORIZONTAL base
    directions; because field B (cued) appears later, its base channel is LESS adapted than A's.
    CRUCIAL: the test translation is a FRESH direction (UP) that neither field moved in before, so
    the UP channel is EQUALLY un-adapted for both fields. The onset/adaptation asymmetry therefore
    lives ONLY in the horizontal base channel and cannot reach the UP detector on its own.
 2. LIKE-TO-LIKE MULTIPLICATIVE FEEDBACK (MT dir d -> V1 dir d): the pooled MT direction response
    re-amplifies its own V1 channel multiplicatively, fbgain[d] = 1 + FBG * MTn[d].
 3. COOPERATIVE LATERAL that carries the BASE-motion bias into the ORTHOGONAL translation channel.
    Each surface's sustained horizontal base motion sets up a persistent facilitatory context
    (ctx_i, a low-pass of the dot's horizontal base gain). When the dot then translates vertically,
    that context multiplies its contribution to the up/down channel:  e_i = (1 + COOPG * ctx_i).
    This is the PS cooperation linking successive motions of the same surface. Because ctx is larger
    for the un-adapted CUED surface, the cooperation TRANSFERS that bias into the (otherwise
    symmetric) UP channel -> the cued translation is amplified. With COOPG=0 there is NO cued
    advantage; the whole effect is carried by the connection.

Read-out = MT translation detector (up minus down) over the test window.

Because ctx (base bias) is built from horizontal motion BEFORE the swap and travels with the
surface's dots, the cued advantage SURVIVES the swap (the base directions flip, the carried bias
does not).

Run:  /usr/bin/python3 ps_wire.py      (RETRAIN unused; nothing is trained)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(0)
HERE = os.path.dirname(os.path.abspath(__file__)); FIGS = HERE + "/figs"
R_AP = 10.0
DIRS = np.array([0, np.pi/2, np.pi, 3*np.pi/2])           # R, U, L, D
RIGHT, UP, LEFT, DOWN = 0, 1, 2, 3
DIRLAB = ["R", "U", "L", "D"]
T, T_ON, T_TEST0, T_TEST1 = 60, 20, 38, 48
BETA, DECAY = 0.22, 0.0                                    # pure accumulation -> clean onset asymmetry
COH = 0.5
G = 12                                                    # V1 spatial grid (display + binning)
SIGMA = 0.5
LAM = 0.35                                                # base-context low-pass rate
VH = 0.30                                                 # base horizontal speed (for advection/display)
VT = 0.42                                                 # translation speed


def make_field(n):
    pts = []
    while len(pts) < n:
        p = np.random.uniform(-R_AP, R_AP, 2)
        if p[0]**2 + p[1]**2 < 0.95*R_AP**2:
            pts.append(p)
    return np.array(pts)


def cell_idx(P):
    ix = np.clip(((P[:, 0]+R_AP)/(2*R_AP)*G).astype(int), 0, G-1)
    iy = np.clip(((P[:, 1]+R_AP)/(2*R_AP)*G).astype(int), 0, G-1)
    return ix, iy


def divnorm_grid(v):
    v = np.maximum(v, 0.0)
    return v / (SIGMA + v.sum(-1, keepdims=True))


def simulate(n_dots, translate="cued", signal=UP, swap=False, coopg=8.0, fbg=0.6, keep=False):
    """Hand-wired PS forward pass. Returns MT (T,4); optionally V1 grids + dot traj for display."""
    posA, posB = make_field(n_dots), make_field(n_dots)
    aHA, aHB = np.zeros(n_dots), np.zeros(n_dots)              # per-dot HORIZONTAL-base adaptation
    ctxA, ctxB = np.zeros(n_dots), np.zeros(n_dots)            # per-dot base-motion context (carried bias)
    cohA = np.random.rand(n_dots) < COH
    cohB = np.random.rand(n_dots) < COH
    MT = np.zeros((T, 4))
    V1frames = []; traj = []
    for t in range(T):
        baseA, baseB = LEFT, RIGHT
        if swap and t >= T_TEST0:
            baseA, baseB = RIGHT, LEFT
        dirA = np.full(n_dots, baseA); dirB = np.full(n_dots, baseB)
        testing = T_TEST0 <= t < T_TEST1
        if testing:
            if translate == "cued":       # cued (delayed) field B translates up
                dirB = np.where(cohB, signal, np.random.randint(0, 4, n_dots))
            else:                         # uncued (first-on) field A translates up
                dirA = np.where(cohA, signal, np.random.randint(0, 4, n_dots))
        present_B = t >= T_ON
        horizA = (dirA == LEFT) | (dirA == RIGHT); vertA = ~horizA
        horizB = (dirB == LEFT) | (dirB == RIGHT); vertB = ~horizB

        # 1. DIRECTION-SPECIFIC adaptation: only the horizontal base channel adapts (grows while
        #    the dot moves horizontally). UP/DOWN is a fresh direction -> un-adapted for both fields.
        aHA = aHA + np.where(horizA, BETA - DECAY*aHA, 0.0)
        if present_B:
            aHB = aHB + np.where(horizB, BETA - DECAY*aHB, 0.0)
        gHA = 1.0/(1.0+aHA); gHB = 1.0/(1.0+aHB)               # adapted horizontal gain (cued > uncued)

        # per-dot contribution:  horizontal -> adapted base gain;  vertical -> FRESH gain (1.0) but
        # 3b. COOPERATIVELY multiplied by the carried base context (the only path bias reaches UP/DOWN)
        eA = np.where(horizA, gHA, 1.0 + coopg*ctxA)
        eB = np.where(horizB, gHB, 1.0 + coopg*ctxB)

        # pool to MT (one hypercolumn), then like-to-like multiplicative feedback
        m = np.zeros(4)
        for d in range(4):
            m[d] += eA[dirA == d].sum()
            if present_B:
                m[d] += eB[dirB == d].sum()
        mn = m / (SIGMA + m.sum())
        fbgain = 1.0 + fbg*mn                                   # 2. like-to-like multiplicative feedback
        MT[t] = m * fbgain

        # 3a. base-motion context for NEXT frame: low-pass of the FEEDBACK-AMPLIFIED horizontal base
        #     drive. The cued field's stronger (less-adapted) base channel is amplified more by the
        #     like-to-like feedback, so its carried bias ctx is larger -> bigger transfer to UP.
        ctxA = ctxA + LAM*(np.where(horizA, gHA*fbgain[dirA], 0.0) - ctxA)
        if present_B:
            ctxB = ctxB + LAM*(np.where(horizB, gHB*fbgain[dirB], 0.0) - ctxB)

        if keep:
            v = np.zeros((G, G, 4))
            ixA, iyA = cell_idx(posA); np.add.at(v, (ixA, iyA, dirA), eA)
            if present_B:
                ixB, iyB = cell_idx(posB); np.add.at(v, (ixB, iyB, dirB), eB)
            v = v * fbgain[None, None, :]
            V1frames.append(divnorm_grid(v))
            angA = np.where(vertA, DIRS[dirA], DIRS[baseA])
            stepA = np.where(vertA, VT, VH)[:, None]
            posA = posA + np.stack([np.cos(angA), np.sin(angA)], 1)*stepA
            posA[:, 0] = ((posA[:, 0]+R_AP) % (2*R_AP))-R_AP
            if present_B:
                angB = np.where(vertB, DIRS[dirB], DIRS[baseB])
                stepB = np.where(vertB, VT, VH)[:, None]
                posB = posB + np.stack([np.cos(angB), np.sin(angB)], 1)*stepB
                posB[:, 0] = ((posB[:, 0]+R_AP) % (2*R_AP))-R_AP
            traj.append((posA.copy(), posB.copy() if present_B else np.empty((0, 2)),
                         gHA.copy(), gHB.copy() if present_B else np.empty(0), testing))
    if keep:
        return MT, V1frames, traj
    return MT


def detector(MT, signal=UP):
    opp = {UP: DOWN, DOWN: UP}[signal]
    return MT[T_TEST0:T_TEST1, signal].mean() - MT[T_TEST0:T_TEST1, opp].mean()


def mean_detector(n, translate, swap, coopg, fbg, reps=40):
    return np.mean([detector(simulate(n, translate, UP, swap, coopg, fbg)) for _ in range(reps)])


# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    COOPG, FBG = 8.0, 0.6
    densities = [15, 30, 60, 120]

    # ---- ablation: does the COOPERATIVE CONNECTION carry the base bias? coop off vs on ----
    print("=== cued vs uncued MT translation detector (hand-wired PS) ===")
    abl = {}
    for cg in [0.0, COOPG]:
        tag = "coop OFF" if cg == 0 else "coop ON "
        print(f"\n[{tag}]   (fbg={FBG})")
        for sw in [False, True]:
            dc = mean_detector(60, "cued", sw, cg, FBG)
            du = mean_detector(60, "uncued", sw, cg, FBG)
            abl[(cg, sw)] = (dc, du)
            print(f"   {'SWAP  ' if sw else 'NOSWAP'}:  cued {dc:6.2f}   uncued {du:6.2f}   ratio {dc/max(du,1e-3):.2f}x")

    # ---- density sweep, coop ON, swap & no-swap ----
    curves = {}
    for sw in [False, True]:
        cc = [mean_detector(n, "cued", sw, COOPG, FBG) for n in densities]
        uc = [mean_detector(n, "uncued", sw, COOPG, FBG) for n in densities]
        curves[sw] = (cc, uc)

    # ---- FIGURE 1: detector outputs (cued vs uncued, no-swap & swap) ----
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
    # (a) time course at one density, swap
    mtC = np.mean([simulate(60, "cued", UP, True, COOPG, FBG) for _ in range(60)], 0)
    mtU = np.mean([simulate(60, "uncued", UP, True, COOPG, FBG) for _ in range(60)], 0)
    ax[0].plot(mtC[:, UP]-mtC[:, DOWN], "-o", ms=3, color="#d1495b", label="CUED translates")
    ax[0].plot(mtU[:, UP]-mtU[:, DOWN], "-s", ms=3, color="#3f88c5", label="UNCUED translates")
    ax[0].axvspan(T_TEST0, T_TEST1, color="gold", alpha=0.2); ax[0].axvline(T_ON, color="gray", ls=":")
    ax[0].axvline(T_TEST0, color="k", ls="--", lw=.8)
    ax[0].axhline(0, color="gray", lw=.8); ax[0].set_xlabel("frame")
    ax[0].set_ylabel("MT translation detector (up − down)")
    ax[0].legend(); ax[0].set_title("Detector time course — SWAP (density 60)")
    # (b) grouped bars: coop off vs on, no-swap & swap
    groups = [("no-swap\ncoop OFF", (0.0, False)), ("swap\ncoop OFF", (0.0, True)),
              ("no-swap\ncoop ON", (COOPG, False)), ("swap\ncoop ON", (COOPG, True))]
    x = np.arange(len(groups)); w = 0.38
    cvals = [abl[k][0] for _, k in groups]; uvals = [abl[k][1] for _, k in groups]
    ax[1].bar(x-w/2, cvals, w, color="#d1495b", label="cued")
    ax[1].bar(x+w/2, uvals, w, color="#3f88c5", label="uncued")
    ax[1].set_xticks(x); ax[1].set_xticklabels([g for g, _ in groups], fontsize=8)
    ax[1].set_ylabel("MT detector (test window)"); ax[1].legend()
    ax[1].set_title("Cooperative connection carries the bias\n(cued > uncued, survives swap)")
    for xi, (cv, uv) in enumerate(zip(cvals, uvals)):
        ax[1].text(xi, max(cv, uv)+0.02*max(cvals), f"{cv/max(uv,1e-3):.2f}x",
                   ha="center", fontsize=8, color="#7a2030")
    # (c) density sweep
    ax[2].plot(densities, curves[False][0], "--o", color="#d1495b", mfc="w", label="cued, no-swap")
    ax[2].plot(densities, curves[False][1], "--s", color="#3f88c5", mfc="w", label="uncued, no-swap")
    ax[2].plot(densities, curves[True][0], "-o", color="#d1495b", label="cued, swap")
    ax[2].plot(densities, curves[True][1], "-s", color="#3f88c5", label="uncued, swap")
    ax[2].set_xlabel("dots per field (density)"); ax[2].set_ylabel("MT detector response")
    ax[2].legend(fontsize=8); ax[2].set_title("Cued advantage vs density")
    fig.tight_layout(); p1 = os.path.join(FIGS, "ps_wire_detector.png")
    fig.savefig(p1, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p1)

    # ---- FIGURE 2: V1 spatial activation + MT bars, cued vs uncued, base frame & translation frame ----
    np.random.seed(3)
    MTc, V1c, _ = simulate(60, "cued", UP, True, COOPG, FBG, keep=True)
    np.random.seed(3)
    MTu, V1u, _ = simulate(60, "uncued", UP, True, COOPG, FBG, keep=True)
    f_base, f_test = 30, 43                                   # a base-motion frame, a translation frame
    fig, ax = plt.subplots(2, 5, figsize=(18, 7.2))
    for row, (V1f, MTf, who) in enumerate([(V1c, MTc, "CUED translates"), (V1u, MTu, "UNCUED translates")]):
        for d in range(4):
            im = ax[row, d].imshow(V1f[f_test][:, :, d].T, origin="lower", cmap="magma",
                                   vmin=0, vmax=0.9, extent=[-R_AP, R_AP, -R_AP, R_AP])
            ax[row, d].set_title(f"V1 {DIRLAB[d]}", fontsize=9); ax[row, d].set_xticks([]); ax[row, d].set_yticks([])
            if d == UP:
                ax[row, d].set_ylabel(who, fontsize=10)
        axb = ax[row, 4]
        axb.bar(range(4), MTf[f_test], color=["#888", "#e0a800", "#888", "#e0a800"])
        axb.set_xticks(range(4)); axb.set_xticklabels(DIRLAB)
        axb.set_title(f"MT (frame {f_test}, translation)\ndet(U−D)={MTf[f_test, UP]-MTf[f_test, DOWN]:.2f}", fontsize=9)
        axb.set_ylim(0, max(MTc[:, :].max(), MTu[:, :].max())*1.05)
    fig.suptitle("V1 (up channel, gold-boxed) shows the cooperative base→translation transfer is stronger for the CUED field — SWAP trial, frame 43", fontsize=11)
    fig.tight_layout(); p2 = os.path.join(FIGS, "ps_wire_v1mt.png")
    fig.savefig(p2, dpi=110, bbox_inches="tight"); plt.close(fig)
    print("figure ->", p2)
