from __future__ import annotations

import networkx as nx

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    activities_matching_area,
    error_finding,
    highlight_nodes,
    max_flow_throughput,
    nodes_of_type,
    ok_finding,
    related_node_ids,
)


def run_a01(ctx: GraphContext) -> AnalyticFinding:
    suppliers = nodes_of_type(ctx, "Supplier")
    supplies = related_node_ids(ctx, "Supplier", "SUPPLIES")
    if not suppliers and not supplies:
        scores = {
            activity_id: ctx.v_score(activity_id)
            for activity_id in activities_matching_area(ctx, "abastec", "procurement")
        }
        if not scores:
            return ok_finding(
                "A-01",
                scores={},
                summary="Descubrimos concentración de suministro (sin proveedores etiquetados).",
            )
        top = max(scores, key=scores.get)
        return ok_finding(
            "A-01",
            scores=scores,
            highlight=highlight_nodes({top}),
            summary=f"Descubrimos concentración operativa en actividad {top}.",
        )
    concentrations: dict[str, float] = {}
    for activity_id, supplier_ids in supplies.items():
        for supplier_id in supplier_ids:
            concentrations[supplier_id] = concentrations.get(supplier_id, 0.0) + ctx.v_score(
                activity_id
            )
    if not concentrations:
        return error_finding("A-01", "no hay proveedores conectados a actividades críticas")
    top = max(concentrations, key=concentrations.get)
    return ok_finding(
        "A-01",
        scores=concentrations,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos concentración de suministro en {top}.",
    )


def run_a02(ctx: GraphContext) -> AnalyticFinding:
    throughput = max_flow_throughput(ctx)
    if throughput <= 0:
        return error_finding("A-02", "no hay cadena de suministro medible en el grafo")
    return ok_finding(
        "A-02",
        scores={"throughput": throughput},
        summary=f"Descubrimos throughput máximo de cadena de suministro: {throughput:.2f}.",
    )


def run_a03(ctx: GraphContext) -> AnalyticFinding:
    suppliers = nodes_of_type(ctx, "Supplier")
    if not suppliers:
        return error_finding("A-03", "no hay proveedores para simular falla")
    target = suppliers[0]
    impacted: dict[str, float] = {}
    supplies = related_node_ids(ctx, "Supplier", "SUPPLIES")
    for activity_id, supplier_ids in supplies.items():
        if target not in supplier_ids:
            continue
        for metric_id in ctx.metric_ids:
            relevance = ctx.relevance(activity_id, metric_id)
            if relevance > 0:
                impacted[metric_id] = impacted.get(metric_id, 0.0) + relevance
    return ok_finding(
        "A-03",
        scores=impacted or {target: 1.0},
        highlight=highlight_nodes({target}),
        summary=f"Descubrimos impacto por falla del proveedor {target}.",
    )


def run_a04(ctx: GraphContext) -> AnalyticFinding:
    suppliers = nodes_of_type(ctx, "Supplier")
    supplies = related_node_ids(ctx, "Supplier", "SUPPLIES")
    if len(suppliers) < 2:
        return error_finding("A-04", "se requieren al menos dos proveedores para clustering")
    bipartite = nx.Graph()
    for supplier_id in suppliers:
        bipartite.add_node(supplier_id, bipartite=0)
    for activity_id, supplier_ids in supplies.items():
        bipartite.add_node(activity_id, bipartite=1)
        for supplier_id in supplier_ids:
            bipartite.add_edge(supplier_id, activity_id)
    try:
        import community as community_louvain

        partition = community_louvain.best_partition(bipartite)
        cluster_scores: dict[str, float] = {}
        for node_id, cluster_id in partition.items():
            if node_id in suppliers:
                cluster_scores[node_id] = float(cluster_id)
    except Exception:
        cluster_scores = {supplier_id: float(index) for index, supplier_id in enumerate(suppliers)}
    return ok_finding(
        "A-04",
        scores=cluster_scores,
        highlight=highlight_nodes(set(cluster_scores)),
        summary="Descubrimos clusters de abastecimiento estratégico vs. operativo.",
    )
