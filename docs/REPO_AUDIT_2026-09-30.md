# Аудит репозитория EIA — локально и на GitHub (2026-09-30)

**Update (2026-09-30, post-hygiene):** [PR #2](https://github.com/errorlogy/eia/pull/2) merged; `main` CI green at `c392eb2`. Quick wins: README table, `docs/INDEX.md`, `RESEARCH_BRANCHES.md`, CONTRIBUTING install extras, GitHub Release `sci-flow-v0.3`, K-KUR-02 test aligned with CI (no Brian2).

> **Для Cursor:** это рабочий документ. Раздел 6 — упорядоченный список задач с командами и критериями приёмки.
> Задачи с пометкой **[решение владельца]** не выполнять без явного согласия (они трогают `src/`, историю git,
> лицензию или публикацию).
> Граница заявлений прежняя: **C2**, `claim_allowed=false`, никаких AGI*-утверждений.

---

## 0. Срочно: состояние рабочего дерева

1. **В одном рабочем дереве работают несколько агентов** (Claude Code CLI и агент Cursor). Во время аудита второй агент
   создал ветку `fix/ci-vendor-skips` (`14ca0e1`) и коммит `0d3fad1` на `research/endogeneity-topology`, пока шли тесты.
   Из-за этого `git stash pop` применил старый stash владельца `stash@{0}` (*tmp-handoff*, ветка kairologos).
   Применение упало на конфликте, **stash сохранён** (`git stash list` — он по-прежнему `stash@{0}`).
2. **Что осталось в дереве:** конфликтный путь `research/kairologos_standalone/README.md` (статус `DU`, *deleted by us*).
   Файл создан самим pop'ом в 09:57; в `HEAD` его нет, копия есть в stash. Исправить вручную:
   ```bash
   git rm --cached research/kairologos_standalone/README.md   # снять конфликт с индекса
   rm research/kairologos_standalone/README.md                  # файл восстановим из stash@{0} при необходимости
   git status                                                   # должно быть чисто
   ```
3. **Правило на будущее:** каждый агент — в своём `git worktree`
   (`git worktree add ../PROACTIVE_AI-topology research/endogeneity-topology`). Никогда не делать `stash pop`
   без проверки `git stash list` до и после.

---

## 1. Снимок состояния

| Слой | Факт |
|---|---|
| GitHub `errorlogy/eia` | публичный, default `main`, 1 звезда, topics нет, 1 PR (merged), issues нет, 107 МБ |
| Releases | только `v0.2.0-mvp0` (Release); `sci-flow-v0.3` существует **только как тег**, хотя README ссылается на него как на релиз |
| CI на `main` | **красный с 2026-09-11** (3 прогона подряд): 6 падений — 5× `ModuleNotFoundError: neuraxon2` (вендор не в main), 1× отсутствует fixture graphitti |
| Фикс CI | локальная ветка `fix/ci-vendor-skips` (`14ca0e1`, skip-маркеры в `tests/conftest.py`) — **не запушена** |
| Локальный `main` | на 1 коммит впереди `origin/main` (`6eb998c` TMP handoff) — **не запушен** |
| `research/endogeneity-topology` | 162 коммита поверх `main`; запушена 2026-09-30; последний локальный коммит `0d3fad1` (второй агент) не запушен |
| Ветки | `main`, `research/cursor-starter-v0.1`, `…v0.2-woe-eis` (отстаёт от main на 23), `brain-ai-connectome` (слита, отстаёт на 5), `kairologos-standalone` (заморожена, TMP ушёл в отдельный репозиторий), `endogeneity-topology`, `docs/sci-flow-v0.3-pointer` (слита) |
| Stash | 5 записей (самая свежая — от 2026-09-12) |
| Код | `src/eia` ≈ 6.5 тыс. строк; `tests/` 40+ файлов; полный прогон ≈ 4 мин |
| Тесты локально | с фиксом skip: **289 passed, 7 skipped**; без него — 6 failed / 290 passed (как в CI) |
| Ruff | `src tests scripts research/sci_flow` — чисто; `research/endogeneity_topology` — 1605 нарушений (плотный стиль исследовательских скриптов: E702/E701/E401) |
| История git | `.git` = 118 МБ; 1865 вендорных файлов (`research/vendor/graphitti`, `neuraxon`: .gpkg до 40 МБ, PDF, PNG) в истории веток v0.2 и brain-ai-connectome |
| Лицензия | GitHub определяет как **"Other"** (текст `LICENSE` нестандартный); CC BY 4.0 применяется и к коду |
| Окружение | в `.venv` нет pytest (есть ruff) — тесты шли через системный Python |

---

## 2. Проблемы репозитория (по приоритету)

### P0 — ломает доверие или воспроизводимость
| # | Проблема | Где | Исправление |
|---|---|---|---|
| R1 | CI на main красный 19 дней | `.github/workflows/eia-ci.yml`, `tests/test_mo_*`, `test_graphitti_witness.py` | запушить `fix/ci-vendor-skips`, открыть PR → main |
| R2 | Сломана строка таблицы в README: в ссылке `[\research/…` превратилось в перевод строки | `README.md` стр. ~9 | заменить на `[research/cursor-starter-v0.2-woe-eis](…)` |
| R3 | Неотправленный коммит main (`6eb998c`) | локальный main | `git push origin main` после R1 |
| R4 | Несколько агентов в одном дереве | весь репозиторий | worktree на агента (см. §0) |

### P1 — гигиена
| # | Проблема | Исправление |
|---|---|---|
| R5 | Вендорные данные (~100 МБ) в истории | вынести в submodule или скрипт `scripts/fetch_vendor.sh`; переписать историю (`git filter-repo`) — **[решение владельца]**, это force-push |
| R6 | `zenodo/proto_agi_horizon_upload.zip` в git, хотя `*.zip` в .gitignore | прикреплять к GitHub Release, из дерева убрать |
| R7 | Мусор в корне: `endogeneity_stack_sim.py`, `.png`, `.csv`; неотслеживаемые `*.zip`, `_extracted/`; и `config/`, и `configs/` | перенести в `research/endogeneity_stack/`, объединить config-каталоги |
| R8 | `docs/` — 40+ файлов, 5 пересекающихся планов (`IMPLEMENTATION_PLAN`, `LOOP_PLAN`, `SCI_FLOW_PLAN`, `PLAN_DELTA`, `ENDOGENEITY_IMPLEMENTATION_PLAN`); `SCI_FLOW_LOG.md` ≈ 2800 строк | `docs/INDEX.md` со статусом каждого файла (active/archived); устаревшее → `docs/archive/`; лог по месяцам |
| R9 | `docs/RESEARCH_BRANCHES.md` знает только 2 ветки из 6 | добавить brain-ai-connectome (слита), kairologos-standalone (заморожена → TMP), endogeneity-topology |
| R10 | `.cursor/rules/eia-sci-flow.mdc` указывает на `research/cursor-starter-v0.2-woe-eis` как на рабочую ветку | обновить; добавить правило для `research/endogeneity_topology/**` |
| R11 | CI не запускается на `research/endogeneity-topology` | добавить ветку в `on.push.branches` или PR-триггер; для `research/endogeneity_topology` — `per-file-ignores` E70x/E401 в `pyproject.toml` |
| R12 | `pyproject` `version = "0.1.0"`, релиз — `v0.2.0` | синхронизировать, `src/eia/version.py` — единственный источник |
| R13 | `sci-flow-v0.3` — только тег | создать GitHub Release с PDF и notes (`docs/SCI_FLOW_RELEASE.md`) |
| R14 | Лицензия "Other"; CC BY 4.0 на код | взять канонический текст CC BY 4.0 или разделить: код — Apache-2.0/MIT, тексты — CC BY 4.0 — **[решение владельца]** |

### P2 — удобство
- Добавить topics на GitHub (`endogenous-agency`, `proactive-ai`, `causal-inference`, `connectome`, `network-science`).
- Разметить медленные тесты `@pytest.mark.slow`; в PR гонять быстрые, полный набор — nightly.
- Разобрать 5 stash-записей (сохранить нужное в ветки `wip/*`, остальное — `git stash drop` — **[решение владельца]**).
- Шаблоны Issues/PR с полем «уровень заявления (C0–C5)».
- `research/endogeneity_topology/toy`: 150 скриптов связаны через `runpy`/импорты друг друга, это хрупко. Выделить
  библиотеку `research/endogeneity_topology/lib/` (simulate, build, E_of, infer_cond, sim_route, discovery),
  а тики превратить в тонкие обёртки или конфиги.

---

## 3. Научное состояние — что уже установлено

Сводка (подробности — `research/endogeneity_topology/FINDINGS.md`, A1–A40, B1–B19, C1–C17, D1–D10):

- **Эндогенность — свойство пары (система, граница)**, а не системы; естественные границы субагентов ищутся вслепую
  (A9–A12).
- **Иерархически-модульная топология** — лучший компромисс: плавное включение, локализация вмешательств, вложенные
  границы, устойчивость к поражениям (сводная таблица топологий в FINDINGS).
- **Атрибуция ≠ генерация**: метрики в духе EOI вознаграждают изоляцию; генератор должен продолжать активность при
  отрезанном входе *и* влиять на других (A26).
- **Рецепт Governor**: медленный протекающий ограничитель хронической доли каждого мотива + глобальный бюджетный
  контур (A29).
- **Мир как скрытая память**: при X=0 реактивный мир несёт 15–35 % «эндогенной» активности; аудит — world-cut
  + неконтингентный replay (A30–A31).
- **Ритмы задают «когда», не «кто/зачем»** (A36); медленный глобальный ритм порождается самой сетью, 1/f-шум его
  маскирует (A40).
- **Открытость**: иерархия жертвует комбинаторной новизной ради локализации; тонкий workspace восстанавливает
  темп новизны (A38–A39).
- **Мозг человека (HCP, 7 испытуемых)**: функциональные метастабильные границы; сенсорная кора — наиболее внешне
  управляемая; избыток самоинициации DMN не воспроизводит ни одна коннектомная модель (B1–B19).
- **Аудит MVP-0**: лексический гейт структурных драйвов, цикл — DAG, персеверация в тишине (C3, C8, C9);
  исправления — `research/endogeneity_topology/patches/combined_all.patch` (308 passed / 6 старых падений,
  18 новых тестов проходят) — **не применён к `src/`**.

Ограничения: toy-модели, в основном 2 сида, 7 испытуемых, нет пререгистрации; всё — уровень C1–C2.

---

## 4. Что дальше в исследовании

### 4.1 Закрыть открытые нити (короткие тики)
1. **do(noise)-аудит** (A40): эндогенная доля при замене шума на замороженную копию или на шум от другого сида —
   E_norm через истинный W этого не видит.
2. **Новизна на уровне коалиций** при динамической маршрутизации (A39): паттерн = множество коактивных узлов после
   кластеризации, а не блок.
3. **Статистика**: A-утверждения с 2 сидами → 10 сидов + бутстрэп-интервалы; сводная таблица «эффект ± CI».

### 4.2 Перенос в архитектуру (главная точка роста)
4. **Endogeneity Audit Card** — модуль `src/eia/audit/endogeneity_card.py`: E_norm по границам, world-cut +
   non-contingent replay, сигнатура генератора (out-influence + независимость), индекс доминирования, фазовая
   связь с медленными глобальными модуляциями. Выход — JSON рядом с EOI. **[решение владельца: трогает `src/`]**
5. **Применить `combined_all.patch`** через отдельную ветку и PR (C11 crash guard, D6 inhibition of return,
   D1 causal drive attribution, PopulationDrives v3). **[решение владельца]**
6. **Governor v2** по рецепту A29: хронический cap + глобальный бюджет; тест — отсутствие захвата одним мотивом
   на 10⁴ тиков тишины.
7. **Иерархический BeliefField**: вложенные модули + тонкий workspace (A35, A39) как структура `DriveEngine`
   вместо плоского списка драйвов.

### 4.3 Данные мозга
8. Больше испытуемых (HCP > 7; neurolib даёт до 80 при внешней загрузке), парцелляции Schaefer-200/400.
9. Task-fMRI / MEG с самоинициированными движениями (readiness-potential-подобные) для проверки «когда vs кто».
10. Связать с `research/brain_ai` (T-BRAIN-01..06) и `research/agent_eia` (T-AGENT-01..03): Brian2 LIF-подграф
    (коммит `0d3fad1`) — кандидат на третью модель рядом с Hopf и drive-units.

### 4.4 Публикация
11. Препринт «Endogeneity is a property of (system, boundary)»: A9–A12, A26, A30–A31, B13–B14 — ядро;
    код — `lib/` из P2; C2-формулировки.
12. Реестр заявлений: каждую A/B/C-находку → YAML с уровнем C, сидами, скриптом, статусом (holds/revised/withdrawn),
    чтобы CI проверял воспроизводимость ключевых чисел.

---

## 5. Решения, которые ждут владельца

| Решение | Варианты |
|---|---|
| Применить `combined_all.patch` к `src/` | PR из отдельной ветки / отложить |
| Переписать историю ради вендорных данных (−~100 МБ) | `git filter-repo` + force-push / оставить |
| Лицензия кода | CC BY 4.0 как есть / Apache-2.0 для кода |
| Слить `research/endogeneity-topology` в main | PR только с `research/endogeneity_topology/**` / держать отдельно |
| Остановить цикл `07e025f1` (тики каждые 5 мин) | остановить / продолжать |
| Судьба 5 stash-записей | сохранить в ветки / удалить |

---

## 6. План для Cursor (по порядку)

| # | Задача | Команды / файлы | Критерий приёмки |
|---|---|---|---|
| 1 | Снять конфликт из §0 | см. §0 п.2 | `git status` чистый, `stash@{0}` на месте |
| 2 | Worktree для агентов | `git worktree add ../PROACTIVE_AI-topology research/endogeneity-topology` | у каждого агента своя директория |
| 3 | Починить CI | `git push -u origin fix/ci-vendor-skips`; `gh pr create -B main` | зелёный прогон EIA CI на PR |
| 4 | Исправить README (R2) | `README.md` | таблица рендерится на GitHub |
| 5 | Запушить main | `git push origin main` (после merge PR из п.3) | `origin/main` = локальный |
| 6 | Обновить `RESEARCH_BRANCHES.md`, `.cursor/rules` (R9, R10) | `docs/`, `.cursor/rules/` | перечислены все 6 веток, правило указывает актуальную ветку |
| 7 | CI для ветки topology + ruff per-file-ignores (R11) | `eia-ci.yml`, `pyproject.toml` | `ruff check research/endogeneity_topology` чисто |
| 8 | Версия (R12), GitHub Release sci-flow-v0.3 (R13) | `pyproject.toml`, `gh release create sci-flow-v0.3 …` | Release виден, PDF приложены |
| 9 | `docs/INDEX.md` + `docs/archive/` (R8) | `docs/` | каждый файл имеет статус |
| 10 | Библиотека `research/endogeneity_topology/lib/` | перенос функций из `topo_endo.py`, `tick12`, `tick35_lib`, `tick142`, `tick148` | тики 148–150 воспроизводят числа из LOG |
| 11 | Тики: do(noise), новизна коалиций, 10 сидов | `toy/tick151+.py` | записи в `LOG.md` и `FINDINGS.md` |
| 12 | **[решение владельца]** patch → PR, Audit Card, Governor v2 | `src/eia/…` | полный набор тестов зелёный, EUIR на eval не изменился |

*Составлено Claude Code CLI по локальному клону, `git`, `gh` и прогону тестов 2026-09-30.*
