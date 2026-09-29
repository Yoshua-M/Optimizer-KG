from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from langchain_community.graphs.graph_document import GraphDocument
from pyvis.network import Network

if TYPE_CHECKING:
    from optimizer.graph_analytics.graph_bridge import GraphContext
    from optimizer.graph_analytics.models import (
        AnalyticFinding,
        HighlightPayload,
        ValueStreamDiscoveryResult,
    )

MATRIX_TOP_N = 15


@dataclass(frozen=True)
class MetricRow:
    id: str
    name: str
    definition: str
    client_need: str


@dataclass(frozen=True)
class ActivityScoreRow:
    metric_id: str
    g: float
    j: float
    dv: float
    b: float
    relevance: float
    pct_contribution: float


@dataclass(frozen=True)
class ActivityRow:
    activity_id: str
    activity_name: str
    process_id: str
    p: float
    c: float
    f: float
    r: float
    v: float
    scores: tuple[ActivityScoreRow, ...]
    strategic_b_zero: bool = False
    b_zero_reason: str | None = None


@dataclass(frozen=True)
class StrategicBZeroRow:
    activity_id: str
    activity_name: str
    b_zero_reason: str


@dataclass(frozen=True)
class ProcessRollupRow:
    process_id: str
    metric_id: str
    relevance_sum: float
    pct_contribution: float


@dataclass(frozen=True)
class ValueScenarioInput:
    metrics: tuple[MetricRow, ...]
    activities: tuple[ActivityRow, ...]
    process_rollups: tuple[ProcessRollupRow, ...]
    strategic_b_zero: tuple[StrategicBZeroRow, ...]
    process_labels: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MatrixDisplayRow:
    activity_id: str
    activity_name: str
    metric_id: str
    relevance: float


@dataclass(frozen=True)
class ActivityScoreDisplay:
    metric_id: str
    g: float | None
    j: float | None
    dv: float | None
    b: float | None
    relevance: float | None
    pct_contribution: float | None


@dataclass(frozen=True)
class ActivityDisplayItem:
    activity_id: str
    activity_name: str
    process_id: str
    strategic_b_zero: bool = False
    b_zero_reason: str | None = None
    scores: tuple[ActivityScoreDisplay, ...] = ()
    p: float | None = None
    c: float | None = None
    f: float | None = None
    r: float | None = None
    v: float | None = None


@dataclass(frozen=True)
class RelevanceHighlight:
    node_ids: frozenset[str]
    edge_keys: frozenset[tuple[str, str, str]]


@dataclass(frozen=True)
class GraphFilter:
    node_types: frozenset[str] | None
    relationship_types: frozenset[str] | None
    isolation_seed_id: str | None
    relevance_pull_enabled: bool
    explain_activity_id: str | None = None
    value_stream_overlay: bool = False
    value_stream_focus_delivery_id: str | None = None
    value_stream_focus_is_fused: bool = False
    value_stream_include_support: bool = False
    value_stream_include_waste: bool = False
    value_stream_merge_crossing: bool = False
    analytic_highlight_id: str | None = None
    relevance_heatmap_enabled: bool = False
    confidence_heatmap_enabled: bool = False
    generated_highlight_enabled: bool = False
    generated_opacity: float = 0.2


@dataclass(frozen=True)
class CrossValidationDisplay:
    activity_id: str
    activity_name: str
    message: str


@dataclass(frozen=True)
class PlotPoint:
    entity_id: str
    entity_name: str
    x: float
    y: float
    distance_from_origin: float


@dataclass(frozen=True)
class TopContribution:
    process_id: str
    metric_id: str
    metric_label: str
    pct_contribution: float


@dataclass(frozen=True)
class PlotSeries:
    relevance_scatter: tuple[PlotPoint, ...]
    v_scatter: tuple[PlotPoint, ...]
    v_relevance_scatter: tuple[PlotPoint, ...]
    process_scatter: tuple[PlotPoint, ...]
    top_relevance: tuple[PlotPoint, ...]
    top_v: tuple[PlotPoint, ...]
    top_v_relevance: tuple[PlotPoint, ...]
    top_process: tuple[PlotPoint, ...]


@dataclass(frozen=True)
class ScenarioViewModel:
    scenario: Any
    graph_network: Network
    metrics: tuple[MetricRow, ...]
    matrix_rows: tuple[MatrixDisplayRow, ...]
    strategic_b_zero: tuple[StrategicBZeroRow, ...]
    activities: tuple[ActivityDisplayItem, ...]
    process_rollups: tuple[dict[str, Any], ...] = ()
    plot_series: PlotSeries | None = None
    metric_label_by_id: dict[str, str] = field(default_factory=dict)
    event_label_by_id: dict[str, str] = field(default_factory=dict)
    process_label_by_id: dict[str, str] = field(default_factory=dict)
    available_node_types: tuple[str, ...] = ()
    available_relationship_types: tuple[str, ...] = ()
    graph_documents: tuple[GraphDocument, ...] = ()
    value_stream_discovery: ValueStreamDiscoveryResult | None = None
    catalog_findings: tuple[AnalyticFinding, ...] = ()
    vs_color_overrides: dict[str, str] | None = None
    active_analytic_highlight: HighlightPayload | None = None
    value_stream_merge_crossing: bool = False
    cumulative_relevance_by_activity_id: dict[str, float] = field(default_factory=dict)
    graph_context: GraphContext | None = None
    evaluation_confidence: float | None = None
    cross_validation_findings: tuple[CrossValidationDisplay, ...] = ()
    confidence_by_node_id: dict[str, float] = field(default_factory=dict)
    generated_node_ids: frozenset[str] = frozenset()
    generated_edge_keys: frozenset[tuple[str, str, str]] = frozenset()
