"""LoopScheduler — EIA runtime loops L-A…L-O with NAMM Hz-band analogies.

Stub for MVP-0: maps spec §13 loop frequencies to pipeline stages and
NAMM brainwave band references (research scaffolding, not literal EEG).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class PipelineStage(str, Enum):
    OBSERVATION_INGEST = "observation_ingest"
    SENSE_MAKING = "sense_making"
    MOTIVE_FORMATION = "motive_formation"
    INTENTION_GENESIS = "intention_genesis"
    INITIATIVE_EMISSION = "initiative_emission"
    CONTACT_GOVERNOR = "contact_governor"


@dataclass
class LoopSpec:
    loop_id: str
    hz_min: float
    hz_max: float
    eia_frequency: str
    pipeline_stage: PipelineStage | None
    namm_band_analogy: str | None = None
    namm_experiment: str | None = None
    namm_protocol: str | None = None


@dataclass
class LoopScheduler:
    """Resolve which EIA loops are active for a pipeline stage."""

    loops: list[LoopSpec] = field(default_factory=list)

    @classmethod
    def from_config(cls, path: Path | None = None) -> LoopScheduler:
        if path is None:
            path = Path(__file__).resolve().parents[3] / "config" / "namm_crosswalk.yaml"
        data: dict[str, Any] = {}
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

        loops_cfg = data.get("loop_scheduler", {}).get("loops", {})
        specs: list[LoopSpec] = []
        for loop_id, cfg in loops_cfg.items():
            hz = cfg.get("hz_range", [0, 0])
            stage_raw = cfg.get("stage")
            stage = PipelineStage(stage_raw) if stage_raw else None
            specs.append(
                LoopSpec(
                    loop_id=loop_id,
                    hz_min=float(hz[0]),
                    hz_max=float(hz[1]) if len(hz) > 1 else float(hz[0]),
                    eia_frequency=cfg.get("eia_frequency", ""),
                    pipeline_stage=stage,
                    namm_band_analogy=cfg.get("namm_band_analogy"),
                    namm_experiment=cfg.get("namm_experiment"),
                    namm_protocol=cfg.get("namm_protocol"),
                )
            )
        return cls(loops=specs)

    def loops_for_stage(self, stage: PipelineStage) -> list[LoopSpec]:
        return [lp for lp in self.loops if lp.pipeline_stage == stage]

    def stage_schedule(self, stage: PipelineStage) -> dict[str, Any]:
        """Summary for causal trace / demo output."""
        active = self.loops_for_stage(stage)
        return {
            "pipeline_stage": stage.value,
            "active_loops": [lp.loop_id for lp in active],
            "namm_experiments": [
                lp.namm_experiment for lp in active if lp.namm_experiment
            ],
            "hz_bands": [
                {
                    "loop": lp.loop_id,
                    "hz_range": [lp.hz_min, lp.hz_max],
                    "namm_band_analogy": lp.namm_band_analogy,
                }
                for lp in active
            ],
        }
