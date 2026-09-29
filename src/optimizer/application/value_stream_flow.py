from __future__ import annotations

from dataclasses import dataclass

from optimizer.application.scenario_models import ScenarioViewModel
from optimizer.application.value_insights import format_activity_label
from optimizer.graph_analytics.models import ValueStreamDiscoveryResult, ValueStreamTree
from optimizer.graph_analytics.value_stream_flow import (
    ValueStreamFlowGraph,
    build_value_stream_flow_graph,
)
from optimizer.graph_analytics.value_streams import discover_value_streams


@dataclass(frozen=True)
class FlowStoryOption:
    """One selectable value-stream flow in the Valor tab."""

    label: str
    delivery_event_ids: frozenset[str]
    discovery: ValueStreamDiscoveryResult
    is_fused: bool


def _delivery_count_in_tree(tree: ValueStreamTree, context) -> int:
    return sum(
        1
        for node_id in tree.node_ids
        if node_id in context.value_realization_event_ids
    )


def _fused_story_label(
    tree: ValueStreamTree,
    discovery: ValueStreamDiscoveryResult,
    context,
) -> str:
    activity_count = len(tree.activity_ids)
    delivery_count = _delivery_count_in_tree(tree, context)
    label = (
        f"Fusionada — rel. {tree.total_relevance:.1f} · "
        f"{activity_count} actividades"
    )
    if discovery.initial_group_count > discovery.group_count:
        label += (
            f" · {discovery.initial_group_count} historias → "
            f"{discovery.group_count} grupo(s)"
        )
    elif delivery_count > 1:
        label += f" · {delivery_count} entregas"
    return label


def list_flow_story_options(view_model: ScenarioViewModel) -> tuple[FlowStoryOption, ...]:
    """Fused stories first, then per-delivery stories."""
    context = view_model.graph_context
    if context is None:
        return ()

    per_delivery = discover_value_streams(context, merge_crossing=False)
    fused = discover_value_streams(context, merge_crossing=True)

    options: list[FlowStoryOption] = []

    fused_trees = sorted(
        fused.trees,
        key=lambda tree: (-tree.total_relevance, tree.delivery_event_id),
    )
    for tree in fused_trees:
        options.append(
            FlowStoryOption(
                label=_fused_story_label(tree, fused, context),
                delivery_event_ids=frozenset({tree.delivery_event_id}),
                discovery=fused,
                is_fused=True,
            )
        )

    per_delivery_trees = sorted(
        per_delivery.trees,
        key=lambda tree: (-tree.total_relevance, tree.delivery_event_id),
    )
    for tree in per_delivery_trees:
        delivery_label = view_model.event_label_by_id.get(
            tree.delivery_event_id,
            tree.delivery_event_id,
        )
        options.append(
            FlowStoryOption(
                label=(
                    f"Por entrega — {delivery_label} · rel. "
                    f"{tree.total_relevance:.1f} · {len(tree.activity_ids)} act."
                ),
                delivery_event_ids=frozenset({tree.delivery_event_id}),
                discovery=per_delivery,
                is_fused=False,
            )
        )

    return tuple(options)


def default_flow_story_index(options: tuple[FlowStoryOption, ...]) -> int:
    """Prefer the first fused story when available."""
    for index, option in enumerate(options):
        if option.is_fused:
            return index
    return 0


def _activity_labels_from_graph_documents(
    view_model: ScenarioViewModel,
) -> dict[str, str]:
    """Activity display labels from graph nodes (works without relevance fixtures)."""
    labels: dict[str, str] = {}
    for document in view_model.graph_documents:
        for node in document.nodes:
            if node.type != "Activity":
                continue
            properties = node.properties or {}
            name = str(properties.get("label") or node.id)
            labels[node.id] = format_activity_label(node.id, name)
    return labels


def build_flow_graph_for_selection(
    view_model: ScenarioViewModel,
    option: FlowStoryOption,
) -> ValueStreamFlowGraph | None:
    """Build a Valor-tab flow diagram payload for the selected story option."""
    if view_model.graph_context is None or not option.delivery_event_ids:
        return None

    activity_label_by_id = _activity_labels_from_graph_documents(view_model)
    for activity in view_model.activities:
        activity_label_by_id[activity.activity_id] = format_activity_label(
            activity.activity_id,
            activity.activity_name,
        )

    return build_value_stream_flow_graph(
        view_model.graph_context,
        option.discovery,
        option.delivery_event_ids,
        event_label_by_id=view_model.event_label_by_id,
        activity_label_by_id=activity_label_by_id,
        metric_label_by_id=view_model.metric_label_by_id,
    )
