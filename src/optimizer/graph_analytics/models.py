from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ActivityCategory(str, Enum):
    VALUE_STREAM = "value_stream"
    STRUCTURAL_SUPPORT = "structural_support"
    SEMANTIC_SUPPORT = "semantic_support"
    WASTE = "waste"


class AnalyticStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


@dataclass(frozen=True)
class HighlightPayload:
    node_ids: frozenset[str]
    edge_keys: frozenset[tuple[str, str, str]] = field(default_factory=frozenset)
    scores: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalyticFinding:
    analytic_id: str
    title: str
    summary: str
    detail: str
    status: AnalyticStatus
    scores: dict[str, float]
    highlight: HighlightPayload | None
    error_message: str | None


@dataclass(frozen=True)
class ValueStreamTree:
    delivery_event_id: str
    anchor_event_ids: frozenset[str]
    activity_ids: frozenset[str]
    node_ids: frozenset[str]
    edge_keys: frozenset[tuple[str, str, str]]
    node_scores: dict[str, float]
    total_relevance: float


@dataclass(frozen=True)
class ValueStreamDiscoveryResult:
    trees: tuple[ValueStreamTree, ...]
    vs_union: frozenset[str]
    classifications: dict[str, ActivityCategory]
    node_overlap: dict[str, int] = field(default_factory=dict)
    edge_overlap: dict[tuple[str, str], int] = field(default_factory=dict)
    backbone: frozenset[str] = field(default_factory=frozenset)
    group_count: int = 0
    avg_group_size: float = 0.0
    initial_group_count: int = 0
    merge_crossing_applied: bool = False


@dataclass(frozen=True)
class ValueStreamFocus:
    """Per-group focus payload for grey-out graph rendering."""

    delivery_event_id: str
    visible_activity_ids: frozenset[str]
    highlight_node_ids: frozenset[str]
    activity_classifications: dict[str, ActivityCategory]
    metric_ids: frozenset[str] = field(default_factory=frozenset)
    boundary_event_ids: frozenset[str] = field(default_factory=frozenset)
    metric_driver_ids: frozenset[str] = field(default_factory=frozenset)
    highlight_edge_keys: frozenset[tuple[str, str, str]] = field(default_factory=frozenset)
    node_scores: dict[str, float] = field(default_factory=dict)
