"""A-26 relevance explain + punto ciego fixtures (ui2-07 / ui2-08)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document

if TYPE_CHECKING:
    from optimizer.application.scenario_models import ValueScenarioInput


def edge_key(source_id: str, target_id: str, rel_type: str) -> tuple[str, str, str]:
    return (source_id, target_id, rel_type.upper())


def a26_relevance_explain_graph_documents() -> list[GraphDocument]:
    """
    Minimal AC-EXPLAIN-1 graph: A-26 G paths (M-01/M-02) + J paths (M-04/M-05/M-06 via CJS).

    Includes unrelated nodes (A-27, P-06, M-03) that must stay in the graph but outside
    the explain highlight set.
    """
    p05 = Node(id="P-05", type="Process", properties={"label": "Logística"})
    p06 = Node(id="P-06", type="Process", properties={"label": "Other process"})
    a26 = Node(
        id="A-26",
        type="Activity",
        properties={"label": "Entrega en planta cliente", "process_id": "P-05"},
    )
    a27 = Node(
        id="A-27",
        type="Activity",
        properties={"label": "Mantenimiento flota", "process_id": "P-05"},
    )
    m01 = Node(id="M-01", type="Metric", properties={"label": "Entrega a tiempo"})
    m02 = Node(id="M-02", type="Metric", properties={"label": "Volumen"})
    m03 = Node(id="M-03", type="Metric", properties={"label": "Unrelated metric"})
    m04 = Node(id="M-04", type="Metric", properties={"label": "Incidentes regulatorios"})
    m05 = Node(id="M-05", type="Metric", properties={"label": "Días de crédito"})
    m06 = Node(id="M-06", type="Metric", properties={"label": "Retención clientes"})
    cjs04 = Node(id="CJS-04", type="CustomerJourneyStep", properties={"label": "Primera entrega"})
    cjs05 = Node(id="CJS-05", type="CustomerJourneyStep", properties={"label": "Ciclo recurrente"})

    rels = [
        Relationship(source=a26, target=p05, type="PART_OF"),
        Relationship(source=a27, target=p05, type="PART_OF"),
        Relationship(source=p05, target=m01, type="CONTRIBUTES_TO"),
        Relationship(source=p05, target=m02, type="CONTRIBUTES_TO"),
        Relationship(source=a26, target=m01, type="AFFECTS"),
        Relationship(source=a26, target=m02, type="AFFECTS"),
        Relationship(source=a26, target=cjs04, type="TOUCHES"),
        Relationship(source=a26, target=cjs05, type="TOUCHES"),
        Relationship(source=cjs04, target=m04, type="SIGNALS"),
        Relationship(source=cjs05, target=m05, type="SIGNALS"),
        Relationship(source=cjs05, target=m06, type="SIGNALS"),
        Relationship(source=a27, target=m03, type="AFFECTS"),
        Relationship(source=p06, target=m03, type="CONTRIBUTES_TO"),
    ]
    nodes = [p05, p06, a26, a27, m01, m02, m03, m04, m05, m06, cjs04, cjs05]
    return [
        GraphDocument(
            nodes=nodes,
            relationships=rels,
            source=Document(page_content="a26 explain fixture"),
        )
    ]


def a26_value_scenario() -> ValueScenarioInput:
    """Scores for A-26 matching energoil fixture (G on M-01/M-02, J on M-04/M-05/M-06)."""
    from optimizer.application.scenario_models import (
        ActivityRow,
        ActivityScoreRow,
        MetricRow,
        ValueScenarioInput,
    )

    metrics = tuple(
        MetricRow(id=mid, name=f"Metric {mid}", definition="", client_need="")
        for mid in ("M-01", "M-02", "M-03", "M-04", "M-05", "M-06")
    )
    return ValueScenarioInput(
        metrics=metrics,
        activities=(
            ActivityRow(
                activity_id="A-26",
                activity_name="Entrega en planta cliente",
                process_id="P-05",
                p=1.0,
                c=1.0,
                f=1.0,
                r=0.75,
                v=0.98,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=1.0,
                        j=0.95,
                        dv=0.0,
                        b=0.78,
                        relevance=0.7644,
                        pct_contribution=0.17,
                    ),
                    ActivityScoreRow(
                        metric_id="M-02",
                        g=1.0,
                        j=0.9,
                        dv=0.0,
                        b=0.76,
                        relevance=0.7448,
                        pct_contribution=0.19,
                    ),
                    ActivityScoreRow(
                        metric_id="M-04",
                        g=0.0,
                        j=0.7,
                        dv=0.0,
                        b=0.28,
                        relevance=0.2744,
                        pct_contribution=0.09,
                    ),
                    ActivityScoreRow(
                        metric_id="M-05",
                        g=0.0,
                        j=0.55,
                        dv=0.0,
                        b=0.22,
                        relevance=0.2156,
                        pct_contribution=0.07,
                    ),
                    ActivityScoreRow(
                        metric_id="M-06",
                        g=0.0,
                        j=0.8,
                        dv=0.0,
                        b=0.32,
                        relevance=0.3136,
                        pct_contribution=0.09,
                    ),
                ),
            ),
        ),
        process_rollups=(),
        strategic_b_zero=(),
        process_labels={"P-05": "Logística"},
    )


def explain_relevance_scenario() -> tuple[ValueScenarioInput, list[GraphDocument], str]:
    """Scenario + graph for ga-04 explain-path smoke (G and J paths on A-26)."""
    return a26_value_scenario(), a26_relevance_explain_graph_documents(), "A-26"


def expected_a26_highlight_node_ids() -> frozenset[str]:
    return frozenset(
        {
            "A-26",
            "P-05",
            "M-01",
            "M-02",
            "M-04",
            "M-05",
            "M-06",
            "CJS-04",
            "CJS-05",
        }
    )


def expected_a26_highlight_edge_keys() -> frozenset[tuple[str, str, str]]:
    return frozenset(
        {
            edge_key("A-26", "P-05", "PART_OF"),
            edge_key("P-05", "M-01", "CONTRIBUTES_TO"),
            edge_key("P-05", "M-02", "CONTRIBUTES_TO"),
            edge_key("A-26", "M-01", "AFFECTS"),
            edge_key("A-26", "M-02", "AFFECTS"),
            edge_key("A-26", "CJS-04", "TOUCHES"),
            edge_key("A-26", "CJS-05", "TOUCHES"),
            edge_key("CJS-04", "M-04", "SIGNALS"),
            edge_key("CJS-05", "M-05", "SIGNALS"),
            edge_key("CJS-05", "M-06", "SIGNALS"),
        }
    )


def punto_ciego_graph_documents() -> list[GraphDocument]:
    """Single activity with direct AFFECTS to M-01 and journey-only linkage to M-04."""
    activity = Node(
        id="A-01",
        type="Activity",
        properties={"label": "Activity One", "process_id": "P-01"},
    )
    cjs = Node(id="CJS-01", type="CustomerJourneyStep", properties={"label": "Stage"})
    m_direct = Node(id="M-01", type="Metric", properties={"label": "Direct metric"})
    m_indirect = Node(id="M-04", type="Metric", properties={"label": "Journey metric"})
    rels = [
        Relationship(source=activity, target=m_direct, type="AFFECTS"),
        Relationship(source=activity, target=cjs, type="TOUCHES"),
        Relationship(source=cjs, target=m_indirect, type="SIGNALS"),
    ]
    return [
        GraphDocument(
            nodes=[activity, cjs, m_direct, m_indirect],
            relationships=rels,
            source=Document(page_content="punto ciego fixture"),
        )
    ]
