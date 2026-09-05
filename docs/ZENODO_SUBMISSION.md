# Zenodo Submission — Proto-AGI Horizon

**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Milestone:** M-ZENODO-PREP  
**Version:** v1.0.0 (September 2026)  
**Claim ceiling:** C2 — `claim_allowed=false`; no AGI\* claims.

---

## Quick paths (copy-paste)

| Item | Path |
|------|------|
| **Drag-drop zip (recommended)** | `zenodo/proto_agi_horizon_upload.zip` |
| **PDF (primary file)** | `zenodo/proto_agi_horizon/Kuznetsov_2026_Proto_AGI_Horizon.pdf` |
| **LaTeX sources (optional)** | `zenodo/proto_agi_horizon/sources/proto_agi_horizon_arXiv_submission.tar.gz` |
| **Metadata reference** | `zenodo/proto_agi_horizon/metadata.yaml`, `datacite.xml` |
| **Upload guide (this file)** | `docs/ZENODO_SUBMISSION.md` |

Regenerate bundle after paper edits:

```powershell
make arxiv-proto-agi-compile
make arxiv-proto-agi-package
# then refresh zenodo/proto_agi_horizon/ copies and re-zip (see SCI_FLOW_LOG Entry 063)
```

---

# Руководство (RU)

## Когда использовать Zenodo вместо arXiv

Если **arXiv endorsement заблокирован** или аккаунт ещё не одобрен — **Zenodo — основной путь публикации** для этой работы. DOI от Zenodo даёт постоянную цитируемую ссылку; arXiv можно добавить позже как зеркало.

См. также: `docs/ARXIV_SUBMISSION.md` (arXiv — опционально, когда endorsement доступен).

## Шаг 1 — Вход

1. Откройте [https://zenodo.org](https://zenodo.org)
2. **Log in** → **Sign in with GitHub** (рекомендуется; аккаунт `errorlogy` или личный с доступом к репо)
3. Убедитесь, что профиль заполнен (имя, affiliation при желании)

## Шаг 2 — Новая загрузка

1. Нажмите **+ New upload** (или **Upload** → **New**)
2. Перетащите **`zenodo/proto_agi_horizon_upload.zip`**  
   **или** загрузите отдельно:
   - `Kuznetsov_2026_Proto_AGI_Horizon.pdf` (обязательно)
   - `sources/proto_agi_horizon_arXiv_submission.tar.gz` (опционально)
   - `README.txt`, `metadata.yaml` (опционально, для архива)
3. Дождитесь завершения загрузки всех файлов

## Шаг 3 — Metadata (скопируйте поля)

### Upload type

| Поле | Значение |
|------|----------|
| **Resource type** | Publication → **Article** |

### Basic information

| Поле | Значение |
|------|----------|
| **Title** | `Proto-AGI Horizon: Endogenous Proactive Architecture, OMEGA Coherence, and Partial Evidence under C2 Ceiling` |
| **Publication date** | `2026-09-05` |
| **Description** | *(см. блок Abstract ниже — вставьте целиком)* |

**Description (Abstract) — скопировать:**

```
We present an operational research horizon for proto-AGI evaluation within the Endogenous Initiative Architecture (EIA) sci-flow program. Under this construction, general intelligence is not a benchmark score but a sustained dynamical regime in which cognitive goals arise from persistent internal state when X_t^trigger=0. We contrast passive architectures (reactive_only, schedule-entrained controls) with proactive endogenous candidates (full_eia, WoE carriers, oscillatory substrates). A twelve-member proto-AGI ensemble registers operational configs for Max consensus diagnostics: per-member potential Φ_i over (E, OMEGA, P, R), ensemble peak Φ_max=max_i Φ_i, and sustained four-parameter conjunction over window ΔT (thresholds TBD). We distinguish carrier Hz (20/30/42/70) from the bounded coherence scalar OMEGA_t, motivate an analog-waves bridge to Miller-lab traveling-wave theory, and report the OMEGA→ΔG bridge experiment (M-OMEGA-DELTA-G): F-OMEGA-DECOR confirmed (aggregate, C2) with OMEGA span 0.604, genesis span 0.0, fingerprint parity True. Partial empirical results—CF-4 do(Z), G2 E01 8/20 worlds, M-3D-EXPRESS 9/9 pass, M-O Tier C adjunct/shadow bridge—map onto the 3D evidence cube (D1 causal / D2 dynamic / D3 boundary). All harnesses operate under claim_allowed=false; active ceiling C2. This paper does not claim AGI*, τ_AGI, consciousness, or biological identity. Open work: pre-register θ_•, close G2 E01 20×3 domains, instrument N_H, and batch T-PROTO-01 ensemble Φ_i.
```

| Поле | Значение |
|------|----------|
| **Notes** | `Research Horizon Paper (non-final). C2-scoped partial evidence; claim_allowed=false; not AGI*. Repo companions (EIA framework v0.3, 3D Evidence Cube) at github.com/errorlogy/eia tag sci-flow-v0.3 — cited, not separate deposits.` |
| **Version** | `1.0.0` |

### Authors

| Name | Affiliation | Email (optional) |
|------|-------------|------------------|
| **Kuznetsov, Roman A.** | Anthemium | research@anthemium.tech |

### Keywords (по одному на строку)

```
proto-AGI
endogenous initiative
proactive architecture
OMEGA coherence
Max consensus
falsifiable evaluation
sci-flow
claim ladder
EIA
evidence cube
```

### License

| Поле | Значение |
|------|----------|
| **License** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** |

### Related / alternate identifiers

Добавьте в **Related identifiers** (тип URL):

| Relation | Identifier | Resource type |
|----------|------------|---------------|
| **Is supplement to** | `https://github.com/errorlogy/eia/tree/sci-flow-v0.3` | Software |
| **References** | `https://github.com/Anthemium/AGI-Manifesto` | Other |
| **References** | `https://github.com/errorlogy/namm-experiments` | Software |

### Communities (опционально)

Оставьте пустым, если нет одобренного community. Не блокирует публикацию.

## Шаг 4 — Publish (не Draft)

1. Проверьте превью PDF в Zenodo
2. Нажмите **Publish** (не **Save for later** / Draft, если нужен DOI сразу)
3. Скопируйте **DOI** вида `10.5281/zenodo.XXXXXXX`
4. Сохраните постоянную ссылку: `https://doi.org/10.5281/zenodo.XXXXXXX`

## Шаг 5 — Пост в X (после DOI)

Замените `YOUR_DOI` и при необходимости ссылку на PDF:

```
Proto-AGI Horizon — operational research horizon for endogenous proactive architecture under C2 evidence ceiling (claim_allowed=false; no AGI* claim).

Twelve-member ensemble, Max consensus over (E, OMEGA, P, R), OMEGA→ΔG bridge (F-OMEGA-DECOR confirmed aggregate), 3D evidence cube mapping.

PDF + sources: https://doi.org/YOUR_DOI
Code: https://github.com/errorlogy/eia/tree/sci-flow-v0.3

#protoAGI #EIA #sci-flow #openScience
```

Аккаунт для тега: [@AGIminister](https://x.com/agiminister)

## Troubleshooting (RU)

| Проблема | Решение |
|----------|---------|
| Файл не загружается | Лимит Zenodo ~50 GB; PDF ~600 KB — ок. Попробуйте один файл без zip |
| Нет кнопки Publish | Заполните обязательные поля: Title, Upload type, License |
| Нужен ORCID | Не обязателен; можно добавить позже в профиле |
| Draft без DOI | Только **Publish** резервирует DOI; Draft — без публичного DOI |
| arXiv endorsement | Используйте Zenodo как primary; arXiv — когда endorsement придёт |
| Устаревший PDF | `make arxiv-proto-agi-compile`; обновите копию в `zenodo/proto_agi_horizon/` |
| Zenodo vs GitHub release | Zenodo DOI — для цитирования статьи; GitHub tag `sci-flow-v0.3` — для кода |

---

# Guide (EN)

## When to use Zenodo vs arXiv

If **arXiv endorsement is blocked** or your account is not yet approved, **Zenodo is the primary publication path** for this paper. A Zenodo DOI provides a permanent citable record; arXiv can be added later as a mirror.

See also: `docs/ARXIV_SUBMISSION.md` (arXiv optional when endorsement is available).

## Step 1 — Sign in

1. Open [https://zenodo.org](https://zenodo.org)
2. **Log in** → **Sign in with GitHub**
3. Confirm profile name (and affiliation if desired)

## Step 2 — New upload

1. Click **+ New upload**
2. Drag **`zenodo/proto_agi_horizon_upload.zip`**  
   **or** upload separately:
   - `Kuznetsov_2026_Proto_AGI_Horizon.pdf` (required)
   - `sources/proto_agi_horizon_arXiv_submission.tar.gz` (optional)
3. Wait until all files finish uploading

## Step 3 — Metadata (copy-paste)

Use the same field values as the RU section above:

- **Upload type:** Publication → Article  
- **Title:** Proto-AGI Horizon: Endogenous Proactive Architecture, OMEGA Coherence, and Partial Evidence under C2 Ceiling  
- **Publication date:** 2026-09-05  
- **Description:** full abstract (RU section block)  
- **Author:** Kuznetsov, Roman A. — Anthemium — research@anthemium.tech  
- **Keywords:** proto-AGI, endogenous initiative, proactive architecture, OMEGA coherence, Max consensus, falsifiable evaluation, sci-flow, claim ladder, EIA, evidence cube  
- **License:** CC BY 4.0  
- **Related identifiers:** EIA `sci-flow-v0.3`, AGI-Manifesto, namm-experiments (table above)  
- **Version:** 1.0.0  

Reference files: `zenodo/proto_agi_horizon/metadata.yaml`, `datacite.xml`

## Step 4 — Publish (not Draft)

1. Preview the PDF  
2. Click **Publish** (not Save as draft if you need a DOI immediately)  
3. Copy DOI `10.5281/zenodo.XXXXXXX`  
4. Canonical URL: `https://doi.org/10.5281/zenodo.XXXXXXX`

## Step 5 — X post template (after DOI)

Replace `YOUR_DOI`:

```
Proto-AGI Horizon — operational research horizon for endogenous proactive architecture under C2 evidence ceiling (claim_allowed=false; no AGI* claim).

Twelve-member ensemble, Max consensus over (E, OMEGA, P, R), OMEGA→ΔG bridge (F-OMEGA-DECOR confirmed aggregate), 3D evidence cube mapping.

PDF + sources: https://doi.org/YOUR_DOI
Code: https://github.com/errorlogy/eia/tree/sci-flow-v0.3

#protoAGI #EIA #sci-flow #openScience
```

## Troubleshooting (EN)

| Issue | Fix |
|-------|-----|
| Upload fails | Retry single PDF; check network; zip is ~1 MB |
| No Publish button | Fill Title, Resource type, License |
| ORCID missing | Optional on Zenodo |
| Draft has no public DOI | Use **Publish** |
| arXiv blocked | Zenodo primary — see `docs/ARXIV_SUBMISSION.md` |
| Stale PDF | Recompile with `make arxiv-proto-agi-compile`; refresh zenodo copies |
| Citation | Use Zenodo DOI for the paper; GitHub tag for reproducible code |

---

## Synced sci-flow milestones (v0.4)

Same as `docs/ARXIV_SUBMISSION.md`: M-PROTO-AGI ensemble, M-OMEGA-DELTA-G, G2 E01 partial, M-3D-EXPRESS 9/9, D1×L3 ledger — all under **C2**, `claim_allowed=false`.

## Honest scope (do not overclaim in metadata)

- C2-scoped **partial** support for endogeneity at best  
- Proto-AGI ensemble is **operational**, not biological  
- No AGI\*, τ_AGI, or consciousness claims  
- θ\_E, θ\_Ω, θ\_P, θ\_R, ΔT remain **TBD**
