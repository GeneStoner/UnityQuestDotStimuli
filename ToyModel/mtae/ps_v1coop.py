"""
Replicate the PS cued-swap result: cooperation in the V1 HYPERCOLUMNS links the
successive motions, carrying the cued object's enhancement through a feature swap.

- ONE MT hypercolumn (full-field RF), D direction units, with ADAPTATION -> the
  delayed (cued) field's fresh direction dominates MT (the cue).
- MT->V1 like-to-like MULTIPLICATIVE feedback: MT's favored direction gains up the
  matching V1 units.
- V1 COOPERATION (within each hypercolumn, across directions) + activity persistence:
  an enhanced unit facilitates the OTHER direction units at the SAME location. When a
  dot's motion swaps, the lingering enhancement of its old-direction unit cooperatively
  boosts its NEW-direction unit at that location -> enhancement follows the dot (the
  object), surviving the feature swap. This is the "cooperation links successive motions".

We compare cooperation ON vs OFF: OFF -> feedback follows the feature and the swap
INVERTS the cue; ON -> the cued object's enhancement SURVIVES the swap.

Run: /usr/bin/python3 ps_v1coop.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(1)
HERE = os.path.dirname(os.path.abspath(__file__)); FIGS = os.path.join(HERE, "figs")

L, D = 32, 2                 # V1 positions (hypercolumns), directions (0=right,1=left)
T, T_ON, T_SWAP = 60, 12, 32
ALPHA = 0.35                 # V1 update rate (1-ALPHA = persistence)
FB = 0.8                     # MT->V1 like-to-like multiplicative feedback strength
BETA, DECAY = 0.25, 0.06     # MT adaptation


def run(coop=0.5):
    PA = np.sort(np.random.choice(L, L//2, replace=False))       # continuous field
    PB = np.array([p for p in range(L) if p not in PA])          # delayed (cued) field
    v = np.zeros((L, D)); a = np.zeros(D)
    cued, uncued = [], []
    for t in range(T):
        dA, dB = (0, 1) if t < T_SWAP else (1, 0)                 # swap exchanges motions
        drive = np.zeros((L, D))
        drive[PA, dA] = 1.0
        present_B = t >= T_ON
        if present_B:
            drive[PB, dB] = 1.0
        # MT: pool drive, adapt -> fresh (cued) direction dominates
        md = drive.sum(0)
        meff = md / (1.0 + a)
        a = a + BETA*meff - DECAY*a
        fbg = 1.0 + FB*meff                                      # like-to-like feedback gain (per dir)
        # V1 cooperation: co-located other-direction activity facilitates each unit
        coop_in = coop * (v.sum(1, keepdims=True) - v)
        target = drive * fbg[None, :] + coop_in
        v = np.clip(v + ALPHA*(target - v), 0, None)
        cued.append(v[PB, dB].mean() if present_B else 0.0)      # cued object, its CURRENT motion
        uncued.append(v[PA, dA].mean())
    return np.array(cued), np.array(uncued)


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), sharey=True)
    for k, (coop, title) in enumerate([(0.0, "cooperation OFF"), (0.5, "cooperation ON (V1)")]):
        c, u = run(coop=coop)
        ax[k].plot(c, "-o", ms=3, color="#d1495b", label="CUED object")
        ax[k].plot(u, "-s", ms=3, color="#3f88c5", label="UNCUED object")
        ax[k].axvline(T_ON, color="gray", ls=":", lw=1)
        ax[k].axvline(T_SWAP, color="k", ls="--", lw=1)
        ax[k].text(T_ON+.4, 0.02, "delayed onset", rotation=90, fontsize=8, va="bottom")
        ax[k].text(T_SWAP+.4, 0.02, "swap", rotation=90, fontsize=8, va="bottom")
        post = slice(T_SWAP+2, T)
        ax[k].set_title(f"{title}\ncued−uncued after swap: {np.mean(c[post]-u[post]):+.2f}")
        ax[k].set_xlabel("timestep")
        if k == 0:
            ax[k].set_ylabel("V1 response on the object's dots"); ax[k].legend(fontsize=9)
    fig.suptitle("PS cued-swap replication: V1 cooperation links successive motions -> cued enhancement survives the swap", fontsize=11)
    fig.tight_layout(); p = os.path.join(FIGS, "ps_v1coop.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)

    for coop in [0.0, 0.5]:
        c, u = run(coop=coop)
        pre = slice(T_ON+2, T_SWAP); post = slice(T_SWAP+2, T)
        print(f"coop={coop}:  cued-uncued  pre-swap {np.mean(c[pre]-u[pre]):+.2f}   post-swap {np.mean(c[post]-u[post]):+.2f}")
    print("figure ->", p)
