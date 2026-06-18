from __future__ import annotations

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    activities_matching_area,
    activities_touching_journey,
    error_finding,
    highlight_nodes,
    journey_step_ids,
    max_flow_throughput,
    nodes_of_type,
    ok_finding,
    related_node_ids,
)


def run_le01(ctx: GraphContext) -> AnalyticFinding:
    throughput = max_flow_throughput(ctx)
    if throughput <= 0:
        return error_finding("LE-01", "no hay red de entrega medible")
    return ok_finding(
        "LE-01",
        scores={"throughput": throughput},
        summary=f"Descubrimos techo de throughput de entrega: {throughput:.2f}.",
    )


def run_le02(ctx: GraphContext) -> AnalyticFinding:
    candidates = activities_matching_area(ctx, "logistica", "entrega", "distribucion")
    if not candidates:
        candidates = list(ctx.activity_ids)
    scores = {
        activity_id: sum(ctx.relevance(activity_id, metric_id) for metric_id in ctx.metric_ids)
        for activity_id in candidates
    }
    scores = {k: v for k, v in scores.items() if v > 0}
    if not scores:
        return error_finding("LE-02", "no hay actividades logísticas con relevancia")
    top = max(scores, key=scores.get)
    return ok_finding(
        "LE-02",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos ruta de mayor valor logístico en {top}.",
    )


def run_le03(ctx: GraphContext) -> AnalyticFinding:
    journey_ids = set(journey_step_ids(ctx))
    if not journey_ids:
        return error_finding("LE-03", "no hay momentos del journey etiquetados")
    touches = activities_touching_journey(ctx)
    coverage: dict[str, float] = {}
    for journey_id in journey_ids:
        covered = any(journey_id in steps for steps in touches.values())
        coverage[journey_id] = 1.0 if covered else 0.0
    gaps = [jid for jid, score in coverage.items() if score == 0.0]
    highlight = highlight_nodes(set(journey_ids) - set(gaps)) if gaps else highlight_nodes(journey_ids)
    return ok_finding(
        "LE-03",
        scores=coverage,
        highlight=highlight,
        summary="Descubrimos cobertura de momentos del cliente por actividades logísticas.",
    )


def run_le04(ctx: GraphContext) -> AnalyticFinding:
    partners = nodes_of_type(ctx, "LogisticsPartner") + nodes_of_type(ctx, "Supplier")
    serves = related_node_ids(ctx, "LogisticsPartner", "SERVES")
    if not partners and not serves:
        return error_finding("LE-04", "no hay socios logísticos etiquetados")
    single_points: dict[str, float] = {}
    for activity_id, partner_ids in serves.items():
        if len(partner_ids) == 1:
            single_points[partner_ids[0]] = max(
                single_points.get(partner_ids[0], 0.0),
                ctx.v_score(activity_id),
            )
    if not single_points:
        single_points = {partner_id: 1.0 for partner_id in partners}
    top = max(single_points, key=single_points.get)
    return ok_finding(
        "LE-04",
        scores=single_points,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos socio logístico crítico sin sustituto: {top}.",
    )
