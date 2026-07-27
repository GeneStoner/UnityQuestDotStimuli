# Behavioral Results: Website Experiments

Generated 2026-07-27. Companion to `stimulus_specs_website_experiments.md`.
All results from single observer G.S. unless otherwise noted.

---

## Data sourcing notes

Numbers below are drawn from: website content files (`content/collab-*.md`),
the density-knob memory table (computed from raw TSV session files), and the
S&B replication writeup (`WriteUps/WebContent/sb_replication.md`).

**Key discrepancy in website text vs. figure for the Çatak replication:**
The prose in `collab-catek-comparison.md` reports the MCvsDb_Ap165 dataset
(3 sessions; N=+14.6pp**, MC=+11.5pp**), while the bar-chart figure caption
(`collab-catek-results-caption.md`) shows the newer NMoCol dataset
(5 sessions; N=+16.8pp***, MC=+19.9pp***). Both use Çatak parameters
(Ap 1.65° radius, 43 dots, 80 ms). Results from both datasets are listed here.

**Analysis scripts** (for re-extraction from TSV files):
- `Analysis/nmocol_figure.py` — Çatak replication (NMoCol) bar chart
- `Analysis/density_ultrahigh_analysis.py` — density parametric series + polar
- `Analysis/catek_noswap_mc_figure.py` — MCvsDb_Ap165 pooled result

**Significance conventions:** * p < .05, ** p < .01, *** p < .001; two-proportion z-test.
**Cueing effect Δpp** = CUED − UNCUED (percentage points). Chance = 12.5%.

---

## 1. Stoner & Blanc (2010) — original paper results

**Observer group:** 15 naïve observers (Experiment 1/2 combined; exact n varies by condition).  
**Display:** 60 Hz CRT at 57 cm.  
**Source:** as reported in Çatak et al. (2022); cited in `collab-catek-comparison.md`.

| Condition | Δpp (cued − uncued) | Significance | Notes |
|-----------|---------------------|--------------|-------|
| N (no swap) | +20.2 pp | — | baseline; absolute %correct not extracted |
| M (motion swap only) | +10.4 pp | p = .018 | ~49% reduction vs. N |
| C (color swap only) | +13.4 pp | p = .049 | ~34% reduction vs. N |
| MC (motion+color) | not separately reported | — | not tested as standalone condition in S&B |

**Key finding:** Neither motion nor color swap eliminates cueing, though both reduce it.
Consistent with surface-based selection, not motion-competition alone.

---

## 2. VRDots S&B Replication — Ap 2.0° radius, 63 dots, 44 ms

**Experiment:** `Exp_StonerBlanc_Replication` / `StonerBlanc_Replication_v1`  
**Sessions:** 2 sessions per condition, observer G.S.  
**n per arm:** 256 (total 512 trials per condition).  
**Source:** `WriteUps/WebContent/sb_replication.md`.  
**Website display:** qualitative description in `collab-vrdots.md` (no numeric bar chart shown).

| Condition | CUED | UNCUED | Δpp | 95% CI | Significance |
|-----------|------|--------|-----|--------|-------------|
| N (no swap) | 65.2% | 48.4% | +16.8 pp | ±8.6 pp | *** |
| MC (motion+color swap) | 70.7% | 50.8% | +19.9 pp | ±8.5 pp | *** |

**Key finding:** Cueing advantage survives combined motion+color swap (MC ≈ N).
Replicates S&B in VR; establishes apparatus validity.

---

## 3. VRDots Çatak Replication — Ap 1.65° radius, 43 dots, 80 ms

### 3a. MCvsDb_Ap165 (3 sessions — used in comparison prose on website)

**Experiment:** `Exp_SubfieldSwap_CatekExact_NDb` / `SubfieldSwap_CatekExact_NDb_v1`  
**Sessions:** 3 sessions, observer G.S.  
**n per arm:** N condition pooled from CatekExact sessions (n = 345); MC and Db each n ≈ 256.  
**Source:** `collab-catek-comparison.md`; `Analysis/catek_noswap_mc_figure.py`.

| Condition | Δpp | Significance | Notes |
|-----------|-----|--------------|-------|
| N (no swap) | +14.6 pp | ** | pooled from CatekExact sessions |
| MC (motion+color swap) | +11.5 pp | ** | ~21% reduction vs. N |
| Db (motion-only subfield swap) | +10.4 pp | * | — |

### 3b. NMoCol (5 sessions — shown in bar chart figure on website)

**Experiment:** `SubfieldSwap_CatekExact_NMoCol_v1`  
**Sessions:** 5 sessions, observer G.S.  
**n per arm:** 320 (total 2560 trials across 4 conditions × 2 arms).  
**Source:** `collab-catek-results-caption.md`; `Analysis/nmocol_figure.py`.

| Condition | Δpp | Significance | Notes |
|-----------|-----|--------------|-------|
| N (no swap) | +16.8 pp | *** | absolute %correct: see analysis script |
| M (motion swap only) | TBD | — | tested; needs script re-run for numbers |
| C (color swap only) | TBD | — | tested; needs script re-run for numbers |
| MC (motion+color swap) | +19.9 pp | *** | ≥ N; cueing fully survives |

**Key finding (both datasets):** Cueing advantage survives the combined MC swap;
direction replicates S&B. MC does NOT disrupt cueing at Çatak parameters.

### 3c. Factor analysis (NDb dataset; `collab-catek-factor-intro.md`)

**Design:** 2³ factorial — F1 = onset cue (delayed vs. non-delayed translates);
F2 = color on translating field; F3 = competing rotation direction.  
**n:** 2,560 trials total.

| Factor | Significant? | Notes |
|--------|-------------|-------|
| F1 (onset cue) | **Yes** | sole significant effect |
| F2 (color of translating field) | No | null |
| F3 (competing rotation direction) | No | null |
| F1 × F2, F1 × F3, F2 × F3, F1×F2×F3 | No | all null |

**Conclusion:** Cueing advantage fully accounted for by onset-cue (delayed field identity),
not by color or motion-history of the translating or competing field.

---

## 4. Density Parametric Series — Ap 3.5° radius, N-swap only

**Experiments:** `Exp_DensityCompare_VRDots` / `HighDens` / `Peak` / `UltraHigh`  
**Sessions:** 1 session per density level, observer G.S.  
**n per arm:** 256 (n_total = 512 per density).  
**Source:** `density_knob.md` memory; `Analysis/density_ultrahigh_analysis.py`.

| N (dots/field) | ρ (dots/deg²) | CUED | UNCUED | Δpp | Cohen's h | OR | z | Sig |
|----------------|--------------|------|--------|-----|----------|----|---|-----|
| 63 | 1.82 | 60.5% | 25.8% | +34.8 pp | 0.718 | 4.42× | 7.94 | *** |
| 173 | 4.99 | 58.6% | 25.0% | +33.6 pp | 0.696 | 4.25× | 7.71 | *** |
| 500 | 14.4 | 63.3% | 28.5% | +34.8 pp | 0.713 | 4.32× | 7.89 | *** |
| 1000 | 28.8 | 53.1% | 28.1% | +25.0 pp | 0.515 | 2.90× | 5.76 | *** |

*ρ = dots per deg² per field (full-disk area convention, matching website). All at Ap 3.5° radius, r_excl = 1.1°.*

**Key finding:** Effect flat across 8× density range (N=63–500, Δpp ≈ +34pp).
Drop of ~10pp at N=1000 driven by CUED arm falling (53% vs. ~61%), not
UNCUED rising — consistent with V1 RF mixing degrading the attended field's signal.
Effect remains highly significant at N=1000.

---

## 5. High-Density Swap — Ap 3.5° radius, Peak and UltraHigh, N vs. MC

**Experiments:** `Exp_DensityCompare_Peak_ColorMotionSwap_v1` (and UltraHigh variant)  
**Sessions:** 1 session per condition, observer G.S.  
**n per arm:** 256.  
**Source:** `collab-highdensswap-caption.md`.

| Density | N (dots) | Condition | Δpp | Significance |
|---------|----------|-----------|-----|-------------|
| Peak | 500 | N (no swap) | +38.7 pp | — |
| Peak | 500 | MC (motion+color swap) | +16.8 pp | — |
| UltraHigh | 1000 | N (no swap) | +27.3 pp | — |
| UltraHigh | 1000 | MC (motion+color swap) | +0.8 pp | n.s. |

*Absolute %correct not extracted from caption; available from analysis script.*  
*Note: N-condition values here differ slightly from the parametric series (§4) because these are separate sessions.*

**Key finding:** Density × swap interaction. At Peak density the MC swap preserves a
strong cueing advantage (+16.8pp; ~57% of the no-swap effect). At UltraHigh density the
MC swap completely abolishes cueing (+0.8pp, n.s.) — a striking dissociation.

---

## Cross-experiment comparison (cueing effect Δpp)

| Experiment | Ap (radius) | N (dots) | Condition | Δpp | Sig | Observer |
|------------|-------------|----------|-----------|-----|-----|---------|
| S&B 2010 (original) | 2.0° | 63 | N | +20.2 pp | — | 15 naïve |
| S&B 2010 (original) | 2.0° | 63 | M | +10.4 pp | p=.018 | 15 naïve |
| S&B 2010 (original) | 2.0° | 63 | C | +13.4 pp | p=.049 | 15 naïve |
| VRDots S&B Replication | 2.0° | 63 | N | +16.8 pp | *** | G.S. |
| VRDots S&B Replication | 2.0° | 63 | MC | +19.9 pp | *** | G.S. |
| VRDots Çatak (MCvsDb) | 1.65° | 43 | N | +14.6 pp | ** | G.S. |
| VRDots Çatak (MCvsDb) | 1.65° | 43 | MC | +11.5 pp | ** | G.S. |
| VRDots Çatak (NMoCol) | 1.65° | 43 | N | +16.8 pp | *** | G.S. |
| VRDots Çatak (NMoCol) | 1.65° | 43 | MC | +19.9 pp | *** | G.S. |
| Density — VRDots (63) | 3.5° | 63 | N | +34.8 pp | *** | G.S. |
| Density — HighDens (173) | 3.5° | 173 | N | +33.6 pp | *** | G.S. |
| Density — Peak (500) | 3.5° | 500 | N | +34.8 pp | *** | G.S. |
| Density — UltraHigh (1000) | 3.5° | 1000 | N | +25.0 pp | *** | G.S. |
| HighDens Swap — Peak | 3.5° | 500 | N | +38.7 pp | — | G.S. |
| HighDens Swap — Peak | 3.5° | 500 | MC | +16.8 pp | — | G.S. |
| HighDens Swap — UltraHigh | 3.5° | 1000 | N | +27.3 pp | — | G.S. |
| HighDens Swap — UltraHigh | 3.5° | 1000 | MC | +0.8 pp | n.s. | G.S. |

**Notable pattern:** At Ap 1.65° (Çatak params) VRDots effects (~+15–20pp) closely match S&B originals.
At Ap 3.5° (density series) effects are substantially larger (~+25–35pp), consistent with
larger aperture improving field segregation. MC swap effect is density-dependent:
near-null at UltraHigh, partial at Peak, absent at CatekExact density.
