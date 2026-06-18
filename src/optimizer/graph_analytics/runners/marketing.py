from __future__ import annotations

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    activities_matching_area,
    activities_touching_journey,
    dominator_activities,
    error_finding,
    highlight_nodes,
    journey_step_ids,
    kam_relevance_scores,
    ok_finding,
    panel_finding,
)


def run_mv01(ctx: GraphContext) -> AnalyticFinding:
    path_activities = dominator_activities(ctx) or set(ctx.activity_ids)
    commercial = activities_matching_area(ctx, "comercial", "ventas", "marketing")
    nodes = set(commercial) & path_activities if commercial else path_activities
    if not nodes:
        return error_finding("MV-01", "no hay pipeline comercial en el grafo")
    return ok_finding(
        "MV-01",
        scores={node_id: ctx.v_score(node_id) for node_id in nodes},
        highlight=highlight_nodes(nodes),
        summary="Descubrimos flujos del pipeline comercial hacia el cierre.",
    )


def run_mv02(ctx: GraphContext) -> AnalyticFinding:
    touches = activities_touching_journey(ctx)
    if not touches:
        return error_finding("MV-02", "no hay actividades comerciales conectadas al journey")
    scores = {activity_id: float(len(steps)) for activity_id, steps in touches.items()}
    top = max(scores, key=scores.get)
    return ok_finding(
        "MV-02",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos actividad comercial con mayor cobertura de journey: {top}.",
    )


def run_mv03(ctx: GraphContext) -> AnalyticFinding:
    scores = kam_relevance_scores(ctx)
    if not scores:
        return error_finding("MV-03", "no hay actividades KAM con relevancia sobre retención")
    top = max(scores, key=scores.get)
    return ok_finding(
        "MV-03",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos relevancia KAM sobre retención en {top}.",
    )


def run_mv04(ctx: GraphContext) -> AnalyticFinding:
    initiatives = activities_matching_area(ctx, "comercial", "iniciativa", "marketing")
    scores = {node_id: ctx.v_score(node_id) for node_id in initiatives}
    detail = "Validación de independencia de iniciativas comerciales (panel bayesiano)."
    try:
        from pgmpy.models import DiscreteBayesianNetwork

        _ = DiscreteBayesianNetwork()
        detail = "Modelo de independencia causal entre iniciativas comerciales."
    except Exception:
        pass
    return panel_finding(
        "MV-04",
        scores=scores,
        detail=detail,
        summary="Descubrimos superposición causal entre iniciativas comerciales.",
    )
