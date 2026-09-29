"""acg-01 / acg-02: topological coherence audit (checks 1–7)."""

from __future__ import annotations

import unittest

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document

from optimizer.graph_hygiene import audit_coherence, format_coherence_report
from optimizer.infrastructure.demo_loader import load_demo_bundle, resolve_repo_root


def _n(nid: str, ntype: str, **props) -> Node:
    return Node(id=nid, type=ntype, properties=props)


def _r(src: Node, tgt: Node, rtype: str, **props) -> Relationship:
    return Relationship(source=src, target=tgt, type=rtype, properties=props)


def _doc(nodes: list[Node], rels: list[Relationship]) -> GraphDocument:
    return GraphDocument(
        nodes=nodes, relationships=rels, source=Document(page_content="coherence-test")
    )


def _ids(findings, check: int) -> set[str]:
    out: set[str] = set()
    for finding in findings:
        if finding.check == check:
            out.update(finding.node_ids)
    return out


class TestCoherenceAudit(unittest.TestCase):
    def test_check1_flags_dead_branch_after_terminal_and_process_without_event(self):
        p1 = _n("P1", "Process")
        p2 = _n("P2", "Process")
        m1 = _n("M1", "Metric")
        m2 = _n("M2", "Metric")
        a1 = _n("A1", "Activity")
        a2 = _n("A2", "Activity")
        a3 = _n("A3", "Activity")
        ev = _n("EV", "Event", event_type="value_realization")
        doc = _doc(
            [p1, p2, m1, m2, a1, a2, a3, ev],
            [
                _r(p1, m1, "CONTRIBUTES_TO"),
                _r(p2, m2, "CONTRIBUTES_TO"),
                _r(a1, p1, "PART_OF"),
                _r(a2, p1, "PART_OF"),
                _r(a3, p1, "PART_OF"),
                _r(a1, a2, "PRECEDES"),
                _r(a2, ev, "PRECEDES"),
                _r(a2, ev, "INVOLVES_EVENT", event_role="produce"),
                _r(a2, a3, "PRECEDES"),
            ],
        )
        ids = _ids(audit_coherence(doc), 1)
        self.assertIn("A3", ids)
        self.assertIn("P2", ids)
        self.assertNotIn("A1", ids)
        self.assertNotIn("A2", ids)
        self.assertNotIn("P1", ids)

    def test_check1_skips_process_without_contributes_to(self):
        p = _n("PS", "Process")
        a = _n("AS", "Activity")
        doc = _doc([p, a], [_r(a, p, "PART_OF")])
        self.assertEqual(_ids(audit_coherence(doc), 1), set())

    def test_check2_reports_exact_cycle(self):
        a = _n("A", "Activity")
        b = _n("B", "Activity")
        findings = [
            f for f in audit_coherence(_doc([a, b], [_r(a, b, "PRECEDES"), _r(b, a, "PRECEDES")]))
            if f.check == 2
        ]
        self.assertTrue(findings)
        self.assertEqual(findings[0].severity, "error")
        self.assertEqual(set(findings[0].node_ids), {"A", "B"})

    def test_check3_orphan_event(self):
        ev = _n("E0", "Event", event_type="milestone")
        a = _n("A", "Activity")
        linked = _n("E1", "Event", event_type="demand")
        doc = _doc([ev, a, linked], [_r(a, linked, "INVOLVES_EVENT", event_role="produce")])
        self.assertEqual(_ids(audit_coherence(doc), 3), {"E0"})

    def test_check4_isolated_activity(self):
        iso = _n("ISO", "Activity")
        a = _n("A", "Activity")
        b = _n("B", "Activity")
        doc = _doc([iso, a, b], [_r(a, b, "PRECEDES")])
        self.assertEqual(_ids(audit_coherence(doc), 4), {"ISO"})

    def test_check5_fork_without_join_before_sinks(self):
        f = _n("F", "Activity")
        b = _n("B", "Activity")
        c = _n("C", "Activity")
        doc = _doc([f, b, c], [_r(f, b, "PRECEDES"), _r(f, c, "PRECEDES")])
        flagged = [x for x in audit_coherence(doc) if x.check == 5]
        self.assertTrue(flagged)
        self.assertEqual(flagged[0].severity, "revisar")
        self.assertIn("F", flagged[0].node_ids)

    def test_check5_reconverge_before_sink_is_ok(self):
        f = _n("F", "Activity")
        b = _n("B", "Activity")
        c = _n("C", "Activity")
        d = _n("D", "Activity")
        t = _n("T", "Event", event_type="value_realization")
        doc = _doc(
            [f, b, c, d, t],
            [
                _r(f, b, "PRECEDES"),
                _r(f, c, "PRECEDES"),
                _r(b, d, "PRECEDES"),
                _r(c, d, "PRECEDES"),
                _r(d, t, "PRECEDES"),
            ],
        )
        self.assertEqual(_ids(audit_coherence(doc), 5), set())

    def test_check6_edge_confidence_above_target(self):
        a = _n("A", "Activity")
        m = _n("M", "Metric", confidence=0.5)
        ok_p = _n("P", "Process", confidence=0.5)
        doc = _doc(
            [a, m, ok_p],
            [
                _r(a, m, "AFFECTS", confidence=0.9),
                _r(ok_p, m, "CONTRIBUTES_TO", confidence=0.4),
            ],
        )
        ids = _ids(audit_coherence(doc), 6)
        self.assertIn("A", ids)
        self.assertIn("M", ids)
        self.assertNotIn("P", ids)

    def test_check7_retirado_and_dangling(self):
        a = _n("A", "Activity")
        dead = _n("DEAD", "Activity", retirado=True)
        ghost = _n("GHOST", "Activity")
        doc = GraphDocument(
            nodes=[a, dead],
            relationships=[_r(a, dead, "PRECEDES"), _r(a, ghost, "PRECEDES")],
            source=Document(page_content="t"),
        )
        ids = _ids(audit_coherence(doc), 7)
        self.assertIn("DEAD", ids)
        self.assertIn("GHOST", ids)

    def test_empty_report_omits_sections(self):
        a = _n("A", "Activity")
        b = _n("B", "Activity")
        ev = _n("EV", "Event", event_type="demand")
        doc = _doc([a, b, ev], [_r(a, b, "PRECEDES"), _r(a, ev, "INVOLVES_EVENT")])
        text = format_coherence_report(audit_coherence(doc))
        self.assertNotIn("## Check", text)

    def test_report_has_finding_sections_and_does_not_mutate(self):
        a = _n("A", "Activity")
        b = _n("B", "Activity")
        doc = _doc([a, b], [_r(a, b, "PRECEDES"), _r(b, a, "PRECEDES")])
        n_rels = len(doc.relationships)
        text = format_coherence_report(audit_coherence(doc), doc)
        self.assertIn("## Check 2 — Ciclos", text)
        self.assertIn("| error |", text)
        self.assertEqual(text.count("## Check 2"), 1)
        self.assertEqual(len(doc.relationships), n_rels)


class TestEneroilCheck1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_demo_bundle(
            "eneroil_real_v4_oficial", repo_root=resolve_repo_root()
        )
        cls.doc = cls.bundle.graph_documents[0]

    def test_pre_reconnect_flags_overdue_branch_registro_and_processes(self):
        ids = _ids(audit_coherence(self.doc), 1)
        self.assertTrue(
            {"ACT-14", "ACT-15", "ACT-16", "ACT-17", "PRO-03", "PRO-05"} <= ids
        )
        self.assertNotIn("ACT-12", ids)
        self.assertNotIn("ACT-13", ids)

    def test_reconnect_clears_cobranza_activities(self):
        by_id = {n.id: n for n in self.doc.nodes}
        patched = GraphDocument(
            nodes=list(self.doc.nodes),
            relationships=list(self.doc.relationships)
            + [_r(by_id["ACT-17"], by_id["ACT-13"], "PRECEDES")],
            source=self.doc.source,
        )
        after_ids = _ids(audit_coherence(patched), 1)
        self.assertFalse({"ACT-14", "ACT-15", "ACT-16", "ACT-17"} & after_ids)
        self.assertIn("PRO-03", after_ids)
        self.assertIn("PRO-05", after_ids)


if __name__ == "__main__":
    unittest.main()
