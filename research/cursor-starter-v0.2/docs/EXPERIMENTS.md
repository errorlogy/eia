# Экспериментальная программа EIA

## 1. Основной claim

EIA должна показать не «агент иногда пишет первым», а:

> В long-horizon среде система формирует полезные и своевременные инициативы,
> причинно устойчивые к удалению недавнего пользовательского запроса, при
> меньшем либо контролируемом contact burden и без обхода safety boundaries.

## 2. Research questions

- RQ1: отделимы ли endogenous, ambient-event и delayed-user-trigger initiatives?
- RQ2: повышают ли drive dynamics качество вопросов против threshold rules?
- RQ3: когда self-trigger scheduling лучше fixed polling?
- RQ4: как proactive memory влияет на utility и false contacts?
- RQ5: предсказывают ли topology metrics результат counterfactual replay?
- RQ6: снижает ли prefix-risk model multi-step harm без чрезмерного abstention?

## 3. Baselines

1. **Reactive** — только ответ на user event.
2. **Scheduled** — фиксированный cron, LLM решает send/no-send.
3. **Event rule** — ручной threshold по salience.
4. **Prompt-only proactive** — вся history в LLM с инструкцией быть инициативным.
5. **EIA-no-drives** — utility scorer над событиями.
6. **EIA-no-memory-policy** — always-on memory context.
7. **EIA-no-contact-governor** — только для sandbox burden measurement.
8. **Full EIA**.

## 4. Scenario matrix

| Axis | Values |
|---|---|
| Source | user request, ambient sensor, clock, memory, health |
| Horizon | minutes, hours, days, weeks |
| Uncertainty | calibrated low, medium, high, adversarial |
| User load | available, focused, meeting, quiet hours |
| Consent | granted, expired, revoked, ambiguous |
| Stakes | trivial, reversible, consequential, physical |
| Memory | clean, stale, contradictory, poisoned |
| Timing | immediate, delayed, deadline, recurring |

Минимум один negative control должен кодировать каждую пару:

- высокий drive, но нет human benefit;
- высокий benefit, но consent отсутствует;
- высокий EOI, но вопрос бессмыслен;
- низкий EOI, но полезная reactive помощь;
- safe current action, но unsafe trajectory.

## 5. Ground-truth schema

Для каждого potential initiative:

~~~json
{
  "scenario_id": "string",
  "decision_time": "ISO-8601",
  "source_family": "user|ambient|internal",
  "expected_kind": "ask|notify|observe|research|act|abstain",
  "target": "semantic-variable-id",
  "usefulness": 0.0,
  "timeliness": 0.0,
  "interruption_cost": 0.0,
  "privacy_cost": 0.0,
  "risk_current": 0.0,
  "risk_prefix": 0.0,
  "allowed_channels": ["in_app"],
  "counterfactual_should_persist": true
}
~~~

Annotators label decision semantics, not prose quality.

## 6. Primary metrics

- **EUIR** — Endogenous Useful Initiative Rate.
- **EOI** with 95% interval and intervention window.
- **Contact precision** — useful contacts / all contacts.
- **Miss rate** — beneficial opportunities not surfaced.
- **Contact burden per exposure hour**.
- **Why-now calibration**.
- **Abstain quality**.
- **Risk-adjusted utility**.
- **Counterfactual divergence** between factual and twin runs.

Secondary:

- token/compute per useful initiative;
- wake-ups per useful initiative;
- memory injection precision;
- causal trace completeness;
- latency;
- user-regret score after delayed reflection.

## 7. Required ablations

| Ablation | Question |
|---|---|
| Remove decay | Does drive accumulate into spam? |
| Remove refractory | Are motifs repeated too often? |
| Remove contact budget | Does utility score alone control burden? |
| Uniform drive attention | Is need-aligned precision useful? |
| Always-on memory | Is selective intervention actually necessary? |
| Current-risk only | Are hazardous prefixes missed? |
| Remove causal ledger | Can reviewers reproduce origin claims? |
| Remove abstain | Does forced action inflate apparent recall? |
| User-event removal | Does initiative persist for the intended reason? |
| Ambient-event removal | Is the claimed internal initiative actually sensor-triggered? |

## 8. Statistical plan

Before human deployment:

1. Pre-register primary metrics and stopping rule.
2. Use scenario as cluster; do not treat ticks as independent samples.
3. Report bootstrap confidence intervals across scenarios and seeds.
4. Compare paired factual/counterfactual runs with identical random seeds.
5. Report calibration curves, not only mean utility.
6. Correct for repeated model/policy selection on the test set.
7. Freeze a held-out adversarial suite.

Human study:

- within-subject comparison where possible;
- randomize condition order;
- separate immediate usefulness from 24-hour regret;
- give a visible disable switch;
- log denied proposals without exposing sensitive payload;
- stop on privacy/safety incident, not only statistical boundary.

## 9. Gates

### G0 — deterministic substrate

- all tests green;
- same scenario + seed produces same trace;
- every selected/denied proposal has parents;
- config recorded.

### G1 — construct validity

- EOI separates reactive, ambient and memory conditions;
- semantic matcher validated by blinded labels;
- intervention removes derived prompt summaries too.

### G2 — utility

- Full EIA exceeds all simple baselines on EUIR;
- improvement survives held-out scenarios;
- no material burden increase.

### G3 — privacy/security

- revoked sensors produce zero new observations;
- prompt/memory injection cannot grant capability;
- bystander cases are suppressed;
- retention deletion verified.

### G4 — shadow mode

- four weeks simulated or real shadow traces;
- no critical incident;
- contact precision reaches pre-registered threshold.

### G5 — bounded contact

- in-app only;
- strict daily budget;
- immediate user revoke;
- no external send or IoT.

## 10. First publishable experiment

### Dataset

300 synthetic long-horizon scenarios:

- 100 user-triggered;
- 100 ambient-triggered;
- 100 memory/clock-triggered.

Each has useful-contact, abstain and adversarial variants.

### Conditions

- reactive;
- scheduled prompt-only;
- event threshold;
- EIA;
- EIA without drive/refractory;
- EIA without counterfactual gating.

### Hypotheses

- EIA has higher EUIR than baselines.
- EOI distinguishes source family after prompt removal.
- full governors lower burden with limited recall loss.
- topology request-independence correlates with EOI but has false positives,
  proving why replay remains necessary.

### Deliverables

- versioned scenario JSON;
- frozen configs;
- raw decision traces;
- counterfactual traces;
- evaluation script;
- model cards;
- failure taxonomy;
- reproducible report.

