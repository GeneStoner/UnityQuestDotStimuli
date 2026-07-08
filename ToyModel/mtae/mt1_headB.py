"""
Head B on the one-MT-hypercolumn model: TRAIN a readout to amplify the CUED
(delayed-field) translation, with a swap on every trial and adaptation in the MT
units (feature-based).

The tension (from mt1_adapt.py): MT feature-adaptation makes the delayed field
dominate BEFORE the swap, but the swap inverts it — post-swap the raw MT response
favors the UNCUED field's direction. So a readout can only amplify the cued
translation if it uses the TEMPORAL onset history (the cued field's direction is
the one that was active early, before the delayed onset), overriding the
misleading late adaptation signal.

We compare:
  - RECURRENT readout (GRU over the MT time course) — has the history,
  - FEEDFORWARD readout (final MT state only) — the control that should fail.

Target: response at the cued direction amplified ~1.5x vs the uncued direction.

Run: /usr/bin/python3 mt1_headB.py
"""
import os, time
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

torch.manual_seed(0); np.random.seed(0)
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
HERE = os.path.dirname(os.path.abspath(__file__)); FIGS = os.path.join(HERE, "figs")
T, BETA, DECAY, AMP = 60, 0.25, 0.06, 1.5


def gen_trial():
    """MT hypercolumn time course (T,2) with feature adaptation; return seq + cued dir."""
    d1 = np.random.randint(2)           # continuous field's initial direction
    d2 = 1 - d1                          # delayed field opposite
    t_on2 = np.random.randint(12, 18)
    t_swap = np.random.randint(26, 36)
    a = np.zeros(2); mt = np.zeros((T, 2), np.float32)
    for t in range(T):
        c1, c2 = (d1, d2) if t < t_swap else (d2, d1)     # swap exchanges directions
        drive = np.zeros(2)
        drive[c1] += 8.0
        if t >= t_on2:
            drive[c2] += 8.0
        r = drive / (1.0 + a)
        a = a + BETA*r - DECAY*a
        mt[t] = r
    d_cued = c2          # delayed field's direction AT JUDGMENT (post-swap) == d1 (early dir)
    return mt, d_cued


def batch(bs):
    seqs, lab = zip(*[gen_trial() for _ in range(bs)])
    return (torch.tensor(np.stack(seqs), device=DEV),
            torch.tensor(np.array(lab), device=DEV, dtype=torch.long))


class Recurrent(nn.Module):
    def __init__(self, h=16):
        super().__init__(); self.gru = nn.GRU(2, h, batch_first=True); self.out = nn.Linear(h, 2)
    def forward(self, x):
        o, _ = self.gru(x); return torch.relu(self.out(o[:, -1]))


class Feedforward(nn.Module):
    def __init__(self, h=16):
        super().__init__(); self.net = nn.Sequential(nn.Linear(2, h), nn.ReLU(), nn.Linear(h, 2))
    def forward(self, x):
        return torch.relu(self.net(x[:, -1]))          # final MT state only


def target(lab):
    t = torch.ones(lab.shape[0], 2, device=DEV)
    t[torch.arange(lab.shape[0]), lab] = AMP           # amplify cued direction
    return t


def train(model, steps=2000, bs=64, lr=3e-3):
    opt = torch.optim.Adam(model.parameters(), lr=lr); t0 = time.time()
    for s in range(steps):
        x, lab = batch(bs)
        loss = ((model(x) - target(lab))**2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return model


@torch.no_grad()
def evaluate(model, n=2000):
    x, lab = batch(n); out = model(x)
    cued = out[torch.arange(n), lab]
    unc = out[torch.arange(n), 1-lab]
    acc = (cued > unc).float().mean().item()
    return cued.mean().item(), unc.mean().item(), acc


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}  target amplification {AMP}x  (cued vs uncued direction)\n")
    results = {}
    for name, Model in [("RECURRENT (has history)", Recurrent), ("FEEDFORWARD (final MT only)", Feedforward)]:
        m = train(Model().to(DEV))
        c, u, acc = evaluate(m)
        results[name] = (c, u, acc)
        print(f"{name:28s}  cued {c:.2f}  uncued {u:.2f}  ratio {c/max(u,1e-3):.2f}x  cued>uncued {100*acc:.0f}%")

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    names = list(results); x = np.arange(len(names)); w = 0.35
    ax.bar(x-w/2, [results[n][0] for n in names], w, color="#d1495b", label="cued direction")
    ax.bar(x+w/2, [results[n][1] for n in names], w, color="#3f88c5", label="uncued direction")
    ax.axhline(AMP, color="#d1495b", ls=":", lw=1); ax.axhline(1.0, color="#3f88c5", ls=":", lw=1)
    for i, n in enumerate(names):
        ax.text(i, max(results[n][:2])+0.05, f"{100*results[n][2]:.0f}% correct", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels([n.split(" (")[0] for n in names])
    ax.set_ylabel("trained readout response"); ax.legend()
    ax.set_title("Head B: amplify CUED translation through a swap\n(MT feature-adaptation; dotted = targets 1.5 / 1.0)")
    fig.tight_layout(); p = os.path.join(FIGS, "mt1_headB.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p)
