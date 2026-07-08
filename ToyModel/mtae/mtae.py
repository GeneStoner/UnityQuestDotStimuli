"""
MT autoencoder toy model for object-based attention in transparent motion.

Premise (Cavanagh et al. 2023, "Architecture of Object-Based Attention"):
object-based attention's feedback-specificity is a *byproduct* of an
autoencoder that reconstructs its own early-visual input. Here the "object
area" is MT: a coarse-retinotopic, direction-tuned bottleneck trained
unsupervised to reproduce a V1 motion-energy population evoked by two
overlapping transparent dot surfaces.

Nothing about surface identity is supplied. The bet (GS): the bottleneck
learns the common-fate statistic on its own because a coherent field is the
compressible structure. We then test whether that learned code supports
surface-selective feedback ("cueing") and whether it breaks down with density.

Run:  /usr/bin/python3 mtae.py
"""
import math, os, time
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

# ---- geometry / representation -------------------------------------------
H = W = 32                 # V1 retinotopic grid
D = 8                      # V1 direction channels
R = 14.0                   # aperture radius (grid units)
SIG_SPACE = 0.9            # dot blob sigma (V1 RF, grid units)
KAPPA = 2.5                # von Mises direction tuning width
CHAN_DIR = np.arange(D) * 2 * np.pi / D   # preferred dir of each V1 channel

yy, xx = np.mgrid[0:H, 0:W]
cx = cy = (H - 1) / 2.0
APER = ((xx - cx) ** 2 + (yy - cy) ** 2) <= R ** 2      # bool aperture mask
APER_T = torch.tensor(APER[None, None].astype(np.float32), device=DEV)


def render_surface(pos, theta):
    """One surface -> (D,H,W) V1 motion-energy. pos:(M,2) in grid coords."""
    M = pos.shape[0]
    if M == 0:
        return np.zeros((D, H, W), np.float32)
    dx = xx[None] - pos[:, 0, None, None]
    dy = yy[None] - pos[:, 1, None, None]
    blob = np.exp(-(dx * dx + dy * dy) / (2 * SIG_SPACE ** 2))       # (M,H,W)
    wdir = np.exp(KAPPA * np.cos(theta - CHAN_DIR))                   # (D,)
    wdir = wdir / wdir.max()
    energy = np.einsum("d,mhw->dhw", wdir, blob).astype(np.float32)   # (D,H,W)
    return energy


def sample_dots(n):
    """n dot positions uniformly inside the aperture."""
    pts = []
    while len(pts) < n:
        p = np.random.rand(2) * [W, H]
        if (p[0] - cx) ** 2 + (p[1] - cy) ** 2 <= R ** 2:
            pts.append(p)
    return np.array(pts, np.float32)


def make_clip(n_per_surface, min_sep_deg=45, single=None, dirs=None):
    """Two transparent surfaces, coherent opposed-ish translation.

    single: if 0 or 1, render only that surface (for probing).
    dirs:   optional (thetaA,thetaB) to fix directions.
    Returns V1 tensor (D,H,W) and per-surface ground-truth (2,D,H,W) + dirs.
    """
    if dirs is None:
        tA = np.random.rand() * 2 * np.pi
        while True:
            tB = np.random.rand() * 2 * np.pi
            d = abs((tB - tA + np.pi) % (2 * np.pi) - np.pi)
            if math.degrees(d) >= min_sep_deg:
                break
    else:
        tA, tB = dirs
    posA, posB = sample_dots(n_per_surface), sample_dots(n_per_surface)
    gtA, gtB = render_surface(posA, tA), render_surface(posB, tB)
    gt = np.stack([gtA, gtB])
    if single == 0:
        v1 = gtA
    elif single == 1:
        v1 = gtB
    else:
        v1 = gtA + gtB
    v1 = v1 * APER[None]
    return v1.astype(np.float32), gt * APER[None], (tA, tB)


def batch(bs, n_range=(15, 55)):
    xs = []
    for _ in range(bs):
        n = np.random.randint(*n_range)
        v1, _, _ = make_clip(n)
        xs.append(v1)
    return torch.tensor(np.stack(xs), device=DEV)


# ---- MT autoencoder -------------------------------------------------------
class MTAutoencoder(nn.Module):
    """Coarse-retinotopic, direction-tuned bottleneck ('MT') reconstructing V1.

    Encoder downsamples 32->8 (bigger RFs); C_mt channels carry direction.
    Decoder upsamples back to the V1 grid. Pure reconstruction objective.
    """
    def __init__(self, C_mt=16, mt_grid=8):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv2d(D, 32, 3, 1, 1), nn.ReLU(),
            nn.Conv2d(32, 32, 4, 2, 1), nn.ReLU(),      # 32->16
            nn.Conv2d(32, C_mt, 4, 2, 1), nn.ReLU(),    # 16->8  (MT)
        )
        self.dec = nn.Sequential(
            nn.ConvTranspose2d(C_mt, 32, 4, 2, 1), nn.ReLU(),  # 8->16
            nn.ConvTranspose2d(32, 32, 4, 2, 1), nn.ReLU(),    # 16->32
            nn.Conv2d(32, D, 3, 1, 1),
        )
        self.C_mt, self.mt_grid = C_mt, mt_grid

    def encode(self, x): return self.enc(x)
    def decode(self, z): return torch.relu(self.dec(z))

    def forward(self, x):
        z = self.encode(x)
        return self.decode(z), z


def train(steps=3000, bs=32, lr=1e-3):
    net = MTAutoencoder().to(DEV)
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


# ---- diagnostics ----------------------------------------------------------
@torch.no_grad()
def mt_direction_pref(net, n_probe=24, n_dots=35):
    """Measure each MT unit's preferred direction from SINGLE-surface probes.
    Returns pref[C_mt,mt_grid,mt_grid] complex resultant, and tuning matrix."""
    dirs = np.linspace(0, 2 * np.pi, n_probe, endpoint=False)
    acc = None
    for th in dirs:
        # average MT response to many single fields of direction th
        zs = []
        for _ in range(8):
            v1, _, _ = make_clip(n_dots, single=0, dirs=(th, th))
            z = net.encode(torch.tensor(v1[None], device=DEV))
            zs.append(z[0].cpu().numpy())
        r = np.mean(zs, 0)                      # (C_mt,g,g)
        if acc is None:
            acc = np.zeros((len(dirs),) + r.shape, np.float32)
        acc[list(dirs).index(th)] = r
    # complex resultant over direction -> preferred dir + selectivity per unit
    w = acc  # (nd,C,g,g)
    phasor = np.exp(1j * dirs)[:, None, None, None]
    resultant = (w * phasor).sum(0) / (w.sum(0) + 1e-6)
    return resultant, acc, dirs


@torch.no_grad()
def cueing_selectivity(net, resultant, dirs, n_dots=35, n_trials=60):
    """Core test: can a direction-defined 'cue' pull out ONE surface?

    For each 2-surface clip we gate the MT code to units whose learned
    preferred direction is near the cued surface's direction, decode, and
    measure how much of each surface's ground-truth V1 the reconstruction
    recovers. Selectivity = corr(recon | cue A, surfA) - corr(recon | cueA, surfB).
    """
    pref_dir = np.angle(resultant)             # (C,g,g) preferred dir per MT unit
    sel_scores = []
    for _ in range(n_trials):
        v1, gt, (tA, tB) = make_clip(n_dots)
        x = torch.tensor(v1[None], device=DEV)
        z = net.encode(x)[0].cpu().numpy()      # (C,g,g)

        def gate_to(theta):
            # keep MT units tuned within 90 deg of cued dir, suppress others
            dd = np.abs((pref_dir - theta + np.pi) % (2 * np.pi) - np.pi)
            g = (np.cos(dd).clip(0, 1)) ** 2     # soft cosine gate
            zc = (z * g)[None].astype(np.float32)
            return net.decode(torch.tensor(zc, device=DEV))[0].cpu().numpy()

        recA, recB = gate_to(tA), gate_to(tB)
        gA = (gt[0] * APER[None]); gB = (gt[1] * APER[None])
        m = np.broadcast_to(APER[None].astype(bool), (D, H, W))
        def corr(a, b):
            a, b = a[m].ravel(), b[m].ravel()
            a = a - a.mean(); b = b - b.mean()
            return float((a * b).sum() / (np.sqrt((a*a).sum()*(b*b).sum()) + 1e-9))
        # cue A should favor surface A; cue B should favor surface B
        selA = corr(recA, gA) - corr(recA, gB)
        selB = corr(recB, gB) - corr(recB, gA)
        sel_scores.append(0.5 * (selA + selB))
    return float(np.mean(sel_scores)), float(np.std(sel_scores))


@torch.no_grad()
def density_sweep(net, resultant, dirs, densities=(10, 20, 35, 55, 80, 120)):
    out = []
    for n in densities:
        sel, sd = cueing_selectivity(net, resultant, dirs, n_dots=n, n_trials=40)
        # also recon error at this density
        errs = []
        for _ in range(20):
            v1, _, _ = make_clip(n)
            x = torch.tensor(v1[None], device=DEV)
            xhat, _ = net(x)
            errs.append((((xhat[0].cpu().numpy() - v1) ** 2) * APER[None]).mean())
        out.append((n, sel, sd, float(np.mean(errs))))
        print(f"  density {n:3d}/surface  selectivity {sel:+.3f}  reconMSE {np.mean(errs):.4f}")
    return out


# ---- figures --------------------------------------------------------------
def fig_recon(net, path):
    v1, gt, (tA, tB) = make_clip(35)
    x = torch.tensor(v1[None], device=DEV)
    with torch.no_grad():
        xhat, _ = net(x)
    xhat = xhat[0].cpu().numpy()
    fig, ax = plt.subplots(1, 3, figsize=(9, 3))
    for a, im, t in zip(ax, [v1.sum(0), xhat.sum(0), (v1 - xhat).sum(0)],
                        ["V1 input (Σ dir)", "MT-AE reconstruction", "residual"]):
        a.imshow(im, cmap="magma"); a.set_title(t); a.axis("off")
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def fig_cueing(net, resultant, path):
    v1, gt, (tA, tB) = make_clip(35)
    x = torch.tensor(v1[None], device=DEV)
    with torch.no_grad():
        z = net.encode(x)[0].cpu().numpy()
    pref_dir = np.angle(resultant)
    def gate_to(theta):
        dd = np.abs((pref_dir - theta + np.pi) % (2 * np.pi) - np.pi)
        g = (np.cos(dd).clip(0, 1)) ** 2
        with torch.no_grad():
            return net.decode(torch.tensor((z * g)[None].astype(np.float32), device=DEV))[0].cpu().numpy()
    recA, recB = gate_to(tA), gate_to(tB)
    panels = [(v1.sum(0), "V1 input (both surfaces)"),
              (gt[0].sum(0), f"surface A truth  ({math.degrees(tA):.0f}°)"),
              (recA.sum(0), "recon | cue A"),
              (gt[1].sum(0), f"surface B truth  ({math.degrees(tB):.0f}°)"),
              (recB.sum(0), "recon | cue B")]
    fig, ax = plt.subplots(1, 5, figsize=(15, 3))
    for a, (im, t) in zip(ax, panels):
        a.imshow(im * APER, cmap="magma"); a.set_title(t, fontsize=9); a.axis("off")
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def fig_density(sweep, path):
    n = [s[0] for s in sweep]; sel = [s[1] for s in sweep]
    sd = [s[2] for s in sweep]; err = [s[3] for s in sweep]
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.errorbar(n, sel, yerr=sd, marker="o", color="C0", label="cueing selectivity")
    ax1.axhline(0, color="gray", lw=0.8)
    ax1.set_xlabel("dots per surface (density)"); ax1.set_ylabel("cueing selectivity", color="C0")
    ax2 = ax1.twinx()
    ax2.plot(n, err, marker="s", color="C3", label="recon MSE")
    ax2.set_ylabel("reconstruction MSE", color="C3")
    ax1.set_title("Cueing selectivity vs density (MT-AE)")
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}")
    ckpt = os.path.join(HERE, "mtae.pt")
    if os.environ.get("RETRAIN", "0") == "0" and os.path.exists(ckpt):
        print("loading cached checkpoint (set RETRAIN=1 to retrain)...")
        net = MTAutoencoder().to(DEV)
        net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training MT autoencoder...")
        net = train(steps=3000)
        torch.save(net.state_dict(), ckpt)

    print("measuring MT direction preferences (unsupervised probe)...")
    resultant, acc, dirs = mt_direction_pref(net)
    frac_tuned = float((np.abs(resultant) > 0.2).mean())
    print(f"  fraction of MT units with clear direction tuning (|R|>0.2): {frac_tuned:.2f}")

    print("cueing selectivity @ density 35...")
    sel, sd = cueing_selectivity(net, resultant, dirs, n_dots=35)
    print(f"  selectivity = {sel:+.3f} +/- {sd:.3f}   (0 = no surface separation)")

    print("density sweep...")
    sweep = density_sweep(net, resultant, dirs)

    fig_recon(net, os.path.join(FIGS, "recon.png"))
    fig_cueing(net, resultant, os.path.join(FIGS, "cueing.png"))
    fig_density(sweep, os.path.join(FIGS, "density.png"))
    print("figures written to", FIGS)
