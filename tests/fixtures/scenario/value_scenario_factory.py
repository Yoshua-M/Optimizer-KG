"""Build ``ValueScenarioInput`` for tests without ``demo_loader`` (ui2-01)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from optimizer.application.scenario_models import ValueScenarioInput


def minimal_value_scenario(*, include_b_zero: bool = False) -> ValueScenarioInput:
    """Single activity, single metric — mirrors ``tests/fixtures/demo/minimal/relevance.json``."""
    from optimizer.application.scenario_models import (
        ActivityRow,
        ActivityScoreRow,
        MetricRow,
        StrategicBZeroRow,
        ValueScenarioInput,
    )

    metrics = (
        MetricRow(
            id="M-01",
            name="On-Time Delivery",
            definition="Share of deliveries within agreed window",
            client_need="Operational continuity",
        ),
    )
    activities = (
        ActivityRow(
            activity_id="A-01",
            activity_name="Track daily rack prices",
            process_id="P-01",
            p=0.5,
            c=0.5,
            f=0.5,
            r=0.5,
            v=0.5,
            scores=(
                ActivityScoreRow(
                    metric_id="M-01",
                    g=1.0,
                    j=0.0,
                    dv=0.0,
                    b=0.4,
                    relevance=0.2,
                    pct_contribution=1.0,
                ),
            ),
            strategic_b_zero=False,
            b_zero_reason=None,
        ),
    )
    strategic_b_zero: tuple[StrategicBZeroRow, ...] = ()
    if include_b_zero:
        activities = activities + (
            ActivityRow(
                activity_id="A-02",
                activity_name="Legacy compliance audit",
                process_id="P-99",
                p=0.0,
                c=0.0,
                f=0.0,
                r=0.0,
                v=1.0,
                scores=(),
                strategic_b_zero=True,
                b_zero_reason="No client value trace in fixture",
            ),
        )
        strategic_b_zero = (
            StrategicBZeroRow(
                activity_id="A-02",
                activity_name="Legacy compliance audit",
                b_zero_reason="No client value trace in fixture",
            ),
        )

    return ValueScenarioInput(
        metrics=metrics,
        activities=activities,
        process_rollups=(),
        strategic_b_zero=strategic_b_zero,
        process_labels={"P-01": "Market Intelligence", "P-99": "Compliance"},
    )


def multi_metric_value_scenario() -> ValueScenarioInput:
    """Two activities with distinct plot coordinates for ui2 analytics tests."""
    from optimizer.application.scenario_models import (
        ActivityRow,
        ActivityScoreRow,
        MetricRow,
        ProcessRollupRow,
        ValueScenarioInput,
    )

    metrics = (
        MetricRow(id="M-01", name="Metric One", definition="", client_need=""),
        MetricRow(id="M-02", name="Metric Two", definition="", client_need=""),
    )
    activities = (
        ActivityRow(
            activity_id="A-01",
            activity_name="High spread activity",
            process_id="P-01",
            p=0.3,
            c=0.3,
            f=0.3,
            r=0.3,
            v=0.9,
            scores=(
                ActivityScoreRow(
                    metric_id="M-01",
                    g=0.0,
                    j=0.0,
                    dv=0.0,
                    b=0.0,
                    relevance=0.1,
                    pct_contribution=0.1,
                ),
                ActivityScoreRow(
                    metric_id="M-02",
                    g=0.0,
                    j=0.0,
                    dv=0.0,
                    b=0.0,
                    relevance=0.5,
                    pct_contribution=0.5,
                ),
            ),
        ),
        ActivityRow(
            activity_id="A-02",
            activity_name="Origin activity",
            process_id="P-01",
            p=0.0,
            c=0.0,
            f=0.0,
            r=0.0,
            v=0.0,
            scores=(
                ActivityScoreRow(
                    metric_id="M-01",
                    g=0.0,
                    j=0.0,
                    dv=0.0,
                    b=0.0,
                    relevance=0.0,
                    pct_contribution=0.0,
                ),
            ),
        ),
    )
    return ValueScenarioInput(
        metrics=metrics,
        activities=activities,
        process_rollups=(
            ProcessRollupRow(
                process_id="P-01",
                metric_id="M-01",
                relevance_sum=0.6,
                pct_contribution=0.4,
            ),
            ProcessRollupRow(
                process_id="P-01",
                metric_id="M-02",
                relevance_sum=0.5,
                pct_contribution=0.3,
            ),
            ProcessRollupRow(
                process_id="P-02",
                metric_id="M-02",
                relevance_sum=0.9,
                pct_contribution=0.9,
            ),
        ),
        strategic_b_zero=(),
        process_labels={"P-01": "Process One", "P-02": "Process Two"},
    )
