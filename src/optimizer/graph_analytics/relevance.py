from __future__ import annotations

from langchain_community.graphs.graph_document import GraphDocument

from optimizer.application.scenario_models import (
    PlotPoint,
    RelevanceHighlight,
    ValueScenarioInput,
)


def top_n_by_distance(points: tuple[PlotPoint, ...], *, n: int = 3) -> tuple[PlotPoint, ...]:
    ranked = sorted(
        (point for point in points if point.distance_from_origin > 0),
        key=lambda point: point.distance_from_origin,
        reverse=True,
    )
    return tuple(ranked[:n])


def build_edge_relevance_map(
    scenario: ValueScenarioInput,
) -> dict[tuple[str, str], float]:
    edge_map: dict[tuple[str, str], float] = {}
    for activity in scenario.activities:
        for score in activity.scores:
            if score.relevance is not None:
                edge_map[(activity.activity_id, score.metric_id)] = float(score.relevance)
    return edge_map


def _edge_key(source_id: str, target_id: str, rel_type: str) -> tuple[str, str, str]:
    return (source_id, target_id, rel_type.upper())


def _has_edge(
    relationships,
    source_id: str,
    target_id: str,
    rel_type: str,
) -> bool:
    rel_upper = rel_type.upper()
    return any(
        relationship.type.upper() == rel_upper
        and relationship.source.id == source_id
        and relationship.target.id == target_id
        for relationship in relationships
    )


def _activity_row(value_input: ValueScenarioInput, activity_id: str):
    for activity in value_input.activities:
        if activity.activity_id == activity_id:
            return activity
    return None


def _score_contributes(score) -> bool:
    return (score.relevance or 0.0) > 0


def build_relevance_explain_paths(
    documents: list[GraphDocument],
    value_input: ValueScenarioInput,
    activity_id: str,
) -> RelevanceHighlight:
    """Return node/edge sets for one activity's G/J/DV relevance paths (no graph pruning)."""
    activity = _activity_row(value_input, activity_id)
    if activity is None or not documents:
        return RelevanceHighlight(node_ids=frozenset(), edge_keys=frozenset())

    document = documents[0]
    relationships = list(document.relationships)
    nodes_by_id = {node.id: node for node in document.nodes}

    node_ids: set[str] = {activity_id}
    edge_keys: set[tuple[str, str, str]] = set()

    for score in activity.scores:
        if not _score_contributes(score):
            continue

        metric_id = score.metric_id
        if metric_id in nodes_by_id:
            node_ids.add(metric_id)

        if score.g > 0:
            if _has_edge(relationships, activity_id, metric_id, "AFFECTS"):
                edge_keys.add(_edge_key(activity_id, metric_id, "AFFECTS"))
            process_id = activity.process_id
            if process_id and process_id in nodes_by_id:
                node_ids.add(process_id)
                if _has_edge(relationships, activity_id, process_id, "PART_OF"):
                    edge_keys.add(_edge_key(activity_id, process_id, "PART_OF"))
                if _has_edge(relationships, process_id, metric_id, "CONTRIBUTES_TO"):
                    edge_keys.add(_edge_key(process_id, metric_id, "CONTRIBUTES_TO"))

        if score.j > 0:
            for relationship in relationships:
                if (
                    relationship.type.upper() != "TOUCHES"
                    or relationship.source.id != activity_id
                ):
                    continue
                cjs_id = relationship.target.id
                for signals in relationships:
                    if (
                        signals.type.upper() == "SIGNALS"
                        and signals.source.id == cjs_id
                        and signals.target.id == metric_id
                    ):
                        node_ids.add(cjs_id)
                        edge_keys.add(_edge_key(activity_id, cjs_id, "TOUCHES"))
                        edge_keys.add(_edge_key(cjs_id, metric_id, "SIGNALS"))

        if score.dv > 0:
            for relationship in relationships:
                if (
                    relationship.type.upper() != "AFFECTS"
                    or relationship.source.id != activity_id
                ):
                    continue
                driver_id = relationship.target.id
                driver = nodes_by_id.get(driver_id)
                if driver is None or driver.type == "Metric":
                    continue
                for has_driver in relationships:
                    if (
                        has_driver.type.upper() == "HAS_DRIVER"
                        and has_driver.source.id == driver_id
                        and has_driver.target.id == metric_id
                    ):
                        node_ids.add(driver_id)
                        edge_keys.add(_edge_key(activity_id, driver_id, "AFFECTS"))
                        edge_keys.add(_edge_key(driver_id, metric_id, "HAS_DRIVER"))

    return RelevanceHighlight(
        node_ids=frozenset(node_ids),
        edge_keys=frozenset(edge_keys),
    )


def build_indirect_relevance_map(
    documents: list[GraphDocument],
    value_input: ValueScenarioInput,
) -> dict[tuple[str, str], float]:
    """Activity→metric scores with no direct ``AFFECTS`` edge in the graph."""
    direct_affects: set[tuple[str, str]] = set()
    for document in documents:
        for relationship in document.relationships:
            if relationship.type.upper() == "AFFECTS":
                direct_affects.add((relationship.source.id, relationship.target.id))

    indirect: dict[tuple[str, str], float] = {}
    for activity in value_input.activities:
        for score in activity.scores:
            if score.relevance is None:
                continue
            pair = (activity.activity_id, score.metric_id)
            if pair in direct_affects:
                continue
            indirect[pair] = float(score.relevance)
    return indirect
