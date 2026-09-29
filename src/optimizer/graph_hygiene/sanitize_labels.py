"""Keep evidence out of node display names; park it on evidence_pointer."""

from __future__ import annotations

import re
from typing import Any

from langchain_community.graphs.graph_document import GraphDocument, Node

# Italic inventory notes: *(corregido F2: …)*
_ITALIC_NOTE = re.compile(r"\s*\*\(([^)]*)\)\*")
# Parenthetical editorial notes after markdown strip / inventory prose
_PAREN_NOTE = re.compile(
    r"\s*\((?:corregido|nota|evidencia|F\d)[^)]*\)",
    re.IGNORECASE,
)


def split_label_evidence(raw: str) -> tuple[str, str | None]:
    """Return (clean_label, evidence_note_or_None)."""
    text = (raw or "").strip()
    notes: list[str] = []

    while True:
        match = _ITALIC_NOTE.search(text)
        if not match:
            break
        notes.append(match.group(1).strip())
        text = text[: match.start()] + text[match.end() :]

    while True:
        match = _PAREN_NOTE.search(text)
        if not match:
            break
        notes.append(match.group(0).strip().strip("()").strip())
        text = text[: match.start()] + text[match.end() :]

    clean = re.sub(r"\s+", " ", text).strip(" \t-–—")
    if not notes:
        return clean, None
    return clean, "; ".join(notes)


def _merge_evidence(existing: Any, note: str) -> str:
    prior = str(existing).strip() if existing else ""
    if not prior:
        return note
    if note in prior:
        return prior
    return f"{prior}; {note}"


def sanitize_label_fields(
    label: str,
    properties: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Clean *label*; move extracted notes into properties['evidence_pointer']."""
    props = dict(properties or {})
    clean, note = split_label_evidence(label)
    if note:
        props["evidence_pointer"] = _merge_evidence(props.get("evidence_pointer"), note)
    if props.get("label") is not None:
        props["label"] = clean
    return clean, props


def sanitize_graph_document(document: GraphDocument) -> GraphDocument:
    """In-place: strip evidence from node labels into evidence_pointer."""
    for node in document.nodes:
        props = dict(node.properties or {})
        raw = props.get("label") or node.id
        clean, props = sanitize_label_fields(str(raw), props)
        props["label"] = clean
        node.properties = props
    return document


def sanitize_graph_json(graph: dict[str, Any]) -> dict[str, Any]:
    """Clean top-level node labels in a graph.json payload (mutates *graph*)."""
    for raw in graph.get("nodes", []):
        label = raw.get("label")
        if not label:
            continue
        clean, props = sanitize_label_fields(str(label), raw.get("properties"))
        raw["label"] = clean
        raw["properties"] = props
    return graph


# ponytail: Node mutability is LangChain's model; copy-on-write if callers need immutability
def sanitize_node(node: Node) -> Node:
    props = dict(node.properties or {})
    raw = props.get("label") or node.id
    clean, props = sanitize_label_fields(str(raw), props)
    props["label"] = clean
    node.properties = props
    return node
