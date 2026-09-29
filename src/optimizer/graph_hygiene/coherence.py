"""Read-only topological coherence audit (checks 1–7). Never mutates the graph."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import networkx as nx
from langchain_community.graphs.graph_document import GraphDocument

CHECK_NAMES = {
    1: "Alcanzabilidad de valor",
    2: "Ciclos",
    3: "Eventos huérfanos",
    4: "Activities completamente desconectadas",
    5: "Ramas sin reconvergencia",
    6: "Violación de techo de confianza",
    7: "Consistencia de retracción",
}

_CEILING_TYPES = frozenset({"AFFECTS", "CONTRIBUTES_TO", "DRIVES"})


@dataclass(frozen=True)
class CoherenceFinding:
    check: int | str
    name: str
    severity: str
    node_ids: tuple[str, ...]
    description: str
    suggested_edge: tuple[str, str] | None = None


def _props(obj: Any) -> dict:
    return dict(getattr(obj, "properties", None) or {})


def _confidence(props: dict) -> float:
    raw = props.get("confidence")
    if raw is not None:
        return float(raw)
    if props.get("generated") is True or props.get("derived") is True:
        return 0.5
    return 1.0


def _finding(
    check: int | str,
    severity: str,
    node_ids: tuple[str, ...],
    description: str,
    suggested_edge: tuple[str, str] | None = None,
    *,
    name: str | None = None,
) -> CoherenceFinding:
    return CoherenceFinding(
        check=check,
        name=name if name is not None else CHECK_NAMES[check],  # type: ignore[index]
        severity=severity,
        node_ids=node_ids,
        description=description,
        suggested_edge=suggested_edge,
    )


def _precedes_graph(document: GraphDocument) -> nx.DiGraph:
    graph = nx.DiGraph()
    for node in document.nodes:
        if node.type in {"Activity", "Event"}:
            graph.add_node(node.id, node_type=node.type)
    for rel in document.relationships:
        if rel.type.upper() != "PRECEDES":
            continue
        src, tgt = rel.source.id, rel.target.id
        if src in graph and tgt in graph:
            graph.add_edge(src, tgt)
    return graph


def _check1(document: GraphDocument, precedes: nx.DiGraph) -> list[CoherenceFinding]:
    contributes: set[str] = set()
    process_metrics: dict[str, set[str]] = {}
    part_of: dict[str, set[str]] = {}
    produces: dict[str, set[str]] = {}
    realizes: dict[str, set[str]] = {}  # metric -> events
    for rel in document.relationships:
        rtype = rel.type.upper()
        if rtype == "CONTRIBUTES_TO" and rel.source.type == "Process":
            contributes.add(rel.source.id)
            process_metrics.setdefault(rel.source.id, set()).add(rel.target.id)
        elif rtype == "PART_OF" and rel.source.type == "Activity":
            part_of.setdefault(rel.target.id, set()).add(rel.source.id)
        elif rtype == "INVOLVES_EVENT" and _props(rel).get("event_role") == "produce":
            if (
                rel.target.type == "Event"
                and _props(rel.target).get("event_type") == "value_realization"
            ):
                produces.setdefault(rel.source.id, set()).add(rel.target.id)
        elif rtype == "REALIZES" and rel.source.type == "Event":
            realizes.setdefault(rel.target.id, set()).add(rel.source.id)

    findings: list[CoherenceFinding] = []
    for process_id in sorted(contributes):
        activities = part_of.get(process_id, set())
        terminals: set[str] = set()
        for mid in process_metrics.get(process_id, ()):
            terminals.update(realizes.get(mid, ()))
        if not terminals:
            for activity_id in activities:
                terminals.update(produces.get(activity_id, ()))
        if not terminals:
            findings.append(
                _finding(
                    1,
                    "error",
                    (process_id,),
                    "Process with CONTRIBUTES_TO has no value_realization event "
                    "(no REALIZES path and no produce INVOLVES_EVENT)",
                )
            )
            continue
        reachable: set[str] = set()
        for terminal in terminals:
            if terminal not in precedes:
                continue
            reachable |= nx.ancestors(precedes, terminal) | {terminal}
        for activity_id in sorted(activities):
            if activity_id not in reachable:
                findings.append(
                    _finding(
                        1,
                        "error",
                        (activity_id,),
                        "Activity cannot reach its process realization event",
                    )
                )
    return findings


def _check2(precedes: nx.DiGraph) -> list[CoherenceFinding]:
    if nx.is_directed_acyclic_graph(precedes):
        return []
    # ponytail: all simple_cycles; cap enumeration if graphs get huge
    findings = []
    for cycle in nx.simple_cycles(precedes):
        findings.append(
            _finding(2, "error", tuple(cycle), "PRECEDES cycle: " + " → ".join(cycle))
        )
    return findings


def _check3(document: GraphDocument) -> list[CoherenceFinding]:
    incoming: set[str] = set()
    for rel in document.relationships:
        if rel.type.upper() == "INVOLVES_EVENT":
            incoming.add(rel.target.id)
    findings = []
    for node in document.nodes:
        if node.type == "Event" and node.id not in incoming:
            findings.append(
                _finding(3, "error", (node.id,), "Event has no incoming INVOLVES_EVENT")
            )
    return findings


def _check4(precedes: nx.DiGraph) -> list[CoherenceFinding]:
    findings = []
    for node_id, data in precedes.nodes(data=True):
        if data.get("node_type") != "Activity":
            continue
        if precedes.in_degree(node_id) == 0 and precedes.out_degree(node_id) == 0:
            findings.append(
                _finding(4, "revisar", (node_id,), "Activity isolated on PRECEDES")
            )
    return findings


def classify_branch_fork(
    node_id: str,
    precedes: nx.DiGraph,
    node_types: dict[str, str],
) -> str | None:
    """If a non-reconverging fork is acceptable or auto-handled, return a reason code.

    Returns None when the fork should remain a pending finding.
    Reason codes: parallel_milestone | event_and_activity | shared_sinks
    """
    if node_id not in precedes:
        return None
    successors = list(precedes.successors(node_id))
    if len(successors) < 2:
        return None
    befores: list[set[str]] = []
    sink_sets: list[set[str]] = []
    for succ in successors:
        branch = {succ} | nx.descendants(precedes, succ)
        sinks = {n for n in branch if precedes.out_degree(n) == 0}
        sink_sets.append(sinks)
        befores.append(branch - sinks)
    shared_mid = befores[0].copy() if befores else set()
    for other in befores[1:]:
        shared_mid &= other
    if shared_mid:
        return None  # already reconverges — not a finding

    succ_types = [node_types.get(s, "") for s in successors]
    n_event = sum(1 for t in succ_types if t == "Event")
    n_act = sum(1 for t in succ_types if t == "Activity")

    # Activity continues + Event side-emit (milestone / terminal)
    if n_event >= 1 and n_act >= 1:
        for succ, st in zip(successors, succ_types):
            if st != "Event":
                continue
            branch = {succ} | nx.descendants(precedes, succ)
            # thin event arm: only events (or empty descendants)
            if all(node_types.get(n) == "Event" for n in branch):
                return "parallel_milestone"
        return "event_and_activity"

    # Parallel arms that end at the same sinks (same value endpoints)
    if sink_sets:
        common_sinks = sink_sets[0].copy()
        for other in sink_sets[1:]:
            common_sinks &= other
        if common_sinks:
            return "shared_sinks"

    return None


def _check5(precedes: nx.DiGraph) -> list[CoherenceFinding]:
    node_types = {
        n: data.get("node_type", "") for n, data in precedes.nodes(data=True)
    }
    findings = []
    for node_id in precedes.nodes:
        successors = list(precedes.successors(node_id))
        if len(successors) < 2:
            continue
        befores: list[set[str]] = []
        for succ in successors:
            branch = {succ} | nx.descendants(precedes, succ)
            sinks = {n for n in branch if precedes.out_degree(n) == 0}
            befores.append(branch - sinks)
        if not befores:
            continue
        shared = befores[0]
        for other in befores[1:]:
            shared &= other
        if shared:
            continue
        reason = classify_branch_fork(node_id, precedes, node_types)
        if reason is not None:
            continue  # resolvable / acceptable — reported via R6, not Sección 3
        findings.append(
            _finding(
                5,
                "revisar",
                (node_id,),
                "Branches do not reconverge before their terminals",
            )
        )
    return findings


def _check6(document: GraphDocument) -> list[CoherenceFinding]:
    findings = []
    for rel in document.relationships:
        if rel.type.upper() not in _CEILING_TYPES:
            continue
        if _confidence(_props(rel)) > _confidence(_props(rel.target)):
            findings.append(
                _finding(
                    6,
                    "error",
                    (rel.source.id, rel.target.id),
                    f"{rel.type} confidence exceeds target node confidence",
                )
            )
    return findings


def _check7(document: GraphDocument) -> list[CoherenceFinding]:
    node_ids = {node.id for node in document.nodes}
    retired = {
        node.id
        for node in document.nodes
        if _props(node).get("retirado")
    }
    findings = []
    for rel in document.relationships:
        src, tgt = rel.source.id, rel.target.id
        bad = []
        if src not in node_ids or src in retired:
            bad.append(src)
        if tgt not in node_ids or tgt in retired:
            bad.append(tgt)
        if bad:
            findings.append(
                _finding(
                    7,
                    "error",
                    tuple(bad),
                    "Active edge references missing or retirado node",
                )
            )
    return findings


def audit_coherence(document: GraphDocument) -> tuple[CoherenceFinding, ...]:
    from optimizer.graph_hygiene.intent_checks import audit_intent_coherence

    precedes = _precedes_graph(document)
    findings = (
        _check1(document, precedes)
        + _check2(precedes)
        + _check3(document)
        + _check4(precedes)
        + _check5(precedes)
        + _check6(document)
        + _check7(document)
        + list(audit_intent_coherence(document))
    )
    return tuple(findings)


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _check_sort_key(check: int | str) -> tuple[int, int | str]:
    if isinstance(check, int):
        return (0, check)
    return (1, check)


def format_coherence_report(
    findings: tuple[CoherenceFinding, ...],
    document: GraphDocument | None = None,
) -> str:
    if not findings:
        return ""
    labels = {
        node.id: _props(node).get("label") or node.id
        for node in (document.nodes if document is not None else [])
    }

    def display(node_id: str) -> str:
        label = labels.get(node_id)
        if label and label != node_id:
            return f"{node_id} ({label})"
        return node_id

    grouped: dict[int | str, list[CoherenceFinding]] = {}
    for finding in findings:
        grouped.setdefault(finding.check, []).append(finding)

    chunks: list[str] = []
    for check in sorted(grouped, key=_check_sort_key):
        rows = grouped[check]
        show_edge = any(row.suggested_edge for row in rows)
        headers = ["Severidad", "Nodos", "Descripción"]
        if show_edge:
            headers.append("Arista sugerida")
        heading = f"Check {check}" if isinstance(check, int) else str(check)
        lines = [
            f"## {heading} — {rows[0].name}",
            "",
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        for row in rows:
            nodes = ", ".join(display(nid) for nid in row.node_ids)
            cells = [row.severity, nodes, row.description]
            if show_edge:
                if row.suggested_edge:
                    src, tgt = row.suggested_edge
                    cells.append(f"{src} → {tgt}")
                else:
                    cells.append("")
            lines.append("| " + " | ".join(_cell(c) for c in cells) + " |")
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks) + "\n"
