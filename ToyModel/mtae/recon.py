"""
Plain reconstruction autoencoder on transparent-motion dot stimuli.

Target = the dot IMAGE stack (positions / contrast map, as V1 simple cells see
it) -- NOT a motion-energy population. Two overlapping surfaces, each a coherent
translating dot field. Input = T-frame stack. An 'MT-ish' coarse bottleneck is
trained to reconstruct the stack. Goal for now: just see that reconstruction
works, trained over many seeds, tested on fresh stimuli.

Run:            /usr/bin/python3 recon.py          (uses cached recon.pt if present)
Retrain:  RETRAIN=1 /usr/bin/python3 recon.py
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
HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")

# ---- geometry -------------------------------------------------------------
H = W = 48
R = 20.0
SIG = 1.0                      # dot blob sigma (px)
T = 5                          # frames per clip
SPEED = 1.2                    # px / frame
N_PER = 40                     # medium density (dots per surface)

cx = cy = (H - 1) / 2.0
yy, xx = np.mgrid[0:H, 0:W]
APER = ((xx - cx) ** 2 + (yy - cy) ** 2) <= R ** 2
APER_T = torch.tensor(APER[None, None].astype(np.float32), device=DEV)   # (1,1,H,W)


def sample_dots(n):
    pts = []
    while len(pts) < n:
        p = np.random.rand(2) * [W, H]
        if (p[0] - cx) ** 2 + (p[1] - cy) ** 2 <= R ** 2:
            pts.append(p)
    return np.array(pts, np.float32)


def render(pos):
    """(M,2) dot centers -> (H,W) luminance via summed Gaussian blobs."""
    if pos.shape[0] == 0:
        return np.zeros((H, W), np.float32)
    dx = xx[None] - pos[:, 0, None, None]
    dy = yy[None] - pos[:, 1, None, None]
    blob = np.exp(-(dx * dx + dy * dy) / (2 * SIG ** 2))
    return blob.sum(0).astype(np.float32)


def make_clip(n_per=N_PER):
    """Two transparent surfaces, coherent random-direction translation -> (T,H,W)."""
    frames = []
    surfs = []
    for _ in range(2):
        th = np.random.rand() * 2 * np.pi
        vel = SPEED * np.array([np.cos(th), np.sin(th)], np.float32)
        pos0 = sample_dots(n_per)
        surfs.append((pos0, vel))
    for t in range(T):
        img = np.zeros((H, W), np.float32)
        for pos0, vel in surfs:
            img = img + render(pos0 + t * vel)
        frames.append(img * APER)
    return np.stack(frames).astype(np.float32)      # (T,H,W)


def batch(bs, n_per=N_PER):
    return torch.tensor(np.stack([make_clip(n_per) for _ in range(bs)]), device=DEV)


# ---- model ----------------------------------------------------------------
class ReconAE(nn.Module):
    """Coarse ('MT') bottleneck reconstructing the T-frame dot-image stack."""
    def __init__(self, C_mt=24):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv2d(T, 32, 3, 1, 1), nn.ReLU(),
            nn.Conv2d(32, 48, 4, 2, 1), nn.ReLU(),      # 48 -> 24
            nn.Conv2d(48, C_mt, 4, 2, 1), nn.ReLU(),    # 24 -> 12   (MT)
        )
        self.dec = nn.Sequential(
            nn.ConvTranspose2d(C_mt, 48, 4, 2, 1), nn.ReLU(),   # 12 -> 24
            nn.ConvTranspose2d(48, 32, 4, 2, 1), nn.ReLU(),     # 24 -> 48
            nn.Conv2d(32, T, 3, 1, 1),
        )

    def forward(self, x):
        z = self.enc(x)
        return torch.relu(self.dec(z)), z


def train(steps=4000, bs=32, lr=1e-3):
    net = ReconAE().to(DEV)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    t0 = time.time()
    for s in range(steps):
        x = batch(bs)
        xhat, _ = net(x)
        loss = (((xhat - x) ** 2) * APER_T).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if s % 500 == 0 or s == steps - 1:
            print(f"  step {s:4d}  loss {loss.item():.5f}  ({time.time()-t0:.0f}s)")
    return net


# ---- figures --------------------------------------------------------------
@torch.no_grad()
def fig_examples(net, seed0=1000, n=6, path=None):
    """Fresh test stimuli: input (mean over frames) vs reconstruction."""
    fig, ax = plt.subplots(3, n, figsize=(2.1 * n, 6.4))
    for j in range(n):
        np.random.seed(seed0 + j)
        clip = make_clip()
        x = torch.tensor(clip[None], device=DEV)
        xhat = net(x)[0][0].cpu().numpy()
        inp, rec = clip.mean(0), xhat.mean(0)
        resid = inp - rec
        for i, (im, t, cm) in enumerate([
                (inp, "input", "magma"), (rec, "reconstruction", "magma"),
                (resid, "residual", "coolwarm")]):
            a = ax[i, j]
            vlim = np.abs(resid).max() if i == 2 else None
            a.imshow(im, cmap=cm, vmin=(-vlim if vlim else None), vmax=(vlim if vlim else None))
            a.axis("off")
            if j == 0:
                a.set_ylabel(t, fontsize=11)
                a.axis("on"); a.set_xticks([]); a.set_yticks([])
        ax[0, j].set_title(f"test seed {seed0+j}", fontsize=9)
    fig.suptitle("MT-AE reconstruction on fresh (unseen) stimuli — mean over frames", y=1.02)
    fig.tight_layout(); fig.savefig(path, dpi=115, bbox_inches="tight"); plt.close(fig)


@torch.no_grad()
def fig_frames(net, seed=2001, path=None):
    """One fresh stimulus, per-frame: does motion survive reconstruction?"""
    np.random.seed(seed)
    clip = make_clip()
    x = torch.tensor(clip[None], device=DEV)
    xhat = net(x)[0][0].cpu().numpy()
    fig, ax = plt.subplots(2, T, figsize=(2.1 * T, 4.4))
    for t in range(T):
        ax[0, t].imshow(clip[t], cmap="magma"); ax[0, t].axis("off"); ax[0, t].set_title(f"frame {t}", fontsize=9)
        ax[1, t].imshow(xhat[t], cmap="magma"); ax[1, t].axis("off")
    ax[0, 0].set_ylabel("input", fontsize=11); ax[0, 0].axis("on"); ax[0, 0].set_xticks([]); ax[0, 0].set_yticks([])
    ax[1, 0].set_ylabel("recon", fontsize=11); ax[1, 0].axis("on"); ax[1, 0].set_xticks([]); ax[1, 0].set_yticks([])
    fig.suptitle(f"Per-frame reconstruction (fresh seed {seed})", y=1.0)
    fig.tight_layout(); fig.savefig(path, dpi=115, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}  grid={H}x{W}  T={T}  dots/surface={N_PER}")
    ckpt = os.path.join(HERE, "recon.pt")
    if os.environ.get("RETRAIN", "0") == "0" and os.path.exists(ckpt):
        print("loading cached checkpoint (RETRAIN=1 to retrain)...")
        net = ReconAE().to(DEV); net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training...")
        net = train(); torch.save(net.state_dict(), ckpt)

    # held-out reconstruction error over many fresh seeds
    errs = []
    with torch.no_grad():
        for s in range(500, 560):
            np.random.seed(s); clip = make_clip()
            x = torch.tensor(clip[None], device=DEV)
            xhat = net(x)[0][0].cpu().numpy()
            num = (((xhat - clip) ** 2) * APER[None]).sum()
            den = ((clip ** 2) * APER[None]).sum() + 1e-9
            errs.append(num / den)
    print(f"held-out normalized recon error (frac variance unexplained): {np.mean(errs):.3f} +/- {np.std(errs):.3f}")

    fig_examples(net, path=os.path.join(FIGS, "recon_examples.png"))
    fig_frames(net, path=os.path.join(FIGS, "recon_frames.png"))
    print("figures ->", FIGS)
