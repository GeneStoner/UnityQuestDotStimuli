import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import math

rng = np.random.default_rng(42)

def place_dots_annulus(n, r_apt, r_excl, rng):
    dots = []
    while len(dots) < n:
        batch = int((n - len(dots)) * 1.5 + 10)
        r = np.sqrt(rng.uniform(r_excl**2, r_apt**2, batch))
        th = rng.uniform(0, 2*np.pi, batch)
        x, y = r*np.cos(th), r*np.sin(th)
        dots.extend(zip(x, y))
    return np.array(dots[:n])

configs = [
    dict(label='VRDots\n(63 dots/field, 7° diam)',
         r_apt=3.5, r_excl=1.1, dots=63,
         fix_outer=0.6, fix_inner=0.24, cross_thk=0.03,
         dot_size=0.08, color='#2166ac'),
    dict(label='Catek\n(43 dots/field, 3.3° diam)',
         r_apt=1.65, r_excl=0.5, dots=43,
         fix_outer=0.30, fix_inner=0.12, cross_thk=0.015,
         dot_size=0.08, color='#d6604d'),
    dict(label='HighDens\n(173 dots/field, 7° diam)',
         r_apt=3.5, r_excl=1.1, dots=173,
         fix_outer=0.6, fix_inner=0.24, cross_thk=0.03,
         dot_size=0.08, color='#4dac26'),
    dict(label='Peak\n(500 dots/field, 7° diam)',
         r_apt=3.5, r_excl=1.1, dots=500,
         fix_outer=0.6, fix_inner=0.24, cross_thk=0.03,
         dot_size=0.08, color='#e8a020'),
]

# Field colors matching Unity assets
COL_A = '#cc3333'   # red field
COL_B = '#22aa44'   # green field

max_r = max(c['r_apt'] for c in configs)
lim = max_r * 1.18

fig = plt.figure(figsize=(20, 13), facecolor='#111')
fig.patch.set_facecolor('#111')

gs = gridspec.GridSpec(3, 4, figure=fig,
                       height_ratios=[1, 1, 0.65],
                       hspace=0.38, wspace=0.28,
                       left=0.03, right=0.99,
                       top=0.94, bottom=0.03)

def draw_fixation(ax, cfg, zorder_base=5):
    fix_r = cfg['fix_outer'] / 2
    ax.add_patch(plt.Circle((0,0), fix_r, color='white', zorder=zorder_base))
    hw = cfg['cross_thk'] / 2
    ax.add_patch(patches.Rectangle((-fix_r, -hw), 2*fix_r, 2*hw,
                                   color='black', zorder=zorder_base+1))
    ax.add_patch(patches.Rectangle((-hw, -fix_r), 2*hw, 2*fix_r,
                                   color='black', zorder=zorder_base+1))
    ax.add_patch(plt.Circle((0,0), cfg['fix_inner']/2, color='white',
                             zorder=zorder_base+2))

def style_ax(ax, cfg):
    ax.set_facecolor('#111')
    ax.set_aspect('equal')
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.tick_params(colors='#888', labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor('#333')
    ax.set_xlabel('degrees', color='#888', fontsize=7)
    ax.set_ylabel('degrees', color='#888', fontsize=7)
    # Scale bar
    sx, sy = lim*0.55, -lim*0.92
    ax.plot([sx, sx+1], [sy, sy], color='white', lw=2)
    ax.text(sx+0.5, sy+0.15, '1°', color='white', fontsize=7.5, ha='center')

def draw_aperture_and_excl(ax, cfg):
    ax.add_patch(plt.Circle((0,0), cfg['r_apt'], fill=True,
                             facecolor='#1e1e1e', edgecolor=cfg['color'],
                             lw=1.5, alpha=1.0, zorder=0))
    ax.add_patch(plt.Circle((0,0), cfg['r_excl'], fill=True,
                             facecolor='#111', edgecolor='#777',
                             lw=0.9, ls='--', alpha=1.0, zorder=2))

def draw_rf_circles(ax, cfg):
    """Draw 2 V1 RF circles at representative eccentricities.
    d_RF(r) = 0.05 + 0.08*r  (Dow et al. 1981)
    Placed at ~315° (lower-right, relatively open space).
    """
    r_inner = cfg['r_excl'] + (cfg['r_apt'] - cfg['r_excl']) * 0.28
    r_outer = cfg['r_excl'] + (cfg['r_apt'] - cfg['r_excl']) * 0.70
    angle = np.radians(315)   # lower-right

    for i, (ecc, ang_off) in enumerate([(r_inner, angle),
                                         (r_outer, angle - np.radians(18))]):
        d_rf = 0.05 + 0.08 * ecc
        cx = ecc * np.cos(ang_off)
        cy = ecc * np.sin(ang_off)
        # bright yellow ring, thick so it shows up
        ax.add_patch(plt.Circle((cx, cy), d_rf / 2,
                                fill=True, facecolor='#ffee0033',
                                edgecolor='#ffe000',
                                lw=2.0, ls='-', alpha=1.0, zorder=8))
        # crosshair at centre
        s = d_rf * 0.7
        ax.plot([cx-s, cx+s], [cy, cy], color='#ffe000', lw=0.9,
                alpha=0.9, zorder=9)
        ax.plot([cx, cx], [cy-s, cy+s], color='#ffe000', lw=0.9,
                alpha=0.9, zorder=9)
        # label with a leader line pointing away from fixation
        label_ecc = ecc + d_rf / 2 + 0.22
        lx = label_ecc * np.cos(ang_off)
        ly = label_ecc * np.sin(ang_off)
        ax.annotate(f'RF\n{d_rf*60:.0f}\'',
                    xy=(cx, cy), xytext=(lx, ly),
                    color='#ffe000', fontsize=6.8, fontweight='bold',
                    ha='center', va='center', zorder=10,
                    arrowprops=dict(arrowstyle='-', color='#ffe000',
                                   lw=0.8, alpha=0.7),
                    bbox=dict(boxstyle='round,pad=0.2', fc='#111',
                              ec='#ffe000', lw=0.6, alpha=0.88))

def stats_box(ax, cfg, a_full, a_eff):
    dens_full = cfg['dots'] / a_full
    dens_eff  = cfg['dots'] / a_eff
    info = (
        f"N = {cfg['dots']} dots/field\n"
        f"A_full = {a_full:.1f} sq°  →  {dens_full:.2f}/sq°\n"
        f"A_eff  = {a_eff:.1f} sq°  →  {dens_eff:.2f}/sq°  ← actual"
    )
    ax.text(0.02, 0.02, info, transform=ax.transAxes,
            color='white', fontsize=7.2, va='bottom', family='monospace',
            bbox=dict(boxstyle='round,pad=0.4', fc='#0a0a0a', ec='#444', alpha=0.95))

# ── Row 0: single field ───────────────────────────────────────────────────────
for col, cfg in enumerate(configs):
    ax = fig.add_subplot(gs[0, col])
    style_ax(ax, cfg)
    draw_aperture_and_excl(ax, cfg)

    xy_a = place_dots_annulus(cfg['dots'], cfg['r_apt'], cfg['r_excl'], rng)
    for x, y in xy_a:
        ax.add_patch(plt.Circle((x, y), cfg['dot_size']/2,
                                color=COL_A, zorder=3))

    draw_fixation(ax, cfg)
    draw_rf_circles(ax, cfg)

    a_full = math.pi * cfg['r_apt']**2
    a_eff  = math.pi * (cfg['r_apt']**2 - cfg['r_excl']**2)
    stats_box(ax, cfg, a_full, a_eff)

    ax.set_title(cfg['label'] + '\n(one field)', color='white',
                 fontsize=9.5, fontweight='bold', pad=6)

# ── Row 1: both fields ────────────────────────────────────────────────────────
for col, cfg in enumerate(configs):
    ax = fig.add_subplot(gs[1, col])
    style_ax(ax, cfg)
    draw_aperture_and_excl(ax, cfg)

    # Field A (red) — reuse same seed sequence by re-seeding rng identically
    rng2 = np.random.default_rng(42 + col*100 + 1)
    rng3 = np.random.default_rng(42 + col*100 + 2)
    xy_a = place_dots_annulus(cfg['dots'], cfg['r_apt'], cfg['r_excl'], rng2)
    xy_b = place_dots_annulus(cfg['dots'], cfg['r_apt'], cfg['r_excl'], rng3)

    for x, y in xy_a:
        ax.add_patch(plt.Circle((x, y), cfg['dot_size']/2,
                                color=COL_A, alpha=0.85, zorder=3))
    for x, y in xy_b:
        ax.add_patch(plt.Circle((x, y), cfg['dot_size']/2,
                                color=COL_B, alpha=0.85, zorder=3))

    draw_fixation(ax, cfg)
    draw_rf_circles(ax, cfg)

    a_full = math.pi * cfg['r_apt']**2
    a_eff  = math.pi * (cfg['r_apt']**2 - cfg['r_excl']**2)
    total_n = cfg['dots'] * 2
    total_eff = total_n / a_eff
    info2 = (
        f"N = {cfg['dots']} dots × 2 fields = {total_n} total\n"
        f"combined dens_eff = {total_eff:.2f}/sq°"
    )
    ax.text(0.02, 0.02, info2, transform=ax.transAxes,
            color='white', fontsize=7.2, va='bottom', family='monospace',
            bbox=dict(boxstyle='round,pad=0.4', fc='#0a0a0a', ec='#444', alpha=0.95))

    ax.set_title(cfg['label'].split('\n')[0] + '\n(both fields: red + green)',
                 color='white', fontsize=9.5, fontweight='bold', pad=6)

    # Field color legend
    ax.text(0.98, 0.98, '● field A (delayed onset)\n● field B (early onset)',
            transform=ax.transAxes, ha='right', va='top', fontsize=6.5,
            color='white',
            bbox=dict(boxstyle='round,pad=0.3', fc='#0a0a0a', ec='#444', alpha=0.9))
    # color the bullets manually via two separate texts
    ax.text(0.984, 0.985, '●', transform=ax.transAxes, ha='right', va='top',
            fontsize=7, color=COL_A)
    ax.text(0.984, 0.955, '●', transform=ax.transAxes, ha='right', va='top',
            fontsize=7, color=COL_B)

# ── Row 2: definitions ────────────────────────────────────────────────────────
ax_def = fig.add_subplot(gs[2, :])
ax_def.set_facecolor('#111')
ax_def.axis('off')

defs = (
    "DEFINITIONS\n\n"
    "  r_apt    = aperture radius (deg)            A_full = π·r_apt²                  — full disk area (S&B convention for quoting density)\n"
    "  r_excl   = exclusion zone radius (deg)      A_eff  = π·(r_apt²−r_excl²)        — annular region where dots are actually placed\n"
    "  N        = dotsPerField (per field)          dens_full = N/A_full               — matches S&B quoted density (~5 dots/sq° for Catek)\n"
    "                                               dens_eff  = N/A_eff  ← actual     — true spatial density the observer sees\n\n"
    "  NOTE: Our Unity code (UniformAnnulus) places all N dots directly in A_eff — no post-hoc exclusion. "
    "S&B placed dots in A_full then excluded near fixation, so their true density ≈ dens_full.\n"
    "  Combined density (both fields) = 2N/A_eff. VRDots: 3.64/sq°  |  Catek: 11.06/sq°  |  HighDens: 9.97/sq°  |  Peak: 28.84/sq°"
)

ax_def.text(0.01, 0.97, defs, transform=ax_def.transAxes,
            color='#ddd', fontsize=8.2, va='top', ha='left',
            family='monospace',
            bbox=dict(boxstyle='round,pad=0.55', fc='#0d0d0d', ec='#444', alpha=0.97))

fig.suptitle('Stimulus Areas & Dot Counts — same scale across all panels',
             color='white', fontsize=12, fontweight='bold')

fig.savefig('/tmp/stimulus_areas.png', dpi=150, bbox_inches='tight', facecolor='#111')
print("Saved /tmp/stimulus_areas.png")
