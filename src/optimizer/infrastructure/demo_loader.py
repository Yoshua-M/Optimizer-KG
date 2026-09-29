from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document

from optimizer.application.demo_models import DemoBundle, DemoScenario
from optimizer.application.scenario_models import (
    ActivityRow,
    ActivityScoreRow,
    MetricRow,
    ProcessRollupRow,
    StrategicBZeroRow,
    ValueScenarioInput,
)

MANIFEST_REL_PATH = Path("configs") / "demo_scenarios.json"
REQUIRED_PATH_KEYS = ("graph", "metrics", "relevance")


class DemoLoadError(Exception):
    """Base error for demo fixture loading."""


class DemoScenarioNotFoundError(DemoLoadError):
    """Scenario id is absent from the manifest."""


class DemoFileMissingError(DemoLoadError):
    """A manifest-referenced fixture file is missing on disk."""


def resolve_repo_root(start: Path | None = None) -> Path:
    """Return repo root (parent of ``configs/``) by walking up from *start*."""
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / MANIFEST_REL_PATH).is_file():
            return candidate

    raise DemoLoadError(f"Could not find {MANIFEST_REL_PATH} above {current}")


def load_manifest(repo_root: Path | None = None) -> list[DemoScenario]:
    root = repo_root or resolve_repo_root()
    manifest_path = root / MANIFEST_REL_PATH
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    scenarios: list[DemoScenario] = []
    for entry in data.get("scenarios", []):
        scenarios.append(
            DemoScenario(
                id=entry["id"],
                title=entry.get("title", entry["id"]),
                description=entry.get("description", ""),
                paths=dict(entry.get("paths", {})),
                kind=entry.get("kind", "value"),
            )
        )
    return scenarios


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise DemoFileMissingError(f"Missing demo fixture: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def graph_json_to_graph_documents(graph: dict[str, Any]) -> list[GraphDocument]:
    """Adapt ``graph.json`` fixture shape to LangChain ``GraphDocument`` list."""
    raw_nodes = graph.get("nodes", [])
    node_by_id: dict[str, Node] = {}

    for raw in raw_nodes:
        node_id = raw["id"]
        properties = dict(raw.get("properties") or {})
        label = raw.get("label")
        if label is not None:
            properties["label"] = label
        node_by_id[node_id] = Node(
            id=node_id,
            type=raw.get("type", ""),
            properties=properties,
        )

    relationships: list[Relationship] = []
    for raw in graph.get("relationships", []):
        source_id = raw.get("source")
        target_id = raw.get("target")
        if source_id not in node_by_id or target_id not in node_by_id:
            continue
        relationships.append(
            Relationship(
                source=node_by_id[source_id],
                target=node_by_id[target_id],
                type=raw.get("type", ""),
                properties=dict(raw.get("properties") or {}),
            )
        )

    return [
        GraphDocument(
            nodes=list(node_by_id.values()),
            relationships=relationships,
            source=Document(page_content=graph.get("title", "demo scenario")),
        )
    ]


def load_demo_bundle(scenario_id: str, repo_root: Path | None = None) -> DemoBundle:
    root = repo_root or resolve_repo_root()
    scenario = next(
        (item for item in load_manifest(root) if item.id == scenario_id),
        None,
    )
    if scenario is None:
        raise DemoScenarioNotFoundError(f"Unknown demo scenario: {scenario_id}")

    paths: dict[str, dict[str, Any]] = {}
    for key in REQUIRED_PATH_KEYS:
        rel_path = scenario.paths.get(key)
        if not rel_path:
            raise DemoFileMissingError(
                f"Scenario {scenario_id} missing required path: {key}"
            )
        paths[key] = _read_json(root / rel_path)

    graph_documents = graph_json_to_graph_documents(paths["graph"])

    return DemoBundle(
        scenario=scenario,
        graph=paths["graph"],
        metrics=paths["metrics"],
        relevance=paths["relevance"],
        graph_documents=graph_documents,
    )


def bundle_to_value_input(bundle: DemoBundle) -> ValueScenarioInput:
    """Map fixture bundle JSON to shared ``ValueScenarioInput`` (sole JSON field adapter)."""
    metrics = tuple(
        MetricRow(
            id=item["id"],
            name=item["name"],
            definition=item.get("definition", ""),
            client_need=item.get("client_need", ""),
        )
        for item in bundle.metrics.get("metrics", [])
    )

    activities: list[ActivityRow] = []
    for act in bundle.relevance.get("activities", []):
        scores = tuple(
            ActivityScoreRow(
                metric_id=score["metric_id"],
                g=float(score.get("g") or 0.0),
                j=float(score.get("j") or 0.0),
                dv=float(score.get("dv") or 0.0),
                b=float(score.get("b") or 0.0),
                relevance=float(score.get("relevance") or 0.0),
                pct_contribution=float(score.get("pct_contribution") or 0.0),
            )
            for score in act.get("scores", [])
        )
        activities.append(
            ActivityRow(
                activity_id=act["activity_id"],
                activity_name=act.get("activity_name", act["activity_id"]),
                process_id=act.get("process_id", ""),
                p=float(act.get("p") or 0.0),
                c=float(act.get("c") or 0.0),
                f=float(act.get("f") or 0.0),
                r=float(act.get("r") or 0.0),
                v=float(act.get("v") or 0.0),
                scores=scores,
                strategic_b_zero=bool(act.get("strategic_b_zero")),
                b_zero_reason=act.get("b_zero_reason"),
            )
        )

    process_rollups = tuple(
        ProcessRollupRow(
            process_id=rollup["process_id"],
            metric_id=rollup["metric_id"],
            relevance_sum=float(rollup.get("relevance_sum") or 0.0),
            pct_contribution=float(rollup.get("pct_contribution") or 0.0),
        )
        for rollup in bundle.relevance.get("process_rollups") or []
    )

    strategic_b_zero: list[StrategicBZeroRow] = []
    for raw in bundle.relevance.get("strategic_b_zero") or []:
        strategic_b_zero.append(
            StrategicBZeroRow(
                activity_id=raw["activity_id"],
                activity_name=raw.get("activity_name", raw["activity_id"]),
                b_zero_reason=raw.get("b_zero_reason") or "",
            )
        )
    if not strategic_b_zero:
        for act in bundle.relevance.get("activities", []):
            if not act.get("strategic_b_zero"):
                continue
            strategic_b_zero.append(
                StrategicBZeroRow(
                    activity_id=act["activity_id"],
                    activity_name=act.get("activity_name", act["activity_id"]),
                    b_zero_reason=act.get("b_zero_reason") or "",
                )
            )

    process_labels: dict[str, str] = {}
    for node in bundle.graph.get("nodes", []):
        if node.get("type") != "Process":
            continue
        process_labels[node["id"]] = node.get("label") or node["id"]

    return ValueScenarioInput(
        metrics=metrics,
        activities=tuple(activities),
        process_rollups=process_rollups,
        strategic_b_zero=tuple(strategic_b_zero),
        process_labels=process_labels,
    )
