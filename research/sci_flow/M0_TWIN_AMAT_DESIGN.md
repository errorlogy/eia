# M0-twin / AMAT drive — architecture design (T_AMAT_M0)

**Status:** harness shipped · OPERATIONAL / CONJECTURE  
**Updated:** 2026-08-20  
**Author:** Roman Kuznetsov — anthemium.tech  
**Claim ceiling:** architecture only — **not C2**, not AGI, not persona  
**Metrics:** [`M0_TWIN_METRICS_2026-08-20.md`](M0_TWIN_METRICS_2026-08-20.md)

## Intent

Endogenous initiative motives should come from **state + off-typical drive geometry**, not from cron or a scripted question list. NAMM **AMAT** supplies the law for an M0-twin:

- Compute typicality location \(B_*\) / \(M_0\) sketch (median helpful motive)
- Prefer **off-typical** phase \(K_{AI\_nd}\) over compact typicality \(K_{AI\_\mu}\)
- `emit_M0=false` — do not paste the median/typical answer as the bot voice
- Contact / emit only if endogenous Δ vs M0 clears gate; else abstain
- Fiber-preserving / chimera aggregation; \(K_A \ll K_H\) non-anthropic search
- Carrier Hz / Kuramoto R are **computational**, not biological certificates

Law sources (NAMM, do not copy wholesale into EIA main):

- `docs/ANTI_MEDIAN_AI_TOPOLOGY.md`
- `data/prompts/k_ai_nd_phase_lock.v1.json` (headers / gates / operating_law)

## Harness (shipped)

| Mode | Behavior |
|------|----------|
| `off` | Force median M0 motive — falsifier collapse path |
| `on` | Emit twin if Δ gate clears and twin≠M0; else abstain; never emit M0 |
| `audit_only` | Compute sketch; leave default WoE selection unchanged |

API:

- `eia.amat_m0.compute_m0_sketch(...)` → `M0Sketch` (`emit_m0` always False)
- `EndogenousEmergenceSimulator.run(..., m0_twin_mode=M0TwinMode.ON|OFF|AUDIT_ONLY)`
- Batch: `python research/sci_flow/run_m0_twin.py`

## Pre-registered falsifiers

1. **Without M0-twin** → collapse to reactive/median (ASK / collaboration)
2. **With M0-twin** → intents that form differ from M0; `emit_m0=false`
3. Gate miss must **not** fall back to emitting M0

## Non-goals

- Prompt spam / “be anti-median” persona injection as architecture
- Lowering live `min_contact_score` for science claims
- Merging NAMM runtime into `src/eia`
- Claiming C2 / AGI\* / ATT-R pass from this harness alone

## Next implementation slice

- Wire NAMM embedding \(d(h(y), B_*)\) when cert pipeline available (T_NAMM_cert)
- M-E / ATT-G non-catalog novelty batch using `eia.goal_genesis`
- Optional receipt payload field for live audit sketches
