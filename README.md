# Endogenous Initiative Architecture (EIA)

**Program name:** **Endogenous Initiative Architecture (EIA)** · *RU:*     
**Legacy / benchmark prefix:** PROACTIVE AI · **PAI-EI** benchmark

Research platform for AI systems with **endogenous initiative** (P4–P5 proactivity) — the ability to form internal reasons, questions, and bounded actions without a current human request, based on memory, sensory context, uncertainty, and a value model.

**Status:** v0.1 — architecture specification (prototype in development)  
**Implementation plan:** [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md)

---

## EN — Overview

| File / directory | Purpose |
|---|---|
| [`PROACTIVE_AI_Endogenous_Initiative_Architecture_EN_v0.1.md`](./PROACTIVE_AI_Endogenous_Initiative_Architecture_EN_v0.1.md) | Full architecture specification (English) |
| [`PROACTIVE_AI_Endogenous_Initiative_Architecture_RU_v0.1.md`](./PROACTIVE_AI_Endogenous_Initiative_Architecture_RU_v0.1.md) | Full architecture specification (Russian) |
| [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md) | Implementation & development plan (R0–R11, MVP-0–3, repo strategy) |
| [`docs/NAMM_INTEGRATION.md`](./docs/NAMM_INTEGRATION.md) | Integration with [NAMM experiments](https://github.com/errorlogy/namm-experiments) |
| [`experiments/PAI-EI-E0-001/`](./experiments/PAI-EI-E0-001/) | First experiment scaffold (Twin World Test) |
| [`.env.example`](./.env.example) | Environment variable template for future implementation |

### Related research (Anthemium lineage)

| Program | Repository | Role |
|---------|------------|------|
| **NAMM** | [errorlogy/namm-experiments](https://github.com/errorlogy/namm-experiments) | Verification-first machine-native math discovery |
| **EIA** (PROACTIVE AI) | this repo → [`errorlogy/eia`](https://github.com/errorlogy/eia) | Endogenous initiative architecture (P4–P5) |

Both programs share falsifiable gates, causal traces, and experiment manifests under the [Anthemium](https://anthemium.tech) research frame.

### Architecture (brief)

- **P4–P5 proactivity** — endogenous motives, not timers or request prediction
- **Causal trace** — every contact traced from observation to action
- **Dual-controller** — Contact Governor and Action Governor independent of LLM
- **Phased roadmap** — digital-only MVP-0 → bounded embodiment MVP-3

See [EN specification](./PROACTIVE_AI_Endogenous_Initiative_Architecture_EN_v0.1.md) §5, §26–27.

### Quick start (NAMM sibling clone)

```powershell
git clone https://github.com/errorlogy/namm-experiments.git ..\namm-experiments
cd ..\namm-experiments
python -m pip install -e ".[dev,nd]"
python -m pytest tests/ -v
```

Integration details: [`docs/NAMM_INTEGRATION.md`](./docs/NAMM_INTEGRATION.md).

---

## RU — 

**Endogenous Initiative Architecture (EIA)** · *  *

   AI-  ** ** (P4–P5) —        ,       ,  ,    .

** :** [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md)

|  /  |  |
|---|---|
| [`PROACTIVE_AI_Endogenous_Initiative_Architecture_RU_v0.1.md`](./PROACTIVE_AI_Endogenous_Initiative_Architecture_RU_v0.1.md) |    (RU) |
| [`PROACTIVE_AI_Endogenous_Initiative_Architecture_EN_v0.1.md`](./PROACTIVE_AI_Endogenous_Initiative_Architecture_EN_v0.1.md) | Full architecture specification (EN) |
| [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md) |     (R0–R11, MVP-0–3) |
| [`docs/NAMM_INTEGRATION.md`](./docs/NAMM_INTEGRATION.md) |   [NAMM experiments](https://github.com/errorlogy/namm-experiments) |
| [`experiments/PAI-EI-E0-001/`](./experiments/PAI-EI-E0-001/) |    (Twin World Test) |
| [`.env.example`](./.env.example) |    |

###   ( Anthemium)

|  |  |  |
|-----------|-------------|------|
| **NAMM** | [errorlogy/namm-experiments](https://github.com/errorlogy/namm-experiments) | Verification-first machine-native math discovery |
| **EIA** (PROACTIVE AI) |   → `[`errorlogy/eia`](https://github.com/errorlogy/eia) |    (P4–P5) |

   falsifiable gates,    experiment manifests     [Anthemium](https://anthemium.tech).

###  ()

- **P4–P5 ** —  ,      
- ** ** —       
- **Dual-controller** — Contact Governor  Action Governor   LLM
- ** roadmap** —  digital-only MVP-0  bounded embodiment MVP-3

: [RU ](./PROACTIVE_AI_Endogenous_Initiative_Architecture_RU_v0.1.md) §5, §26–27.

###   ( NAMM )

```powershell
git clone https://github.com/errorlogy/namm-experiments.git ..\namm-experiments
cd ..\namm-experiments
python -m pip install -e ".[dev,nd]"
python -m pytest tests/ -v
```

 : [`docs/NAMM_INTEGRATION.md`](./docs/NAMM_INTEGRATION.md).

---

## Prerequisites / 

At documentation stage (v0.1), no additional software is required.

For future MVP-0 implementation:

- **Python 3.11+** — services and simulator
- **PostgreSQL 15+** (pgvector optional) — state and memory
- **Docker / Docker Compose** — local lab
- **Git** — version control

Optional (MVP-1+): NATS/Kafka, Temporal, Vault, OpenTelemetry.

NAMM requires **Python 3.12+** — see [namm-experiments README](https://github.com/errorlogy/namm-experiments).

---

## Environment /  

Copy `.env.example` to `.env` when implementation begins. `.env` is **not committed**.

| Group | Purpose |
|---|---|
| `LLM_*`, `OPENAI_API_KEY` | Cognitive core provider |
| `POSTGRES_*`, `DATABASE_URL` | State and memory |
| `CONTACT_*` | Proactive contact limits (safety) |
| `SIMULATOR_*`, `CAUSAL_TRACE_*` | Research simulator mode |
| `OTEL_*` | Tracing and observability |

---

## Security / 

- Store secrets only in `.env` or external vault (HashiCorp Vault / KMS)
- Do not commit API keys, passwords, certificates, or DB dumps
- Before push: `git status` must not show `.env`, `node_modules/`, `venv/`, etc.

---

## Author / 

**Roman Kuznetsov**

- Site: [anthemium.tech](https://anthemium.tech)
- X: [@AGIminister](https://x.com/AGIminister)

---

## License / 

License not specified. Add `LICENSE` before public release if needed.

## Contributing / 

Early-stage repository. Coordinate architecture changes with specification version (currently v0.1).
