"""Intent-layer coherence checks (protocol C1–C4). Read-only; never mutates."""

from __future__ import annotations

from typing import Any

from langchain_community.graphs.graph_document import GraphDocument

from optimizer.graph_hygiene.coherence import CoherenceFinding, _finding
from optimizer.ontology.schema import INTENT_NODE_TYPE

C1 = "C1"
C2 = "C2"
C3 = "C3"
C4 = "C4"

INTENT_CHECK_NAMES = {
    C1: "Cobertura de intención",
    C2: "Desviación de intención",
    C3: "Nivel en la escalera",
    C4: "Alineación intención–efecto",
}


def _ifind(
    check: str,
    severity: str,
    node_ids: tuple[str, ...],
    description: str,
) -> CoherenceFinding:
    return _finding(
        check,
        severity,
        node_ids,
        description,
        name=INTENT_CHECK_NAMES[check],
    )


def _index(document: GraphDocument) -> dict[str, Any]:
    pursues: dict[str, set[str]] = {}
    part_of: dict[str, str] = {}
    serves: dict[str, set[str]] = {}
    serves_metrics: dict[str, set[str]] = {}
    affects_metrics: dict[str, set[str]] = {}
    drives_via: dict[str, set[str]] = {}
    contributes: dict[str, set[str]] = {}
    driver_to_metric: dict[str, set[str]] = {}

    for rel in document.relationships:
        rtype = rel.type.upper()
        src, tgt = rel.source.id, rel.target.id
        if rtype == "PURSUES":
            pursues.setdefault(src, set()).add(tgt)
        elif rtype == "PART_OF" and rel.source.type == "Activity":
            part_of[src] = tgt
        elif rtype == "SERVES":
            serves.setdefault(src, set()).add(tgt)
            if rel.target.type == "Metric":
                serves_metrics.setdefault(src, set()).add(tgt)
        elif rtype == "AFFECTS" and rel.source.type == "Activity":
            if rel.target.type == "Metric":
                affects_metrics.setdefault(src, set()).add(tgt)
            elif rel.target.type == "MetricDriver":
                drives_via.setdefault(src, set()).add(tgt)
        elif rtype == "DRIVES" and rel.source.type == "MetricDriver":
            driver_to_metric.setdefault(src, set()).add(tgt)
        elif rtype == "CONTRIBUTES_TO" and rel.source.type == "Process":
            contributes.setdefault(src, set()).add(tgt)

    activity_effect_metrics: dict[str, set[str]] = {
        aid: set(ms) for aid, ms in affects_metrics.items()
    }
    for aid, drivers in drives_via.items():
        for did in drivers:
            activity_effect_metrics.setdefault(aid, set()).update(
                driver_to_metric.get(did, ())
            )

    return {
        "pursues": pursues,
        "part_of": part_of,
        "serves": serves,
        "serves_metrics": serves_metrics,
        "activity_effect_metrics": activity_effect_metrics,
        "contributes": contributes,
    }


def activity_intents(activity_id: str, idx: dict[str, Any]) -> set[str]:
    own = set(idx["pursues"].get(activity_id, ()))
    process_id = idx["part_of"].get(activity_id)
    if process_id:
        own |= idx["pursues"].get(process_id, set())
    return own


def ladder_level(activity_id: str, idx: dict[str, Any]) -> str | None:
    intents = activity_intents(activity_id, idx)
    if not intents:
        return None
    effect = idx["activity_effect_metrics"].get(activity_id, set())
    process_id = idx["part_of"].get(activity_id)
    process_metrics = idx["contributes"].get(process_id, set()) if process_id else set()
    intent_metrics: set[str] = set()
    for iid in intents:
        intent_metrics |= idx["serves_metrics"].get(iid, set())
    if effect:
        return "N1"
    if process_metrics:
        return "N2"
    if intent_metrics:
        return "N3"
    return "N4"


def check_c1(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _index(document)
    findings: list[CoherenceFinding] = []
    for node in document.nodes:
        if node.type != "Activity":
            continue
        if not activity_intents(node.id, idx):
            findings.append(
                _ifind(
                    C1,
                    "error",
                    (node.id,),
                    "Activity has no Intent (own PURSUES or inherited via Process)",
                )
            )
    for node in document.nodes:
        if node.type != INTENT_NODE_TYPE:
            continue
        if not idx["serves"].get(node.id):
            findings.append(
                _ifind(
                    C1,
                    "revisar",
                    (node.id,),
                    "Intent has no SERVES beneficiary (unidentified para quién)",
                )
            )
    return findings


def check_c2(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _index(document)
    findings: list[CoherenceFinding] = []
    for node in document.nodes:
        if node.type != "Activity":
            continue
        process_id = idx["part_of"].get(node.id)
        if not process_id:
            continue
        own = idx["pursues"].get(node.id, set())
        inherited = idx["pursues"].get(process_id, set())
        if not own or not inherited:
            continue
        if own != inherited and not own <= inherited:
            findings.append(
                _ifind(
                    C2,
                    "revisar",
                    (node.id, process_id),
                    "Activity own Intent set differs from its Process Intent",
                )
            )
    return findings


def check_c3(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _index(document)
    counts = {"N1": 0, "N2": 0, "N3": 0, "N4": 0}
    placed = 0
    for node in document.nodes:
        if node.type != "Activity":
            continue
        level = ladder_level(node.id, idx)
        if level is None:
            continue
        counts[level] += 1
        placed += 1
    if placed == 0:
        return [
            _ifind(
                C3,
                "info",
                (),
                "No activities on ladder N1–N4 (none have Intent yet)",
            )
        ]
    dist = ", ".join(f"{k}={v}" for k, v in counts.items())
    return [_ifind(C3, "info", (), f"Ladder distribution ({placed} activities): {dist}")]


def check_c4(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _index(document)
    findings: list[CoherenceFinding] = []
    pursued_metrics: set[str] = set()

    for node in document.nodes:
        if node.type != "Activity":
            continue
        aid = node.id
        intents = activity_intents(aid, idx)
        effect = idx["activity_effect_metrics"].get(aid, set())
        intent_metrics: set[str] = set()
        for iid in intents:
            intent_metrics |= idx["serves_metrics"].get(iid, set())
        pursued_metrics |= intent_metrics

        for mid in sorted(intent_metrics - effect):
            findings.append(
                _ifind(
                    C4,
                    "revisar",
                    (aid, mid),
                    "Pursues Metric via Intent.SERVES but no AFFECTS/driver path to it",
                )
            )
        for mid in sorted(effect - intent_metrics):
            findings.append(
                _ifind(
                    C4,
                    "revisar",
                    (aid, mid),
                    "Has effect on Metric but no Intent that SERVES it",
                )
            )

    for node in document.nodes:
        if node.type == "Metric" and node.id not in pursued_metrics:
            findings.append(
                _ifind(
                    C4,
                    "revisar",
                    (node.id,),
                    "Metric that nobody pursues (no Intent.SERVES)",
                )
            )
    return findings


def audit_intent_coherence(document: GraphDocument) -> tuple[CoherenceFinding, ...]:
    idx = _index(document)
    return tuple(
        check_c1(document, idx)
        + check_c2(document, idx)
        + check_c3(document, idx)
        + check_c4(document, idx)
    )
