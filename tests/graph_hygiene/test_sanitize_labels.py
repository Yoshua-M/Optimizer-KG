"""Label sanitization: evidence notes out of display names."""

from __future__ import annotations

import unittest

from langchain_community.graphs.graph_document import GraphDocument, Node
from langchain_core.documents import Document

from optimizer.graph_hygiene.sanitize_labels import (
    sanitize_graph_document,
    split_label_evidence,
)


class TestSplitLabelEvidence(unittest.TestCase):
    def test_italic_corregido_note(self):
        clean, note = split_label_evidence(
            "Confirmación de disponibilidad de producto "
            "*(corregido F2: alcance solo producto, sin logística)*"
        )
        self.assertEqual(clean, "Confirmación de disponibilidad de producto")
        self.assertIn("corregido F2", note or "")
        self.assertNotIn("corregido", clean)

    def test_parenthetical_after_markdown_strip(self):
        clean, note = split_label_evidence(
            'Generación y seguimiento de pedidos (corregido F2 — antes "Planeación")'
        )
        self.assertEqual(clean, "Generación y seguimiento de pedidos")
        self.assertIn("corregido F2", note or "")

    def test_clean_label_unchanged(self):
        clean, note = split_label_evidence("Elaboración y envío de cotización")
        self.assertEqual(clean, "Elaboración y envío de cotización")
        self.assertIsNone(note)


class TestSanitizeGraphDocument(unittest.TestCase):
    def test_moves_note_to_evidence_pointer_and_keeps_existing(self):
        node = Node(
            id="ACT-05",
            type="Activity",
            properties={
                "label": "Foo *(corregido F2: bar)*",
                "evidence_pointer": "prior quote",
            },
        )
        sanitize_graph_document(
            GraphDocument(
                nodes=[node],
                relationships=[],
                source=Document(page_content="t"),
            )
        )
        self.assertEqual(node.properties["label"], "Foo")
        self.assertIn("prior quote", node.properties["evidence_pointer"])
        self.assertIn("corregido F2", node.properties["evidence_pointer"])


if __name__ == "__main__":
    unittest.main()
