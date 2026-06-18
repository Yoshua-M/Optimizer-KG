from __future__ import annotations

import networkx as nx

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    activities_matching_area,
    dominator_activities,
    error_finding,
    fragility_score,
    highlight_nodes,
    ok_finding,
)


def run_g01(ctx: GraphContext) -> AnalyticFinding:
    dominators = dominator_activities(ctx)
    gov_dominators = dominators or set(activities_matching_area(ctx, "gobernanza"))
    if not gov_dominators:
        return error_finding("G-01", "no hay rutas entre eventos de demanda y entrega de valor")
    names = ", ".join(sorted(gov_dominators))
    return ok_finding(
        "G-01",
        scores={activity_id: 1.0 for activity_id in gov_dominators},
        highlight=highlight_nodes(gov_dominators),
        summary=f"Descubrimos actividades de gobernanza dominantes: {names}.",
    )


def run_g02(ctx: GraphContext) -> AnalyticFinding:
    candidates = activities_matching_area(ctx, "gobernanza") or list(ctx.activity_ids)
    scores = {activity_id: fragility_score(ctx, activity_id) for activity_id in candidates}
    scores = {k: v for k, v in scores.items() if v > 0}
    if not scores:
        return error_finding("G-02", "no se encontraron controles de gobernanza en rutas de valor")
    top = max(scores, key=scores.get)
    return ok_finding(
        "G-02",
        scores=scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos fragilidad estructural en controles de gobernanza (máximo: {top}).",
    )


def run_g03(ctx: GraphContext) -> AnalyticFinding:
    gov_nodes = activities_matching_area(ctx, "gobernanza")
    if not gov_nodes:
        return error_finding("G-03", "no hay actividades de gobernanza para simular falla")
    target = gov_nodes[0]
    flow = ctx.flow_graph
    affected: set[str] = set()
    for metric_id in ctx.metric_ids:
        for activity in ctx.value_input.activities:
            if ctx.relevance(activity.activity_id, metric_id) <= 0:
                continue
            try:
                if nx.has_path(flow, target, activity.activity_id):
                    affected.add(activity.activity_id)
            except nx.NetworkXError:
                continue
    if not affected:
        affected = set(nx.descendants(flow, target)) & set(ctx.activity_ids)
    return ok_finding(
        "G-03",
        scores={node_id: 1.0 for node_id in affected},
        highlight=highlight_nodes({target} | affected),
        summary=f"Descubrimos impacto en cascada si falla el control {target}.",
    )


def run_g04(ctx: GraphContext) -> AnalyticFinding:
    flow = ctx.flow_graph
    sources = list(ctx.demand_event_ids)
    sinks = list(ctx.value_realization_event_ids)
    if not sources or not sinks:
        return error_finding("G-04", "faltan eventos de demanda o entrega de valor")
    try:
        cut_value, partition = nx.minimum_cut(flow, sources[0], sinks[0])
    except nx.NetworkXError:
        return error_finding("G-04", "no se pudo calcular el corte mínimo de continuidad")
    reachable, _ = partition
    cut_nodes = {
        node_id
        for node_id in reachable
        if node_id in ctx.activity_ids and "gobernanza" in str(ctx.node_properties(node_id).get("area", "")).lower()
    }
    if not cut_nodes:
        cut_nodes = {node_id for node_id in reachable if node_id in ctx.activity_ids}
    return ok_finding(
        "G-04",
        scores={node_id: float(cut_value) for node_id in cut_nodes},
        highlight=highlight_nodes(cut_nodes),
        summary="Descubrimos el conjunto mínimo de controles para continuidad operativa.",
    )

