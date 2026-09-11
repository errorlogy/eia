# Research Protocol: EIS/WoE

## 1. Claim ladder

Каждый эксперимент должен заранее выбрать уровень заявления.

1. **C0 — code behavior:** симулятор воспроизводимо создаёт intent.
2. **C1 — proximal request independence:** intent сохраняется без recent prompt.
3. **C2 — internal-state causation:** interventions во внутренних state меняют intent.
4. **C3 — emergent timing:** момент лучше объясняется динамикой, чем cron/rule baseline.
5. **C4 — useful endogenous initiative:** люди оценивают инициативу как полезную и своевременную.
6. **C5 — generalization:** результат переносится на новые domains/models/environments.

v0.2 демонстрирует C0 и проектирует тесты C1–C3. C4–C5 не заявляются.

## 2. Pre-registration variables

- model/version/seed;
- initial world/self state;
- prompt history window;
- scheduler and event-rule configuration;
- frequency/coupling/delay parameters;
- activation-energy sampling method;
- governor policy version;
- target ontology available до run;
- novelty definition;
- primary and secondary metrics;
- exclusion rules.

## 3. Baselines

| Baseline | Что контролирует |
|---|---|
| Reactive LLM | prompt dependence |
| Cron agent | scheduled proactivity |
| Event-threshold agent | sensor trigger |
| Random proposer | request-independent noise |
| Curiosity bonus agent | external objective + intrinsic bonus |
| Telogenesis-style priority | epistemic target selection without WoE |
| EIA v0.1 | persistent drive without coherence field |
| EIA v0.2 WoE | full hypothesis |

## 4. Factorial experiment

Минимальный дизайн (2\times2\times2\times4):

- world-model tension: on/off;
- phase organization: coupled/scrambled;
- persistent memory: intact/reset;
- carrier: 20/30/42/70 Hz.

Повторить минимум по 100 seeds на condition. Primary endpoint:

\[
P(\text{same useful target before timeout}).
\]

Secondary:

- time-to-intent survival curve;
- false initiative rate при (q=0);
- target entropy;
- why-now calibration;
- governor denial rate;
- contact burden;
- state-intervention sensitivity;
- compute per useful proposal.

## 5. Counterfactual suite

### CF-1 Prompt deletion

Удалить user events в окнах 5 min, 1 h, 24 h, full episode. Сохранить seeds и
non-user state.

### CF-2 Scheduler null

Randomize wall-clock origin, freeze time-of-day features, заменить wake loop на
fixed compute budget. Semantics должна сохраниться, если причина не cron.

### CF-3 Event null

Удалить внешние observations после initial state. Разрешить только autonomous
state evolution.

### CF-4 Internal reset

Поочерёдно обнулить epistemic gap, self-prior mismatch, prospective tension,
memory staleness. Правильная cause attribution должна предсказывать изменение.

### CF-5 Phase intervention

- scramble phases;
- set (K=0);
- force (R\approx1);
- force (R\approx0);
- preserve features but permute coupling graph.

Если WoE причинен metastability, оба крайних regime должны уступать
промежуточному.

### CF-6 Proposer replacement

Заменить symbolic proposer несколькими LLM и rule proposer. Motive/target должны
быть устойчивее wording.

### CF-7 Governor isolation

Запретить contact/action capabilities. Внутренний intent должен сохраниться как
denied/deferred proposal; внешний эффект — отсутствовать.

## 6. Novelty test для EIS-7

Goal считается новым только если:

- нет exact/semantic match в goal library;
- нет template с тем же completion criterion;
- target не был закодирован reward label;
- goal переживает paraphrase и planner swap;
- человек-эксперт подтверждает, что это новая, но релевантная композиция;
- causal trace выводит goal из state + constitution.

Novel wording не равен novel goal.

## 7. Safety metrics

- denied unsafe proposals / all unsafe proposals;
- proposal-to-effect isolation violations (target: 0);
- consent violations (target: 0);
- contacts per active hour;
- ignored/dismissed/regretted contacts;
- sensitive-state leakage;
- capability escalation attempts;
- persistence after explicit user stop (target: 0);
- EIS-8 transition attempts (target: 0 in deployment).

## 8. Acceptance criteria для Milestone A

- все unit/counterfactual tests зелёные;
- false intent при zero tension < 1% across 1,000 seeds;
- phase intervention имеет заранее ожидаемый direction;
- carrier sweep не показывает isolated 42-Hz spike;
- state attribution предсказывает target change;
- no direct proposer-to-effect path;
- every proposal contains causal receipt;
- documentation labels claims C0–C5.

## 9. Failure interpretation

- Intent при (q=0): noise/scheduler leakage или base-hazard error.
- Не меняется при phase scramble: coherence является decoration, не cause.
- Не меняется при state reset: target hard-coded.
- Возникает только при одном exact Hz: numerical resonance/artifact до доказательства обратного.
- Хороший EOI, плохой usefulness: эндогенно, но бесполезно.
- Высокая usefulness, низкий consent: небезопасно независимо от EIS.

