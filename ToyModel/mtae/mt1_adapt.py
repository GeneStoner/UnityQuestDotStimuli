"""
Drastically simplified model: ONE MT hypercolumn.

- MT = a single hypercolumn (full-field RF), D direction-tuned units, with ADAPTATION.
- V1 = a row of L retinotopic hypercolumns (same D directions) that supply MT.
- Stimulus: two left/right translating dot fields sized to the MT RF. One field is
  DELAYED (the cue); the continuous field's direction has been driving MT and adapts,
  so when the delayed field arrives its (fresh) direction unit responds LARGER -> the
  cued field dominates MT. That is the cueing effect, mechanistically.
- SWAP on the trial: the two fields exchange motion at t_swap.
- KEY KNOB: where adaptation lives.
    'feature'  -> adaptation on MT direction units  -> swap INVERTS the cue.
    'position' -> adaptation on V1 positions (the field's dots) -> cue SURVIVES the swap.

This script is the MECHANISM DEMO (forward only, no training yet): show the delayed
field gets a larger response, and how the swap interacts with adaptation locus.

Run: /usr/bin/python3 mt1_adapt.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(0)
HERE = os.path.dirname(os.path.abspath(__file__)); FIGS = os.path.join(HERE, "figs")

L = 16            # V1 positions across the MT RF
D = 2             # directions: 0 = rightward, 1 = leftward
T = 60            # timesteps
T_ONSET2 = 15     # delayed field onset
T_SWAP = 35       # motion swap
BETA, DECAY = 0.25, 0.06   # adaptation accrue / decay rates


def simulate(adapt="feature", swap=True):
    """Return per-timestep response attributed to the CUED (delayed) and UNCUED fields."""
    # two fields occupy disjoint position subsets, sized to fill the RF
    P1 = np.sort(np.random.choice(L, L//2, replace=False))          # continuous field
    P2 = np.array([p for p in range(L) if p not in P1])             # delayed field
    dir1, dir2 = 0, 1                                               # field1 right, field2 left

    a_feat = np.zeros(D)    # MT feature (direction) adaptation
    a_pos = np.zeros(L)     # V1 position adaptation
    cued, uncued = [], []   # response attributed to each field (object-tracked)

    for t in range(T):
        # current motion direction of each field (swap exchanges them)
        d1, d2 = (dir1, dir2)
        if swap and t >= T_SWAP:
            d1, d2 = dir2, dir1

        # V1 drive: each present field drives its direction channel at its positions
        V1 = np.zeros((L, D))
        V1[P1, d1] = 1.0
        present2 = t >= T_ONSET2
        if present2:
            V1[P2, d2] = 1.0

        # apply gain (adaptation) and pool V1 -> MT; attribute response back to each field
        if adapt == "feature":
            gain_d = 1.0 / (1.0 + a_feat)                          # per-direction gain
            r1 = len(P1) * gain_d[d1]
            r2 = (len(P2) * gain_d[d2]) if present2 else 0.0
            # update MT feature adaptation from total per-direction drive
            drive_d = V1.sum(0)
            a_feat = a_feat + BETA*(drive_d*gain_d) - DECAY*a_feat
        else:  # position adaptation (on V1 dots / the field)
            gain_p = 1.0 / (1.0 + a_pos)                           # per-position gain
            r1 = gain_p[P1].sum()
            r2 = gain_p[P2].sum() if present2 else 0.0
            active = V1.sum(1)                                     # which positions are driven
            a_pos = a_pos + BETA*(active*gain_p) - DECAY*a_pos

        cued.append(r2)      # field2 = delayed = CUED
        uncued.append(r1)    # field1 = continuous = UNCUED
    return np.array(cued), np.array(uncued)


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for k, mode in enumerate(["feature", "position"]):
        cued, uncued = simulate(adapt=mode, swap=True)
        ax[k].plot(cued, "-o", ms=3, color="#d1495b", label="CUED (delayed) field")
        ax[k].plot(uncued, "-s", ms=3, color="#3f88c5", label="UNCUED (continuous) field")
        ax[k].axvline(T_ONSET2, color="gray", ls=":", lw=1); ax[k].text(T_ONSET2+.4, ax[k].get_ylim()[1]*0.02, "delayed onset", fontsize=8, rotation=90, va="bottom")
        ax[k].axvline(T_SWAP, color="k", ls="--", lw=1); ax[k].text(T_SWAP+.4, ax[k].get_ylim()[1]*0.02, "swap", fontsize=8, rotation=90, va="bottom")
        ax[k].set_title(f"adaptation on {mode.upper()}"); ax[k].set_xlabel("timestep")
        if k == 0: ax[k].set_ylabel("MT response attributed to field"); ax[k].legend(fontsize=9)
    fig.suptitle("One-MT-hypercolumn cueing: delayed field dominates via adaptation; swap survival depends on adaptation locus", fontsize=11)
    fig.tight_layout(); p = os.path.join(FIGS, "mt1_adapt.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)

    # quick numbers: cued advantage just after delayed onset, and just after swap
    for mode in ["feature", "position"]:
        c, u = simulate(adapt=mode, swap=True)
        pre = slice(T_ONSET2+2, T_SWAP)          # after onset, before swap
        post = slice(T_SWAP+2, T)                # after swap
        print(f"adapt={mode:8s}  cued-uncued  pre-swap {np.mean(c[pre]-u[pre]):+.2f}   post-swap {np.mean(c[post]-u[post]):+.2f}")
    print("figure ->", p)
