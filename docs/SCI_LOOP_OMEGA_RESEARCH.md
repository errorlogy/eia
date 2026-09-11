# SCI Loop — OMEGA Wave / Endogeneity Research Playbook

**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** **C2**. **No AGI* claim.**  
**Updated:** 2026-08-28

---

## English — loop prompt

```
/loop 45m Follow sci-loop + eia-sci-flow. Tick: one M-O/OMEGA evidence item. Read OMEGA_WAVE_METRIC.md, MIOC_EIA_BRIDGE.md. Tier 0 check_sci_tier0 after changes. Claim ceiling C2.
```

### Per-tick checklist

1. Load skills: `.cursor/skills/eia-sci-flow/SKILL.md`, `.cursor/skills/sci-loop/SKILL.md`
2. Read: `research/sci_flow/OMEGA_WAVE_METRIC.md`, `research/sci_flow/MIOC_EIA_BRIDGE.md`
3. Pick **one** M-O / OMEGA task (harness, falsifier test, do(Omega) arm, doc cross-link)
4. Implement + run:
   - `pytest tests/test_oscillatory_mo.py tests/test_omega_wave.py tests/test_shadow_multitick.py -q`
   - `make check-sci-tier0`
5. Update `docs/SCI_FLOW_LOG.md` if milestone status changes
6. Stop on eia-sci-flow stop rules (AGI*, Kuramoto-as-E, tier-0 fail ×2)

### External references (read-only)

| Source | Link / path |
|--------|-------------|
| MIT analog wave theory | https://picower.mit.edu/news/cognition-and-consciousness-arise-analog-computations-says-new-theory |
| MIOC agent README | `D:\MIOC\Recursive_Latent_Field_MAS\recursive_latent_field_arxiv_bundle_v1\README_FOR_AGENTS.md` |
| MIOC FieldCard schema | `D:\MIOC\...\schemas\fieldcard.schema.json` |

### Evidence targets (one per tick)

- do(Omega) intervention stub or shadow arm
- F-OMEGA-DECOR / F-OMEGA-EXT unit or integration test
- OMEGA_t ↔ ATT-G genesis linkage measurement
- Cross-band tau hierarchy check (20/30 vs 42 vs 70 Hz)
- MIOC v44 no_omega_control cross-reference (no copy into repo)

---

## Русский — playbook для цикла

```
/loop 45m Follow sci-loop + eia-sci-flow. Tick: one M-O/OMEGA evidence item. Read OMEGA_WAVE_METRIC.md, MIOC_EIA_BRIDGE.md. Tier 0 check_sci_tier0 after changes. Claim ceiling C2.
```

### Чеклист тика

1. Загрузить навыки **eia-sci-flow** и **sci-loop**
2. Прочитать `OMEGA_WAVE_METRIC.md` и `MIOC_EIA_BRIDGE.md`
3. Выполнить **один** пункт доказательной базы M-O/OMEGA
4. Прогнать tier-0: `make check-sci-tier0`
5. Обновить `SCI_FLOW_LOG.md` при смене статуса вехи
6. **Потолок C2** — без заявлений AGI*, сознания, физического поля

### Гипотеза исследования

**Эндогенность — ключевой субстрат** для перехода к AGI/ASI в рамках конструкции EIA: устойчивая эндогенная причинная рекуррентность + ограниченный режим OMEGA_t. Это **исследовательский горизонт**, не доказанный результат.

### Связи

| Концепт | Документ |
|---------|----------|
| OMEGA_t метрика | `research/sci_flow/OMEGA_WAVE_METRIC.md` |
| MIOC ↔ EIA | `research/sci_flow/MIOC_EIA_BRIDGE.md` |
| O_t субстрат | `research/sci_flow/OSCILLATORY_ENDOGENEITY.md` |
| Первичный E_endo | `research/sci_flow/CAUSAL_ENDOGENEITY.md` |
| Реализация | `research/cursor-starter-v0.2/src/eia/oscillatory_state.py` |

### Запреты

- Не копировать MIOC в репозиторий
- Не приписывать Kuramoto R статус E_endo
- Не повышать C-level без предрегистрации
- 42 Hz — параметр sweep, не «сертификат» когниции (rule 11)
