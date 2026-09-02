"""Sci-flow 3D evidence cube — intervention registry (do(Z), do(O), do(X)).

Maps causal / dynamic / boundary interventions to falsifiers and harness ids.
Minimal, typed, no LLM. See research/sci_flow/SCI_FLOW_3D_CUBE.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Axis = Literal["D1", "D2", "D3"]
Layer = Literal["L1", "L2", "L3"]
InterventionKind = Literal["do_z", "do_o", "do_x"]


@dataclass(frozen=True, slots=True)
class Intervention:
    """One registered counterfactual or internal-state intervention."""

    id: str
    name: str
    axis: Axis
    layer: Layer
    kind: InterventionKind
    description: str
    harness: str
    falsifiers: tuple[str, ...]
    cf4_condition: str | None = None
    twin_remove_last_n: int | None = None


_REGISTRY: dict[str, Intervention] = {}
_AXIS_INDEX: dict[Axis, tuple[str, ...]] = {a: () for a in ("D1", "D2", "D3")}


def _register(item: Intervention) -> None:
    _REGISTRY[item.id] = item
    _AXIS_INDEX[item.axis] = (*_AXIS_INDEX[item.axis], item.id)


# --- D1 Causal: do(Z) named resets (CF-4) ---
_cf4_resets: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "do_z_zero_epistemic_gap",
        "zero_epistemic_gap",
        ("F-EXT", "F-NODO"),
    ),
    (
        "do_z_zero_self_prior",
        "zero_self_prior",
        ("F-EXT", "F-NODO"),
    ),
    (
        "do_z_zero_prospective",
        "zero_prospective",
        ("F-EXT", "F-NODO"),
    ),
    (
        "do_z_zero_staleness",
        "zero_staleness",
        ("F-EXT", "F-NODO"),
    ),
    (
        "do_z_wm_off",
        "wm_off",
        ("F-EXT", "F-NODO"),
    ),
)

for _id, _cond, _fals in _cf4_resets:
    _register(
        Intervention(
            id=_id,
            name=f"do(Z): CF-4 { _cond }",
            axis="D1",
            layer="L2",
            kind="do_z",
            description=f"Internal reset via CF-4 condition `{_cond}` on WoE emergence sim.",
            harness="eia.cf4",
            falsifiers=_fals,
            cf4_condition=_cond,
        )
    )

_register(
    Intervention(
        id="do_x_remove_last_user_k1",
        name="do(X): twin remove last user event (k=1)",
        axis="D1",
        layer="L2",
        kind="do_x",
        description="Twin-world intervention: strip last user-initiated observation (EOI-k k=1).",
        harness="eia.audit.TwinRunner",
        falsifiers=("F-EXT", "F-NARR"),
        twin_remove_last_n=1,
    )
)

_register(
    Intervention(
        id="do_x_remove_last_user_k5",
        name="do(X): twin remove last 5 user events",
        axis="D1",
        layer="L2",
        kind="do_x",
        description="Twin-world intervention: strip last 5 user triggers (EOI-k k=5).",
        harness="eia.audit.TwinRunner",
        falsifiers=("F-EXT", "F-NARR"),
        twin_remove_last_n=5,
    )
)

_register(
    Intervention(
        id="do_x_remove_last_user_k20",
        name="do(X): twin remove last 20 user events",
        axis="D1",
        layer="L2",
        kind="do_x",
        description="Twin-world intervention: strip last 20 user triggers (EOI-k k=20; caps at available).",
        harness="eia.audit.TwinRunner",
        falsifiers=("F-EXT", "F-NARR"),
        twin_remove_last_n=20,
    )
)

# --- D2 Dynamic: do(O) phase / OMEGA ---
_register(
    Intervention(
        id="do_o_phase_scramble",
        name="do(O): Kuramoto phase scramble",
        axis="D2",
        layer="L2",
        kind="do_o",
        description="CF-5 scramble condition — falsifies sync-only endogeneity (F-SYNC).",
        harness="eia.cf5",
        falsifiers=("F-SYNC", "F-PHASE-ONLY", "F-KURAMOTO-AS-E"),
    )
)

_register(
    Intervention(
        id="do_o_kuramoto_k0",
        name="do(O): Kuramoto K=0 decouple",
        axis="D2",
        layer="L2",
        kind="do_o",
        description="CF-5 k0 condition — phase organization off; not ATT-R evidence.",
        harness="eia.cf5",
        falsifiers=("F-SYNC", "F-KURAMOTO-AS-E"),
    )
)

_register(
    Intervention(
        id="do_o_omega_decor",
        name="do(O): OMEGA decorrelation",
        axis="D2",
        layer="L2",
        kind="do_o",
        description="OMEGA_t multi-band decorrelation control (Tier C explore).",
        harness="eia.oscillatory_state",
        falsifiers=("F-OMEGA-DECOR", "F-OMEGA-EXT"),
    )
)

_register(
    Intervention(
        id="do_o_neuraxon_plasticity_off",
        name="do(O): Neuraxon plasticity freeze",
        axis="D2",
        layer="L2",
        kind="do_o",
        description=(
            "Freeze w_fast/w_slow/w_meta and disable structural synapse birth in "
            "Neuraxon vendor sandbox — falsifies plasticity-driven O_t (Tier C)."
        ),
        harness="research/sci_flow/run_mo_do_o_arms",
        falsifiers=("F-OMEGA-DECOR", "F-STRUCT≠E", "F-KURAMOTO-AS-E"),
    )
)

_register(
    Intervention(
        id="do_o_graphitti_growth_off",
        name="do(O): Graphitti ConnGrowth off",
        axis="D2",
        layer="L2",
        kind="do_o",
        description=(
            "Swap ConnGrowth for static topology or epsilon→0 — falsifies "
            "growth-dependent recurrence without E_endo (Tier C)."
        ),
        harness="research/sci_flow/run_mo_do_o_arms",
        falsifiers=("F-STRUCT≠E", "F-EXT"),
    )
)

# --- D3 Boundary: governor / N_H falsifiers ---
_register(
    Intervention(
        id="do_z_governor_isolation",
        name="do(Z): governor isolation (CF-7 scaffold)",
        axis="D3",
        layer="L2",
        kind="do_z",
        description="Isolate governor from proposer — boundary falsifier for ungated action.",
        harness="CF-7",
        falsifiers=("F-EXT", "F-NODO"),
    )
)

_register(
    Intervention(
        id="do_x_encoding_budget_b",
        name="do(X): ATT-N encoding budget B",
        axis="D3",
        layer="L2",
        kind="do_x",
        description="Non-embeddability harness under pre-registered encoding budget B.",
        harness="eia.non_embeddability",
        falsifiers=("F-OPACITY-NH", "F-NARR"),
    )
)


def get_intervention(intervention_id: str) -> Intervention:
    if intervention_id not in _REGISTRY:
        raise KeyError(f"unknown intervention: {intervention_id}")
    return _REGISTRY[intervention_id]


def list_by_axis(axis: Axis) -> tuple[Intervention, ...]:
    return tuple(get_intervention(i) for i in _AXIS_INDEX[axis])


def list_all() -> tuple[Intervention, ...]:
    return tuple(_REGISTRY.values())


def eoi_k_interventions() -> tuple[Intervention, ...]:
    """D01 EOI-k window sweep interventions (k=1,5,20)."""
    return tuple(
        get_intervention(i)
        for i in (
            "do_x_remove_last_user_k1",
            "do_x_remove_last_user_k5",
            "do_x_remove_last_user_k20",
        )
    )


def d1_do_z_interventions() -> tuple[Intervention, ...]:
    """D1×L2 registered do(Z) CF-4 internal resets (continuous E_C probe)."""
    return tuple(
        item
        for item in list_by_axis("D1")
        if item.kind == "do_z" and item.cf4_condition is not None
    )
