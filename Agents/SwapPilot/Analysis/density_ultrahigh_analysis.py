"""
Density knob comparison: VRDots / HighDens / Peak / UltraHigh
4-column layout matching density_peak_analysis.py style.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import math

# ── session files ─────────────────────────────────────────────────────────────
SESSIONS = [
    dict(label='VRDots\nN=63',    short='VRDots',    n_dots=63,
         color='#2166ac', path='/tmp/quest_density_pull/vr_dots_session_260421_1541.tsv'),
    dict(label='HighDens\nN=173', short='HighDens',  n_dots=173,
         color='#4dac26', path='/tmp/quest_density_pull/vr_dots_session_260422_0708.tsv'),
    dict(label='Peak\nN=500',     short='Peak',      n_dots=500,
         color='#9c51b6', path='/tmp/quest_density_pull/vr_dots_session_260422_1431.tsv'),
    dict(label='UltraHigh\nN=1000', short='UltraHigh', n_dots=1000,
         color='#d73027', path='/tmp/quest_density_pull/vr_dots_session_260422_1733.tsv'),
]

# aperture params (same for all)
R_APT, R_EXCL = 3.5, 1.1
A_EFF = math.pi * (R_APT**2 - R_EXCL**2)

# ── helpers ───────────────────────────────────────────────────────────────────
def load(path):
    df = pd.read_csv(path, sep='\t')
    df['correct'] = (df['TransDeg'] == df['RespDeg']).astype(int)
    df['err_deg'] = ((df['RespDeg'] - df['TransDeg'] + 180) % 360) - 180
    df['err_rad'] = np.deg2rad(df['err_deg'])
    return df

def mean_resultant(err_rad):
    return abs(np.mean(np.exp(1j * err_rad)))

def wilson_ci(p, n, z=1.96):
    denom = 1 + z**2/n
    centre = (p + z**2/(2*n)) / denom
    half = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return centre - half, centre + half

def cohens_h(p1, p2):
    return 2*math.asin(math.sqrt(p1)) - 2*math.asin(math.sqrt(p2))

def lor(p1, p2):
    return math.log(p1/(1-p1)) - math.log(p2/(1-p2))

def ztest_props(p1, n1, p2, n2):
    p_pool = (p1*n1 + p2*n2) / (n1+n2)
    se = math.sqrt(p_pool*(1-p_pool)*(1/n1 + 1/n2))
    return (p1 - p2) / se

def rayleigh_r(err_rad):
    n = len(err_rad)
    R = abs(np.sum(np.exp(1j * err_rad)))
    return R / n, 2*n*(R/n)**2   # r̄, Rayleigh statistic

# ── compute per-session stats ─────────────────────────────────────────────────
results = []
polar_data = []
for s in SESSIONS:
    df = load(s['path'])
    rho = s['n_dots'] / A_EFF

    # temporal lambda (using 80ms translation, d_trans=0.181°, mid-ecc ~2.3°)
    d_rf_mid = 0.05 + 0.08 * 2.3
    lam_static = rho * math.pi * (d_rf_mid/2)**2
    lam_eff    = lam_static * 1.77
    S_lam      = 2 * (1 - math.exp(-lam_eff)) * math.exp(-lam_eff)

    cued   = df[df['Cond'] == 'CUED']
    uncued = df[df['Cond'] == 'UNCUED']

    pc = cued['correct'].mean()
    pu = uncued['correct'].mean()
    nc, nu = len(cued), len(uncued)

    rc = mean_resultant(cued['err_rad'].values)
    ru = mean_resultant(uncued['err_rad'].values)

    z = ztest_props(pc, nc, pu, nu)
    p_val = 2 * (1 - stats.norm.cdf(abs(z)))

    results.append(dict(
        label=s['label'], short=s['short'], color=s['color'],
        n_dots=s['n_dots'], rho=rho,
        lam_static=lam_static, lam_eff=lam_eff, S_lam=S_lam,
        pc=pc, pu=pu, nc=nc, nu=nu,
        delta_pp=(pc-pu)*100,
        h=cohens_h(pc, pu),
        lor=lor(pc, pu),
        OR=math.exp(lor(pc, pu)),
        rc=rc, ru=ru, delta_r=rc-ru,
        z=z, p=p_val,
    ))
    polar_data.append(dict(cued=cued, uncued=uncued, label=s['label'],
                           short=s['short'], color=s['color']))

# ── plot ──────────────────────────────────────────────────────────────────────
NCOL = len(SESSIONS)
fig = plt.figure(figsize=(5.5*NCOL, 22), facecolor='#f8f8f8')
fig.patch.set_facecolor('#f8f8f8')

outer = gridspec.GridSpec(5, NCOL, figure=fig,
                          hspace=0.52, wspace=0.38,
                          left=0.06, right=0.97,
                          top=0.95, bottom=0.04)

BINS = np.arange(-180, 181, 45)
DIRS = np.arange(-180, 181, 45)

# ── row 0: summary metrics text ───────────────────────────────────────────────
for col, r in enumerate(results):
    ax = fig.add_subplot(outer[0, col])
    ax.set_facecolor('#f8f8f8')
    ax.axis('off')

    stars = '***' if r['p'] < 0.001 else ('**' if r['p'] < 0.01 else
            ('*' if r['p'] < 0.05 else 'n.s.'))
    rho_str = f"{r['rho']:.1f}"

    lines = [
        f"ρ = {rho_str} dots/sq°",
        f"λ_eff = {r['lam_eff']:.3f}",
        f"",
        f"CUED:   {r['pc']*100:.1f}%  (R̄={r['rc']:.3f})",
        f"UNCUED: {r['pu']*100:.1f}%  (R̄={r['ru']:.3f})",
        f"",
        f"Δpp  = {r['delta_pp']:+.1f} pp  {stars}",
        f"h    = {r['h']:.3f}",
        f"OR   = {r['OR']:.2f}×",
        f"ΔR̄  = {r['delta_r']:+.3f}",
        f"z    = {r['z']:.2f}  (p={r['p']:.3f})",
    ]
    txt = '\n'.join(lines)
    ax.text(0.5, 0.95, r['label'].replace('\n', ' — '), transform=ax.transAxes,
            ha='center', va='top', fontsize=13, fontweight='bold', color=r['color'])
    ax.text(0.5, 0.78, txt, transform=ax.transAxes,
            ha='center', va='top', fontsize=10.5, family='monospace',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', ec=r['color'], lw=1.5))

# ── rows 1 & 2: polar error plots ─────────────────────────────────────────────
for col, (r, pd_) in enumerate(zip(results, polar_data)):
    for row_i, (arm, arm_label, arm_col) in enumerate([
            ('cued',   'CUED',   '#2166ac'),
            ('uncued', 'UNCUED', '#d6604d')]):
        ax = fig.add_subplot(outer[row_i+1, col], projection='polar')
        err_rad = pd_[arm]['err_rad'].values
        counts, _ = np.histogram(np.rad2deg(err_rad), bins=BINS)
        theta = np.deg2rad(np.arange(-180, 180, 45))
        width = np.deg2rad(40)
        bars = ax.bar(theta, counts, width=width, align='center',
                      color=arm_col, alpha=0.78, edgecolor='white', lw=0.6)
        mrl = mean_resultant(err_rad)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
        ax.set_xticklabels(['0°','45°','90°','135°','±180°',
                            '−135°','−90°','−45°'], fontsize=7)
        ax.tick_params(axis='y', labelsize=6, colors='#666')
        ax.set_facecolor('#fafafa')
        acc = pd_[arm]['correct'].mean()
        ax.set_title(f'{arm_label}  {acc*100:.1f}%  R̄={mrl:.3f}',
                     fontsize=9, pad=8, color=arm_col, fontweight='bold')

# ── row 3: error distributions ────────────────────────────────────────────────
for col, (r, pd_) in enumerate(zip(results, polar_data)):
    ax = fig.add_subplot(outer[3, col])
    ax.set_facecolor('white')
    for arm, label, color in [('cued','CUED','#2166ac'),
                               ('uncued','UNCUED','#d6604d')]:
        errs = pd_[arm]['err_deg'].values
        counts, edges = np.histogram(errs, bins=BINS)
        centres = (edges[:-1] + edges[1:]) / 2
        ax.plot(centres, counts/counts.sum()*100, 'o-', color=color,
                label=label, lw=1.8, ms=5)
    ax.axvline(0, color='#aaa', lw=0.8, ls='--')
    ax.axhline(100/8, color='#bbb', lw=0.8, ls=':')
    ax.set_xlim(-202, 202)
    ax.set_xticks(DIRS)
    ax.set_xticklabels([f'{d}°' for d in DIRS], fontsize=7, rotation=45)
    ax.set_ylabel('% trials', fontsize=8)
    ax.set_xlabel('angular error', fontsize=8)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.25)
    ax.spines[['top','right']].set_visible(False)

# ── row 4: parametric panels ──────────────────────────────────────────────────
inner4 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[4, :], wspace=0.40)

n_vals  = [r['n_dots'] for r in results]
rho_vals = [r['rho'] for r in results]
p_cued  = [r['pc']*100  for r in results]
p_uncued= [r['pu']*100  for r in results]
d_pp    = [r['delta_pp'] for r in results]
h_vals  = [r['h']        for r in results]
or_vals = [r['OR']       for r in results]
rc_vals = [r['rc']       for r in results]
ru_vals = [r['ru']       for r in results]
colors  = [r['color']    for r in results]

# RF model prediction overlay
rho_fine = np.linspace(0.1, 35, 300)
A_RF_mid = math.pi * ((0.05 + 0.08*2.3)/2)**2
lam_eff_fine = rho_fine * A_RF_mid * 1.77
S_fine = 2 * (1 - np.exp(-lam_eff_fine)) * np.exp(-lam_eff_fine)
S_peak = 0.5   # maximum of S(λ)

# left: accuracy CUED and UNCUED separately
ax_acc = fig.add_subplot(inner4[0])
ax_acc.plot(rho_vals, p_cued,   'o-', color='#2166ac', lw=2, ms=8,
            label='CUED', zorder=3)
ax_acc.plot(rho_vals, p_uncued, 's-', color='#d6604d', lw=2, ms=8,
            label='UNCUED', zorder=3)
for i, r in enumerate(results):
    ax_acc.annotate(r['short'], (rho_vals[i], p_cued[i]),
                    textcoords='offset points', xytext=(0, 8),
                    ha='center', fontsize=7.5, color=r['color'])
ax_acc.axhline(12.5, color='#bbb', lw=0.8, ls=':', label='chance')
ax_acc.set_xlabel('dot density ρ (dots/sq°)', fontsize=9)
ax_acc.set_ylabel('accuracy (%)', fontsize=9)
ax_acc.set_title('Accuracy vs density', fontsize=10, fontweight='bold')
ax_acc.legend(fontsize=8)
ax_acc.set_ylim(0, 85)
ax_acc.grid(True, alpha=0.2)
ax_acc.spines[['top','right']].set_visible(False)
ax_acc.set_facecolor('white')

# middle: R̄ CUED and UNCUED + RF model S(λ_eff) overlay
ax_mrl = fig.add_subplot(inner4[1])
ax_mrl.plot(rho_vals, rc_vals, 'o-', color='#2166ac', lw=2, ms=8, label='R̄ CUED')
ax_mrl.plot(rho_vals, ru_vals, 's-', color='#d6604d', lw=2, ms=8, label='R̄ UNCUED')
# RF model on right axis
ax_rf = ax_mrl.twinx()
ax_rf.plot(rho_fine, S_fine / S_peak, color='#888', lw=1.5, ls='--', alpha=0.7,
           label='RF model S(λ_eff) norm.')
ax_rf.set_ylabel('S(λ_eff) / peak', fontsize=8, color='#888')
ax_rf.tick_params(axis='y', colors='#888', labelsize=7)
ax_rf.set_ylim(0, 1.15)
ax_mrl.set_xlabel('dot density ρ (dots/sq°)', fontsize=9)
ax_mrl.set_ylabel('mean resultant length R̄', fontsize=9)
ax_mrl.set_title('R̄ vs density + RF model', fontsize=10, fontweight='bold')
ax_mrl.set_ylim(0, 0.85)
ax_mrl.grid(True, alpha=0.2)
ax_mrl.spines[['top']].set_visible(False)
ax_mrl.set_facecolor('white')
lines1, labs1 = ax_mrl.get_legend_handles_labels()
lines2, labs2 = ax_rf.get_legend_handles_labels()
ax_mrl.legend(lines1+lines2, labs1+labs2, fontsize=7, loc='upper right')

# right: effect sizes
ax_es = fig.add_subplot(inner4[2])
x = np.arange(len(results))
w = 0.28
bars_pp = ax_es.bar(x - w, d_pp,    w, label='Δpp (pp)',    color='#4a90d9', alpha=0.85)
bars_h  = ax_es.bar(x,     h_vals,  w, label="Cohen's h",   color='#5cb85c', alpha=0.85)
bars_or = ax_es.bar(x + w, or_vals, w, label='OR',          color='#e8a020', alpha=0.85)
ax_es.axhline(0, color='#333', lw=0.7)
ax_es.set_xticks(x)
ax_es.set_xticklabels([r['short'] for r in results], fontsize=8, rotation=15)
ax_es.set_ylabel('effect size', fontsize=9)
ax_es.set_title('Effect sizes', fontsize=10, fontweight='bold')
ax_es.legend(fontsize=7.5)
ax_es.grid(True, alpha=0.2, axis='y')
ax_es.spines[['top','right']].set_visible(False)
ax_es.set_facecolor('white')

for bars in [bars_pp, bars_h, bars_or]:
    for bar in bars:
        h = bar.get_height()
        ax_es.text(bar.get_x() + bar.get_width()/2, h + 0.3,
                   f'{h:.1f}', ha='center', va='bottom', fontsize=6.5)

fig.suptitle('Density Knob: VRDots → UltraHigh (N=63–1000)\n'
             'Same aperture (7°, r_excl=1.1°), GS observer, n=512 per session',
             fontsize=13, fontweight='bold', y=0.975)

out = '/tmp/density_ultrahigh_comparison.png'
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor='#f8f8f8')
print(f"Saved {out}")

# ── print table ───────────────────────────────────────────────────────────────
print(f"\n{'Condition':<14} {'N':>5} {'ρ':>6} {'λ_eff':>7} "
      f"{'CUED':>7} {'UNCUED':>7} {'Δpp':>7} {'h':>6} {'OR':>6} {'z':>6} {'p':>7}")
print('-'*80)
for r in results:
    stars = '***' if r['p']<0.001 else ('**' if r['p']<0.01 else
            ('*' if r['p']<0.05 else 'n.s.'))
    print(f"{r['short']:<14} {r['n_dots']:>5} {r['rho']:>6.1f} {r['lam_eff']:>7.3f} "
          f"{r['pc']*100:>6.1f}% {r['pu']*100:>6.1f}% "
          f"{r['delta_pp']:>+6.1f}pp {r['h']:>6.3f} {r['OR']:>6.2f}x "
          f"{r['z']:>6.2f} {r['p']:>6.3f} {stars}")
