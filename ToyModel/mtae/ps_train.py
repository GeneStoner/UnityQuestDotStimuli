"""
TRAIN a V1<->MT network to produce a cued-swap effect in MT — and see what
solution training finds (PS-style V1 cooperation? something else? nothing?).

Architecture (D=2 directions, L V1 positions, ONE MT hypercolumn):
  - MT adaptation: FIXED (the cue source; the delayed field's fresh direction dominates).
  - TRAINABLE 2x2 connection matrices:
      ff  (V1->MT, like-to-like init),
      fb  (MT->V1 multiplicative gain, like-to-like init),
      lat (V1 co-located cross-direction cooperation, init 0)  <- where PS cooperation would appear.
  - Dynamics run over the trial (delayed onset + swap); V1 has activity persistence.
Objective: after the swap, MT should signal the CUED object's (post-swap) motion — even
though MT adaptation alone favors the UNCUED (fresh) direction. The only way to fix this is
to carry the cued object's identity through the swap; PS does it with V1 cooperation linking
successive motions (off-diagonal lat). Does training discover that?

Also trains a control with lat FROZEN at 0 (no cooperation) to show it's necessary.

Run: /usr/bin/python3 ps_train.py
"""
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0); np.random.seed(0)
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
HERE = os.path.dirname(os.path.abspath(__file__))
L, D, T, T_ON, T_SWAP = 32, 2, 48, 10, 28
BETA, DECAY, ALPHA = 0.25, 0.06, 0.35


def gen_batch(bs):
    """drive (bs,T,L,D) and cued post-swap direction label (bs,)."""
    drive = np.zeros((bs, T, L, D), np.float32); cued = np.zeros(bs, np.int64)
    for b in range(bs):
        PA = np.sort(np.random.choice(L, L//2, replace=False))
        PB = np.array([p for p in range(L) if p not in PA])
        dA0 = np.random.randint(2); dB0 = 1-dA0
        for t in range(T):
            dA, dB = (dA0, dB0) if t < T_SWAP else (dB0, dA0)
            drive[b, t, PA, dA] = 1.0
            if t >= T_ON:
                drive[b, t, PB, dB] = 1.0
        cued[b] = dA0                 # B's post-swap direction == A's initial direction
    return torch.tensor(drive, device=DEV), torch.tensor(cued, device=DEV)


class VMT(nn.Module):
    def __init__(self, use_lat=True):
        super().__init__()
        self.ff = nn.Parameter(torch.eye(D))          # V1->MT like-to-like init
        self.fb = nn.Parameter(torch.eye(D))          # MT->V1 like-to-like init
        self.lat = nn.Parameter(torch.zeros(D, D))    # V1 co-located cooperation, init 0
        self.fbg = nn.Parameter(torch.tensor(0.8))
        self.coopg = nn.Parameter(torch.tensor(0.5))
        self.use_lat = use_lat

    def forward(self, drive):
        bs = drive.shape[0]
        v = torch.zeros(bs, L, D, device=drive.device)
        a = torch.zeros(bs, D, device=drive.device)
        meff = torch.zeros(bs, D, device=drive.device)
        for t in range(T):
            dr = drive[:, t]                                  # (bs,L,D)
            mdrive = v.sum(1) @ self.ff                       # (bs,D)
            meff = mdrive / (1.0 + a)
            a = a + BETA*meff - DECAY*a
            fbgain = 1.0 + self.fbg*F.relu(meff @ self.fb)    # (bs,D)
            coop = self.coopg * torch.einsum("bli,ji->blj", v, self.lat) if self.use_lat else 0.0
            target = dr * fbgain[:, None, :] + coop
            v = F.relu(v + ALPHA*(target - v))
        return meff


def train(use_lat, steps=1500, bs=64, lr=5e-3):
    net = VMT(use_lat).to(DEV)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    for s in range(steps):
        drive, cued = gen_batch(bs)
        loss = F.cross_entropy(net(drive), cued)
        opt.zero_grad(); loss.backward(); opt.step()
    return net


@torch.no_grad()
def evaluate(net, n=2000):
    drive, cued = gen_batch(n)
    meff = net(drive)
    acc = (meff.argmax(1) == cued).float().mean().item()
    return acc


if __name__ == "__main__":
    print(f"device={DEV}  task: post-swap, does MT signal the CUED object's motion?\n")
    for use_lat, name in [(True, "trainable V1 cooperation"), (False, "NO V1 cooperation (control)")]:
        net = train(use_lat)
        acc = evaluate(net)
        print(f"[{name}]  cued-swap accuracy = {100*acc:.0f}%   (chance 50%)")
        if use_lat:
            ff = net.ff.detach().cpu().numpy(); fb = net.fb.detach().cpu().numpy()
            lat = net.lat.detach().cpu().numpy()
            print(f"   learned lat (V1 co-located coupling), coopg={net.coopg.item():.2f}:")
            print("     ", np.round(lat, 2).tolist(), " diag=self, OFF-DIAG=links successive motions")
            print(f"   learned ff diag/off: {np.round(np.diag(ff),2).tolist()} / {np.round(ff[0,1],2)},{np.round(ff[1,0],2)}")
            print(f"   learned fb diag/off: {np.round(np.diag(fb),2).tolist()} / {np.round(fb[0,1],2)},{np.round(fb[1,0],2)}  fbg={net.fbg.item():.2f}")
    print("\n(off-diagonal lat >> diagonal => training found the PS 'cooperation links successive motions' solution)")
