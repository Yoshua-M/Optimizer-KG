"""Coherence protocol C5–C14, repairs, cycle controller, Salidas report.

Deterministic first pass: no LLM. Abduces Process/Activity Intent (R1) and
SERVES links from CONTRIBUTES_TO / effects / value events (R2). Topology (R6)
auto-applies and is reported. Ontology-layer R3 means-to-end merges require
authorize_ontology. 1.5 (persigue sin AFFECTS) is report-only — no auto-AFFECTS.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

import networkx as nx
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship

from optimizer.graph_hygiene.coherence import (
    CoherenceFinding,
    _precedes_graph,
    _props,
    audit_coherence,
    classify_branch_fork,
)
from optimizer.graph_hygiene.intent_checks import (
    _index,
    activity_intents,
    ladder_level,
)
from optimizer.ontology.schema import (
    ABDUCTION_CONFIDENCE_CEILING,
    ALL_EDGE_TYPES,
    INTENT_NODE_TYPE,
    NODE_TYPES,
)

C5, C6, C7, C8, C9, C10, C11, C12, C13, C14 = (
    "C5",
    "C6",
    "C7",
    "C8",
    "C9",
    "C10",
    "C11",
    "C12",
    "C13",
    "C14",
)

_EXTRA_NAMES = {
    C5: "Alcanzabilidad de propósito",
    C6: "Completitud de flujo",
    C7: "Ajuste de rol (mecánico)",
    C8: "Exposición de conflictos",
    C9: "Candidatos a variante",
    C10: "Candidatos a fusión de intenciones",
    C11: "Perfil funcional",
    C12: "Calibración",
    C13: "Integridad de esquema",
    C14: "Estabilidad y compresión",
}


def _efind(check: str, severity: str, node_ids: tuple[str, ...], description: str) -> CoherenceFinding:
    from optimizer.graph_hygiene.coherence import _finding

    return _finding(check, severity, node_ids, description, name=_EXTRA_NAMES[check])


def _label(node: Node) -> str:
    return str(_props(node).get("label") or node.id)


def _rich_index(document: GraphDocument) -> dict[str, Any]:
    idx = _index(document)
    nodes = {n.id: n for n in document.nodes}
    performs: dict[str, set[str]] = {}  # activity -> teams
    conflicts: list[tuple[str, str, str]] = []  # a, b, kind
    serves_events: dict[str, set[str]] = {}
    precedes = _precedes_graph(document)
    for rel in document.relationships:
        rtype = rel.type.upper()
        if rtype == "PERFORMS" and rel.target.type == "Activity":
            performs.setdefault(rel.target.id, set()).add(rel.source.id)
        elif rtype == "CONFLICTS_WITH":
            kind = str(_props(rel).get("conflict_kind") or "trade_off")
            conflicts.append((rel.source.id, rel.target.id, kind))
        elif rtype == "SERVES" and rel.target.type == "Event":
            serves_events.setdefault(rel.source.id, set()).add(rel.target.id)
    idx.update(
        {
            "nodes": nodes,
            "performs": performs,
            "conflicts": conflicts,
            "serves_events": serves_events,
            "precedes": precedes,
        }
    )
    return idx


def check_c5(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    precedes: nx.DiGraph = idx["precedes"]
    findings = []
    for node in document.nodes:
        if node.type != "Activity":
            continue
        for iid in activity_intents(node.id, idx):
            for eid in idx["serves_events"].get(iid, ()):
                if eid not in precedes or node.id not in precedes:
                    findings.append(
                        _efind(
                            C5,
                            "revisar",
                            (node.id, eid),
                            "Intent SERVES Event but activity/event missing from PRECEDES graph",
                        )
                    )
                    continue
                if node.id == eid:
                    continue
                if not nx.has_path(precedes, node.id, eid):
                    findings.append(
                        _efind(
                            C5,
                            "error",
                            (node.id, eid),
                            "Activity cannot reach Event that its Intent SERVES via PRECEDES",
                        )
                    )
    return findings


def check_c6(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    precedes: nx.DiGraph = idx["precedes"]
    findings = []
    demands = [
        n.id
        for n in document.nodes
        if n.type == "Event" and _props(n).get("event_type") == "demand"
    ]
    terminals = [
        n.id
        for n in document.nodes
        if n.type == "Event" and _props(n).get("event_type") == "value_realization"
    ]
    for did in demands:
        if did not in precedes:
            findings.append(_efind(C6, "error", (did,), "Demand event off PRECEDES graph"))
            continue
        if not any(
            t in precedes and nx.has_path(precedes, did, t) for t in terminals
        ):
            findings.append(
                _efind(C6, "error", (did,), "Demand has no PRECEDES path to a value_realization Event")
            )
    for nid, data in precedes.nodes(data=True):
        if data.get("node_type") != "Activity":
            continue
        if precedes.in_degree(nid) == 0 and precedes.out_degree(nid) == 0:
            findings.append(_efind(C6, "revisar", (nid,), "Hanging activity (isolated on PRECEDES)"))
    return findings


def check_c7(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    precedes: nx.DiGraph = idx["precedes"]
    findings = []
    if not nx.is_directed_acyclic_graph(precedes):
        for cycle in nx.simple_cycles(precedes):
            findings.append(
                _efind(C7, "error", tuple(cycle), "PRECEDES cycle: " + " → ".join(cycle))
            )
    terminals = [
        n.id
        for n in document.nodes
        if n.type == "Event" and _props(n).get("event_type") == "value_realization"
    ]
    for tid in terminals:
        if tid not in precedes:
            continue
        after = nx.descendants(precedes, tid)
        for aid in sorted(a for a in after if precedes.nodes[a].get("node_type") == "Activity"):
            findings.append(
                _efind(
                    C7,
                    "revisar",
                    (aid, tid),
                    "Activity sits after a value_realization terminal on PRECEDES",
                )
            )
    return findings


def check_c8(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    findings = []
    conflict_pairs = {(a, b) if a < b else (b, a): kind for a, b, kind in idx["conflicts"]}
    # activities pursuing both sides of a conflict
    for node in document.nodes:
        if node.type != "Activity":
            continue
        intents = activity_intents(node.id, idx)
        for (ia, ib), kind in conflict_pairs.items():
            if ia in intents and ib in intents:
                findings.append(
                    _efind(
                        C8,
                        "error",
                        (node.id, ia, ib),
                        f"Activity pursues conflicting Intents ({kind})",
                    )
                )
    # pairs of activities with conflicting intents sharing process/team
    act_intents = {
        n.id: activity_intents(n.id, idx)
        for n in document.nodes
        if n.type == "Activity"
    }
    acts = sorted(act_intents)
    for i, a in enumerate(acts):
        for b in acts[i + 1 :]:
            shared_conflict = None
            for (ia, ib), kind in conflict_pairs.items():
                if (ia in act_intents[a] and ib in act_intents[b]) or (
                    ib in act_intents[a] and ia in act_intents[b]
                ):
                    shared_conflict = kind
                    break
            if not shared_conflict:
                continue
            same_process = idx["part_of"].get(a) and idx["part_of"].get(a) == idx["part_of"].get(b)
            same_team = bool(idx["performs"].get(a, set()) & idx["performs"].get(b, set()))
            if same_process or same_team:
                findings.append(
                    _efind(
                        C8,
                        "revisar",
                        (a, b),
                        f"Conflicting intents ({shared_conflict}) with shared "
                        f"{'process' if same_process else 'team'}",
                    )
                )
    return findings


def _neighborhood(activity_id: str, document: GraphDocument) -> set[str]:
    neigh: set[str] = set()
    for rel in document.relationships:
        if rel.source.id == activity_id:
            neigh.add(rel.target.id)
        elif rel.target.id == activity_id:
            neigh.add(rel.source.id)
    return neigh


def check_c9(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    findings = []
    precedes: nx.DiGraph = idx["precedes"]
    by_intent: dict[str, list[str]] = {}
    for node in document.nodes:
        if node.type != "Activity":
            continue
        for iid in activity_intents(node.id, idx):
            by_intent.setdefault(iid, []).append(node.id)
    for iid, aids in by_intent.items():
        if len(aids) < 2:
            continue
        for i, a in enumerate(sorted(aids)):
            for b in sorted(aids)[i + 1 :]:
                if _variant_pair_is_distinct(document, a, b, precedes):
                    continue
                src_a = _props(idx["nodes"][a]).get("source") or _props(idx["nodes"][a]).get(
                    "evidence_pointer"
                )
                src_b = _props(idx["nodes"][b]).get("source") or _props(idx["nodes"][b]).get(
                    "evidence_pointer"
                )
                if src_a and src_b and src_a == src_b:
                    continue
                na, nb = _neighborhood(a, document), _neighborhood(b, document)
                if not na or not nb:
                    continue
                overlap = len(na & nb) / max(1, len(na | nb))
                if overlap >= 0.4:
                    findings.append(
                        _efind(
                            C9,
                            "revisar",
                            (a, b, iid),
                            f"Variant candidate: same Intent, neighborhood overlap={overlap:.2f}",
                        )
                    )
    return findings


_ROLE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"vencid|cartera vencida", re.I), "overdue"),
    (re.compile(r"escalam", re.I), "escalate"),
    (re.compile(r"estado de cuenta bancario", re.I), "bank_stmt"),
    (re.compile(r"estado de cuenta del cliente|env[ií]o del estado de cuenta", re.I), "client_stmt"),
    (re.compile(r"seguimiento (al pago|diario a cartera)", re.I), "follow"),
    (re.compile(r"registro del pago", re.I), "register"),
    (re.compile(r"prepago", re.I), "prepay"),
    (re.compile(r"liberaci[oó]n de fondos", re.I), "funds"),
    (re.compile(r"liberaci[oó]n de cr[eé]dito", re.I), "credit"),
    (re.compile(r"auditor[ií]a?s?\s+intern", re.I), "audit_int"),
    (re.compile(r"auditor[ií]a?s?\s+a\s+proveedores", re.I), "audit_sup"),
    (re.compile(r"aprobaci[oó]n de proveedores", re.I), "approve_sup"),
    (re.compile(r"folio|log[ií]stica", re.I), "logistics_folio"),
    (re.compile(r"conciliaci[oó]n", re.I), "reconcile"),
]


def _activity_role(label: str) -> str | None:
    for pat, role in _ROLE_PATTERNS:
        if pat.search(label):
            return role
    return None


def _variant_pair_is_distinct(
    document: GraphDocument,
    a: str,
    b: str,
    precedes: nx.DiGraph,
) -> bool:
    """True → not a real variant candidate (sequential steps or different roles)."""
    nodes = {n.id: n for n in document.nodes}
    if a in precedes and b in precedes:
        if nx.has_path(precedes, a, b) or nx.has_path(precedes, b, a):
            return True
    la = _label(nodes[a]) if a in nodes else a
    lb = _label(nodes[b]) if b in nodes else b
    ra, rb = _activity_role(la), _activity_role(lb)
    if ra and rb and ra != rb:
        return True
    return False


_CLARITY_RENAMES: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"^Auditor[ií]as?\s+internas?$", re.I),
        "Auditoría interna (SGC)",
        "distinguir de auditoría a proveedores",
    ),
    (
        re.compile(r"^Auditor[ií]as?\s+a\s+proveedores$", re.I),
        "Auditoría a proveedores",
        "singular claro vs auditoría interna",
    ),
    (
        re.compile(r"^Seguimiento al pago$", re.I),
        "Seguimiento diario a cartera (pagos pendientes)",
        "distinguir de contacto/escalamiento por vencida",
    ),
    (
        re.compile(r"^Identificaci[oó]n de facturas vencidas$", re.I),
        "Identificación de cartera vencida",
        "aclarar precursor de contacto por vencida",
    ),
    (
        re.compile(r"^Contacto al cliente por factura vencida$", re.I),
        "Contacto al cliente por cartera vencida",
        "alinear con cartera vencida (no solo una factura)",
    ),
]


def check_c10(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    findings = []
    intents = [n for n in document.nodes if n.type == INTENT_NODE_TYPE]
    pursuers: dict[str, set[str]] = {}
    for node in document.nodes:
        if node.type not in {"Activity", "Process"}:
            continue
        for iid in idx["pursues"].get(node.id, ()):
            pursuers.setdefault(iid, set()).add(node.id)
    for i, a in enumerate(intents):
        for b in intents[i + 1 :]:
            la, lb = _label(a).lower(), _label(b).lower()
            if SequenceMatcher(None, la, lb).ratio() < 0.72:
                continue
            sa, sb = idx["serves"].get(a.id, set()), idx["serves"].get(b.id, set())
            if sa and sb and sa != sb:
                continue
            pa, pb = pursuers.get(a.id, set()), pursuers.get(b.id, set())
            if pa & pb or (pa and pb and len(pa & pb) / len(pa | pb) >= 0.3):
                findings.append(
                    _efind(
                        C10,
                        "revisar",
                        (a.id, b.id),
                        "Intent merge candidate: similar label, overlapping pursuers/SERVES",
                    )
                )
    return findings


def check_c11(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    # one summary finding per process
    findings = []
    process_ids = [n.id for n in document.nodes if n.type == "Process"]
    for pid in sorted(process_ids):
        acts = [aid for aid, p in idx["part_of"].items() if p == pid]
        intent_ids: set[str] = set(idx["pursues"].get(pid, ()))
        for aid in acts:
            intent_ids |= activity_intents(aid, idx)
        client = internal = none = conflict = 0
        for iid in intent_ids:
            targets = idx["serves"].get(iid, set())
            if not targets:
                none += 1
            else:
                types = {idx["nodes"][t].type for t in targets if t in idx["nodes"]}
                if "Metric" in types or "CustomerJourneyStep" in types:
                    client += 1
                elif "Event" in types:
                    internal += 1
                else:
                    none += 1
        for a, b, _ in idx["conflicts"]:
            if a in intent_ids and b in intent_ids:
                conflict += 1
        findings.append(
            _efind(
                C11,
                "info",
                (pid,),
                f"Intents={len(intent_ids)} client={client} internal={internal} "
                f"no_beneficiary={none} conflict_pairs={conflict} activities={len(acts)}",
            )
        )
    return findings


def check_c12(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    findings = []
    for rel in document.relationships:
        if rel.type.upper() not in {"AFFECTS", "DRIVES", "CONTRIBUTES_TO", "PURSUES", "SERVES"}:
            continue
        props = _props(rel)
        conf = props.get("confidence")
        corr = props.get("corroboration")
        weak = False
        if conf is not None and float(conf) <= 0.5:
            weak = True
        if corr is not None and int(corr) <= 1:
            weak = True
        if weak:
            findings.append(
                _efind(
                    C12,
                    "revisar",
                    (rel.source.id, rel.target.id),
                    f"Weak calibration on {rel.type}: confidence={conf} corroboration={corr}",
                )
            )
    return findings


def check_c13(document: GraphDocument, idx: dict[str, Any] | None = None) -> list[CoherenceFinding]:
    findings = []
    for node in document.nodes:
        if node.type not in NODE_TYPES:
            findings.append(
                _efind(C13, "error", (node.id,), f"Unknown node type {node.type!r}")
            )
        if node.type == INTENT_NODE_TYPE and not _props(node).get("label"):
            findings.append(_efind(C13, "error", (node.id,), "Intent missing label"))
    for rel in document.relationships:
        if rel.type.upper() not in ALL_EDGE_TYPES:
            findings.append(
                _efind(
                    C13,
                    "error",
                    (rel.source.id, rel.target.id),
                    f"Unknown edge type {rel.type!r}",
                )
            )
    # s(A,T) sums to ~1 when PERFORMS shares exist
    shares: dict[str, float] = {}
    for rel in document.relationships:
        if rel.type.upper() != "PERFORMS":
            continue
        aid = rel.target.id
        share = _props(rel).get("share")
        if share is None:
            continue
        shares[aid] = shares.get(aid, 0.0) + float(share)
    for aid, total in shares.items():
        if abs(total - 1.0) > 0.05:
            findings.append(
                _efind(C13, "error", (aid,), f"PERFORMS share s(A,T) sums to {total:.3f}, expected 1")
            )
    return findings


def check_c14(
    document: GraphDocument,
    idx: dict[str, Any] | None = None,
    *,
    previous: dict[str, Any] | None = None,
) -> list[CoherenceFinding]:
    idx = idx or _rich_index(document)
    # compression: activities per intent
    pursuer_count: dict[str, int] = {}
    activity_count = 0
    for node in document.nodes:
        if node.type != "Activity":
            continue
        activity_count += 1
        for iid in activity_intents(node.id, idx):
            pursuer_count[iid] = pursuer_count.get(iid, 0) + 1
    intent_n = max(1, len([n for n in document.nodes if n.type == INTENT_NODE_TYPE]))
    compression = activity_count / intent_n if intent_n else 0.0
    msg = f"Intent compression={compression:.2f} activities/intent ({activity_count} acts / {intent_n} intents)"
    if previous:
        prev_c = float(previous.get("compression") or 0)
        delta = compression - prev_c
        msg += f"; Δ vs prior={delta:+.2f}"
        if delta < -0.01:
            return [_efind(C14, "revisar", (), msg + " (compression fell)")]
    return [_efind(C14, "info", (), msg)]


def audit_protocol_checks(
    document: GraphDocument,
    *,
    previous: dict[str, Any] | None = None,
) -> tuple[CoherenceFinding, ...]:
    idx = _rich_index(document)
    return tuple(
        list(audit_intent_coherence(document))
        + check_c5(document, idx)
        + check_c6(document, idx)
        + check_c7(document, idx)
        + check_c8(document, idx)
        + check_c9(document, idx)
        + check_c10(document, idx)
        + check_c11(document, idx)
        + check_c12(document, idx)
        + check_c13(document, idx)
        + check_c14(document, idx, previous=previous)
    )


# --- repairs R1 / R2 ---------------------------------------------------------


@dataclass(frozen=True)
class RepairRecord:
    kind: str
    subject_ids: tuple[str, ...]
    basis: str
    evidence_pointer: str
    detail: str


def _node_map(document: GraphDocument) -> dict[str, Node]:
    return {n.id: n for n in document.nodes}


def _next_intent_id(document: GraphDocument) -> str:
    nums = []
    for n in document.nodes:
        if n.type != INTENT_NODE_TYPE:
            continue
        m = re.fullmatch(r"INT-(\d+)", n.id)
        if m:
            nums.append(int(m.group(1)))
    return f"INT-{max(nums, default=0) + 1:02d}"


def _add_intent(
    document: GraphDocument,
    *,
    intent_id: str,
    label: str,
    evidence_pointer: str,
) -> Node:
    node = Node(
        id=intent_id,
        type=INTENT_NODE_TYPE,
        properties={
            "label": label,
            "generated": True,
            "generation_basis": "abduction",
            "confidence": ABDUCTION_CONFIDENCE_CEILING,
            "informant_distance": 3,
            "corroboration": 1,
            "evidence_pointer": evidence_pointer,
        },
    )
    document.nodes.append(node)
    return node


def _add_rel(
    document: GraphDocument,
    source: Node,
    target: Node,
    rtype: str,
    **props: Any,
) -> None:
    document.relationships.append(
        Relationship(
            source=source,
            target=target,
            type=rtype,
            properties={
                "generated": True,
                "generation_basis": props.get("generation_basis", "abduction"),
                "confidence": props.get("confidence", ABDUCTION_CONFIDENCE_CEILING),
                **{k: v for k, v in props.items() if k not in {"generation_basis", "confidence"}},
            },
        )
    )


def repair_r1(document: GraphDocument) -> list[RepairRecord]:
    """Assign Intent: process first (parsimony), then orphan activities."""
    repairs: list[RepairRecord] = []
    idx = _index(document)
    nodes = _node_map(document)

    for node in list(document.nodes):
        if node.type != "Process":
            continue
        if idx["pursues"].get(node.id):
            continue
        iid = _next_intent_id(document)
        label = f"Cumplir propósito de {_label(node)}"
        evidence = f"R1 abduction from Process {_label(node)} ({node.id})"
        intent = _add_intent(document, intent_id=iid, label=label, evidence_pointer=evidence)
        _add_rel(document, node, intent, "PURSUES", evidence_pointer=evidence)
        repairs.append(
            RepairRecord("R1", (node.id, iid), "abduction", evidence, "Process PURSUES new Intent")
        )
        idx = _index(document)  # refresh

    idx = _index(document)
    nodes = _node_map(document)
    for node in list(document.nodes):
        if node.type != "Activity":
            continue
        if activity_intents(node.id, idx):
            continue
        iid = _next_intent_id(document)
        label = f"Cumplir {_label(node)}"
        evidence = f"R1 abduction from Activity {_label(node)} ({node.id}) — no Process Intent"
        intent = _add_intent(document, intent_id=iid, label=label, evidence_pointer=evidence)
        _add_rel(document, node, intent, "PURSUES", evidence_pointer=evidence)
        repairs.append(
            RepairRecord("R1", (node.id, iid), "abduction", evidence, "Activity PURSUES new Intent")
        )
        idx = _index(document)

    return repairs


def repair_r2(document: GraphDocument) -> list[RepairRecord]:
    """Link Intent.SERVES from process CONTRIBUTES_TO, activity effects, or value Events."""
    repairs: list[RepairRecord] = []
    idx = _rich_index(document)
    nodes = idx["nodes"]

    # reverse: intent -> processes / activities that pursue it
    pursuers: dict[str, set[str]] = {}
    for src, intents in idx["pursues"].items():
        for iid in intents:
            pursuers.setdefault(iid, set()).add(src)

    for node in list(document.nodes):
        if node.type != INTENT_NODE_TYPE:
            continue
        if idx["serves"].get(node.id):
            continue
        candidates: list[tuple[Node, str]] = []
        for pid in pursuers.get(node.id, ()):
            pnode = nodes.get(pid)
            if pnode is None:
                continue
            if pnode.type == "Process":
                for mid in idx["contributes"].get(pid, ()):
                    if mid in nodes:
                        candidates.append((nodes[mid], f"Process {pid} CONTRIBUTES_TO"))
                # value events produced by process activities
                acts = [a for a, p in idx["part_of"].items() if p == pid]
                for rel in document.relationships:
                    if rel.type.upper() != "INVOLVES_EVENT":
                        continue
                    if rel.source.id not in acts:
                        continue
                    if _props(rel.target).get("event_type") == "value_realization":
                        candidates.append(
                            (rel.target, f"value_realization via {rel.source.id}")
                        )
            elif pnode.type == "Activity":
                for mid in idx["activity_effect_metrics"].get(pid, ()):
                    if mid in nodes:
                        candidates.append((nodes[mid], f"Activity {pid} effect"))

        # prefer Metric, then Event
        candidates.sort(key=lambda c: 0 if c[0].type == "Metric" else 1)
        if not candidates:
            continue
        target, why = candidates[0]
        evidence = f"R2 beneficiary from {why}"
        _add_rel(
            document,
            node,
            target,
            "SERVES",
            evidence_pointer=evidence,
            generation_basis="abduction",
        )
        repairs.append(
            RepairRecord(
                "R2",
                (node.id, target.id),
                "abduction",
                evidence,
                f"Intent SERVES {target.type}",
            )
        )
        idx = _rich_index(document)

    return repairs


_ORTHOGONAL_INTENT_RE = re.compile(
    r"regulat|cne|queja|no conformidad|auditor|trazabilidad|documental|cumplimiento",
    re.I,
)


def _intent_of_activity(activity_id: str, idx: dict[str, Any]) -> set[str]:
    return activity_intents(activity_id, idx)


def _is_orthogonal_intent(document: GraphDocument, intent_id: str) -> bool:
    node = next((n for n in document.nodes if n.id == intent_id), None)
    if node is None:
        return False
    return bool(_ORTHOGONAL_INTENT_RE.search(_label(node)))


def _has_edge(document: GraphDocument, source_id: str, target_id: str, rtype: str) -> bool:
    rt = rtype.upper()
    return any(
        r.type.upper() == rt and r.source.id == source_id and r.target.id == target_id
        for r in document.relationships
    )


def _merge_intent(
    document: GraphDocument,
    *,
    dropped_id: str,
    canonical_id: str,
    evidence: str,
) -> RepairRecord:
    """Reassign PURSUES/SERVES/CONFLICTS_WITH from dropped → canonical; remove dropped."""
    nodes = _node_map(document)
    canonical = nodes[canonical_id]
    new_rels: list[Relationship] = []
    for rel in document.relationships:
        rtype = rel.type.upper()
        if rel.target.id == dropped_id and rtype == "PURSUES":
            if not _has_edge(document, rel.source.id, canonical_id, "PURSUES"):
                new_rels.append(
                    Relationship(
                        source=rel.source,
                        target=canonical,
                        type="PURSUES",
                        properties={
                            **dict(rel.properties or {}),
                            "generated": True,
                            "generation_basis": "abduction",
                            "evidence_pointer": evidence,
                        },
                    )
                )
            continue
        if rel.source.id == dropped_id and rtype in {"SERVES", "CONFLICTS_WITH", "PROMOTED_TO"}:
            if not _has_edge(document, canonical_id, rel.target.id, rtype):
                new_rels.append(
                    Relationship(
                        source=canonical,
                        target=rel.target,
                        type=rtype,
                        properties={
                            **dict(rel.properties or {}),
                            "generated": True,
                            "evidence_pointer": evidence,
                        },
                    )
                )
            continue
        if rel.source.id == dropped_id or rel.target.id == dropped_id:
            continue
        new_rels.append(rel)
    document.relationships[:] = new_rels
    document.nodes[:] = [n for n in document.nodes if n.id != dropped_id]
    return RepairRecord(
        "R3",
        (dropped_id, canonical_id),
        "abduction",
        evidence,
        f"means-to-end merge {dropped_id} → {canonical_id}",
    )


def propose_r3_means_to_end(document: GraphDocument) -> list[tuple[str, str, str]]:
    """Return (dropped, canonical, evidence) candidates without mutating."""
    idx = _rich_index(document)
    precedes: nx.DiGraph = idx["precedes"]
    pursuers: dict[str, set[str]] = {}
    for src, intents in idx["pursues"].items():
        for iid in intents:
            pursuers.setdefault(iid, set()).add(src)

    proposals: list[tuple[str, str, str]] = []
    for node in document.nodes:
        if node.type != INTENT_NODE_TYPE:
            continue
        ia = node.id
        if idx["serves"].get(ia):
            continue
        if _is_orthogonal_intent(document, ia):
            continue
        # collect downstream intents reached via PRECEDES from pursuers' activities
        acts: set[str] = set()
        for pid in pursuers.get(ia, ()):
            pnode = idx["nodes"].get(pid)
            if pnode is None:
                continue
            if pnode.type == "Activity":
                acts.add(pid)
            elif pnode.type == "Process":
                acts.update(a for a, p in idx["part_of"].items() if p == pid)
        targets: dict[str, str] = {}
        for act in acts:
            if act not in precedes:
                continue
            for desc in nx.descendants(precedes, act):
                dnode = idx["nodes"].get(desc)
                if dnode is None or dnode.type != "Activity":
                    continue
                for ib in _intent_of_activity(desc, idx):
                    if ib == ia:
                        continue
                    if _is_orthogonal_intent(document, ib):
                        continue
                    # prefer intents that already SERVES a Metric, else any process intent
                    why = f"{act} PRECEDES…→ {desc} pursues {ib}"
                    targets[ib] = why
        if not targets:
            continue
        # pick canonical: SERVES Metric first, then lowest INT-id among process-owned
        def rank(ib: str) -> tuple[int, str]:
            serves = idx["serves"].get(ib, set())
            has_metric = any(
                idx["nodes"].get(t) and idx["nodes"][t].type == "Metric" for t in serves
            )
            return (0 if has_metric else 1, ib)

        canonical = sorted(targets, key=rank)[0]
        proposals.append((ia, canonical, f"R3 means-to-end: {targets[canonical]}"))
    return proposals


def repair_r3_means_to_end(
    document: GraphDocument,
    *,
    authorize_ontology: bool,
) -> list[RepairRecord]:
    """Merge feeder intents into downstream purpose. No-op unless authorize_ontology."""
    if not authorize_ontology:
        return []
    repairs: list[RepairRecord] = []
    while True:
        proposals = [(a, b, e) for a, b, e in propose_r3_means_to_end(document) if a != b]
        if not proposals:
            break
        idx = _index(document)

        def sort_key(p: tuple[str, str, str]) -> tuple[int, str]:
            return (0 if idx["serves"].get(p[1]) else 1, p[0])

        proposals.sort(key=sort_key)
        dropped, canonical, evidence = proposals[0]
        if not any(n.id == dropped for n in document.nodes):
            break
        if not any(n.id == canonical for n in document.nodes):
            break
        repairs.append(
            _merge_intent(
                document,
                dropped_id=dropped,
                canonical_id=canonical,
                evidence=evidence,
            )
        )
    return repairs


def repair_topology(document: GraphDocument) -> list[RepairRecord]:
    """Auto wiring: REALIZES terminals + PRECEDES reachability + hanging links. Always OK."""
    repairs: list[RepairRecord] = []
    nodes = _node_map(document)

    contributes: dict[str, set[str]] = {}
    part_of: dict[str, set[str]] = {}
    produces: dict[str, set[str]] = {}
    realizes: dict[str, set[str]] = {}  # metric -> events
    for rel in document.relationships:
        rtype = rel.type.upper()
        if rtype == "CONTRIBUTES_TO" and rel.source.type == "Process":
            contributes.setdefault(rel.source.id, set()).add(rel.target.id)
        elif rtype == "PART_OF" and rel.source.type == "Activity":
            part_of.setdefault(rel.target.id, set()).add(rel.source.id)
        elif rtype == "INVOLVES_EVENT" and _props(rel).get("event_role") == "produce":
            if rel.target.type == "Event":
                produces.setdefault(rel.source.id, set()).add(rel.target.id)
        elif rtype == "REALIZES" and rel.source.type == "Event":
            realizes.setdefault(rel.target.id, set()).add(rel.source.id)

    precedes = _precedes_graph(document)

    def add_precedes(src_id: str, tgt_id: str, evidence: str) -> None:
        nonlocal precedes
        if src_id not in nodes or tgt_id not in nodes:
            return
        if _has_edge(document, src_id, tgt_id, "PRECEDES"):
            return
        # avoid cycles
        if src_id in precedes and tgt_id in precedes and nx.has_path(precedes, tgt_id, src_id):
            return
        _add_rel(
            document,
            nodes[src_id],
            nodes[tgt_id],
            "PRECEDES",
            evidence_pointer=evidence,
            generation_basis="logical",
        )
        repairs.append(
            RepairRecord(
                "R6",
                (src_id, tgt_id),
                "logical",
                evidence,
                f"PRECEDES {src_id} → {tgt_id}",
            )
        )
        precedes = _precedes_graph(document)

    for process_id, metrics in sorted(contributes.items()):
        activities = part_of.get(process_id, set())
        for mid in sorted(metrics):
            if mid not in nodes:
                continue
            terminals = set(realizes.get(mid, ()))
            if not terminals:
                # Prefer Events produced by this process's activities; only then
                # fall back to reachable Events (nearest / value_realization).
                candidates: list[tuple[int, int, int, str]] = []

                def _rank_event(ev_id: str, *, produced: bool, dist: int) -> tuple[int, int, int, str]:
                    et = str(_props(nodes[ev_id]).get("event_type") or "")
                    other = any(
                        ev_id in evs and m != mid for m, evs in realizes.items()
                    )
                    type_rank = (
                        0 if et == "value_realization" else 1 if et == "milestone" else 2
                    )
                    return (
                        0 if produced else 1,
                        9 if other else type_rank,
                        dist,
                        ev_id,
                    )

                produced_cands: list[tuple[int, int, int, str]] = []
                reach_cands: list[tuple[int, int, int, str]] = []
                for act in activities:
                    for ev in produces.get(act, ()):
                        if ev in nodes:
                            produced_cands.append(
                                _rank_event(ev, produced=True, dist=0)
                            )
                # Events produced by *other* CONTRIBUTES_TO processes — don't steal their terminals
                foreign_produced: set[str] = set()
                for other_pid, mets in contributes.items():
                    if other_pid == process_id:
                        continue
                    for act in part_of.get(other_pid, ()):
                        foreign_produced |= produces.get(act, set())
                for act in activities:
                    if act not in precedes:
                        continue
                    for desc in nx.descendants(precedes, act):
                        dnode = nodes.get(desc)
                        if dnode is None or dnode.type != "Event":
                            continue
                        if desc in foreign_produced:
                            continue
                        try:
                            dist = nx.shortest_path_length(precedes, act, desc)
                        except nx.NetworkXNoPath:
                            dist = 99
                        reach_cands.append(
                            _rank_event(desc, produced=False, dist=dist)
                        )

                def _is_vr(c: tuple[int, int, int, str]) -> bool:
                    return c[1] == 0  # type_rank 0 == value_realization (and not other)

                produced_vr = [c for c in produced_cands if _is_vr(c)]
                reach_vr = [c for c in reach_cands if _is_vr(c)]
                # Local VR → reachable VR (not foreign) → local produce → other reachable
                pool = (
                    produced_vr
                    or reach_vr
                    or produced_cands
                    or [c for c in reach_cands if c[1] != 9]
                    or reach_cands
                )
                if not pool:
                    continue
                pool.sort()
                ev_id = pool[0][-1]
                if not _has_edge(document, ev_id, mid, "REALIZES"):
                    evidence = (
                        f"R6 topology: {process_id} CONTRIBUTES_TO {mid}; "
                        f"wire {ev_id} REALIZES {mid}"
                    )
                    _add_rel(
                        document,
                        nodes[ev_id],
                        nodes[mid],
                        "REALIZES",
                        evidence_pointer=evidence,
                        generation_basis="logical",
                    )
                    repairs.append(
                        RepairRecord(
                            "R6",
                            (ev_id, mid),
                            "logical",
                            evidence,
                            f"REALIZES {ev_id} → {mid}",
                        )
                    )
                    realizes.setdefault(mid, set()).add(ev_id)
                terminals = set(realizes.get(mid, ()))

            if not terminals:
                continue
            precedes = _precedes_graph(document)
            reachable: set[str] = set()
            for terminal in terminals:
                if terminal not in precedes:
                    continue
                reachable |= nx.ancestors(precedes, terminal) | {terminal}
            for act in sorted(activities):
                if act in reachable:
                    continue
                terminal = sorted(terminals)[0]
                add_precedes(
                    act,
                    terminal,
                    f"R6 reachability: {act} → {terminal} for {process_id}/{mid}",
                )
                precedes = _precedes_graph(document)
                reachable |= nx.ancestors(precedes, terminal) | {terminal}

    # hanging activities: same-process peer → hanging
    precedes = _precedes_graph(document)
    part_of_act = {
        r.source.id: r.target.id
        for r in document.relationships
        if r.type.upper() == "PART_OF" and r.source.type == "Activity"
    }
    for node in list(document.nodes):
        if node.type != "Activity" or node.id not in precedes:
            continue
        if precedes.in_degree(node.id) or precedes.out_degree(node.id):
            continue
        pid = part_of_act.get(node.id)
        if not pid:
            continue
        peers = [
            a
            for a, p in part_of_act.items()
            if p == pid
            and a != node.id
            and a in precedes
            and (precedes.in_degree(a) or precedes.out_degree(a))
        ]
        if not peers:
            peers = [a for a, p in part_of_act.items() if p == pid and a != node.id]
        if not peers:
            continue
        peer = sorted(peers)[0]
        add_precedes(peer, node.id, f"R6 hanging: {peer} → {node.id} within {pid}")

    return repairs


_BRANCH_REASON_ES = {
    "parallel_milestone": "hito Event en paralelo (continuación + emisión)",
    "event_and_activity": "fork Event + Activity (terminal/excepción vs continuación)",
    "shared_sinks": "brazos paralelos con mismos sinks finales",
}


def repair_branch_forks(document: GraphDocument) -> list[RepairRecord]:
    """Record acceptable non-reconverging forks (R6). Check 5 only flags the rest."""
    repairs: list[RepairRecord] = []
    precedes = _precedes_graph(document)
    nodes = _node_map(document)
    node_types = {n.id: n.type for n in document.nodes}
    for node_id in list(precedes.nodes):
        node = nodes.get(node_id)
        if node is not None and _props(node).get("branch_resolution"):
            continue
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
        shared = befores[0].copy()
        for other in befores[1:]:
            shared &= other
        if shared:
            continue
        reason = classify_branch_fork(node_id, precedes, node_types)
        if reason is None:
            continue
        if node is not None:
            props = dict(node.properties or {})
            props["branch_resolution"] = reason
            node.properties = props
        succs_txt = ", ".join(successors)
        evidence = f"R6 branch accepted ({reason}): {node_id} → [{succs_txt}]"
        repairs.append(
            RepairRecord(
                "R6_BRANCH",
                (node_id, *successors[:4]),
                "logical",
                evidence,
                _BRANCH_REASON_ES.get(reason, reason),
            )
        )
    return repairs


def repair_label_clarity(document: GraphDocument) -> list[RepairRecord]:
    """Rename activities that confuse sibling steps; record distinct-pair resolutions."""
    repairs: list[RepairRecord] = []
    precedes = _precedes_graph(document)
    nodes = _node_map(document)

    for node in list(document.nodes):
        if node.type != "Activity":
            continue
        label = _label(node)
        for pat, new_label, why in _CLARITY_RENAMES:
            if not pat.fullmatch(label.strip()):
                continue
            if label == new_label:
                break
            props = dict(node.properties or {})
            props["label"] = new_label
            props["label_previous"] = label
            props["label_clarity_reason"] = why
            node.properties = props
            repairs.append(
                RepairRecord(
                    "R5_RENAME",
                    (node.id,),
                    "logical",
                    f"R5 clarity rename: {why}",
                    f"{label} → {new_label}",
                )
            )
            break

    idx = _rich_index(document)
    by_intent: dict[str, list[str]] = {}
    for n in document.nodes:
        if n.type != "Activity":
            continue
        for iid in activity_intents(n.id, idx):
            by_intent.setdefault(iid, []).append(n.id)

    seen: set[tuple[str, str]] = set()
    for _iid, aids in by_intent.items():
        for i, a in enumerate(sorted(aids)):
            for b in sorted(aids)[i + 1 :]:
                if (a, b) in seen:
                    continue
                cleared = set(_props(nodes[a]).get("variant_cleared_with") or [])
                if b in cleared:
                    continue
                if not _variant_pair_is_distinct(document, a, b, precedes):
                    continue
                na, nb = _neighborhood(a, document), _neighborhood(b, document)
                if not na or not nb:
                    continue
                overlap = len(na & nb) / max(1, len(na | nb))
                if overlap < 0.4:
                    continue
                seen.add((a, b))
                ra = _activity_role(_label(nodes[a]))
                rb = _activity_role(_label(nodes[b]))
                if a in precedes and b in precedes and (
                    nx.has_path(precedes, a, b) or nx.has_path(precedes, b, a)
                ):
                    why = "hay PRECEDES entre ellas — pasos del flujo, no variantes"
                elif ra and rb and ra != rb:
                    why = f"roles distintos ({ra} vs {rb})"
                else:
                    why = "pasos secuenciales o roles distintos — no variante"
                for nid in (a, b):
                    n = nodes[nid]
                    props = dict(n.properties or {})
                    peer = b if nid == a else a
                    cleared = set(props.get("variant_cleared_with") or [])
                    cleared.add(peer)
                    props["variant_cleared_with"] = sorted(cleared)
                    n.properties = props
                repairs.append(
                    RepairRecord(
                        "R5_DISTINCT",
                        (a, b, _iid),
                        "logical",
                        f"R5 distinct: {why}",
                        why,
                    )
                )
    return repairs


# --- triage + cycle ----------------------------------------------------------


@dataclass
class TriageItem:
    finding: CoherenceFinding
    classification: str  # defecto | hallazgo | residuo
    note: str


@dataclass
class CoherenceDegree:
    ladder: dict[str, int]
    evidence_intents: int
    abduced_intents: int
    compression: float
    activity_count: int
    intent_count: int


@dataclass
class ProtocolResult:
    iterations: int
    converged: bool
    non_convergent: bool
    repairs: list[RepairRecord] = field(default_factory=list)
    fusions: list[dict[str, Any]] = field(default_factory=list)
    metrics_added: list[dict[str, Any]] = field(default_factory=list)
    triage: list[TriageItem] = field(default_factory=list)
    validation_agenda: list[str] = field(default_factory=list)
    degree: CoherenceDegree | None = None
    degree_before: CoherenceDegree | None = None
    findings: tuple[CoherenceFinding, ...] = ()
    document: GraphDocument | None = None


def _defect_count(findings: tuple[CoherenceFinding, ...]) -> int:
    return sum(1 for f in findings if f.severity == "error" and f.check in {"C1", "C5", "C7", "C8", "C13", 1, 2, 6, 7})


def triage_findings(findings: tuple[CoherenceFinding, ...]) -> list[TriageItem]:
    items: list[TriageItem] = []
    for f in findings:
        if f.severity == "info":
            continue
        if f.check == "C1" and "no Intent" in f.description:
            items.append(TriageItem(f, "defecto", "Missing Intent — model gap → R1"))
        elif f.check == "C1" and "no SERVES" in f.description:
            items.append(TriageItem(f, "hallazgo", "Intención sin beneficiario identificado"))
        elif f.check == "C4" and "nobody pursues" in f.description:
            items.append(TriageItem(f, "hallazgo", "Valor que nadie persigue"))
        elif f.check == "C4" and "no AFFECTS" in f.description:
            items.append(TriageItem(f, "hallazgo", "Esfuerzo sin efecto (o hueco de datos)"))
        elif f.check == "C4" and "no Intent that SERVES" in f.description:
            items.append(TriageItem(f, "hallazgo", "Efecto sin intención declarada"))
        elif f.check == "C2":
            items.append(TriageItem(f, "hallazgo", "Desviación de intención vs proceso"))
        elif f.check == "C8":
            items.append(TriageItem(f, "hallazgo", "Conflicto de intención"))
        elif f.check in {"C9", "C10"}:
            items.append(TriageItem(f, "residuo", "Needs validation / merge judgment"))
        elif f.check in {1, "C5", "C6"} and f.severity == "error":
            items.append(TriageItem(f, "hallazgo", "Hueco estructural de flujo / valor"))
        elif f.check == "C12":
            continue  # expected noise on fresh abductions; not an agenda item
        elif f.check in {4, 5, "C6"} and f.severity == "revisar":
            items.append(TriageItem(f, "hallazgo", "Hueco / rama estructural"))
        elif f.severity == "error":
            items.append(TriageItem(f, "defecto", "Structural / schema defect"))
        else:
            items.append(TriageItem(f, "residuo", "Undecidable from graph alone"))
    return items


def _node_display(document: GraphDocument | None, node_id: str) -> str:
    """Protocol v0.2: always `Nombre (ID)`."""
    if document is None:
        return f"— ({node_id})"
    for node in document.nodes:
        if node.id != node_id:
            continue
        label = str(_props(node).get("label") or node_id)
        return f"{label} ({node_id})"
    return f"— ({node_id})"


def _process_of(document: GraphDocument | None, activity_id: str) -> str:
    if document is None:
        return "— (sin proceso)"
    for rel in document.relationships:
        if rel.type.upper() == "PART_OF" and rel.source.id == activity_id:
            return _node_display(document, rel.target.id)
    return "— (sin proceso)"


def _serves_of(document: GraphDocument | None, intent_id: str) -> str:
    if document is None:
        return "—"
    targets = [
        _node_display(document, rel.target.id)
        for rel in document.relationships
        if rel.type.upper() == "SERVES" and rel.source.id == intent_id
    ]
    return "; ".join(targets) if targets else "— (sin beneficiario)"


def _pursuers_of(document: GraphDocument | None, intent_id: str) -> list[str]:
    if document is None:
        return []
    return [
        _node_display(document, rel.source.id)
        for rel in document.relationships
        if rel.type.upper() == "PURSUES" and rel.target.id == intent_id
    ]


def _format_finding_nodes(document: GraphDocument | None, node_ids: tuple[str, ...]) -> str:
    parts = []
    for nid in node_ids:
        text = _node_display(document, nid)
        if document is not None and any(
            n.id == nid and n.type == INTENT_NODE_TYPE for n in document.nodes
        ):
            who = _pursuers_of(document, nid)
            if who:
                text += f" ← {'; '.join(who)}"
        parts.append(text)
    return ", ".join(parts)


def _degree_line(d: CoherenceDegree | None) -> str:
    if d is None:
        return "sin datos"
    return (
        f"N1={d.ladder['N1']} N2={d.ladder['N2']} N3={d.ladder['N3']} N4={d.ladder['N4']}; "
        f"evidencia={d.evidence_intents} abducción={d.abduced_intents}; "
        f"compresión={d.compression:.2f} ({d.activity_count}/{d.intent_count})"
    )


@dataclass
class _Situation:
    code: str
    title: str
    one_liner: str
    why: str
    explanation: str
    columns: tuple[str, ...]
    rows: list[tuple[str, ...]] = field(default_factory=list)

    @property
    def n_cases(self) -> int:
        return len(self.rows)


def _situation_block(s: _Situation) -> list[str]:
    lines = [
        f"#### {s.code} {s.title}",
        "",
        f"**Situación.** {s.one_liner}",
        "",
        f"**Por qué importa.** {s.why}",
        "",
        f"**Explicación.** {s.explanation}",
        "",
        "**Casos.**",
        "",
        "| " + " | ".join(s.columns) + " |",
        "| " + " | ".join("---" for _ in s.columns) + " |",
    ]
    for row in s.rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return lines


def _build_situations(result: ProtocolResult) -> tuple[list[_Situation], list[_Situation], list[_Situation]]:
    doc = result.document
    if doc is None:
        from langchain_core.documents import Document

        doc = GraphDocument(nodes=[], relationships=[], source=Document(page_content=""))
    idx = _index(doc)
    findings = result.findings

    # --- 1.1 repaired activities without intent ---
    s11 = _Situation(
        "1.1",
        "Actividades sin intención (reparadas)",
        "Actividades que no tenían intención propia ni heredada y recibieron una en esta corrida.",
        "Sin intención no hay *para qué* legible; es defecto del modelo (I1), no de la organización.",
        "Se detectó por C1. R1 asignó intención al proceso (parsimonia) o a la actividad huérfana. "
        "No significa que el propósito sea el real — es abducción hasta validar con evidencia.",
        (
            "Actividad",
            "Proceso",
            "Intención asignada",
            "Origen",
            "Base",
            "Evidencia",
        ),
    )
    process_intent: dict[str, tuple[str, str, str]] = {}  # process_id -> (intent_id, basis, evidence)
    # resolve intent ids that were later merged away
    fusion_to: dict[str, str] = {}
    for fus in result.fusions:
        fusion_to[fus["dropped"]] = fus["canonical"]

    def _resolve_intent(iid: str) -> str:
        seen: set[str] = set()
        cur = iid
        while cur in fusion_to and cur not in seen:
            seen.add(cur)
            cur = fusion_to[cur]
        return cur

    for r in result.repairs:
        if r.kind != "R1" or len(r.subject_ids) < 2:
            continue
        owner, intent_id = r.subject_ids[0], _resolve_intent(r.subject_ids[1])
        if doc is None:
            continue
        owner_node = next((n for n in doc.nodes if n.id == owner), None)
        if owner_node is None:
            continue
        if owner_node.type == "Process":
            process_intent[owner] = (intent_id, r.basis, r.evidence_pointer)
            for aid, pid in idx["part_of"].items():
                if pid != owner:
                    continue
                s11.rows.append(
                    (
                        _node_display(doc, aid),
                        _node_display(doc, owner),
                        _node_display(doc, intent_id),
                        "heredada",
                        r.basis,
                        r.evidence_pointer,
                    )
                )
        elif owner_node.type == "Activity":
            s11.rows.append(
                (
                    _node_display(doc, owner),
                    _process_of(doc, owner),
                    _node_display(doc, intent_id),
                    "nueva",
                    r.basis,
                    r.evidence_pointer,
                )
            )

    # --- 1.2 deviation ---
    s12 = _Situation(
        "1.2",
        "Intención desviada del proceso",
        "La actividad declara intención propia distinta de la de su proceso.",
        "Puede ser especialización legítima o desalineación; hay que ver a quién sirve cada una.",
        "Detectado por C2 (conjuntos PURSUES distintos). No implica error automático.",
        (
            "Actividad",
            "Proceso",
            "Intención del proceso",
            "Intención de la actividad",
            "A quién sirve cada una",
        ),
    )
    for f in findings:
        if f.check != "C2" or len(f.node_ids) < 2:
            continue
        aid, pid = f.node_ids[0], f.node_ids[1]
        p_intents = idx["pursues"].get(pid, set())
        a_intents = idx["pursues"].get(aid, set())
        p_txt = "; ".join(_node_display(doc, i) for i in sorted(p_intents)) or "—"
        a_txt = "; ".join(_node_display(doc, i) for i in sorted(a_intents)) or "—"
        serves = []
        for iid in sorted(p_intents | a_intents):
            serves.append(f"{_node_display(doc, iid)} → {_serves_of(doc, iid)}")
        s12.rows.append(
            (
                _node_display(doc, aid),
                _node_display(doc, pid),
                p_txt,
                a_txt,
                "; ".join(serves) or "—",
            )
        )

    # --- 1.3 / 1.4 conflicts ---
    s13 = _Situation(
        "1.3",
        "Intenciones en conflicto",
        "Dos propósitos tiran en direcciones opuestas (`CONFLICTS_WITH`).",
        "Es incoherencia organizacional a hacer visible y arbitrar, no a 'arreglar' en silencio.",
        "Detectado por C8 sobre aristas CONFLICTS_WITH. Requiere juicio (trade-off vs oposición).",
        (
            "Intención A",
            "Intención B",
            "Tipo",
            "Actividades de cada lado (proceso, equipo)",
            "Beneficiario compartido",
        ),
    )
    s14 = _Situation(
        "1.4",
        "Tensión interna",
        "Una misma actividad persigue dos intenciones en conflicto.",
        "La unidad de trabajo está tironeada; el trade-off no está resuelto en el diseño del trabajo.",
        "C8 sobre una actividad con ambos PURSUES. No se repara automáticamente.",
        ("Actividad", "Proceso", "Equipo", "Las dos intenciones en conflicto"),
    )
    for f in findings:
        if f.check != "C8":
            continue
        if "pursues conflicting" in f.description.lower() and len(f.node_ids) >= 3:
            aid, ia, ib = f.node_ids[0], f.node_ids[1], f.node_ids[2]
            teams = "—"
            if doc is not None:
                tnames = [
                    _node_display(doc, rel.source.id)
                    for rel in doc.relationships
                    if rel.type.upper() == "PERFORMS" and rel.target.id == aid
                ]
                teams = "; ".join(tnames) if tnames else "—"
            s14.rows.append(
                (
                    _node_display(doc, aid),
                    _process_of(doc, aid),
                    teams,
                    f"{_node_display(doc, ia)} · {_node_display(doc, ib)}",
                )
            )
        elif len(f.node_ids) >= 2 and "shared" in f.description.lower():
            # activity pair with conflicting intents — fold into 1.3 lightly
            pass

    # --- 1.5 pursues without effect ---
    s15 = _Situation(
        "1.5",
        "Persigue sin llegar",
        "La intención apunta a una métrica, pero no hay ruta de efecto (`AFFECTS`/driver) hasta ella.",
        "O es hueco de datos (falta arista) o esfuerzo que no entrega — C4 no decide cuál. "
        "Por ahora solo se reporta; no se inventan `AFFECTS` automáticamente.",
        "Detectado por C4: Intent.SERVES → M sin efecto de la actividad a M. N3 en la escalera. "
        "El peso en relevancia se calibrará más adelante.",
        ("Actividad", "Proceso", "Intención", "Métrica a la que sirve", "Qué ruta falta"),
    )
    for f in findings:
        if f.check != "C4" or "no AFFECTS" not in f.description or len(f.node_ids) < 2:
            continue
        aid, mid = f.node_ids[0], f.node_ids[1]
        intents = activity_intents(aid, idx)
        intent_txt = "—"
        for iid in sorted(intents):
            if mid in idx.get("serves_metrics", {}).get(iid, set()):
                intent_txt = _node_display(doc, iid)
                break
        if intent_txt == "—" and intents:
            intent_txt = _node_display(doc, sorted(intents)[0])
        s15.rows.append(
            (
                _node_display(doc, aid),
                _process_of(doc, aid),
                intent_txt,
                _node_display(doc, mid),
                "AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica",
            )
        )

    # --- 1.6 value nobody pursues ---
    s16 = _Situation(
        "1.6",
        "Valor que nadie persigue",
        "Hay una métrica de cliente a la que ninguna intención `SERVES`.",
        "La organización puede estar moviendo el indicador por efecto colateral sin propósito declarado.",
        "C4: Metric sin Intent.SERVES. Las actividades listadas la mueven por AFFECTS/driver.",
        ("Métrica", "Actividades que la mueven por efecto, con su proceso"),
    )
    for f in findings:
        if f.check != "C4" or "nobody pursues" not in f.description:
            continue
        mid = f.node_ids[0]
        movers = []
        for aid, mets in idx.get("activity_effect_metrics", {}).items():
            if mid in mets:
                movers.append(f"{_node_display(doc, aid)} / {_process_of(doc, aid)}")
        s16.rows.append(
            (
                _node_display(doc, mid),
                "; ".join(movers) if movers else "— (nadie la mueve por efecto)",
            )
        )

    # --- 1.7 intent without beneficiary ---
    s17 = _Situation(
        "1.7",
        "Intención sin beneficiario",
        "Existe el *para qué*, pero no el *para quién* (`SERVES` ausente).",
        "Señal de coherencia (ontología): propósito cuyo destinatario no está identificado.",
        "C1 sobre Intent sin SERVES. R2 solo enlaza cuando hay CONTRIBUTES_TO o efecto claro; "
        "si no, queda como hallazgo — no se inventa un beneficiario. "
        "Candidatos medio-a-fin (R3) se listan en la columna de propuesta.",
        ("Intención", "Actividades y procesos que la persiguen", "¿Propuesta merge medio-a-fin?"),
    )
    r3_map = {a: (b, e) for a, b, e in propose_r3_means_to_end(doc)}
    for f in findings:
        if f.check != "C1" or "no SERVES" not in f.description:
            continue
        iid = f.node_ids[0]
        who = _pursuers_of(doc, iid)
        if iid in r3_map:
            can, _ev = r3_map[iid]
            proposal = f"fusionar → {_node_display(doc, can)}"
        else:
            proposal = "— (conservar / SERVES interno pendiente)"
        s17.rows.append(
            (
                _node_display(doc, iid),
                "; ".join(who) if who else "— (nadie la persigue)",
                proposal,
            )
        )

    # --- 1.8 fusions ---
    s18 = _Situation(
        "1.8",
        "Intenciones fusionadas (eliminadas)",
        "Intenciones equivalentes o medio-a-fin colapsadas en una canónica (única eliminación permitida).",
        "Compresión de intenciones: menos nodos, mismo propósito compartido.",
        "R3 means-to-end / equivalencia — requiere autorización ontológica de la corrida.",
        (
            "Intención eliminada",
            "Intención canónica",
            "Actividades reasignadas con su proceso",
            "Evidencia de equivalencia o medio-a-fin",
        ),
    )
    for fus in result.fusions:
        dropped = fus["dropped"]
        canonical = fus["canonical"]
        # pursuers now on canonical that came from merge — list from repair evidence
        who = _pursuers_of(doc, canonical)
        s18.rows.append(
            (
                f"— ({dropped})",  # node removed
                _node_display(doc, canonical),
                "; ".join(who) if who else "—",
                fus.get("evidence", "—"),
            )
        )

    # --- 1.9 functional dispersion ---
    s19 = _Situation(
        "1.9",
        "Dispersión funcional",
        "Perfil de intenciones por proceso/equipo: cliente vs interna vs sin beneficiario.",
        "Define la función de cada parte de la organización y dónde hay conflicto o vacío.",
        "Agregado por C11. Es diagnóstico, no defecto por sí solo.",
        (
            "Equipo o Proceso",
            "Intenciones que persigue",
            "Proporción al cliente / interna / sin beneficiario / en conflicto",
        ),
    )
    for f in findings:
        if f.check != "C11" or not f.node_ids:
            continue
        # description already has counts
        s19.rows.append(
            (
                _node_display(doc, f.node_ids[0]),
                "— (ver descripción agregada)",
                f.description,
            )
        )

    section1 = [s11, s12, s13, s14, s15, s16, s17, s18, s19]

    # --- Section 2: graph changes (mostly empty this run) ---
    s21 = _Situation(
        "2.1",
        "Actividades consolidadas",
        "Variantes unidas bajo una actividad canónica (`VARIANT_OF`).",
        "Restablece I3 (variantes fuera de subgrafos) y evita doble conteo de esfuerzo.",
        "R5 diferido — `VARIANT_OF` aún no está en la ontología publicada. C9 solo lista candidatos.",
        (
            "Actividad canónica",
            "Variantes (nombre, fuente, informante)",
            "En qué difieren",
            "Proceso",
            "Equipos",
            "PERFORMS disputado y efecto en s(A,T)",
        ),
    )
    s22 = _Situation(
        "2.2",
        "Actividades generadas",
        "Actividades nuevas insertadas para cerrar flujo.",
        "Restablece completitud de flujo (I3 / escalera) cuando faltaba un paso.",
        "R6 diferido — no se generan actividades en esta corrida (solo Intent).",
        (
            "Actividad",
            "Proceso",
            "Entre qué actividades se insertó",
            "Qué flujo cerró (hacia qué evento)",
            "Base",
        ),
    )
    s23 = _Situation(
        "2.3",
        "Aristas de efecto añadidas",
        "Nuevos `AFFECTS`/drivers para subir en la escalera.",
        "Mueve actividades de N3/N4 hacia N1 cuando la evidencia lo permite.",
        "R6 diferido — no se inventan efectos sin evidencia de llenado.",
        ("Actividad", "Proceso", "Métrica", "Nivel antes → después", "Evidencia"),
    )
    s24 = _Situation(
        "2.4",
        "Orden / alcanzabilidad corregida",
        "Cambios en `PRECEDES` / `REALIZES` / `INVOLVES_EVENT` para terminales de valor.",
        "Corrige alcanzabilidad mecánica (check 1 / C5–C7) sin cambiar el vocabulario ontológico.",
        "R6 topología — aplicada automáticamente y reportada.",
        (
            "Actividades u eventos involucrados",
            "Proceso",
            "Qué cambió",
            "Evento terminal",
            "Métrica",
        ),
    )
    s25 = _Situation(
        "2.5",
        "Métricas añadidas",
        "Métricas nuevas cuando ninguna del inventario encajaba.",
        "Amplía el ancla de valor del cliente; debe reportarse y calibrarse como abducción.",
        "R7 diferido — no se promueven métricas automáticamente.",
        (
            "Métrica",
            "Origen",
            "Actividades y procesos que la sostienen",
            "Evidencia",
            "Por qué ninguna existente encajaba",
        ),
    )
    s26 = _Situation(
        "2.6",
        "Correcciones de esquema",
        "Arreglos de tipos, propiedades obligatorias o `s(A,T)`.",
        "Restablece I3 (integridad estructural).",
        "C13 no encontró correcciones aplicadas en esta corrida.",
        ("Elemento", "Qué se corrigió"),
    )
    s27 = _Situation(
        "2.7",
        "Reparaciones topológicas (resumen)",
        "Aristas de instancia añadidas en la corrida (ningún tipo ontológico nuevo).",
        "Transparencia de lo que R6 cambió automáticamente.",
        "Derivado de reparaciones R6.",
        ("Arista / cambio", "Evidencia"),
    )
    s28 = _Situation(
        "2.8",
        "Bifurcaciones resueltas",
        "Forks `PRECEDES` sin reconvergencia intermedia clasificados como aceptables (o unidos).",
        "Evita alarmas por hitos en paralelo o ramas de excepción; solo lo irresoluble va a Sección 3.",
        "R6 branch: hito Event paralelo, Event+Activity, o sinks compartidos.",
        ("Nodo horquilla", "Sucesores", "Resolución", "Evidencia"),
    )
    s29 = _Situation(
        "2.9",
        "Renombres de claridad / pares no-variante",
        "Actividades renombradas para no confundir pasos hermanos, o pares descartados como variantes.",
        "Reduce falsos candidatos C9; lo aún ambiguo queda en Sección 3.",
        "R5 claridad (rename) o R5 distinct (secuenciales / roles distintos).",
        ("Elementos", "Cambio o veredicto", "Motivo"),
    )
    for r in result.repairs:
        if r.kind == "R6":
            ids = " · ".join(_node_display(doc, i) for i in r.subject_ids)
            proc = _process_of(doc, r.subject_ids[0]) if r.subject_ids else "—"
            terminal = "—"
            metric = "—"
            if "REALIZES" in r.detail and len(r.subject_ids) >= 2:
                terminal = _node_display(doc, r.subject_ids[0])
                metric = _node_display(doc, r.subject_ids[1])
            elif "PRECEDES" in r.detail and len(r.subject_ids) >= 2:
                terminal = _node_display(doc, r.subject_ids[1])
            s24.rows.append((ids, proc, r.detail, terminal, metric))
            s27.rows.append((r.detail, r.evidence_pointer))
        elif r.kind == "R6_BRANCH":
            fork = _node_display(doc, r.subject_ids[0]) if r.subject_ids else "—"
            succs = ", ".join(_node_display(doc, i) for i in r.subject_ids[1:]) or "—"
            s28.rows.append((fork, succs, r.detail, r.evidence_pointer))
            s27.rows.append((f"branch: {r.detail}", r.evidence_pointer))
        elif r.kind == "R5_RENAME":
            s29.rows.append(
                (
                    _node_display(doc, r.subject_ids[0]) if r.subject_ids else "—",
                    r.detail,
                    r.evidence_pointer,
                )
            )
        elif r.kind == "R5_DISTINCT":
            elems = " · ".join(_node_display(doc, i) for i in r.subject_ids[:2])
            s29.rows.append((elems, "no son variantes", r.detail))
    section2 = [s21, s22, s23, s24, s25, s26, s27, s28, s29]
    section3 = _build_section3_pendientes(doc, idx, findings)
    return section1, section2, section3


def _build_section3_pendientes(
    doc: GraphDocument,
    idx: dict[str, Any],
    findings: tuple[CoherenceFinding, ...],
) -> list[_Situation]:
    """Open-ended pending situations not covered by Sección 1–2."""
    situations: list[_Situation] = []

    # 3.1 Value reachability (structural check 1)
    s_reach = _Situation(
        "3.1",
        "Alcanzabilidad de valor",
        "Un proceso declara contribución a valor pero no hay terminal alcanzable, o una actividad de ese proceso no llega al evento de realización.",
        "Sin ruta al desenlace de valor, la contribución del proceso es una afirmación sin soporte estructural (coherencia de flujo).",
        "Chequeo estructural 1 / REALIZES. Puede ser hueco de aristas PRECEDES, falta de Event terminal, o actividad colgando fuera del eje. No implica por sí solo mala intención.",
        ("Elemento", "Proceso o contexto", "Qué falla"),
    )
    for f in findings:
        if f.check != 1:
            continue
        primary = f.node_ids[0] if f.node_ids else "—"
        proc = "—"
        if doc is not None and f.node_ids:
            node = next((n for n in doc.nodes if n.id == f.node_ids[0]), None)
            if node and node.type == "Activity":
                proc = _process_of(doc, node.id)
            elif node and node.type == "Process":
                proc = _node_display(doc, node.id)
        s_reach.rows.append(
            (
                _node_display(doc, primary) if f.node_ids else "—",
                proc,
                f.description,
            )
        )
    if s_reach.n_cases:
        situations.append(s_reach)

    # 3.2 Flow completeness — hanging / demand without path
    s_flow = _Situation(
        "3.2",
        "Completitud de flujo",
        "Demandas sin camino a valor, o actividades colgantes (aisladas en PRECEDES).",
        "Fragmentos del grafo no participan del patrón demanda→valor; el mapa operativo está incompleto o roto.",
        "C6 y chequeo estructural 4. Una actividad aislada puede ser soporte real no enlazado, o basura de extracción.",
        ("Elemento", "Tipo de hueco", "Detalle"),
    )
    for f in findings:
        if f.check == 4 or (
            f.check == "C6"
            and ("Hanging" in f.description or "Demand" in f.description or "no PRECEDES path" in f.description)
        ):
            kind = "actividad aislada" if f.check == 4 or "Hanging" in f.description else "demanda sin ruta a valor"
            nid = f.node_ids[0] if f.node_ids else "—"
            if any(r[0].endswith(f"({nid})") and r[1] == kind for r in s_flow.rows):
                continue
            s_flow.rows.append(
                (
                    _node_display(doc, nid) if f.node_ids else "—",
                    kind,
                    f.description,
                )
            )
    if s_flow.n_cases:
        situations.append(s_flow)

    # 3.x Branch / cycle topology — only unresolved check-5 forks
    s_topo = _Situation(
        "3.3",
        "Topología de flujo (ramas irresolubles)",
        "Forks `PRECEDES` que no reconvergen y no encajan en hito paralelo / excepción / sinks compartidos.",
        "Aquí sí hay ambigüedad de orden hacia el valor; priorización y P pueden fallar.",
        "Check 5 tras filtro R6. Los forks aceptados están en Sección 2.8.",
        ("Elemento(s)", "Proceso (si aplica)", "Qué se observó"),
    )
    for f in findings:
        if f.check == 5 or f.check == "C7" or (f.check == 2):
            elems = ", ".join(_node_display(doc, n) for n in f.node_ids) if f.node_ids else "—"
            proc = "—"
            if f.node_ids:
                proc = _process_of(doc, f.node_ids[0])
            s_topo.rows.append((elems, proc, f.description))
    if s_topo.n_cases:
        situations.append(s_topo)

    # Variant candidates (C9) — only still-ambiguous after clarity/distinct
    s_var = _Situation(
        "3.4",
        "Candidatos a variante (pendientes)",
        "Pares con misma intención y vecindario solapado que no se pudieron descartar ni aclarar con renombre.",
        "Pueden ser el mismo esfuerzo con nombres distintos — requieren juicio / `VARIANT_OF`.",
        "C9 tras R5 claridad. Renombres y pares descartados están en Sección 2.9.",
        ("Actividad A", "Actividad B", "Intención compartida", "Proceso(s)", "Solapamiento"),
    )
    for f in findings:
        if f.check != "C9" or len(f.node_ids) < 3:
            continue
        a, b, iid = f.node_ids[0], f.node_ids[1], f.node_ids[2]
        overlap = "—"
        if "overlap=" in f.description:
            overlap = f.description.split("overlap=")[-1].strip()
        s_var.rows.append(
            (
                _node_display(doc, a),
                _node_display(doc, b),
                _node_display(doc, iid),
                f"{_process_of(doc, a)} · {_process_of(doc, b)}",
                overlap,
            )
        )
    if s_var.n_cases:
        situations.append(s_var)

    # 3.5 Merge candidates (C10)
    s_merge = _Situation(
        "3.5",
        "Candidatos a fusión de intenciones",
        "Intenciones con formulación similar, mismo SERVES y perseguidores solapados.",
        "Compresión posible (R3); fusionar mal borra distinciones reales de propósito.",
        "C10. R3 diferido — requiere equivalencia semántica con evidencia, no solo similitud de texto.",
        ("Intención A", "Intención B", "Quién las persigue", "Detalle"),
    )
    for f in findings:
        if f.check != "C10" or len(f.node_ids) < 2:
            continue
        ia, ib = f.node_ids[0], f.node_ids[1]
        who = "; ".join(
            _pursuers_of(doc, ia) + [p for p in _pursuers_of(doc, ib) if p not in _pursuers_of(doc, ia)]
        ) or "—"
        s_merge.rows.append(
            (
                _node_display(doc, ia),
                _node_display(doc, ib),
                who,
                f.description,
            )
        )
    if s_merge.n_cases:
        situations.append(s_merge)

    # 3.6 Effect without declared intent
    s_fx = _Situation(
        "3.6",
        "Efecto sin intención declarada",
        "La actividad mueve una métrica por efecto, pero ninguna intención que persigue `SERVES` a esa métrica.",
        "Efecto colateral o propósito no declarado — no se debe confundir con relevancia intencional.",
        "C4 (efecto sin Intent.SERVES). Distinto de 1.5 (persigue sin llegar).",
        ("Actividad", "Proceso", "Métrica afectada", "Intenciones actuales de la actividad"),
    )
    for f in findings:
        if f.check != "C4" or "no Intent that SERVES" not in f.description or len(f.node_ids) < 2:
            continue
        aid, mid = f.node_ids[0], f.node_ids[1]
        intents = activity_intents(aid, idx)
        intent_txt = (
            "; ".join(_node_display(doc, i) for i in sorted(intents)) if intents else "— (ninguna)"
        )
        s_fx.rows.append(
            (
                _node_display(doc, aid),
                _process_of(doc, aid),
                _node_display(doc, mid),
                intent_txt,
            )
        )
    if s_fx.n_cases:
        situations.append(s_fx)

    # 3.7 Other residual / unclassified leftovers (C5 purpose reachability, etc.)
    covered_checks = {1, 2, 4, 5, "C6", "C7", "C9", "C10"}
    s_other = _Situation(
        "3.7",
        "Otros pendientes",
        "Banderas residuales o de juicio que no encajan en 3.1–3.6 ni en las Secciones 1–2.",
        "Quedan en agenda de validación: el grafo no puede decidir solo.",
        "Clasificación residual del triage. Revisar caso a caso con evidencia de entrevista.",
        ("Elementos", "Chequeo", "Detalle"),
    )
    for f in findings:
        if f.severity == "info":
            continue
        # Already in section 1
        if f.check in {"C1", "C2", "C3", "C4", "C8", "C11"}:
            continue
        if f.check in covered_checks:
            continue
        if f.check == "C12":
            continue
        if f.check == "C5":
            elems = ", ".join(_node_display(doc, n) for n in f.node_ids) if f.node_ids else "—"
            s_other.rows.append((elems, "C5", f.description))
        elif f.check == "C13" and f.severity == "error":
            elems = ", ".join(_node_display(doc, n) for n in f.node_ids) if f.node_ids else "—"
            s_other.rows.append((elems, "C13", f.description))
        elif f.check == 3:  # orphan events
            elems = ", ".join(_node_display(doc, n) for n in f.node_ids) if f.node_ids else "—"
            s_other.rows.append((elems, "Check 3", f.description))
        elif f.check in {6, 7} and f.severity == "error":
            elems = ", ".join(_node_display(doc, n) for n in f.node_ids) if f.node_ids else "—"
            s_other.rows.append((elems, f"Check {f.check}", f.description))
    if s_other.n_cases:
        situations.append(s_other)

    # Renumber densely 3.1.. only those present (already numbered; keep gaps ok OR renumber)
    for i, s in enumerate(situations, start=1):
        s.code = f"3.{i}"
    return situations


def format_protocol_report(result: ProtocolResult) -> str:
    """Salidas según Protocolo v0.3 — situaciones con contexto; topología auto; ontología autorizada."""
    section1, section2, section3 = _build_situations(result)
    chunks: list[str] = [
        "# Auditoría de coherencia — protocolo v0.3",
        "",
        "## Encabezado",
        "",
        f"- **Grado de coherencia:** {_degree_line(result.degree_before)} → {_degree_line(result.degree)}",
        f"- **Iteraciones:** {result.iterations}",
        f"- **Ciclo convergió:** {'sí' if result.converged else 'no'}"
        + ("; no convergente" if result.non_convergent else ""),
        "",
    ]

    def top3(section: list[_Situation], label: str) -> None:
        ranked = sorted((s for s in section if s.n_cases), key=lambda s: -s.n_cases)[:3]
        if not ranked:
            chunks.append(f"- **Top situaciones ({label}):** ninguna con casos")
            return
        parts = [f"{s.code} {s.title} ({s.n_cases})" for s in ranked]
        chunks.append(f"- **Top situaciones ({label}):** " + "; ".join(parts))

    top3(section1, "Sección 1")
    top3(section2, "Sección 2")
    top3(section3, "Sección 3")
    chunks.append("")

    chunks += ["## Sección 1 — Salud de las intenciones", ""]
    empty1: list[str] = []
    for s in section1:
        if s.n_cases:
            chunks.extend(_situation_block(s))
        else:
            empty1.append(f"{s.code} {s.title}")
    if empty1:
        chunks.append("_Sin casos:_ " + "; ".join(empty1))
        chunks.append("")

    chunks += ["## Sección 2 — Cambios en el grafo", ""]
    empty2: list[str] = []
    for s in section2:
        if s.n_cases:
            chunks.extend(_situation_block(s))
        else:
            empty2.append(f"{s.code} {s.title}")
    if empty2:
        chunks.append("_Sin casos:_ " + "; ".join(empty2))
        chunks.append("")

    chunks += ["## Sección 3 — Pendientes a resolver", ""]
    if not section3:
        chunks.append("_Ningún pendiente fuera de las Secciones 1–2._")
        chunks.append("")
    else:
        for s in section3:
            chunks.extend(_situation_block(s))

    return "\n".join(chunks).rstrip() + "\n"


def compute_degree(document: GraphDocument) -> CoherenceDegree:
    idx = _index(document)
    ladder = {"N1": 0, "N2": 0, "N3": 0, "N4": 0}
    acts = 0
    for node in document.nodes:
        if node.type != "Activity":
            continue
        acts += 1
        level = ladder_level(node.id, idx)
        if level:
            ladder[level] += 1
    evidence = abduced = 0
    intents = 0
    for node in document.nodes:
        if node.type != INTENT_NODE_TYPE:
            continue
        intents += 1
        basis = _props(node).get("generation_basis")
        if basis == "evidence":
            evidence += 1
        else:
            abduced += 1
    compression = acts / intents if intents else 0.0
    return CoherenceDegree(ladder, evidence, abduced, compression, acts, intents)


def run_protocol_cycle(
    document: GraphDocument,
    *,
    max_iters: int = 5,
    previous_degree: dict[str, Any] | None = None,
    authorize_ontology: bool = False,
) -> ProtocolResult:
    all_repairs: list[RepairRecord] = []
    fusions: list[dict[str, Any]] = []
    iterations = 0
    degree_before = compute_degree(document)

    def snapshot() -> tuple[CoherenceFinding, ...]:
        return tuple(audit_coherence(document)) + tuple(
            check_c5(document)
            + check_c6(document)
            + check_c7(document)
            + check_c8(document)
            + check_c9(document)
            + check_c10(document)
            + check_c11(document)
            + check_c12(document)
            + check_c13(document)
            + check_c14(document, previous=previous_degree)
        )

    def finish(
        findings: tuple[CoherenceFinding, ...],
        *,
        converged: bool,
        non_convergent: bool,
    ) -> ProtocolResult:
        triage = triage_findings(findings)
        if non_convergent:
            for t in triage:
                if t.classification == "defecto" and t.finding.check == "C1":
                    t.classification = "residuo"
                    t.note = "No convergente — " + t.note
        agenda = [
            f"¿{t.note}? nodos={','.join(t.finding.node_ids)}"
            for t in triage
            if t.classification == "residuo"
        ]
        if not authorize_ontology:
            for dropped, canonical, evidence in propose_r3_means_to_end(document):
                agenda.append(
                    f"R3 means-to-end propuesto (requiere --authorize-ontology): "
                    f"{dropped} → {canonical} ({evidence})"
                )
        return ProtocolResult(
            iterations=iterations,
            converged=converged,
            non_convergent=non_convergent,
            repairs=all_repairs,
            fusions=fusions,
            triage=triage,
            validation_agenda=agenda,
            degree=compute_degree(document),
            degree_before=degree_before,
            findings=findings,
            document=document,
        )

    for _ in range(max_iters):
        iterations += 1
        batch: list[RepairRecord] = []
        batch.extend(repair_r1(document))
        batch.extend(repair_r2(document))
        batch.extend(repair_topology(document))
        batch.extend(repair_branch_forks(document))
        batch.extend(repair_label_clarity(document))
        r3 = repair_r3_means_to_end(document, authorize_ontology=authorize_ontology)
        for r in r3:
            fusions.append(
                {
                    "dropped": r.subject_ids[0],
                    "canonical": r.subject_ids[1],
                    "evidence": r.evidence_pointer,
                }
            )
        batch.extend(r3)

        if not batch:
            findings = snapshot()
            return finish(
                findings,
                converged=_defect_count(findings) == 0,
                non_convergent=False,
            )
        all_repairs.extend(batch)

    return finish(snapshot(), converged=False, non_convergent=True)


def document_to_graph_json(document: GraphDocument, *, meta: dict[str, Any] | None = None) -> dict:
    nodes = []
    for n in document.nodes:
        props = dict(n.properties or {})
        label = props.pop("label", n.id)
        nodes.append({"id": n.id, "type": n.type, "label": label, "properties": props})
    rels = []
    for r in document.relationships:
        rels.append(
            {
                "source": r.source.id,
                "target": r.target.id,
                "type": r.type,
                "properties": dict(r.properties or {}),
            }
        )
    out = {"nodes": nodes, "relationships": rels}
    if meta:
        out.update(meta)
    return out
