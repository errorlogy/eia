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

## Queue (next ticks)
- [ ] (optional) better blind attribution: conditional lagged excess / surrogates
- [x] tick 14: boundary detector on human-connectome Hopf model → no anatomical self-boundaries, ER-like (see ../human_connectome/RESULTS.md)
- [x] tick 15: empirical rs-fMRI HAS functional self-boundaries (sensory / DMN+value / BG+SMA / FPN; ARI with EIA map up to 0.40) that the Hopf model lacks — see ../human_connectome/RESULTS.md
- [x] tick 16: block-wise a_k / frequency detuning do NOT reproduce empirical boundaries (≈ shuffled null) — see ../human_connectome/RESULTS.md
- [x] tick 17: HRF lag (≤2 s) + SNR (≤3×) do NOT fake boundaries → empirical boundaries likely genuine
- [x] tick 18: block gating (g_in 3, g_out 0.03) reproduces empirical boundaries + E gain; empirical blocks are SC-compatible (easier to impose than random)
- [x] tick 19: gating doubles FC fit (0.23→0.49); intermittent gate no shortcut (tonic property)
- [x] tick 20: cross-subject — boundaries transfer partially (ARI 0.19), FC gain does NOT (withdrawn)
- [ ] consensus blocks from 3 subjects → leave-one-out on the 4th
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
