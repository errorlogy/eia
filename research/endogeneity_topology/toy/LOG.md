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
