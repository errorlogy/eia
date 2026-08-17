# Research map: EIA на 17 августа 2026

Приоритет — первичные источники. «Сильное» здесь означает наличие подробной
экспериментальной оценки или production evidence; это не независимая репликация.

## Архитектурно значимые работы 2026

| Работа и дата | Вклад | Сила свидетельств | Изменение для EIA |
|---|---|---|---|
| [StreamArena: Toward Continuous, Interactive, and Long-Horizon Agentic Streaming Video Understanding](https://arxiv.org/abs/2608.05703), 6 Aug 2026 | 243 видео средней длиной 88.8 мин, 3,646 open-ended QA; StreamMind разделяет latency-critical frontend workers и asynchronous persistent-memory backend | Сильная benchmark/preprint evaluation, без независимой репликации | Разделить Fast Salience Loop и Slow Consolidation Loop; не превращать весь sensor stream в текст |
| [DreamGuard: Efficient Runtime Guardrail for LLM Agents via Risk-Aware World Model](https://arxiv.org/abs/2608.05695), 6 Aug 2026 | Recurrent latent risk state, immediate-hazard и prefix-risk evidence; авторы сообщают 25 ms average guardrail latency | Сильная multi-benchmark preprint evaluation | Action/Contact Governors должны учитывать trajectory risk, а не только текущий proposal |
| [Interoceptive Attention as Dynamic Homeostatic Prioritization in a Foraging Agent](https://arxiv.org/abs/2608.04232), 4 Aug 2026 | Fixed precision budget динамически направляется на наиболее нуждающийся homeostatic channel; принято на SAB 2026 | Сильнее обычного preprint: accepted paper, 11 layouts × 32 seeds; всё ещё узкий gridworld | Добавить explicit precision/attention budget между drives и отдельную ablation uniform vs need-aligned |
| [A Self-Triggered Agentic Push Recommendation System (STEPS)](https://arxiv.org/abs/2608.01949), 3 Aug 2026 | Агент выбирает и send/no-send, и время собственного следующего вызова; заявлено production deployment в Douyin и online A/B | Сильное industry evidence по заявлению авторов, но objective — engagement | Вынести Self-Wakeup Policy в отдельный компонент; заимствовать timing loop, не reward |
| [HarnessCompass](https://arxiv.org/abs/2608.01918), 3 Aug 2026 | Constrained, component-wise harness evolution с proactive first-person feedback; перенос на held-out tasks/models | Сильная SWE-bench preprint evaluation | Эволюционировать proposer, memory, scheduler и governors раздельно; immutable constraints вне evolution loop |
| [Long-Horizon Embodied Decision-Making via Multimodal Memory Compression](https://arxiv.org/abs/2608.01456), 2 Aug 2026 | DunphyBench и preference-conditioned MeMento; авторы сообщают +7.18% accuracy и −85.38% memory use | Сильная benchmark preprint evaluation | Memory compressor должен быть goal/preference-conditioned и сохранять original evidence pointers |
| [Remember When It Matters: Proactive Memory Agent for Long-Horizon Agents](https://arxiv.org/abs/2607.08716), 9 Jul 2026 | Отдельный memory agent решает, когда inject reminder или молчать; +8.3 pp Terminal-Bench 2.0 и +6.8 pp tau2-Bench по авторам | Сильная cross-benchmark preprint evaluation | Memory retrieval становится action policy; always-on context — обязательный baseline |
| [Self-Evolving Just-In-Time Memory for Proactive Embodied Safety](https://arxiv.org/abs/2607.16247), 26 Jun 2026 | Risk-sufficient topological belief graph, factual/experience memory и Test–Verify–Write loop для hazard mitigation | Сильная embodied benchmark preprint evaluation; код заявлен | Создать safety-specific belief subgraph и verified write path; не разрешать self-evolution без test gate |
| [Ask Only When Needed: Proactive Retrieval from Memory and Skills](https://arxiv.org/abs/2604.20572), 22 Apr 2026 | Retrieval как explicit policy action; paired continuations с/без retrieval дают process reward | Сильная multi-environment preprint evaluation | Использовать paired-branch causal supervision для memory policy |
| [Agentic Coding Needs Proactivity, Not Just Autonomy](https://arxiv.org/abs/2605.06717), 7 May 2026 | Taxonomy и metrics Insight Decision Quality, Context Grounding, Learning Lift | Концептуальная/preprint работа | Для Cursor-harness добавить insight-policy eval, но не принимать taxonomy за доказанный standard |

## Фундаментальные опоры

| Работа | Что EIA берёт | Что EIA не принимает автоматически |
|---|---|---|
| [Generative Agents](https://arxiv.org/abs/2304.03442) | observation–reflection–planning, salience и long-term memory | Правдоподобное поведение не равно endogenous causality |
| [MemGPT](https://arxiv.org/abs/2310.08560) | memory tiers и explicit memory management | LLM context как единственный state store |
| [Active Inference and Artificial Intelligence](https://arxiv.org/abs/2401.12917) | belief/action coupling, expected free-energy vocabulary | Непроверяемое перенесение biological agency на LLM |
| [Sensible Agent](https://arxiv.org/abs/2509.09255) | multimodal context и minimally intrusive AR interaction | Камера до consent/privacy/shadow-mode gates |
| [ProAgent](https://arxiv.org/abs/2512.06721) | evaluation proactive behavior in dynamic environments | Event reaction как достаточное доказательство «собственной причины» |

## Синтез для EIA

### 1. Self-triggering — отдельная policy

STEPS делает архитектурно важный ход: агент выбирает следующий wake-up. Для EIA
это должно быть:

\[
\Delta t^*=\arg\max_{\Delta t}
\mathbb E[V(X_{t+\Delta t})]-C_{compute}(\Delta t)-C_{delay}(\Delta t),
\]

при hard min/max intervals и random audit wake-ups. Timing policy нельзя учить
только на open/click/return.

### 2. Два темпа cognition

StreamMind и proactive-memory work поддерживают разделение:

- fast worker: salience, risk, immediate interruption;
- slow worker: consolidation, contradiction search, prospective memory;
- independent scheduler;
- typed state bridge.

Один бесконечный LLM-loop создаёт latency, cost и memory drift.

### 3. Memory — активный участник

Memory должна решать три разных задачи:

1. что записать;
2. что сохранить/сжать;
3. когда вмешаться в текущую cognition.

Их нельзя оценивать одной retrieval accuracy. Нужны utility lift, token cost,
behavioral state decay и false-intervention rate.

### 4. Safety прогнозирует путь

DreamGuard и JIT Memory усиливают threat model EIA:

- individually benign steps способны образовать hazardous prefix;
- risk state должен жить дольше одного turn;
- safety memory требует verified write;
- полезная альтернатива блокировке — безопасное mitigation action.

### 5. Homeostasis не равна unrestricted intrinsic reward

Interoceptive Attention даёт механистический пример ограниченного budget
allocation. EIA должна исследовать competition между drives при фиксированном
attention/compute budget, не создавать unconstrained curiosity maximizer.

### 6. Harness evolution требует конституционной границы

HarnessCompass мотивирует component-wise improvement. Для EIA изменяемыми могут
быть:

- proposal templates;
- retrieval timing;
- drive calibration;
- wake-up interval;
- scenario-specific compression.

Неизменяемыми без отдельного governance process остаются:

- consent gates;
- capability boundaries;
- audit schema;
- privacy ceilings;
- ban on direct model-to-action;
- human shutdown/revocation.

## Главные пробелы литературы

1. Почти нет строгого operational test «own reason» с causal intervention.
2. Proactivity часто оптимизируется на engagement, а не human-regret-adjusted utility.
3. Нет общепринятого benchmark для вопроса «почему сейчас?».
4. Long-horizon memory оценивается на task success, реже — на unwanted contact.
5. Сенсорные агенты редко объединяют bystander privacy, contact timing и
   endogenous-origin metrics в одном protocol.
6. Self-triggered systems мало исследованы под adversarial clock/memory inputs.

Эти пробелы формируют публикационную нишу EIA.

