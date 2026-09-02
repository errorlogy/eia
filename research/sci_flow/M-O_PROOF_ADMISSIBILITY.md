# M-O Proof Admissibility — Tier C D2×L3 Witness Path

**Status:** `OPERATIONAL` / adjunct classifier (2026-09-02)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Protocol:** `sci-flow-mo-adjunct-v0.1`  
**Code:** `research/cursor-starter-v0.2/src/eia/evidence_proofs.py`  
**Bridge:** `research/sci_flow/run_mo_proof_bridge.py`  
**Claim ceiling:** **C2** · **`claim_allowed=false`** · **no AGI\***

---

## RU summary

Kuramoto / OMEGA / M-O остаются **Tier C explore** и **не** допускаются в D1 proof ledger (`e_endo_support`, C-ladder). Новый путь **`mo_tier_c_witness`** делает M-O **допустимым только для D2×L3 witness ledger**: парные `do(O)` руки с измеримым Δ метрики под фальсификаторами. Это **не** повышение до Tier A и **не** доказательство \(E_{\mathrm{endo}}\).

---

## Problem statement

До этого протокола:

| Input | D1×L3 (`evaluate_eia_proof_version`) | D2×L2 explore |
|-------|--------------------------------------|---------------|
| `OMEGA_T`, `KURAMOTO_R`, `O_T` | **Rejected** (`F-SYNC`, `NON_TIER_A_OR_NON_CLAIMABLE`) | Allowed as explore |
| Paired `do(O)` metric delta | No ledger slot | Harness only (`run_mo_do_o_arms.py`) |

M-O имел harness и метрики, но **не было формального admissibility path** для proof-protocol witness receipts на D2×L3.

---

## Evidence class: `mo_tier_c_witness`

Alias: `d2_explore_adjunct` (same semantics; canonical id in code: `mo_tier_c_witness`).

| Field | Value |
|-------|-------|
| Cube cell | **D2×L3** only |
| Tier | **C** |
| `claim_allowed` | **false** (hard) |
| `e_endo_support` | **none** (hard; no D1 bleed) |
| `witness_support` | `none` or `partial` |
| `c_ladder_raise_allowed` | **false** |
| `agi_star_claim` | **false** |

---

## What M-O CAN contribute

1. **Paired `do(O)` witness receipts** — baseline vs intervention metric deltas under:
   - `do_o_neuraxon_plasticity_off`
   - `do_o_graphitti_growth_off` (stub when binary unavailable)
   - native `oscillatory_state.py` crosswalk (reference arm, not intervention witness)
2. **OmegaWaveState channel summary** — `phase_coherence`, `cadence`, `synchrony`, etc., via `omega_metric()`.
3. **Annotation falsifiers** — e.g. `F-KURAMOTO-AS-E` when \(R \ge 0.85\); logged, not blocking if Δ exists under `do(O)`.
4. **D2×L3 ledger JSON** — `M-MO_proof_adjunct_<date>.json` via `evaluate_mo_adjunct_ledger()`.

---

## What M-O CANNOT contribute

| Blocked claim | Reason |
|---------------|--------|
| `e_endo_support=partial` | Requires Tier-A metrics + `do(Z)` bar (D1 protocol) |
| C-ladder raise | Hard false in adjunct protocol |
| `claim_allowed=true` | Metrics pool marks OMEGA/Kuramoto `claim_allowed=false` |
| Kuramoto \(R\) = \(E_{\mathrm{endo}}\) | **F-KURAMOTO-AS-E** hard ban |
| OMEGA decorative (no Δ under `do(O)`) | **F-OMEGA-DECOR** blocks witness |
| Sync-only without intervention | **F-SYNC** blocks witness |
| Structural growth alone = E | **F-STRUCT≠E** annotation; not E proof |
| AGI\* / \(\tau_{AGI}\) | Hard false |

---

## Admissibility rules (`sci-flow-mo-adjunct-v0.1`)

An `MOAdjunctEvidenceItem` is **accepted** into the D2×L3 witness ledger only if **all** hold:

1. `evidence_class == mo_tier_c_witness`
2. `metric_id ∈ {OMEGA_T, O_T, KURAMOTO_R, MO_STRUCTURAL_DELTA, MO_W_FAST_DRIFT}`
3. `intervention_id` is non-empty (paired `do(O)` arm)
4. `|metric_delta| ≥ 1e-6` vs baseline
5. No **blocking** falsifier in `falsifiers_triggered`:
   - `F-OMEGA-DECOR` — zero OMEGA delta under intervention
   - `F-SYNC` — sync-only / no intervention
6. Annotation falsifiers (`F-KURAMOTO-AS-E`, `F-STRUCT≠E`) are recorded but do **not** auto-reject when (3–5) pass.

Positive outcome: `witness_support=partial` with `accepted_evidence_ids` populated.  
**Never** changes D1 `e_endo_support`.

---

## Active falsifiers

| ID | Role | Effect on adjunct |
|----|------|-------------------|
| **F-KURAMOTO-AS-E** | Kuramoto \(R\) ≠ \(E_{\mathrm{endo}}\) | Annotation when \(R \ge 0.85\) |
| **F-OMEGA-DECOR** | OMEGA without causal Δ | **Blocks** witness if \|Δ\| ≈ 0 |
| **F-SYNC** | Sync-only evidence | **Blocks** if no intervention or zero Δ |
| **F-STRUCT≠E** | Growth ≠ endogeneity | Annotation when structural events > 0 |

Cross-ref: [`M-O_NEURAXON_GRAPHITTI_ENDOGENEITY.md`](M-O_NEURAXON_GRAPHITTI_ENDOGENEITY.md), [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md).

---

## Bridge harness

```
run_mo_do_o_arms.py
    → M-MO_do_o_arms_2026-09-02.json
run_mo_proof_bridge.py
    → build_mo_adjunct_evidence_from_arms_payload()
    → evaluate_mo_adjunct_ledger()
    → M-MO_proof_adjunct_2026-09-02.json + .md
run_mo_shadow_bridge.py
    → Neuraxon O_t → OmegaWaveState → shadow multitick
    → ATT-R scorecard compare vs native shadow
    → M-MO_shadow_bridge_2026-09-02.json + .md
```

Arms compared:

| Arm | Role |
|-----|------|
| `neuraxon_baseline` | Baseline for paired Δ |
| `do_o_neuraxon_plasticity_off` | Primary `do(O)` witness |
| `do_o_graphitti_growth_off` | Structural stub (Tier C) |
| `native_oscillatory_state` | OmegaWaveState reference |

---

## 3D cube placement

| Cell | M-O role |
|------|----------|
| D2×L1 | Falsifier invariants (F-KURAMOTO-AS-E, F-OMEGA-DECOR, F-SYNC, F-STRUCT≠E) |
| D2×L2 | Harness + paired arms (`run_mo_do_o_arms.py`) |
| D2×L3 | **Proof adjunct ledger** (`run_mo_proof_bridge.py`) — **new admissible path** |

D1×L3 remains CF-4 + D01 only (`evaluate_eia_proof_version`).

---

## Verification

```bash
cd C:\Users\Public\PROACTIVE_AI
python research/sci_flow/run_mo_proof_bridge.py
pytest tests/test_mo_proof_bridge.py -q
make check-sci-tier0
```

Expected invariants:

- `witness_support=partial` (when paired Δ present)
- `e_endo_support=none`
- `claim_allowed=false`
- `c_ladder_raise_allowed=false`

---

## Document history

| Date | Change |
|------|--------|
| 2026-09-02 | Initial M-O proof adjunct admissibility path + bridge harness |
