"""Build ``GraphDocument`` lists for graph-filter tests (ui2-02)."""

from __future__ import annotations

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document


def process_isolation_graph_documents() -> list[GraphDocument]:
    """
    P-01 ─ PART_OF ─ A-01 ─ AFFECTS ─ M-01
    P-02 ─ PART_OF ─ A-02 ─ AFFECTS ─ M-02
    """
    p1 = Node(id="P-01", type="Process", properties={"label": "Process One"})
    p2 = Node(id="P-02", type="Process", properties={"label": "Process Two"})
    a1 = Node(
        id="A-01",
        type="Activity",
        properties={"label": "Activity One", "process_id": "P-01"},
    )
    a2 = Node(
        id="A-02",
        type="Activity",
        properties={"label": "Activity Two", "process_id": "P-02"},
    )
    m1 = Node(id="M-01", type="Metric", properties={"label": "Metric One"})
    m2 = Node(id="M-02", type="Metric", properties={"label": "Metric Two"})

    rels = [
        Relationship(source=a1, target=p1, type="PART_OF"),
        Relationship(source=a2, target=p2, type="PART_OF"),
        Relationship(source=a1, target=m1, type="AFFECTS"),
        Relationship(source=a2, target=m2, type="AFFECTS"),
    ]
    return [
        GraphDocument(
            nodes=[p1, p2, a1, a2, m1, m2],
            relationships=rels,
            source=Document(page_content="filter fixture"),
        )
    ]
