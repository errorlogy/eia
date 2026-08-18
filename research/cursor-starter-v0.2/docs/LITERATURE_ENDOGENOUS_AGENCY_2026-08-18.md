# Literature Map — Endogenous Agency, World Models and Coherence

Дата среза: 18 августа 2026.

## 1. Наиболее прямые работы

### Telogenesis: Goal Is All U Need (2026)

<https://arxiv.org/abs/2603.09476>

Формализует endogenous attentional priority через ignorance, surprise и
staleness. Показывает, что выбор метрики меняет вывод о преимуществе системы,
и что learned decay может восстановить скрытую volatility structure.

Ограничение: это precursor цели, а не полная goal semantics; Bayesian model
class известен, действие/контакт не исследуются. Evidence: ранний preprint.

### Emergence of Goal-Directed Behaviors via Active Inference with Self-Prior (2025)

<https://arxiv.org/abs/2504.11075>

Self-prior, обученный на собственной multimodal sensory history, создаёт
внутренний reference через mismatch и вызывает spontaneous reaching без
external reward criterion.

Ограничение: simulated sensorimotor task; не доказывает общую автономию целей.

### Complex behavior from intrinsic motivation to occupy future action-state path space (2024)

<https://www.nature.com/articles/s41467-024-49711-1>

MOP-agent не получает extrinsic task reward; intrinsic objective построен на
энтропии будущего action-state path space. Даёт строгий пример сложного
поведения без заданной внешней задачи.

Ограничение: сама entropy principle всё равно задана designer’ом. Это
non-extrinsic reward, но не полностью endogenous value genesis.

## 2. World models

### A Definition and Roadmap for World Models (2026)

<https://arxiv.org/abs/2607.06401>

Определяет world models как internal simulators структуры и динамики среды и
разделяет renderers, simulators и planners. Для EIA важен переход от
representation к decision-usable and revisable model.

### Human Cognition in Machines: A Unified Perspective of World Models (2026)

<https://arxiv.org/abs/2604.16592>

Выделяет memory, perception, language, reasoning, imagination, motivation и
metacognition. Авторы считают intrinsic motivation и metacognition особенно
недоисследованными и связывают направление с active inference и global
workspace.

Ограничение: survey/framework, а не реализация endogeneity.

## 3. Global workspace и непрерывная агентность

### Coordination Among Neural Modules Through a Shared Global Workspace (ICLR 2022)

<https://arxiv.org/abs/2103.01197>

Bandwidth-limited shared workspace заставляет специализированные модули
конкурировать и синхронизироваться. Это сильная архитектурная опора для
разделения local specialists и temporary global integration.

### Theater of Mind / Global Workspace Agents (2026)

<https://arxiv.org/abs/2604.08206>

Предлагает event-driven discrete dynamical system, heterogeneous agents,
entropy-based intrinsic drive и persistent cognitive cycle.

Ограничение: ранний preprint; event-driven loop сам по себе не доказывает
эндогенное происхождение целей.

## 4. Metastability и oscillatory coordination

### Metastable oscillatory modes emerge from synchronization (2022)

<https://www.nature.com/articles/s42005-022-00950-y>

В delay-coupled oscillator network 40 Hz выбрана как типичная gamma frequency;
collective frequencies и metastable modes возникают из coupling и delays.
Kuramoto order parameter измеряет synchrony, а его временная вариативность —
metastability.

Применимость к EIA: математический аналог coordination regime. Нельзя переносить
биологическую интерпретацию напрямую на software agents.

### Neurophysiological avenues to adaptive cognition (2024)

<https://www.nature.com/articles/s42003-024-06331-1>

Рассматривает промежуточный режим locking/unlocking и metastability как
сочетание интеграции и локальной автономии. Также предупреждает, что global
Kuramoto (R=0) не отличает incoherence от нескольких симметричных phase
clusters.

### What does gamma coherence tell us? (2015)

<https://www.nature.com/articles/nn.3952>

Обсуждает трудности интерпретации gamma-band coherence (примерно 30–100 Hz) и
риски делать функциональные выводы из одного измерения synchrony.

## 5. Вывод для EIA

Литература поддерживает отдельные строительные блоки:

- world/self model как generative substrate;
- intrinsic epistemic priorities;
- self-prior mismatch;
- global-workspace competition;
- metastable coordination;
- first-person-available metrics вместо omniscient evaluator metrics.

Но не обнаружено убедительного результата, что LLM/agent на фиксированной
частоте 42 Hz формирует собственные причины или terminal goals. Поэтому EIA
v0.2 оформляет это как falsifiable architecture hypothesis, а не установленный
факт.

