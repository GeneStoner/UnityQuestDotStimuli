"""Slot AE: selectivity vs angular separation between the two surfaces, plus a
figure of well-separated (easy) examples. Loads slot_ae.pt."""
import os
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import recurrent_scaffold as RS
import head_a_recon as HA
import slot_ae as S

torch.set_grad_enabled(False)
DEV, FIGS, APER = RS.DEV, RS.FIGS, RS.APER
NDIR, H, W, CHAN_DIR = RS.NDIR, RS.H, RS.W, RS.CHAN_DIR

net = S.SlotAE().to(DEV)
net.load_state_dict(torch.load(os.path.join(RS.HERE, "slot_ae.pt"), map_location=DEV))
net.eval()


def make_pair(tA, tB, n=30):
    clean = np.zeros((NDIR, H, W), np.float32); surfs = []
    for th in (tA, tB):
        e = HA.render_energy(HA.sample_dots(n), th)
        clean += e; surfs.append((e*APER[None], th))
    return (clean*APER[None]).astype(np.float32), surfs


def slot_sel(d, surfs):
    (eA, tA), (eB, tB) = surfs
    recon, slots, dens, w = net(torch.tensor(d[None], device=DEV))
    slots = slots[0].cpu().numpy(); wk = w[0].cpu().numpy()
    slot_dir = np.angle((wk*np.exp(1j*CHAN_DIR)[None]).sum(1))
    ad = lambda a, b: abs((a-b+np.pi) % (2*np.pi) - np.pi)
    sA = int(np.argmin([ad(slot_dir[k], tA) for k in range(net.K)]))
    sB = int(np.argmin([ad(slot_dir[k], tB) for k in range(net.K)]))
    return 0.5*((S.corr(slots[sA], eA)-S.corr(slots[sA], eB)) +
                (S.corr(slots[sB], eB)-S.corr(slots[sB], eA))), (slots, sA, sB, slot_dir)


print("slot readout selectivity vs angular separation between surfaces:")
for sep in [10, 20, 30, 45, 60, 90, 135, 180]:
    ss = []
    for _ in range(50):
        tA = np.random.rand()*2*np.pi
        d, surfs = make_pair(tA, tA + np.radians(sep))
        ss.append(slot_sel(d, surfs)[0])
    print(f"  sep {sep:3d}°   selectivity {np.mean(ss):+.3f} +/- {np.std(ss):.3f}")

# figure: well-separated (>=100°) examples
fig, ax = plt.subplots(4, 5, figsize=(13, 10))
for j in range(4):
    np.random.seed(6000+j)
    tA = np.random.rand()*2*np.pi
    d, surfs = make_pair(tA, tA + np.radians(110 + np.random.rand()*60))
    (eA, tA), (eB, tB) = surfs
    _, (slots, sA, sB, sdir) = slot_sel(d, surfs)
    panels = [(d.sum(0), "input (both)"),
              (eA.sum(0), f"surf A ({np.degrees(tA):.0f}°)"),
              (slots[sA].sum(0), f"slot->A ({np.degrees(sdir[sA]):.0f}°)"),
              (eB.sum(0), f"surf B ({np.degrees(tB):.0f}°)"),
              (slots[sB].sum(0), f"slot->B ({np.degrees(sdir[sB]):.0f}°)")]
    for i,(im,t) in enumerate(panels):
        ax[j,i].imshow(im*APER, cmap="magma"); ax[j,i].axis("off")
        if j==0: ax[j,i].set_title(t, fontsize=9)
fig.suptitle("Slot AE, well-separated surfaces (>=110°): clean one-slot readout", y=1.005)
fig.tight_layout(); p = os.path.join(FIGS, "slot_separated.png")
fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
print("figure ->", p)
