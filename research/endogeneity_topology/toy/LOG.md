# Loop log — endogenous proactive architecture across topologies

Model: `topo_endo.py` (N=200 EIA-like drive units, X_trigger=0, uncertainty aging +
noise + neighbour coupling; W normalised to equal spectral radius = gain).

## Tick 1 — 2026-09-29 — baseline sweep (gain 0.2 / 0.6 / 1.0, seed 42)

Findings:
1. **Aging alone = hidden clock.** `isolated` keeps 73% of activity with noise off,
   ISI CV = 0.16 (almost periodic). Uncertainty aging is an internal generator, but a
   timer-like one — exactly identification threat #1 (hidden scheduler).
2. **Gain 1.0 splits topologies into three regimes** (equal spectral radius!):
   - *seizure/clock*: ring, small-world, complete, ER, tree — rate hits refractory
     limit 1/6, CV ≈ 0.01–0.3, persist ≈ 1. Self-sustaining but meaningless.
   - *subcritical*: scale-free — hubs eat the spectral radius, rest stays weak
     (n̂ 0.86, persist 0.42).
   - *rich/critical*: **modular SBM** — CV ≈ 1.04 (Poisson/bursty), n̂ ≈ 0.93,
     avalanches up to 2239, rate ×5, persist 0.78. Only topology giving
     "neither clock nor seizure".
3. Spectral radius is not a sufficient control variable; modularity widens the
   near-critical band (cf. Griffiths phases, Moretti & Muñoz 2013).

## Tick 2 — gain 0.7–1.3 × 3 seeds, + hierarchical-modular (`tick2.py`)

"Rich" = rate ×base > 1.5 and CV 0.7–2.5, in ≥2/3 seeds.

| topology | rich band width (of 7 gains) | where |
|---|---|---|
| ring / small-world | 1 | 0.9 only, then clock (CV≈0) |
| ER / modular SBM / hier-modular | 2 | 0.9–1.0 |
| scale-free | 0 | never; slow ramp, CV ≤ 0.5 (regular) |

- **Tick-1 claim "only modular is rich" is weakened**: with 3 seeds ER is equally rich; tick-1 ER seizure at 1.0 was seed-specific.
- No Griffiths-phase widening at N=200 / this resolution. Hier-modular ≈ modular.
- Scale-free robustly avoids both seizure and richness (hubs absorb gain) — a distinct "safe but dull" regime.
- Human connectome (brain_eia, Hopf model) *did* show modularity→burstiness via rewiring; the toy spiking-drive model does not separate it from ER. Discrepancy to resolve.

## Tick 3 — N=1000, gain 0.85–1.10 step 0.025, 3 seeds (`tick3.py`)

| topology | rich width /11 | band | transition shape |
|---|---|---|---|
| small-world | 4 | 0.875–0.95 | abrupt: rate ×12 → ×26 → ×29 (saturation) within 0.05 |
| ER | 4 | 0.90–0.975 | abrupt jump ×5.5 → ×15 at 1.0 |
| modular SBM | 5 | 0.95–1.05 | smooth ramp ×3 → ×15 by 1.1, no saturation |
| hier-modular | **6** | 0.925–1.05 | smooth, widest |

- At N=1000 the tick-1 intuition returns in a better form: **modularity turns an abrupt
  (explosive-like) transition into a smooth, graded one** and pushes seizure beyond ρ=1.1.
  Hierarchy adds a bit more width. Consistent with Griffiths-phase smoothing, and with the
  human-connectome rewiring result.
- Trade-off: SW/ER peak burstiness is higher (CV up to 1.4) but in a razor-thin band;
  modular CV ≈ 0.7–0.9 but controllable.
- Architectural reading: a modular/hierarchical drive graph gives a **tunable
  "endogeneity gain" knob** — initiative rate scales smoothly with coupling instead of
  flipping silence→seizure. That is the property a Contact/Action Governor needs.

## Tick 4 — N=3000, 5 seeds (`tick4.py`)

| topology | rich width /11 (per seed) | band | max step jump in rate ×base |
|---|---|---|---|
| small-world | 4 [4,4,4,4,4] | 0.875–0.95 | **15.6** |
| ER | 4 [4,4,4,4,4] | 0.90–0.975 | 8.9 |
| modular | 4 [4,4,4,4,3] | 0.975–1.05 | 3.5 |
| hier-modular | 5 [5×5] | 1.0–1.1 (**truncated by range**) | **2.9** |

- Seed-robust at N=3000. "Width" ordering is weak (hier 5 vs 4) and hier band runs off the
  scanned range — width is not the right metric.
- **Robust result: transition smoothness.** Max jump SW 15.6 → ER 8.9 → mod 3.5 → hier 2.9
  (~5× smoother). Modularity also shifts the critical coupling right (≈0.95 → ≈1.05).
- Upgrade tick-3 claim: modularity ⇒ graded, controllable endogeneity gain (confirmed);
  modularity ⇒ wider rich band (not confirmed / undetermined).

## Tick 5 — gain 0.95–1.30, N=3000, 5 seeds (`tick5.py`)

True rich-band widths (combined with tick 4 lower end):
| topology | band | width (gain units) | last gain with discrete avalanches |
|---|---|---|---|
| ER | 0.90–0.975 | 0.075 | 0.975 |
| modular | 0.975–1.05 | 0.075 | 1.0 |
| hier-modular | 1.0–1.10 | **0.10** (+33%) | 1.025 |

- Hierarchy widens the rich band by ~1/3, seed-robust (5/5). Modest effect.
- All topologies converge to same saturated regime (×24) by 1.3; above band avalanches merge
  into continuous activity (max_aval → 0 = never silent) — the "seizure" limit.
- **Settled for this model:** main topological effect = smoothness (5×) + critical shift;
  width effect = small (+33%, hierarchy only). Line closed.

## Tick 6 — do(Z) on one 50-node module, exact twin (same noise), N=1000, 3 seeds × 5 modules (`tick6.py`)

do(Z): at t0 set d=1, u=1 on module S. D = hamming / 2p(1-p) (1 = fully decorrelated).

| topology (gain) | rate | D_out first 50 | D_out after 600 | D_in after 600 | extra initiatives in S (z) |
|---|---|---|---|---|---|
| ER (0.94) | 0.018 | 0.015 | 0.38 | 0.54 | **8.5** |
| modular (1.01) | 0.031 | **0.32** | **1.04** | 0.84 | 1.9 |
| hier (1.05) | 0.076 | 0.13 | 0.90 | 0.80 | 0.8 |

- Perturbation never fully dies in any topology (noise + threshold ⇒ butterfly effect).
- ER: effect stays partly local and gives a **reliable distributional change** in the target.
- Modular/hier (rich regime): internal intervention **decorrelates the whole system**
  quickly, yet the *count* of initiatives in the target is not reliably changed.
- ⇒ Tension: the rich/graded regime is the most sensitive at the trajectory level
  but the hardest to test for E_endo at the distribution level. Exact-twin EOI is
  meaningless there (twin diverges anyway) → need distributional metrics over many seeds.
- **Confound:** operating rates differ (0.018 / 0.031 / 0.076). Must match rate.

## Tick 7 — tick 6 at rate-matched points (rate ≈ 0.029, gain bisected per seed) (`tick7.py`)

| topology | gain | D_out first 50 | D_out end | extra initiatives in S | z | spill-over z |
|---|---|---|---|---|---|---|
| ER | 0.974 | **0.81** | 0.93 | 90 | 5.3 | 1.6 |
| modular | 1.010 | 0.47 | 0.97 | 44 | 1.4 | 2.5 |
| hier-modular | 1.011 | **0.29** | 0.83 | 98 | **6.2** | 0.6 |

- **Tick-6 ordering reversed** — it was a rate confound. At equal activity ER sits on
  its explosive edge and spreads a local intervention globally fastest.
- **Hier-modular = best combination**: slowest global spread, strongest and most
  reliable local causal effect of do(Z), no significant spill-over. The tick-6
  "tension" (rich regime untestable) disappears for hierarchy.
- Flat modular is weak here (z 1.4) — unexplained, maybe variance (15 samples). Check.
- EIA reading: a hierarchical-modular drive graph lets an internal change in one
  motive reliably alter that motive's initiatives without hijacking the whole agent —
  a structural form of "motive separability" useful for audit and for E_endo cond. 4.

## Tick 8 — tick 7 with 10 seeds (50 interventions / topology) (`tick8.py`)

| topology | D_out first 50 | extra initiatives in S | z | spill-over z |
|---|---|---|---|---|
| ER | 0.74 | 93 | 4.9 | **+2.2** |
| modular | 0.35 | 44 | 2.7 | +0.4 |
| hier-modular | **0.27** | 82 | 4.1 | **−3.2** |

- Containment ordering robust: hier < modular < ER (spread).
- Flat modular weak local effect confirmed (44 vs 82–93) — not variance.
- Tick-7 "hier strongest local effect" **not confirmed**: ER ≈ hier (z 4.9 vs 4.1).
- **New: sign of spill-over depends on topology.** ER: do(Z) in one motive *excites*
  the rest (+). Hierarchy: it *suppresses* the rest (−), with purely excitatory coupling.
  Hypothesis: the forced burst discharges the module (refractory + uncertainty reset),
  removing it as a future avalanche trigger for its super-module neighbours →
  emergent competition between motives without inhibition.
- Revised EIA reading: hierarchy gives containment + emergent motive competition
  (a structural "attention/priority" mechanism); ER gives contagion.

## Queue (next ticks)
- [ ] test discharge hypothesis: do(Z) that raises u only (no forced spike) — does negative spill-over vanish?
- [ ] hyperbolic / p-adic tree (Kairologos link)
- [ ] directed graphs, inhibition (E/I balance)
- [ ] hyperbolic / p-adic tree (Kairologos link)
- [ ] directed graphs (feed-forward vs recurrent motifs), Dale-like inhibition
- [ ] metric: Hawkes branching ratio via proper fit; Lempel–Ziv complexity of pattern
- [ ] replace aging clock with stochastic aging (Poisson staleness) — does the clock disappear?
- [ ] do(Z) test: perturb one module, measure trajectory divergence (E_endo cond. 4)
