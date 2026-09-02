# Research vendor dependencies

Third-party packages cloned for **sci-flow adjunct research** (Tier C explore). **Not** merged into `src/eia/` runtime. Claim ceiling **C2**; no AGI* claim.

| Package | Path | Source | Pinned commit | Role |
|---------|------|--------|---------------|------|
| **Neuraxon** | `neuraxon/` | [DavidVivancos/Neuraxon](https://github.com/DavidVivancos/Neuraxon) | `21eff5c` | Structural plasticity, multi-timescale synapses, recurrent loops |
| **Graphitti** | `graphitti/` | [UWB-Biocomputing/Graphitti](https://github.com/UWB-Biocomputing/Graphitti) | `b96e96c` | Growth-phase topology + STDP; endogenously active neurons |

Application map: [`../sci_flow/NEUROPLASTICITY_EIA_APPLICATION.md`](../sci_flow/NEUROPLASTICITY_EIA_APPLICATION.md).

---

## Neuraxon

**Language:** Python 3.8+  
**Dependencies:** none (core `neuraxon2.py` is pure Python; optional CUDA in `cuNxon/`)

```powershell
# Smoke (from repo root)
python research/sci_flow/smoke_vendor_neuroplasticity.py
```

**Manual import:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("research/vendor/neuraxon")))
from neuraxon2 import NeuraxonNetwork, NetworkParameters

net = NeuraxonNetwork(NetworkParameters(num_input_neurons=3, num_hidden_neurons=5, num_output_neurons=2))
for _ in range(10):
    net.simulate_step()
```

**Install note:** cloned with `git clone --depth 1`; `.git` removed for monorepo vendor snapshot. Re-sync: re-clone and record new SHA here.

---

## Graphitti

**Language:** C++17  
**Binary:** `cgraphitti` (CPU) or `ggraphitti` (CUDA) — see upstream `CMakeLists.txt`  
**Build:** CMake ≥ 3.12; CPU default (`ENABLE_CUDA=NO`) or GPU (`ENABLE_CUDA=YES`)

### Linux / WSL (recommended)

```bash
# Prerequisites (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y cmake build-essential

cd research/vendor/graphitti
mkdir -p build && cd build
cmake -D ENABLE_CUDA=NO ..
make -j
./cgraphitti -c ../configfiles/test-tiny.xml
# XmlRecorder output: build/Output/Results/test-tiny-out.xml
```

### Windows native (optional)

1. Install [CMake](https://cmake.org/download/) and **Visual Studio Build Tools** (C++ workload).
2. From a VS Developer shell or PATH with `cl.exe`:

```powershell
cd research\vendor\graphitti
mkdir build -Force; cd build
cmake -D ENABLE_CUDA=NO ..
cmake --build . --config Release
.\Release\cgraphitti.exe -c ..\configfiles\test-tiny.xml
```

### Sci-flow witness harness

```powershell
python research/sci_flow/run_graphitti_witness.py
# → research/sci_flow/M-MO_graphitti_witness_2026-09-02.json (D2×L3, tier C)
```

Parses XmlRecorder spike-time matrices for population spike-rate metrics when `cgraphitti` is built; otherwise emits `build_blocked` stub (`witness_kind: stub`) with upgrade plan.

### Linux CI (M-GRAPHITTI-CI)

Workflow: [`.github/workflows/graphitti-witness.yml`](../../.github/workflows/graphitti-witness.yml)

```bash
# Local Linux equivalent
bash scripts/build_graphitti.sh
GRAPHITTI_CI=1 python research/sci_flow/run_graphitti_witness.py
# witness_kind → binary_ok when simulation status is ok
```

CI uploads artifact `graphitti-witness-<sha>` with `cgraphitti`, witness JSON, and `test-tiny-out.xml`. To use locally without rebuilding:

```bash
mkdir -p research/sci_flow/.ci-artifacts/graphitti
cp cgraphitti research/sci_flow/.ci-artifacts/graphitti/
python research/sci_flow/run_graphitti_witness.py
```

Or set `GRAPHITTI_BINARY=/path/to/cgraphitti` / `GRAPHITTI_BUILD_DIR=/path/to/build`.

**Host status (2026-09-02, tick M-O-GRAPHITTI-BIN):**

| Environment | cmake | g++ | Result |
|-------------|-------|-----|--------|
| Windows PATH | **no** | n/a | Build blocked |
| WSL Ubuntu 24.04 | **no** | **no** | apt install blocked (offline / archive unreachable) |

Config smoke (no binary): `test-tiny.xml` has `ConnGrowth` + `AllDSSynapses` + starter neurons (`starter_vthresh` < `Vthresh`). Regression reference: `graphitti/Testing/RegressionTesting/GoodOutput/Cpu/test-tiny-out.xml`.

**Features relevant to EIA:** `ConnGrowth` (radius-based edge birth/death), STDP edge classes, starter neurons with low `Vthresh` for spontaneous activity ([configuration docs](graphitti/docs/User/configuration.md)).

---

## Discipline

- Vendor code is **read/run in research** only; integration hypotheses use `do(O)` / shadow arms — see application doc.
- After substantive sci-flow edits: `python scripts/check_sci_tier0.py`.
