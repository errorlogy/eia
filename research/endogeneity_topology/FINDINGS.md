# Endogeneity × Topology — consolidated findings (ticks 1–33, 2026-09-29)

Exploratory, toy-model and small-sample evidence. "Status" says how far each claim survived our own
replications and controls. Details and numbers: [`toy/LOG.md`](toy/LOG.md),
[`human_connectome/RESULTS.md`](human_connectome/RESULTS.md), [`eia_prototype/`](eia_prototype/).

## A. What topology does to endogenous initiative (toy drive-unit networks, X_trigger = 0)

| # | Claim | Evidence | Status |
|---|---|---|---|
| A1 | Uncertainty aging alone is an internal *clock* (ISI CV ≈ 0.16), not rich initiative | tick 1 | holds |
| A2 | Modularity smooths the silence→seizure transition (~5× smaller max rate jump) and shifts critical gain right | ticks 3–5, N=3000, 5 seeds | **robust** |
| A3 | Modularity widens the rich band | ticks 1–5 | weak: only hierarchy, +33% |
| A4 | Hierarchical-modular graphs contain a do(Z) perturbation best at matched activity | ticks 6–8 | **robust** (10 seeds) |
| A5 | Hierarchy has the strongest local do(Z) effect | tick 7 | withdrawn (tick 8: ER equal) |
| A6 | Spill-over sign depends on topology: ER contagion (+), hierarchy suppression (−) | tick 8 | holds (z ±2–3) |
| A7 | Suppression is "discharge" | tick 8 | **refuted** (tick 9) |
| A8 | Both signs are carried by one channel: triggered initiatives resolving neighbours' uncertainty | tick 10 | holds, with regime-shift caveat |
| A9 | ~92% of unit-level initiatives are neighbour-triggered: endogeneity is boundary-dependent | tick 10–11 | **robust** |
| A10 | Endogeneity profile E(B): natural self-boundaries exist in modular / hierarchical graphs, not in ER | tick 11 | **robust** |
| A11 | Self-boundaries are recoverable blind from activity (held-out); with conditional attribution + null-normalised E_norm the blind profile is calibrated (within 0.03 of truth) | ticks 12–13, 35 | **robust** |
| A12 | Sub-agents become *blindly discoverable* from activity only when < ~10–15 % of a module's links leave it (μ_c ≈ 0.08–0.15). With known labels they are already strongly endogenous at μ = 0.3 (E_norm ≈ 0.75) — μ_c is a discoverability, not an existence, threshold | ticks 22–24, 43 | **robust (reinterpreted)** |
| A13 | Hierarchy steepness, not ultrametricity per se, controls sub-agents (p-adic α_c ≈ 1.45) | ticks 22–23 | holds |
| A14 | Hyperbolic graphs behave like scale-free dynamically (never rich) but have real sub-agents | tick 22 | holds, not rate-matched |
| A15 | Lateral inhibition between modules removes the sparsity requirement (sub-agents at μ = 0.3) | tick 25 | holds (partly by construction) |
| A16 | Lateral inhibition abolishes per-motive controllability | tick 26 | withdrawn (tick 27) |
| A17 | Under lateral inhibition, controllability is state-dependent: boosting a non-dominant motive = takeover; boosting the dominant one ≈ inert | ticks 27–28 | holds (n = 40); sign flip withdrawn |
| A18 | Collective (network-level) endogeneity requires cycles: a strict DAG never self-amplifies (×6 at branching 1.5, only per-unit aging clocks), while any cyclic directed/undirected graph shows the onset at g≈1 | holds (tick 49) |
| A19 | The fraction of recurrent (cycle-forming) edges sets loop gain ρ(W)/g continuously; onset follows ρ(W) ≈ 1; sparse recurrence (2–5 % reversed edges) gives strong but graded collective amplification, dense recurrence a sharp onset | holds (tick 50, 2 seeds) |

## B. Human connectome (HCP, AAL2, 4 subjects)

| # | Claim | Status |
|---|---|---|
| B1 | In a homogeneous Hopf model, initiative at X = 0 is a distributed hub property, not DMN-specific (strength-matched control beats DMN) | holds |
| B2 | That model has no *functional* self-boundaries; calibrated attribution shows it *is* bounded by anatomy (hemispheres E_norm 0.37), while the real brain is bounded by function (found parts 0.68, EIA map 0.25, hemispheres 0.05) | revised (tick 36) |
| B3 | Empirical rs-fMRI has functional self-boundaries: sensory / DMN+value / BG+SMA / FPN, partly consistent across people | holds (4 subjects) |
| B4 | Not a hemodynamic lag (≤ 2 s) or SNR (≤ 3×) artefact | holds; motion/physio untested |
| B5 | Local excitability / frequency heterogeneity cannot reproduce B3; tonic inter-block gating can | holds |
| B6 | Gating explains FC | **withdrawn** (does not cross-validate) |
| B7 | Population (leave-one-out) blocks + gating predict a held-out subject's boundaries | holds (4/4 folds, ARI ≈ 0.17) |
| B9 | Empirical self-boundaries are **degenerate**: split-half partitions barely agree (ARI 0.09) yet each stays endogenous on held-out data (E_norm ≈ 0.45). Held-out empirical strength is ≈ 0.42–0.49 (tick-36 0.68 was inflated). Fixed-gating models impose one rigid partition and miss this | holds (tick 39) |
| B10 | Metastable gating (switching among a repertoire of decompositions, dwell ≈ 2 min) reproduces the degenerate empirical profile (ARI 0.17 / E 0.55 / 0.41 vs 0.09 / 0.49 / 0.42); fixed gating does not (0.43 / 0.77 / 0.69). Toy check: fixed modular networks are *not* degenerate (ARI 0.66–0.98); switching decompositions makes them so (0.43) | holds (ticks 40, 42) |
| B11 | In the human model, gating multiplies the local effect of do(Z) on the DMN+value block (+6.6 % → +16.8 %, paired z 5.7) and cuts leakage ~85 % (+4.5 % → +0.7 %, z −13) — containment like toy A4. The tick-44 suppression (sign flip) did not replicate at n = 24 | **robust** (tick 45); sign flip withdrawn |
| B12 | With excitatory drive-units on the human connectome, onset of self-driven activity is smoother for real SC than randomised SC (max jump 10.5 vs 16.8) and ~2.8× smoother again with functional gating (3.8); homotopic links add nothing to smoothness — toy A2 transfers to human anatomy | **robust** (ticks 47–48, 4 subj × 2 seeds) |
| B8 | SC + modest homotopic boost (h≈0.05–0.1) + tonic functional gating reproduces the empirical endogeneity profile on held-out subjects (EIA map 0.19–0.27 vs 0.25; hemispheres 0.06/−0.10 vs 0.05); subject-specific parts ≈ 0.3 vs held-out empirical ≈ 0.45 (see B9); FC does not constrain it | holds (ticks 37–38, 1 seed) |

## C. MVP-0 pipeline audit (eia_prototype)

| # | Finding | Evidence |
|---|---|---|
| C1 | `DriveEngine` has no intrinsic dynamics in silence: drives pin at saturation or decay to 0 | probe + tick 29 |
| C2 | `PopulationDriveEngine` (populations + aging/noise + μ + optional lateral inhibition) runs unchanged inside the pipeline; bursty initiative in silence; toy findings A12/A6/A15 carry over qualitatively | ticks 29–30 |
| C3 | `AuthenticReason._drive_is_structural` is a **keyword test on the explanation string** — wrong in both directions (baseline 7/7 vs causal 4/7; population 0/7 vs causal 5/7) and gameable by wording | ticks 30–31 |
| C4 | IntentionGenesis ranks candidates by per-kind constants first; drive intensity acts as a gate (≥ 0.2), not a weight | tick 32 |
| C5 | Different drives often target the same belief → overdetermined initiatives; single-drive do() misses them, joint do() finds them | tick 32 |
| C6 | Baseline drive *state* is causally inert in 2/7 scenarios (field alone determines initiative); the field→drive *channel* is causal in 7/7 | ticks 32–33 |
| C7 | `source_drives` over-credits one drive where Shapley splits ≈ 0.5/0.5 | tick 33 |
| C8 | Static audit: in `run_scenario` the cognitive cycle is a DAG per episode (only a leaky drive self-loop); the satisfaction channel is dead code; `shadow_multitick` closes Action→Belief but with a content-free update (zero loop gain); novelty is a constant schedule | tick 51 |
| C9 | In silence MVP-0 perseverates: the same question is proposed in 30/30 episodes, the Governor denies 29; closing Action→Belief does not help because intention selection ignores drive state and denials (no goal succession) | tick 52 |
| C10 | System card (harness): proposed combination (population drives + closed loop + state-IOR) vs current — questions in 200 silent episodes 200 → 3.6, same-question run 199 → 1, ISI CV 0.03 → 1.24, drive-dependence 0.71 → 0.99; cost: first eval initiative unchanged 0.81, EOI 0.82 | tick 57 |

## D. Concrete proposals for EIA

1. **Replace the lexical structural gate** (`src/eia/audit/authentic_reason.py:122–126`) with a causal test:
   from the post-cognition snapshot, re-run MotiveFormation → IntentionGenesis under do(silence drive
   subsets); record Shapley φ and v(all) under *state-only* and *state + channel* interventions.
   Classify initiatives as field-driven / memory-driven / overdetermined. Cost: ≤ 8 extra computes.
2. **Give drives intrinsic dynamics** (aging + noise, or the population engine) so that silence produces
   graded, bursty initiative instead of pinning or decay (C1); calibrate readout before behavioural use.
3. **Design rule for motive graphs**: excitatory cross-motive coupling ≲ 10 % of a motive's coupling if
   motives must be auditable *without labels* (A12; with labels, ≲ 30 % suffices); dense cross-coupling only as mutual inhibition (A15). Prefer hierarchical organisation for
   containment (A4) and graded endogeneity gain (A2).
4. **Audit at natural boundaries**: compute the endogeneity profile E(B) and audit initiatives (EOI,
   AuthenticReason) at the boundary with the largest E jump (A10–A11); auditing at a non-natural
   boundary labels most initiatives exogenous.
5. **Condition intervention audits on dominance state** when the governor is competitive (A17).
6. **Close the loop through IntentionGenesis** (C4, C9): minimal eval-compatible step = inhibition of return on
   asked/denied targets (tick 53: perseveration 29 → 1 episodes, first initiative unchanged 100 %) — with a
   *state-dependent* release, since fixed-decay IOR is itself a hidden clock (tick 54: CV 0.03 with one belief);
   re-admitting a target only when its belief's entropy has grown cuts re-asking ~10× and makes timing follow
   the world's staleness statistics (tick 55: CV ≈ 1); drive-weighted
   choice is a later step (changes eval initiatives). Also make IntentionGenesis sensitive to drive intensity
   beyond a gate, otherwise drive dynamics
   cannot shape *which* initiative is chosen.
7. **Governor as constitutive, not add-on**: in the human data, functional self-boundaries need tonic
   gating (B5) — the Governor role is part of what makes sub-agents endogenous.
8. **Metastable decomposition**: let the Governor re-route among several motive decompositions on a slow
   timescale (B9–B10) instead of fixing one; audit the ensemble of high-E_norm partitions.
9. **Close the cognitive loop with state-dependent, sparse, sub-unity gain** (A18–A19, C8): feed contact
   outcomes into `satisfaction`, make post-action belief updates depend on the action, derive novelty from
   state; report the measured loop gain as an architectural metric. See `eia_prototype/tick51_pipeline_loops.md`.

## E. Open threads
- finer parcellation (Schaefer-200) and empirically fitted local dynamics for the human model
- causal gate (D1) as an actual patch + tests in `src/`, then re-run PAI-EI-E0-001 baselines
