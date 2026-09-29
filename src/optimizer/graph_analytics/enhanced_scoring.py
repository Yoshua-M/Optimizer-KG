from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import networkx as nx
from langchain_community.graphs.graph_document import GraphDocument

from optimizer.application.scenario_models import (
    ActivityRow,
    ActivityScoreRow,
    MetricRow,
    ProcessRollupRow,
    ValueScenarioInput,
)

V_WEIGHTS = {"p": 0.3, "c": 0.4, "f": 0.2, "r": 0.1}
BRIDGE_W = (0.4, 0.4, 0.2)  # G, J, DV
CROSS_VALIDATION_THRESHOLD = 0.25

CJS_METRIC_SIGNALS: dict[tuple[str, str], float] = {
    ("CJS-04", "MET-01"): 0.85,
    ("CJS-05", "MET-02"): 0.85,
    ("CJS-06", "MET-03"): 0.85,
}


@dataclass(frozen=True)
class DimensionValue:
    value: float | None
    confidence: float | None = None


@dataclass(frozen=True)
class EnhancedActivityInput:
    activity_id: str
    activity_name: str
    process_id: str
    p: DimensionValue
    c: DimensionValue
    f: DimensionValue
    r: DimensionValue
    team_id: str = ""


@dataclass
class Phase2ActivityScores:
    value_proximity: float | None = None
    leverage: float | None = None
    coherence_flags: list[str] = field(default_factory=list)
    refinement_priority: float | None = None


@dataclass(frozen=True)
class CrossValidationFinding:
    activity_id: str
    activity_name: str
    semantic_p: float
    proximity_norm: float
    divergence: float
    message: str


@dataclass(frozen=True)
class EnhancedScoringResult:
    value_input: ValueScenarioInput
    evaluation_confidence: float | None
    phase2_by_activity: dict[str, Phase2ActivityScores]
    cross_validation_findings: tuple[CrossValidationFinding, ...]
    proximity_by_activity: dict[str, float]


def normalize_corroboration(raw: int | float | None) -> float:
    if raw is None:
        return 0.0
    return min(float(raw), 3.0) / 3.0


def compose_v(
    p: float | None,
    c: float | None,
    f: float | None,
    r: float | None,
) -> float | None:
    dims = {"p": p, "c": c, "f": f, "r": r}
    present = {key: value for key, value in dims.items() if value is not None}
    if not present:
        return None
    total_weight = sum(V_WEIGHTS[key] for key in present)
    if total_weight <= 0:
        return None
    return sum(V_WEIGHTS[key] * present[key] for key in present) / total_weight


def dimension_confidence(conf: float | None, *, default: float = 1.0) -> float:
    if conf is None:
        return default
    return max(0.0, min(float(conf), 1.0))


def activity_evaluation_confidence(activity: EnhancedActivityInput) -> float | None:
    pairs = [
        (activity.p.value, activity.p.confidence),
        (activity.c.value, activity.c.confidence),
        (activity.f.value, activity.f.confidence),
        (activity.r.value, activity.r.confidence),
    ]
    present = [(value, conf) for value, conf in pairs if value is not None]
    if not present:
        return None
    weighted = 0.0
    total = 0.0
    for value, conf in present:
        weight = abs(float(value)) or 0.25
        c = dimension_confidence(conf)
        weighted += weight * c
        total += weight
    return weighted / total if total > 0 else None


def overall_evaluation_confidence(activities: tuple[EnhancedActivityInput, ...]) -> float | None:
    scores = [
        score
        for act in activities
        if (score := activity_evaluation_confidence(act)) is not None
    ]
    if not scores:
        return None
    return sum(scores) / len(scores)


def _index_graph(graph: dict[str, Any]) -> tuple[
    dict[tuple[str, str], float],
    set[tuple[str, str]],
    set[tuple[str, str]],
    dict[str, str],
    dict[str, str],
]:
    affects_conf: dict[tuple[str, str], float] = {}
    touches: set[tuple[str, str]] = set()
    process_metric: set[tuple[str, str]] = set()
    driver_parent: dict[str, str] = {}
    activity_process: dict[str, str] = {}

    for node in graph.get("nodes", []):
        if node.get("type") == "Activity":
            props = node.get("properties") or {}
            if props.get("process_id"):
                activity_process[node["id"]] = props["process_id"]

    for rel in graph.get("relationships", []):
        source = rel["source"]
        target = rel["target"]
        rtype = rel.get("type", "").upper()
        props = rel.get("properties") or {}
        conf = float(props.get("confidence") or 0.5)
        if rtype == "AFFECTS":
            affects_conf[(source, target)] = conf
        elif rtype == "TOUCHES":
            touches.add((source, target))
        elif rtype == "CONTRIBUTES_TO":
            process_metric.add((source, target))
        elif rtype == "DRIVES":
            driver_parent[source] = target

    return affects_conf, touches, process_metric, driver_parent, activity_process


def _g_score(
    aid: str,
    mid: str,
    affects_conf: dict[tuple[str, str], float],
    activity_process: dict[str, str],
    process_metric: set[tuple[str, str]],
) -> float:
    g = 0.0
    if (aid, mid) in affects_conf:
        g = max(g, 1.0 * affects_conf[(aid, mid)])
    pid = activity_process.get(aid)
    if pid and (pid, mid) in process_metric:
        g = max(g, 0.7 * 0.85)
    return g


def _j_score(aid: str, mid: str, touches: set[tuple[str, str]]) -> float:
    best = 0.0
    for activity_id, cjs_id in touches:
        if activity_id != aid:
            continue
        best = max(best, CJS_METRIC_SIGNALS.get((cjs_id, mid), 0.0))
    return best


def _dv_score(
    aid: str,
    mid: str,
    affects_conf: dict[tuple[str, str], float],
    driver_parent: dict[str, str],
) -> float:
    best = 0.0
    for (activity_id, target_id), conf in affects_conf.items():
        if activity_id != aid:
            continue
        if target_id.startswith("MDR-") and driver_parent.get(target_id) == mid:
            best = max(best, 1.0 * conf)
    return best


def _build_flow_graph(documents: list[GraphDocument]) -> nx.DiGraph:
    if not documents:
        return nx.DiGraph()
    document = documents[0]
    flow = nx.DiGraph()
    flow_node_types = {"Activity", "Event"}
    node_ids = {node.id for node in document.nodes}
    for node in document.nodes:
        if node.type in flow_node_types:
            flow.add_node(node.id, node_type=node.type)
    for rel in document.relationships:
        if rel.type.upper() != "PRECEDES":
            continue
        if rel.source.id in flow and rel.target.id in flow:
            flow.add_edge(rel.source.id, rel.target.id)
    return flow


def compute_value_proximity(flow_graph: nx.DiGraph, activity_ids: frozenset[str]) -> dict[str, float]:
    if flow_graph.number_of_nodes() == 0:
        return {}
    try:
        raw = nx.closeness_centrality(flow_graph)
    except nx.NetworkXError:
        return {}
    activity_vals = {aid: raw.get(aid, 0.0) for aid in activity_ids if aid in raw}
    if not activity_vals:
        return {}
    max_val = max(activity_vals.values()) or 1.0
    return {aid: val / max_val for aid, val in activity_vals.items()}


def compute_leverage(flow_graph: nx.DiGraph, metric_ids: frozenset[str], documents: list[GraphDocument]) -> dict[str, float]:
    if flow_graph.number_of_nodes() == 0:
        return {}
    try:
        betweenness = nx.betweenness_centrality(flow_graph)
    except nx.NetworkXError:
        betweenness = {}

    metric_reachable: set[str] = set()
    if documents:
        document = documents[0]
        for rel in document.relationships:
            if rel.type.upper() in ("AFFECTS", "CONTRIBUTES_TO") and rel.target.id in metric_ids:
                metric_reachable.add(rel.source.id)

    combined: dict[str, float] = {}
    for node_id in flow_graph.nodes:
        if flow_graph.nodes[node_id].get("node_type") != "Activity":
            continue
        bet = betweenness.get(node_id, 0.0)
        reach_bonus = 0.15 if node_id in metric_reachable else 0.0
        combined[node_id] = bet + reach_bonus
    if not combined:
        return {}
    max_val = max(combined.values()) or 1.0
    return {aid: val / max_val for aid, val in combined.items()}


def compute_coherence_flags(
    documents: list[GraphDocument],
    flow_graph: nx.DiGraph,
    demand_event_ids: frozenset[str],
) -> dict[str, list[str]]:
    flags: dict[str, list[str]] = {}
    if not documents:
        return flags
    document = documents[0]
    node_ids = {node.id for node in document.nodes}
    connected = set()
    for rel in document.relationships:
        connected.add(rel.source.id)
        connected.add(rel.target.id)

    for node in document.nodes:
        node_flags: list[str] = []
        if node.id not in connected and node.type in ("Activity", "Event", "Metric"):
            node_flags.append("dangling")
        if node.type == "Activity" and node.id in flow_graph:
            if flow_graph.in_degree(node.id) == 0 and flow_graph.out_degree(node.id) == 0:
                node_flags.append("flow_isolated")
        if node_flags:
            flags[node.id] = node_flags

    for event_id in demand_event_ids:
        if event_id in flow_graph and flow_graph.out_degree(event_id) == 0:
            flags.setdefault(event_id, []).append("orphaned_demand")

    try:
        if not nx.is_directed_acyclic_graph(flow_graph):
            for cycle in nx.simple_cycles(flow_graph):
                for node_id in cycle:
                    flags.setdefault(node_id, []).append("cycle_in_flow")
                break
    except nx.NetworkXError:
        pass

    return flags


def compute_refinement_priority(
    activity_id: str,
    node_props: dict[str, Any],
    leverage: float | None,
) -> float | None:
    if leverage is None:
        return None
    confidence = node_props.get("confidence")
    if confidence is None:
        confidence = 1.0 if not node_props.get("generated") else 0.5
    confidence_deficit = 1.0 - float(confidence)
    informant_distance = float(node_props.get("informant_distance") or 1.0)
    return round(confidence_deficit * leverage * informant_distance, 4)


def cross_validate_p_vs_proximity(
    activities: tuple[EnhancedActivityInput, ...],
    proximity_by_activity: dict[str, float],
    *,
    threshold: float = CROSS_VALIDATION_THRESHOLD,
) -> tuple[CrossValidationFinding, ...]:
    findings: list[CrossValidationFinding] = []
    for act in activities:
        if act.p.value is None:
            continue
        prox = proximity_by_activity.get(act.activity_id)
        if prox is None:
            continue
        divergence = abs(float(act.p.value) - prox)
        if divergence < threshold:
            continue
        findings.append(
            CrossValidationFinding(
                activity_id=act.activity_id,
                activity_name=act.activity_name,
                semantic_p=float(act.p.value),
                proximity_norm=prox,
                divergence=round(divergence, 4),
                message=(
                    f"Divergencia Fase-1 vs Fase-2: P semántico={act.p.value:.2f}, "
                    f"proximidad topológica={prox:.2f} (Δ={divergence:.2f})"
                ),
            )
        )
    return tuple(findings)


def _parse_dimension(raw: dict[str, Any], key: str) -> DimensionValue:
    value = raw.get(key)
    conf_key = f"{key}_confidence"
    conf = raw.get(conf_key)
    if value is None:
        return DimensionValue(value=None, confidence=conf)
    return DimensionValue(value=float(value), confidence=float(conf) if conf is not None else None)


def parse_enhanced_activities(relevance: dict[str, Any]) -> tuple[EnhancedActivityInput, ...]:
    activities: list[EnhancedActivityInput] = []
    for raw in relevance.get("activities", []):
        activities.append(
            EnhancedActivityInput(
                activity_id=raw["activity_id"],
                activity_name=raw.get("activity_name", raw["activity_id"]),
                process_id=raw.get("process_id", ""),
                team_id=raw.get("team_id", ""),
                p=_parse_dimension(raw, "p"),
                c=_parse_dimension(raw, "c"),
                f=_parse_dimension(raw, "f"),
                r=_parse_dimension(raw, "r"),
            )
        )
    return tuple(activities)


def compose_enhanced_value_input(
    graph: dict[str, Any],
    metrics_doc: dict[str, Any],
    relevance: dict[str, Any],
    graph_documents: list[GraphDocument],
) -> EnhancedScoringResult:
    enhanced_activities = parse_enhanced_activities(relevance)
    metric_rows = tuple(
        MetricRow(
            id=item["id"],
            name=item["name"],
            definition=item.get("definition", ""),
            client_need=item.get("client_need", item.get("definition", "")),
        )
        for item in metrics_doc.get("metrics", [])
    )
    metric_ids = frozenset(m.id for m in metric_rows)

    affects_conf, touches, process_metric, driver_parent, activity_process = _index_graph(graph)
    flow_graph = _build_flow_graph(graph_documents)
    activity_ids = frozenset(
        node["id"] for node in graph.get("nodes", []) if node.get("type") == "Activity"
    )
    demand_events = frozenset(
        node["id"]
        for node in graph.get("nodes", [])
        if node.get("type") == "Event"
        and (node.get("properties") or {}).get("event_type") == "demand"
    )

    proximity_by_activity = compute_value_proximity(flow_graph, activity_ids)
    leverage_by_activity = compute_leverage(flow_graph, metric_ids, graph_documents)
    coherence = compute_coherence_flags(graph_documents, flow_graph, demand_events)

    node_props_by_id = {
        node["id"]: dict(node.get("properties") or {})
        for node in graph.get("nodes", [])
    }

    phase2: dict[str, Phase2ActivityScores] = {}
    for aid in activity_ids:
        props = node_props_by_id.get(aid, {})
        lev = leverage_by_activity.get(aid)
        phase2[aid] = Phase2ActivityScores(
            value_proximity=proximity_by_activity.get(aid),
            leverage=lev,
            coherence_flags=list(coherence.get(aid, [])),
            refinement_priority=compute_refinement_priority(aid, props, lev),
        )

    activity_rows: list[ActivityRow] = []
    matrix_cells: list[dict[str, Any]] = []

    for act in enhanced_activities:
        v = compose_v(act.p.value, act.c.value, act.f.value, act.r.value)
        if v is None:
            continue
        v = round(v, 4)
        row_scores: list[ActivityScoreRow] = []
        for metric in metric_rows:
            mid = metric.id
            g = _g_score(act.activity_id, mid, affects_conf, activity_process, process_metric)
            j = _j_score(act.activity_id, mid, touches)
            dv = _dv_score(act.activity_id, mid, affects_conf, driver_parent)
            b = round(BRIDGE_W[0] * g + BRIDGE_W[1] * j + BRIDGE_W[2] * dv, 4)
            rel = round(b * v, 4)
            if b <= 0 and rel <= 0:
                continue
            row_scores.append(
                ActivityScoreRow(
                    metric_id=mid,
                    g=round(g, 4),
                    j=round(j, 4),
                    dv=round(dv, 4),
                    b=b,
                    relevance=rel,
                    pct_contribution=0.0,
                )
            )
            matrix_cells.append(
                {
                    "activity_id": act.activity_id,
                    "metric_id": mid,
                    "relevance": rel,
                    "b": b,
                    "v": v,
                }
            )

        by_metric: dict[str, float] = {}
        for score in row_scores:
            by_metric[score.metric_id] = by_metric.get(score.metric_id, 0.0) + score.relevance
        row_scores = tuple(
            ActivityScoreRow(
                metric_id=score.metric_id,
                g=score.g,
                j=score.j,
                dv=score.dv,
                b=score.b,
                relevance=score.relevance,
                pct_contribution=(
                    round(score.relevance / by_metric[score.metric_id], 4)
                    if by_metric.get(score.metric_id, 0.0) > 0
                    else 0.0
                ),
            )
            for score in row_scores
        )

        activity_rows.append(
            ActivityRow(
                activity_id=act.activity_id,
                activity_name=act.activity_name,
                process_id=act.process_id,
                p=float(act.p.value or 0.0),
                c=float(act.c.value or 0.0),
                f=float(act.f.value or 0.0),
                r=float(act.r.value or 0.0),
                v=v,
                scores=row_scores,
            )
        )

        props = node_props_by_id.get(act.activity_id, {})
        p2 = phase2.get(act.activity_id)
        if p2:
            phase2[act.activity_id] = Phase2ActivityScores(
                value_proximity=proximity_by_activity.get(act.activity_id),
                leverage=leverage_by_activity.get(act.activity_id),
                coherence_flags=list(coherence.get(act.activity_id, [])),
                refinement_priority=compute_refinement_priority(
                    act.activity_id, props, leverage_by_activity.get(act.activity_id)
                ),
            )

    process_labels = {
        node["id"]: node.get("label") or node["id"]
        for node in graph.get("nodes", [])
        if node.get("type") == "Process"
    }

    process_rollups: list[ProcessRollupRow] = []
    by_metric_total: dict[str, float] = {}
    for cell in matrix_cells:
        by_metric_total[cell["metric_id"]] = by_metric_total.get(cell["metric_id"], 0.0) + cell["relevance"]

    process_ids = {act.process_id for act in activity_rows if act.process_id}
    for pid in sorted(process_ids):
        for mid in sorted(metric_ids):
            total_rel = sum(
                cell["relevance"]
                for cell in matrix_cells
                if cell["metric_id"] == mid
                and next(
                    (a.process_id for a in activity_rows if a.activity_id == cell["activity_id"]),
                    "",
                )
                == pid
            )
            if total_rel > 0:
                denom = by_metric_total.get(mid, 0.0) or 1.0
                process_rollups.append(
                    ProcessRollupRow(
                        process_id=pid,
                        metric_id=mid,
                        relevance_sum=round(total_rel, 4),
                        pct_contribution=round(total_rel / denom, 4),
                    )
                )

    cross_findings = cross_validate_p_vs_proximity(enhanced_activities, proximity_by_activity)
    eval_conf = overall_evaluation_confidence(enhanced_activities)

    value_input = ValueScenarioInput(
        metrics=metric_rows,
        activities=tuple(activity_rows),
        process_rollups=tuple(process_rollups),
        strategic_b_zero=(),
        process_labels=process_labels,
    )

    return EnhancedScoringResult(
        value_input=value_input,
        evaluation_confidence=round(eval_conf, 4) if eval_conf is not None else None,
        phase2_by_activity=phase2,
        cross_validation_findings=cross_findings,
        proximity_by_activity=proximity_by_activity,
    )


def node_confidence(node_props: dict[str, Any]) -> float:
    if node_props.get("generated") is True:
        raw = node_props.get("confidence")
        return float(raw) if raw is not None else 0.5
    raw = node_props.get("confidence")
    return float(raw) if raw is not None else 1.0


def relationship_confidence(rel_props: dict[str, Any]) -> float:
    if rel_props.get("generated") is True or rel_props.get("derived") is True:
        raw = rel_props.get("confidence")
        return float(raw) if raw is not None else 0.5
    raw = rel_props.get("confidence")
    return float(raw) if raw is not None else 1.0
