from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import ValueStreamDiscoveryResult, ValueStreamTree
from optimizer.graph_analytics.enhanced_scoring import node_confidence
from optimizer.infrastructure.visualization.colors import relevance_gradient_color


@dataclass(frozen=True)
class FlowMetricFlag:
    metric_id: str
    metric_label: str
    relevance: float


@dataclass(frozen=True)
class FlowNode:
    id: str
    kind: str
    label: str
    cumulative_relevance: float = 0.0
    normalized_relevance: float = 0.0
    color: str = "#888888"
    metrics: tuple[FlowMetricFlag, ...] = ()
    in_degree: int = 0
    out_degree: int = 0
    overlap_count: int = 1
    is_backbone: bool = False
    is_join: bool = False
    is_split: bool = False
    confidence: float = 1.0
    generated: bool = False
    p: float | None = None
    c: float | None = None
    f: float | None = None
    r: float | None = None
    v: float | None = None


@dataclass(frozen=True)
class FlowEdge:
    source: str
    target: str


@dataclass(frozen=True)
class ValueStreamFlowGraph:
    nodes: tuple[FlowNode, ...]
    edges: tuple[FlowEdge, ...]
    selected_delivery_ids: tuple[str, ...]
    overlay_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [
                {
                    "id": node.id,
                    "kind": node.kind,
                    "label": node.label,
                    "cumulative_relevance": node.cumulative_relevance,
                    "normalized_relevance": node.normalized_relevance,
                    "color": node.color,
                    "metrics": [
                        {
                            "metric_id": metric.metric_id,
                            "metric_label": metric.metric_label,
                            "relevance": metric.relevance,
                        }
                        for metric in node.metrics
                    ],
                    "in_degree": node.in_degree,
                    "out_degree": node.out_degree,
                    "overlap_count": node.overlap_count,
                    "is_backbone": node.is_backbone,
                    "is_join": node.is_join,
                    "is_split": node.is_split,
                    "confidence": node.confidence,
                    "generated": node.generated,
                    "p": node.p,
                    "c": node.c,
                    "f": node.f,
                    "r": node.r,
                    "v": node.v,
                }
                for node in self.nodes
            ],
            "edges": [
                {"source": edge.source, "target": edge.target}
                for edge in self.edges
            ],
            "selected_delivery_ids": list(self.selected_delivery_ids),
            "overlay_mode": self.overlay_mode,
        }


def _node_kind(context: GraphContext, node_id: str, delivery_ids: frozenset[str]) -> str:
    if node_id in delivery_ids:
        return "delivery_event"
    if node_id in context.activity_ids:
        return "activity"
    if node_id in context.demand_event_ids:
        return "demand_event"
    props = context.node_properties(node_id)
    if props.get("event_type") == "value_realization":
        return "delivery_event"
    return "anchor_event"


def _node_label(
    node_id: str,
    kind: str,
    *,
    event_label_by_id: dict[str, str],
    activity_label_by_id: dict[str, str],
    context: GraphContext,
) -> str:
    if kind == "activity":
        label = activity_label_by_id.get(node_id)
        if label:
            return label
        props = context.node_properties(node_id)
        name = str(props.get("label") or "")
        if name and name != node_id:
            return f"{node_id} — {name}"
        return node_id
    label = event_label_by_id.get(node_id)
    if label:
        return label
    props = context.node_properties(node_id)
    return str(props.get("label") or node_id)


def _activity_metrics(
    context: GraphContext,
    activity_id: str,
    metric_label_by_id: dict[str, str],
) -> tuple[FlowMetricFlag, ...]:
    flags: list[FlowMetricFlag] = []
    for metric_id in sorted(context.metric_ids):
        relevance = context.relevance(activity_id, metric_id)
        if relevance <= 0:
            continue
        flags.append(
            FlowMetricFlag(
                metric_id=metric_id,
                metric_label=metric_label_by_id.get(metric_id, metric_id),
                relevance=relevance,
            )
        )
    return tuple(flags)


def _trees_for_delivery_ids(
    discovery: ValueStreamDiscoveryResult,
    delivery_event_ids: frozenset[str],
) -> tuple[ValueStreamTree, ...]:
    return tuple(
        tree
        for tree in discovery.trees
        if tree.delivery_event_id in delivery_event_ids
    )


def build_value_stream_flow_graph(
    context: GraphContext,
    discovery: ValueStreamDiscoveryResult,
    delivery_event_ids: frozenset[str],
    *,
    event_label_by_id: dict[str, str],
    activity_label_by_id: dict[str, str],
    metric_label_by_id: dict[str, str],
) -> ValueStreamFlowGraph | None:
    """Build a layered flow payload for one or more selected value stream trees."""
    if not delivery_event_ids:
        return None

    trees = _trees_for_delivery_ids(discovery, delivery_event_ids)
    if not trees:
        return None

    overlay_mode = len(trees) > 1
    node_ids: set[str] = set()
    edge_pairs: set[tuple[str, str]] = set()
    score_by_node: dict[str, float] = {}

    for tree in trees:
        node_ids.update(tree.node_ids)
        for source_id, target_id, _rel in tree.edge_keys:
            edge_pairs.add((source_id, target_id))
        for node_id, score in tree.node_scores.items():
            score_by_node[node_id] = max(score_by_node.get(node_id, 0.0), score)

    in_degree: dict[str, int] = {node_id: 0 for node_id in node_ids}
    out_degree: dict[str, int] = {node_id: 0 for node_id in node_ids}
    for source_id, target_id in edge_pairs:
        if source_id in in_degree and target_id in in_degree:
            out_degree[source_id] += 1
            in_degree[target_id] += 1

    activity_scores = [
        score_by_node[node_id]
        for node_id in node_ids
        if node_id in context.activity_ids
    ]
    max_activity_score = max(activity_scores) if activity_scores else 1.0
    max_activity_score = max_activity_score or 1.0

    overlap_by_node: dict[str, int] = {}
    for node_id in node_ids:
        if overlay_mode:
            overlap_by_node[node_id] = sum(
                1 for tree in trees if node_id in tree.node_ids
            )
        else:
            overlap_by_node[node_id] = discovery.node_overlap.get(node_id, 1)

    eval_by_id = {row.activity_id: row for row in context.value_input.activities}

    flow_nodes: list[FlowNode] = []
    for node_id in sorted(node_ids):
        kind = _node_kind(context, node_id, delivery_event_ids)
        cumulative = score_by_node.get(node_id, 0.0) if kind == "activity" else 0.0
        normalized = (
            cumulative / max_activity_score if kind == "activity" else 0.0
        )
        overlap_count = overlap_by_node.get(node_id, 1)
        node_props = context.node_properties(node_id)
        row = eval_by_id.get(node_id) if kind == "activity" else None
        flow_nodes.append(
            FlowNode(
                id=node_id,
                kind=kind,
                label=_node_label(
                    node_id,
                    kind,
                    event_label_by_id=event_label_by_id,
                    activity_label_by_id=activity_label_by_id,
                    context=context,
                ),
                cumulative_relevance=cumulative,
                normalized_relevance=normalized,
                color=(
                    relevance_gradient_color(normalized)
                    if kind == "activity"
                    else ""
                ),
                metrics=(
                    _activity_metrics(context, node_id, metric_label_by_id)
                    if kind == "activity"
                    else ()
                ),
                in_degree=in_degree.get(node_id, 0),
                out_degree=out_degree.get(node_id, 0),
                overlap_count=overlap_count,
                is_backbone=overlap_count >= 2,
                is_join=in_degree.get(node_id, 0) > 1,
                is_split=out_degree.get(node_id, 0) > 1,
                confidence=node_confidence(node_props),
                generated=bool(node_props.get("generated")),
                p=None if row is None else row.p,
                c=None if row is None else row.c,
                f=None if row is None else row.f,
                r=None if row is None else row.r,
                v=None if row is None else row.v,
            )
        )

    flow_edges = tuple(
        FlowEdge(source=source_id, target=target_id)
        for source_id, target_id in sorted(edge_pairs)
    )

    return ValueStreamFlowGraph(
        nodes=tuple(flow_nodes),
        edges=flow_edges,
        selected_delivery_ids=tuple(sorted(delivery_event_ids)),
        overlay_mode=overlay_mode,
    )
