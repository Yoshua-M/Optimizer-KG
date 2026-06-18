from __future__ import annotations

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    articulation_points,
    betweenness_scores,
    error_finding,
    highlight_nodes,
    longest_duration_path,
    ok_finding,
)


def run_li01(ctx: GraphContext) -> AnalyticFinding:
    path = longest_duration_path(ctx, area_keywords=("logistica_interna", "logistica", "interna"))
    if not path:
        path = longest_duration_path(ctx)
    if not path:
        return error_finding("LI-01", "no hay ruta interna medible en el grafo")
    return ok_finding(
        "LI-01",
        scores={node_id: float(index + 1) for index, node_id in enumerate(path)},
        highlight=highlight_nodes(set(path)),
        summary=f"Descubrimos la ruta crítica interna: {' → '.join(path)}.",
    )


def run_li02(ctx: GraphContext) -> AnalyticFinding:
    scores = betweenness_scores(ctx, area_keywords=("logistica_interna", "logistica", "interna"))
    if not scores:
        scores = betweenness_scores(ctx)
    if not scores:
        return error_finding("LI-02", "no hay flujo de materiales medible")
    top = max(scores, key=scores.get)
    return ok_finding(
        "LI-02",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos cuello de botella en flujo de materiales: {top}.",
    )


def run_li03(ctx: GraphContext) -> AnalyticFinding:
    points = articulation_points(ctx, area_keywords=("logistica_interna", "logistica", "interna"))
    if not points:
        points = articulation_points(ctx)
    if not points:
        return error_finding("LI-03", "no hay puntos únicos de falla en recepción")
    return ok_finding(
        "LI-03",
        scores={node_id: 1.0 for node_id in points},
        highlight=highlight_nodes(set(points)),
        summary="Descubrimos puntos únicos de falla en recepción interna.",
    )
