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
