"""Protocol cycle R1/R2/R6; optional R3; report v0.3."""

from __future__ import annotations

import unittest

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document

from optimizer.graph_hygiene.protocol import run_protocol_cycle


def _n(nid: str, ntype: str, **props) -> Node:
    return Node(id=nid, type=ntype, properties=props)


def _r(src: Node, tgt: Node, rtype: str, **props) -> Relationship:
    return Relationship(source=src, target=tgt, type=rtype, properties=props)


class TestProtocolCycle(unittest.TestCase):
    def test_r1_r2_assign_process_intent_and_serves_metric(self):
        p = _n("P1", "Process", label="Facturación")
        a = _n("A1", "Activity", label="Timbrar")
        m = _n("M1", "Metric", label="CFDI a tiempo")
        doc = GraphDocument(
            nodes=[p, a, m],
            relationships=[_r(a, p, "PART_OF"), _r(p, m, "CONTRIBUTES_TO")],
            source=Document(page_content="t"),
        )
        result = run_protocol_cycle(doc)
        self.assertTrue(any(r.kind == "R1" for r in result.repairs))
        self.assertTrue(any(r.kind == "R2" for r in result.repairs))
        self.assertFalse(
            any(
                f.check == "C1" and "no Intent" in f.description for f in result.findings
            )
        )
        intents = [n for n in doc.nodes if n.type == "Intent"]
        self.assertEqual(len(intents), 1)
        serves = [
            r
            for r in doc.relationships
            if r.type.upper() == "SERVES" and r.target.id == "M1"
        ]
        self.assertTrue(serves)

    def test_report_uses_v03_situation_format(self):
        p = _n("P1", "Process", label="Facturación")
        a = _n("A1", "Activity", label="Timbrar")
        m = _n("M1", "Metric", label="CFDI a tiempo")
        doc = GraphDocument(
            nodes=[p, a, m],
            relationships=[_r(a, p, "PART_OF"), _r(p, m, "CONTRIBUTES_TO")],
            source=Document(page_content="t"),
        )
        from optimizer.graph_hygiene.protocol import format_protocol_report

        text = format_protocol_report(run_protocol_cycle(doc))
        self.assertIn("protocolo v0.3", text)
        self.assertIn("## Sección 1 — Salud de las intenciones", text)
        self.assertIn("#### 1.1 Actividades sin intención (reparadas)", text)
        self.assertIn("## Sección 3 — Pendientes a resolver", text)
        self.assertIn("Timbrar (A1)", text)
        self.assertIn("**Por qué importa.**", text)

    def test_topology_realizes_and_authorized_r3_merge(self):
        p_quote = _n("PRO-02", "Process", label="Cotización")
        p_order = _n("PRO-03", "Process", label="Pedidos")
        a_cost = _n("ACT-26", "Activity", label="Costo flete")
        a_quote = _n("ACT-03", "Activity", label="Cotizar")
        a_order = _n("ACT-05", "Activity", label="Disponibilidad")
        m = _n("MET-01", "Metric", label="Entrega")
        ev = _n("EVT-09", "Event", label="Entrega OK", event_type="value_realization")
        doc = GraphDocument(
            nodes=[p_quote, p_order, a_cost, a_quote, a_order, m, ev],
            relationships=[
                _r(a_quote, p_quote, "PART_OF"),
                _r(a_order, p_order, "PART_OF"),
                _r(p_order, m, "CONTRIBUTES_TO"),
                _r(a_cost, a_quote, "PRECEDES"),
                _r(a_quote, a_order, "PRECEDES"),
                _r(a_order, ev, "PRECEDES"),
                _r(a_order, ev, "INVOLVES_EVENT", event_role="produce"),
            ],
            source=Document(page_content="t"),
        )
        result = run_protocol_cycle(doc, authorize_ontology=True)
        realizes = [
            r
            for r in doc.relationships
            if r.type.upper() == "REALIZES"
            and r.source.id == "EVT-09"
            and r.target.id == "MET-01"
        ]
        self.assertTrue(realizes, "R6 should wire REALIZES")
        self.assertTrue(
            any(r.kind == "R3" for r in result.repairs),
            "R3 should merge feeder intent",
        )
        intent_ids = {n.id for n in doc.nodes if n.type == "Intent"}
        self.assertLessEqual(len(intent_ids), 2)


if __name__ == "__main__":
    unittest.main()
