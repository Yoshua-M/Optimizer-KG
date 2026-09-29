from __future__ import annotations

from itertools import combinations

import networkx as nx
from networkx.algorithms.approximation import steiner_tree

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.relevance import build_cumulative_relevance_scores
from optimizer.graph_analytics.models import (
    ActivityCategory,
    ValueStreamDiscoveryResult,
    ValueStreamFocus,
    ValueStreamTree,
)

_SEMANTIC_V_THRESHOLD = 0.5
_DEFAULT_OVERLAP_THRESHOLD = 0.30
_DEFAULT_BACKBONE_MIN_OVERLAP = 2


def _event_type(flow: nx.DiGraph, node_id: str) -> str | None:
    return flow.nodes[node_id].get("event_type")


def _is_event(flow: nx.DiGraph, node_id: str) -> bool:
    return flow.nodes[node_id].get("node_type") == "Event"


def _group_by_delivery_anchor(context: GraphContext) -> list[frozenset[str]]:
    flow = context.flow_graph
    groups: list[frozenset[str]] = []

    for delivery_id in sorted(context.value_realization_event_ids):
        if delivery_id not in flow:
            continue
        ancestors = nx.ancestors(flow, delivery_id)
        anchor_events = {
            node_id
            for node_id in ancestors
            if _is_event(flow, node_id)
            and _event_type(flow, node_id) != "value_realization"
        }
        groups.append(frozenset(anchor_events | {delivery_id}))

    return groups


def _ancestor_activities(flow: nx.DiGraph, event_id: str, activity_ids: frozenset[str]) -> set[str]:
    if event_id not in flow:
        return set()
    return {
        node_id
        for node_id in nx.ancestors(flow, event_id)
        if node_id in activity_ids
    }


def _merge_crossing_groups(
    groups: list[frozenset[str]],
    context: GraphContext,
    overlap_threshold: float,
) -> list[frozenset[str]]:
    if len(groups) < 2:
        return groups

    flow = context.flow_graph
    activity_ids = context.activity_ids
    group_acts: list[set[str]] = []
    for group in groups:
        acts: set[str] = set()
        for event_id in group:
            if _event_type(flow, event_id) == "value_realization":
                acts |= _ancestor_activities(flow, event_id, activity_ids)
        group_acts.append(acts)

    meta = nx.Graph()
    meta.add_nodes_from(range(len(groups)))
    for i, j in combinations(range(len(groups)), 2):
        inter = group_acts[i] & group_acts[j]
        smaller = min(len(group_acts[i]), len(group_acts[j])) or 1
        if len(inter) / smaller >= overlap_threshold:
            meta.add_edge(i, j)

    merged: list[frozenset[str]] = []
    for component in nx.connected_components(meta):
        union_group: set[str] = set()
        for idx in component:
            union_group |= groups[idx]
        merged.append(frozenset(union_group))
    return merged


def _set_edge_costs(flow: nx.DiGraph, cum_relevance: dict[str, float]) -> None:
    max_cum = max(cum_relevance.values()) if cum_relevance else 0.0
    max_cum = max_cum or 1.0
    for source_id, target_id in flow.edges:
        norm = cum_relevance.get(target_id, 0.0) / max_cum
        flow[source_id][target_id]["vs_cost"] = 1.0 - norm


def _delivery_in_group(group: frozenset[str], context: GraphContext) -> str | None:
    for event_id in group:
        if event_id in context.value_realization_event_ids:
            return event_id
    return None


def _connected_terminals(
    flow: nx.DiGraph,
    group: frozenset[str],
    delivery_id: str,
) -> list[str] | None:
    terminals = [node_id for node_id in group if node_id in flow]
    if len(terminals) < 2:
        return None

    undirected = flow.to_undirected()
    if delivery_id not in undirected:
        return None
    component = nx.node_connected_component(undirected, delivery_id)
    connected = [node_id for node_id in terminals if node_id in component]
    if len(connected) < 2:
        return None
    return connected


def _tree_to_directed(
    tree_undirected: nx.Graph,
    flow: nx.DiGraph,
) -> nx.DiGraph:
    tree = nx.DiGraph()
    tree.add_nodes_from(tree_undirected.nodes(data=True))
    for source_id, target_id in tree_undirected.edges:
        if flow.has_edge(source_id, target_id):
            tree.add_edge(source_id, target_id)
        elif flow.has_edge(target_id, source_id):
            tree.add_edge(target_id, source_id)
    return tree


def _precedes_keys_for_tree(tree: nx.DiGraph) -> frozenset[tuple[str, str, str]]:
    return frozenset(
        (source_id, target_id, "PRECEDES")
        for source_id, target_id in tree.edges
    )


def _build_vs_tree(
    group: frozenset[str],
    flow_with_costs: nx.DiGraph,
    context: GraphContext,
) -> nx.DiGraph | None:
    delivery_id = _delivery_in_group(group, context)
    if delivery_id is None:
        return None

    terminals = _connected_terminals(flow_with_costs, group, delivery_id)
    if terminals is None:
        return None

    undirected = flow_with_costs.to_undirected()
    component = nx.node_connected_component(undirected, delivery_id)
    subgraph = undirected.subgraph(component)
    tree_undirected = steiner_tree(subgraph, terminals, weight="vs_cost")
    return _tree_to_directed(tree_undirected, flow_with_costs)


def _tree_to_result(
    tree: nx.DiGraph,
    group: frozenset[str],
    context: GraphContext,
    cum_relevance: dict[str, float],
) -> ValueStreamTree:
    delivery_id = _delivery_in_group(group, context)
    if delivery_id is None:
        raise ValueError("group has no delivery event")

    activity_ids = frozenset(
        node_id for node_id in tree.nodes if node_id in context.activity_ids
    )
    anchor_event_ids = frozenset(
        node_id for node_id in group if node_id != delivery_id
    )
    node_scores = {
        activity_id: cum_relevance.get(activity_id, 0.0)
        for activity_id in activity_ids
    }
    total_relevance = sum(node_scores.values())
    return ValueStreamTree(
        delivery_event_id=delivery_id,
        anchor_event_ids=anchor_event_ids,
        activity_ids=activity_ids,
        node_ids=frozenset(tree.nodes),
        edge_keys=_precedes_keys_for_tree(tree),
        node_scores=node_scores,
        total_relevance=total_relevance,
    )


def _union_and_overlap(
    trees: list[nx.DiGraph],
) -> tuple[nx.DiGraph, dict[str, int], dict[tuple[str, str], int]]:
    node_overlap: dict[str, int] = {}
    edge_overlap: dict[tuple[str, str], int] = {}
    union = nx.DiGraph()

    for tree in trees:
        for node_id in tree.nodes:
            node_overlap[node_id] = node_overlap.get(node_id, 0) + 1
        for source_id, target_id in tree.edges:
            edge_overlap[(source_id, target_id)] = (
                edge_overlap.get((source_id, target_id), 0) + 1
            )
        union = nx.compose(union, tree)

    return union, node_overlap, edge_overlap


def _identify_backbone(node_overlap: dict[str, int], min_overlap: int) -> frozenset[str]:
    return frozenset(
        node_id
        for node_id, count in node_overlap.items()
        if count >= min_overlap
    )


def _classify_activities(
    context: GraphContext,
    vs_union: frozenset[str],
) -> dict[str, ActivityCategory]:
    vs_nodes = set(vs_union)
    flow = context.flow_graph

    structural_support: set[str] = set()
    for vs_node in vs_nodes:
        ancestors = nx.ancestors(flow, vs_node)
        structural_support.update(
            (ancestors - vs_nodes) & set(context.activity_ids),
        )

    semantic_support: set[str] = set()
    remaining = set(context.activity_ids) - vs_nodes - structural_support
    for activity_id in remaining:
        if context.v_score(activity_id) <= _SEMANTIC_V_THRESHOLD:
            continue
        if all(context.b_score(activity_id, metric_id) == 0.0 for metric_id in context.metric_ids):
            semantic_support.add(activity_id)

    waste = set(context.activity_ids) - vs_nodes - structural_support - semantic_support

    classifications: dict[str, ActivityCategory] = {}
    for activity_id in vs_nodes:
        classifications[activity_id] = ActivityCategory.VALUE_STREAM
    for activity_id in structural_support:
        classifications[activity_id] = ActivityCategory.STRUCTURAL_SUPPORT
    for activity_id in semantic_support:
        classifications[activity_id] = ActivityCategory.SEMANTIC_SUPPORT
    for activity_id in waste:
        classifications[activity_id] = ActivityCategory.WASTE
    return classifications


def _metric_affectation_keys(
    context: GraphContext,
    visible_activity_ids: frozenset[str],
) -> tuple[frozenset[tuple[str, str, str]], frozenset[str], frozenset[str]]:
    """Metric links from visible VS activities: direct AFFECTS and driver-mediated DRIVES."""
    edge_keys: set[tuple[str, str, str]] = set()
    driver_ids: set[str] = set()
    metric_ids: set[str] = set()
    document = context.documents[0]
    node_types = {node.id: node.type for node in document.nodes}
    rels = document.relationships

    for relationship in rels:
        if relationship.type.upper() != "AFFECTS":
            continue
        source_id = relationship.source.id
        if source_id not in visible_activity_ids:
            continue
        target_id = relationship.target.id
        target_type = node_types.get(target_id)
        if target_type == "Metric":
            edge_keys.add((source_id, target_id, "AFFECTS"))
            metric_ids.add(target_id)
        elif target_type == "MetricDriver":
            edge_keys.add((source_id, target_id, "AFFECTS"))
            driver_ids.add(target_id)

    changed = True
    while changed:
        changed = False
        for relationship in rels:
            rel_type = relationship.type.upper()
            source_id = relationship.source.id
            target_id = relationship.target.id
            key = (source_id, target_id, rel_type)
            if key in edge_keys:
                continue
            if rel_type != "DRIVES":
                continue
            if source_id in driver_ids and node_types.get(target_id) == "Metric":
                edge_keys.add(key)
                metric_ids.add(target_id)
                changed = True
            elif target_id in metric_ids and node_types.get(source_id) == "MetricDriver":
                edge_keys.add(key)
                driver_ids.add(source_id)
                changed = True

    return frozenset(edge_keys), frozenset(driver_ids), frozenset(metric_ids)


def _support_precedes_keys(
    context: GraphContext,
    visible_activity_ids: frozenset[str],
    support_activity_ids: frozenset[str],
) -> frozenset[tuple[str, str, str]]:
    if not support_activity_ids:
        return frozenset()

    keys: set[tuple[str, str, str]] = set()
    flow = context.flow_graph
    for support_id in support_activity_ids:
        for other_id in visible_activity_ids:
            if support_id == other_id:
                continue
            if flow.has_edge(support_id, other_id):
                keys.add((support_id, other_id, "PRECEDES"))
            if flow.has_edge(other_id, support_id):
                keys.add((other_id, support_id, "PRECEDES"))
    return frozenset(keys)


def build_value_stream_focus(
    context: GraphContext,
    discovery: ValueStreamDiscoveryResult,
    delivery_event_id: str,
    *,
    include_support: bool = False,
    include_waste: bool = False,
) -> ValueStreamFocus | None:
    """Build highlight + classification payload for one group's value stream tree."""
    tree_result = next(
        (item for item in discovery.trees if item.delivery_event_id == delivery_event_id),
        None,
    )
    if tree_result is None or not tree_result.activity_ids:
        return None

    vs_union = frozenset(tree_result.activity_ids)
    classifications = _classify_activities(context, vs_union)

    visible: set[str] = set(tree_result.activity_ids)
    if include_support:
        for activity_id, category in classifications.items():
            if category in (
                ActivityCategory.STRUCTURAL_SUPPORT,
                ActivityCategory.SEMANTIC_SUPPORT,
            ):
                visible.add(activity_id)
    if include_waste:
        for activity_id, category in classifications.items():
            if category == ActivityCategory.WASTE:
                visible.add(activity_id)

    visible_frozen = frozenset(visible)
    boundary_event_ids = frozenset(
        tree_result.anchor_event_ids | {tree_result.delivery_event_id}
    )
    metric_source_ids = set(visible_frozen)
    for activity_id, category in classifications.items():
        if category == ActivityCategory.STRUCTURAL_SUPPORT:
            metric_source_ids.add(activity_id)
    metric_edge_keys, driver_ids, metric_ids = _metric_affectation_keys(
        context,
        frozenset(metric_source_ids),
    )
    linking_activities = {
        source_id
        for source_id, _target_id, rel_type in metric_edge_keys
        if rel_type == "AFFECTS"
    }
    visible.update(linking_activities)
    visible_frozen = frozenset(visible)
    activity_classifications = {
        activity_id: classifications[activity_id]
        for activity_id in visible_frozen
        if activity_id in classifications
    }

    support_ids = frozenset(
        activity_id
        for activity_id in visible_frozen
        if classifications.get(activity_id)
        in (
            ActivityCategory.STRUCTURAL_SUPPORT,
            ActivityCategory.SEMANTIC_SUPPORT,
        )
    )
    support_precedes = _support_precedes_keys(context, visible_frozen, support_ids)
    highlight_edge_keys = tree_result.edge_keys | support_precedes | metric_edge_keys
    highlight_node_ids = (
        visible_frozen
        | metric_ids
        | boundary_event_ids
        | driver_ids
    )

    return ValueStreamFocus(
        delivery_event_id=delivery_event_id,
        visible_activity_ids=visible_frozen,
        highlight_node_ids=highlight_node_ids,
        activity_classifications=activity_classifications,
        metric_ids=metric_ids,
        boundary_event_ids=boundary_event_ids,
        metric_driver_ids=driver_ids,
        highlight_edge_keys=highlight_edge_keys,
        node_scores=dict(tree_result.node_scores),
    )


def discover_value_streams(
    context: GraphContext,
    *,
    merge_crossing: bool = False,
    overlap_threshold: float = _DEFAULT_OVERLAP_THRESHOLD,
    backbone_min_overlap: int = _DEFAULT_BACKBONE_MIN_OVERLAP,
) -> ValueStreamDiscoveryResult:
    """Discover value stream trees per delivery-anchored event group."""
    initial_groups = _group_by_delivery_anchor(context)
    groups = initial_groups
    if merge_crossing:
        groups = _merge_crossing_groups(groups, context, overlap_threshold)

    cum_relevance = build_cumulative_relevance_scores(context)
    flow_with_costs = context.flow_graph.copy()
    _set_edge_costs(flow_with_costs, cum_relevance)

    raw_trees: list[tuple[str, nx.DiGraph, frozenset[str]]] = []
    for group in groups:
        delivery_id = _delivery_in_group(group, context)
        if delivery_id is None:
            continue
        tree = _build_vs_tree(group, flow_with_costs, context)
        if tree is not None:
            raw_trees.append((delivery_id, tree, group))

    union, node_overlap, edge_overlap = _union_and_overlap(
        [tree for _, tree, _ in raw_trees]
    )
    backbone = _identify_backbone(node_overlap, backbone_min_overlap)

    trees: list[ValueStreamTree] = []
    for delivery_id, raw_tree, group in raw_trees:
        trees.append(_tree_to_result(raw_tree, group, context, cum_relevance))

    vs_union = frozenset(
        node_id for node_id in union.nodes if node_id in context.activity_ids
    )
    classifications = _classify_activities(context, vs_union)

    group_count = len(groups)
    avg_group_size = (
        sum(len(group) for group in groups) / group_count if group_count else 0.0
    )

    return ValueStreamDiscoveryResult(
        trees=tuple(trees),
        vs_union=vs_union,
        classifications=classifications,
        node_overlap=node_overlap,
        edge_overlap=edge_overlap,
        backbone=backbone,
        group_count=group_count,
        avg_group_size=avg_group_size,
        initial_group_count=len(initial_groups),
        merge_crossing_applied=merge_crossing,
    )
