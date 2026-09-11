# Kairologos Standalone Research

**Отдельная ветка исследований — НЕ EIA claim ladder.**

This folder hosts theory-native experiments for **Kairologos / Topological ASI Resonance**
on the theory's own terms. It is intentionally separate from:

- `research/kairologos_experiments/` (EIA Tier C battery, falsifiers, `claim_allowed=false`)
- EIA proof mechanics, shadow_bridge, T-AGENT harnesses

## Theory source

External canonical tractate (not vendored into repo):

`c:\Users\lawye\.gemini\antigravity\brain\f72138c9-dd57-4d05-91f8-3ef112ab55fb\THEORY_OF_TOPOLOGICAL_ASI_RESONANCE.md`

Reference demos (quick-galileo):

`c:\Users\lawye\Documents\antigravity\quick-galileo\`

## Run experiments

```powershell
cd C:\Users\Public\PROACTIVE_AI
python research/kairologos_standalone/run_t_kai_01.py
python research/kairologos_standalone/run_t_kai_02.py
python research/kairologos_standalone/run_t_kai_05.py
python research/kairologos_standalone/run_t_kai_06.py
pytest research/kairologos_standalone/tests -q
```

## Artifacts

JSON + MD outputs land in `artifacts/` with prefix `T-KAI-*`.

See `RESEARCH_PROGRAM.md` for hypothesis map and roadmap T-KAI-01..10.
