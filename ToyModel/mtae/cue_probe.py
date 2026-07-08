"""
Fair cueing probe for a trained head-A network.

The in-line cueing test assumed MT channel k == direction k, but training remaps
the MT->V1 kernel, so that clamp likely hit the wrong units. Here we:
  1. MEASURE each MT channel's preferred direction from single-surface probes,
  2. cue by boosting MT channels aligned to the cued surface's direction,
  3. sweep cue strength,
and ask whether the trained (reconstruction-only) feedback selectively enhances
the cued surface in V1 -- i.e. does object-based attention emerge for free.

Run: /usr/bin/python3 cue_probe.py
"""
import os
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import recurrent_scaffold as RS
import head_a_recon as HA

torch.set_grad_enabled(False)
DEV, FIGS = RS.DEV, RS.FIGS
NDIR, NDIR_MT, H, W = RS.NDIR, RS.NDIR_MT, RS.H, RS.W
MT_H, MT_W, APER = RS.MT_H, RS.MT_W, RS.APER

net = RS.RecurrentVMT().to(DEV)
net.load_state_dict(torch.load(os.path.join(RS.HERE, "head_a.pt"), map_location=DEV))
net.eval()


def settle(net, s, cue_vec=None, n_steps=40):
    """Thin wrapper over HA.settle (multiplicative feedback) with a per-channel MT cue."""
    return HA.settle(net, s, cue_channels=cue_vec, n_steps=n_steps)


def one_surface(th, n=30):
    pos = HA.sample_dots(n)
    return torch.tensor((HA.render_energy(pos, th)*APER[None])[None].astype(np.float32), device=DEV)


def measure_mt_pref(n_probe=16, n_trials=6):
    dirs = np.linspace(0, 2*np.pi, n_probe, endpoint=False)
    Rc = np.zeros(NDIR_MT, complex); den = np.zeros(NDIR_MT)
    for th in dirs:
        acc = np.zeros(NDIR_MT)
        for _ in range(n_trials):
            _, m = settle(net, one_surface(th))
            acc += m[0].mean((1, 2)).cpu().numpy()
        acc /= n_trials
        Rc += acc*np.exp(1j*th); den += acc
    pref = np.angle(Rc/(den+1e-9))
    sel = np.abs(Rc)/(den+1e-9)
    return pref, sel


def corr(a, b):
    m = np.broadcast_to(APER[None].astype(bool), a.shape)
    a, b = a[m], b[m]; a = a-a.mean(); b = b-b.mean()
    return float((a*b).sum()/(np.sqrt((a*a).sum()*(b*b).sum())+1e-9))


if __name__ == "__main__":
    pref, sel = measure_mt_pref()
    print("measured MT channel preferred directions (deg):",
          np.round(np.degrees(pref) % 360).astype(int))
    print("MT channel direction selectivity |R|:", np.round(sel, 2))

    def cue_vec(theta, strength):
        return (strength*np.clip(np.cos(pref-theta), 0, None)).astype(np.float32)

    print("\ncueing selectivity vs cue strength (fair probe, measured MT tuning):")
    best = (None, -1)
    for strength in [0.0, 0.5, 1.0, 2.0, 4.0]:
        sels = []
        for _ in range(60):
            d, c, surfs = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.0)
            (eA, tA), (eB, tB) = surfs
            s = torch.tensor(d[None], device=DEV)
            vA, _ = settle(net, s, cue_vec(tA, strength))
            vB, _ = settle(net, s, cue_vec(tB, strength))
            vA, vB = vA[0].cpu().numpy(), vB[0].cpu().numpy()
            sels.append(0.5*((corr(vA, eA)-corr(vA, eB)) + (corr(vB, eB)-corr(vB, eA))))
        mu, sd = float(np.mean(sels)), float(np.std(sels))
        print(f"  strength {strength:>4.1f}:  selectivity {mu:+.3f} +/- {sd:.3f}")
        if mu > best[1]: best = (strength, mu)

    # figure at best strength
    strength = best[0] if best[0] else 2.0
    np.random.seed(4242)
    d, c, surfs = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.0)
    (eA, tA), (eB, tB) = surfs
    s = torch.tensor(d[None], device=DEV)
    vA, _ = settle(net, s, cue_vec(tA, strength)); vB, _ = settle(net, s, cue_vec(tB, strength))
    vA, vB = vA[0].cpu().numpy(), vB[0].cpu().numpy()
    panels = [(d[0]*0+c.sum(0), "input (both)"),
              (eA.sum(0), f"surf A truth ({np.degrees(tA):.0f}°)"),
              (vA.sum(0), f"recon | cue A (str {strength})"),
              (eB.sum(0), f"surf B truth ({np.degrees(tB):.0f}°)"),
              (vB.sum(0), "recon | cue B")]
    fig, ax = plt.subplots(1, 5, figsize=(15, 3))
    for a, (im, t) in zip(ax, panels):
        a.imshow(im*APER, cmap="magma"); a.set_title(t, fontsize=9); a.axis("off")
    fig.suptitle(f"Head A cueing (reconstruction-only; best strength {strength})", y=1.02)
    fig.tight_layout(); p = os.path.join(FIGS, "headA_cueing.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p)
