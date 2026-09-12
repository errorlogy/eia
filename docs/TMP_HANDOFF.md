# TMP Handoff / Передача исследований Topological Manifold Programming

**Decision date:** 2026-09-12  
**Дата решения:** 2026-09-12

---

## New canonical home / Новый канонический дом

`C:\Users\Public\Topological_Manifold_Programming`

All future **Topological Manifold Programming (TMP)** work — Kairologos lineage, TopoLang, pre-proof lemmas, visualization, and eventually the quick-galileo TopoMatrix stack — continues in a **separate Cursor workspace** and (when ready) a **private GitHub repository** created from that folder.

Вся дальнейшая работа по **Topological Manifold Programming (TMP)** — линия Kairologos, TopoLang, pre-proof леммы, визуализация и в перспективе стек TopoMatrix из quick-galileo — продолжается в **отдельном окне Cursor** и (когда будет готово) в **приватном GitHub-репозитории**, созданном из этой папки.

---

## PROACTIVE_AI strand status / Статус ветки в PROACTIVE_AI

| Item | Value |
|------|-------|
| Folder | `research/kairologos_standalone/` |
| Branch | `research/kairologos-standalone` |
| TMP status | **Frozen for TMP purposes** — no new TMP claims, experiments, or merges here |
| Rationale | PROACTIVE_AI remains the home for **EIA / Brain-AI / Agent-EIA** research |

Папка `kairologos_standalone` на ветке `research/kairologos-standalone` **заморожена для целей TMP**. Новые TMP-эксперименты и утверждения ведутся только в `Topological_Manifold_Programming`.

---

## What stays in PROACTIVE_AI / Что остаётся в PROACTIVE_AI

These strands are **not** merged with TMP theory claims:

- **EIA** — claim ladder, falsifiers, proof mechanics
- **Brain-AI** — connectome / trajectory research under `research/brain_ai/`
- **Agent-EIA** — agent harnesses scoped to EIA
- **`research/kairologos_experiments/`** — EIA Tier C battery (`claim_allowed=false`)

**No merge of TMP claims into EIA.** TMP and EIA remain explicitly separated research programs.

В PROACTIVE_AI остаются EIA, Brain-AI, Agent-EIA и kairologos_experiments (EIA-scoped). **Слияния TMP-утверждений в EIA не будет.**

---

## What migrates to TMP / Что переносится в TMP

| Component | Source (current) | Notes |
|-----------|------------------|-------|
| `topo_lang/` | `research/kairologos_standalone/topo_lang/` | `.topo` parser, interpreter, examples |
| Pre-proof | `PRE_PROOF.md`, `run_all_preproof.py`, `harnesses/lemma_battery.py` | Operational lemmas L-TOPO-* / L-MAT-* |
| Visualization | `viz/`, T-KAI-11 | Three.js TopoLang viewer, export pipeline |
| Theory docs | `TOPOLOGICAL_CODE_SYNTAX.md`, `LLM_MATRIX_BRIDGE.md` | Paradigm and LLM bridge |
| Harnesses T-KAI-* | `harnesses/`, `run_t_kai_*.py` | Native Kairologos experiments (not EIA) |
| TopoMatrix stack | `quick-galileo` (eventually) | `topomatrix_core.py`, HoTT/VSA layers |

---

## Source references / Исходные ссылки

| Resource | Path |
|----------|------|
| quick-galileo demos | `C:\Users\lawye\Documents\antigravity\quick-galileo\` |
| Frozen snapshot (PROACTIVE_AI) | `PROACTIVE_AI/research/kairologos_standalone/` on branch `research/kairologos-standalone` |
| Canonical theory tractate | `c:\Users\lawye\.gemini\antigravity\brain\f72138c9-dd57-4d05-91f8-3ef112ab55fb\THEORY_OF_TOPOLOGICAL_ASI_RESONANCE.md` |
| TMP workspace (new) | `C:\Users\Public\Topological_Manifold_Programming\` |

---

## Next steps (new Cursor window) / Следующие шаги

1. **Open folder** in Cursor: `C:\Users\Public\Topological_Manifold_Programming`
2. **Ask the agent:**
   > Create a private GitHub repo named `Topological_Manifold_Programming`, initialize git, and scaffold the project structure. Port core modules from `research/kairologos_standalone` (topo_lang, pre-proof, viz) and reference implementations from `quick-galileo`. Do not merge EIA claims.
3. **Port incrementally** — start with docs + `topo_lang` + pre-proof harnesses; add TopoMatrix from quick-galileo when the base repo is stable.

---

## Related files in this repo

- `research/kairologos_standalone/README.md` — points here and to the TMP path
- `research/kairologos_standalone/RESEARCH_PROGRAM.md` — frozen T-KAI-01..11 roadmap (historical)
