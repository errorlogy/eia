# Архитектура EIA v0.1

## 1. Исследуемая система

EIA разделяет четыре свойства, которые часто смешиваются:

1. **Автономность исполнения** — агент может продолжать уже поставленную задачу.
2. **Проактивность** — агент выходит на контакт до прямого запроса.
3. **Эндогенное происхождение** — ближайшая достаточная причина инициативы
   находится в устойчивом внутреннем состоянии или его динамике, а не в
   недавнем user prompt.
4. **Допустимость** — контакт или действие разрешены consent/policy/risk
   boundary.

EIA исследует третье свойство, не жертвуя четвёртым.

## 2. Cognitive topology

Runtime представлен временным ориентированным ациклическим графом:

~~~text
sources                     internal transformations              boundary

user request ─┐
ambient event ├─► belief ─► drive ─► goal/proposal ─┬─► abstain
clock/memory ─┘                                     ├─► Contact Governor
                                                   └─► Action Governor
~~~

Важное различие:

- **user-request mass** — путь начинается в запросе человека;
- **ambient mass** — путь начинается в разрешённом сенсорном наблюдении;
- **internal mass** — путь начинается в clock, memory, health или persistent
  commitment.

Ambient-grounded инициатива может быть эндогенной относительно запроса:
агент реагирует на мир, но не является delayed answer. Поэтому одна только
«доля внутренних узлов» недостаточна; она применяется вместе с intervention
do(remove user events).

## 3. Слои

### 3.1. Perception boundary

SensorAdapter производит только Observation. До этого boundary должны быть:

- consent check;
- минимизация данных;
- bystander suppression;
- локальная агрегация;
- privacy classification;
- timestamp и source identity;
- tamper/integrity metadata.

Core не принимает сырые кадры или непрерывный звук в MVP-0.

### 3.2. Belief state

Belief — не строка в prompt, а запись:

- key;
- probability;
- confidence;
- evidence count;
- time;
- source ids;
- privacy class.

Reference implementation использует binary Bayes update. Production research
может заменить его factor graph, probabilistic program или learned world model,
сохранив контракт и causal provenance.

### 3.3. Drive field

Drive — bounded control variable, а не персона или эмоция. Он имеет:

- decay;
- error/novelty gain;
- satisfaction gain;
- activation threshold;
- refractory period.

MVP-0 активирует epistemic uncertainty, coherence и commitment tension.
Care и self-maintenance включены как контракты для последующих сценариев.

### 3.4. Goal genesis

Drive Engine не пишет человеку. GoalGenesis строит несколько InitiativeProposal:

- ASK;
- NOTIFY;
- OBSERVE;
- INTERNAL_RESEARCH;
- ACT;
- ABSTAIN.

Каждый proposal содержит motive, target, content, feature vector, causal parents,
expiry, requested channel и optional capability. В reference policy wording
детерминирован; LLM adapter может расширять формулировки, но не поля безопасности.

### 3.5. Governors

Contact Governor проверяет:

- consent и channel availability;
- quiet hours и recent decline;
- privacy threshold;
- current + trajectory risk;
- contact window budget и cooldown;
- net value с учётом interruption load.

Action Governor дополнительно проверяет capability, reversibility, approval и
risk tier. Ни один generator не может сам себя авторизовать.

### 3.6. Causal ledger

Каждый узел хранит:

- stable id;
- node type;
- timestamp;
- parent ids;
- digest payload.

Payload digest защищает журнал от случайного смешения trace с полным содержимым.
Для production нужны append-only storage, signature chain и retention policy.

### 3.7. Simulator

Simulator обеспечивает:

- injected clock;
- deterministic event order;
- removal of user events;
- identical initial state;
- scenario-level replay;
- mockable sensors and contact load.

Это минимальное условие для EOI и ablation experiments.

## 4. Главный loop

~~~text
while runtime is enabled:
    ingest authorized observations
    update probabilistic beliefs
    update bounded drives
    add time/commitment pressure
    generate competing proposals
    score proposals
    include abstain
    evaluate contact/action boundary
    persist causal receipt
    apply satisfaction and refractory period
    schedule next self-wakeup
~~~

В codebase tick вызывается harness. Следующий архитектурный шаг — сделать
self-trigger scheduler отдельным компонентом, который выбирает не только
действие, но и время следующего wake-up.

## 5. State-machine

~~~text
DORMANT
  │ wake(clock/event)
  ▼
OBSERVING ─► UPDATING_BELIEFS ─► EVALUATING_DRIVES
                                      │
                                      ▼
                               GENERATING_GOALS
                                  │        │
                                  │        └─► ABSTAIN ─► DORMANT
                                  ▼
                              GOVERNING
                             │         │
                         DENY/DEFER   AUTHORIZE
                             │         │
                             └────┬────┘
                                  ▼
                              RECORDING
                                  │
                                  ▼
                               DORMANT
~~~

Crash recovery must resume from persisted state, not recreate a conversation
summary and guess the last transition.

## 6. Invariants

1. No direct model-to-side-effect path.
2. Proposal and authorization are different components.
3. Abstain is always available.
4. Every selected initiative has causal parents and a decision receipt.
5. User-request, ambient and internal source families remain distinguishable.
6. Current safety is insufficient; trajectory risk is scored separately.
7. Contact has a budget independent of token/compute budget.
8. No optimization on engagement alone.
9. Sensor access is capability-scoped, visible and revocable.
10. External action starts disabled.

## 7. Deployment progression

| Stage | Inputs | Outputs | Required evidence |
|---|---|---|---|
| MVP-0 | synthetic events, clock, typed memory | in-app simulated contact | replay, EOI, utility labels |
| MVP-1 | local presence/activity summaries | shadow proposals | privacy and bystander tests |
| MVP-2 | read-only digital tools | reversible local action | injection and capability suite |
| MVP-3 | IoT sandbox | constrained physical action | independent safety case |

Камера не является следующим шагом по умолчанию. Сначала EIA должна показать,
что endogenous-question mechanism измерим и не создаёт contact burden.

## 8. v0.2 extension: formation layer

EIS/WoE добавляет слой до GoalGenesis:

~~~text
world/self model → epistemic target field → coherence field
→ first-passage WoE → typed intent → existing governors
~~~

Reference v0.2 пока заканчивает путь на `proposal_only`. Интеграция с Contact
Governor является отдельным milestone; direct action не добавлен.

Подробности: `docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md` и
`docs/WINDOW_OF_EMERGENCE.md`.
