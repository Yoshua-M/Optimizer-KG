"""Backward-compatible re-exports; new UI lives in ``scenario_views``."""

from optimizer.presentation.scenario_views import (
    build_graph_filter,
    render_activity_detail,
    render_activity_sidebar,
    render_graph_embed,
    render_graph_tab,
    render_value_tab,
)

__all__ = [
    "build_graph_filter",
    "render_activity_detail",
    "render_activity_sidebar",
    "render_graph_embed",
    "render_graph_tab",
    "render_value_tab",
]
