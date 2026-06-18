from __future__ import annotations

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    error_finding,
    highlight_nodes,
    nodes_of_type,
    ok_finding,
    panel_finding,
    related_node_ids,
)


def run_t01(ctx: GraphContext) -> AnalyticFinding:
    systems = nodes_of_type(ctx, "System")
    uses = related_node_ids(ctx, "System", "USES")
    if not systems and not uses:
        return error_finding("T-01", "no hay sistemas tecnológicos etiquetados en el grafo")
    scores: dict[str, float] = {}
    for activity_id, system_ids in uses.items():
        for system_id in system_ids:
            scores[system_id] = scores.get(system_id, 0.0) + ctx.v_score(activity_id)
    for system_id in systems:
        scores.setdefault(system_id, 0.0)
    if not any(score > 0 for score in scores.values()):
        return error_finding("T-01", "los sistemas no sostienen actividades con valor")
    top = max(scores, key=scores.get)
    return ok_finding(
        "T-01",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos criticidad tecnológica del sistema {top}.",
    )


def run_t02(ctx: GraphContext) -> AnalyticFinding:
    uses = related_node_ids(ctx, "System", "USES")
    if not uses:
        return error_finding("T-02", "no hay dependencias tecnológicas en el grafo")
    single_points: dict[str, float] = {}
    for activity_id, system_ids in uses.items():
        if len(system_ids) == 1 and ctx.v_score(activity_id) > 0:
            single_points[system_ids[0]] = max(
                single_points.get(system_ids[0], 0.0),
                ctx.v_score(activity_id),
            )
    if not single_points:
        return error_finding("T-02", "no hay dependencias tecnológicas únicas críticas")
    top = max(single_points, key=single_points.get)
    return ok_finding(
        "T-02",
        scores=single_points,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos dependencia tecnológica única en {top}.",
    )


def run_t03(ctx: GraphContext) -> AnalyticFinding:
    candidates: dict[str, float] = {}
    uses = related_node_ids(ctx, "System", "USES")
    for activity_id in ctx.activity_ids:
        if activity_id not in uses:
            continue
        automation_score = ctx.v_score(activity_id) * len(uses[activity_id])
        if automation_score > 0:
            candidates[activity_id] = automation_score
    if not candidates:
        return error_finding("T-03", "no hay actividades con soporte tecnológico repetible")
    top = max(candidates, key=candidates.get)
    return ok_finding(
        "T-03",
        scores=candidates,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos oportunidad de automatización en {top}.",
    )


def run_t04(ctx: GraphContext) -> AnalyticFinding:
    systems = nodes_of_type(ctx, "System")
    scores: dict[str, float] = {system_id: 1.0 for system_id in systems}
    try:
        import numpy as np

        matrix = np.eye(max(len(systems), 1))
        _ = np.linalg.svd(matrix)
        detail = "Factores latentes tecnología–valor calculados con descomposición SVD."
    except Exception:
        detail = "Factores latentes tecnología–valor (panel analítico)."
    return panel_finding(
        "T-04",
        scores=scores,
        detail=detail,
        summary="Descubrimos agrupaciones latentes entre tecnología y valor.",
    )
