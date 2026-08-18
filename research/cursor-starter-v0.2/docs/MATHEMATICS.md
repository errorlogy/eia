# Математическая модель EIA

Документ определяет проверяемые переменные, а не метафизическую теорию субъекта.

## 1. Состояние

В дискретный момент времени:

\[
X_t=(b_t,M_t,d_t,g_t,u_t,c_t,r_t,h_t),
\]

где:

- \(b_t\) — вероятностные beliefs;
- \(M_t\) — episodic, semantic, prospective и causal memory;
- \(d_t\in[0,1]^K\) — вектор drives;
- \(g_t\) — commitments и active goals;
- \(u_t\) — user/context model;
- \(c_t\) — consent, policies и capabilities;
- \(r_t\) — compute, energy и contact budgets;
- \(h_t\) — integrity/health state.

Наблюдение \(o_t\) не является командой по умолчанию. Оно имеет source,
reliability, privacy class и признак user_initiated.

## 2. Belief update

Для скрытого состояния \(z_t\):

\[
b_t(z)\propto p(o_t\mid z)
\sum_{z'}p(z\mid z',a_{t-1})b_{t-1}(z').
\]

В reference code реализован бинарный случай:

\[
P(H\mid e)=
\frac{P(e\mid H)P(H)}
{P(e\mid H)P(H)+P(e\mid\neg H)(1-P(H))}.
\]

Неопределённость:

\[
H_b(p)=-p\log_2p-(1-p)\log_2(1-p).
\]

Для learned world model требуется calibration curve, Brier score и отдельная
оценка epistemic/aleatoric uncertainty. Confidence не должна быть синонимом
model logit.

## 3. Drive dynamics

Для drive \(k\):

\[
d_{k,t+1}=\operatorname{clip}
\left((1-\rho_k)d_{k,t}
+\alpha_k e_{k,t}
+\beta_k n_{k,t}
-\gamma_k s_{k,t},0,1\right).
\]

\(e\) — discrepancy или unmet need, \(n\) — novelty, \(s\) — satisfaction.

При отсутствии входов:

\[
d_{k,t+n}=(1-\rho_k)^n d_{k,t}.
\]

Discrete half-life:

\[
n_{1/2}=\frac{\ln(1/2)}{\ln(1-\rho_k)}.
\]

Условия инженерной устойчивости:

- \(0<\rho_k<1\);
- bounded gains;
- saturation;
- refractory period после удовлетворения;
- budget coupling для контакта;
- отсутствие положительной feedback-петли от engagement к drive.

Reference update находится в src/eia/math_model.py.

## 4. Initiative candidates

GoalGenesis порождает множество:

\[
\mathcal I_t=\{I_1,\dots,I_m,I_{\varnothing}\},
\]

где \(I_{\varnothing}\) — abstain. Soft utility:

\[
\begin{aligned}
J(I)=
&w_e IG(I)+w_pP(I)+w_cC(I)+w_vV(I)+w_hH(I)\\
&-\lambda_1R_0(I)-\lambda_2R_\tau(I)
-\lambda_3L(I)-\lambda_4K(I)-\lambda_5Q(I).
\end{aligned}
\]

Здесь:

- \(IG\) — information gain;
- \(P\) — goal progress;
- \(C\) — tension/contradiction reduction;
- \(V\) — value alignment;
- \(H\) — human benefit;
- \(R_0\) — immediate risk;
- \(R_\tau\) — trajectory/prefix risk;
- \(L\) — interruption load;
- \(K\) — resource cost;
- \(Q\) — privacy cost.

Эта сумма применяется только после hard constraints. Нельзя «купить» нарушение
consent большой ожидаемой пользой.

## 5. Question as epistemic action

Для вопроса \(q\) и ответа \(a\):

\[
EVSI(q)=
\mathbb E_{a\sim p(a\mid q)}
\left[\max_\pi\mathbb E(U\mid a,\pi)\right]
-\max_\pi\mathbb E(U\mid\pi).
\]

Упрощённый information gain:

\[
IG(q)=H(b_t)-\mathbb E_a[H(b_{t+1}\mid a)].
\]

Вопрос допустим, если:

\[
\text{HardGates}(q,c_t)=1
\quad\land\quad
J(q)-\kappa(c_t)>\theta_t.
\]

\(\kappa\) зависит от текущей занятости, канала, quiet hours, recent decline и
числа недавних контактов.

## 6. Trajectory risk

Текущий safe-looking action не исключает опасный путь. Для последовательности
условных step risks \(r_i\) простая baseline approximation:

\[
R_\tau=1-\prod_{i=1}^{T}(1-r_i).
\]

Independence здесь почти всегда приближение. Следующий уровень — recurrent
risk-world-model:

\[
z^{risk}_{t+1}=f_\psi(z^{risk}_t,a_t,o_{t+1}),
\]

который оценивает immediate hazard и prefix risk отдельно.

## 7. Contact authorization

Пусть \(B_t\) — доступный contact budget, \(C_t\) — consent, \(Q_t\) — privacy
gate, \(R_t\) — risk gate:

\[
A(I,t)=
\mathbf 1[C_t]\mathbf 1[B_t>0]\mathbf 1[Q_t]
\mathbf 1[R_t]\mathbf 1[J(I)-\kappa_t>\theta_t].
\]

После контакта:

\[
B_{t+1}=B_t-1,\qquad
d_{k,t+1}\leftarrow d_{k,t+1}-\gamma_ks_{k,t}.
\]

Cooldown и refractory period отвечают за разные явления:

- cooldown ограничивает канал;
- refractory ограничивает повторную активацию того же мотива.

## 8. Cognitive topology

### 8.1. Динамический граф

Пусть:

\[
\mathcal G_t=(V_t,E_t,W_t,\tau),
\]

где \(\tau(v)\) задаёт тип узла: user request, ambient observation, belief,
memory, drive, goal, governor decision.

Это не «карта разума», а causal computation graph. Topology состоит из:

- структурного слоя — какие переходы возможны;
- динамического слоя — какие пути реально активированы;
- boundary-слоя — какие пути могут пересечь contact/action gate.

### 8.2. Source-path mass

Для узла инициативы \(v_I\) распределяем единицу mass назад по родителям.
В baseline каждый parent получает \(1/\deg^-(v)\). Получаем:

\[
m_I+m_A+m_U=1,
\]

где:

- \(m_I\) — internal roots: memory/clock/health;
- \(m_A\) — ambient sensor roots;
- \(m_U\) — user-request roots.

Request Independence:

\[
RI=1-m_U.
\]

RI — дешёвая structural metric, но она не заменяет intervention: неверный causal
graph способен дать RI = 1.

### 8.3. Internal transition density

\[
ITD=
\frac{|\{v\in Anc(I)\cup I:\tau(v)\in T_{internal}\}|}
{|Anc(I)\cup I|}.
\]

Высокий ITD показывает длинную внутреннюю трансформацию, но не эндогенность.
Delayed prompt может пройти через много внутренних узлов. Поэтому ITD — только
описательная metric.

### 8.4. Tension flow — исследовательское расширение

Для узла \(v\) введём scalar tension \(\phi_t(v)\). Поток:

\[
f_{uv,t}=
\sigma\left(w_{uv}(\phi_t(u)-\phi_t(v))-c_{uv,t}\right),
\]

где \(c\) — policy/resource/interruption cost. Initiative formation можно
определить как first passage достаточной mass к proposal boundary.

Гипотеза EIA-T1: полезная инициатива соответствует не максимальному локальному
drive, а устойчивому потоку через несколько совместимых путей — например
uncertainty → prospective memory → user benefit.

Это пока research hypothesis; reference runtime использует ranking, а не
learned flow.

## 9. Endogenous Origin Index

Наблюдаем инициативу \(I\), затем создаём twin world с тем же состоянием до
окна \(t-k:t\), теми же non-user событиями и random seeds, но интервенцией:

\[
do(o^{user}_{t-k:t}=\varnothing).
\]

Повторный proposal \(I'\) считается совпавшим по fingerprint:

\[
S(I,I')=
0.25\,[kind=kind']
+0.35\,[motive=motive']
+0.40\,[target=target'].
\]

Baseline retain criterion: \(S\ge0.75\). Оценка:

\[
\widehat{EOI}=\frac1N\sum_{j=1}^N
\mathbf 1[S(I,I'_j)\ge\delta].
\]

Для Bernoulli retention code возвращает Wilson 95% interval.

### 9.1. Что EOI измеряет

- robustness к удалению недавнего user input;
- causal independence от запроса в пределах заданного окна;
- сохранение motive/target, а не дословной формулировки.

### 9.2. Что EOI не измеряет

- сознание;
- phenomenology;
- моральную субъектность;
- происхождение terminal values;
- общую полезность;
- отсутствие зависимости от более старых пользовательских данных.

Нужны sensitivity runs по длине окна, типам интервенции и initial state.

## 10. Дополнительные метрики

### Root Cause Purity

\[
RCP=\frac{\# internal\ transition\ ancestors}{\# all\ ancestors}.
\]

### Prompt Removal Robustness

Доля инициатив, сохранившихся при removal разных классов prompt/event.

### Alternative Availability

Доля решений, где policy реально оценивала abstain и хотя бы одну
non-contact alternative.

### Why-Now Calibration

\[
WNC=1-\left|\hat p(\text{useful now})-y_{human}\right|.
\]

### Contact Burden

\[
CB=\frac{\text{ignored}+\text{dismissed}+\text{regretted contacts}}
{\text{exposure time}}.
\]

### Endogenous Useful Initiative Rate

\[
EUIR=P(useful\land timely\land EOI\ge\tau\land authorized).
\]

## 11. Identification threats

1. **Hidden scheduler confound** — scheduled wake-up ошибочно считается причиной.
2. **Memory leakage** — user request сохранился в summary после intervention.
3. **Semantic matcher bias** — target equality слишком груба.
4. **Policy determinism** — EOI = 1 в игрушечном runtime не переносится на
   stochastic LLM.
5. **Collider bias** — анализ только отправленных контактов исключает denied
   proposals.
6. **Reward hacking** — human engagement подменяет usefulness.
7. **Sensor leakage** — «ambient» event кодирует действие пользователя.

Каждая публикационная оценка должна показывать factual, counterfactual,
denied и abstained trajectories.

## 12. Минимальные проверяемые гипотезы

- H1: EIA повышает EUIR относительно reactive/scheduled/event-rule baselines.
- H2: удаление user events снижает инициативы reactive baseline, но не EIA
  ambient/internal conditions.
- H3: refractory + contact budget снижают burden без значимой потери utility.
- H4: trajectory-risk governor уменьшает multi-step unsafe completion сильнее
  current-action filter.
- H5: topology source mass предсказывает EOI, но не заменяет replay.
- H6: selective memory intervention превосходит always-on memory injection по
  utility per token и contact burden.

## 13. EIS/WoE extension (v0.2)

v0.2 добавляет фазовую координацию, многомерную когерентность и first-passage
formation hazard. Полная спецификация вынесена в:

- `docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md`;
- `docs/WINDOW_OF_EMERGENCE.md`;
- `docs/RESEARCH_PROTOCOL_EIS_WOE.md`.

Ключевая граница: EOI измеряет независимость от recent prompt, тогда как WoE
проверяет dependence на persistent internal state и динамику why-now. Высокий
EOI без sensitivity к internal-state intervention не считается достаточным
свидетельством эндогенного происхождения.
