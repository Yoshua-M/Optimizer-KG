from __future__ import annotations

from langchain_community.graphs.graph_document import GraphDocument

from optimizer.application.graph_filter import (
    explain_activity_relevance,
    filter_graph_document,
    isolate_subgraph,
    list_node_types,
    list_relationship_types,
    merge_explain_highlight_into_documents,
)
from optimizer.application.scenario_models import (
    CrossValidationDisplay,
    GraphFilter,
    ScenarioViewModel,
    ValueScenarioInput,
)
from optimizer.application.value_insights import (
    build_edge_relevance_map,
    build_indirect_relevance_map,
    build_plot_series,
    format_metric_label,
    format_process_label,
)
from optimizer.graph_analytics.enhanced_scoring import node_confidence, relationship_confidence
from optimizer.graph_analytics.graph_bridge import GraphContext, build_graph_context
from optimizer.graph_analytics.models import ActivityCategory, HighlightPayload
from optimizer.graph_analytics.relevance import build_cumulative_relevance_scores
from optimizer.graph_analytics.run_catalog import run_all_analytics
from optimizer.graph_analytics.value_streams import (
    _metric_affectation_keys,
    build_value_stream_focus,
    discover_value_streams,
)
from optimizer.infrastructure.visualization.colors import confidence_gradient_color
from optimizer.infrastructure.visualization.pyvis_graph import (
    VS_BOUNDARY_EVENT_COLOR,
    VS_CATEGORY_COLORS,
    VS_FLOW_EDGE_COLOR,
    VS_METRIC_DRIVER_NODE_COLOR,
    VS_METRIC_EDGE_COLOR,
    VS_METRIC_NODE_COLOR,
    VS_SUPPORT_EDGE_COLOR,
    VisualizeOptions,
    relevance_heatmap_color,
    visualize_graph,
)

GENERATED_DEFAULT_OPACITY = 0.2
_ISOLATION_SEED_COLOR = "#FFEB3B"
_ISOLATION_SEED_SIZE = 40.0


def _stamp_activity_evaluation(
    documents: list[GraphDocument],
    value_input: ValueScenarioInput,
) -> None:
    rows = {activity.activity_id: activity for activity in value_input.activities}
    for document in documents:
        for node in document.nodes:
            if node.type != "Activity":
                continue
            row = rows.get(node.id)
            if row is None:
                continue
            props = dict(node.properties or {})
            props.update(p=row.p, c=row.c, f=row.f, r=row.r, v=row.v)
            node.properties = props


def _build_vs_color_overrides(
    classifications: dict[str, ActivityCategory],
    *,
    boundary_event_ids: frozenset[str] = frozenset(),
    metric_ids: frozenset[str] = frozenset(),
    metric_driver_ids: frozenset[str] = frozenset(),
) -> dict[str, str]:
    overrides = {
        activity_id: VS_CATEGORY_COLORS[category.value]
        for activity_id, category in classifications.items()
    }
    for event_id in boundary_event_ids:
        overrides[event_id] = VS_BOUNDARY_EVENT_COLOR
    for metric_id in metric_ids:
        overrides[metric_id] = VS_METRIC_NODE_COLOR
    for driver_id in metric_driver_ids:
        overrides[driver_id] = VS_METRIC_DRIVER_NODE_COLOR
    return overrides


def _build_vs_edge_width_overrides(
    highlight_edge_keys: frozenset[tuple[str, str, str]],
    node_scores: dict[str, float],
) -> dict[tuple[str, str, str], float]:
    if not node_scores:
        return {}
    max_score = max(node_scores.values()) or 1.0
    overrides: dict[tuple[str, str, str], float] = {}
    for source_id, target_id, rel_type in highlight_edge_keys:
        if rel_type != "PRECEDES":
            continue
        score = node_scores.get(target_id, 0.0)
        norm = score / max_score
        overrides[(source_id, target_id, rel_type)] = 1.0 + norm * 4.0
    return overrides


def _build_backbone_node_sizes(
    node_overlap: dict[str, int],
    backbone: frozenset[str],
) -> dict[str, float]:
    if not backbone:
        return {}
    return {
        node_id: min(25.0, 10.0 + node_overlap.get(node_id, 0) * 3.0)
        for node_id in backbone
    }


def _event_label_by_id(graph_documents: list[GraphDocument]) -> dict[str, str]:
    labels: dict[str, str] = {}
    if not graph_documents:
        return labels
    for node in graph_documents[0].nodes:
        if node.type != "Event":
            continue
        properties = node.properties or {}
        display = properties.get("label") or node.id
        labels[node.id] = f"{node.id} — {display}" if display != node.id else node.id
    return labels


def _build_vs_edge_color_overrides(
    highlight_edge_keys: frozenset[tuple[str, str, str]],
    activity_classifications: dict[str, ActivityCategory],
) -> dict[tuple[str, str, str], str]:
    support_categories = {
        ActivityCategory.STRUCTURAL_SUPPORT,
        ActivityCategory.SEMANTIC_SUPPORT,
    }
    support_ids = {
        activity_id
        for activity_id, category in activity_classifications.items()
        if category in support_categories
    }
    overrides: dict[tuple[str, str, str], str] = {}
    for edge_key in highlight_edge_keys:
        source_id, target_id, rel_type = edge_key
        if rel_type == "PRECEDES":
            if source_id in support_ids or target_id in support_ids:
                overrides[edge_key] = VS_SUPPORT_EDGE_COLOR
            else:
                overrides[edge_key] = VS_FLOW_EDGE_COLOR
        elif rel_type in ("AFFECTS", "DRIVES"):
            overrides[edge_key] = VS_METRIC_EDGE_COLOR
    return overrides


def _highlight_from_finding(finding) -> HighlightPayload:
    if finding.highlight is not None:
        return finding.highlight
    if finding.scores:
        return HighlightPayload(
            node_ids=frozenset(finding.scores.keys()),
            scores=dict(finding.scores),
        )
    return HighlightPayload(node_ids=frozenset())


def _activity_ids_from_documents(documents: list[GraphDocument]) -> frozenset[str]:
    if not documents:
        return frozenset()
    return frozenset(
        node.id for node in documents[0].nodes if node.type == "Activity"
    )


def _build_relevance_heatmap_payload(
    graph_context: GraphContext,
    filtered_docs: list[GraphDocument],
) -> tuple[frozenset[str], frozenset[tuple[str, str, str]], dict[str, str]]:
    """Activity-only highlight with blue→orange cumulative relevance colors; dim all edges."""
    activity_ids = _activity_ids_from_documents(filtered_docs)
    if not activity_ids:
        return frozenset(), frozenset(), {}

    scores = build_cumulative_relevance_scores(graph_context)
    max_score = max((scores.get(activity_id, 0.0) for activity_id in activity_ids), default=0.0)
    max_score = max_score or 1.0

    overrides = {
        activity_id: relevance_heatmap_color(scores.get(activity_id, 0.0) / max_score)
        for activity_id in activity_ids
    }
    return activity_ids, frozenset(), overrides


def _collect_provenance(
    graph_documents: list[GraphDocument],
) -> tuple[frozenset[str], frozenset[tuple[str, str, str]], dict[str, float]]:
    if not graph_documents:
        return frozenset(), frozenset(), {}
    document = graph_documents[0]
    generated_nodes: set[str] = set()
    generated_edges: set[tuple[str, str, str]] = set()
    confidence_by_node: dict[str, float] = {}
    for node in document.nodes:
        props = node.properties or {}
        confidence_by_node[node.id] = node_confidence(props)
        if props.get("generated") is True:
            generated_nodes.add(node.id)
    for rel in document.relationships:
        props = rel.properties or {}
        edge_key = (rel.source.id, rel.target.id, rel.type.upper())
        if props.get("generated") is True or props.get("derived") is True:
            generated_edges.add(edge_key)
    return frozenset(generated_nodes), frozenset(generated_edges), confidence_by_node


def _build_confidence_heatmap_payload(
    filtered_docs: list[GraphDocument],
    confidence_by_node: dict[str, float],
) -> tuple[frozenset[str], frozenset[tuple[str, str, str]], dict[str, str], dict[str, float], dict[tuple[str, str, str], float]]:
    if not filtered_docs:
        return frozenset(), frozenset(), {}, {}, {}
    document = filtered_docs[0]
    node_ids = frozenset(node.id for node in document.nodes)
    node_colors: dict[str, str] = {}
    node_opacity: dict[str, float] = {}
    edge_opacity: dict[tuple[str, str, str], float] = {}
    for node in document.nodes:
        conf = confidence_by_node.get(node.id, 1.0)
        node_colors[node.id] = confidence_gradient_color(conf)
        node_opacity[node.id] = 1.0
    for rel in document.relationships:
        props = rel.properties or {}
        conf = relationship_confidence(props)
        edge_key = (rel.source.id, rel.target.id, rel.type.upper())
        node_colors.setdefault(rel.source.id, confidence_gradient_color(confidence_by_node.get(rel.source.id, conf)))
        node_colors.setdefault(rel.target.id, confidence_gradient_color(confidence_by_node.get(rel.target.id, conf)))
        edge_opacity[edge_key] = max(0.35, conf)
    return node_ids, frozenset(), node_colors, node_opacity, edge_opacity


def _build_generated_opacity_payload(
    filtered_docs: list[GraphDocument],
    generated_nodes: frozenset[str],
    generated_edges: frozenset[tuple[str, str, str]],
    *,
    emphasize_generated: bool,
    opacity: float = 0.2,
) -> tuple[dict[str, float], dict[tuple[str, str, str], float]]:
    if not filtered_docs or emphasize_generated:
        return {}, {}
    document = filtered_docs[0]
    clamped = max(0.05, min(float(opacity), 1.0))
    node_opacity = {
        node.id: clamped
        for node in document.nodes
        if node.id in generated_nodes
    }
    edge_opacity: dict[tuple[str, str, str], float] = {}
    for rel in document.relationships:
        edge_key = (rel.source.id, rel.target.id, rel.type.upper())
        if edge_key in generated_edges:
            edge_opacity[edge_key] = clamped
    return node_opacity, edge_opacity


def run_scenario_view(
    graph_documents: list[GraphDocument],
    value_input: ValueScenarioInput,
    graph_filter: GraphFilter | None = None,
    *,
    scenario=None,
    metrics=(),
    matrix_rows=(),
    strategic_b_zero=(),
    activities=(),
    process_rollups=(),
    evaluation_confidence: float | None = None,
    cross_validation_findings: tuple[CrossValidationDisplay, ...] = (),
) -> ScenarioViewModel:
    """
    Build a unified scenario view model: filter graph → PyVis → value insights.

    Demo and production callers share this orchestration; fixture adapters stay at the edge.
    """
    active_filter = graph_filter or GraphFilter(
        node_types=None,
        relationship_types=None,
        isolation_seed_id=None,
        relevance_pull_enabled=False,
        explain_activity_id=None,
    )

    available_node_types = list_node_types(graph_documents)
    available_relationship_types = list_relationship_types(graph_documents)

    _stamp_activity_evaluation(graph_documents, value_input)
    graph_context = build_graph_context(graph_documents, value_input)
    value_stream_discovery = discover_value_streams(
        graph_context,
        merge_crossing=active_filter.value_stream_merge_crossing,
    )
    catalog_findings = tuple(run_all_analytics(graph_context))

    vs_color_overrides = None
    value_stream_focus = None
    node_size_overrides: dict[str, float] = {}
    edge_width_overrides: dict[tuple[str, str, str], float] = {}
    if active_filter.value_stream_focus_delivery_id:
        focus_discovery = discover_value_streams(
            graph_context,
            merge_crossing=active_filter.value_stream_focus_is_fused,
        )
        value_stream_focus = build_value_stream_focus(
            graph_context,
            focus_discovery,
            active_filter.value_stream_focus_delivery_id,
            include_support=active_filter.value_stream_include_support,
            include_waste=active_filter.value_stream_include_waste,
        )
        if value_stream_focus is not None:
            vs_color_overrides = _build_vs_color_overrides(
                value_stream_focus.activity_classifications,
                boundary_event_ids=value_stream_focus.boundary_event_ids,
                metric_ids=value_stream_focus.metric_ids,
                metric_driver_ids=value_stream_focus.metric_driver_ids,
            )
    elif active_filter.value_stream_overlay:
        overlay_acts = frozenset(
            activity_id
            for activity_id, category in value_stream_discovery.classifications.items()
            if category
            in (
                ActivityCategory.VALUE_STREAM,
                ActivityCategory.STRUCTURAL_SUPPORT,
            )
        )
        _metric_edges, driver_ids, metric_ids = _metric_affectation_keys(
            graph_context,
            overlay_acts,
        )
        vs_color_overrides = _build_vs_color_overrides(
            value_stream_discovery.classifications,
            metric_ids=metric_ids,
            metric_driver_ids=driver_ids,
        )
        node_size_overrides = _build_backbone_node_sizes(
            value_stream_discovery.node_overlap,
            value_stream_discovery.backbone,
        )

    active_analytic_highlight = None
    if active_filter.analytic_highlight_id:
        finding = next(
            (
                item
                for item in catalog_findings
                if item.analytic_id == active_filter.analytic_highlight_id
            ),
            None,
        )
        if finding is not None:
            active_analytic_highlight = _highlight_from_finding(finding)

    generated_nodes, generated_edges, confidence_by_node = _collect_provenance(graph_documents)

    highlight = None
    if active_filter.explain_activity_id:
        highlight = explain_activity_relevance(
            graph_documents,
            value_input,
            active_filter.explain_activity_id,
        )

    filtered_docs = filter_graph_document(graph_documents, active_filter)
    if highlight is not None:
        filtered_docs = merge_explain_highlight_into_documents(
            filtered_docs,
            graph_documents,
            highlight,
        )
    elif active_filter.isolation_seed_id:
        filtered_docs = isolate_subgraph(
            filtered_docs,
            active_filter.isolation_seed_id,
            value_input=value_input,
            value_stream_trees=value_stream_discovery.trees,
        )

    edge_relevance_map = build_edge_relevance_map(value_input)
    indirect_relevance_map = (
        build_indirect_relevance_map(filtered_docs, value_input)
        if active_filter.relevance_pull_enabled
        else {}
    )

    highlight_node_ids = None
    highlight_edge_keys = None
    edge_color_overrides: dict[tuple[str, str, str], str] = {}
    heatmap_color_overrides: dict[str, str] = {}
    node_opacity_overrides: dict[str, float] = {}
    edge_opacity_overrides: dict[tuple[str, str, str], float] = {}
    generated_emphasis_active = False
    if highlight is not None:
        highlight_node_ids = highlight.node_ids
        highlight_edge_keys = highlight.edge_keys
    elif active_analytic_highlight is not None:
        highlight_node_ids = active_analytic_highlight.node_ids
        highlight_edge_keys = active_analytic_highlight.edge_keys
    elif value_stream_focus is not None:
        highlight_node_ids = value_stream_focus.highlight_node_ids
        highlight_edge_keys = value_stream_focus.highlight_edge_keys
        edge_color_overrides = _build_vs_edge_color_overrides(
            highlight_edge_keys,
            value_stream_focus.activity_classifications,
        )
        edge_width_overrides = _build_vs_edge_width_overrides(
            highlight_edge_keys,
            value_stream_focus.node_scores,
        )
    elif active_filter.relevance_heatmap_enabled:
        (
            highlight_node_ids,
            highlight_edge_keys,
            heatmap_color_overrides,
        ) = _build_relevance_heatmap_payload(graph_context, filtered_docs)
    elif active_filter.confidence_heatmap_enabled:
        (
            highlight_node_ids,
            highlight_edge_keys,
            heatmap_color_overrides,
            node_opacity_overrides,
            edge_opacity_overrides,
        ) = _build_confidence_heatmap_payload(filtered_docs, confidence_by_node)
    elif generated_nodes and not active_filter.generated_highlight_enabled:
        node_opacity_overrides, edge_opacity_overrides = _build_generated_opacity_payload(
            filtered_docs,
            generated_nodes,
            generated_edges,
            emphasize_generated=False,
            opacity=active_filter.generated_opacity,
        )
        generated_emphasis_active = True

    node_color_overrides = dict(heatmap_color_overrides or vs_color_overrides or {})
    if highlight is None and active_filter.isolation_seed_id:
        node_size_overrides = {
            **node_size_overrides,
            active_filter.isolation_seed_id: _ISOLATION_SEED_SIZE,
        }
        node_color_overrides[active_filter.isolation_seed_id] = _ISOLATION_SEED_COLOR

    visualize_options = VisualizeOptions(
        relevance_pull_enabled=active_filter.relevance_pull_enabled,
        edge_relevance_map=edge_relevance_map,
        indirect_relevance_map=indirect_relevance_map,
        highlight_node_ids=highlight_node_ids,
        highlight_edge_keys=highlight_edge_keys,
        edge_color_overrides=edge_color_overrides,
        edge_width_overrides=edge_width_overrides,
        node_color_overrides=node_color_overrides,
        node_size_overrides=node_size_overrides,
        node_opacity_overrides=node_opacity_overrides,
        edge_opacity_overrides=edge_opacity_overrides,
        generated_node_ids=generated_nodes,
        generated_edge_keys=generated_edges,
        generated_emphasis_active=generated_emphasis_active,
    )
    graph_network = visualize_graph(filtered_docs, options=visualize_options)

    plot_series = build_plot_series(value_input)
    cumulative_relevance = build_cumulative_relevance_scores(graph_context)
    metric_label_by_id = {
        metric.id: format_metric_label(metric.id, value_input.metrics)
        for metric in value_input.metrics
    }
    process_ids = set(value_input.process_labels)
    for activity in value_input.activities:
        if activity.process_id:
            process_ids.add(activity.process_id)
    process_label_by_id = {
        process_id: format_process_label(process_id, value_input.process_labels)
        for process_id in sorted(process_ids)
    }
    event_labels = _event_label_by_id(graph_documents)

    return ScenarioViewModel(
        scenario=scenario,
        graph_network=graph_network,
        metrics=metrics,
        matrix_rows=matrix_rows,
        strategic_b_zero=strategic_b_zero,
        activities=activities,
        process_rollups=process_rollups,
        plot_series=plot_series,
        metric_label_by_id=metric_label_by_id,
        event_label_by_id=event_labels,
        process_label_by_id=process_label_by_id,
        available_node_types=available_node_types,
        available_relationship_types=available_relationship_types,
        graph_documents=tuple(filtered_docs),
        value_stream_discovery=value_stream_discovery,
        catalog_findings=catalog_findings,
        vs_color_overrides=vs_color_overrides,
        active_analytic_highlight=active_analytic_highlight,
        value_stream_merge_crossing=active_filter.value_stream_merge_crossing,
        cumulative_relevance_by_activity_id=cumulative_relevance,
        graph_context=graph_context,
        evaluation_confidence=evaluation_confidence,
        cross_validation_findings=cross_validation_findings,
        confidence_by_node_id=confidence_by_node,
        generated_node_ids=generated_nodes,
        generated_edge_keys=generated_edges,
    )
