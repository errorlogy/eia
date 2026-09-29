# Human-connectome EIA model — results (2026-09-29)

Data: HCP DTI SC 94×94 (AAL2) + rs-fMRI, subjects 101309 102311 102816 131217 (neurolib public set).
Model: Stuart–Landau whole-brain, X_trigger = 0. Readout: SAL+BG+SMA envelope, threshold fixed at 95th pct of intact @ G*.
Files: brain_eia.py (E1–E5), control_e3.py, hetero.py; JSON outputs alongside. Single seed per subject — preliminary.

| Result | Value |
|---|---|
| E1 best FC fit | r = 0.28 at G* = 1.3 (modest) |
| E2 rate vs G | peak 6/min at G 0.6; at G* rarer but bursty, CV 1.3–1.6 |
| E3 silence DMN (16) | 1.17 → 0.10 /min |
| control: random 16 | → 0.26 |
| control: top-strength 16 non-DMN | → 0.06 (stronger than DMN!) |
| silence SEN / VAL | → 0.23 / 0.44 |
| stim SEN | rate ↑1.8, GC_SEN→D rises to ≈ GC_DMN (attribution shifts exogenous — sanity OK) |
| E5 Granger at X=0 intact | DMN→D 0.014 vs SEN→D 0.006 |
| E4 degree-preserving rewire | Q 0.30→0.20, CV 1.40→0.95 (burstiness lost), FC fit 0.23→0.03 |
| hetero a_j (transmodal near bifurcation) | DMN 0.19 vs top-strength 0.26 vs random 0.34 — weak specificity, FC fit 0.20 |

Conclusions
1. Homogeneous model: initiative is a distributed hub property, not a DMN module.
2. DMN specificity needs heterogeneous local dynamics; hand-coded hierarchy gives only a hint.
3. Modularity ↔ bursty (CV>1) initiative timing reproduces the topology-loop tick-1 finding on a real human connectome.

Caveats: silencing = damping sink (a=-1) not node removal; AAL2→network mapping hand-made; 4 subjects, 1 seed.
Next: real heterogeneity maps (neuromaps T1w/T2w, principal gradient, receptor densities; abagen), Schaefer-200 + Yeo-7 labels,
per-region a_j fit (Deco 2017), node-removal lesions, multi-seed CIs, G as LC-NE gain.

## Tick 14 — blind self-boundary detection on the Hopf model (`tick14_boundaries.py`)

Events = envelope onsets above own 90th pct (0.2 s sampling, 1800 s). Directed lagged excess
(lags 1–5), Louvain chosen by blind E gain on held-out half. 4 subjects × {homogeneous, heterogeneous a_j}.

| | parts | E found | E null (same sizes) | E of EIA module map | ARI vs EIA map / hemispheres / SC communities |
|---|---|---|---|---|---|
| homogeneous | 2–3 | 0.65–0.81 | 0.44–0.59 | 0.30–0.34 | ≈ 0 / ≈ 0.1 / ≈ 0.1 |
| heterogeneous | 3–6 | 0.53–0.71 | 0.36–0.54 | 0.28–0.33 | ≈ 0 / ≈ 0.1 / ≈ 0.1 |

- Found parts are large, functionally mixed (DMN+SEN+VAL+BG in each), not hemispheric, not
  frequency-sorted, and differ across subjects. Gain over null is small (0.13–0.23).
- **In this model the human brain behaves like the ER case of the toy study**: no natural
  sub-agent boundaries, endogeneity only at whole-brain level — consistent with E3 (initiative
  is a distributed hub property). SC modularity (Q≈0.30) is not enough to create self-boundaries
  under homogeneous diffusive Hopf coupling; the hand-made hetero a_j does not change this.
- Hand-made EIA module map is a poor boundary (E 0.30), i.e. auditing initiative at the level of
  "DMN / SAL / BG" modules would misattribute most events as exogenous in this model.
- Next: finer parcellation (Schaefer-200), empirically fitted a_j, and running the same detector
  on the *empirical* rs-fMRI (onsets from BOLD) — does real data have self-boundaries the model lacks?

## Tick 15 — same detector on EMPIRICAL rs-fMRI vs model (`tick15_empirical.py`)

Point-process events (upward +1 SD crossings of band-passed BOLD), lags 1–3 TR, 1200 TRs,
train/test halves. Model processed identically (x sampled at TR).

| source | parts | E found − null | ARI vs EIA functional map | ARI vs hemispheres / SC communities | cross-subject ARI |
|---|---|---|---|---|---|
| **empirical** | 2–5 | **0.20–0.34** | **0.19–0.40** | ≈ 0 / 0.04–0.11 | **0.18** |
| model | 2–6 | 0.09–0.12 | ≈ 0 | 0–0.15 / 0.07–0.13 | 0.04 |

Recurring empirical parts (3 of 4 subjects): **sensory block** (SEN), **DMN + value** (DMN, OFC,
amygdala), **basal ganglia (+SMA)**, **fronto-parietal**. I.e. the real brain separates an
exogenous channel from an internal-generator + value block and from an action-gate block —
close to the EIA functional decomposition — while the homogeneous Hopf model has no such
self-boundaries.

- The model's missing ingredient is not SC (both use the same SC) but **local dynamics**.
- Caveats: BOLD lagged co-activation is weak causal evidence (hemodynamic lag differences,
  especially subcortex); 1200 TRs; AAL2 coarse; E uses inferred Ŵ (biased low, tick 13).
- Next: fit per-region a_j / frequency so the model reproduces the empirical boundaries —
  an "endogeneity-profile fit" as a new model-fitting target beyond FC.

## Tick 16 — can local dynamics reproduce the empirical self-boundaries? (`tick16_fit.py`)

Subject 131217, blocks = its 4 empirical parts. Random search (15 samples) over per-block
bifurcation a_k (A) or per-block frequency detuning (W); null = same search with block labels
shuffled; best candidate re-tested on a fresh noise seed. Empirical E gain for this subject 0.34.

| mechanism | best ARI (search) | fresh-seed ARI | E gain |
|---|---|---|---|
| homogeneous baseline | 0.01 | — | 0.19 |
| A true blocks | 0.07 | −0.01 | 0.11–0.13 |
| A shuffled (null) | 0.03 | 0.01 | 0.08 |
| W true blocks | 0.04 | 0.01 | 0.14–0.15 |
| W shuffled (null) | 0.07 | −0.01 | 0.15–0.16 |

- **Negative result**: neither block-wise excitability nor frequency detuning makes the diffusive
  Hopf model reproduce the empirical boundaries; search gains are indistinguishable from the
  shuffled-label null and vanish on retest.
- Two live explanations:
  1. **measurement artefact** — region-specific hemodynamics / SNR (subcortical BG block, sensory
     block) could create the empirical grouping without causal self-boundaries;
  2. **effective connectivity ≠ SC** — boundaries require gating of coupling (within-block gain vs
     between-block gain), which neither knob changes.
- Next: (1) pass model output through a Balloon–Windkessel HRF with block-specific lags — does the
  detector then "find" blocks with no causal boundary? (2) block-wise coupling gain search.
