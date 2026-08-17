"""ASCII visualization of BeliefField tension gradients."""

from __future__ import annotations

from eia.beliefs import BeliefField


def render_field_heatmap(field: BeliefField, width: int = 40) -> str:
    """Render drive-relevant field state as ASCII heatmap."""
    gradients = field.gradient_snapshot()
    lines = ["BeliefField Tension Heatmap", "=" * (width + 12), ""]

    for name, value in gradients.items():
        filled = int(value * width)
        bar = "#" * filled + "-" * (width - filled)
        lines.append(f"  {name:12s} [{bar}] {value:.3f}")

    lines.append("")
    lines.append("Belief nodes:")
    for bid, belief in field.beliefs.items():
        unc = belief.uncertainty
        marker = "!" if unc > 0.6 else " "
        lines.append(f"  {marker} {bid:20s} {belief.subject:15s} u={unc:.2f}  {belief.claim[:40]}")

    if field.contradictions:
        lines.append("")
        lines.append("Contradictions:")
        for a, b, topic in field.contradictions:
            lines.append(f"  * {a} <-> {b}  ({topic})")

    return "\n".join(lines)
