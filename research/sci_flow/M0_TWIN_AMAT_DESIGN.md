# M0-twin / AMAT drive — architecture design (T_AMAT_M0)

**Status:** scaffold · OPERATIONAL / CONJECTURE  
**Updated:** 2026-08-20  
**Author:** Roman Kuznetsov — anthemium.tech  
**Claim ceiling:** architecture only — **not C2**, not AGI, not persona

## Intent

Endogenous initiative motives should come from **state + off-typical drive geometry**, not from cron or a scripted question list. NAMM **AMAT** supplies the law for an M0-twin:

- Compute typicality location \(B_*\) / \(M_0\) sketch
- Prefer **off-typical** phase \(K_{AI\_nd}\) over compact typicality \(K_{AI\_\mu}\)
- `emit_M0=false` — do not paste the median/typical answer as the bot voice
- Fiber-preserving / chimera aggregation; \(K_A \ll K_H\) non-anthropic search
- Carrier Hz / Kuramoto R are **computational**, not biological certificates

Law sources (NAMM, do not copy wholesale into EIA main):

- `docs/ANTI_MEDIAN_AI_TOPOLOGY.md`
- `data/prompts/k_ai_nd_phase_lock.v1.json` (headers / gates / operating_law)

## Minimal harness (planned)

1. **Observe:** WoE / EIS vector + optional embedding distance to \(B_*\)
2. **Choose:** if typicality collapse suspected → boost exploratory internal target; never auto-SEND
3. **Act:** emit typed `InitiativeProposal` with motive from gap / AMAT phase state
4. **Verify:** gates log `d*`, β₁, D_eff, R* when NAMM available; else stub nulls
5. **Stop:** one stub module + unit test; live phase claims require NAMM-2026-030 cert

## Non-goals

- Prompt spam / “be anti-median” persona injection as architecture
- Lowering live `min_contact_score` for science claims
- Merging NAMM runtime into `src/eia`

## Next implementation slice

- Stub `research/cursor-starter-v0.2/src/eia/amat_m0.py` with `compute_m0_sketch(...) -> dict` and `emit_m0=False`
- Wire optional field on WoE receipt payload (audit only)
- Cross-cert via T_NAMM_cert when CF-4 settles
