from __future__ import annotations

from langchain_community.graphs.graph_document import GraphDocument

from optimizer.application.scenario_models import GraphFilter, RelevanceHighlight, ValueScenarioInput
from optimizer.graph_analytics.relevance import build_relevance_explain_paths

_VALUE_RELATIONSHIPS = frozenset({"AFFECTS", "SIGNALS", "TOUCHES"})


def list_node_types(documents: list[GraphDocument]) -> tuple[str, ...]:
    types: set[str] = set()
    for document in documents:
        for node in document.nodes:
            if node.type:
                types.add(node.type)
    return tuple(sorted(types))


def list_relationship_types(documents: list[GraphDocument]) -> tuple[str, ...]:
    types: set[str] = set()
    for document in documents:
        for relationship in document.relationships:
            if relationship.type:
                types.add(relationship.type)
    return tuple(sorted(types))


def filter_graph_document(
    documents: list[GraphDocument],
    graph_filter: GraphFilter,
) -> list[GraphDocument]:
    filtered: list[GraphDocument] = []
    for document in documents:
        nodes = list(document.nodes)
        if graph_filter.node_types is not None:
            nodes = [node for node in nodes if node.type in graph_filter.node_types]

        allowed_ids = {node.id for node in nodes}
        relationships = list(document.relationships)
        if graph_filter.relationship_types is not None:
            relationships = [
                relationship
                for relationship in relationships
                if relationship.type in graph_filter.relationship_types
            ]

        relationships = [
            relationship
            for relationship in relationships
            if relationship.source.id in allowed_ids
            and relationship.target.id in allowed_ids
        ]

        filtered.append(
            GraphDocument(
                nodes=nodes,
                relationships=relationships,
                source=document.source,
            )
        )
    return filtered


def _node_by_id(document: GraphDocument) -> dict[str, object]:
    return {node.id: node for node in document.nodes}


def _relationships_for(document: GraphDocument):
    return list(document.relationships)


def _collect_process_neighborhood(
    document: GraphDocument,
    process_id: str,
) -> set[str]:
    nodes_by_id = _node_by_id(document)
    included = {process_id}

    for node in document.nodes:
        if node.type == "Activity":
            properties = node.properties or {}
            if properties.get("process_id") == process_id:
                included.add(node.id)

    for relationship in document.relationships:
        if relationship.type == "PART_OF" and relationship.target.id == process_id:
            included.add(relationship.source.id)

    value_targets: set[str] = set()
    for relationship in document.relationships:
        if relationship.type not in _VALUE_RELATIONSHIPS:
            continue
        if relationship.source.id in included:
            value_targets.add(relationship.target.id)
        if relationship.target.id in included:
            value_targets.add(relationship.source.id)
    included.update(value_targets)

    if process_id in nodes_by_id:
        included.add(process_id)
    return included


def _collect_activity_neighborhood(
    document: GraphDocument,
    activity_id: str,
    *,
    value_input: ValueScenarioInput | None = None,
    value_stream_trees=(),
) -> set[str]:
    """Activity, its process, scored value paths, and value-stream trees through it."""
    included = {activity_id}

    for relationship in document.relationships:
        if relationship.type == "PART_OF" and relationship.source.id == activity_id:
            included.add(relationship.target.id)
        if relationship.type == "PART_OF" and relationship.target.id == activity_id:
            included.add(relationship.source.id)

    node = _node_by_id(document).get(activity_id)
    if node is not None:
        process_id = (node.properties or {}).get("process_id")
        if process_id:
            included.add(process_id)

    if value_input is not None:
        included.update(
            explain_activity_relevance([document], value_input, activity_id).node_ids
        )
    else:
        for relationship in document.relationships:
            if relationship.type not in _VALUE_RELATIONSHIPS:
                continue
            if relationship.source.id == activity_id:
                included.add(relationship.target.id)
            elif relationship.target.id == activity_id:
                included.add(relationship.source.id)

    # ponytail: events come only from value-stream trees that contain the activity.
    # Walk PRECEDES ancestors/descendants when a scored activity sits on no tree.
    for tree in value_stream_trees:
        if activity_id in tree.activity_ids:
            included.update(tree.node_ids)

    return included


def explain_activity_relevance(
    documents: list[GraphDocument],
    value_input: ValueScenarioInput,
    activity_id: str,
) -> RelevanceHighlight:
    """Highlight sets for one activity's relevance paths; does not prune the graph."""
    return build_relevance_explain_paths(documents, value_input, activity_id)


def merge_explain_highlight_into_documents(
    filtered_documents: list[GraphDocument],
    source_documents: list[GraphDocument],
    highlight: RelevanceHighlight,
) -> list[GraphDocument]:
    """Re-inject explain-path nodes and edges removed by type filters."""
    if not highlight.node_ids or not filtered_documents:
        return filtered_documents

    merged: list[GraphDocument] = []
    for filtered_doc, source_doc in zip(filtered_documents, source_documents):
        nodes_by_id = {node.id: node for node in filtered_doc.nodes}
        relationships = list(filtered_doc.relationships)
        rel_keys = {
            (rel.source.id, rel.target.id, rel.type.upper()) for rel in relationships
        }

        for node in source_doc.nodes:
            if node.id in highlight.node_ids and node.id not in nodes_by_id:
                nodes_by_id[node.id] = node

        for relationship in source_doc.relationships:
            edge_key = (
                relationship.source.id,
                relationship.target.id,
                relationship.type.upper(),
            )
            if edge_key not in highlight.edge_keys or edge_key in rel_keys:
                continue
            if (
                relationship.source.id in nodes_by_id
                and relationship.target.id in nodes_by_id
            ):
                relationships.append(relationship)
                rel_keys.add(edge_key)

        merged.append(
            GraphDocument(
                nodes=list(nodes_by_id.values()),
                relationships=relationships,
                source=filtered_doc.source,
            )
        )
    return merged


def isolate_subgraph(
    documents: list[GraphDocument],
    seed_id: str,
    *,
    value_input: ValueScenarioInput | None = None,
    value_stream_trees=(),
) -> list[GraphDocument]:
    isolated: list[GraphDocument] = []
    for document in documents:
        nodes_by_id = _node_by_id(document)
        seed_node = nodes_by_id.get(seed_id)
        if seed_node is None:
            isolated.append(
                GraphDocument(nodes=[], relationships=[], source=document.source)
            )
            continue

        if seed_node.type == "Process":
            included = _collect_process_neighborhood(document, seed_id)
        else:
            included = _collect_activity_neighborhood(
                document,
                seed_id,
                value_input=value_input,
                value_stream_trees=value_stream_trees,
            )

        nodes = [node for node in document.nodes if node.id in included]
        relationships = [
            relationship
            for relationship in document.relationships
            if relationship.source.id in included and relationship.target.id in included
        ]
        isolated.append(
            GraphDocument(
                nodes=nodes,
                relationships=relationships,
                source=document.source,
            )
        )
    return isolated
