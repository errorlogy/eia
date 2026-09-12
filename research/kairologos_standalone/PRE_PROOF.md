# PRE_PROOF — операционные леммы / operational lemmas

> **Не формальное доказательство.** «Предварительно-доказательно» здесь означает:  
> **гипотеза → скрипт → порог pass/fail → JSON-артефакт**.  
> Это эмпирические леммы, не QED и не claim ladder EIA.

---

## Что мы называем «pre-proof»

| Элемент | Смысл |
|---------|--------|
| **Lemma** | Проверяемое утверждение о представлении или динамике |
| **Hypothesis** | Что именно должно наблюдаться |
| **Experiment** | Python harness в `harnesses/` |
| **Threshold** | Числовой критерий pass/fail (задан заранее) |
| **Artifact** | `artifacts/PRE_PROOF_YYYY-MM-DD.json` |

Запуск всей батареи:

```powershell
python research/kairologos_standalone/run_all_preproof.py
```

---

## Таблица лемм

| Lemma ID | Claim (RU) | Claim (EN) | Test | Harness | Pass threshold |
|----------|------------|------------|------|---------|----------------|
| **L-TOPO-1** | Топо-кодировка устойчивее к перестановке имён узлов, чем линейный shuffle токенов | Topo encoding has lower semantic drift under node permutation than linear token shuffle | HDC cosine после shuffle | T-KAI-08 | topo mean sim ≥ linear + 0.1; ≥4/5 tasks |
| **L-TOPO-2** | Замкнутая геодезика сохраняет массу активации лучше линейного re-entry | Closed geodesic preserves activation mass better than linear re-entry | L2 norm после 3 проходов | `lemma_battery` | loop retention > linear + 0.05 |
| **L-TOPO-3** | Braid-crossing различает ветвь и merge по паттерну активации | Braid crossing encodes conditional branch distinguishable from path merge | cosine separation финальных векторов | `lemma_battery` | separation > 0.15 для всех пар |
| **L-TOPO-4** | p-адическая ультраметрика отражает иерархию программы | Ultrametric (p-adic) clustering matches hierarchical program structure | p-adic distance parent/child vs unrelated | T-KAI-06 ext | mean(parent-child) < mean(unrelated) |
| **L-MAT-1** | QK^T (rank-1D pairwise) и HDC binding (ND superposition) — разные профили устойчивости | LLM attention QK^T vs HDC binding — different stability under noise | cosine под шумом 0–0.2 | T-KAI-09 | профили различаются (не тождественны) |
| **L-MAT-2** | Слой трансформера (matmul chain) vs topo step (Laplacian + phase) | Transformer layer = matmul sequence; topo step = graph diffusion + phase coupling | 8-node task, impulse-noise output drift | T-KAI-09 | diffusion sim ≥ attention + 0.02 |

---

## Связь с экспериментами T-KAI

| T-KAI | Леммы | Статус |
|-------|-------|--------|
| T-KAI-08 | L-TOPO-1 | operational |
| T-KAI-09 | L-MAT-1, L-MAT-2 | operational |
| T-KAI-10 | ND quasi-orthogonality (supporting) | operational |
| T-KAI-06 | L-TOPO-4 (base ultrametric) | operational |

---

## Интерпретация (честно)

- **Pass** означает: в нашей toy-модели порог выполнен. Не «доказано для всех программ».
- **Fail** не опровергает теорию целиком — возможно, порог слишком жёсткий или модель слишком грубая.
- Высокая HDC shuffle-similarity для topo **не** означает AGI или сознание.
- Мы **не** утверждаем, что трансформеры «неправильны» — только что 1D-индексная бутылочная горлышко релевантна для дискурса AGI.

---

## Артефакты

После `run_all_preproof.py`:

- `artifacts/T-KAI-08_*.json`
- `artifacts/T-KAI-09_*.json`
- `artifacts/T-KAI-10_*.json`
- `artifacts/PRE_PROOF_*.json` — сводная таблица лемм
