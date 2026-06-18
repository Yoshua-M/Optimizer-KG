from __future__ import annotations

import itertools
from collections import defaultdict

import networkx as nx

from optimizer.graph_analytics.catalog.definitions import get_analytic_definition
from optimizer.graph_analytics.catalog.messages import get_executive_messages
from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import (
    AnalyticFinding,
    AnalyticStatus,
    HighlightPayload,
)
from optimizer.graph_analytics.validation import analytic_error_message

_PATH_CUTOFF = 15


def ok_finding(
    analytic_id: str,
    *,
    scores: dict[str, float] | None = None,
    highlight: HighlightPayload | None = None,
    detail: str = "",
    summary: str | None = None,
) -> AnalyticFinding:
    definition = get_analytic_definition(analytic_id)
    messages = get_executive_messages(analytic_id)
    return AnalyticFinding(
        analytic_id=analytic_id,
        title=definition.title,
        summary=summary or messages.discovery_text,
        detail=detail or messages.rationale_text,
        status=AnalyticStatus.OK,
        scores=dict(scores or {}),
        highlight=highlight,
        error_message=None,
    )


def error_finding(analytic_id: str, detail: str) -> AnalyticFinding:
    definition = get_analytic_definition(analytic_id)
    messages = get_executive_messages(analytic_id)
    return AnalyticFinding(
        analytic_id=analytic_id,
        title=definition.title,
        summary=messages.discovery_text,
        detail=messages.rationale_text,
        status=AnalyticStatus.ERROR,
        scores={},
        highlight=None,
        error_message=analytic_error_message(detail),
    )


def panel_finding(
    analytic_id: str,
    *,
    scores: dict[str, float] | None = None,
    detail: str = "",
    summary: str | None = None,
) -> AnalyticFinding:
    return ok_finding(
        analytic_id,
        scores=scores,
        highlight=None,
        detail=detail,
        summary=summary,
    )


def highlight_nodes(node_ids: set[str] | frozenset[str]) -> HighlightPayload:
    return HighlightPayload(node_ids=frozenset(node_ids))


def activity_area(ctx: GraphContext, activity_id: str) -> str:
    return str(ctx.node_properties(activity_id).get("area") or "").lower()


def activities_matching_area(ctx: GraphContext, *keywords: str) -> list[str]:
    matches: list[str] = []
    for activity_id in ctx.activity_ids:
        area = activity_area(ctx, activity_id)
        if any(keyword.lower() in area for keyword in keywords):
            matches.append(activity_id)
    return matches


def nodes_of_type(ctx: GraphContext, node_type: str) -> list[str]:
    document = ctx.documents[0]
    return [node.id for node in document.nodes if node.type == node_type]


def activity_path_sets(ctx: GraphContext) -> list[set[str]]:
    paths: list[set[str]] = []
    flow = ctx.flow_graph
    for demand_id in ctx.demand_event_ids:
        for value_id in ctx.value_realization_event_ids:
            if not nx.has_path(flow, demand_id, value_id):
                continue
            for raw_path in nx.all_simple_paths(
                flow,
                demand_id,
                value_id,
                cutoff=_PATH_CUTOFF,
            ):
                activity_path = {node_id for node_id in raw_path if node_id in ctx.activity_ids}
                if activity_path:
                    paths.append(activity_path)
    return paths


def dominator_activities(ctx: GraphContext) -> set[str]:
    path_sets = activity_path_sets(ctx)
    if not path_sets:
        return set()
    dominators = set.intersection(*path_sets)
    return dominators


def paths_through_activity(ctx: GraphContext, activity_id: str) -> int:
    count = 0
    flow = ctx.flow_graph
    for demand_id in ctx.demand_event_ids:
        for value_id in ctx.value_realization_event_ids:
            if not nx.has_path(flow, demand_id, value_id):
                continue
            for raw_path in nx.all_simple_paths(
                flow,
                demand_id,
                value_id,
                cutoff=_PATH_CUTOFF,
            ):
                if activity_id in raw_path:
                    count += 1
    return count


def fragility_score(ctx: GraphContext, activity_id: str) -> float:
    total_paths = len(activity_path_sets(ctx))
    if total_paths == 0:
        return 0.0
    through = paths_through_activity(ctx, activity_id)
    return through / total_paths


def activity_subgraph(ctx: GraphContext, *, area_keywords: tuple[str, ...] = ()) -> nx.DiGraph:
    nodes = list(ctx.activity_ids)
    if area_keywords:
        nodes = [
            activity_id
            for activity_id in nodes
            if any(kw in activity_area(ctx, activity_id) for kw in area_keywords)
        ]
    return ctx.flow_graph.subgraph(nodes).copy()


def _ensure_edge_duration(graph: nx.DiGraph) -> None:
    for source, target in graph.edges:
        graph[source][target].setdefault("duracion", 1.0)


def longest_duration_path(
    ctx: GraphContext,
    *,
    area_keywords: tuple[str, ...] = (),
) -> tuple[str, ...]:
    graph = activity_subgraph(ctx, area_keywords=area_keywords)
    if graph.number_of_nodes() == 0:
        return ()
    _ensure_edge_duration(graph)
    if nx.is_directed_acyclic_graph(graph):
        path = nx.dag_longest_path(graph, weight="duracion")
        return tuple(node_id for node_id in path if node_id in ctx.activity_ids)

    best: tuple[str, ...] = ()
    best_weight = -1.0
    for source in graph.nodes:
        for target in graph.nodes:
            if source == target:
                continue
            try:
                for raw_path in nx.all_simple_paths(graph, source, target, cutoff=_PATH_CUTOFF):
                    weight = 0.0
                    for left, right in zip(raw_path, raw_path[1:]):
                        weight += float(graph[left][right].get("duracion", 1.0))
                    activity_path = tuple(n for n in raw_path if n in ctx.activity_ids)
                    if weight > best_weight and activity_path:
                        best_weight = weight
                        best = activity_path
            except nx.NetworkXNoPath:
                continue
    return best


def betweenness_scores(ctx: GraphContext, *, area_keywords: tuple[str, ...] = ()) -> dict[str, float]:
    graph = activity_subgraph(ctx, area_keywords=area_keywords).to_undirected()
    if graph.number_of_nodes() == 0:
        return {}
    scores = nx.betweenness_centrality(graph)
    return {node_id: float(score) for node_id, score in scores.items()}


def articulation_points(ctx: GraphContext, *, area_keywords: tuple[str, ...] = ()) -> list[str]:
    graph = activity_subgraph(ctx, area_keywords=area_keywords).to_undirected()
    if graph.number_of_nodes() == 0:
        return []
    return list(nx.articulation_points(graph))


def k_core_nodes(ctx: GraphContext, k: int = 3) -> list[str]:
    graph = activity_subgraph(ctx).to_undirected()
    if graph.number_of_nodes() == 0:
        return []
    try:
        core = nx.k_core(graph, k=k)
    except nx.NetworkXError:
        return []
    return list(core.nodes)


def related_node_ids(ctx: GraphContext, node_type: str, rel_type: str) -> dict[str, list[str]]:
    """Map activity id → related node ids via outgoing rel_type edges."""
    mapping: dict[str, list[str]] = defaultdict(list)
    document = ctx.documents[0]
    rel_upper = rel_type.upper()
    for relationship in document.relationships:
        if relationship.type.upper() != rel_upper:
            continue
        source = relationship.source
        target = relationship.target
        if source.type == "Activity" and target.type == node_type:
            mapping[source.id].append(target.id)
        elif target.type == "Activity" and source.type == node_type:
            mapping[target.id].append(source.id)
    return dict(mapping)


def team_for_activity(ctx: GraphContext, activity_id: str) -> str | None:
    props = ctx.node_properties(activity_id)
    team = props.get("team_id") or props.get("team")
    if team:
        return str(team)
    for team_id in nodes_of_type(ctx, "Team"):
        props = ctx.node_properties(team_id)
        members = props.get("members") or props.get("activity_ids") or ()
        if activity_id in members:
            return team_id
    return None


def max_flow_throughput(ctx: GraphContext) -> float:
    graph = activity_subgraph(ctx)
    if graph.number_of_nodes() < 2:
        return 0.0
    sources = [n for n in graph.nodes if graph.in_degree(n) == 0]
    sinks = [n for n in graph.nodes if graph.out_degree(n) == 0]
    if not sources or not sinks:
        return float(graph.number_of_nodes())
    flow_graph = nx.DiGraph()
    for node in graph.nodes:
        flow_graph.add_node(node, capacity=float("inf"))
    for source, target in graph.edges:
        flow_graph.add_edge(source, target, capacity=1.0)
    total = 0.0
    for source in sources:
        for sink in sinks:
            try:
                flow_value, _ = nx.maximum_flow(flow_graph, source, sink)
                total = max(total, flow_value)
            except nx.NetworkXError:
                continue
    return float(total)


def journey_step_ids(ctx: GraphContext) -> list[str]:
    return nodes_of_type(ctx, "CustomerJourneyStep")


def activities_touching_journey(ctx: GraphContext) -> dict[str, set[str]]:
    document = ctx.documents[0]
    touches: dict[str, set[str]] = defaultdict(set)
    for relationship in document.relationships:
        if relationship.type.upper() != "TOUCHES":
            continue
        if relationship.source.type == "Activity":
            touches[relationship.source.id].add(relationship.target.id)
    return dict(touches)


def kam_relevance_scores(ctx: GraphContext) -> dict[str, float]:
    scores: dict[str, float] = {}
    for activity_id in activities_matching_area(ctx, "kam", "comercial", "ventas"):
        for metric_id in ctx.metric_ids:
            relevance = ctx.relevance(activity_id, metric_id)
            if relevance > 0:
                scores[activity_id] = max(scores.get(activity_id, 0.0), relevance)
    if scores:
        return scores
    for activity_id in ctx.activity_ids:
        total = sum(ctx.relevance(activity_id, metric_id) for metric_id in ctx.metric_ids)
        if total > 0:
            scores[activity_id] = total
    return scores


def shapley_approx(values: dict[str, float]) -> dict[str, float]:
    keys = list(values)
    if not keys:
        return {}
    n = len(keys)
    if n > 6:
        return {key: values[key] / max(sum(values.values()), 1.0) for key in keys}
    totals = {key: 0.0 for key in keys}
    for size in range(1, n + 1):
        for subset in itertools.combinations(keys, size):
            subset_value = sum(values[k] for k in subset)
            for key in subset:
                totals[key] += subset_value / len(subset)
    return {key: totals[key] / (2 ** (n - 1)) for key in keys}
