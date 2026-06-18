from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from optimizer.application.run_scenario_view import run_scenario_view
from optimizer.application.scenario_models import (
    MATRIX_TOP_N,
    ActivityDisplayItem,
    ActivityScoreDisplay,
    GraphFilter,
    MatrixDisplayRow,
    MetricRow,
    ScenarioViewModel,
    StrategicBZeroRow,
)
from optimizer.infrastructure.demo_loader import (
    bundle_to_value_input,
    load_demo_bundle,
    resolve_repo_root,
)


def run_demo_scenario(
    scenario_id: str,
    *,
    repo_root: Path | None = None,
    graph_filter: GraphFilter | None = None,
) -> ScenarioViewModel:
    """
    Load a fixture scenario and return a presentation-ready view model.

    No LLM calls; reads manifest + JSON only.
    """
    root = repo_root or resolve_repo_root()
    bundle = load_demo_bundle(scenario_id, repo_root=root)
    value_input = bundle_to_value_input(bundle)
    return run_scenario_view(
        graph_documents=bundle.graph_documents,
        value_input=value_input,
        graph_filter=graph_filter,
        scenario=bundle.scenario,
        metrics=tuple(_build_metrics(bundle.metrics)),
        matrix_rows=tuple(_build_matrix_rows(bundle.relevance, bundle.metrics)),
        strategic_b_zero=tuple(_build_strategic_b_zero(bundle.relevance)),
        activities=tuple(_build_activities(bundle.relevance)),
        process_rollups=tuple(bundle.relevance.get("process_rollups") or []),
    )


def _build_metrics(metrics_doc: dict[str, Any]) -> list[MetricRow]:
    return [
        MetricRow(
            id=item["id"],
            name=item["name"],
            definition=item.get("definition", ""),
            client_need=item.get("client_need", ""),
        )
        for item in metrics_doc.get("metrics", [])
    ]


def _strategic_b_zero_ids(relevance: dict[str, Any]) -> set[str]:
    ids = {
        act["activity_id"]
        for act in relevance.get("activities", [])
        if act.get("strategic_b_zero")
    }
    for entry in relevance.get("strategic_b_zero", []):
        ids.add(entry["activity_id"])
    return ids


def _build_matrix_rows(
    relevance: dict[str, Any], metrics_doc: dict[str, Any]
) -> list[MatrixDisplayRow]:
    activities_by_id = {
        act["activity_id"]: act for act in relevance.get("activities", [])
    }
    metric_names = {m["id"]: m["name"] for m in metrics_doc.get("metrics", [])}
    excluded = _strategic_b_zero_ids(relevance)

    by_metric: dict[str, list[MatrixDisplayRow]] = defaultdict(list)
    for cell in relevance.get("matrix", []):
        activity_id = cell["activity_id"]
        if activity_id in excluded:
            continue
        relevance_val = cell.get("relevance")
        if relevance_val is None:
            continue
        activity = activities_by_id.get(activity_id, {})
        row = MatrixDisplayRow(
            activity_id=activity_id,
            activity_name=activity.get("activity_name", activity_id),
            metric_id=cell["metric_id"],
            relevance=float(relevance_val),
        )
        by_metric[row.metric_id].append(row)

    rows: list[MatrixDisplayRow] = []
    for metric_id in metric_names:
        metric_rows = by_metric.get(metric_id, [])
        metric_rows.sort(key=lambda item: item.relevance, reverse=True)
        rows.extend(metric_rows[:MATRIX_TOP_N])
    return rows


def _build_strategic_b_zero(relevance: dict[str, Any]) -> list[StrategicBZeroRow]:
    entries: list[StrategicBZeroRow] = []
    for raw in relevance.get("strategic_b_zero", []):
        entries.append(
            StrategicBZeroRow(
                activity_id=raw["activity_id"],
                activity_name=raw.get("activity_name", raw["activity_id"]),
                b_zero_reason=raw.get("b_zero_reason") or "",
            )
        )
    if entries:
        return entries

    for act in relevance.get("activities", []):
        if not act.get("strategic_b_zero"):
            continue
        entries.append(
            StrategicBZeroRow(
                activity_id=act["activity_id"],
                activity_name=act.get("activity_name", act["activity_id"]),
                b_zero_reason=act.get("b_zero_reason") or "",
            )
        )
    return entries


def _build_activities(relevance: dict[str, Any]) -> list[ActivityDisplayItem]:
    items: list[ActivityDisplayItem] = []
    for act in relevance.get("activities", []):
        scores = tuple(
            ActivityScoreDisplay(
                metric_id=score["metric_id"],
                g=score.get("g"),
                j=score.get("j"),
                dv=score.get("dv"),
                b=score.get("b"),
                relevance=score.get("relevance"),
                pct_contribution=score.get("pct_contribution"),
            )
            for score in act.get("scores", [])
        )
        items.append(
            ActivityDisplayItem(
                activity_id=act["activity_id"],
                activity_name=act.get("activity_name", act["activity_id"]),
                process_id=act.get("process_id", ""),
                strategic_b_zero=bool(act.get("strategic_b_zero")),
                b_zero_reason=act.get("b_zero_reason"),
                scores=scores,
            )
        )
    return items
