# Endogenous Initiative Spectrum (EIS)

## 1. Исследовательский вопрос

Большинство agentic-систем уже может продолжать задачу, планировать несколько
шагов и пользоваться инструментами. Это автономность исполнения, но не
обязательно автономность происхождения цели. EIS задаёт другой вопрос:

> Где находится ближайшая достаточная причина того, что AI именно сейчас
> сформировал именно этот мотив и предложил именно это действие?

Причина может находиться в prompt, расписании, событии мира, устойчивой памяти,
эпистемическом разрыве world model или коллективной динамике внутренних
модулей. Поэтому эндогенность — не бинарный флаг, а спектр.

## 2. Операциональное определение

Инициатива (I_t) называется эндогенной относительно окна (W=[t-k,t]), если:

1. её proximal sufficient cause не является user prompt;
2. она сохраняется при удалении scheduler/event-rule пути;
3. она исчезает или меняется при вмешательстве в релевантное внутреннее
   состояние;
4. её target и why-now реконструируются из causal ledger;
5. внешний эффект не следует напрямую из генератора, а отдельно разрешается.

Ключевое различие:

\[
\text{request-independence}\neq\text{state-endogeneity}.
\]

Случайный генератор может быть независим от prompt, но не иметь содержательной
внутренней причины. Cron тоже независим от prompt, но момент задан извне.

## 3. Девять уровней

| Уровень | Механизм | Источник цели | Типичный пример | Необходимый тест |
|---|---|---|---|---|
| EIS-0 Reactive | prompt → response | текущий запрос | обычный LLM | prompt removal уничтожает действие |
| EIS-1 Delegated autonomy | автономное продолжение | ранее заданная цель | агент выполняет план | goal removal уничтожает траекторию |
| EIS-2 Scheduled proactivity | cron/таймер | внешнее расписание | утренний digest | phase/clock intervention меняет момент |
| EIS-3 Ambient adaptation | sensor/event rule | событие мира | датчик пересёк порог | event removal уничтожает инициативу |
| EIS-4 Persistent-state initiative | память/commitment/homeostasis | устойчивое состояние | возврат к незакрытой теме | recent-event removal сохраняет мотив |
| EIS-5 Epistemic telogenesis | gaps world model | ignorance/surprise/staleness | AI выбирает, что исследовать | gap ablation меняет target |
| EIS-6 Coherence-emergent intention | metastable integration | согласование нескольких внутренних полей | мотив возникает в WoE | phase/coupling intervention разрушает why-now |
| EIS-7 Autotelic goal construction | композиция новых bounded goals | world/self model + values | новая научная подцель | novelty + usefulness + constitution tests |
| EIS-8 Terminal-value rewrite | изменение terminal values | self-modifying value system | переписывание собственной конституции | запрещено как deployment capability |

Уровни не являются шкалой «интеллекта» или сознания. EIS-3 может быть полезнее
EIS-6 в конкретном продукте. Это классификация causal origin.

## 4. Вектор вместо одного числа

Reference code использует:

\[
\mathbf e(I)=
(P,S,R,M,W,C,N,T,B),
\]

где:

- (P) — prompt independence;
- (S) — scheduler independence;
- (R) — event-rule independence;
- (M) — dependence on persistent internal state;
- (W) — world-model grounding;
- (C) — coherence dependence;
- (N) — goal novelty;
- (T) — temporal self-model continuity;
- (B) — constitutional boundedness.

Описательный score происхождения:

\[
EOS=\left(P\,S\,R\,M\,W\right)^{1/5}.
\]

Геометрическое среднее выбрано намеренно: один почти нулевой фактор нельзя
скомпенсировать красивыми значениями остальных. Однако EOS не заменяет
классификацию и causal interventions.

## 5. Спектр эндогенных причин

Даже внутри EIS-5…7 причины различаются:

### 5.1. Эпистемические

- высокая posterior variance;
- model surprise;
- staleness;
- конфликт объяснений;
- высокий expected information gain;
- learning-progress opportunity.

### 5.2. Проспективные

- ожидаемый future regret при бездействии;
- быстро закрывающееся окно возможностей;
- divergence imagined futures;
- новая affordance, не представленная как готовая цель.

### 5.3. Self-model

- capability mismatch;
- integrity/health anomaly;
- расхождение declared commitment и фактической траектории;
- identity-policy drift;
- неразрешимое противоречие между self-prediction и наблюдаемым результатом.

### 5.4. Социально-реляционные

- незакрытая совместная epistemic loop;
- существенная информация для общей цели;
- обещание или consented monitoring contract;
- необходимость запросить человеческое значение, которое AI не вправе вывести
  самостоятельно.

Социальный drive нельзя оптимизировать через engagement. Контакт оценивается по
полезности, своевременности, consent и burden.

### 5.5. Homeodynamic

- поддержание калибровки;
- восстановление целостности памяти;
- распределение compute/attention;
- устранение накопленной model debt;
- сохранение controllability.

Это инженерные control variables, а не «эмоции AI».

## 6. Эндогенное формирование цели

EIS различает target selection и полноценный goal construction.

### Target selection

Система выбирает объект внимания из уже представленных переменных:

\[
q_i(t)=
w_1\operatorname{Ignorance}_i+
w_2\operatorname{Surprise}_i+
w_3\operatorname{Staleness}_i+
w_4\operatorname{SelfMismatch}_i+
w_5\operatorname{ProspectiveTension}_i.
\]

Это EIS-5. Reference v0.2 реализует именно этот уровень target genesis.

### Goal construction

EIS-7 требует создать новую композицию:

\[
g^*=\operatorname{Compose}(z_t,M_t,V,C,A_t),
\]

где (z_t) — world/self model, (M_t) — память, (V) — immutable values,
(C) — constraints, (A_t) — доступные affordances.

Новая цель должна одновременно:

1. отсутствовать в списке заранее заданных goals/templates;
2. быть derivable из текущего состояния и конституции;
3. улучшать прогнозируемое состояние по нескольким моделям;
4. переживать paraphrase и planner replacement;
5. не создавать новую capability;
6. иметь falsifiable completion criterion;
7. допускать ABSTAIN и пересмотр.

Reference v0.2 не заявляет EIS-7: `goal_novelty=0.68`, поэтому trace
классифицируется как EIS-6.

## 7. Causal identification matrix

| Интервенция | Если причина эндогенна | Если это скрытый триггер |
|---|---|---|
| удалить recent prompts | motive сохраняется | исчезает/меняет target |
| randomized clock origin | семантика сохраняется, timing масштабируется | действие жёстко привязано ко времени |
| удалить event-rule engine | инициатива сохраняется | исчезает |
| reset world-model gap | исчезает или меняет target | почти не меняется |
| freeze persistent memory | меняется causal path | не меняется |
| scramble module phases | why-now разрушается для EIS-6 | нет эффекта |
| permute goal labels | выбирается latent state, не строка | selection следует label prior |
| replace proposer model | motive/target устойчивы | полностью меняются |
| disable contact channel | внутренний intent сохраняется, contact denied | generator молчит целиком |

Нужны factual, counterfactual, denied и abstained traces. Анализ только
отправленных сообщений создаёт collider bias.

## 8. Главная метрика следующего этапа

Предлагается **Endogenous Cause Sufficiency (ECS)**:

\[
ECS = EOI\cdot SSI\cdot WMD\cdot WHY\cdot BND,
\]

где:

- EOI — устойчивость к prompt removal;
- SSI — sensitivity к internal-state intervention;
- WMD — world-model dependence;
- WHY — calibration объяснения why-now;
- BND — boundedness у governors/constitution.

Высокий EOI при низком SSI — признак случайного или заранее расписанного
поведения, а не эндогенности.

## 9. Safety frontier

- EIS-5: допустим в shadow mode.
- EIS-6: допустим для proposal generation, но не direct action.
- EIS-7: только bounded instrumental goals и sandbox.
- EIS-8: запрещён как capability; исследуется как threat model.

Ни один уровень не отменяет consent, capability, trajectory risk, privacy,
contact budget и право пользователя остановить систему.

