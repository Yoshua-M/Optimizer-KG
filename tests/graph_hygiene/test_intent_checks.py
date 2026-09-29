"""Intent-layer coherence checks C1–C4."""

from __future__ import annotations

import unittest

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document

from optimizer.graph_hygiene.intent_checks import (
    _index,
    audit_intent_coherence,
    ladder_level,
)
from optimizer.ontology.schema import INTENT_EDGE_TYPES, is_intent_edge


def _n(nid: str, ntype: str, **props) -> Node:
    return Node(id=nid, type=ntype, properties=props)


def _r(src: Node, tgt: Node, rtype: str, **props) -> Relationship:
    return Relationship(source=src, target=tgt, type=rtype, properties=props)


def _doc(nodes: list[Node], rels: list[Relationship]) -> GraphDocument:
    return GraphDocument(
        nodes=nodes, relationships=rels, source=Document(page_content="intent-test")
    )


def _by_check(findings, check: str):
    return [f for f in findings if f.check == check]


class TestOntologyIntentIsolation(unittest.TestCase):
    def test_intent_edges_are_isolated_from_computation_set(self):
        for edge in INTENT_EDGE_TYPES:
            self.assertTrue(is_intent_edge(edge))
            self.assertFalse(is_intent_edge("AFFECTS"))


class TestIntentChecks(unittest.TestCase):
    def test_c1_flags_activity_without_intent(self):
        a = _n("A1", "Activity", label="Do thing")
        findings = _by_check(audit_intent_coherence(_doc([a], [])), "C1")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].node_ids, ("A1",))

    def test_inherited_process_intent_covers_activity(self):
        a = _n("A1", "Activity")
        p = _n("P1", "Process")
        intent = _n("INT-1", "Intent", label="Deliver on time")
        m = _n("M1", "Metric")
        doc = _doc(
            [a, p, intent, m],
            [
                _r(a, p, "PART_OF"),
                _r(p, intent, "PURSUES"),
                _r(intent, m, "SERVES"),
            ],
        )
        c1 = _by_check(audit_intent_coherence(doc), "C1")
        self.assertEqual(c1, [])
        self.assertEqual(ladder_level("A1", _index(doc)), "N3")

    def test_c4_effect_without_intent(self):
        a = _n("A1", "Activity")
        m = _n("M1", "Metric")
        findings = _by_check(
            audit_intent_coherence(_doc([a, m], [_r(a, m, "AFFECTS")])),
            "C4",
        )
        descriptions = {f.description for f in findings}
        self.assertTrue(any("no Intent that SERVES" in d for d in descriptions))
        self.assertTrue(any("nobody pursues" in d for d in descriptions))


if __name__ == "__main__":
    unittest.main()
