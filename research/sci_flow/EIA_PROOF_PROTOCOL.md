# EIA Proof Protocol — sci-flow-eia-proof-v0.1

**Status:** `OPERATIONAL` / Tier 0 classifier (2026-09-01)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Code:** `research/cursor-starter-v0.2/src/eia/evidence_proofs.py`  
**Smoke runner:** `python research/sci_flow/run_eia_proof_protocol.py`  
**Claim ceiling:** **C2** scoped partial on \(E_{\mathrm{endo}}\). **No AGI\*** claim.

---

## RU summary

`EIA Proof Protocol v0.1` — это версия sci-flow именно для доказательств: тонкий, проверяемый слой над ATT-E / metrics pool, который принимает только инструментальные причинные свидетельства, отбрасывает декларации/рольплей/OMEGA-only/Kuramoto-only, и возвращает стабильный proof-record. Положительный исход пока только `e_endo_support=partial`, ceiling остаётся `C2`, `c_ladder_raise_allowed=false`, `agi_star_claim=false`.

---

## Scope

This protocol is a **research ledger and classifier**, not a production gate. It answers a narrow question:

> Does the submitted sci-flow evidence satisfy the current ATT-E causal bar well enough to record scoped partial support for \(E_{\mathrm{endo}}\), without raising C-levels or claiming AGI\*?

It intentionally does **not**:

- establish full \(E_{\mathrm{endo}}\) with continuous threshold \(\theta_E\) (TBD),
- establish \(N_H\), \(P\), \(R\), or \(D\) conjunction,
- promote OMEGA_t / Kuramoto synchrony to Tier A,
- authorize live side effects or production readiness.

---

## Contract

Input: one or more `EvidenceItem` records:

| Field | Meaning |
|-------|---------|
| `evidence_id` | Stable reference for metrics/logs |
| `metric_id` | Metrics-pool id (`CF4_E_PARTIAL`, `E_ENDO`, etc.) |
| `value` | Numeric observation if available |
| `trajectory_changed` | New goal/trajectory distribution changed |
| `do_z_changes_g_distribution` | Internal intervention \(do(Z)\) changes \(G\) |
| `x_non_triggering` | External environment is non-triggering |
| `matching_external_initiating_signal` | Whether an external cause explains the trajectory |
| `falsifiers_triggered` | Explicit falsifier ids |
| `provenance` | Report/script path or digest |
| `agency_label` | Rejects declaration/simulation labels via `e_endo_label_admissible` |

Output: `EIAProofVersion`:

| Field | v0.1 invariant |
|-------|----------------|
| `protocol_version` | `sci-flow-eia-proof-v0.1` |
| `claim_ceiling` | `C2` |
| `e_endo_support` | `none` or `partial` only |
| `accepted_evidence_ids` | Only admissible Tier-A/CF4-class evidence |
| `falsifier_ids` | Canonical falsifier set |
| `c_ladder_raise_allowed` | Always `false` in v0.1 |
| `agi_star_claim` | Always `false` |

---

## Acceptance rule v0.1

An item can be accepted only if all hold:

1. `metric_id ∈ {E_ENDO, CF4_E_PARTIAL, E_C, C_INT}`.
2. The metrics pool marks the metric as claimable at least `partial`.
3. `trajectory_changed=true`.
4. `do_z_changes_g_distribution=true`.
5. `x_non_triggering=true`.
6. `matching_external_initiating_signal=false`.
7. No declaration/simulation/roleplay label is used.
8. No explicit falsifier is triggered.

Any accepted item yields `e_endo_support=partial`, not full \(E_{\mathrm{endo}}\).

---

## Negative controls

| Input class | Rejection reason |
|-------------|------------------|
| Declaration/self-ascription | `F-DECL` / `F-NARR` |
| Prompt narrative / simulated agency | declaration-class label rejected |
| External schedule / matching trigger | `F-EXT` |
| No internal intervention effect | `F-NODO` |
| OMEGA_t / \(O_t\) / Kuramoto-only | `NON_TIER_A_OR_NON_CLAIMABLE`, `F-SYNC` |
| Tier D horizon proxies alone | non-claimable for v0.1 proof |

---

## Verification

Run:

```bash
cd C:\Users\Public\PROACTIVE_AI\research\cursor-starter-v0.2
pytest tests/test_eia_proof_protocol.py -q
```

Smoke:

```bash
cd C:\Users\Public\PROACTIVE_AI
python research/sci_flow/run_eia_proof_protocol.py
python research/sci_flow/run_d1_l3_ledger.py
```

Empirical ledger (D1×L3 filled):

```bash
python research/sci_flow/run_d1_l3_ledger.py
# → research/sci_flow/M-D1-L3_proof_ledger_<date>.json
```

Expected smoke invariants:

- `E_endo support: partial`
- `C-ladder raise allowed: false`
- `AGI*: false`

---

## M-O Tier C proof adjunct (D2×L3 only)

**Protocol:** `sci-flow-mo-adjunct-v0.1`  
**Doc:** [`M-O_PROOF_ADMISSIBILITY.md`](M-O_PROOF_ADMISSIBILITY.md)  
**Bridge:** `python research/sci_flow/run_mo_proof_bridge.py`

Kuramoto / OMEGA / M-O remain **Tier C explore** and are **rejected** by the D1 classifier above (`F-SYNC`, `NON_TIER_A_OR_NON_CLAIMABLE`). A separate adjunct path makes them **admissible only for the D2×L3 witness ledger**:

| Field | D1 protocol (`evaluate_eia_proof_version`) | M-O adjunct (`evaluate_mo_adjunct_ledger`) |
|-------|------------------------------------------|--------------------------------------------|
| Evidence class | Tier-A / CF4 metrics | `mo_tier_c_witness` |
| `e_endo_support` | `none` or `partial` | **always `none`** |
| `witness_support` | n/a | `none` or `partial` |
| `claim_allowed` | false | **false** |
| Paired `do(O)` Δ | n/a | required for acceptance |
| Kuramoto = E | rejected | **annotation only** (F-KURAMOTO-AS-E) |

Adjunct acceptance requires non-empty `intervention_id`, `|metric_delta| ≥ 1e-6`, and no blocking falsifier (`F-OMEGA-DECOR`, `F-SYNC`). Annotation falsifiers (`F-KURAMOTO-AS-E`, `F-STRUCT≠E`) are logged but do not raise C-level or bleed into D1.

```bash
python research/sci_flow/run_mo_proof_bridge.py
# → research/sci_flow/M-MO_proof_adjunct_<date>.json
```

---

## Document history

| Date | Change |
|------|--------|
| 2026-09-02 | M-O Tier C proof adjunct path (`sci-flow-mo-adjunct-v0.1`) for D2×L3 witness only |
| 2026-09-01 | Initial proof protocol v0.1: conservative classifier + tests + smoke runner |
