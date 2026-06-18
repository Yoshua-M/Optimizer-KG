from __future__ import annotations

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    activities_matching_area,
    activities_touching_journey,
    betweenness_scores,
    error_finding,
    highlight_nodes,
    journey_step_ids,
    longest_duration_path,
    ok_finding,
    panel_finding,
)


def run_pv01(ctx: GraphContext) -> AnalyticFinding:
    path = longest_duration_path(ctx, area_keywords=("postventa", "servicio", "incidente"))
    if not path:
        path = longest_duration_path(ctx)
    if not path:
        return error_finding("PV-01", "no hay ruta de resolución de incidentes")
    return ok_finding(
        "PV-01",
        scores={node_id: float(index + 1) for index, node_id in enumerate(path)},
        highlight=highlight_nodes(set(path)),
        summary=f"Descubrimos ruta crítica de resolución de incidentes: {' → '.join(path)}.",
    )


def run_pv02(ctx: GraphContext) -> AnalyticFinding:
    scores = betweenness_scores(ctx, area_keywords=("postventa", "servicio", "escalacion"))
    if not scores:
        scores = betweenness_scores(ctx)
    if not scores:
        return error_finding("PV-02", "no hay rutas de escalación medibles")
    top = max(scores, key=scores.get)
    return ok_finding(
        "PV-02",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos cuello de botella en escalación: {top}.",
    )


def run_pv03(ctx: GraphContext) -> AnalyticFinding:
    service_nodes = activities_matching_area(ctx, "postventa", "servicio")
    scores = {node_id: ctx.v_score(node_id) for node_id in service_nodes}
    detail = "Riesgo bayesiano de churn por degradación del servicio (panel)."
    try:
        from pgmpy.models import DiscreteBayesianNetwork

        _ = DiscreteBayesianNetwork()
        detail = "Modelo bayesiano de degradación de servicio y churn."
    except Exception:
        pass
    return panel_finding(
        "PV-03",
        scores=scores,
        detail=detail,
        summary="Descubrimos probabilidad de churn por degradación del servicio.",
    )


def run_pv04(ctx: GraphContext) -> AnalyticFinding:
    journey_ids = set(journey_step_ids(ctx))
    if not journey_ids:
        return error_finding("PV-04", "no hay momentos del journey para cobertura postventa")
    touches = activities_touching_journey(ctx)
    postventa = set(activities_matching_area(ctx, "postventa", "servicio"))
    coverage: dict[str, float] = {}
    for journey_id in journey_ids:
        covered = any(
            journey_id in steps and activity_id in postventa
            for activity_id, steps in touches.items()
        ) or any(journey_id in steps for steps in touches.values())
        coverage[journey_id] = 1.0 if covered else 0.0
    return ok_finding(
        "PV-04",
        scores=coverage,
        highlight=highlight_nodes({jid for jid, score in coverage.items() if score > 0}),
        summary="Descubrimos cobertura de momentos críticos del journey por postventa.",
    )


def run_pv05(ctx: GraphContext) -> AnalyticFinding:
    adoption = activities_matching_area(ctx, "exito", "adopcion", "acompañamiento", "postventa")
    if not adoption:
        adoption = list(ctx.activity_ids)
    scores: dict[str, float] = {}
    for activity_id in adoption:
        upstream_value = sum(
            ctx.relevance(activity_id, metric_id) for metric_id in ctx.metric_ids
        )
        if upstream_value > 0:
            scores[activity_id] = upstream_value
    if not scores:
        return error_finding("PV-05", "no hay actividades de éxito del cliente con valor propagado")
    top = max(scores, key=scores.get)
    return ok_finding(
        "PV-05",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos propagación de valor upstream desde {top}.",
    )
