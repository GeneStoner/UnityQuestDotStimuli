"""
Faithful stimulus + TRAINED recurrent V1<->MT network (GS spec):
 - MT direction adaptation (feature-based, as specified),
 - MULTIPLICATIVE feedback (MT->V1),
 - trained V1 LATERAL (cross-direction, co-located) + feedforward,
 - divisive normalization for stability,
 - spatial V1 (P positions x 4 directions R/U/L/D), one MT hypercolumn.
Stimulus: two fields opposite base motion (L/R), delayed-onset cue, brief ORTHOGONAL
(U/D) translation at 50% coherence, optional motion swap, density range.
Task: read out the translation direction (U vs D) from MT. Then measure whether the
CUED field's translation is detected/represented more strongly than the UNCUED — and
whether training discovered the cross-direction lateral that lets MT-base-adaptation
reach the orthogonal translation.

Run:            /usr/bin/python3 real_train.py
Retrain:  RETRAIN=1 /usr/bin/python3 real_train.py
"""
import os, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0); np.random.seed(0)
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
HERE = os.path.dirname(os.path.abspath(__file__))
P, ND = 32, 4                                   # positions, directions (0R,1U,2L,3D)
R_, U_, L_, D_ = 0, 1, 2, 3
T, T_ON, T_T0, T_T1 = 48, 10, 30, 40
BETA, DECAY, ALPHA, SIG = 0.22, 0.03, 0.4, 1.0
COH = 0.5


def gen_batch(bs, dens=(8, 24)):
    drive = np.zeros((bs, T, P, ND), np.float32)
    label = np.zeros(bs, np.int64)              # 0=U signal, 1=D signal
    meta = []                                   # (translate_cued, swap, n)
    for b in range(bs):
        n = np.random.randint(*dens)
        idx = np.random.permutation(P)
        PA, PB = idx[:n], idx[n:2*n]
        signal = U_ if np.random.rand() < 0.5 else D_
        cued = np.random.rand() < 0.5           # True: cued(B) translates; False: uncued(A)
        swap = np.random.rand() < 0.5
        cohM = np.random.rand(2*n) < COH
        for t in range(T):
            bA, bB = (L_, R_) if not (swap and t >= T_T0) else (R_, L_)
            dA = np.full(len(PA), bA); dB = np.full(len(PB), bB)
            if T_T0 <= t < T_T1:
                if cued:
                    rnd = np.random.randint(0, ND, len(PB))
                    dB = np.where(cohM[len(PA):len(PA)+len(PB)], signal, rnd)
                else:
                    rnd = np.random.randint(0, ND, len(PA))
                    dA = np.where(cohM[:len(PA)], signal, rnd)
            drive[b, t, PA, dA] = 1.0
            if t >= T_ON:
                drive[b, t, PB, dB] = 1.0
        label[b] = 0 if signal == U_ else 1
        meta.append((cued, swap, n))
    return torch.tensor(drive, device=DEV), torch.tensor(label, device=DEV), meta


def divnorm(r, sigma=SIG):
    r = F.relu(r)
    return r / (sigma + r.sum(-1, keepdim=True))


class VMT4(nn.Module):
    def __init__(self):
        super().__init__()
        self.ff = nn.Parameter(torch.eye(ND))
        self.fb = nn.Parameter(torch.eye(ND))
        self.lat = nn.Parameter(torch.zeros(ND, ND))
        self.fbg = nn.Parameter(torch.tensor(1.0))
        self.coopg = nn.Parameter(torch.tensor(0.5))
        self.read = nn.Linear(ND, 2)                       # translation detector: U vs D

    def forward(self, drive, return_mt=False):
        bs = drive.shape[0]
        v = torch.zeros(bs, P, ND, device=drive.device)
        a = torch.zeros(bs, ND, device=drive.device)
        mt_acc = torch.zeros(bs, ND, device=drive.device); cnt = 0
        for t in range(T):
            s = drive[:, t]
            m_drive = torch.einsum("bpd,de->be", v, self.ff) / 8.0   # scale pooling for stability
            m_eff = m_drive / (1.0 + a)
            a = a + BETA*m_eff - DECAY*a
            fbgain = 1.0 + self.fbg*F.relu(m_eff @ self.fb)          # (bs,ND) multiplicative
            coop = self.coopg * torch.einsum("bpd,de->bpe", v, self.lat)
            v = v + ALPHA*(divnorm(s*fbgain[:, None, :] + coop) - v)
            if T_T0 <= t < T_T1:
                mt_acc = mt_acc + m_eff; cnt += 1
        mt = mt_acc / max(cnt, 1)
        logits = self.read(mt)
        return (logits, mt) if return_mt else logits


def train(steps=2500, bs=32, lr=1.5e-3):
    net = VMT4().to(DEV); opt = torch.optim.Adam(net.parameters(), lr=lr)
    t0 = time.time()
    for s in range(steps):
        d, lab, _ = gen_batch(bs)
        loss = F.cross_entropy(net(d), lab)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
        if s % 300 == 0 or s == steps-1:
            print(f"  step {s:4d}  loss {loss.item():.4f}  ({time.time()-t0:.0f}s)")
    return net


@torch.no_grad()
def evaluate(net, n_trials=3000):
    d, lab, meta = gen_batch(n_trials)
    logits, mt = net(d, return_mt=True)
    pred = logits.argmax(1); correct = (pred == lab)
    meta = np.array(meta)                                  # cols: cued, swap, n
    cued = meta[:, 0].astype(bool); swap = meta[:, 1].astype(bool)
    # translation-detector magnitude = response to the signal direction
    sigdir = torch.where(lab == 0, torch.full_like(lab, U_), torch.full_like(lab, D_))
    sig_resp = mt[torch.arange(len(lab)), sigdir].cpu().numpy()
    out = {}
    for sw in [True, False]:
        for cu in [True, False]:
            mask = (swap == sw) & (cued == cu)
            out[(sw, cu)] = (correct.cpu().numpy()[mask].mean(), sig_resp[mask].mean())
    return out


if __name__ == "__main__":
    print(f"device={DEV}  spatial V1={P}x{ND}, MT adaptation, mult. feedback, trained lateral")
    ckpt = os.path.join(HERE, "real_train.pt")
    if os.environ.get("RETRAIN", "0") == "0" and os.path.exists(ckpt):
        print("loading cached checkpoint...")
        net = VMT4().to(DEV); net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training..."); net = train(); torch.save(net.state_dict(), ckpt)

    out = evaluate(net)
    print("\n            translation-detection acc   |   MT signal response")
    for sw in [True, False]:
        for cu in [True, False]:
            acc, resp = out[(sw, cu)]
            print(f"  {'SWAP  ' if sw else 'NOSWAP'} {'CUED  ' if cu else 'UNCUED'} translates:   acc {acc*100:5.1f}%      resp {resp:.2f}")
    # cued advantage
    for sw in [True, False]:
        rc = out[(sw, True)][1]; ru = out[(sw, False)][1]
        print(f"  {'swap' if sw else 'no-swap'}: cued/uncued MT response ratio = {rc/max(ru,1e-6):.2f}x")
    lat = net.lat.detach().cpu().numpy()
    print("\nlearned V1 lateral (rows/cols = R,U,L,D)  coopg={:.2f}:".format(net.coopg.item()))
    print(np.round(lat, 2))
    print("(base dirs = R,L ; translation dirs = U,D ; base->translation coupling = the key learned transfer)")
