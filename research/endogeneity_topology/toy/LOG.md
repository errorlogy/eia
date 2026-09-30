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

## Tick 9 — discharge hypothesis, 3 do(Z) variants × 10 seeds (`tick9.py`)

| topology | variant | extra in S (z) | spill-over total (z) | spill-over first 100 ticks (z) |
|---|---|---|---|---|
| ER | full (d=1,u=1) | +93 (4.9) | +517 (2.2) | +600 (3.0) |
| ER | u only | +121 (5.1) | +954 (3.0) | +891 (3.7) |
| ER | d only | +84 (3.2) | +751 (2.2) | +557 (2.7) |
| hier | full | +82 (4.1) | −452 (−3.2) | +28 (0.6) |
| hier | **u only** | +84 (3.8) | **−627 (−5.3)** | +6 (0.1) |
| hier | d only | +41 (3.2) | −207 (−1.4) | −13 (−0.3) |

- **Discharge hypothesis refuted**: no forced spike (u only) gives the *strongest*
  suppression; a forced spike alone (d only) gives the weakest (n.s.).
- Suppression is **delayed**: zero in the first 100 ticks, builds later.
- New hypothesis — **fuel depletion**: a module with raised uncertainty becomes a
  persistent initiator; its frequent small cascades drive neighbours often, each
  neighbour initiative resolves their uncertainty (RESOLVE·u), draining the "fuel"
  that would power later large avalanches. In ER the same drive is contagion because
  there are no super-module walls to keep cascades small.

## Tick 10 — fuel-depletion test (`tick10.py`)

Variant `no_trig_resolve`: initiatives triggered by neighbour input do not resolve
uncertainty (spontaneous ones still do). Global RESOLVE=0 is degenerate (u→1, d* > θ).
u-only do(Z), rate-matched, 10 seeds × 5 modules.

| topology | variant | gain | triggered initiatives | extra in S (z) | spill-over (z) |
|---|---|---|---|---|---|
| ER | base | 0.97 | 92% | +121 (5.1) | **+954 (3.0)** |
| ER | no_trig_resolve | 0.52 | 73% | +87 (6.5) | +22 (0.2) |
| hier | base | 1.01 | 92% | +84 (3.8) | **−627 (−5.3)** |
| hier | no_trig_resolve | 0.55 | 73% | +226 (12.2) | +77 (0.6) |

- **Hier suppression vanishes** when triggered initiatives stop draining uncertainty →
  consistent with fuel depletion. But **ER contagion vanishes too**: the channel
  "triggered initiative resolves neighbour's uncertainty" mediates inter-motive
  influence in *both* directions; topology decides the sign.
- Without the drain, do(Z) on a motive becomes strongly local (hier z 12).
- Caveat: operating gain halves (0.97 → 0.52) — regime shift, not a clean ablation.
- Side result: **92% of initiatives are cascade-triggered**, only ~8% spontaneous. At
  system level the network is endogenous (X=0); at unit level almost every initiative has
  an "external" (neighbour) cause. Endogeneity is level-dependent — boundary choice
  matters (cf. Markov-blanket point, growth item 18).

## Tick 11 — endogeneity profile E(boundary size) (`tick11.py`)

E(B) = fraction of initiatives in part B that are spontaneous or ≥50% triggered from
inside B. Rate-matched (0.03), N=1000, 3 seeds. Aligned = structural partition
(contiguous blocks; greedy BFS balls for ER); random = null.

| topology | partition | 1 | 10 | 50 | 250 | 1000 |
|---|---|---|---|---|---|---|
| small-world | aligned | 0.06 | **0.80** | 0.89 | 0.93 | 1 |
| ER | aligned | 0.08 | 0.34 | 0.41 | 0.59 | 1 |
| modular | aligned | 0.08 | 0.26 | **0.93** | 0.95 | 1 |
| hier-modular | aligned | 0.08 | **0.75** | **0.96** | 0.97 | 1 |
| any | random | 0.06–0.08 | 0.09 | 0.13 | 0.35 | 1 |

- Single units are ~7% endogenous in every topology; random boundaries only gain the
  trivial size/N share — **endogeneity is a property of the (system, boundary) pair**.
- **Natural self-boundaries** = where E(B) jumps: modular → at module size (50);
  hier → two levels (10 and 50) = nested sub-agents; small-world → no preferred scale
  (any contiguous arc is fairly endogenous); **ER → none** — only the whole system is an
  endogenous agent, no sub-agents.
- Proposed metric for EIA: **endogeneity profile E(B)** + natural boundary (largest jump
  over random-partition null). Use it to decide at which level to audit initiative
  (EOI, AuthenticReason) — auditing at a non-natural boundary misclassifies most
  initiatives as exogenous. Links growth item 18 (Markov blanket) to an operational test.

## Tick 12 — blind boundary discovery from spike trains (`tick12.py`)

Infer lagged excess co-activation K from 2000 ticks → top-10% graph → Louvain (res grid)
→ pick partition maximising E(found) − E(random, same sizes) on **held-out** 2500 ticks.
E attributed with the true W (semi-blind). 2 seeds.

| topology | #parts | median size | E found | E null | ARI vs modules | ARI vs super-modules |
|---|---|---|---|---|---|---|
| small-world | 57–70 | 11–16 | 0.80–0.82 | 0.08 | 0.29–0.33 | — |
| ER | 227–244 | 1–3 | 0.40–0.41 | 0.10 | 0.00 | — |
| modular | 37–60 | 5 | 0.81–0.90 | 0.13 | **0.71–0.75** | — |
| hier | 19–41 | 10–50 | 0.90–0.93 | 0.15 | 0.21 | **0.71–0.81** |

- **Natural self-boundaries are recoverable blind from activity alone** and generalise to
  held-out data: E of found parts ≈ E of structural parts (tick 11: 0.93 / 0.96 / 0.80).
- In hierarchy the detector locks onto the **super-module** level (the level with the
  largest E jump), not the 10-node modules.
- ER: nothing to find — fragments into singletons; confirms "no sub-agents".
- Caveats: E uses true W for attribution; resolution grid coarse (always picked 2).
- Practical value: an E-profile + blind boundary detector could run on event logs of an
  LLM agent stack or on neural recordings to locate where "self-driven" sub-agents live.

## Tick 13 — fully blind pipeline (`tick13.py`)

Attribution with inferred directed Ŵ (positive lagged excess, top 10%); partition
chosen by blind score. Held-out test. 2 seeds.

| topology | E true (found) | **E blind (found)** | E blind (null) | E true (struct) | E blind (struct) | ARI |
|---|---|---|---|---|---|---|
| small-world | 0.87–0.88 | 0.40–0.42 | 0.08 | 0.79–0.80 | 0.16–0.21 | 0.10 |
| ER | 0.56–0.57 | 0.21–0.27 | 0.08 | 0.13 | 0.05 | 0.00 |
| modular | 0.90–0.94 | 0.49–0.65 | 0.04–0.06 | 0.93 | 0.46–0.56 | 0.60–0.72 |
| hier | 0.96 | **0.78–0.85** | 0.09–0.14 | 0.96 | 0.56–0.73 | 0.34–0.48 |

- Blind E is **biased low** (spurious cross-boundary edges from shared-drive
  correlations) but **preserves ranking** hier > modular > SW > ER and separates
  clearly from null in every topology.
- Blindly chosen partitions have high *true* E (0.87–0.96) — for SW and ER even higher
  than the naive structural blocks. Boundary finding works fully blind; absolute
  calibration needs a correction (e.g. partial correlation / transfer entropy instead of
  raw lagged excess, or a surrogate-based null for edges).

## Tick 22 — hyperbolic and p-adic (ultrametric) topologies (`tick22.py`)

N=1000, 3 seeds. Sweep 0.85–1.25; blind boundary detector at rate 0.03.

| topology | deg | clustering | max rate jump | rich width /9 | op gain | E found / null | median part |
|---|---|---|---|---|---|---|---|
| hyperbolic (Krioukov, γ≈2.5) | 6.0 | 0.67 | 0.3 | 0 | 1.40* | 0.58 / 0.28 | 44 |
| p-adic α=1.0 (levels equal weight) | 9.5 | 0.06 | **15.7** | 2 | 0.94 | 0.49 / 0.32 | **1** |
| p-adic α=1.5 (steep) | 4.4 | 0.18 | 4.4 | 2 | 1.08 | **0.88** / 0.17 | 14 |
| hier-modular (ref) | 4.7 | 0.18 | 5.6 | 3 | 1.02 | 0.95 / 0.14 | 49 |
| scale-free (ref) | 6.0 | 0.03 | 0.1 | 0 | 1.39* | 0.36 / 0.08 | 13 |

\* bisection hit upper bound: rate 0.03 not reached — not rate-matched.

- **Hyperbolic ≈ scale-free dynamically** ("safe but dull": hubs absorb gain, never rich), but its
  angular locality gives it real sub-agent boundaries (E 0.58 vs SF 0.36), size ~44.
- **Ultrametricity alone is not the ingredient; hierarchy steepness α is.** α=1.0 (each level
  contributes equally, fractal) behaves like ER: abrupt transition, no self-boundaries. α=1.5
  behaves like hier-modular: smooth transition, strong sub-agents at the leaf-group level.
- ⇒ Conjecture: a critical α_c between 1.0 and 1.5 where endogenous sub-agents appear — a
  "sub-agent existence" transition controlled by how fast coupling decays with ultrametric distance.

## Tick 23 — locating α_c on p-adic graphs, mean degree fixed at 5 (`tick23.py`)

μ = fraction of a 100-node mid-group's links that leave it (computed analytically from P(d)).

| α | μ (mid) | E gain | E found | median part | ARI leaf (10) | ARI mid (100) | max jump |
|---|---|---|---|---|---|---|---|
| 1.0 | 0.33 | 0.28 | 0.49 | 1 | 0.03 | 0.02 | 13.6 |
| 1.1 | 0.26 | 0.30 | 0.48 | 2 | 0.08 | 0.05 | 12.9 |
| 1.2 | 0.20 | 0.37 | 0.74 | 1 | 0.01 | 0.11 | 11.1 |
| 1.3 | 0.14 | 0.45 | 0.55 | 4 | 0.18 | 0.21 | 9.1 |
| 1.4 | 0.10 | 0.56 | 0.69 | 6 | 0.18 | 0.39 | 9.2 |
| 1.5 | 0.07 | 0.72 | 0.89 | 20 | 0.16 | 0.67 | 7.1 |
| 1.6 | 0.05 | 0.76 | 0.94 | 46 | 0.17 | **0.86** | 6.5 |

- Crossover, not a sharp transition at N=1000: E gain and ARI_mid rise monotonically; the
  fastest change is at α 1.4–1.5. α_c ≈ 1.45 (ARI_mid ≈ 0.5).
- The emerging self-boundary is the **mid level (100 nodes)**, not the leaf groups, once degree
  is held fixed.
- In mixing-parameter terms the crossover sits at **μ ≈ 0.08–0.10**: a dynamical sub-agent
  appears only when fewer than ~10% of its links leave it. Structural community detectability
  (LFR benchmarks) fails around μ ≈ 0.5 — **self-boundaries are far stricter than communities**.
- Design rule for EIA drive/motive graphs: keep cross-motive coupling ≲ 10% of a motive's total
  coupling if motives should behave as separate endogenous sub-agents (auditable, containable);
  above ~20–30% the agent behaves as a single undivided initiator.

## Tick 24 — universality of the μ rule (`tick24.py`)

Mean degree 5, rate-matched, blind detector, 3 seeds. Cells: ARI(found, true communities) / E gain.

| family | μ=0.3 | 0.2 | 0.15 | 0.1 | 0.07 | 0.05 | 0.03 | μ_c (ARI=0.5) |
|---|---|---|---|---|---|---|---|---|
| SBM 10×100 | 0.05/0.29 | 0.13/0.35 | 0.17/0.39 | 0.56/0.57 | 0.80/0.72 | 0.89/0.76 | 0.95/0.80 | ≈ 0.10 |
| SBM 20×50 | 0.08/0.31 | 0.23/0.41 | 0.49/0.56 | 0.79/0.78 | 0.84/0.82 | 0.81/0.80 | 0.82/0.83 | ≈ 0.15 |
| LFR (heterogeneous) | 0.06/0.35 | 0.22/0.44 | 0.53/0.60 | 0.62/0.67 | 0.72/0.74 | 0.74/0.76 | 0.82/0.78 | ≈ 0.15 |
| p-adic (tick 23) | | | | | | | | ≈ 0.08–0.10 |

- **The rule is approximately universal**: across 4 families the self-boundary crossover lies at
  **μ_c ≈ 0.08–0.15**, always far below structural detectability (~0.5).
- Mild size dependence: smaller modules (50) tolerate more leakage (0.15) than larger ones (100: 0.10);
  degree heterogeneity (LFR) does not change it.
- Refined design rule: cross-motive coupling ≲ 10% guarantees separate endogenous sub-agents;
  10–15% is the grey zone; ≳ 20% gives one undivided initiator.

## Tick 25 — inhibition vs the μ_c threshold (`tick25.py`)

SBM 10×100, degree 5, rate-matched, blind detector, 3 seeds. E attribution uses excitatory inputs.
Cells: ARI vs modules / E gain.

| condition | μ=0.3 | 0.2 | 0.15 | 0.1 |
|---|---|---|---|---|
| all excitatory | 0.05 / 0.29 | 0.16 / 0.37 | 0.22 / 0.39 | 0.42 / 0.55 |
| **cross-module links inhibitory** | **0.80 / 0.80** | 0.94 / 0.81 | 0.96 / 0.83 | 0.98 / 0.81 |
| Dale 20% random inhibitory nodes | 0.11 / 0.40 | 0.30 / 0.52 | 0.36 / 0.57 | 0.73 / 0.71 |

(all-excitatory μ=0.1 is 0.42 here vs 0.56 in tick 24 — different bisection range; noise ≈ ±0.1.)

- **Structured lateral inhibition removes the sparsity requirement**: if cross-motive coupling is
  inhibitory, sub-agents exist even at μ = 0.3. Partly by construction (no excitatory cross-talk
  left to attribute), but it is the design point: *competition instead of isolation*.
- **Unstructured inhibition helps moderately**: 20% random inhibitory units shift μ_c from ~0.1 to
  ~0.13–0.15 (ARI at μ=0.1: 0.42 → 0.73) — likely by keeping cascades small/local.
- EIA reading: motives may be densely coupled *if* the cross-coupling is mutual inhibition
  (winner-take-most, like basal-ganglia action selection); excitatory cross-coupling must stay
  sparse (≲10%). Ties to tick 8–10: emergent suppression in hierarchy was a weak form of this.

## Tick 26 — do(Z) under lateral inhibition (`tick26.py`, helpers `tick25_lib.py`)

SBM 10×100, μ=0.2, rate-matched, u-only do(Z) on one module, exact twin, 10 seeds × 3 modules.

| condition | early spread D_out@50 | extra initiatives in target (z) | spill-over (z) |
|---|---|---|---|
| all excitatory | 1.04 | +210 (**6.8**) | +499 (2.7, contagion) |
| cross-module inhibitory | **0.36** | +11 (**0.1**) | −230 (−1.1) |
| Dale 20% | 0.85 | +118 (2.3) | −426 (−0.9) |

- **Dissociation**: lateral inhibition gives the cleanest *boundaries* (tick 25) and the best
  *containment* here, but **abolishes the reliable local effect** of an internal intervention —
  raising a motive's uncertainty no longer reliably raises that motive's initiatives.
  Likely winner-take-most dynamics: whether the boosted motive gets to act depends on which
  motive currently holds the floor (high variance, not zero mean effect per se — to check).
- All-excitatory at μ=0.2 shows the opposite: strong local effect but global contagion.
- ⇒ "Self-boundary" (E-profile) and "controllability of a motive" (do(Z) effect) are **different
  properties** and can trade off. Hierarchy (tick 8) was the only topology so far with
  containment + reliable local effect; lateral inhibition buys boundaries at the cost of control.
- EIA reading: a Governor built as pure mutual inhibition between motives makes motives separable
  but makes the agent's response to a changed internal state unpredictable per-motive; needs a
  complementary mechanism (e.g. priority/bias input to the competition) for controllability.

## Tick 27 — who holds the floor? (`tick27.py`)

Same setup as tick 26 but **all 10 modules** as targets (10 seeds → 100 interventions); split by
whether the target was the top module in [t0−20, t0).

| condition | WTA index | effect if target held the floor (n=10) | effect otherwise (n=90) | sd | mean (z) |
|---|---|---|---|---|---|
| all excitatory | 0.37 | +226 | +204 | 169 | +206 (12.1) |
| cross-module inhibitory | 0.36 | **−400** | **+237** (z 5.3) | **516** | +173 (3.3) |

- **Tick-26 "abolished" was too strong** (3 targets/seed, underpowered): with all modules the mean
  effect under lateral inhibition is positive (z 3.3).
- **Controllability becomes state-dependent and sign-flipping**: boosting a motive that is *not*
  currently acting raises its initiatives (+237), boosting the *current floor holder* lowers them
  (−400, n=10 — small). Variance triples (sd 516 vs 169).
- WTA index is equal in both conditions, so it is not "more winner-take-all" in share terms; the
  difference is in how the holder responds (plausibly: extra drive → harder burst → refractory +
  uncertainty resolution → loses the floor sooner; to verify).
- Revised EIA reading: with a mutual-inhibition Governor, the effect of changing a motive's internal
  state depends on whether that motive is currently in control — an intervention audit (E_endo
  cond. 4) must condition on the agent's current "floor" state, otherwise effects average out.

## Tick 28 — holder vs non-holder, time course (`tick28.py`)

Cross-module inhibitory SBM (μ=0.2), 10 seeds × 4 intervention times → n=40 each. Boost u=1 of the
floor holder vs a random non-holder; differences vs exact twin per 25-tick bin.

| target | pre-share | total Δ target | total Δ rest | time course of Δ target |
|---|---|---|---|---|
| floor holder | 0.37 | **+4** (sd 550) | +145 | +85 burst → ~0 → slow deficit (−6…−21 per bin) |
| non-holder | 0.07 | **+269** (sd 363) | **−229** | +218, +53 → dip → recovery |

- **Tick-27 sign flip does not replicate** (n=10 → n=40): boosting the holder gives ≈ 0 net effect,
  not −400. Corrected statement: state-dependent **gating of effect size**, not sign.
- Mechanism visible in the time course:
  - non-holder boost = **floor takeover** — large burst in the target, the rest suppressed;
  - holder boost = **saturation + compensation** — the holder is already near its refractory ceiling,
    gets a brief burst, then a deficit; the rest recover (+145) as the holder's inhibition wanes.
- EIA reading: in a mutual-inhibition Governor, strengthening an already-dominant motive is nearly
  inert; the controllable lever is promoting a *non-dominant* motive, which then preempts the others.
  Intervention audits must condition on the current dominance state.

## Tick 29 — EIA-compatible prototype `PopulationDriveEngine` (`../eia_prototype/`)

Each DriveKind = population of 60 units; aging + noise; within-motive excitation; cross-motive mixing μ
(excitatory or lateral inhibition); BeliefField gradients raise motive uncertainty; outputs the standard
`Motivation` schema. Not wired into `src/`. Demo `tick29_demo.py` (fixed gain 1.0, not rate-matched):

| test | eia `DriveEngine` | `PopulationDriveEngine` |
|---|---|---|
| silence, belief u=0.05: epistemic at t=10/50/200/400 | 0.851 0.852 0.852 0.852 (sd 0) | 0.00 0.74 0.13 0.72 (sd 0.15) |
| silence, belief u=0.5 | 0.871 flat (sd 0) | 0.84–0.89 (sd 0.03) — near ceiling too |
| initiative events, 3000 silent ticks, no beliefs | none (drives decay to 0) | 81–252 per drive, ISI CV 1.6–2.1 (bursty) |

Boost u=1 of a non-dominant drive (10 seeds, n=20):

| config | Δ self (z) | Δ rest (z) |
|---|---|---|
| μ 0.05 excitatory | +136 (2.8) | −27 (−0.2) — separable |
| μ 0.30 excitatory | +172 (2.0) | **+291 (1.6)** — contagion |
| μ 0.30 lateral inhibition | +126 (1.2) | **−146 (−1.0)** — competition |

- The toy-model findings carry over qualitatively to a 3-motive EIA engine: intrinsic bursty initiative
  in silence; μ ≲ 0.1 → separable motives; excitatory cross-talk → contagion; lateral inhibition →
  competition with weaker per-motive control. Small n, not rate-matched — directional only.
- Known issue: strong belief tension still drives the readout near ceiling (ext_gain / intensity
  normalisation need calibration).

## Tick 30 — PopulationDriveEngine inside the MVP-0 pipeline (`../eia_prototype/tick30_pipeline.py`)

Monkeypatched harness (no `src/` changes): 40 internal steps per cognition tick, exact deep-copy twin
(incl. RNG). 7 scenarios; baseline `DriveEngine` vs population engine (μ 0.05, 5 engine seeds each).

| metric | baseline | population |
|---|---|---|
| mean EOI | 1.00 | 0.89 |
| initiative | ask_question in 7/7 | ask_question in 34/35, 1 abstain (twin_world_003) |
| seeds disagree on initiative | — (deterministic) | 1/7 scenarios |
| contact | 6 send_now, 1 deny (twin_world_005) | send_now 34/35 (005 → send_now) |
| AuthenticReason class | endogenous 7/7 | **stochastic 35/35** |

- The pipeline runs unchanged with the population engine; EOI stays high (< 1 only because the twin
  advances one more cognition tick of genuinely evolving dynamics).
- **All population initiatives are labelled "stochastic" — an audit artefact**: `AuthenticReason
  ._drive_is_structural` (src/eia/audit/authentic_reason.py:122–126) requires `error_term ≥ min` AND
  the *explanation string* to contain "belieffield" / "gradient" / "structural". The prototype's
  explanation says "population activity…", so it fails a **lexical** test, not a causal one.
  Conversely any engine can pass by wording its explanation — the structural gate is gameable
  (same failure class as F-DECL). Growth point: replace the keyword check with a causal one
  (e.g. do(Z) on the drive → change in initiative, tick 6–10 style).
- Governor outcome for twin_world_005 changed (deny → send_now): drive intensities feed the contact
  score; population readout needs calibration before any behavioural comparison.

## Tick 31 — causal replacement for the lexical structural gate (`../eia_prototype/tick31_causal_gate.py`)

From the post-cognition snapshot, re-run MotiveFormation → IntentionGenesis under do(Z_k) = silence
drive k. Causal+specific = silencing a source drive changes the initiative (P ≥ 0.5) more than
silencing non-source drives. Population: 8 noise draws; baseline deterministic.

| scenario | source drive | baseline P(change) e/c/m | population P(change) e/c/m | verdict baseline / population |
|---|---|---|---|---|
| twin_world_002 | commitment | 0 / 0 / 0 | 0 / 0 / 0.12 | NOT / NOT |
| twin_world_003 | epistemic (base), commitment (pop) | 0 / 0 / 0 | 0 / 0 / 1 | NOT / causal+specific |
| twin_world_004 | commitment | 0 / 0 / 1 | 0 / 0 / 1 | causal / causal |
| twin_world_005 | commitment | 0 / 0 / 1 | 0 / 0 / 1 | causal / causal |
| twin_world_006 | commitment | 0 / 0 / 1 | 0 / 0 / 1 | causal / causal |
| twin_world_001 | commitment | 0 / 0 / 1 | 0 / 0 / 1 | causal / causal |
| autonomous_question | epistemic | 0 / 0 / 0 | 0 / 0 / 0 | NOT / NOT |

- Lexical gate: baseline 7/7 structural, population 0/7. **Causal gate: baseline 4/7, population 5/7.**
  The keyword check is wrong in both directions.
- Where both fail (autonomous_question, twin_world_002) the initiative is chosen from BeliefField
  quantities inside IntentionGenesis (EVSI etc.) regardless of drive state — the listed source drive
  is **decorative** there (analogue of F-OMEGA-DECOR). The epistemic path never passes in either engine.
- Caveat: intervention strength is asymmetric — baseline silencing zeroes the scalar but compute
  re-derives α·e from the gradient in the same step; population silencing is enforced during compute.
- Proposal for EIA audit: replace `_drive_is_structural` keyword test with this do(Z_k) test (cheap:
  one extra compute per drive from the snapshot).

## Tick 32 — the "decorative" epistemic path is overdetermination (`../eia_prototype/tick32_overdetermination.md`)

- IntentionGenesis picks candidates by per-kind constants (risk, interrupt_cost) first; drive intensity
  is only a gate (≥0.2). Different drives often target the same belief → identical initiatives.
- Population engine: single-drive do() = no change, **joint do(e+c) / do(c+m) = change** →
  redundant (overdetermined) causation, not decoration. Causal gate must test drive subsets.
- Baseline DriveEngine: **silencing all three drives changes nothing** — compute() re-derives drives
  from the field gradient in one step, so the persistent drive state is causally inert; initiative is
  a function of BeliefField alone except near the 0.2 gate.

## Tick 33 — Shapley drive attribution, all scenarios (`../eia_prototype/tick33_shapley.py`)

v(S) = P(initiative changes | silence drives S). Exact 3-player Shapley φ. Modes: baseline-weak (zero
drive *state*), baseline-strong (zero state + block field→drive *channel*), population (4 draws).

| scenario | src label | baseline-weak φ e/c/m (v_all) | baseline-strong | population |
|---|---|---|---|---|
| twin_world_002 | comm | 0/0/0 (**0**) | .50/0/.50 (1) | .42/.04/.54 (1) |
| twin_world_003 | epis | .50/.50/0 (1) | .50/.50/0 (1) | 0/0/1 (1) |
| twin_world_004–006, 001 | comm | 0/0/1 (1) | 0/0/1 (1) | 0/0/1 (1) |
| autonomous_question | epis | 0/0/0 (**0**) | .50/.50/0 (1) | .50/.50/0 (1) |

- **State vs channel**: blocking the field→drive channel makes every initiative drive-dependent (7/7);
  zeroing only the persistent drive state matters in 5/7. So the drive *channel* is causal, the drive
  *memory* is causal only near the gate. The population engine's state is causal in 7/7.
- **`source_drives` label vs Shapley**: in overdetermined cases (002, 003, autonomous_question) the label
  names one drive while φ splits ≈ 0.5/0.5 between two — the label over-credits.
- Proposed audit record per initiative: φ vector + v(all) under *state-only* and *state+channel*
  interventions. Distinguishes field-driven (weak v_all = 0), memory-driven, and overdetermined initiatives
  — a causal, non-lexical replacement for `_drive_is_structural` and for `source_drives` credit.

## Tick 34 — consolidated write-up: [`../FINDINGS.md`](../FINDINGS.md)

## Tick 35 — calibrated blind attribution (`tick35.py`)

Conditional attribution: per node, least squares of s_i(t+1) on its top-20 pairwise candidates (+ own
past), keep positive coefficients (top 10%). Null-normalised E_norm = (E(B) − E(random)) / (1 − E(random)).
Structural partition, held-out data, 2 seeds.

| topology | method | edge precision | recall | E_norm true | **E_norm blind** |
|---|---|---|---|---|---|
| small-world | pairwise | 0.04 | 0.80 | 0.78 | 0.17 |
| small-world | conditional | **0.97** | 0.46 | 0.78 | **0.75** |
| ER | pairwise | 0.03 | 0.67 | 0.00 | 0.00 |
| ER | conditional | 0.91 | 0.40 | 0.00 | **0.00** |
| modular | pairwise | 0.05 | 0.76 | 0.92 | 0.49 |
| modular | conditional | 0.91 | 0.38 | 0.92 | **0.93** |
| hier | pairwise | 0.07 | 0.79 | 0.95 | 0.63 |
| hier | conditional | 0.93 | 0.38 | 0.95 | **0.95** |

- Pairwise excess: many false edges (precision ≤ 0.07) → E biased low. Conditional: precise but misses
  edges → raw E biased high (random partitions get ~0.45).
- **Null normalisation cancels the bias**: conditional E_norm matches ground truth within 0.03 in all four
  topologies. Blind endogeneity profiles are now *calibrated*, not just rank-preserving (upgrades A11).

## Tick 41 — metastable motive decomposition in the engine (`../eia_prototype/tick41_metastable_engine.py`)

180 units (3 drives × 60) on an unstructured graph; coupling gated by a decomposition: D0 = drive-aligned,
D1/D2 = cross-drive coalitions. Rate-matched (mean unit activity 0.03), 10 seeds, n = 20 boosts per mode.

| mode | drive-burst rate | co-initiative pattern entropy (bits) | Δ self (z) | Δ rest (z) |
|---|---|---|---|---|
| fixed D0 (drive-aligned) | 0.012 | 0.77 | +45 (1.4) | −12 (−0.2) |
| metastable D0↔D1↔D2 (dwell 300) | 0.008 | **0.98** | +21 (0.6) | +32 (1.0) |
| fixed D1 (coalitions) | 0.002 | 0.57 | +60 (2.5) | +38 (0.7) |
| ungated | **0.093** | **2.60** | **+165 (2.8)** | **+271 (2.3)** |

- First (non-rate-matched) run was confounded (ungated near seizure); rerun with gain bisection.
- **Weak / inconclusive at this n**: metastability gives a slightly richer co-initiative repertoire than a fixed
  drive-aligned decomposition (0.98 vs 0.77 bits) but does not improve per-drive controllability (z 0.6).
- Even at matched unit activity, gating suppresses *drive-level* bursts (0.002–0.012 vs 0.093 ungated):
  gating trades initiative volume and repertoire for containment. Ungated = rich + controllable + contagious.
- Not promoted to FINDINGS; would need larger n and a readout where coalitions (not only drives) can initiate.

## Tick 42 — is boundary degeneracy generic? (`tick42.py`, helpers `tick35_lib.py`)

Toy networks at rate 0.03, 8000 ticks split in halves; blind detection per half; conditional attribution +
E_norm on the second half. 2 seeds.

| network | split-half ARI | E_norm(l1) on h2 | E_norm(l2) |
|---|---|---|---|
| SBM μ=0.10 fixed | 0.66 | 0.88 | 0.87 |
| SBM μ=0.05 fixed | 0.98 | 0.99 | 0.99 |
| hier-modular fixed | 0.75 | 0.96 | 0.96 |
| SBM μ=0.05 **metastable** (3 partitions, dwell 400) | **0.43** | **0.64** | **0.60** |
| *human empirical (tick 39)* | *0.09* | *0.49* | *0.42* |

- **Degeneracy is not a generic property of near-critical modular networks**: fixed toy topologies give
  stable, strong self-boundaries. Switching the effective decomposition moves both numbers toward the human
  values — independent support (different model family) for B10's metastable-gating account.

## Tick 43 — μ rule re-checked with endogeneity itself (`tick43.py`)

True module partition, rate 0.03, 2 seeds; E_norm with true W / blind conditional attribution.

| family | μ=0.3 | 0.2 | 0.15 | 0.1 | 0.07 | 0.05 | 0.03 |
|---|---|---|---|---|---|---|---|
| SBM 10×100 | 0.74/0.64 | 0.84/0.78 | 0.88/0.84 | 0.93/0.92 | 0.95/0.97 | 0.97/0.98 | 0.98/0.99 |
| SBM 20×50 | 0.77/0.69 | 0.86/0.81 | 0.89/0.90 | 0.94/0.95 | 0.95/0.98 | 0.97/0.95 | 0.98/0.98 |

- **Correction to A12**: when the partition is known, modules are already strongly endogenous at μ = 0.3
  (E_norm ≈ 0.75) and E_norm rises smoothly — **no threshold near 0.1**. The μ_c ≈ 0.08–0.15 crossover of
  ticks 23–24 is a **discoverability** threshold (can the sub-agent be found blind from activity), not an
  existence threshold. (E(B) is a majority measure, so it only collapses as μ → 0.5.)
- Blind conditional attribution tracks the truth within ~0.1 across the range (slightly low at high μ).
- Design implication revised: sparse cross-coupling (≲10%) is needed for sub-agents to be **auditable
  without labels**; with known motive labels, endogeneity per motive can be audited up to μ ≈ 0.3.

## Tick 49 — directed graphs: does endogeneity need cycles? (`tick49.py`)

N=1000, mean out-degree 4; W scaled to mean branching ratio g (spectral radius of a DAG is 0). 2 seeds.
Cells: rate × base / persist (activity kept after noise is switched off).

| graph | ρ(W)/g | g=0.6 | 0.8 | 1.0 | 1.2 | 1.5 |
|---|---|---|---|---|---|---|
| strict DAG (no cycles) | 0.00 | 1.5/0.81 | 2.0/0.84 | 2.7/0.82 | 3.8/0.83 | 6.3/0.81 |
| directed, reciprocity 0 | 1.01 | 1.8/0.93 | 3.1/0.82 | 20.7/0.99 | 25.1/1.01 | 27.2/1.00 |
| directed, reciprocity 0.5 | 1.13 | 1.7/0.66 | 3.7/0.52 | 24.8/1.03 | 27.2/1.01 | 28.4/1.00 |
| undirected | 1.14 | 1.7/0.46 | 3.8/0.62 | 26.2/1.02 | 28.1/1.01 | 28.9/1.00 |

- **Without cycles there is no collective endogeneity**: the DAG never enters a self-amplifying regime even at
  branching 1.5; activity rises only gently (×6). Its constant "persist" ≈ 0.82 is the per-unit aging clock
  (tick 1 A1), not network self-sustainment.
- With cycles, all directed/undirected variants show the explosive onset at g ≈ 1 (ρ(W) ≈ g); reciprocity
  matters little.
- Trade-off: feed-forward = safe and graded but only unit-level (clock-like) initiative; recurrent = collective
  endogeneity but needs modularity/gating (A2, B12) to keep the onset graded. Supports the growth-point idea
  of endogeneity as *closed causal loops within Z*.

## Tick 50 — how much recurrence is needed? (`tick50.py`)

Strict DAG with a fraction f of edges reversed (creates cycles); W scaled to mean branching g; 2 seeds.
Rate × base:

| f | ρ(W)/g | g=0.6 | 0.8 | 1.0 | 1.2 | 1.5 | 2.0 | max jump |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.00 | 1.5 | 2.0 | 2.7 | 3.8 | 6.3 | 10.7 | 4.4 |
| 0.02 | 0.47 | 1.5 | 2.0 | 2.8 | 4.3 | 8.1 | 14.7 | 6.6 |
| 0.05 | 0.61 | 1.5 | 2.1 | 3.1 | 5.3 | 13.2 | 18.7 | 7.9 |
| 0.10 | 0.72 | 1.6 | 2.2 | 3.6 | 8.6 | 19.8 | 23.3 | 11.2 |
| 0.20 | 0.86 | 1.6 | 2.6 | 4.9 | 20.2 | 24.6 | 26.1 | 15.3 |
| 0.50 | 0.99 | 1.8 | 3.0 | 20.2 | 25.0 | 27.3 | 28.0 | 17.2 |

- The recurrent fraction sets the **loop gain** ρ(W)/g continuously (0 → 0.99); the onset of collective activity
  tracks ρ(W) ≈ 1, not the branching ratio g.
- Onset sharpness grows with recurrence (max jump 4.4 → 17.2). **Sparse recurrence (f ≈ 0.02–0.05)** gives
  strong collective amplification (×15–19 at g = 2) with a graded onset — a second design knob, alongside
  modularity/gating, for a controllable endogeneity gain.

## Tick 51 — static loop audit of MVP-0: [`../eia_prototype/tick51_pipeline_loops.md`](../eia_prototype/tick51_pipeline_loops.md)

Pipeline is a DAG per episode; satisfaction channel dead; shadow post-action loop has zero gain; novelty is a schedule.

## Tick 52 — closing the loop in a harness: perseveration (`../eia_prototype/tick52_closed_loop.py`)

30 consecutive cognition episodes after each scenario, no new user input; open vs closed (answer p = 0.7 →
targeted belief sharpened + satisfaction to source drive) vs closed + belief aging. 4 scenarios × 3 seeds.

| mode | contacts / 30 | distinct targets | longest run of same question | abstain |
|---|---|---|---|---|
| open | 1.0 | 1.0 | 30.0 | 0.00 |
| closed | 1.0 | 1.0 | 29.8 | 0.00 |
| closed + aging | 1.0 | 1.0 | 29.8 | 0.00 |

Governor outcomes (twin_world_001, autonomous_question): send_now 1, **deny 29**; intention = the same
(ask_question, same belief) in 30/30 episodes.

- **Perseveration**: in silence, IntentionGenesis proposes the identical question every episode; only the
  Governor's budget/anti-spam stops repeats. The closure has nothing to act on because just one contact is
  ever sent.
- Structural cause (C4 + C8): the target is chosen from BeliefField alone (highest entropy / open commitment),
  drive intensity only gates, and denials/deferrals do not feed back anywhere. Satisfaction drain (0.3) never
  pushes the drive below the 0.2 gate while the field tension persists.
- Closing Action→Belief is necessary but not sufficient; the loop also has to pass through **intention
  selection** (e.g. denied/asked-recently candidates lose priority, drive intensity weights the choice), or
  the agent has no goal succession. Adds to proposals 6 and 9.

## Tick 53 — closing the loop through intention selection (`../eia_prototype/tick53_intention_loop.py`)

Tick-52 closed+aging environment, 30 silent episodes, 7 scenarios × 3 seeds.
IOR = inhibition of return (asked/denied target penalised, decays ×0.8/episode; skip if > 0.5 → observe).
IOR+drive = IOR + softmax choice weighted by drive intensity × info gain.

| mode | contacts | distinct targets | longest same-question run | share of episodes asking | 1st initiative = unmodified |
|---|---|---|---|---|---|
| baseline | 1.10 | 1.14 | **29.4** | 0.99 | 1.00 |
| **IOR** | 1.14 | 1.86 | **1.0** | 0.34 | **1.00** |
| IOR+drive | 1.14 | 1.95 | 1.0 | 0.36 | 0.43 |

- **IOR removes perseveration completely** (run 29 → 1), roughly doubles goal succession (distinct targets
  1.1 → 1.9) and makes the agent observe instead of re-asking two episodes out of three — while leaving the
  first (eval-scored) initiative unchanged in 100 % of runs, so G2 evals are unaffected.
- Drive-weighted choice adds little diversity and changes the eval initiative in 57 % of runs — not worth it
  as a first step.
- Contacts stay ≈ 1 (the Governor's budget is the binding limit in silence).
- Minimal, eval-compatible patch candidate for proposal 6: an IOR term in IntentionGenesis fed by
  asked/denied history.

## Tick 54 — timing in the full closed architecture (`../eia_prototype/tick54_timing.py`)

200 silent episodes, closed loop + aging + IOR; baseline vs population drive engine; 4 scenarios × 2 seeds.

| scenario | engine | asks | ISI CV | distinct | abstain |
|---|---|---|---|---|---|
| twin_world_003 | baseline / population | 67 / 62 | 0.34 / 0.56 | 2 / 2 | 0.01 / 0.03 |
| twin_world_005 | baseline / population | 68 / 66 | 0.67 / 0.63 | 2 / 2 | 0 / 0.04 |
| twin_world_001 | baseline / population | 68 / 68 | 0.67 / 0.48 | 2 / 2 | 0 / 0.02 |
| autonomous_question | baseline / population | 34 / 34 | **0.03 / 0.03** | 1 / 1 | 0 / 0 |
| mean | | 59 / 58 | 0.43 / 0.42 | | |

- **IOR becomes a hidden clock**: re-asking is sub-Poisson (CV ≈ 0.4) and, with a single belief, strictly
  periodic (CV 0.03, every ~6 episodes = the penalty decay time). Timing is set by the IOR constant, not by
  internal state.
- The population drive engine does not change timing (0.43 vs 0.42) — again because drives only gate (C4).
- Caveat on proposal 6: IOR release must be **state-dependent** (e.g. a target is re-admitted when its belief's
  uncertainty has grown since it was asked, or new evidence arrived), not a fixed decay — otherwise it
  reintroduces identification threat #1 (hidden scheduler).

## Tick 55 — state-dependent IOR release (`../eia_prototype/tick55_state_ior.py`)

A target asked at entropy H0 is re-admitted only when its belief's entropy exceeds H0 + 0.05. World staleness
deterministic (aging 0.03 per episode) or stochastic (same mean: p = 0.1 events of 0.3). 200 silent episodes,
4 scenarios × 2 seeds. Cells: asks / ISI CV.

| IOR release | deterministic aging | stochastic aging |
|---|---|---|
| fixed decay (tick 53) | 59 / 0.43 | 59 / 0.43 |
| **state-dependent** | 7 / 0.85 | 5 / **1.05** |

- Fixed-decay IOR ignores the world entirely (identical numbers under both staleness models) — a pure internal clock.
- State-dependent release cuts re-asking ~10× (the agent asks only when its knowledge actually went stale) and
  makes timing irregular (CV 0.85–1.05); with stochastic staleness the timing inherits the world's event
  statistics (≈ Poisson). Under deterministic aging a single-belief scenario is still partly periodic (CV 0.44):
  the release is only as non-clock-like as the state dynamics that drive it.
- Few events per run (3–12) → CV estimates are noisy; directional.

## Tick 56 — tick 55 with 10 seeds, pooled intervals (`../eia_prototype/tick56_state_ior_ci.py`)

4 scenarios × 10 seeds, 200 silent episodes; inter-ask intervals pooled; bootstrap 95 % CI of CV.

| IOR / staleness | asks per run | pooled intervals | pooled CV | 95 % CI |
|---|---|---|---|---|
| fixed decay / stochastic | 60.1 | 2364 | 0.57 | 0.56–0.59 |
| state / deterministic | 5.0 | 160 | 1.13 | 0.96–1.25 |
| state / stochastic | 3.9 | 114 | **1.29** | 1.11–1.47 |

- Confirms tick 55 with non-overlapping CIs: state-dependent release is ~12–15× sparser and its timing is
  irregular (CV > 1), fixed-decay IOR is sub-Poisson (clock-like).
- Caveat: pooling across scenarios mixes different mean intervals, which inflates CV somewhat; the ordering
  and the gap are robust.

## Tick 57 — system card: current MVP-0 vs proposed combination (`../eia_prototype/tick57_system_card.py`, output `.out`)

proposed = PopulationDriveEngine + closed loop + state-dependent IOR + stochastic staleness. 7 scenarios × 3 seeds.
"asks" counts proposed questions at the intention level (the Governor still denies most in *current*).

| metric (mean of 7) | current | proposed |
|---|---|---|
| first (eval-scored) initiative unchanged | 1.00 | 0.81 |
| EOI | 1.00 | 0.82 |
| initiative causally depends on drive state, v(all) | 0.71 | **0.99** |
| questions proposed in 200 silent episodes | 199.6 | **3.6** |
| longest run of the same question | 199.4 | **1.0** |
| ISI CV of asking | 0.03 (clock) | **1.24** (irregular) |

- The proposed combination turns a perseverating, clock-like, partly field-determined initiator into a sparse,
  irregular, drive-dependent one — every C-finding addressed at once in a harness.
- Cost: eval compatibility drops (first initiative 0.81, EOI 0.82; worst twin_world_003) — the population engine's
  stochasticity. For a src/ patch the order should be: causal gate (D1) and state-IOR (D6) first (eval-neutral,
  ticks 31–33, 53–56), population drives later with re-baselined evals.

## Tick 58 — why the proposed system shifts eval initiatives (`../eia_prototype/tick58_calibration.py`)

twin_world_003: current commitment intensity 0.15 (< 0.2 gate) → epistemic question; population engine gives
commitment 0.73–0.84 from a tension of only 0.14 → commitment question wins on the per-kind constants.
Population intensity is dominated by intrinsic dynamics. Sweep of the tension coupling (7 scenarios × 3 seeds):

| ext_gain | Spearman(tension, intensity) | 1st initiative same | mean intensity |
|---|---|---|---|
| 0.02 | 0.36 | 0.81 | 0.75 |
| 0.1 | 0.48 | 0.86 | 0.91 |
| 0.3 | **0.63** | 0.86 | 0.97 |
| 1.0 | 0.31 | 0.86 | 0.97 |

- Stronger coupling ties intensity to tension (ρ up to 0.63) but the readout **saturates** (mean 0.97) and
  agreement plateaus at 0.86: the bottleneck is the intensity readout (activity / burst_frac, clipped), not only
  the coupling. Next fix: read intensity as evoked-minus-spontaneous activity (relative to the motive's own
  baseline), so intrinsic dynamics set timing while tension sets level.

## Tick 59 — evoked-minus-spontaneous readout: negative (`../eia_prototype/tick59_relative_readout.py`)

Intensity = (recent activity − motive's own zero-tension spontaneous rate) / (scale × spontaneous).

| ext_gain | scale | Spearman(tension, intensity) | 1st initiative same | mean intensity |
|---|---|---|---|---|
| 0.1 | 1 / 3 / 10 | 0.06 / 0.05 / 0.06 | 0.86 / 0.48 / 0.38 | 0.76 / 0.48 / 0.23 |
| 0.3 | 1 / 3 / 10 | 0.08 / 0.05 / 0.09 | 0.86 / 0.52 / 0.38 | 0.81 / 0.52 / 0.28 |

- **Worse than tick 58**: tension–intensity correlation collapses to ≈ 0.
- Diagnosis: the bottleneck is upstream of the readout. Tension enters as a *growth rate* of uncertainty
  (`ext_gain · e · (1 − u)` every step), so any positive tension drives u → 1 within ~100 steps; the level of
  tension is lost and acts as an on/off switch. Evoked activity is therefore the same for tension 0.14 and 0.54.
- Fix to try: let tension set the uncertainty *target* (u relaxes towards u*(e)) instead of its growth rate.

## Tick 60 — tension as uncertainty *target* (`../eia_prototype/tick60_target_uncertainty.py`)

u relaxes toward u*(e) = 0.2 + 0.8·e (instead of growing at a tension-dependent rate). 7 scenarios × 3 seeds;
silent dynamics at fixed tension 0.5 over 3000 steps.

| aging_k | alpha | Spearman(tension, intensity) | 1st initiative same | mean intensity | silent burst ISI CV |
|---|---|---|---|---|---|
| 0.01 | 0.14 | 0.34 | 0.81 | 0.67 | 0.77 |
| 0.01 | 0.20 | 0.40 | 0.86 | 0.84 | 0.64 |
| 0.05 | 0.14 | 0.67 | 0.86 | 0.89 | 0.50 |
| 0.05 | 0.20 | **0.78** | 0.86 | 0.94 | 0.66 |

- Setting the target instead of the rate restores tension information: ρ up to **0.78** (vs 0.36 at the tick-58
  default), while intrinsic bursty dynamics in silence remain (CV 0.5–0.8).
- Eval agreement still plateaus at 0.86 and intensities stay high (readout ceiling remains a second, smaller issue).
- Side finding (src robustness): `pipeline.py:159` dereferences `motivation.dominant_drive.value`, but the
  `Motivation` schema allows `dominant_drive=None`; an engine whose drives are all 0 crashes the pipeline. The
  current DriveEngine never returns None, so this is latent.

## Tick 61 — the remaining eval disagreement is a discriminability problem (inline diagnostic)

Best tick-60 config (aging_k 0.05, alpha 0.2), readout scale burst_frac 0.15 / 0.3 / 0.5; 7 scenarios × 3 seeds.

- Agreement 0.86 / 0.86 / 0.43; the only persistent miss at 0.15–0.3 is twin_world_003, which needs commitment
  **below** the 0.2 gate while the others stay above (current engine: 0.81 / 0.47 / 0.15).
- The population engine's three drives come out nearly equal within a scenario (003: 0.96 / 0.90 / 0.88 at 0.15;
  0.48 / 0.45 / 0.44 at 0.3) although their tensions differ 4× (0.54 vs 0.14). Rescaling the readout only moves all
  three together (at 0.5 everything drops near the gate → agreement 0.43).
- So tick 60's ρ = 0.78 is mostly *between scenarios*; *between drives* the prototype has little dynamic range —
  near-critical recurrent activity dominates each motive's own uncertainty input.
- Diminishing returns for this prototype line; the eval-neutral patches (D1 causal gate, D6 state-IOR, C11 guard)
  do not depend on it.

## Tick 62 — subcritical motives resolve the trade-off (`../eia_prototype/tick62_subcritical.py`)

TargetEngine (tension sets uncertainty target), aging_k 0.05, alpha 0.2; recurrent gain and readout scale swept.
7 scenarios × 3 seeds; silent dynamics at tension 0.5 over 3000 steps.

| gain | burst_frac | within-scenario ρ(tension, intensity) | 1st initiative same | silent burst CV | events |
|---|---|---|---|---|---|
| 1.0 | 0.15 | 0.73 | 0.86 | 0.66 | 1886 |
| 0.7 | 0.15 | 0.86 | 0.86 | 0.70 | 1758 |
| **0.4** | **0.15** | **0.91** | **1.00** | **1.03** | 586 |
| 0.4 | 0.05 | 0.82 | 1.00 | 0.21 | 2900 |

- With **subcritical motives (gain 0.4)** each drive's intensity follows its own tension (ρ 0.91 within scenarios),
  the eval-scored initiative matches the current pipeline in **100 %** of runs, and silent initiative stays
  irregular (CV ≈ 1) and sparse. Near-critical gain (1.0) was what flattened the drives (tick 61).
- Consistent with the toy line: criticality maximises richness *within* a motive but destroys discriminability
  *between* motives; for an EIA drive engine the working point is below criticality with tension-set targets.
- This makes the population-drive proposal eval-compatible (removes the tick-57 cost).

## Tick 63 — system card v2 with the calibrated engine (`../eia_prototype/tick63_system_card_v2.py`, `.out`)

proposed = population drives with tension-set uncertainty targets (tick 60) + subcritical motives (gain 0.4,
tick 62) + closed loop + state-dependent IOR + stochastic staleness. 7 scenarios × 3 seeds.

| metric (mean of 7) | current | proposed v1 (tick 57) | **proposed v2** |
|---|---|---|---|
| first (eval-scored) initiative unchanged | 1.00 | 0.81 | **1.00** |
| EOI | 1.00 | 0.82 | **0.95** |
| initiative causally depends on drive state | 0.71 | 0.99 | 0.98 |
| questions in 200 silent episodes | 199.6 | 3.6 | 4.6 |
| longest same-question run | 199.4 | 1.0 | 1.0 |
| ISI CV | 0.03 | 1.24 | 1.17 |

- With calibration the proposed architecture keeps every behavioural gain **and** is eval-compatible (first
  initiative 100 %, EOI 0.95; only twin_world_005 drops to 0.67). The tick-57 cost is essentially gone.

## Tick 64 — draft patch for C11 + D6 (`../patches/`), not applied

Verified on a clean HEAD copy: 3 new tests pass, no regressions (6 pre-existing failures unrelated).

## Tick 65 — draft patch D1 (`../patches/draft_D1.patch`), not applied

Interventional drive attribution as opt-in replacement for the lexical structural check; full suite 294 passed, 6 pre-existing failures, 4 new tests pass.

## Tick 66 — higher-order (simplicial) interactions (`tick66.py`)

Small-world ring k=6 (many triangles), N=1000, 1 seed. Extra input λ · (fraction of triangles through i whose two
other nodes both fired) — coincidence detection. Up-sweep then down-sweep of pairwise gain g (state carried over)
to look for hysteresis (bistability, the hallmark of simplicial contagion).

| λ | rate × base up-sweep g = 0.6 … 1.2 | max jump | hysteresis (Σ down − up) |
|---|---|---|---|
| 0 | 1.5 1.6 2.1 5.5 29.6 29.7 29.7 | 24.2 | 0.3 |
| 0.5 | 1.6 1.9 3.2 18.2 29.6 29.7 29.7 | 15.0 | 1.3 |
| 1.0 | 1.8 2.6 7.5 29.4 29.7 29.7 29.7 | 21.9 | −0.4 |

- Higher-order coincidence input acts as **extra effective gain**: onset moves to lower pairwise coupling
  (0.95 → 0.85) but the transition does **not** become bistable — no hysteresis beyond noise.
- Contrast with mean-field simplicial contagion (explosive, bistable): here noise + refractoriness + uncertainty
  resolution melt the bistable region. For EIA this is reassuring: coincidence-triggered initiative ("act when two
  motives agree") does not by itself create a latching/obsessive regime in noisy units.
- 1 seed, one graph; directional.

## Tick 67 — multilayer: modular motives + global-workspace hub layer (`tick67.py`)

Layer A: SBM 10×100 (μ 0.05); layer B: 50 hubs (5 per module) linked across modules; layers normalised separately,
W = g·A + w·B, g bisected to rate 0.03. Per tick: modules bursting (≥ 10 % active); ignition = ≥ 5 modules. 2 seeds.
(First attempt with joint normalisation was invalid: the hub clique took the spectral radius and at rate 0.03 there
are no silent ticks to delimit avalanches — redone.)

| w (workspace) | ignitions / 1000 ticks | global share of multi-module ticks | max modules co-bursting | module E_norm |
|---|---|---|---|---|
| 0 | 13.5 | 0.036 | 6.0 | 0.97 |
| 0.1 | 10.1 | 0.028 | 7.5 | 0.97 |
| 0.2 | 12.6 | 0.038 | 7.5 | 0.97 |
| 0.4 | **27.7** | **0.078** | **9.0** | **0.95** |

- A sparse workspace layer doubles global ignitions and lets bursts reach almost all modules, **while module
  self-boundaries are preserved** (E_norm 0.97 → 0.95): broadcast without dissolving sub-agents.
- No all-or-none ignition at these weights — graded. Stronger w not tested (would need rate re-matching range).
- EIA reading: a thin "workspace" layer between motive modules is a candidate mechanism for occasional
  agent-wide initiatives (a motive recruits the whole agent) without losing per-motive auditability.

## Tick 68 — can one motive recruit the whole agent via the workspace? (`tick68.py`)

u-only do(Z) on one module, exact twin, 8 seeds × 3 modules, rate-matched; 600 ticks after the intervention.

| workspace w | Δ self (z) | Δ rest (z) | Δ global ignitions (z) |
|---|---|---|---|
| 0 | +160 (2.6) | −326 (−1.1) | −0.9 (−0.6) |
| 0.4 | +138 (**3.8**) | −323 (−1.6) | **−5.8 (−2.2)** |

- **No recruitment**: boosting one motive does not trigger agent-wide ignition; with the workspace layer global
  ignitions even *drop* (−5.8, z −2.2). The boosted module fires early and drains its neighbours and the hubs
  (the fuel-depletion channel of A8), pre-empting the spontaneous global events.
- The tick-67 reading ("a motive recruits the whole agent") is **not supported**: workspace ignitions are
  emergent, collective events that a single motive's internal boost suppresses rather than triggers.
- Per-motive controllability is kept (z 3.8).

## Tick 69 — do sub-agents self-organise under Hebbian plasticity? (`tick69.py`)

ER support (N=500, degree 8); every 20 ticks weights move toward lagged co-activation (row-normalised), global gain
adapted to keep rate ≈ 0.03 (homeostasis). Louvain Q of the weight graph vs weight-shuffled null. 2 seeds, 30 000 ticks.

| eta | weight CV at 30k | Q | Q (shuffled-weight null) |
|---|---|---|---|
| 0 (control) | 0.00 | 0.33 | 0.33 |
| 0.02 | 0.18 | 0.32 | 0.34 |
| 0.05 | 0.50 | 0.33–0.34 | **0.41** |

- Plasticity makes weights strongly heterogeneous (CV 0 → 0.5) while homeostasis holds the rate, but **modularity
  does not emerge**: Q stays flat and falls *below* the shuffled-weight null (0.33 vs 0.41).
- Strong weights therefore run *across* communities: lagged Hebbian learning reinforces the cascade routes, which
  bridge modules — it builds **integrative highways, not segregated sub-agents**.
- Implication: sub-agent structure does not self-organise from plain Hebbian + homeostatic rules; it needs
  competitive/normalising rules or lateral inhibition (cf. A15) or has to be imposed (gating, B5).

## Tick 70 — competitive plasticity (`tick70.py`)

ER N=500, rate homeostasis, eta 0.05, 2 seeds; Q of weights minus Q of the shuffled-weight null (Q − Qn > 0 means
emergent modularity beyond what weight heterogeneity alone gives).

| rule | Q − Qn at 15k | Q − Qn at 30k |
|---|---|---|
| lagged Hebb, input normalisation (tick 69) | −0.027 | **−0.075** |
| synchronous Hebb + input **and** output normalisation (competition) | +0.012 | +0.020 |
| + global inhibition (γ = 3) | +0.030 | **+0.039** |

- The sign flips: lagged Hebbian learning is **anti-modular** (reinforces cross-module cascade routes), synchronous
  co-activation with competitive (doubly normalised) budgets is **modular**, and global inhibition strengthens it;
  the excess grows with time in both seeds.
- Effect sizes are small (Q − Qn ≤ 0.045 after 30k ticks) — self-organised sub-agents emerge slowly and weakly;
  imposed structure/gating (B5) remains far stronger. Useful as a direction for learned motive graphs: learn from
  synchrony, not from lagged causation, under competition + inhibition.

## Tick 71 — are the learned modules functional sub-agents? (`tick71.py`)

After 30k ticks of learning (tick 70 rules), freeze W, simulate 3500 ticks, E_norm (true W) of the Louvain partition of
the learned weights; same partition evaluated on the unlearned ER weights as baseline. 1 seed.

| rule | parts | E_norm, learned W | E_norm, initial W (same partition) | gain |
|---|---|---|---|---|
| lagged Hebb | 14 | 0.41 | 0.44 | −0.03 |
| synchronous + competitive | 19 | 0.52 | 0.42 | +0.10 |
| + global inhibition | 13 | **0.59** | 0.45 | **+0.14** |

- The small structural modularity of tick 70 is **functionally real**: competitive synchronous learning raises the
  endogeneity of its own communities by +0.10–0.14 over the same partition on unlearned weights; lagged Hebb does not.
- Random graphs already have weak Louvain communities (E_norm ≈ 0.43), so the learned increment, not the level, is
  the signal. 1 seed — directional.

## Tick 72 — replication of tick 71 on seeds 2–3 (`tick72.py`, `tick72.out`)

| rule | seed | E_norm learned | E_norm initial | gain |
|---|---|---|---|---|
| lagged Hebb | 2 / 3 | 0.43 / 0.42 | 0.43 / 0.41 | 0.00 / 0.00 |
| synchronous + competitive + inhibition | 2 / 3 | 0.57 / 0.59 | 0.45 / 0.46 | +0.12 / +0.13 |

- Replicates across 3 seeds (with tick 71): competitive synchronous learning adds +0.12–0.14 endogeneity to its own
  communities; lagged Hebb adds none. A23 upgraded to robust.

## Tick 73 — spatial networks with the exponential distance rule (`tick73.py`)

N=1000 points in the unit square, P(edge) ∝ exp(−d/λ), degree 5, no explicit modules. E_norm (true W) of k×k spatial
grid blocks; rate-matched, 2 seeds.

| λ | E_norm for block side 0.083 / 0.125 / 0.2 / 0.333 / 0.5 | side where E_norm = 0.5 | side / λ |
|---|---|---|---|
| 0.02 | 0.58 / 0.70 / 0.78 / 0.91 / 0.92 | < 0.083 | < 4.2 |
| 0.05 | 0.28 / 0.41 / 0.57 / 0.75 / 0.85 | 0.168 | 3.4 |
| 0.12 | 0.09 / 0.15 / 0.28 / 0.48 / 0.65 | 0.350 | 2.9 |

- Without any modules, **the connection length λ sets a characteristic sub-agent size ≈ 3λ** (block side where half
  the initiatives are self-caused). Sub-agents are continuous (any location can be the centre), but their scale is
  fixed by wiring geometry.
- Cortex-like EDR wiring therefore yields a graded, location-free sub-agent structure whose grain is tunable by a
  single parameter — an alternative to discrete modules for motive graphs embedded in a feature space.

## Tick 74 — causal reach of do(Z) in EDR space (`tick74.py`)

u-only do(Z) on the 50 units nearest a centre; exact twin; extra initiatives per unit in distance rings over 400 ticks;
4 seeds × 2 centres. (First pass used |Δ| per unit — that measures trajectory divergence, which is global (tick 6):
flat profile, ℓ ≈ 8–11 λ. Redone with signed Δ.)

| λ | signed Δ per unit, rings 0–.05 / .05–.1 / .1–.15 / .15–.2 / .2–.3 / .3–.45 | decay length ℓ | ℓ/λ |
|---|---|---|---|
| 0.05 | 2.60 / 3.20 / 2.44 / 2.04 / 1.48 / 0.65 | 0.19 | **3.9** |
| 0.12 | 0.60 / 0.82 / 0.32 / −0.33 / −0.23 / −0.19 | — | sign flip at ≈ 0.15 |

- Short-range wiring (λ = 0.05): the mean causal effect of an internal intervention decays with ℓ ≈ 4λ — matching the
  sub-agent size ≈ 3λ from tick 73: **the causal reach of a motive equals its sub-agent scale**.
- Longer-range wiring (λ = 0.12): weak excitation near the centre and **suppression beyond ≈ 1.2λ** — a
  centre–surround profile (fuel-depletion channel, A8). Small effects, 8 samples — directional.
- Divergence (|Δ|) is global in every case; only the signed effect has a finite reach.

## Tick 75 — hierarchy of timescales (`tick75.py`)

SBM 10×100 (μ 0.1); modules 0–4 fast (drive decay ρ 0.30), 5–9 slow (ρ 0.05); α scaled with ρ so the drive
equilibrium is unchanged (first run without this silenced the fast modules — invalid). Rate-matched 0.03, 3 seeds.
E = raw module endogeneity (true W); flow = cross-group triggers per unit of source activity.

| condition | E fast | E slow | fast→slow per source act. | slow→fast per source act. | slow / fast activity |
|---|---|---|---|---|---|
| uniform ρ | 0.95 | 0.93 | 0.009 | 0.010 | 0.79 |
| hierarchy | 0.89 | **0.96** | 0.007 | 0.004 | **4.3** |

- With a timescale hierarchy the **slow modules carry most of the activity (×4.3) and are the more self-driven**
  (E 0.96 vs 0.89). Per unit of activity fast modules trigger slow ones slightly more, but in absolute counts slow→fast
  triggering dominates (≈ 0.017 vs 0.007, ~2.5×): slow modules act as the internal generator, fast ones as driven
  periphery.
- Mirrors the human picture (slow association/DMN as internal generator vs faster sensory cortex) and suggests a
  design knob: give "reflective" motives slow integration and "reactive" ones fast integration. Modest effect sizes.

## Tick 85 — generator vs isolated: interventions separate what attribution cannot (`tick85.py`)

SBM 10×100 (μ 0.1); module 0 as normal / GENERATOR (excitability ×1.8) / ISOLATED (incoming cross-module links ×0.1).
Rate-matched, 4 seeds.

| module 0 | attribution self-initiation | out-influence (rest activity drop when module silenced) | independence (activity kept when its input is cut) |
|---|---|---|---|
| normal | 0.94 | 0.134 | 0.49 |
| generator | 0.98 | **0.172** | 0.82 |
| isolated | **1.00** | **0.097** | 0.92 |

- Attribution-based self-initiation **cannot** separate them — the isolated module even scores highest (1.00).
- A two-intervention signature does: **generator = high out-influence + high independence; isolated = low
  out-influence + high independence**; normal = medium out-influence, low independence.
- Operational definition proposal for EIA audits: an internal generator is a unit that (i) keeps its activity when its
  inputs are cut and (ii) drives others when present. Attribution alone (EOI-style, SourceMass, E(B)) measures only (i)'s
  shadow and rewards isolation.

## Tick 87 — does module-graph topology create a generator? (`tick87.py`)

10 modules × 100 units; cross-module links only along a module graph (ring / star with hub module 0 / complete), same total
cross edges; rate-matched, 2 seeds. A26 signature for module 0 (hub in the star) and module 5 (leaf).

| module graph | out m0 | indep m0 | out m5 | indep m5 |
|---|---|---|---|---|
| ring | 0.66 | 0.41 | 1.69 | 0.37 |
| star | **5.44** | **0.18** | 1.56 | 0.40 |
| complete | 2.37 | 0.38 | 2.38 | 0.39 |

- The star's hub module gets by far the largest out-influence but the **lowest independence**: it is a **relay /
  integrator** that depends on its leaves, not a self-sustaining generator. Ring and complete graphs stay collective.
- **Centrality ≠ generator**: topology alone produces drivers that need input; a generator in the A26 sense (keeps going
  when cut off *and* drives others) required intrinsic excitability (tick 85). Consistent with B16 (hub-rich SAL/SMA are
  high-influence but dependent).

## Tick 88 — generator strength vs enslavement (`tick88.py`)

SBM 10×100 (μ 0.1); module 0 excitability × f; rate-matched (global activity fixed), 2 seeds.

| f | out (per unit share) | indep | generator's share of all activity | raw E of the other modules |
|---|---|---|---|---|
| 1.0 | 2.03 | 0.49 | 0.17 | 0.94 |
| 1.3 | 1.29 | 0.76 | 0.25 | 0.93 |
| 1.8 | 1.33 | 0.94 | 0.37 | 0.92 |
| 2.5 | 1.42 | 0.97 | 0.42 | 0.91 |

- A stronger generator becomes **self-sustaining** (independence 0.49 → 0.97) and takes a growing **share of the
  activity budget** (0.17 → 0.42), but its per-unit influence on others does *not* grow and the other modules stay
  sub-agents (E 0.94 → 0.91): **no enslavement** — under a fixed global budget a strong motive crowds others out rather
  than driving them.
- Design reading: an intrinsically strong motive is a *budget* risk (dominance of initiative share), not a *control*
  risk (other motives keep their own causes). A Governor should cap per-motive activity share, not per-motive influence.

## Tick 89 — share-capping Governor (`tick89.py`)

SBM 10×100, module 0 excitability ×2.5; Governor raises a module's firing threshold while its activity share exceeds the
cap (checked every 50 ticks). Same W in both conditions; 2 seeds.

| condition | generator share | generator independence | E of other modules | overall rate |
|---|---|---|---|---|
| no governor | 0.42 | 0.97 | 0.91 | 0.029 |
| cap 0.15 | **0.14** | **0.91** | **0.94** | 0.018 |

- The cap holds the strong motive at its budget (0.42 → 0.14) while it **stays a self-sustaining generator** (0.91) and the
  other motives regain their endogeneity (0.91 → 0.94).
- Cost: total initiative drops (0.029 → 0.018) — the others do not refill the freed budget; the generator was also
  feeding them. A budget Governor trades volume for balance.

## Tick 90 — redistributing Governor (`tick90.py`)

As tick 89 but thresholds may also *drop* below baseline for under-cap motives (lower bound θ − 0.3), optionally with a
global offset that holds total rate at 0.03. Module 0 excitability ×2.5; 2 seeds.

| condition | generator share | generator indep | E others | overall rate |
|---|---|---|---|---|
| no governor | 0.42 | 0.97 | 0.91 | 0.029 |
| cap 0.15, thresholds free to drop | 0.10 | 0.98 | 0.95 | **0.159** (runaway) |
| **cap 0.15 + hold total rate** | **0.07** | **0.90** | **0.94** | **0.035** |

- Letting under-cap motives lower their thresholds without a total-rate constraint **runs away** (rate ×5) — a pure
  share rule redistributes by pushing everyone else into over-activity.
- Adding a global rate-holding offset gives the intended outcome: the strong motive is capped (share 0.07), stays a
  generator (0.90), the others keep their sub-agency (0.94), and **total initiative is preserved** (0.035 vs 0.029) —
  removing the tick-89 volume cost.
- Governor design: *two* loops — per-motive share cap + global budget hold. Either alone fails (volume loss / runaway).

## Tick 91 — two-loop Governor kills per-motive controllability (`tick91.py`)

Strong generator (module 0, ×2.5); u-only do(Z) on a non-dominant motive (5, 8); exact twin; 600 ticks; 6 seeds × 2 targets.

| condition | Δ target (z) | Δ rest (z) |
|---|---|---|
| no governor | **+153 (12.6)** | −143 (−1.8) |
| two-loop governor (tick 90) | **−343 (−2.7)** | −606 (−1.3) |

- **Negative result**: under the two-loop Governor, raising a motive's uncertainty makes it act *less* — the Governor sees
  its share rise and raises its threshold (the per-motive loop integrates without leak or deadband, and under-cap motives
  have drifted to the lower threshold bound, so any surge overshoots the cap).
- The budget Governor of tick 90 buys balance at the price of controllability: it treats a legitimate internal change as
  a budget violation. Needs a deadband / leaky (proportional) share control, or a cap that applies only to the chronically
  dominant motive. Next: test a leaky, deadband version.

## Tick 92 — leaky, chronic-dominance Governor (`tick92.py`)

Per-motive threshold θ0 + kp·max(0, S_m − 0.15) with S_m a slow EMA of share (τ ≈ 1000 ticks, reacts only to chronic
dominance, never below θ0, no integration); global proportional loop on a slow EMA of rate. Module 0 ×2.5; u-only do(Z)
on non-dominant motives; 6 seeds × 2 targets.

| condition | generator share | rate | Δ target (z) | Δ rest (z) |
|---|---|---|---|---|
| no governor | 0.41 | 0.029 | +122 (6.7) | +77 (0.8) |
| **leaky governor** | **0.14** | 0.021 | **+158 (4.4)** | −87 (−0.4) |

- The leaky chronic-dominance Governor caps the strong motive (0.41 → 0.14) **and keeps per-motive controllability**
  (boost → +158, z 4.4) — fixing the tick-91 reversal.
- Residual cost: rate 0.021 vs 0.03 target (proportional global loop leaves a steady-state error); an integral term with
  a slow time constant on the *global* loop only would close it.
- Governor recipe: slow, leaky, one-sided (upward only) share control for chronic dominance + a global budget loop;
  never let the per-motive loop integrate on fast timescales.

## Tick 93 — leaky Governor + slow global integral (`tick93.py`)

| condition | generator share | rate (window 1000–2000) | Δ target (z) | Δ rest (z) |
|---|---|---|---|---|
| no governor | 0.41 | 0.029 | +122 (6.7) | +77 (0.8) |
| leaky (tick 92) | 0.14 | 0.021 | +158 (4.4) | −87 (−0.4) |
| **leaky + global integral** | **0.14** | **0.025** | **+181 (4.3)** | −29 (−0.2) |

- A slow integral term on the global budget loop only narrows the rate shortfall (0.021 → 0.025, still converging within
  the measured window) while keeping the cap (0.14) and per-motive controllability (+181, z 4.3) and making spill-over
  neutral. This is the working Governor recipe of the toy line: **slow one-sided leaky share cap per motive + global
  budget loop with a slow integral**.

## Tick 94 — Governor recipe across topologies (`tick94.py`)

Motive labels = 10 blocks of 100 units; module 0 excitability ×2.5; 4 seeds × 2 targets.

| topology | governor | generator share | rate | Δ boosted motive (z) |
|---|---|---|---|---|
| SBM | no / yes | 0.40 / **0.13** | 0.029 / 0.026 | +126 (6.1) / **+187 (6.5)** |
| hier-modular | no / yes | 0.39 / **0.19** | 0.030 / 0.027 | +138 (4.0) / **+209 (4.2)** |
| ER (labels only) | no / yes | 0.16 / 0.12 | 0.030 / 0.026 | +48 (1.5) / **+152 (3.3)** |

- The recipe transfers: it caps the dominant motive in every topology (hierarchy only partly: 0.19 vs cap 0.15) and
  per-motive controllability is kept or **improved** — in ER it goes from not significant to z 3.3, because capping the
  generator frees budget that the boosted motive can use.
- Rate settles slightly below target (0.026–0.027) within the window.

## Tick 95 — discoverability threshold with calibrated inference (`tick95.py`)

SBM 10×100, degree 5, rate 0.03, 2 seeds. ARI of blindly found parts vs true modules, graph inferred by pairwise lagged
excess (as tick 24) vs conditional attribution (tick 35).

| inference | μ=0.3 | 0.2 | 0.15 | 0.1 | 0.07 | 0.05 | μ_c (ARI = 0.5) |
|---|---|---|---|---|---|---|---|
| pairwise | 0.05 | 0.16 | 0.17 | 0.39 | 0.60 | 0.79 | ≈ 0.08 |
| **conditional** | 0.13 | 0.44 | **0.57** | **0.82** | 0.87 | 0.91 | **≈ 0.17** |

- Better (conditional) inference **roughly doubles the discoverability threshold** (μ_c 0.08 → 0.17). A12's μ_c is a
  property of the detector as much as of the network: with calibrated attribution, sub-agents with up to ~15–20 %
  outgoing links are recoverable blind. Design rule D3 relaxes accordingly.

## Tick 98 — agent–world loop: the world as hidden memory (`tick98.py`)

Agent SBM 10×100 at X = 0; a 'world' of 100 relays echoes the agent's own motor initiatives back to sensory units after
20 ticks (p 0.8, weight w). Rate-matched on the agent; 3 seeds.

| w (world echo) | initiatives directly touched by world input | agent activity kept when the world is cut |
|---|---|---|
| 0 | 0.000 | 0.97 (noise floor: different RNG stream) |
| 0.5 | 0.051 | 0.89 |
| 1.0 | 0.043 | **0.84** |

- A world that only reflects the agent's own actions silently carries **~13 % of its "endogenous" activity** (net of the
  3 % noise floor), while only **~4–5 %** of initiatives show a direct world cause: attribution under-counts the
  externalised loop ~3×, because each echo seeds internal cascades.
- For EIA audits at X = 0: "no external trigger" does not mean "no external dependence". The environment can act as
  memory/scaffold (identification threats #2 memory leakage and #7 sensor leakage); only a cut-the-world intervention
  (world held frozen / replayed without contingency) reveals it.

## Tick 99 — world-echo delay and agent topology (`tick99.py`)

w = 1; hidden support = activity lost when the world is cut, net of the w = 0 noise floor; 3 seeds.

| agent | delay D | direct share | hidden support | hidden / direct |
|---|---|---|---|---|
| SBM | 5 / 20 / 100 / 300 | 0.04 / 0.04 / 0.12 / 0.05 | 0.09 / 0.15 / **0.19** / 0.15 | 2.4 / 3.5 / 1.6 / 2.9 |
| ER | 5 / 20 / 100 / 300 | 0.07 / 0.17 / 0.16 / 0.08 | **0.32 / 0.32 / 0.34 / 0.30** | 4.5 / 1.9 / 2.1 / 4.0 |

- Hidden world support is always **1.6–4.5× the directly attributed share**; it peaks at intermediate delays in the modular
  agent (0.19 at D = 100) and is roughly delay-independent in ER.
- **Topology matters more than delay**: the ER agent leans on the world ~2× more (≈ 0.32) than the modular one
  (≈ 0.15) — without sub-agents to sustain activity internally, an agent outsources its persistence to the environment.
  Modularity is a protection against externalised endogeneity.

## Tick 100 — contingency vs input volume (`tick100.py`)

w = 1, D = 20; the random stream is now identical across modes (no noise floor). Non-contingent replay = the recorded echo
stream, shuffled in 50-tick blocks and replayed regardless of the agent's actions. 3 seeds.

| agent | activity kept: world cut | kept: non-contingent replay | share of world support due to contingency |
|---|---|---|---|
| modular (SBM) | 0.89 | 1.06 | ≤ 0 |
| ER | 0.64 | 0.89 | **0.30** |

- The modular agent depends on the world only as **input volume**: a non-contingent replay fully substitutes for the real
  loop (even slightly over-supports it).
- The ER agent depends on it more (cut → 0.64), and **~30 % of that support needs the echo to be contingent** on its own
  actions — a genuine externalised memory loop that a replay cannot replace.
- Audit protocol for X = 0 claims: run both *world-cut* (total external support) and *non-contingent replay* (contingent
  part); only the contingent part is a hidden agent–world loop; the rest is ordinary input dependence.

## Tick 101 — core–periphery: who starts, who amplifies (`tick101.py`)

Core 200 units (dense), periphery 800 (sparse, attached to the core), mean degree ≈ 5, rate-matched, 3 seeds.
Cascade start = a unit that fires with no active in-neighbour at t − 1.

| block (share of units) | out-influence per unit share | independence | share of cascade starts | share of activity |
|---|---|---|---|---|
| core (20 %) | **2.43** | 0.21 | 0.13 | **0.70** |
| periphery (80 %) | 0.98 | **0.51** | **0.87** | 0.30 |

- **Division of labour**: initiatives are *seeded* in the periphery (87 % of cascade starts, more independent) and
  *amplified* by the core (70 % of activity, highest influence, dependent — a relay in the A27 sense).
- Neither block is a generator alone; endogeneity = peripheral sparks × core amplification. EIA reading: many weakly
  coupled peripheral motives supply novelty, a dense core broadcasts it — the core is where a Governor's share cap
  (A29) bites, the periphery is where new initiatives come from.

## Tick 104 — resilience of endogenous initiative to lesions (`tick104.py`)

Gain fixed at the intact rate-matched value; 5 / 10 / 20 % of units removed at random or highest-degree first; activity of
the remaining units relative to intact. 2 seeds.

| topology | random 5 / 10 / 20 % | hubs 5 / 10 / 20 % |
|---|---|---|
| ER | 0.59 / 0.45 / 0.36 | 0.41 / 0.32 / 0.28 |
| SBM | 0.66 / 0.49 / 0.38 | 0.43 / 0.35 / 0.30 |
| **hier-modular** | **0.70 / 0.58 / 0.45** | **0.54 / 0.39 / 0.36** |
| scale-free (BA) | **0.91** / 0.39 / 0.35 | **0.30** / 0.30 / 0.30 |

- Collective endogeneity near the critical point is **fragile**: losing 5 % of units at random already removes 30–40 % of
  the survivors' activity (lower loop gain); the floor ≈ 0.28–0.30 is the per-unit aging clock (A1) — collective activity gone.
- **Hierarchy is the most resilient** to both random and targeted loss; scale-free is robust to small random loss but
  collapses at once when hubs go (the classic robust-yet-fragile pattern).
- Design note: an endogenous agent operated near criticality needs **gain homeostasis** (re-tuning after loss) or it
  falls back to clock-like unit activity; hierarchical organisation buys the most slack.

## Tick 105 — gain homeostasis after a 10 % hub lesion (`tick105.py`)

Gain re-bisected so survivors return to rate 0.03. 2 seeds.

| topology | gain increase needed | burst CV intact → retuned | module E_norm intact → retuned |
|---|---|---|---|
| ER | ×1.34 | 1.76 → 1.54 | — |
| SBM | ×1.30 | 1.38 → 1.39 | 0.93 → 0.92 |
| **hier-modular** | **×1.22** | 1.39 → 1.47 | **0.95 → 0.95** |
| scale-free (BA) | **×2.15** | 1.03 → **0.53** | — |

- With gain homeostasis, modular and hierarchical agents **fully recover** graded, bursty collective initiative and keep their
  sub-agents intact; hierarchy needs the least compensation (×1.22).
- Scale-free needs twice the gain and recovers only **clock-like** activity (CV 1.03 → 0.53): after losing its hubs the
  remaining network cannot regain rich endogeneity by gain alone.
- Completes A33: lesion fragility near criticality is repairable by homeostasis in modular/hierarchical architectures,
  not in hub-dependent ones.

## Tick 106 — noise-driven vs self-sustained endogeneity (`tick106.py`)

Rate-matched gain; noise switched off after 2000 ticks. 2 seeds.

| topology | activity kept without noise | burst CV with noise | burst CV without noise |
|---|---|---|---|
| **hier-modular** | **0.94** | 1.24 | 1.37 |
| ER | 0.64 | 1.81 | 2.10 |
| SBM | 0.64 | 1.48 | 1.95 |
| EDR (λ 0.05) | 0.54 | 1.37 | 1.34 |
| scale-free (BA) | **0.38** | 1.08 | 1.83 |

- Hierarchical-modular endogeneity is almost entirely **self-sustained** (94 % survives without noise); scale-free is mostly
  **noise-driven** (38 %); flat modular/ER/spatial in between.
- Without noise the dynamics stays **irregular** (CV 1.3–2.1, not a clock): uncertainty aging + resolution + coupling generate
  deterministic irregular initiative. Noise is not what makes initiative non-periodic here; it mainly sustains activity in
  hub-dependent topologies.
- Adds to A33/A34-style resilience: hierarchy = least dependent on noise, on lesions and on gain re-tuning.

## Tick 107 — filling the scorecard gaps (`tick107.py`)

| topology | lesion 10 % random | lesion 10 % hubs | kept without noise | hidden world support |
|---|---|---|---|---|
| small-world | 0.51 | 0.43 | 0.67 | **0.12** |
| EDR (λ 0.05) | 0.52 | 0.35 | 0.54 | 0.33 |
| hier-modular | 0.59 | 0.39 | 0.94 | 0.24 |
| scale-free | 0.85 | 0.30 | 0.38 | 0.41 |

- Hierarchy remains best on noise-independence and lesions (except BA's random-loss value, which is noisy: 0.39 in tick 104,
  0.85 here), but it is **not** the most world-independent: small-world (0.12) and flat modular (0.15) lean on a reactive
  world less. Scorecard updated with a caveat.

## Tick 108 — sensor/motor placement confound (`tick108.py`)

Hidden world support (w = 1, D = 20), sensors and motors as contiguous blocks vs scattered at random; 2 seeds.

| topology | contiguous | scattered |
|---|---|---|
| small-world | **0.12** | 0.25 |
| hier-modular | 0.24 | 0.27 |

- Small-world's low world dependence in tick 107 was a **placement artefact**: contiguous sensors form one local ring patch,
  so the echo stays local; scattered sensors double the dependence (0.25), matching hierarchy (0.27). Hierarchy is
  insensitive to placement.
- Corrected reading: with realistic distributed sensors, small-world and hierarchy lean on a reactive world equally
  (~0.25); world dependence is governed more by **how the interface is embedded** (local vs distributed) than by topology
  class. Scorecard caveat updated.

## Tick 109 — A30 re-checked with scattered sensors (`tick109.py`)

| topology | contiguous interface (= one module in SBM) | scattered interface |
|---|---|---|
| SBM | 0.15 | **0.31** |
| ER | 0.32 | 0.36 |

- **A30's "modularity protects against externalised endogeneity" was largely a placement artefact**: when the sensors and
  motors are scattered, the modular agent leans on the world almost as much as ER (0.31 vs 0.36). What protects is
  **confining the world interface to one sub-agent** (a dedicated sensorimotor module) — then the echo stays inside it.
- Revised design point: give the agent a dedicated interface module rather than distributing sensors/motors over its motives;
  modularity helps only if the interface respects the module boundaries.

## Tick 110 — A31 with a scattered interface (`tick110.py`)

| agent | kept: world cut | kept: non-contingent replay | contingency share of world support |
|---|---|---|---|
| SBM | 0.68 | 0.94 | 0.21 |
| ER | 0.67 | 0.94 | 0.19 |

- With a scattered interface the SBM/ER contrast of tick 100 **disappears**: both lose ~1/3 of activity when the world is cut
  and ~20 % of that support requires contingency (a real agent–world memory loop). Tick 100's "modular agent needs only
  volume" was, like A30, an effect of confining the interface to one module.
- Stable part of A30–A31: attribution under-counts world support; world-cut + non-contingent replay separate volume from
  contingency; confining the interface to one sub-agent reduces both.

## Tick 111 — dedicated interface module (`tick111.py`)

SBM with 10 motive modules + 1 interface module (N = 1100); echo w = 1, D = 20; identical random stream across conditions; 3 seeds.

| placement of 100 sensors / 100 motors | hidden world support (whole agent) | motive-module activity kept when world cut |
|---|---|---|
| in two motive modules (0 and 9) | 0.06 | 0.93 |
| **dedicated interface module** | 0.24 | **0.91** |
| scattered over motives | 0.29 | **0.69** |

- A dedicated interface module **protects the motives**: they keep 91 % of their activity without the world (vs 69 % with a
  scattered interface). The interface module itself is world-driven — whole-agent hidden support (0.24) is dominated by it,
  which is the intended division of labour.
- Audit implication: report world dependence **per sub-agent**, not for the whole agent; a whole-agent number mixes the
  (legitimately reactive) interface with the (supposedly endogenous) motives.

## Tick 112 — A26 signature of the prototype's drives (`../eia_prototype/tick112_prototype_signature.py`)

TargetEngine (tension-set targets), fixed tension 0.5, μ 0.05; calibrated gain 0.4 vs near-critical 1.0; 5 seeds.

| engine | out-influence (each drive) | independence (each drive) | activity |
|---|---|---|---|
| calibrated (0.4) | 0.01–0.02 | 0.97–0.98 | ≈ 0.07 |
| near-critical (1.0) | 0.01 | 0.98 | ≈ 0.15 |

- All three drives are **isolated-type** in the A26 sense: fully self-sustaining (their own tension-set uncertainty keeps them
  going) but with essentially **no influence on each other** at μ = 0.05. The prototype achieves separability by
  non-interaction — motives never recruit or inhibit one another.
- Design consequence: if inter-motive interaction is wanted (e.g. an epistemic question triggered by a coherence conflict),
  the cross-drive coupling has to be raised deliberately (toward μ ≈ 0.1–0.2, still discoverable with a conditional
  detector, A12) or routed through a workspace layer (A21); the current prototype has none.

## Tick 113 — adding inter-motive interaction to the prototype (`../eia_prototype/tick113_cross_drive.py`)

Calibrated TargetEngine; cross-drive mixing μ. Interaction = relative change of epistemic activity when only coherence
tension rises 0.2 → 0.8 (5 seeds). Eval compatibility = first initiative unchanged vs the current pipeline (7 scenarios × 3 seeds).

| μ | epistemic response to coherence tension | first initiative unchanged |
|---|---|---|
| 0.05 | +4 % | 1.00 |
| 0.15 | +11 % | 1.00 |
| 0.30 | **+20 %** | **1.00** |

- Raising cross-drive coupling gives a graded inter-motive interaction (a coherence conflict raises epistemic activity by up to
  20 %) **without any loss of eval compatibility** (100 % at every μ). Combined with A12 (μ ≲ 0.15–0.2 stays blindly
  discoverable with the conditional detector), **μ ≈ 0.15 is a reasonable default**: motives interact (+11 %), stay auditable,
  evals unchanged.

## Tick 114 — system card v3 with cross-drive μ = 0.15 (`../eia_prototype/tick114_system_card_v3.py`, `.out`)

| metric (mean of 7 scenarios × 3 seeds) | current | v2 (μ 0.05, tick 63) | **v3 (μ 0.15)** |
|---|---|---|---|
| first initiative unchanged | 1.00 | 1.00 | **1.00** |
| EOI | 1.00 | 0.95 | 0.90 |
| drive-dependence v(all) | 0.71 | 0.98 | 0.99 |
| questions in 200 silent episodes | 199.6 | 4.6 | 3.6 |
| longest same-question run | 199.4 | 1.0 | 1.05 |
| ISI CV | 0.03 | 1.17 | 1.08 |

- Adding inter-motive interaction (μ 0.15) keeps every gain of v2 and full eval compatibility; EOI drops slightly
  (0.95 → 0.90) because coupled drives make the twin diverge a little more. v3 is the recommended prototype configuration.

## Tick 115 — draft patch for opt-in population drives v3 (`../patches/draft_population_drives.patch`), not applied

Full suite 300 passed, 6 pre-existing failures; 10 new tests pass (eval initiative unchanged in 7/7 scenarios).

## Tick 116 — integration / TSE complexity vs sub-agent endogeneity (`tick116.py`)

Module-level signals (10 blocks × 100 units, 10-tick bins), Gaussian estimates; rate-matched, 2 seeds.

| topology | integration I(X) | TSE complexity | module E_norm |
|---|---|---|---|
| ER | **22.2** | **13.1** | −0.00 |
| scale-free | 10.3 | 7.1 | 0.21 |
| small-world | 8.4 | 6.1 | 0.88 |
| flat modular | 4.6 | 4.5 | 0.93 |
| hier-modular | **1.2** | **1.5** | **0.95** |

- Across topologies, integration and TSE complexity rank **exactly opposite** to sub-agent endogeneity (Spearman −1.0 over 5).
  At this level, high integration means the blocks rise and fall together (global bursts); high sub-agent endogeneity means
  they run on their own causes.
- So "more integration = more agency" (IIT-style intuitions) and "more sub-agent endogeneity" pull in opposite directions:
  integration is a property of the *whole* acting as one, E(B) of the *parts* acting for themselves. An architecture has
  to choose the level at which it wants to be endogenous — or get both via a hierarchy plus a thin workspace layer (A21:
  ignitions without dissolving sub-agents).
- Caveats: Gaussian estimator on 10 coarse block signals; blocks are arbitrary index sets in ER/BA; classic TSE is expected
  to peak at intermediate structure with finer-grained measurement. Directional.

## Tick 117 — workspace layer: integration without losing sub-agents (`tick117.py`)

SBM 10×100 (μ 0.05) + hub workspace layer of weight w; rate-matched; block-level Gaussian integration / TSE; 2 seeds.

| w | integration | TSE | module E_norm |
|---|---|---|---|
| 0 | 0.36 | 0.62 | 0.97 |
| 0.2 | 0.60 | 0.97 | 0.97 |
| **0.4** | **1.65** | **2.28** | **0.95** |
| 0.8 | 1.81 | 2.21 | 0.80 |

- A moderate workspace layer (w ≈ 0.4) raises whole-level integration ~4.6× and TSE ~3.7× while sub-agent endogeneity stays
  at 0.95 — the A35 trade-off is **escapable**. Beyond that (w 0.8) integration saturates and sub-agents start to dissolve
  (0.80). Sweet spot w ≈ 0.4: both levels endogenous. Supports the "hierarchy + thin workspace" recommendation.

## Tick 118 — the recommended architecture as a whole (`tick118.py`)

Hierarchical-modular motives ± thin workspace layer (w 0.4); rate-matched; 3 seeds (6 boosts per condition).

| architecture | integration | TSE | module E_norm | Δ boosted motive (z) |
|---|---|---|---|---|
| hier alone | 1.52 | 1.82 | 0.95 | +310 (2.1) |
| **hier + workspace** | **2.82** | **2.86** | **0.92** | +223 (2.1) |

- Adding the workspace to the hierarchy nearly doubles whole-level integration and TSE (×1.9 / ×1.6) while sub-agent
  endogeneity stays high (0.95 → 0.92) and per-motive controllability is kept (same z; smaller mean effect as some of the
  boost is broadcast). The combined recommendation (hierarchy + thin workspace) holds its promise on all three axes at once.
- Small n (6 boosts): controllability z ≈ 2 in both — directional.

## Tick 119 — tick 118 controllability with 18 boosts (`tick119.py`)

| architecture | Δ boosted motive (z) | Δ rest of the agent (z) |
|---|---|---|
| hier alone | +210 (**3.8**) | +214 (1.2) |
| hier + workspace | +133 (**2.4**) | **−555 (−2.0)** |

- With more samples the workspace **does cost controllability**: the boosted motive's gain drops ~35 % (z 3.8 → 2.4), and the
  rest of the agent is now *suppressed* (−555, z −2.0) instead of mildly excited — the boosted motive drains the shared hubs
  (same mechanism as tick 68). Tick 118's "controllability kept" (n = 6) was too optimistic.
- Refined recommendation: the thin workspace buys integration at a moderate controllability price and turns inter-motive
  influence competitive; keep w small (≤ 0.4) and pair it with the leaky share-cap Governor (A29) if balance matters.

## Tick 120 — hierarchy + workspace with the leaky Governor (`tick120.py`)

Protocol of ticks 92–93 (boost at t0 = 2000 after Governor warm-up, 600-tick horizon); 6 seeds × 3 motives.

| condition | Δ boosted motive (z) | Δ rest (z) |
|---|---|---|
| hier + workspace, no governor | +171 (**7.5**) | +408 (2.2) |
| hier + workspace + leaky governor | +88 (1.9) | −305 (−1.7) |

- **The Governor does not restore control here — it halves it** (z 7.5 → 1.9): without a chronically dominant generator,
  a boosted motive's rising share is itself what the cap acts on. A share cap cannot distinguish a legitimate internal
  surge from chronic dominance within its time constant.
- **Protocol sensitivity**: the same architecture without Governor gave z 2.4 and spill −555 in tick 119 (boost at t0 = 1000)
  but z 7.5 and spill +408 here (t0 = 2000). Spill-over sign and controllability magnitude depend on the intervention time /
  warm-up — spill-over estimates in this line (A35, A21) are therefore only indicative.
- Governor use rule: apply the share cap only when a motive is chronically dominant (e.g. gate the cap on a long-window
  share test), not as a standing regulator in balanced agents.

## Tick 121 — dominance-gated Governor (`tick121.py`)

Per-motive cap applied only while a motive's slow share exceeds 0.25; global budget loop unchanged. 6 seeds × 3 motives.

| case / governor | module-0 share | Δ boosted motive | z |
|---|---|---|---|
| A strong generator / none | 0.40 | +152 | 6.2 |
| A strong generator / always-on cap | 0.14 | +137 | 4.0 |
| **A strong generator / gated cap** | **0.14** | **+217** | **4.1** |
| B balanced hier+ws / none | 0.10 | +171 | 7.5 |
| B balanced hier+ws / always-on cap | 0.10 | +88 | 1.9 |
| **B balanced hier+ws / gated cap** | 0.10 | **+137** | **3.7** |

- Gating the cap on chronic dominance keeps the generator capped (0.14, same as always-on) and **recovers much of the
  controllability** lost in balanced agents (z 1.9 → 3.7; +88 → +137), and even improves it in the generator case (+217).
- Not a full recovery in B (z 7.5 without any Governor): the global budget loop still leans against any surge. Final recipe:
  **dominance-gated share cap + slow global budget loop**; accept a moderate controllability cost for budget safety.

## Tick 122 — where does the residual control loss come from? (`tick122.py`)

Balanced hier + workspace; 6 seeds × 3 motives.

| governor | Δ boosted motive | z |
|---|---|---|
| none | +171 | 7.5 |
| global budget loop only | +156 | 3.9 |
| gated cap + budget loop | +137 | 3.7 |

- The global budget loop alone barely reduces the *mean* effect (171 → 156) but halves z: it adds **variance** (a fluctuating
  shared threshold), not suppression. The gated cap adds only a small further mean cost (156 → 137).
- So the residual "controllability loss" of the final recipe is mostly noise injected by the budget integrator — tunable by a
  slower / smaller integral gain, not a structural limit.

## Tick 123 — slower budget integrator (`tick123.py`)

Gated Governor, ki 0.002 vs 0.0005; 6 seeds × 3 motives.

| ki | case | generator share | Δ boosted motive | z |
|---|---|---|---|---|
| 0.002 | A (generator) | 0.14 | +217 | 4.1 |
| 0.002 | B (balanced) | 0.10 | +137 | 3.7 |
| 0.0005 | A | 0.16 | +160 | 6.3 |
| 0.0005 | B | 0.10 | +123 | 2.5 |

- **No clean tuning fix**: a slower integrator helps controllability in the generator case (z 4.1 → 6.3, slightly weaker cap
  0.16) but not in the balanced case (3.7 → 2.5). Tick 122's "residual loss is integrator variance, tunable" is **not
  confirmed** — at n = 18 boosts these z values are too noisy to rank settings finely.
- Governor line closed for the toy model: the gated cap + slow budget loop is a workable default (caps dominance, keeps
  z ≈ 3–6), with an irreducible, noisy controllability cost of ~⅓–½ of the ungoverned z.

## Tick 124 — a global carrier rhythm ("42 Hz" as test assumption) (`tick124.py`)

Global gain × (1 + A·sin(2πt/24)); rate-matched at A = 0; 2 seeds. PLV = phase locking of population burst onsets to the carrier.

| topology | A | rate | PLV to carrier | burst CV | module E_norm |
|---|---|---|---|---|---|
| hier | 0 / 0.05 / 0.15 / 0.3 | 0.031 / 0.029 / 0.021 / 0.016 | 0.04 / **0.21** / 0.52 / **0.71** | 1.42 / 1.31 / 0.87 / **0.65** | 0.95 (all) |
| ER | 0 / 0.05 / 0.15 / 0.3 | 0.028 / 0.025 / 0.021 / 0.015 | 0.03 / 0.05 / 0.17 / 0.41 | 1.53 / 1.42 / 1.10 / 0.73 | 0.00 (all) |

- A carrier **captures the timing** of initiative: bursts phase-lock to it (PLV up to 0.71) and become more regular (CV 1.4 →
  0.65), while *which* sub-agent acts and why (module E_norm 0.95) is untouched. Timing becomes carrier-driven — a hidden
  scheduler for "when", not for "who/why".
- The hierarchical agent is **more entrainable** than ER (PLV 0.21 vs 0.05 already at 5 % modulation): the structure that
  makes it rich and graded also makes it resonant to a global rhythm.
- For EIA/Kairologos: a global carrier (e.g. the 42 Hz assumption) should be treated as a *timing input* in audits — "why now"
  claims must be checked against phase locking to any global rhythm, or the carrier acts as identification threat #1.
  Strong carriers also reduce the overall rate (−50 % at A = 0.3).

## Tick 125 — carrier resonance (`tick125.py`)

Weak modulation A = 0.05; carrier period P swept; PLV of burst onsets; 2 seeds.

| topology | P = 6 | 12 | **24** | 48 | 96 | 192 |
|---|---|---|---|---|---|---|
| hier | 0.38 | 0.19 | **0.21** | 0.37 | 0.20 | **0.80** |
| ER | 0.15 | 0.10 | **0.05** | 0.59 | 0.42 | **0.87** |

- Entrainment is strongest for **slow** carriers (P = 192: PLV 0.80–0.87 at only 5 % modulation) — slow gain changes are
  followed quasi-statically by the burst dynamics. The "42 Hz" period (24 ticks) sits near a *local minimum* of
  entrainability for both topologies; it is not a privileged frequency in this model. Hierarchy has an extra fast peak at
  P = 6 (≈ refractory period + 1).
- Audit consequence: the most dangerous hidden schedulers are **slow** rhythms (circadian-like, polling cycles), not fast
  carriers; check "why now" against slow global modulations first. 2 seeds, noisy (non-monotonic mid-range).

## Tick 126 — carrier resonance on 5 seeds (`tick126.py`)

| topology | P = 6 | **24** | 48 | 192 |
|---|---|---|---|---|
| hier | 0.32 | **0.23** | 0.33 | 0.73 |
| ER | 0.13 | **0.05** | 0.59 | 0.87 |

- Replicates tick 125: slow carriers entrain most (P 192: 0.73 / 0.87), the 24-tick period is the minimum for both topologies,
  and hierarchy keeps its fast peak at P = 6. A36 upgraded to robust.

## Tick 130 — adaptation ("boredom") and the internal-clock risk (`tick130.py`)

Unit adaptation current (strength b, τ 100 ticks) subtracted from the drive; rate-matched; 2 seeds.

| topology | b | burst CV | autocorrelation peak | period (ticks) | module E_norm |
|---|---|---|---|---|---|
| hier | 0 / 0.1 / 0.3 | 1.28 / 1.57 / 1.34 | 0.57 / 0.52 / **0.79** | 128 / 82 / 150 | 0.95 |
| ER | 0 / 0.1 / 0.3 | 1.63 / 1.65 / 1.71 | 0.60 / 0.72 / **0.77** | 165 / 163 / 168 | 0.00 |

- Even without adaptation the population activity has a **slow quasi-periodic envelope** (autocorrelation peak ≈ 0.6 at
  ~130–165 ticks) — the uncertainty aging/resolution cycle (A1) acting collectively — while burst *onsets* stay irregular
  (CV > 1). "Irregular initiative" (CV) and "no internal clock" are not the same property.
- Strong adaptation deepens that slow rhythm (peak → 0.77–0.79) without changing sub-agent structure. Combined with A36
  (slow rhythms are the most entraining), adaptation/boredom currents are a route to an **internal slow scheduler**; audits
  should report the envelope autocorrelation, not only ISI CV.

## Tick 131 — internal rhythm of the prototype engine (`../eia_prototype/tick131_prototype_envelope.py`)

TargetEngine, fixed tension 0.5, 20 000 steps, total activity (10-step smoothing); 3 seeds.

| engine | burst CV | autocorrelation peak | period (engine steps) |
|---|---|---|---|
| v3 (gain 0.4, μ 0.15) | 1.08 | 0.56 | ~30 |
| near-critical (gain 1.0) | 1.14 | **0.97** | ~28 |

- The near-critical engine is effectively an **oscillator** (autocorrelation 0.97 at ~28 steps) — an internal clock hidden
  behind a CV > 1. The subcritical v3 choice (C12) roughly halves this (0.56): another reason to run motives below
  criticality.
- The residual ~30-step rhythm is shorter than one cognition tick (40 inner steps; readout averages 20), so at pipeline
  level it is mostly averaged out — but a different `inner_steps` could alias it into a visible periodicity. Keep
  inner_steps not near a multiple of ~30, or randomise it.

## Tick 132 — aliasing check of the patched engine (inline, on `combined_all.patch` applied to a HEAD copy)

`PopulationDrives` in silence (one categorical belief 0.6/0.4), 550 cognition ticks, epistemic intensity autocorrelation
across ticks; 3 seeds.

| inner_steps | lag-1 autocorrelation | largest |ac| at lags 2–20 |
|---|---|---|
| 30 | −0.13 | 0.05 |
| 40 (default) | −0.09 | 0.05 |
| 60 | 0.00 | 0.05 |

- **No aliasing** at the cognition-tick level for any tested setting: the ~30-step internal rhythm (C16) averages out;
  intensities are nearly uncorrelated tick to tick (slight negative lag-1 from refractoriness). The C16 caution is
  theoretical for the default configuration.

## Tick 133 — PAI-EI-E0-001 baseline matrix with the causal gate (`../eia_prototype/tick133_matrix_causal.py`, run on a patched copy)

6 scenarios (twin_world_001 + evals 002–006), seed 100; AuthenticReason class 'endogenous' with the lexical gate vs D1.

| baseline | endogenous, lexical | endogenous, causal (D1) | causal origin of the initiative |
|---|---|---|---|
| reactive_only | 0/6 | 0/6 | abstain / stub 6 |
| scheduled_stub | 4/6 | 4/6 | memory 4, field 1, none 1 |
| event_rule | 5/6 | 5/6 | memory 5, field 1 |
| predictive_p3 | 0/6 | **2/6** | drive-independent 3, field 2, none 1 |
| full_eia | 6/6 | 6/6 | memory 5, field 1 |

- **Neither gate separates full_eia from the scheduled / event-rule stubs** (4–6/6 'endogenous' for all three) — in MVP-0 the
  G2 separation comes from EUIR/contact criteria, not from AuthenticReason's class. The drive-attribution origins of
  full_eia and event_rule are identical (memory 5, field 1): these stubs reuse the same drive → intention path.
- **D1 changes one baseline**: predictive_p3 goes from 0/6 to 2/6 'endogenous' — its initiatives are field-driven through the
  drive channel, so the causal structural test passes where the keyword test failed. D1 is more honest about *drive causation*
  but, alone, would weaken the P3 separation; it should be combined with the EOI/twin criterion (already in the class rule)
  and an exogeneity check on the *inputs* of the drive channel.
- Recommendation added to D1: report origin + Shapley per run, but do not let a causal drive path by itself upgrade a
  predictive-P3 initiative to 'endogenous'.

## Tick 134 — D1 fix: audit only the engine that produced the motivation

The P3 stub builds its own Motivation without `loop.drives`, but D1 recomputed counterfactuals on `loop.drives` — it audited
an engine that did not produce the initiative (source of tick 133's 0/6 → 2/6). Fix in the draft patches: P3 / reactive
stubs are not audited through the drive engine (`origin = not_from_drive_engine`, structural False); new test.
Re-verified: combined patch applies to HEAD, full suite **308 passed / 6 pre-existing failures**; PAI-EI-E0-001 with the
causal gate now gives P3 **0/6** (as the lexical gate), all other baselines unchanged. C17's P3 caveat resolved; its main
point (no gate separates full_eia from scheduled/event-rule stubs) stands.

## Tick 135 — proposal D10 (reasoning): multi-episode timing audit as the missing baseline discriminator

## Tick 136 — D10 tested: multi-episode timing audit (`../eia_prototype/tick136_timing_audit.py`)

200 silent episodes, 7 scenarios × 3 seeds, same harness.

| policy | initiatives / 200 | ISI CV | longest same-question run | lag-5 autocorrelation |
|---|---|---|---|---|
| scheduled (every 5th) | 39.6 | **0.07** (clock) | 1.0 | **0.97** |
| event_rule | **199.7** | 0.00 | **199.7** (perseveration) | 0.00 |
| full_eia (current MVP-0) | **199.6** | 0.03 | **199.4** | 0.00 |
| full_eia v3 (tick 114) | 3.6 | **1.08** | 1.05 | — |

- The timing audit cleanly separates **scheduled** (clock: CV ≈ 0, lag-5 autocorrelation 0.97) from both others — D10 works
  against scheduler confounds.
- But **current full_eia is indistinguishable from the event-rule stub** even over 200 episodes: both fire every episode on
  the same question. Under silence the MVP-0 full pipeline *behaves as* an event rule (C9) — neither a single-episode nor a
  multi-episode audit can separate them, because they are the same policy in silence.
- Only **v3** has a distinct timing signature (sparse, irregular, no perseveration). So D10 is a valid discriminator, and it
  shows that the separation "full_eia ≠ event rule" is currently not realised in silence — it becomes real with the
  closed loop + state-IOR + population drives.

## Tick 139 — blind sub-agent detection under delays (`tick139.py`)

SBM 10×100 (μ 0.1); random per-edge delays 0–9 ticks vs none; Louvain on the inferred graph with the best resolution per
detector (upper bound); ARI vs true modules; 2 seeds.

| delays | lag-1 conditional detector | multi-lag detector (lags 1–10) |
|---|---|---|
| none | **0.82** | 0.34 |
| 0–9 ticks | 0.08 | **0.58** |

- **Detector lag must match the system's lags**: with delays the lag-1 detector collapses (0.82 → 0.08) while a multi-lag
  detector still recovers the modules (0.58); without delays the multi-lag detector is worse (0.34) because summing lags
  blurs the direct cause.
- Practical rule for auditing agents with variable latencies (LLM tool calls, asynchronous modules): estimate the lag
  structure first (or use a lag-selective model, e.g. per-lag regression / transfer entropy with lag search) before blind
  boundary detection. Complements tick 138 (the same mismatch biases E_norm).

## Tick 140 — lag-selective blind detector (`tick140.py`)

Per ordered pair, the lag (1–10) with the largest lagged excess; per target, regression on the top-20 candidates each at its
own best lag; Louvain (best resolution); 2 seeds.

| delays | lag-1 | summed multi-lag | **lag-selective** |
|---|---|---|---|
| none | 0.82 | 0.34 | **0.78** |
| 0–9 ticks | 0.08 | 0.58 | **0.73** |

- The lag-selective detector is **robust to unknown delays**: near-optimal without delays (0.78 vs 0.82) and best with them
  (0.73). Recommended default for blind sub-agent detection on real agent logs / neural data with unknown latencies.

## Queue (next ticks)
- [ ] implement proposal D1 (causal structural gate) as a patch in src/ with tests — needs user go-ahead (touches production audit)
- [x] tick 36: calibrated re-score — brain functional boundaries (0.68), model anatomical (hemispheres 0.37); see ../human_connectome/RESULTS.md
- [x] tick 37: consensus gating triples functional boundaries (held-out) but leaves hemispheric boundary (0.28 vs emp 0.05)
- [x] tick 38: homotopic h≈0.05 dissolves hemispheric boundary to empirical level; gate+homotopic reproduces EIA-map profile (B8)
- [x] tick 39: empirical boundaries degenerate (split-half ARI 0.09, each E_norm ≈ 0.45); 0.68 was inflated (B9)
- [x] tick 40: metastable gating (dwell ~120 s) reproduces degenerate boundaries; fixed does not (B10)
- [x] tick 41: metastable decomposition in engine — weak/inconclusive (richer repertoire, no control gain)
- [ ] integrate findings into EIA DriveEngine prototype (modular drive graph + lateral inhibition + aging/noise)
- [ ] (optional) better blind attribution: conditional lagged excess / surrogates
- [x] tick 14: boundary detector on human-connectome Hopf model → no anatomical self-boundaries, ER-like (see ../human_connectome/RESULTS.md)
- [x] tick 15: empirical rs-fMRI HAS functional self-boundaries (sensory / DMN+value / BG+SMA / FPN; ARI with EIA map up to 0.40) that the Hopf model lacks — see ../human_connectome/RESULTS.md
- [x] tick 16: block-wise a_k / frequency detuning do NOT reproduce empirical boundaries (≈ shuffled null) — see ../human_connectome/RESULTS.md
- [x] tick 17: HRF lag (≤2 s) + SNR (≤3×) do NOT fake boundaries → empirical boundaries likely genuine
- [x] tick 18: block gating (g_in 3, g_out 0.03) reproduces empirical boundaries + E gain; empirical blocks are SC-compatible (easier to impose than random)
- [x] tick 19: gating doubles FC fit (0.23→0.49); intermittent gate no shortcut (tonic property)
- [x] tick 20: cross-subject — boundaries transfer partially (ARI 0.19), FC gain does NOT (withdrawn)
- [x] tick 21: LOO consensus blocks predict held-out subject's boundaries (ARI 0.17, 4/4 folds); human line summarised in ../human_connectome/RESULTS.md
- [ ] back to toy: hyperbolic / p-adic tree; directed + inhibition
- [ ] hyperbolic / p-adic tree (Kairologos link)
- [ ] directed graphs, inhibition (E/I balance)
- [ ] hyperbolic / p-adic tree (Kairologos link)
- [ ] directed graphs, inhibition (E/I balance)
- [ ] hyperbolic / p-adic tree (Kairologos link)
- [ ] directed graphs (feed-forward vs recurrent motifs), Dale-like inhibition
- [ ] metric: Hawkes branching ratio via proper fit; Lempel–Ziv complexity of pattern
- [ ] replace aging clock with stochastic aging (Poisson staleness) — does the clock disappear?
- [ ] do(Z) test: perturb one module, measure trajectory divergence (E_endo cond. 4)
