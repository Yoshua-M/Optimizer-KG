from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
from langchain_community.graphs.graph_document import GraphDocument

from optimizer.application.scenario_models import ValueScenarioInput

_FLOW_NODE_TYPES = frozenset({"Activity", "Event"})
_FLOW_EDGE_TYPES = frozenset({"PRECEDES"})


@dataclass
class GraphContext:
    """Normalized graph view for analytics runners."""

    documents: tuple[GraphDocument, ...]
    value_input: ValueScenarioInput
    flow_graph: nx.DiGraph
    activity_ids: frozenset[str]
    demand_event_ids: frozenset[str]
    value_realization_event_ids: frozenset[str]
    metric_ids: frozenset[str]
    _relevance: dict[tuple[str, str], float] = field(repr=False, default_factory=dict)
    _v_scores: dict[str, float] = field(repr=False, default_factory=dict)
    _b_scores: dict[tuple[str, str], float] = field(repr=False, default_factory=dict)
    _node_properties: dict[str, dict] = field(repr=False, default_factory=dict)

    def relevance(self, activity_id: str, metric_id: str) -> float:
        return self._relevance.get((activity_id, metric_id), 0.0)

    def v_score(self, activity_id: str) -> float:
        return self._v_scores.get(activity_id, 0.0)

    def b_score(self, activity_id: str, metric_id: str) -> float:
        return self._b_scores.get((activity_id, metric_id), 0.0)

    def node_properties(self, node_id: str) -> dict:
        return dict(self._node_properties.get(node_id, {}))


def build_graph_context(
    documents: list[GraphDocument],
    value_input: ValueScenarioInput,
) -> GraphContext:
    if not documents:
        raise ValueError("Se requiere al menos un GraphDocument")

    document = documents[0]
    flow_graph = nx.DiGraph()
    activity_ids: set[str] = set()
    demand_event_ids: set[str] = set()
    value_realization_event_ids: set[str] = set()
    node_properties: dict[str, dict] = {}

    for node in document.nodes:
        properties = dict(node.properties or {})
        node_properties[node.id] = properties
        if node.type not in _FLOW_NODE_TYPES:
            continue
        flow_graph.add_node(node.id, node_type=node.type, **properties)
        if node.type == "Activity":
            activity_ids.add(node.id)
        if node.type == "Event":
            event_type = properties.get("event_type")
            if event_type == "demand":
                demand_event_ids.add(node.id)
            elif event_type == "value_realization":
                value_realization_event_ids.add(node.id)

    node_ids = {node.id for node in document.nodes}
    for relationship in document.relationships:
        if relationship.type.upper() not in _FLOW_EDGE_TYPES:
            continue
        source_id = relationship.source.id
        target_id = relationship.target.id
        if source_id not in node_ids or target_id not in node_ids:
            continue
        if source_id not in flow_graph or target_id not in flow_graph:
            continue
        edge_props = dict(getattr(relationship, "properties", None) or {})
        flow_graph.add_edge(source_id, target_id, **edge_props)

    relevance: dict[tuple[str, str], float] = {}
    v_scores: dict[str, float] = {}
    b_scores: dict[tuple[str, str], float] = {}
    for activity in value_input.activities:
        v_scores[activity.activity_id] = float(activity.v)
        for score in activity.scores:
            relevance[(activity.activity_id, score.metric_id)] = float(score.relevance)
            b_scores[(activity.activity_id, score.metric_id)] = float(score.b)

    metric_ids = frozenset(metric.id for metric in value_input.metrics)

    return GraphContext(
        documents=tuple(documents),
        value_input=value_input,
        flow_graph=flow_graph,
        activity_ids=frozenset(activity_ids),
        demand_event_ids=frozenset(demand_event_ids),
        value_realization_event_ids=frozenset(value_realization_event_ids),
        metric_ids=metric_ids,
        _relevance=relevance,
        _v_scores=v_scores,
        _b_scores=b_scores,
        _node_properties=node_properties,
    )
