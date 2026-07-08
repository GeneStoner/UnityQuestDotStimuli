"""Report cued vs uncued MT responses (swap & no-swap) + the learned connectivity,
for a single network trained 50/50 on swap and no-swap trials."""
import os
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ps_train as P

torch.manual_seed(3); np.random.seed(3)
FIGS = os.path.join(P.HERE, "figs")


def gen(bs, force=None):
    drive = np.zeros((bs, P.T, P.L, P.D), np.float32); cued = np.zeros(bs, np.int64)
    for b in range(bs):
        PA = np.sort(np.random.choice(P.L, P.L//2, replace=False))
        PB = np.array([p for p in range(P.L) if p not in PA])
        dA0 = np.random.randint(2); dB0 = 1-dA0
        swap = (np.random.rand() < 0.5) if force is None else force
        for t in range(P.T):
            dA, dB = (dA0, dB0) if (not swap or t < P.T_SWAP) else (dB0, dA0)
            drive[b, t, PA, dA] = 1.0
            if t >= P.T_ON:
                drive[b, t, PB, dB] = 1.0
        cued[b] = dA0 if swap else dB0
    return torch.tensor(drive, device=P.DEV), torch.tensor(cued, device=P.DEV)


# --- train 50/50 with trainable V1 cooperation (lat init = 0) ---
net = P.VMT(use_lat=True).to(P.DEV)
opt = torch.optim.Adam(net.parameters(), lr=5e-3)
for s in range(2500):
    d, c = gen(64); loss = F.cross_entropy(net(d), c)
    opt.zero_grad(); loss.backward(); opt.step()

# --- responses ---
res = {}
for force, lab in [(False, "no-swap"), (True, "swap")]:
    d, c = gen(4000, force=force)
    with torch.no_grad():
        meff = net(d)
    idx = torch.arange(len(c))
    cued_r = meff[idx, c].mean().item()
    unc_r = meff[idx, 1-c].mean().item()
    acc = (meff.argmax(1) == c).float().mean().item()
    res[lab] = (cued_r, unc_r, acc)
    print(f"{lab:8s}:  cued {cued_r:6.2f}   uncued {unc_r:6.2f}   ratio {cued_r/max(unc_r,1e-3):5.2f}x   cued-wins {acc*100:.0f}%")

print("\n--- LEARNED connectivity (2x2 direction matrices) ---")
ff = net.ff.detach().cpu().numpy(); fb = net.fb.detach().cpu().numpy(); lat = net.lat.detach().cpu().numpy()
print(f"ff  (V1->MT, init=I):\n{np.round(ff,2)}")
print(f"fb  (MT->V1, init=I):\n{np.round(fb,2)}   fbg={net.fbg.item():.2f}")
print(f"lat (V1 lateral, init=0):\n{np.round(lat,2)}   coopg={net.coopg.item():.2f}")
print("(ADAPTATION dynamics are FIXED, not trained; architecture is designed; ff/fb init like-to-like; lat init exactly 0)")

# --- figure ---
fig, ax = plt.subplots(figsize=(6.5, 4.2))
labels = ["no-swap", "swap"]; x = np.arange(2); w = 0.35
ax.bar(x-w/2, [res[l][0] for l in labels], w, color="#d1495b", label="CUED translation")
ax.bar(x+w/2, [res[l][1] for l in labels], w, color="#3f88c5", label="UNCUED translation")
for i, l in enumerate(labels):
    ax.text(i, max(res[l][0], res[l][1])+0.1, f"{100*res[l][2]:.0f}% cued>uncued", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel("MT response")
ax.set_title("Cued vs uncued MT response (trained 50/50, V1 cooperation learned from lat=0)")
ax.legend()
fig.tight_layout(); p = os.path.join(FIGS, "mt1_report.png")
fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
print("\nfigure ->", p)
