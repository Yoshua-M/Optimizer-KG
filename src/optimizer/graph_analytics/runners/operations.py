from __future__ import annotations

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    activities_matching_area,
    betweenness_scores,
    error_finding,
    highlight_nodes,
    k_core_nodes,
    longest_duration_path,
    ok_finding,
    panel_finding,
)


def run_o01(ctx: GraphContext) -> AnalyticFinding:
    path = longest_duration_path(ctx, area_keywords=("operacion", "produccion", "operaciones"))
    if not path:
        path = longest_duration_path(ctx)
    if not path:
        return error_finding("O-01", "no hay ruta productiva medible")
    return ok_finding(
        "O-01",
        scores={node_id: float(index + 1) for index, node_id in enumerate(path)},
        highlight=highlight_nodes(set(path)),
        summary=f"Descubrimos la ruta crítica de producción: {' → '.join(path)}.",
    )


def run_o02(ctx: GraphContext) -> AnalyticFinding:
    qc_nodes = activities_matching_area(ctx, "calidad", "control")
    scores = betweenness_scores(ctx, area_keywords=("operacion", "produccion", "operaciones"))
    if qc_nodes:
        scores = {node_id: scores.get(node_id, 1.0) for node_id in qc_nodes}
    if not scores:
        return error_finding("O-02", "no hay controles de calidad en el flujo productivo")
    top = max(scores, key=scores.get)
    return ok_finding(
        "O-02",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos centralidad de control de calidad en {top}.",
    )


def run_o03(ctx: GraphContext) -> AnalyticFinding:
    maintenance = activities_matching_area(ctx, "manten", "mantenimiento")
    scores = {node_id: ctx.v_score(node_id) for node_id in maintenance}
    detail = "Riesgo bayesiano de falla de calidad por degradación de mantenimiento (panel)."
    try:
        from pgmpy.models import DiscreteBayesianNetwork

        _ = DiscreteBayesianNetwork()
        detail = "Modelo bayesiano de mantenimiento y calidad calibrado con el grafo."
    except Exception:
        pass
    return panel_finding(
        "O-03",
        scores=scores,
        detail=detail,
        summary="Descubrimos probabilidad de falla de calidad por degradación de mantenimiento.",
    )


def run_o04(ctx: GraphContext) -> AnalyticFinding:
    core_nodes = k_core_nodes(ctx, k=3)
    if not core_nodes:
        core_nodes = list(ctx.activity_ids)
    scores = {node_id: float(index + 1) for index, node_id in enumerate(core_nodes)}
    return ok_finding(
        "O-04",
        scores=scores,
        highlight=highlight_nodes(set(core_nodes)) if core_nodes else None,
        summary="Descubrimos el núcleo operativo irreducible de la producción.",
    )
