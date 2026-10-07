# M-OPENAI-MATH-POINTER — Tier C formal-math reference adjunct

**Status:** `REFERENCE` / pointer only (2026-10-07)  
**Protocol:** `sci-flow-external-corpus-v0.1`  
**Upstream submodule:** `research/external/openai-math` → [openai/math](https://github.com/openai/math)  
**Integration doc:** [`docs/INTEGRATION_OPENAI_MATH.md`](../../docs/INTEGRATION_OPENAI_MATH.md)  
**Claim ceiling:** **C2** · **`claim_allowed=false`** · **no AGI\*** · **no `e_endo_support`**

---

## RU summary

Репозиторий OpenAI `math` подключён как **git submodule** (формальная математика и PDF-корпус **вне** доказательной базы EIA). EIA **не** утверждает корректность теорем, Lean-формализаций или рассуждений модели. Использование: навигация по `CONTENTS.md`, сопоставление методологии с Tier C harnesses, будущие **adjunct** сравнения без повышения claim ladder.

---

## Problem statement

EIA sci-flow needs a **stable, license-clear** pointer to contemporary model-generated mathematical literature without:

1. Vendoring ~722 PDFs into `errorlogy/eia` history.
2. Implying that ATT-R, D1 ledger, or C-ladder gates validate upstream proofs.
3. Pulling Lean / PDF trees into default CI or pytest collection.

---

## Evidence class: `external_math_corpus`

| Field | Value |
|-------|-------|
| Cube cell | **none** (out of cube) |
| Tier | **C** |
| `claim_allowed` | **false** (hard) |
| `e_endo_support` | **none** (hard) |
| `witness_support` | **none** |
| `c_ladder_raise_allowed` | **false** |
| `agi_star_claim` | **false** |

---

## What this pointer CAN support

1. **Bibliographic cross-links** from M-* notes to upstream family IDs (e.g. quasi-Riemann family 003).
2. **Methodology contrast** — how EIA records falsifiers vs upstream “reasoning summary” PDFs.
3. **Optional local Lean tooling** — developers init submodule locally; no CI dependency.

---

## What this pointer CANNOT support

- D1×L3 proof ledger entries citing openai/math as verified evidence.
- Statements that EIA “reproduced” or “confirmed” upstream results.
- Raising `active_ceiling` in `research/sci_flow/config.yaml` based on corpus presence alone.

---

## Operator commands

```bash
git submodule update --init --depth 1 research/external/openai-math
# Manuscript index (inside submodule):
#   research/external/openai-math/CONTENTS.md
```

Sparse partial tree: `scripts/fetch_openai_math.sh` (see integration doc).

---

## Falsifiers (meta)

| ID | Condition |
|----|-----------|
| F-EXT-MATH-AS-E | Any harness output treated as proof of an upstream theorem |
| F-EXT-MATH-D1-BLEED | `e_endo_support` or D1 receipt sourced only from openai/math |
| F-EXT-MATH-CI-PULL | CI workflow enables submodule checkout without explicit review |

---

## Changelog

| Date | Note |
|------|------|
| 2026-10-07 | Initial submodule pin `adc7f1241b42e322a6451854ab7e4b4c146bf78a`; pointer created |
