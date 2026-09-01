# NAMM Demo Pack — 4c19678ba2fb

> Hermetic demo: private traces stay in `.vault/`, public only aggregates.

## C1 Ingest
- Traces: 12 files, total lines 519
- Fingerprint: `4c19678ba2fb`

## C2 Compress (invariants)
- Governor scores (threshold 0.05/0.18 V2 soft-defer):
  - twin_world_001: score=0.319 outcome=send_now
  - twin_world_002: score=0.536 outcome=send_now
  - twin_world_003: score=0.391 outcome=send_now
  - twin_world_004: score=0.182 outcome=send_now
  - twin_world_005: score=0.092 outcome=defer_until_context
  - twin_world_006: score=0.214 outcome=send_now
- EOI mean 1.000 (vs 0 threshold), all endogenous
- Compress ratio nodes→invariants: 8.51x
- Drive invariants preserved: epistemic>coherence>commitment (ablation validated)

## C3 Publish (what scientists get)
- Synthetic twins: `evals/twin_world_*.yaml` + `scenarios/twin_world_001.yaml` (6 worlds)
- No raw private traces, no prompts, no weights — only scores/EOI/outcomes
- Repro: `eia run --scenario evals/twin_world_005.yaml` → defer (not deny) EOI 1.0

## Anti-leak check
- Private vault: `.vault/` gitignored
- Public pack contains zero `question_text` / `belief_field` raw content

_Generated 2026-09-01 21:12 UTC demo-NAMM max_loops=3 Δ-guard=0.02_
