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

## Tick 17 — can hemodynamics fake the boundaries? (`tick17_hrf.py`)

Homogeneous model (no causal blocks) → canonical double-gamma HRF with block-specific latency
and/or block-specific measurement noise (blocks = empirical parts of 131217) → same detector.
3 seeds.

| condition | ARI vs blocks | E gain |
|---|---|---|
| common HRF | 0.03 ± 0.03 | 0.11 |
| lag spread 1 s | 0.00 | 0.09 |
| lag spread 2 s | 0.04 ± 0.02 | 0.09 |
| SNR ×1..×3 | 0.01 ± 0.02 | 0.09 |
| lag 2 s + SNR | 0.01 ± 0.02 | 0.08 |
| *empirical (tick 15)* | *0.40 (vs EIA map)* | *0.34* |

- **Hemodynamic latency (up to 2 s) and SNR differences (up to 3×) do not fake self-boundaries**;
  ARI stays at null level and E gain stays far below the empirical 0.34.
- This removes explanation 1 of tick 16 (at least for lag/SNR; motion, physiological noise and
  global-signal artefacts are not tested). The empirical boundaries look like a genuine
  dynamical feature that the SC-diffusive model lacks → leading candidate: **effective
  connectivity gating** (block-wise within/between coupling gain).

## Tick 18 — effective-connectivity gating reproduces the boundaries (`tick18_gating.py`)

C_eff = C · (g_in within block, g_out between blocks); blocks = empirical parts of 131217.
Cells: ARI vs empirical / E gain.

| g_in \ g_out | 1 | 0.3 | 0.1 | 0.03 |
|---|---|---|---|---|
| 1 | 0.00 / 0.12 | 0.04 / 0.11 | 0.18 / 0.21 | 0.17 / 0.21 |
| 2 | 0.05 / 0.15 | 0.09 / 0.16 | 0.32 / 0.21 | 0.49 / 0.31 |
| 3 | 0.09 / 0.14 | 0.19 / 0.19 | 0.69 / 0.28 | **0.71 / 0.34** |

Fresh-seed retest of (3, 0.03): ARI vs empirical 0.69 / 0.51, E gain 0.33 / 0.36 (empirical 0.34).
Same gating on *shuffled* blocks: imposed blocks recovered worse (retest ARI 0.33–0.38).

- **Gating is sufficient**: strong within/between gain contrast (ratio ≳ 30–100) makes the model
  match both the empirical partition and the empirical E gain. Partly circular (imposed blocks
  become detectable by construction), but two non-trivial points:
  1. the *magnitude* of E gain matches the empirical value at the same operating point;
  2. **empirical blocks are easier to impose than random ones** of equal sizes (0.51–0.69 vs
     0.33–0.38) — they are SC-compatible, i.e. anatomy supports these boundaries but does not
     create them; dynamics-level gating does.
- EIA reading: self-boundaries between the exogenous channel, internal generator + value, action
  gate and executive blocks need **active gating** of inter-block influence (thalamic /
  neuromodulatory gating in the brain; the Governor role in EIA), not just wiring.
- Open: required contrast is large; check FC fit under gating, and whether a *state-dependent*
  gate (on only part of the time) achieves the same with smaller average contrast.

## Tick 19 — FC fit under gating; constant vs intermittent gate (`tick19_gate_state.py`)

Subject 131217, 2 seeds. Intermittent = telegraph process (mean dwell 20 s), ON = (3, 0.03).

| condition | ON time | ARI vs empirical | E gain | **FC fit** |
|---|---|---|---|---|
| no gate | — | 0.02 | 0.13 | 0.23 |
| constant (2, 0.1) | 1 | 0.54 | 0.29 | 0.44 |
| constant (3, 0.03) | 1 | **0.74** | **0.38** | **0.49** |
| intermittent 25% | 0.23 | 0.09 | 0.09 | 0.24 |
| intermittent 50% | 0.48 | 0.25 | 0.17 | 0.31 |
| intermittent 75% | 0.77 | 0.38 | 0.23 | 0.35 |

- **Gating doubles the FC fit (0.23 → 0.49)** — FC is a separate target from the boundary
  detector (zero-lag correlation vs lagged event co-activation), so this is supporting, though
  not independent evidence (blocks and FC come from the same scan).
- Intermittent gating gives no shortcut: all metrics scale ~linearly with ON time. Boundaries
  need the gate on most of the time — a *tonic* property, not an occasional state.
- Next: cross-validation — gate with 131217's blocks on other subjects' SC and score their FC,
  vs shuffled-block gating (control for "any gating helps FC").

## Tick 20 — cross-subject validation (`tick20_crossval.py`)

Blocks learned on 131217 gate (3, 0.03) the SC of the other 3 subjects; scored against *their*
empirical FC and *their own* empirical partitions. Controls: no gate; 3 shuffled block sets. 2 seeds.

| condition (mean of 3 subjects) | FC fit | ARI vs own empirical partition | E gain |
|---|---|---|---|
| no gate | **0.33** | 0.01 | 0.12 |
| 131217 blocks | 0.31 | **0.19** | **0.35** |
| shuffled blocks | 0.16 | 0.02 | 0.26 |

- **Tick-19 FC doubling does not transfer**: across subjects the gated model fits FC no better
  than the ungated one (0.31 vs 0.33). The within-subject gain was largely subject-specific /
  circular. What transfers is weaker: the empirical blocks are *FC-compatible* (random gating
  halves FC fit, real blocks do not).
- **Boundary structure transfers partially**: gating with another person's blocks makes the model
  reproduce this person's own empirical partition (ARI 0.19 vs 0.01–0.02), same order as the
  empirical cross-subject consistency (0.18, tick 15).
- E gain rises with *any* gating (0.26 shuffled) — partly generic — but more with real blocks (0.35).
- Net status: "self-boundaries require gating" stands; "gating explains FC" is withdrawn.

## Tick 21 — leave-one-subject-out consensus blocks (`tick21_loo.py`)

Consensus of 3 subjects' empirical partitions (co-assignment → Louvain, 2–3 blocks) gates the
held-out subject's SC. 4 folds × 2 seeds.

| condition (mean of 4 folds) | FC fit | ARI vs held-out own partition | E gain |
|---|---|---|---|
| no gate | 0.24 | 0.00 | 0.13 |
| consensus blocks | 0.26 | **0.17** (4/4 folds > 0: 0.07–0.22) | **0.36** |
| shuffled consensus | 0.13 | 0.00 | 0.29 |

- Held-out prediction of self-boundaries works in every fold, at the level of the direct
  consensus-vs-own agreement (0.07–0.27) — the gated model faithfully *carries* population
  boundaries; it does not add information beyond them (expected).
- FC: no gain over ungated (confirms tick 20); random gating halves FC fit.

### Line summary (ticks 14–21)
1. SC-diffusive Hopf model has no anatomical self-boundaries (ER-like).
2. Empirical rs-fMRI has them: sensory / DMN+value / BG+SMA / FPN, partly consistent across people.
3. Not a hemodynamic lag/SNR artefact.
4. Local excitability or frequency heterogeneity cannot produce them; **inter-block gating can**,
   tonically, and empirical blocks are SC-compatible. Population blocks predict held-out subjects.
5. Gating does not explain FC (withdrawn after cross-validation).
EIA implication: the functional separation "exogenous channel / internal generator + value /
action gate / executive" is maintained by active gating, i.e. a Governor-like function is
constitutive of endogenous sub-agents, not an add-on safety layer.

## Tick 36 — re-scored with calibrated blind attribution (`tick36_calibrated.py`)

Conditional regression attribution (lags 1–3 TR) + null-normalised E_norm (20 size-matched permutations);
infer on first half, score second half. Mean of 4 subjects:

| partition | empirical E_norm | model E_norm |
|---|---|---|
| found parts (tick 15)* | **0.68** | 0.09 |
| EIA functional map | **0.25** | 0.03 |
| hemispheres | 0.05 | **0.37** |
| SC communities | 0.24 | 0.27 |

\* found parts came from the full scan in tick 15, so this row is not fully held-out.

- Confirms B3 with calibrated numbers: the real brain has strong functional self-boundaries (0.68) and
  partially respects the EIA functional map (0.25); the model has neither.
- **Revises B2**: the model is *not* boundary-free — it is bounded by **anatomy** (hemispheres 0.37,
  SC communities 0.27). The real brain is bounded by **function** (hemispheres ≈ 0.05). The uncalibrated
  detector (tick 14) missed the model's hemispheric boundary.
- Sharper statement: SC-diffusive dynamics produce anatomical self-boundaries; the brain overrides them
  with functional ones — consistent with gating (B5) re-routing effective connectivity across anatomy.

## Tick 37 — does gating convert anatomical → functional boundaries? (`tick37_gated_calibrated.py`)

Held-out subject, LOO-consensus gate (3, 0.03), calibrated E_norm, 2 seeds × 4 folds (means):

| model | own empirical parts | EIA map | hemispheres | SC communities |
|---|---|---|---|---|
| no gate | 0.11 | 0.03 | 0.32 | 0.21 |
| consensus gate | **0.33** | **0.15** | 0.28 | 0.30 |
| shuffled gate | 0.13 | 0.07 | 0.35 | 0.28 |
| *empirical (tick 36)* | *0.68* | *0.25* | *0.05* | *0.24* |

- Gating with *population* blocks roughly triples functional boundary strength on a held-out subject
  (own parts 0.11 → 0.33, EIA map 0.03 → 0.15; shuffled control ≈ no gate) — about half the empirical level.
- But it **does not dissolve the hemispheric boundary** (0.32 → 0.28 vs empirical 0.05). Gating adds
  functional boundaries on top of anatomical ones rather than replacing them.
- Candidate missing ingredient: inter-hemispheric (homotopic) coupling, which DTI tractography is known
  to under-represent. Next: strengthen homotopic links and re-score.

## Tick 38 — homotopic links (`tick38_homotopic.py`)

C_h = C + h·H (H = left–right mirror pairs; max SC = 0.2). Held-out subject, LOO-consensus gate, calibrated
E_norm, 1 seed × 4 folds (means):

| gate | h | own parts | EIA map | hemispheres | FC fit |
|---|---|---|---|---|---|
| no | 0 | 0.06 | 0.04 | 0.32 | 0.29 |
| no | 0.05 | 0.06 | 0.08 | **0.05** | 0.30 |
| no | 0.10 | 0.15 | 0.14 | −0.12 | 0.30 |
| no | 0.20 | 0.22 | 0.22 | −0.15 | 0.30 |
| yes | 0 | 0.26 | 0.16 | 0.40 | 0.26 |
| yes | 0.05 | 0.28 | 0.19 | **0.06** | 0.25 |
| yes | 0.10 | **0.36** | **0.27** | −0.10 | 0.25 |
| yes | 0.20 | 0.34 | 0.29 | −0.17 | 0.26 |
| *empirical* | | *0.68* | *0.25* | *0.05* | |

- **A modest homotopic boost (h = 0.05, a quarter of max SC) dissolves the hemispheric self-boundary
  exactly to the empirical level** (0.32 → 0.05). Larger h over-couples the hemispheres (negative E_norm).
- Homotopic links alone also raise functional/EIA boundaries (bilateral systems become self-contained).
- **Gate + h 0.05–0.10 reproduces the empirical profile on EIA map (0.19–0.27 vs 0.25) and hemispheres
  (0.06 / −0.10 vs 0.05)** on held-out subjects. Remaining gap: subject-specific parts (0.28–0.36 vs 0.68).
- FC fit unaffected (0.25–0.30) — the E-profile is a target that FC does not constrain.
- Minimal recipe for a human-like endogeneity profile: SC + homotopic boost + tonic functional gating.

## Tick 39 — the subject-specific gap is mostly an artefact; boundaries are degenerate (`tick39_subject_specific.py`)

Split each empirical scan in halves; blocks lab1 (first half) and lab2 (second half, never seen by the model).

| quantity (mean of 4) | value |
|---|---|
| empirical split-half agreement ARI(lab1, lab2) | **0.09** |
| empirical E_norm of lab1 on second half (held-out) | **0.49** |
| empirical E_norm of lab2 on second half | 0.42 |
| model gated by lab1 (+homotopic 0.05): E_norm(lab1) | 0.88 (circular) |
| same model: E_norm(lab2, held-out) | 0.19 |
| model gated by LOO consensus: E_norm(lab2) | 0.15 |

- **Tick-36 "0.68" was inflated** (blocks found on the full scan incl. the test half). Honest held-out
  empirical boundary strength is **≈ 0.42–0.49**.
- **Empirical self-boundaries are real but degenerate**: two halves of the same 14-min scan yield almost
  unrelated partitions (ARI 0.09), yet each partition stays strongly endogenous on the other half (0.49).
  Many near-equivalent partitions exist; the detector picks one. Not simple drift (lab1 remains valid
  in the second half).
- A fixed-gating model imposes one rigid partition (0.88 on it) and does not reproduce the degeneracy
  (0.19 on the alternative). Real brain boundaries look like a **landscape of near-equivalent sub-agent
  decompositions**, not a single fixed modular structure.
- EIA reading: an agent's "sub-agents" need not be a unique fixed decomposition; audits should report the
  set/ensemble of high-E_norm partitions, not a single one.

## Tick 40 — metastable gating reproduces degenerate boundaries (`tick40_metastable.py`)

Repertoire = the other 3 subjects' empirical partitions (non-circular); homotopic h = 0.05; the gate switches
between repertoire partitions (telegraph, mean dwell τ). Same split-half pipeline as tick 39; 4 subjects × 2 seeds.

| condition | split-half ARI | E_norm(l1) on 2nd half | E_norm(l2) |
|---|---|---|---|
| no gate | 0.00 | 0.32 | 0.10 |
| fixed gate (consensus) | 0.43 | 0.77 | 0.69 |
| **switching, τ = 120 s** | **0.17** | **0.55** | **0.41** |
| switching, τ = 30 s | 0.18 | 0.56 | 0.60 |
| *empirical* | *0.09* | *0.49* | *0.42* |

- **Metastable gating with ~2-min dwell comes closest to the empirical profile** on all three numbers; fixed
  gating is too stable and too strong; no gating has no boundaries; fast switching (30 s) over-strengthens
  the second-half partition.
- Residual: split-half ARI still 0.17 vs 0.09 (repertoire of only 3 partitions).
- Picture: the brain's endogenous sub-agent decomposition is **metastable** — tonic gating that re-routes
  among several near-equivalent decompositions on a minutes timescale.

## Tick 44 — do(Z) in the human model: gating gives controllability + suppressive spill-over (`tick44_brain_doZ.py`)

Target = LOO-consensus block with most DMN regions (43 regions, DMN+value). do(Z): bifurcation parameter
a → +0.02 for 30 s; exact twin; relative envelope change over the next 120 s. 4 subjects × 2 seeds (n = 8).

| condition | Δ inside target | Δ outside | Δ initiation loop (SAL+BG+SMA, outside target) | leak ratio |
|---|---|---|---|---|
| no gate | +3.5 % | +0.4 % | +0.6 % | +0.11 |
| gate | **+10.2 %** | **−0.8 %** | −0.7 % | −0.06 |
| gate + homotopic 0.05 | **+12.0 %** | **−0.9 %** | −0.9 % | −0.11 |

- Gating ~triples the local effect of an internal intervention and **flips the spill-over sign** from
  excitatory leak to mild suppression — the same pattern as the toy networks (ER contagion vs hierarchical
  suppression, A4/A6), now in a connectome-based oscillator model with population-derived blocks.
- Boosting the internal-generator block (DMN+value) slightly *lowers* the initiation loop outside it under
  gating: blocks compete rather than recruit each other.
- Small effects (≤ 1 % outside), n = 8, no CIs — directional.

## Tick 45 — tick 44 with n = 24 (`tick45_brain_doZ_ci.py`)

| condition | Δ inside (z) | Δ outside (z) | Δ initiation loop (z) |
|---|---|---|---|
| no gate | +6.6 % (15.6) | +4.5 % (11.4) | +5.3 % (11.0) |
| gate | +16.8 % (7.8) | +0.7 % (2.1) | +0.6 % (2.2) |
| paired gate − no gate | **+10.2 % (z 5.7)** | **−3.8 % (z −13.1)** | |

- **Robust**: gating multiplies the local effect of do(Z) (~2.5×) and cuts leakage to the rest of the brain by
  ~85 % — containment + controllability, as in toy hierarchies (A4).
- **Tick-44 sign flip does not replicate**: with n = 24 the gated spill-over is small and *positive* (+0.7 %),
  not suppressive. The n = 8 estimate was noise. Withdrawn.

## Tick 46 — toy A2 (transition smoothness) in the human model: not testable here (`tick46_brain_smoothness.py`)

Sweep G 0.2–3.0, plain SC vs gated + homotopic, 4 subjects.

- Mean activity **decreases monotonically** with G in both (0.062 → 0.027 plain; 0.054 → 0.026 gated):
  with subcritical nodes (a = −0.02) and *diffusive* coupling (z_k − z_j), coupling synchronises and damps;
  there is no silence→seizure transition to smooth. Burstiness (CV of the initiation drive) rises with G;
  gating lowers it slightly at high G (0.245 → 0.214).
- A2 cannot be tested in this model family — it needs additive excitatory coupling or near/supercritical
  nodes. Left open (not a refutation).

## Tick 47 — A2 on the human connectome with excitatory drive-units (`tick47_units_on_sc.py`)

94 regions × 10 units (topo_endo dynamics, additive excitatory coupling via SC weights); gain sweep
0.80–1.30; rate × base; 2 subjects × 2 seeds.

| SC variant | rate at gain 1.0 → 1.05 | max step jump |
|---|---|---|
| degree-preserving rewired | 5.6 → 22.3 (at 0.95 → 1.0) | **16.7** |
| plain human SC | 4.1 → 14.4 | 10.3 |
| gated + homotopic (LOO consensus) | 4.4 → 7.7 | **3.3** |

- **Toy A2 holds on the human connectome**: real SC gives a smoother onset of self-driven activity than a
  randomised SC (10.3 vs 16.7), and functional gating smooths it ~3× further (3.3), saturating at half
  the level (12 vs 21–28 × base) — a graded, controllable "endogeneity gain".

## Tick 48 — which ingredient smooths the onset? (`tick48_units_decompose.py`)

Tick-47 design, all 4 subjects × 2 seeds, gain 0.90–1.20. Max step jump of rate × base (mean ± sd):

| SC variant | max jump |
|---|---|
| degree-preserving rewired | 16.8 ± 2.1 |
| plain human SC | 10.5 ± 1.6 |
| homotopic only | 11.2 ± 1.8 |
| **gated only** | **3.8 ± 1.2** |
| gated + homotopic | 4.2 ± 1.0 |

- Consistent in every subject: anatomy smooths vs random (−37 %), **functional gating smooths ~2.8× further**;
  homotopic links contribute nothing to smoothness (their role is the boundary profile, tick 38).
- Division of labour: gating → graded endogeneity gain + containment (B11, B12); homotopic coupling →
  human-like (function-, not hemisphere-bounded) sub-agent profile (B8).

## Tick 76 — timescale hierarchy on the human connectome (`tick76_timescale_brain.py`)

Drive-units on SC (94 regions × 10 units). Homogeneous ρ vs hierarchy (DMN+value slow ρ 0.05, sensory fast ρ 0.30,
α scaled with ρ). Outcome: initiation-loop (SAL+BG+SMA) activity after silencing, relative to intact; rate-matched,
2 subjects × 2 seeds.

| condition | silence DMN | silence 16 strongest non-DMN | silence sensory |
|---|---|---|---|
| homogeneous | 0.29 | 0.28 | 0.36 |
| hierarchy | 0.26 | 0.25 | **0.80** |

- DMN is still **not** more specific than equally strong hubs (0.26 vs 0.25) — B1 stands under a timescale hierarchy too.
- But the hierarchy **decouples initiative from the sensory channel**: silencing sensory cortex costs 64 % of
  initiation-loop activity in the homogeneous model and only 20 % with slow association / fast sensory timescales —
  the endogenous drive migrates to the slow, internal part of the network (cf. A25).

## Tick 77 — gating + timescale hierarchy: still no DMN specificity (`tick77_gate_timescale.py`)

Drive-units on SC with the timescale hierarchy; plain SC vs gated + homotopic SC (LOO consensus). Initiation-loop
activity kept after silencing (relative to intact), 2 subjects × 2 seeds.

| SC | silence DMN | silence 16 strongest non-DMN | silence sensory | DMN-specific margin (top16 − DMN) |
|---|---|---|---|---|
| plain | 0.26 | 0.25 | 0.80 | −0.00 |
| gated + homotopic | 0.54 | 0.50 | 0.92 | −0.04 |

- Gating makes the initiation loop more robust to *any* silencing (containment, B11) but the DMN never becomes more
  critical than equally strong hubs. **B1 holds across every model variant tried** (Hopf homogeneous / heterogeneous,
  drive-units, timescale hierarchy, gating + homotopic): in connectome-based models the internal generator is
  hub-bound. DMN specificity would need an ingredient not modelled here (e.g. region-specific excitability or
  neuromodulatory/receptor maps).

## Tick 78 — how much DMN excitability buys specificity (`tick78_dmn_excitability.py`)

Drive-units on plain SC + timescale hierarchy; DMN units' excitability α × f; rate-matched; 2 subjects × 2 seeds.

| f | loop kept after silencing DMN | after silencing 16 strongest non-DMN | DMN-specific margin | DMN share of all activity |
|---|---|---|---|---|
| 1.0 | 0.27 | 0.27 | −0.00 | 0.24 |
| 1.3 | 0.26 | 0.27 | +0.02 | 0.26 |
| 1.6 | 0.27 | 0.32 | +0.05 | 0.27 |
| 2.0 | 0.26 | 0.30 | +0.05 | 0.29 |

- Even doubling DMN excitability yields only a small specificity margin (+0.05) and a modest rise of its activity share
  (0.24 → 0.29): network position (hub strength) dominates intrinsic excitability. A DMN-specific internal generator is
  hard to get from local parameters in these models — consistent with B1 being robust.

## Tick 79 — which regions self-initiate in real data? (`tick79_empirical_initiators.py`)

Per region: share of BOLD events with no inferred parent activity in the previous 1–3 TR (conditional attribution,
inferred on the first half, scored on the second). Mean over regions per module, 4 subjects.

| module | VAL | BG | other | DMN | FPN | SAL | SMA | SEN |
|---|---|---|---|---|---|---|---|---|
| self-initiated share | **0.88** | 0.78 | 0.74 | 0.70 | 0.63 | 0.60 | 0.59 | **0.50** |

- Top-10 regions: olfactory L/R, pallidum R, OFC (ant/lat/med), temporal pole, paracentral lobule, amygdala.
- Spearman(self-initiation, SC strength) = **−0.55**; cross-subject consistency of the profile 0.36.
- **Strongly confounded**: the most "self-initiating" regions are weakly connected and are the classic fMRI
  susceptibility/dropout regions (orbitofrontal, olfactory, temporal pole) with low SNR — events there look uncaused
  because nothing is inferred to drive them. The ranking therefore does not identify an internal generator; at most
  it shows sensory cortex is the most externally driven (0.50) and DMN intermediate. Not promoted to FINDINGS.
- A clean empirical test of B1 would need SNR-matched regions or a causal perturbation dataset (e.g. TMS-fMRI).

## Tick 80 — tick 79 with confounds regressed out (`tick80_residual_initiators.py`)

Per subject, self-initiated share regressed on SC strength, inferred in-degree and event count (these explain
R² = 0.57–0.68); residuals averaged per module over 4 subjects.

| module | BG | **DMN** | VAL | SAL | FPN | SMA | **SEN** |
|---|---|---|---|---|---|---|---|
| residual self-initiation | +0.053 | **+0.046** | +0.008 | −0.000 | −0.021 | −0.041 | **−0.064** |
| z vs regional spread | +1.7 | **+2.1** | +0.3 | 0.0 | −0.7 | −0.9 | **−3.1** |

- The orbitofrontal/value "top" of tick 79 **disappears** once connectivity and signal proxies are removed (VAL ≈ 0) —
  it was the dropout artefact.
- What remains: **DMN (and basal ganglia) modestly more self-initiating than their connectivity predicts, sensory
  cortex clearly less**. This is the first empirical hint of DMN specificity — the thing none of the connectome models
  reproduced (B1). Tension with the models: real DMN may carry an ingredient they lack.
- Tentative: z is against regional spread, not across subjects; the residual *regional* profile is weakly consistent
  across subjects (Spearman 0.13), only the module-level pattern is. Needs more subjects (HCP has ~1000).

## Tick 81 — B14 on all 7 neurolib HCP subjects (`tick81_initiators_7subj.py`)

Residualised self-initiation (tick 80 method), module means per subject, one-sample t across subjects (n = 7).

| module | mean residual | sd | t | p | subjects > 0 |
|---|---|---|---|---|---|
| BG | +0.052 | 0.034 | 4.10 | **0.006** | 7/7 |
| DMN | +0.034 | 0.032 | 2.75 | 0.033 | **7/7** |
| SMA | +0.024 | 0.105 | 0.61 | 0.56 | 5/7 |
| SAL | +0.015 | 0.066 | 0.59 | 0.58 | 4/7 |
| FPN | −0.003 | 0.085 | −0.09 | 0.93 | 3/7 |
| VAL | −0.003 | 0.026 | −0.34 | 0.74 | 4/7 |
| SEN | −0.066 | 0.043 | −4.06 | **0.007** | 0/7 |

- Across subjects: **basal ganglia and DMN self-initiate more than their connectivity/signal predict, in 7/7 subjects;
  sensory cortex less, in 7/7.** BG and SEN survive Bonferroni over 7 modules (p < 0.007); DMN is nominal
  (p = 0.033; sign test 7/7, p = 0.016).
- Consistent with the EIA mapping in an interesting way: the *action-gate* (BG) and *internal generator* (DMN) blocks
  are the empirically self-starting ones, the exogenous channel (SEN) the most driven. The connectome models capture the
  SEN side (B13) but not DMN/BG specificity (B1).

## Tick 82 — which model reproduces the empirical self-initiation profile? (`tick82_model_initiators.py`)

Tick-81 pipeline applied to Hopf-model output for all 7 subjects. Module residuals (mean over subjects) and correlation
of the 7-module profile with the empirical one.

| variant | BG | DMN | SMA | SAL | FPN | VAL | SEN | r with empirical |
|---|---|---|---|---|---|---|---|---|
| *empirical* | +0.052 | +0.034 | +0.024 | +0.015 | −0.003 | −0.003 | −0.066 | |
| plain SC | +0.015 | −0.001 | −0.004 | −0.006 | +0.013 | −0.013 | −0.014 | +0.59 |
| **gated + homotopic** | +0.002 | **+0.027** | +0.009 | −0.007 | −0.016 | −0.012 | **−0.039** | **+0.85** |
| + BG/DMN near bifurcation | −0.033 | +0.011 | +0.002 | −0.010 | +0.028 | −0.009 | −0.021 | +0.02 |

- **Functional gating reproduces the empirical profile** (r = 0.85): the DMN excess (+0.027 vs +0.034) and the sensory
  deficit come out without any DMN-specific local parameter. Raising BG/DMN excitability *breaks* the match (r 0.02).
- So the empirical "DMN self-initiation" is plausibly a **block-gating effect** (DMN sits in a gated internal block, so
  few of its events have inferred cross-block causes), not evidence of an intrinsic DMN generator — reconciling B14 with B1.
- **BG is not reproduced** (+0.002 vs +0.052): basal-ganglia self-initiation needs an ingredient the model lacks
  (subcortical loop dynamics / different haemodynamics).
- Caveat: the gating blocks are the consensus of 4 subjects that are among the 7 — partly circular for those 4.

## Tick 83 — held-out check of tick 82: withdrawn (`tick83_heldout_initiators.py`)

Gating blocks from the 4 original subjects; evaluation only on the 3 new subjects against their own empirical profiles
(3 model seeds each). Pearson r over 7 modules:

| subject | plain SC | gated + homotopic |
|---|---|---|
| 211619 | +0.36 | +0.37 |
| 213522 | +0.54 | +0.44 |
| 377451 | +0.64 | +0.26 |
| **mean** | **+0.51** | **+0.36** |

- On held-out subjects the gated model does **not** beat plain SC (0.36 vs 0.51); the tick-82 r = 0.85 came from
  circularity (4 of the 7 subjects shaped the blocks) and group averaging. **Tick-82 conclusion withdrawn**: the
  empirical DMN excess is *not* shown to be a gating effect. Both models get the sensory deficit; neither reproduces
  BG or a consistent DMN excess. B1 and B14 stand as an unresolved model–data gap.

## Tick 84 — basal-ganglia self-initiation from weak cortical input (`tick84_bg_input.py`)

Plain Hopf model; incoming SC of BG regions scaled by k; 7 subjects × 2 seeds; tick-81 residual pipeline.

| k (BG input) | BG | DMN | SEN | r (7-module profile vs empirical) |
|---|---|---|---|---|
| 1.0 | +0.011 | +0.005 | −0.003 | +0.10 |
| 0.3 | +0.032 | +0.006 | −0.004 | +0.57 |
| 0.1 | **+0.042** | −0.007 | −0.011 | +0.59 |
| *empirical* | *+0.052* | *+0.034* | *−0.066* | |

- Weakening the effective cortical input to BG reproduces most of the empirical BG excess (0.011 → 0.042 vs 0.052).
  Parsimonious reading: BG looks "self-initiating" because it is **weakly driven** (or DTI overstates cortex→BG
  effective input), not necessarily because it generates activity intrinsically.
- **Methodological caveat for every endogeneity metric used here**: attribution-based self-initiation cannot by itself
  distinguish an intrinsic generator from a weakly coupled / isolated unit. A causal intervention (do(Z) inside vs
  input manipulation) is needed to tell them apart.
- Profile correlations are noisy across seed sets (plain r 0.10 here vs 0.59 in tick 82).

## Tick 86 — A26 generator signature per EIA block on the connectome (`tick86_generator_signature.py`)

Drive-units on SC with timescale hierarchy; out = drop of everyone else's activity when the block is silenced, divided
by the block's share of units; indep = block activity kept when its incoming cross-block links are cut. 2 subjects.

| block | out (per unit share) | indep |
|---|---|---|
| SMA | 11.5 | 0.10 |
| SAL | 9.8 | 0.17 |
| FPN | 6.5 | 0.15 |
| BG | 5.2 | 0.21 |
| DMN | 4.0 | 0.15 |
| SEN | 1.4 | 0.28 |
| VAL | 0.8 | **0.57** |

- **No block is a generator in the A26 sense**: every block loses ≥ 72 % of its activity when cut off from the rest
  (indep ≤ 0.28), except VAL (0.57), which also has the weakest out-influence — an *isolated*-type block (slow + weakly
  connected), not a generator.
- Endogeneity in the connectome model is **collective**: blocks drive each other (small hub-rich blocks SAL/SMA have the
  largest per-unit influence) but none sustains itself alone. DMN is a mid-level driver, not a self-sustaining source.
- Caveat: out is normalised by block size, which inflates small blocks; 2 subjects, 1 seed.

## Tick 96 — boundary degeneracy is not a detector artefact (`tick96_degeneracy_conditional.py`)

Split-half test on all 7 subjects, detection and scoring with the conditional-attribution graph (vs the pairwise detector).

| | pairwise split-half ARI | conditional split-half ARI | E_norm of first-half parts on second half (conditional) |
|---|---|---|---|
| mean of 7 | 0.08 | **0.04** | **0.38** |

- With the calibrated detector the two halves of a scan agree even less (0.04), while each half's partition stays strongly
  endogenous on the other half (0.38). **B9 holds with a better detector and 7 subjects**: many near-equivalent
  sub-agent decompositions, not one noisy one.

## Tick 97 — B10 re-checked with the conditional detector (`tick97_metastable_conditional.py`)

4 subjects × 2 seeds, homotopic h = 0.05, same split-half pipeline as tick 96.

| condition | split-half ARI | E_norm of first-half parts on second half |
|---|---|---|
| no gate | −0.00 | 0.24 |
| fixed gate | 0.20 | 0.55 |
| **switching gate (dwell 120 s)** | **0.06** | **0.43** |
| *empirical (tick 96)* | *0.04* | *0.38* |

- With the calibrated detector the metastable-gating model matches the empirical degeneracy even more closely than in
  tick 40 (0.06 / 0.43 vs 0.04 / 0.38); fixed gating stays too stable and too strong, no gating too weak. B10 robust.

## Tick 102 — periphery seeds, hubs amplify: also in the connectome model (`tick102_periphery_brain.py`)

Drive-units on SC (homogeneous timescales, no SNR differences), 4 subjects. Per region: share of initiatives that start a
cascade, activity, SC strength.

| | Spearman with SC strength |
|---|---|
| cascade-start share | **−0.84** (all subjects −0.82 … −0.87) |
| activity | **+0.95** |
| *empirical self-initiation (tick 79)* | *−0.55* |

- The model reproduces A32 on human anatomy: weakly connected regions seed cascades, hubs carry the activity.
- **Revises tick 79**: the empirical negative correlation between self-initiation and SC strength is *expected
  mechanistically*, not only an SNR artefact (orbitofrontal dropout still inflates the top of the raw ranking).
  Consequently residualising on strength (tick 80–81) also removes a real peripheral-seeding effect; the BG/DMN/SEN residual
  pattern (B14) is what remains *beyond* that effect.

## Tick 103 — does the model predict WHICH regions self-initiate? (`tick103_model_vs_emp_regions.py`)

Per subject, Spearman between the model's regional cascade-start share (tick 102) and empirical self-initiation (tick 79),
raw and partial on SC strength. 4 subjects.

| | mean ρ (range) |
|---|---|
| raw | **+0.33** (+0.27 … +0.43) |
| partial, controlling SC strength | **+0.03** (−0.10 … +0.24) |

- The model predicts the empirical regional pattern moderately (ρ ≈ 0.33, every subject positive), but **entirely through
  SC strength**: beyond strength it predicts nothing (partial ≈ 0). Anatomy explains the periphery-seeding part of the
  empirical profile; the remaining regional differences (incl. the BG/DMN excess of B14) need ingredients outside SC.

## Tick 127 — are empirical events paced by the slow global signal? (`tick127_global_phase.py` + inline leave-own-module-out check)

Global signal band-passed 0.01–0.03 Hz, Hilbert phase; PLV of each region's BOLD events to it; 7 subjects.

| | all regions | SMA | SEN | SAL | FPN | DMN | BG | VAL |
|---|---|---|---|---|---|---|---|---|
| PLV (global incl. own region) | 0.40 | 0.51 | 0.50 | 0.45 | 0.42 | 0.37 | 0.26 | 0.26 |
| PLV (global **excluding own module**) | **0.38** | 0.51 | 0.45 | 0.44 | 0.40 | 0.34 | **0.26** | **0.26** |
| null (circular shifts): mean / 95 % | 0.16 / 0.21 | | | | | | | |

- Real "spontaneous" events are strongly **paced by the slow global fluctuation** (PLV 0.38 vs null 0.16 / 0.21), and this
  survives removing the region's own module from the global signal — A36's "slow rhythms schedule *when*" holds in data.
- **Basal ganglia and value regions are the least paced** (0.26) — the same blocks that looked most self-initiating (B14–B15):
  their events keep their own timing rather than riding the global wave. Sensory and SMA are the most paced.
- Caveat: shared slow BOLD fluctuations (vascular / arousal / respiration) are a known confound; the global signal is not
  a pure "carrier".

## Tick 128 — region-level pacing vs self-initiation (`tick128_pacing_vs_selfinit.py`)

Spearman across regions between global-rhythm pacing (leave-own-module-out PLV) and residual self-initiation, per subject.

| | mean ρ | subjects negative | mean partial ρ (| event count) |
|---|---|---|---|
| pacing vs residual self-initiation | **−0.13** | 6/7 | −0.13 |

- Weak but consistent: regions less paced by the global slow rhythm self-initiate slightly more than their connectivity
  predicts (6/7 subjects negative, small effect). The module-level match of B14/B18 (BG, value: least paced, most
  self-initiating) is mostly a between-module effect; within the region set the link is weak.

## Tick 129 — global pacing in the connectome model (`tick129_model_pacing.py`)

Same leave-own-module-out PLV analysis on Hopf-model output (plain SC), 7 subjects.

| | all | DMN | SAL | BG | SMA | VAL | FPN | SEN |
|---|---|---|---|---|---|---|---|---|
| model | 0.24 | 0.27 | 0.26 | 0.23 | 0.24 | **0.15** | 0.28 | 0.26 |
| empirical | 0.38 | 0.34 | 0.44 | 0.26 | **0.51** | 0.26 | 0.40 | 0.45 |

- The model shows weaker global pacing (0.24 vs 0.38) and only partly the module pattern (r = 0.57): it reproduces the *low*
  end (VAL lowest, BG low — weakly connected regions ride the global wave less, an anatomical effect) but not the strong
  pacing of SMA/SAL/SEN. The extra empirical pacing of those blocks is not explained by SC — plausibly arousal/vascular
  global fluctuations that act most on sensorimotor and salience regions.

## Tick 137 — conduction delays from real tract lengths (`tick137_delays.py`)

Drive-units on SC; between-region links delayed by length / velocity (1 tick = 1 ms), 8 delay classes; rate-matched;
2 subjects × 2 seeds.

| velocity | median delay | burst CV | envelope autocorrelation | period (ticks) | EIA-module E_norm* |
|---|---|---|---|---|---|
| no delays | 0 | 1.56 | 0.58 | 12 | 0.22 |
| 10 m/s | 13 ms | 1.20 | **0.95** | 12 | 0.10 |
| 3 m/s | 44 ms | **0.44** | **0.99** | 19 | 0.09 |

\* E_norm here attributes causes at a 1-tick lag; with delays the true causes are k ticks back, so the E_norm drop is
at least partly a **measurement artefact** — not interpreted.

- Realistic conduction delays turn the collective activity into a **near-periodic oscillation** (envelope autocorrelation
  0.95–0.99; burst CV down to 0.44 at slow conduction): the network generates its *own* carrier rhythm from wiring
  geometry. Per A36/A37 such an intrinsic rhythm acts as an internal scheduler of *when* initiatives occur.
- Link to the Kairologos carrier assumption: a fast carrier need not be imposed — delays + recurrent coupling produce one;
  its period is set by delays and refractoriness (12–19 ms here ≈ 50–80 Hz in this toy time scale).
- Method note: every lag-1 attribution metric (E, E_norm, conditional attribution) must be generalised to multi-lag before
  it is used on delayed systems.

## Tick 138 — multi-lag endogeneity under delays (`tick138_multilag_E.py`)

Causes attributed per delay class (input via M_k comes from spiking at t − 1 − k). 2 subjects × 1 seed.

| velocity | E_norm, lag-1 attribution | E_norm, multi-lag attribution |
|---|---|---|
| none | 0.22 | 0.22 |
| 10 m/s | 0.14 | **0.20** |
| 3 m/s | 0.05 | **0.25** |

- With correct (multi-lag) attribution, **sub-agent endogeneity is unchanged by delays** (0.20–0.25 vs 0.22): the tick-137
  drop was entirely a lag-1 measurement artefact — the lag-1 metric fell to 0.05 while the true value did not move.
- So delays change *when* (intrinsic carrier, B19) but not *who/why* — the same separation as for imposed carriers (A36).
- Method rule: endogeneity metrics must match the system's causal lags; a lag mismatch silently reads delayed internal
  causation as external. (Relevant for any LLM/agent log with variable latencies.)

## Tick 141 — B9 with the lag-selective detector (`tick141_degeneracy_lagsel.py`)

Split-half test on 7 subjects with the lag-selective detector (best lag 1–3 TR per pair) for detection and attribution.

| detector | split-half ARI | held-out E_norm of first-half parts |
|---|---|---|
| pairwise summed lags (tick 39) | 0.08 | — |
| conditional summed lags (tick 96) | 0.04 | 0.38 |
| **lag-selective** | **0.02** | **0.29** |

- Degeneracy is **not** a detector artefact: with the lag-selective detector the two halves agree even less (0.02), and the
  first-half partition stays endogenous on the held-out half (0.29, lower than 0.38). B9 holds under all three detectors.

## Tick 146 — activity-bound routing on the human connectome (`tick146_routing_brain.py`)

Drive-units on SC with co-activity gating; E_norm (true time-averaged W, unit level) of anatomical vs functional partitions;
2 subjects.

| β | hemispheres | SC communities | EIA map |
|---|---|---|---|
| 0 | 0.80 | 0.71 | 0.23 |
| 2 | 0.82 | 0.59 | 0.19 |

- **A38 does not transfer as is**: routing leaves the model bounded by anatomy (hemispheres 0.80 → 0.82) and does not raise the
  functional EIA partition. Routing only re-weights *existing* edges; where cross-hemisphere / cross-community edges are sparse
  (SC), there is nothing to route through. (Magnitudes are true-W unit-level values, not comparable one-to-one with the blind
  empirical numbers.)
- So function-over-anatomy in the brain needs both: enough cross-anatomical wiring (e.g. homotopic links, B8) *and* a routing /
  gating mechanism to use it (B5, A38). Next: routing + homotopic boost.

## Tick 147 — routing × homotopic boost (`tick147_routing_homotopic.py`)

Drive-units on SC; E_norm (true time-averaged W) of hemispheres / SC communities / EIA map; 2 subjects.

| β | h | hemispheres | SC communities | EIA map |
|---|---|---|---|---|
| 0 | 0 | 0.80 | 0.71 | 0.23 |
| 2 | 0 | 0.82 | 0.59 | 0.19 |
| 0 | 0.1 | 0.54 | 0.61 | **0.35** |
| 2 | 0.1 | **0.46** | **0.49** | 0.28 |

- The homotopic boost is what moves boundaries off anatomy (hemispheres 0.80 → 0.54) and raises the functional EIA partition
  (0.23 → 0.35). Routing on top loosens anatomy further (hemispheres 0.46, SC communities 0.49) but does not raise the EIA
  partition (0.28): it produces *activity* coalitions, not specifically the EIA blocks.
- Consistent with B8 (homotopic links → hemisphere boundary dissolves) and with the tick-146 reading: cross-anatomical wiring
  is necessary; routing only amplifies its use. The EIA-specific pattern still needs the gating of B5 / B18.
