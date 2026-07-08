"""
Temporal-scramble test: is the trained ReconAE actually USING motion, or just
reconstructing each frame semi-independently?

Compare held-out reconstruction error on:
  (a) ordered clips (smooth translation, as trained), vs
  (b) the SAME clips with frame order randomly shuffled (jerky, OOD if the model
      learned a smooth-motion prior).

If err(scrambled) ~= err(ordered): model is NOT exploiting temporal order
  -> per-frame reconstruction, motion is incidental.
If err(scrambled) >> err(ordered): model relies on smooth-motion structure.

Run: /usr/bin/python3 scramble_test.py
"""
import os
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import recon as R

torch.set_grad_enabled(False)
net = R.ReconAE().to(R.DEV)
net.load_state_dict(torch.load(os.path.join(R.HERE, "recon.pt"), map_location=R.DEV))
net.eval()


def norm_err(clip):
    x = torch.tensor(clip[None], device=R.DEV)
    xhat = net(x)[0][0].cpu().numpy()
    num = (((xhat - clip) ** 2) * R.APER[None]).sum()
    den = ((clip ** 2) * R.APER[None]).sum() + 1e-9
    return num / den, xhat


def shuffled(clip, rng):
    while True:
        perm = rng.permutation(R.T)
        if not np.array_equal(perm, np.arange(R.T)):
            return clip[perm], perm


ordered, scram = [], []
rng = np.random.RandomState(7)
for s in range(300, 420):
    np.random.seed(s)
    clip = R.make_clip()
    eo, _ = norm_err(clip)
    cs, _ = shuffled(clip, rng)
    es, _ = norm_err(cs)
    ordered.append(eo); scram.append(es)

ordered, scram = np.array(ordered), np.array(scram)
print(f"ordered   normalized recon error: {ordered.mean():.4f} +/- {ordered.std():.4f}")
print(f"scrambled normalized recon error: {scram.mean():.4f} +/- {scram.std():.4f}")
print(f"ratio scrambled/ordered: {scram.mean()/ordered.mean():.2f}x")
print(f"per-clip: scrambled worse in {100*np.mean(scram>ordered):.0f}% of clips")

# figure: one clip, ordered vs scrambled, input + recon
np.random.seed(2001)
clip = R.make_clip()
_, rec_o = norm_err(clip)
cs, perm = shuffled(clip, np.random.RandomState(3))
_, rec_s = norm_err(cs)
fig, ax = plt.subplots(4, R.T, figsize=(2.1 * R.T, 8.4))
rows = [(clip, "ordered input"), (rec_o, "ordered recon"),
        (cs, "scrambled input"), (rec_s, "scrambled recon")]
for r, (stack, lab) in enumerate(rows):
    for t in range(R.T):
        ax[r, t].imshow(stack[t], cmap="magma"); ax[r, t].axis("off")
        if r == 0:
            ax[r, t].set_title(f"slot {t}", fontsize=9)
    ax[r, 0].set_ylabel(lab, fontsize=10); ax[r, 0].axis("on")
    ax[r, 0].set_xticks([]); ax[r, 0].set_yticks([])
fig.suptitle(f"Temporal scramble (perm={list(perm)})", y=1.0)
fig.tight_layout()
p = os.path.join(R.FIGS, "scramble.png")
fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
print("figure ->", p)
