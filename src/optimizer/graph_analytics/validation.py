from __future__ import annotations

from dataclasses import dataclass

from optimizer.graph_analytics.graph_bridge import GraphContext


@dataclass(frozen=True)
class PreflightResult:
    ok: bool
    warnings: tuple[str, ...]


def preflight_graph(context: GraphContext) -> PreflightResult:
    """Emit warnings for missing ontology labels required by analytics."""
    warnings: list[str] = []

    for node_id in sorted(context.flow_graph.nodes):
        node_type = context.flow_graph.nodes[node_id].get("node_type")
        if node_type != "Event":
            continue
        properties = context.node_properties(node_id)
        if "event_type" not in properties:
            warnings.append(
                f"Advertencia: el Evento {node_id} no tiene la propiedad event_type"
            )

    return PreflightResult(ok=not warnings, warnings=tuple(warnings))


def analytic_error_message(detail: str) -> str:
    """Spanish error string for runner failures."""
    return f"Datos insuficientes: {detail}"
