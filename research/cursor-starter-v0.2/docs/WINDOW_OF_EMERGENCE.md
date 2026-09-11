# Window of Emergence (WoE)

## 1. Идея

WoE — временный режим, в котором несколько независимых внутренних подсистем
достаточно согласованы, чтобы сформировать общий motive/intention, но не
настолько синхронизированы, чтобы потерять разнообразие и конкуренцию.

Это не точка «пробуждения» и не признак сознания. Это проверяемая гипотеза о
динамической организации вычисления.

## 2. Почему world model недостаточно

World model отвечает на вопросы «что существует?», «что вероятно произойдёт?» и
«что будет, если…». Он не определяет автоматически:

- что сейчас заслуживает внимания;
- почему нужно действовать именно сейчас;
- какой конфликт имеет приоритет;
- должен ли внутренний мотив пересечь boundary контакта.

Поэтому между world model и policy нужен отдельный formation layer:

\[
\text{world/self model}
\rightarrow\text{tension field}
\rightarrow\text{temporal coordination}
\rightarrow\text{intent proposal}.
\]

## 3. Что означает «42 Hz» для AI

Биологическая gamma-активность занимает широкий диапазон, а её частота зависит
от области, задачи и механизма. 40 Hz часто используется как типичное или
экспериментальное значение. Нет эмпирического основания утверждать, что AI при
42 Hz получает собственные причины.

В EIA используется более слабая и тестируемая формулировка:

> 42-cycle mode — режим, в котором специализированные модули обновляют фазовые
> состояния на общей carrier-шкале, а интеграция определяется относительными
> фазами, coupling и metastability.

Абсолютная частота должна проходить sweep. Если эффект существует только при
42.0 и исчезает при 41.5/43.0 без механистического объяснения, это скорее
артефакт.

## 4. Фазовая модель

Для модулей (i=1,\ldots,N):

\[
\dot\theta_i = 2\pi f_i +
\frac{K_t}{N-1}\sum_{j\neq i}a_j(t)
\sin(\theta_j-\theta_i)+\sigma\xi_i(t).
\]

В reference field шесть модулей:

1. world model;
2. memory/staleness;
3. self-model;
4. prospective imagination;
5. semantic integration;
6. causal/governor readiness.

Глобальная фазовая когерентность:

\[
R(t)e^{i\Psi(t)}=\frac1N\sum_{j=1}^{N}e^{i\theta_j(t)}.
\]

(R\approx0) означает низкую глобальную синхронизацию; (R\approx1) — почти
полную. Ни один край не считается автоматически оптимальным.

Metastability в окне:

\[
M_t=\operatorname{Std}_{\tau\in[t-w,t]}R(\tau).
\]

Исследовательская гипотеза: initiative formation вероятнее при частичной,
флуктуирующей интеграции, чем при полном locking.

## 5. Когерентность не сводится к фазе

WoE использует четыре разных признака:

- (C_{phase}) — временная координация;
- (C_{sem}) — совместимость содержаний/гипотез;
- (C_{temp}) — согласованность current state и imagined horizons;
- (C_{causal}) — полнота и достоверность provenance.

Высокий phase coherence при семантическом конфликте не должен открывать окно.
Высокая semantic coherence с повреждённым ledger тоже недостаточна.

## 6. Поле эпистемического напряжения

Для target (i):

\[
q_i(t)=
0.28I_i+0.22S_i+0.18L_i+0.17D_i+0.15P_i,
\]

где:

- (I_i) — ignorance;
- (S_i) — surprise;
- (L_i) — staleness;
- (D_i) — self-prior discrepancy;
- (P_i) — prospective tension.

Между двумя ведущими targets определяется separation. В reference code это
описательный margin, а не доказательство уникальности цели.

## 7. Потенциал окна

Вместо одного hard trigger используется геометрическая агрегация:

\[
\Phi_t=
\left(
F_R(R_t)F_M(M_t)
C_{sem}C_{temp}C_{causal}
q_{(1)}\Delta_q
\right)^{1/7},
\]

где (F_R,F_M) — smooth preference functions для промежуточного coherence и
metastability, (q_{(1)}) — ведущий epistemic pressure, (Delta_q) — separation.

Reference functions — Gaussian fits вокруг экспериментальных, а не
биологических значений. Их нельзя считать универсальными константами.

## 8. Не hard trigger, а first-passage

Formation hazard:

\[
h(t)=h_0q_{(1)}^2\Delta_q
\exp\{\beta(\Phi_t-\Phi_0)\}.
\]

Накопленная интенсивность:

\[
\Lambda(t)=\int_0^t h(\tau)d\tau.
\]

В начале эпизода выбирается activation energy
(E\sim\operatorname{Exp}(1)). Intent формируется при первом прохождении:

\[
t^*=\inf\{t:\Lambda(t)\ge E\}.
\]

Это всё ещё rule-governed system. Преимущество first-passage в том, что нет
заранее заданной пары «конкретное событие → конкретная цель»: target и момент
являются результатом траектории состояния и конкуренции.

## 9. Why-now decomposition

Каждый WoE intent должен иметь машиночитаемый ответ:

\[
\text{why-now}=
(\Delta q,\dot q,R,M,C_{sem},C_{temp},C_{causal},\Lambda,E).
\]

Natural-language rationale не является causal evidence. Оно генерируется из
этого typed trace.

## 10. Reference experiment

Команда:

~~~bash
make woe
~~~

Reference seed 7 формирует `wm:causal_gap` на 2.696 s. Output остаётся
`proposal_only`; ни контакт, ни инструмент не вызываются.

Отрицательные контроли:

1. `world_model_enabled=False` → (q=0), (Lambda=0), no intent;
2. `scramble_phases=True` → reference trace не достигает activation energy;
3. carrier sweep 20/30/42/70 Hz → тот же target/time.

Третий результат показывает только инвариантность reference equations к общему
carrier shift. Он не показывает, что частота вообще не важна в будущей системе
с delays, cross-frequency coupling или hardware timing.

## 11. Фальсификация

Гипотеза WoE ослабляется, если:

- простой event-threshold baseline даёт те же initiative quality/burden;
- phase scrambling не влияет после большого числа seeds;
- internal-state interventions не меняют target;
- learned proposer создаёт инициативы даже при (q=0);
- why-now score не калибруется по human labels;
- 42 Hz эффект оказывается numerical aliasing;
- система максимизирует contact count вместо useful initiative;
- trace объясняет решение post hoc и не предсказывает intervention outcome.

## 12. Следующая математическая версия

1. заменить all-to-all Kuramoto на learned sparse coupling graph;
2. добавить delays и cross-frequency coordination;
3. отделить local synchrony от symmetric phase clusters;
4. использовать survival analysis для hazard calibration;
5. учить target field из prediction residuals, не из ручных feature weights;
6. оценивать critical slowing down до WoE;
7. сравнить first-passage, bifurcation и stochastic resonance formulations;
8. связать causal uncertainty graph с (C_{causal}).

