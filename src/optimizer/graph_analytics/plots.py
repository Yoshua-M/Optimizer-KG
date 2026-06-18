from __future__ import annotations

import math

from optimizer.application.scenario_models import (
    PlotPoint,
    PlotSeries,
    TopContribution,
    ValueScenarioInput,
)
from optimizer.graph_analytics.relevance import top_n_by_distance


def format_metric_label(metric_id: str, metrics: tuple) -> str:
    for metric in metrics:
        if metric.id == metric_id:
            return f"{metric_id} — {metric.name}"
    return metric_id


def format_process_label(process_id: str, process_labels: dict[str, str]) -> str:
    name = process_labels.get(process_id)
    if not name:
        return process_id
    if name == process_id:
        return process_id
    return f"{process_id} — {name}"


def format_activity_label(activity_id: str, activity_name: str) -> str:
    if not activity_name or activity_name == activity_id:
        return activity_id
    return f"{activity_id} — {activity_name}"


def _plot_point(
    entity_id: str,
    entity_name: str,
    x: float,
    y: float,
) -> PlotPoint:
    return PlotPoint(
        entity_id=entity_id,
        entity_name=entity_name,
        x=x,
        y=y,
        distance_from_origin=math.hypot(x, y),
    )


def _max_relevance(activity) -> float:
    if not activity.scores:
        return 0.0
    return max(float(score.relevance or 0.0) for score in activity.scores)


def _metrics_affected_count(activity) -> int:
    return sum(1 for score in activity.scores if (score.relevance or 0.0) > 0)


def _processes_affected_count(activity) -> int:
    if not activity.process_id:
        return 0
    return 1


def _plot_eligible_activities(scenario: ValueScenarioInput):
    return tuple(
        activity for activity in scenario.activities if not activity.strategic_b_zero
    )


def build_plot_series(scenario: ValueScenarioInput) -> PlotSeries:
    eligible = _plot_eligible_activities(scenario)

    relevance_scatter = tuple(
        _plot_point(
            activity.activity_id,
            format_activity_label(activity.activity_id, activity.activity_name),
            _max_relevance(activity),
            float(_metrics_affected_count(activity)),
        )
        for activity in eligible
    )
    v_scatter = tuple(
        _plot_point(
            activity.activity_id,
            format_activity_label(activity.activity_id, activity.activity_name),
            float(activity.v),
            float(_processes_affected_count(activity)),
        )
        for activity in eligible
    )
    v_relevance_scatter = tuple(
        _plot_point(
            activity.activity_id,
            format_activity_label(activity.activity_id, activity.activity_name),
            float(activity.v),
            _max_relevance(activity),
        )
        for activity in eligible
    )

    process_metrics: dict[str, set[str]] = {}
    process_relevance_sum: dict[str, float] = {}
    for rollup in scenario.process_rollups:
        process_metrics.setdefault(rollup.process_id, set()).add(rollup.metric_id)
        process_relevance_sum[rollup.process_id] = (
            process_relevance_sum.get(rollup.process_id, 0.0) + rollup.relevance_sum
        )

    process_scatter = tuple(
        _plot_point(
            process_id,
            format_process_label(process_id, scenario.process_labels),
            process_relevance_sum[process_id],
            float(len(process_metrics[process_id])),
        )
        for process_id in sorted(process_metrics)
    )

    return PlotSeries(
        relevance_scatter=relevance_scatter,
        v_scatter=v_scatter,
        v_relevance_scatter=v_relevance_scatter,
        process_scatter=process_scatter,
        top_relevance=top_n_by_distance(relevance_scatter),
        top_v=top_n_by_distance(v_scatter),
        top_v_relevance=top_n_by_distance(v_relevance_scatter),
        top_process=top_n_by_distance(process_scatter),
    )


def build_top_contributions(
    scenario: ValueScenarioInput,
    *,
    n: int = 3,
) -> tuple[TopContribution, ...]:
    ranked = sorted(
        scenario.process_rollups,
        key=lambda rollup: rollup.pct_contribution,
        reverse=True,
    )
    contributions: list[TopContribution] = []
    for rollup in ranked[:n]:
        contributions.append(
            TopContribution(
                process_id=rollup.process_id,
                metric_id=rollup.metric_id,
                metric_label=format_metric_label(rollup.metric_id, scenario.metrics),
                pct_contribution=rollup.pct_contribution,
            )
        )
    return tuple(contributions)
