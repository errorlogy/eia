# D3 Boundary Witness — sci-flow boundary layer (C2 ceiling)

**Status:** `OPERATIONAL` Tier B soft witness (2026-09-01)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Harness:** `research/sci_flow/boundary_witness_harness.py`  
**Express cell:** D3×L3 in `run_3d_express.py`  
**Claim ceiling:** **C2** — `claim_allowed=false`, **no strong \(N_H\)**, **not AGI\***

---

## RU summary

**D3×L3 boundary witness** — измеряемые квитанции граничного слоя (governor, фальсификаторы, ATT-N explore, NAMM soft) при потолке **C2**. Это **не** доказательство сильного \(N_H\) и **не** AGI\*. NAMM intent corpus — только **Tier B soft witness**.

---

## What \(N_H\) witness means at C2 scope

At C2 we record **instrumented boundary receipts**, not non-embeddability certificates:

| Witness class | Tier | Meaning |
|---------------|------|---------|
| Falsifier registry links | A (structural) | `intervention_cube` D3 entries + `CAUSAL_ENDOGENEITY.md` taxonomy (F-DECL, F-NARR, F-EXT, F-NODO) |
| Governor gate smoke | A (structural) | `ContactGovernor` rejects low-value contact; CF-7 `do_z_governor_isolation` registered |
| ATT-N explore batch | B (metric) | `run_att_n_batch` under budget \(B\); `n_h_claim=false`, `claim_allowed=false` |
| NAMM intent corpus | B (soft) | `traces/namm_intents/*.json` hook receipts — opacity / topology hooks, **not** \(N_H\) proof |

**Hard bans (unchanged):**

- No `n_h_claim=true` from this harness
- No C-ladder raise from ATT-N explore or NAMM hooks alone
- Opacity / compression asymmetry ≠ strong \(N_H\)

Full \(N_H\) conjunction remains per [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md) — unmeasured at C2.

---

## Measurable checks

```bash
python research/sci_flow/run_boundary_witness.py
python research/sci_flow/run_3d_express.py   # includes D3×L3 cell
```

Pass (D3×L3 express cell): falsifier registry + governor gate + ATT-N smoke all `ok`; NAMM soft witness annotates tier (`B_soft_NH` vs `B_partial`).

---

## Cross-links

| Doc / code | Role |
|------------|------|
| [`intervention_cube.py`](../cursor-starter-v0.2/src/eia/intervention_cube.py) | D3 `do(Z)` / `do(X)` falsifier registry |
| [`non_embeddability.py`](../cursor-starter-v0.2/src/eia/non_embeddability.py) | ATT-N explore under budget \(B\) |
| [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) | F-DECL / F-NARR / F-EXT / F-NODO bar |
| [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md) | Full boundary conjunction (not claimed) |
