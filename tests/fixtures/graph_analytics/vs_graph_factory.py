"""Graph + value fixtures for value-stream and graph-bridge tests (ga-02, ga-05)."""

from __future__ import annotations

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document

from optimizer.application.scenario_models import (
    ActivityRow,
    ActivityScoreRow,
    MetricRow,
    ValueScenarioInput,
)


def value_stream_graph_documents() -> list[GraphDocument]:
    """
    Minimal VS path for M-01:

    EV-D1 (demand) --PRECEDES--> A-01 --PRECEDES--> A-02 --PRECEDES--> EV-V1 (value)
    A-03 --PRECEDES--> A-01   (structural support upstream of VS)
    A-04 isolated             (waste)
    """
    ev_d1 = Node(
        id="EV-D1",
        type="Event",
        properties={"label": "Orden de compra", "event_type": "demand"},
    )
    ev_v1 = Node(
        id="EV-V1",
        type="Event",
        properties={"label": "Entrega confirmada", "event_type": "value_realization"},
    )
    a1 = Node(
        id="A-01",
        type="Activity",
        properties={"label": "Actividad VS 1", "area": "operaciones"},
    )
    a2 = Node(
        id="A-02",
        type="Activity",
        properties={"label": "Actividad VS 2", "area": "operaciones"},
    )
    a3 = Node(
        id="A-03",
        type="Activity",
        properties={"label": "Soporte estructural", "area": "logistica"},
    )
    a4 = Node(
        id="A-04",
        type="Activity",
        properties={"label": "Desperdicio", "area": "operaciones"},
    )
    m1 = Node(id="M-01", type="Metric", properties={"label": "Entrega a tiempo"})

    rels = [
        Relationship(source=ev_d1, target=a1, type="PRECEDES"),
        Relationship(source=a1, target=a2, type="PRECEDES"),
        Relationship(source=a2, target=ev_v1, type="PRECEDES"),
        Relationship(source=a3, target=a1, type="PRECEDES"),
        Relationship(source=a1, target=m1, type="AFFECTS"),
        Relationship(source=a2, target=m1, type="AFFECTS"),
    ]
    return [
        GraphDocument(
            nodes=[ev_d1, ev_v1, a1, a2, a3, a4, m1],
            relationships=rels,
            source=Document(page_content="vs fixture"),
        )
    ]


def value_stream_value_input() -> ValueScenarioInput:
    return ValueScenarioInput(
        metrics=(
            MetricRow(
                id="M-01",
                name="Entrega a tiempo",
                definition="",
                client_need="",
            ),
        ),
        activities=(
            ActivityRow(
                activity_id="A-01",
                activity_name="Actividad VS 1",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.6,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.3,
                        relevance=0.8,
                        pct_contribution=0.5,
                    ),
                ),
            ),
            ActivityRow(
                activity_id="A-02",
                activity_name="Actividad VS 2",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.2,
                        relevance=0.4,
                        pct_contribution=0.3,
                    ),
                ),
            ),
            ActivityRow(
                activity_id="A-03",
                activity_name="Soporte estructural",
                process_id="P-02",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.9,
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
            ActivityRow(
                activity_id="A-04",
                activity_name="Desperdicio",
                process_id="P-99",
                p=0.1,
                c=0.1,
                f=0.1,
                r=0.1,
                v=0.1,
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
        ),
        process_rollups=(),
        strategic_b_zero=(),
        process_labels={"P-01": "Operaciones", "P-02": "Logística"},
    )


def governance_graph_documents() -> list[GraphDocument]:
    """Two paths through G-01 gobernanza dominator A-GOV."""
    ev_d = Node(
        id="EV-D1",
        type="Event",
        properties={"event_type": "demand"},
    )
    ev_v = Node(
        id="EV-V1",
        type="Event",
        properties={"event_type": "value_realization"},
    )
    gov = Node(
        id="A-GOV",
        type="Activity",
        properties={"label": "Aprobación legal", "area": "gobernanza"},
    )
    a1 = Node(id="A-01", type="Activity", properties={"label": "Ops 1"})
    a2 = Node(id="A-02", type="Activity", properties={"label": "Ops 2"})
    m1 = Node(id="M-01", type="Metric", properties={"label": "M1"})

    rels = [
        Relationship(source=ev_d, target=gov, type="PRECEDES"),
        Relationship(source=gov, target=a1, type="PRECEDES"),
        Relationship(source=a1, target=ev_v, type="PRECEDES"),
        Relationship(source=ev_d, target=a2, type="PRECEDES"),
        Relationship(source=a2, target=gov, type="PRECEDES"),
        Relationship(source=a1, target=m1, type="AFFECTS"),
    ]
    return [
        GraphDocument(
            nodes=[ev_d, ev_v, gov, a1, a2, m1],
            relationships=rels,
            source=Document(page_content="governance fixture"),
        )
    ]


def governance_value_input() -> ValueScenarioInput:
    return ValueScenarioInput(
        metrics=(
            MetricRow(id="M-01", name="M1", definition="", client_need=""),
        ),
        activities=(
            ActivityRow(
                activity_id="A-GOV",
                activity_name="Aprobación legal",
                process_id="P-G",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.7,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.5,
                        relevance=0.5,
                        pct_contribution=0.5,
                    ),
                ),
            ),
            ActivityRow(
                activity_id="A-01",
                activity_name="Ops 1",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.3,
                        relevance=0.3,
                        pct_contribution=0.3,
                    ),
                ),
            ),
            ActivityRow(
                activity_id="A-02",
                activity_name="Ops 2",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(),
            ),
        ),
        process_rollups=(),
        strategic_b_zero=(),
    )


def convergent_value_stream_graph_documents() -> list[GraphDocument]:
    """
    Two demand anchors converge through A-MID into one delivery:

    EV-D1 --> A-01 --> A-MID --> EV-V1
    EV-D2 ------------^
    """
    ev_d1 = Node(
        id="EV-D1",
        type="Event",
        properties={"label": "Demanda 1", "event_type": "demand"},
    )
    ev_d2 = Node(
        id="EV-D2",
        type="Event",
        properties={"label": "Demanda 2", "event_type": "demand"},
    )
    ev_v1 = Node(
        id="EV-V1",
        type="Event",
        properties={"label": "Entrega", "event_type": "value_realization"},
    )
    a1 = Node(id="A-01", type="Activity", properties={"label": "Rama 1"})
    amid = Node(id="A-MID", type="Activity", properties={"label": "Convergencia"})
    m1 = Node(id="M-01", type="Metric", properties={"label": "M1"})

    rels = [
        Relationship(source=ev_d1, target=a1, type="PRECEDES"),
        Relationship(source=a1, target=amid, type="PRECEDES"),
        Relationship(source=ev_d2, target=amid, type="PRECEDES"),
        Relationship(source=amid, target=ev_v1, type="PRECEDES"),
        Relationship(source=amid, target=m1, type="AFFECTS"),
    ]
    return [
        GraphDocument(
            nodes=[ev_d1, ev_d2, ev_v1, a1, amid, m1],
            relationships=rels,
            source=Document(page_content="convergent vs fixture"),
        )
    ]


def convergent_value_stream_value_input() -> ValueScenarioInput:
    return ValueScenarioInput(
        metrics=(MetricRow(id="M-01", name="M1", definition="", client_need=""),),
        activities=(
            ActivityRow(
                activity_id="A-01",
                activity_name="Rama 1",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.3,
                        relevance=0.6,
                        pct_contribution=0.5,
                    ),
                ),
            ),
            ActivityRow(
                activity_id="A-MID",
                activity_name="Convergencia",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.5,
                        relevance=1.0,
                        pct_contribution=0.5,
                    ),
                ),
            ),
        ),
        process_rollups=(),
        strategic_b_zero=(),
    )


def shared_backbone_graph_documents() -> list[GraphDocument]:
    """
    Shared mid-stream activity across two delivery groups:

    EV-D1 --> A-SHARED --> EV-V1
    EV-D2 --> A-SHARED --> EV-V2
    """
    ev_d1 = Node(
        id="EV-D1",
        type="Event",
        properties={"event_type": "demand"},
    )
    ev_d2 = Node(
        id="EV-D2",
        type="Event",
        properties={"event_type": "demand"},
    )
    ev_v1 = Node(
        id="EV-V1",
        type="Event",
        properties={"event_type": "value_realization"},
    )
    ev_v2 = Node(
        id="EV-V2",
        type="Event",
        properties={"event_type": "value_realization"},
    )
    shared = Node(id="A-SHARED", type="Activity", properties={"label": "Shared"})
    m1 = Node(id="M-01", type="Metric", properties={"label": "M1"})

    rels = [
        Relationship(source=ev_d1, target=shared, type="PRECEDES"),
        Relationship(source=shared, target=ev_v1, type="PRECEDES"),
        Relationship(source=ev_d2, target=shared, type="PRECEDES"),
        Relationship(source=shared, target=ev_v2, type="PRECEDES"),
        Relationship(source=shared, target=m1, type="AFFECTS"),
    ]
    return [
        GraphDocument(
            nodes=[ev_d1, ev_d2, ev_v1, ev_v2, shared, m1],
            relationships=rels,
            source=Document(page_content="shared backbone fixture"),
        )
    ]


def shared_backbone_value_input() -> ValueScenarioInput:
    return ValueScenarioInput(
        metrics=(MetricRow(id="M-01", name="M1", definition="", client_need=""),),
        activities=(
            ActivityRow(
                activity_id="A-SHARED",
                activity_name="Shared",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.5,
                        relevance=0.5,
                        pct_contribution=1.0,
                    ),
                ),
            ),
        ),
        process_rollups=(),
        strategic_b_zero=(),
    )


def convergent_value_stream_graph_documents() -> list[GraphDocument]:
    """
    Two demand anchors converge through A-MID into one delivery:

    EV-D1 --> A-01 --> A-MID --> EV-V1
    EV-D2 ------------^
    """
    ev_d1 = Node(
        id="EV-D1",
        type="Event",
        properties={"label": "Demanda 1", "event_type": "demand"},
    )
    ev_d2 = Node(
        id="EV-D2",
        type="Event",
        properties={"label": "Demanda 2", "event_type": "demand"},
    )
    ev_v1 = Node(
        id="EV-V1",
        type="Event",
        properties={"label": "Entrega", "event_type": "value_realization"},
    )
    a1 = Node(id="A-01", type="Activity", properties={"label": "Rama 1"})
    amid = Node(id="A-MID", type="Activity", properties={"label": "Convergencia"})
    m1 = Node(id="M-01", type="Metric", properties={"label": "M1"})

    rels = [
        Relationship(source=ev_d1, target=a1, type="PRECEDES"),
        Relationship(source=a1, target=amid, type="PRECEDES"),
        Relationship(source=ev_d2, target=amid, type="PRECEDES"),
        Relationship(source=amid, target=ev_v1, type="PRECEDES"),
        Relationship(source=amid, target=m1, type="AFFECTS"),
    ]
    return [
        GraphDocument(
            nodes=[ev_d1, ev_d2, ev_v1, a1, amid, m1],
            relationships=rels,
            source=Document(page_content="convergent vs fixture"),
        )
    ]


def convergent_value_stream_value_input() -> ValueScenarioInput:
    return ValueScenarioInput(
        metrics=(MetricRow(id="M-01", name="M1", definition="", client_need=""),),
        activities=(
            ActivityRow(
                activity_id="A-01",
                activity_name="Rama 1",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.3,
                        relevance=0.6,
                        pct_contribution=0.5,
                    ),
                ),
            ),
            ActivityRow(
                activity_id="A-MID",
                activity_name="Convergencia",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.5,
                        relevance=1.0,
                        pct_contribution=0.5,
                    ),
                ),
            ),
        ),
        process_rollups=(),
        strategic_b_zero=(),
    )


def shared_backbone_graph_documents() -> list[GraphDocument]:
    """
    Shared mid-stream activity across two delivery groups:

    EV-D1 --> A-SHARED --> EV-V1
    EV-D2 --> A-SHARED --> EV-V2
    """
    ev_d1 = Node(
        id="EV-D1",
        type="Event",
        properties={"event_type": "demand"},
    )
    ev_d2 = Node(
        id="EV-D2",
        type="Event",
        properties={"event_type": "demand"},
    )
    ev_v1 = Node(
        id="EV-V1",
        type="Event",
        properties={"event_type": "value_realization"},
    )
    ev_v2 = Node(
        id="EV-V2",
        type="Event",
        properties={"event_type": "value_realization"},
    )
    shared = Node(id="A-SHARED", type="Activity", properties={"label": "Shared"})
    m1 = Node(id="M-01", type="Metric", properties={"label": "M1"})

    rels = [
        Relationship(source=ev_d1, target=shared, type="PRECEDES"),
        Relationship(source=shared, target=ev_v1, type="PRECEDES"),
        Relationship(source=ev_d2, target=shared, type="PRECEDES"),
        Relationship(source=shared, target=ev_v2, type="PRECEDES"),
        Relationship(source=shared, target=m1, type="AFFECTS"),
    ]
    return [
        GraphDocument(
            nodes=[ev_d1, ev_d2, ev_v1, ev_v2, shared, m1],
            relationships=rels,
            source=Document(page_content="shared backbone fixture"),
        )
    ]


def shared_backbone_value_input() -> ValueScenarioInput:
    return ValueScenarioInput(
        metrics=(MetricRow(id="M-01", name="M1", definition="", client_need=""),),
        activities=(
            ActivityRow(
                activity_id="A-SHARED",
                activity_name="Shared",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(
                    ActivityScoreRow(
                        metric_id="M-01",
                        g=0.0,
                        j=0.0,
                        dv=0.0,
                        b=0.5,
                        relevance=0.5,
                        pct_contribution=1.0,
                    ),
                ),
            ),
        ),
        process_rollups=(),
        strategic_b_zero=(),
    )
