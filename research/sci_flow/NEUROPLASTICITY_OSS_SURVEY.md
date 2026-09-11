# Neuroplasticity OSS Survey — EIA Sci-Flow Notes

**Status:** `SURVEY` (2026-09-01) — literature scan, not vendor adoption  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** **C2** — explore adjunct only; no AGI\* claim from OSS survey alone

> **Neuraxon** and **Graphitti** (Tier **A** endogenous-loop substrates) are covered separately in [`NEUROPLASTICITY_EIA_APPLICATION.md`](NEUROPLASTICITY_EIA_APPLICATION.md) (install + EIA mapping).

---

## Резюме (RU)

Обзор **27** OSS-репозиториев (GitHub + Hugging Face) по нейропластичности и формированию связей — **без** Neuraxon/Graphitti. Категории: STDP/Hebbian, рост коннектома, динамические синапсы, GNN-коннектомы, HF-модели/датасеты. Для каждого: URL, лицензия, tier релевантности EIA (A/B/C/none). Tier **A** зарезервирован за Neuraxon/Graphitti; здесь максимум **B** (NEST structural plasticity, Brian2, BindsNET, Inferno, DeNSE, NETMORPH, NeuroDevSim, Cerebrum).

---

## EIA relevance tiers

| Tier | Meaning |
|------|---------|
| **A** | Direct endogenous-loop substrate — structural plasticity + multi-timescale dynamics (Neuraxon, Graphitti only; see linked doc) |
| **B** | Strong overlap — local plasticity rules, connectome growth, or inferring connectivity from activity |
| **C** | Partial overlap — recurrent SNN, neuromorphic deploy, rule-based wiring, temporal graph models |
| **none** | fMRI connectome ML / datasets / surrogate-gradient training; not biological connection formation |

---

## 1. STDP / Hebbian (spike-timing plasticity)

| Name | URL | One-line | License | EIA tier |
|------|-----|----------|---------|----------|
| **Brian2** | https://github.com/brian-team/brian2 | Clock-driven SNN simulator with `Synapses` STDP, Hebbian, and homeostatic rules | Other | **B** |
| **BindsNET** | https://github.com/BindsNET/bindsnet | PyTorch SNN library with STDP learning for ML/RL without backprop | AGPL-3.0 | **B** |
| **Inferno** | https://github.com/mdominijanni/inferno | Extensible PyTorch SNN: STDP, triplet STDP, MSTDP, and learnable delays | BSD-3-Clause | **B** |
| **Norse** | https://github.com/norse/norse | PyTorch spiking + learning library for event-driven recurrent networks | LGPL-3.0 | **C** |
| **SpykeTorch** | https://github.com/miladmozafari/SpykeTorch | High-speed STDP/CNN framework for spiking networks | GPL-3.0 | **C** |
| **CoNeX** | https://github.com/cnrl/CoNeX | PyTorch/Pymonntorch cortical columns with STDP/RSTDP/iSTDP modules | MIT | **C** |

---

## 2. Connectome growth (morphogenesis, wiring rules)

| Name | URL | One-line | License | EIA tier |
|------|-----|----------|---------|----------|
| **DeNSE** | https://github.com/SENeC-Initiative/DeNSE | 2D neuronal growth simulator: morphogenesis and emergent network wiring | GPL-2.0 | **B** |
| **NETMORPH** | https://github.com/randalkoene/netmorph | Stochastic 3D morphology generator; synapses form on branch proximity | GPL-3.0 | **B** |
| **NeuroDevSim** | https://github.com/CNS-OIST/NeuroDevSim | Parallel 3D morphology growth and microcircuit emergence (growth cones, migration) | GPL-3.0 | **B** |
| **NetPyNE** | https://github.com/suny-downstate-medical-center/netpyne | Python → NEURON: declarative rule-based population connectivity at scale | MIT | **C** |

---

## 3. Dynamic synapses (structural + weight plasticity platforms)

| Name | URL | One-line | License | EIA tier |
|------|-----|----------|---------|----------|
| **NEST** | https://github.com/nest/nest-simulator | Large-scale SNN simulator with **structural plasticity** (synapse creation/deletion) | GPL-2.0 | **B** |
| **BrainPy** | https://github.com/brainpy/BrainPy | JAX/PyTorch differentiable brain dynamics; STP, STDP, network models | GPL-3.0 | **C** |
| **snnTorch** | https://github.com/jeshraghian/snntorch | PyTorch SNN with surrogate gradients (local plasticity via BindsNET/Inferno) | MIT | **none** |
| **Rockpool** | https://github.com/synsense/rockpool | SNN training/deploy across Torch/JAX/Brian2 → neuromorphic HW (Dynap-SE2, Xylo) | AGPL-3.0 | **C** |
| **Lava** | https://github.com/lava-nc/lava | Intel neuromorphic framework (Loihi); event-driven networks with on-chip plasticity | Other | **C** |
| **Nengo** | https://github.com/nengo/nengo | Universal neural simulator with spiking + learning rules and neuromorphic export | Other | **C** |
| **ANNarchy** | https://github.com/ANNarchy/ANNarchy | ANN → C++/OpenCL compiler with STDP and synaptic state variables | GPL-2.0 | **C** |

---

## 4. GNN connectomes (inference, evolution, foundation models)

| Name | URL | One-line | License | EIA tier |
|------|-----|----------|---------|----------|
| **Cerebrum** | https://github.com/bxptr/cerebrum | Hodgkin–Huxley neurons + GNN to infer synaptic connectivity from activity | — | **B** |
| **BrainGFM** | https://github.com/weixinxu666/BrainGFM | Graph foundation model (GCL + GMAE) for fMRI connectome representation | — | **none** |
| **EvoGraphNet** | https://github.com/basiralab/EvoGraphNet | GAN predicting temporal evolution of brain graphs | — | **C** |
| **MultigraphGNet** | https://github.com/basiralab/MultigraphGNet | GNN augmentation of multigraph connectomes from a single graph | — | **none** |
| **FDSyn-GNN** | https://github.com/ZHChen-294/FDSyn-GNN | Synaptic graph Transformer for rs-fMRI connectivity | — | **none** |
| **LCM** (`brain_network_decoder`) | https://github.com/Chrisa142857/brain_network_decoder | 1.2B decoder-only fMRI foundation model for connectome analysis (AAAI-26) | — | **none** |

---

## 5. Hugging Face (models and datasets)

| Name | URL | One-line | License | EIA tier |
|------|-----|----------|---------|----------|
| **CortexMAE** | https://huggingface.co/medarc/CortexMAE · https://github.com/MedARC-AI/CortexMAE | fMRI foundation model (flat map, Schaefer-400); code + 50+ checkpoints | CC-BY-NC-4.0 (model) / Apache-2.0 (code) | **none** |
| **Brain-JEPA** | https://huggingface.co/eugenehp/brainjepa · https://github.com/hzlab/Brain-JEPA | ViT foundation model for parcellated fMRI dynamics (NeurIPS 2024) | — | **none** |
| **multi-modal-derived-brain-network** | https://huggingface.co/datasets/pakkinlau/multi-modal-derived-brain-network | PPMI connectivity graphs (Schaefer100, AAL116, …) for GNN training | — | **none** |
| **scwbd-anatomy-prior-414** | https://huggingface.co/datasets/jacob-valdez/scwbd-anatomy-prior-414 | Schaefer-400 structural connectome + geometry + delays as dynamics prior | CC-BY-4.0 | **C** |

---

## Sci-flow mapping

| Cube axis | Relevant OSS categories | Notes |
|-----------|-------------------------|-------|
| **D1** Causal | STDP/Hebbian, dynamic synapses (NEST structural) | Plasticity rules as `do(Z)`-like interventions on weights/topology |
| **D2** Dynamic | All Tier B/C | Recurrent loops, homeostasis, multi-timescale plasticity |
| **D3** Boundary | — | No direct governor mapping; explore only under C2 ceiling |

**Do not conflate:** BrainGFM, CortexMAE, LCM analyze *already formed* functional connectomes from fMRI — not biological synapse formation.

---

## Cross-links

| Doc | Role |
|-----|------|
| [`NEUROPLASTICITY_EIA_APPLICATION.md`](NEUROPLASTICITY_EIA_APPLICATION.md) | Tier A vendors: Neuraxon + Graphitti install and EIA mapping |
| [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) | M-O oscillatory explore adjunct (Tier C metrics pool) |
| [`ENDOGENEITY_METRICS_POOL.md`](ENDOGENEITY_METRICS_POOL.md) | EIA metric tiers A–E (distinct from OSS survey tiers above) |
| [`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md) | Evidence cube scaffold |

---

## Selection guide

| Task | Start with |
|------|------------|
| STDP/Hebbian in Python | **Brian2**, **BindsNET**, **Inferno** |
| Physical connectome growth | **DeNSE**, **NETMORPH**, **NeuroDevSim** |
| Large-scale structural plasticity | **NEST** |
| Endogenous growth + loops (Tier A) | **Neuraxon**, **Graphitti** — see linked application doc |
| Neuromorphic deploy | **Rockpool**, **Lava** |
| Infer connectivity from dynamics | **Cerebrum** |
| fMRI connectome embeddings | **CortexMAE**, **Brain-JEPA** |
