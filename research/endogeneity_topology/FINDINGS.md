# Endogeneity × Topology — consolidated findings (ticks 1–97, 2026-09-29/30)

Exploratory, toy-model and small-sample evidence. "Status" says how far each claim survived our own
replications and controls. Details and numbers: [`toy/LOG.md`](toy/LOG.md),
[`human_connectome/RESULTS.md`](human_connectome/RESULTS.md), [`eia_prototype/`](eia_prototype/),
draft patches: [`patches/`](patches/).

## TL;DR — twelve takeaways

1. **Endogeneity is a property of (system, boundary)**, not of a system: single units are ~7 % self-caused; natural
   sub-agent boundaries are where the endogeneity profile E(B) jumps (A9–A11), and can be found blind (A11).
2. **Sub-agents need sparse excitatory cross-coupling to be discoverable** (μ ≲ 0.1–0.15, A12) — or dense *inhibitory*
   cross-coupling (A15). With labels they are endogenous up to μ ≈ 0.3.
3. **Collective endogeneity needs cycles** (A18); sparse recurrence and modular/hierarchical wiring give a graded,
   controllable onset (A2, A19, B12); criticality gives richness *within* a motive but flattens differences *between*
   motives (C12).
4. **Attribution ≠ generation**: attribution-based metrics (EOI-style, E(B), self-initiation) reward isolation; a
   generator must keep activity when inputs are cut *and* drive others (A26, B15).
5. **Human brain**: functional self-boundaries (sensory / DMN+value / BG+SMA / FPN) exist, are degenerate/metastable
   (B3, B9–B10) and need tonic gating, not just wiring (B5); sensory cortex is the most externally driven region
   empirically and in models (B13–B14).
6. **DMN specificity is a model–data gap**: data show a modest DMN (and BG) self-initiation excess (B14), no connectome
   model reproduces DMN's (B1 robust, B16); BG's is explained by weak input (B15).
7. **MVP-0 audit**: the structural-drive gate is lexical and wrong both ways (C3); the cognitive cycle is a DAG (C8); in
   silence the agent perseverates on one question (C9).
8. **Fixes that keep evals unchanged**: causal drive attribution (D1), state-dependent inhibition of return (D6), crash
   guard (C11) — as draft patches with tests.
9. **Calibrated population drives** (tension-set uncertainty targets, subcritical motives) keep eval initiatives 100 %
   while making silent initiative sparse, irregular and drive-dependent (C12–C13).
10. **Learning**: plain Hebbian plasticity builds integrative highways, not sub-agents; competitive synchronous learning
    grows weak but functional sub-agents (A22–A23).
11. **Generators vs relays**: topology alone makes relays (central, high influence, dependent), not generators; a strong
    intrinsic generator crowds other motives out of the activity budget rather than enslaving them (A26–A28).
12. **Governor recipe** (robust across topologies): slow, leaky, upward-only cap on each motive's *chronic* activity
    share + a global budget loop with a slow integral. Integrating the per-motive loop fast reverses controllability
    (A29, proposal 4c). Detector quality matters: calibrated inference doubles the blind-discoverability threshold (A12).

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
| A12 | Sub-agents become *blindly discoverable* from activity only when < ~10–15 % of a module's links leave it (μ_c ≈ 0.08–0.15). With known labels they are already strongly endogenous at μ = 0.3 (E_norm ≈ 0.75) — μ_c is a discoverability, not an existence, threshold; with calibrated conditional inference μ_c roughly doubles (0.08 → 0.17), so it depends on the detector too | ticks 22–24, 43, 95 | **robust (reinterpreted)** |
| A13 | Hierarchy steepness, not ultrametricity per se, controls sub-agents (p-adic α_c ≈ 1.45) | ticks 22–23 | holds |
| A14 | Hyperbolic graphs behave like scale-free dynamically (never rich) but have real sub-agents | tick 22 | holds, not rate-matched |
| A15 | Lateral inhibition between modules removes the sparsity requirement (sub-agents at μ = 0.3) | tick 25 | holds (partly by construction) |
| A16 | Lateral inhibition abolishes per-motive controllability | tick 26 | withdrawn (tick 27) |
| A17 | Under lateral inhibition, controllability is state-dependent: boosting a non-dominant motive = takeover; boosting the dominant one ≈ inert | ticks 27–28 | holds (n = 40); sign flip withdrawn |
| A18 | Collective (network-level) endogeneity requires cycles: a strict DAG never self-amplifies (×6 at branching 1.5, only per-unit aging clocks), while any cyclic directed/undirected graph shows the onset at g≈1 | holds (tick 49) |
| A19 | The fraction of recurrent (cycle-forming) edges sets loop gain ρ(W)/g continuously; onset follows ρ(W) ≈ 1; sparse recurrence (2–5 % reversed edges) gives strong but graded collective amplification, dense recurrence a sharp onset | holds (tick 50, 2 seeds) |
| A20 | Higher-order (coincidence) interactions add effective gain (onset at lower pairwise coupling) but produce no bistability/hysteresis in noisy refractory units — no latching regime | directional (tick 66, 1 seed) |
| A21 | A sparse cross-module hub ("global workspace") layer doubles global ignitions (13.5 → 27.7 / 1000 ticks, up to 9/10 modules) while module endogeneity stays ≈ intact (E_norm 0.97 → 0.95) — broadcast without dissolving sub-agents. But a single motive's boost does *not* recruit ignition; it suppresses it (−5.8 / 1000 t, z −2.2) — ignitions are emergent, not motive-triggered | holds (ticks 67–68) |
| A22 | Plain lagged-Hebbian plasticity + rate homeostasis on ER does not grow sub-agents: weights become heterogeneous (CV 0.5) but modularity stays below the shuffled null (0.33 vs 0.41) — learning builds cross-module cascade highways | holds (tick 69, 2 seeds) |
| A23 | Plasticity rule decides the sign: lagged Hebb is anti-modular (Q − Q_null −0.075), synchronous Hebb with competitive input/output normalisation is modular (+0.02), + global inhibition +0.04 — sub-agents can self-organise, but slowly and weakly; the learned communities are functional (E_norm +0.12–0.14 vs the same partition on unlearned weights, 3 seeds; lagged Hebb ≈ 0) | **robust** (ticks 70–72) |
| A24 | Spatial exponential-distance wiring (cortex-like EDR) without modules gives a characteristic sub-agent size ≈ 3λ (side where E_norm = 0.5: 0.17 at λ 0.05, 0.35 at λ 0.12) — continuous, location-free sub-agents with tunable grain; the signed causal reach of do(Z) matches it (ℓ ≈ 4λ at λ 0.05; centre–surround sign flip at λ 0.12), while trajectory divergence is global | holds (ticks 73–74) |
| A25 | A timescale hierarchy (slow vs fast drive integration, equal equilibrium) makes slow modules the internal generator: ×4.3 activity, higher endogeneity (0.96 vs 0.89), ~2.5× more slow→fast than fast→slow triggering in absolute terms | holds (tick 75, 3 seeds) |
| A26 | Attribution-based self-initiation cannot tell an intrinsic generator from an isolated module (isolated scores highest, 1.00). Two interventions can: generator = high out-influence (0.17) + high independence (0.82); isolated = low out-influence (0.10) + high independence (0.92) | holds (tick 85, 4 seeds) |
| A27 | Topology alone makes relays, not generators: the hub module of a star gets the largest out-influence (5.4) but the lowest independence (0.18); ring/complete stay collective. Centrality ≠ generator; generators need intrinsic excitability (A26) | holds (tick 87, 2 seeds) |
| A28 | A stronger intrinsic generator becomes self-sustaining (indep 0.49 → 0.97) and takes more of the activity budget (share 0.17 → 0.42) without driving others more or dissolving their sub-agency (E 0.94 → 0.91): crowding-out, not enslavement — cap activity share per motive | holds (tick 88, 2 seeds) |
| A29 | A share-capping Governor (adaptive per-module threshold) holds a strong generator at its cap (0.42 → 0.14) without destroying its self-sustainment (0.91) and restores the others' endogeneity (0.91 → 0.94); cost: total initiative −38 %. Adding a global rate-holding loop removes the cost (rate 0.035 vs 0.029, share 0.07, generator indep 0.90, others 0.94); a share rule that lets others' thresholds drop without the global loop runs away (rate ×5). **But** the integrating two-loop Governor reverses per-motive controllability (boosting a motive: +153 → −343 initiatives, tick 91) — share control must be leaky / deadbanded. A slow, leaky, upward-only chronic-dominance Governor caps the motive (0.41 → 0.14) while keeping controllability (boost +158, z 4.4); a slow integral on the global loop narrows the rate shortfall (0.025) with controllability intact (+181, z 4.3); the recipe transfers to hierarchical and ER graphs (cap holds, controllability kept or improved) | **robust** (ticks 89–94) |
| A30 | At X = 0 a world that merely echoes the agent's own actions silently supports ~13 % of its activity (cut-the-world test) while only ~4–5 % of initiatives show a direct world cause — attribution under-counts externalised loops ~3×; audits need a world-cut / non-contingent-replay intervention. Hidden support is 1.6–4.5× the direct share at all delays and ~2× larger in an ER agent (≈ 0.32) than a modular one (≈ 0.15): modularity protects against externalised endogeneity | holds (ticks 98–99, 3 seeds) |
| A31 | World-cut vs non-contingent replay separates two kinds of external support: the modular agent needs only input volume (replay fully substitutes), the ER agent's larger dependence (cut → 0.64) is ~30 % contingency — a genuine externalised memory loop | holds (tick 100, 3 seeds) |
| A32 | Core–periphery: the sparse periphery seeds 87 % of cascades (independence 0.51), the dense core amplifies them (70 % of activity, highest influence, independence 0.21) — endogeneity as peripheral sparks × core amplification | holds (tick 101, 3 seeds) |

## B. Human connectome (HCP, AAL2, 4 subjects)

| # | Claim | Status |
|---|---|---|
| B1 | In a homogeneous Hopf model, initiative at X = 0 is a distributed hub property, not DMN-specific (strength-matched control beats DMN) | **robust**: holds across all variants tried — heterogeneous Hopf, drive-units, timescale hierarchy, gating + homotopic (`control_e3.py`, `hetero.py`, ticks 76–77); doubling DMN excitability buys only +0.05 specificity (tick 78) |
| B2 | That model has no *functional* self-boundaries; calibrated attribution shows it *is* bounded by anatomy (hemispheres E_norm 0.37), while the real brain is bounded by function (found parts 0.68, EIA map 0.25, hemispheres 0.05) | revised (tick 36) |
| B3 | Empirical rs-fMRI has functional self-boundaries: sensory / DMN+value / BG+SMA / FPN, partly consistent across people | holds (4 subjects) |
| B4 | Not a hemodynamic lag (≤ 2 s) or SNR (≤ 3×) artefact | holds; motion/physio untested |
| B5 | Local excitability / frequency heterogeneity cannot reproduce B3; tonic inter-block gating can | holds |
| B6 | Gating explains FC | **withdrawn** (does not cross-validate) |
| B7 | Population (leave-one-out) blocks + gating predict a held-out subject's boundaries | holds (4/4 folds, ARI ≈ 0.17) |
| B9 | Empirical self-boundaries are **degenerate**: split-half partitions barely agree (ARI 0.09) yet each stays endogenous on held-out data (E_norm ≈ 0.45). Held-out empirical strength is ≈ 0.42–0.49 (tick-36 0.68 was inflated). Fixed-gating models impose one rigid partition and miss this. Confirmed with the conditional detector on 7 subjects (split-half ARI 0.04, held-out E_norm 0.38) | **robust** (ticks 39, 96) |
| B10 | Metastable gating (switching among a repertoire of decompositions, dwell ≈ 2 min) reproduces the degenerate empirical profile (ARI 0.17 / E 0.55 / 0.41 vs 0.09 / 0.49 / 0.42); fixed gating does not (0.43 / 0.77 / 0.69). Toy check: fixed modular networks are *not* degenerate (ARI 0.66–0.98); switching decompositions makes them so (0.43). Re-checked with the conditional detector: switching 0.06 / 0.43 vs empirical 0.04 / 0.38 | **robust** (ticks 40, 42, 97) |
| B11 | In the human model, gating multiplies the local effect of do(Z) on the DMN+value block (+6.6 % → +16.8 %, paired z 5.7) and cuts leakage ~85 % (+4.5 % → +0.7 %, z −13) — containment like toy A4. The tick-44 suppression (sign flip) did not replicate at n = 24 | **robust** (tick 45); sign flip withdrawn |
| B12 | With excitatory drive-units on the human connectome, onset of self-driven activity is smoother for real SC than randomised SC (max jump 10.5 vs 16.8) and ~2.8× smoother again with functional gating (3.8); homotopic links add nothing to smoothness — toy A2 transfers to human anatomy | **robust** (ticks 47–48, 4 subj × 2 seeds) |
| B13 | On the human connectome a timescale hierarchy (slow DMN+value, fast sensory) does not make DMN more specific than hubs (0.26 vs 0.25 remaining), but makes initiative largely independent of sensory cortex (silencing it: 0.36 → 0.80 of loop activity kept) | holds (tick 76, 2 subj × 2 seeds) |
| B14 | Empirical: after regressing out SC strength, inferred in-degree and event count, basal ganglia (+0.052, p 0.006) and DMN (+0.034, p 0.033) self-initiate more than connectivity predicts and sensory cortex less (−0.066, p 0.007), each in 7/7 subjects; the raw orbitofrontal 'top' was a dropout artefact. No connectome model tried reproduces the BG/DMN excess on held-out subjects (the tick-82 gating match, r 0.85, was circular: held-out r 0.36 vs plain 0.51 — withdrawn); models only get the sensory deficit. Open model–data gap with B1 | holds (ticks 79–83, 7 subjects; DMN nominal, BG/SEN Bonferroni-significant) |
| B15 | The empirical BG self-initiation excess is reproduced by weakening effective cortical input to BG (k 0.1: +0.042 vs empirical +0.052) — BG looks self-starting because it is weakly driven. Attribution-based self-initiation conflates intrinsic generation with isolation; only interventions separate them | holds (tick 84, 7 subj × 2 seeds) |
| B16 | By the A26 signature, no EIA block on the connectome model is a self-sustaining generator: all keep ≤ 28 % of activity when cut off (VAL 57 % but lowest out-influence → isolated-type); endogeneity is collective across blocks, DMN a mid-level driver | holds (tick 86, 2 subjects) |
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
| C12 | Subcritical population motives with tension-set uncertainty targets make the population engine eval-compatible (first initiative unchanged 100 %) while keeping irregular silent initiative (CV ≈ 1); near-critical motives flatten between-drive differences | tick 62 |
| C13 | System card v2 (calibrated: tension-set targets + subcritical motives): first eval initiative unchanged 1.00, EOI 0.95, drive-dependence 0.98, silent questions 200 → 4.6, same-question run 199 → 1, ISI CV 0.03 → 1.17 | tick 63 |
| C11 | Latent crash: `pipeline.py:159` assumes `motivation.dominant_drive` is not None although the schema allows None (all-zero drives) | tick 60 |

## D. Concrete proposals for EIA

1. **Replace the lexical structural gate** (`src/eia/audit/authentic_reason.py:122–126`) with a causal test:
   from the post-cognition snapshot, re-run MotiveFormation → IntentionGenesis under do(silence drive
   subsets); record Shapley φ and v(all) under *state-only* and *state + channel* interventions.
   Classify initiatives as field-driven / memory-driven / overdetermined. Cost: ≤ 8 extra computes.
2. **Give drives intrinsic dynamics** (aging + noise, or the population engine) so that silence produces
   graded, bursty initiative instead of pinning or decay (C1); let BeliefField tension set the uncertainty
   *target* rather than its growth rate (ticks 58–60), and run motives **subcritical** (recurrent gain ≈ 0.4):
   within-scenario tension–intensity ρ 0.91, eval initiative unchanged 100 %, silent CV ≈ 1 (tick 62).
3. **Design rule for motive graphs**: excitatory cross-motive coupling ≲ 10 % (pairwise detector) or ≲ 15–20 %
   (conditional detector, tick 95) of a motive's coupling if motives must be auditable *without labels* (A12; with labels, ≲ 30 % suffices); dense cross-coupling only as mutual inhibition (A15). Prefer hierarchical organisation for
   containment (A4) and graded endogeneity gain (A2).
4. **Audit at natural boundaries**: compute the endogeneity profile E(B) and audit initiatives (EOI,
   AuthenticReason) at the boundary with the largest E jump (A10–A11); auditing at a non-natural
   boundary labels most initiatives exogenous.
4b. **Define 'internal generator' by two interventions**, not attribution: keeps activity when inputs are cut AND
   drives others when present (A26) — otherwise audits reward mere isolation.
4c. **Governor recipe** (A28–A29): cap each motive's *chronic* activity share with a slow, leaky, upward-only threshold
   term, plus a global budget loop with a slow integral; never integrate the per-motive loop on fast timescales
   (it reverses controllability).
4d. **X = 0 audits need two world interventions** (A30–A31): world-cut (total external support) and non-contingent replay
   (the contingent agent–world loop); attribution under-counts both.
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
- B14 with many more HCP subjects (and SNR-matched regions): is empirical DMN self-initiation real, and what model ingredient reproduces it?
