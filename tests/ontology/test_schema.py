"""Ontology v2.2 Intent schema vocabulary."""

from __future__ import annotations

import unittest

from optimizer.ontology import (
    COMPUTATION_EDGE_TYPES,
    INTENT_EDGE_TYPES,
    NODE_TYPES,
    is_computation_edge,
    is_intent_edge,
)


class TestOntologySchema(unittest.TestCase):
    def test_intent_node_and_edges_present(self):
        self.assertIn("Intent", NODE_TYPES)
        self.assertEqual(
            INTENT_EDGE_TYPES,
            frozenset({"PURSUES", "SERVES", "CONFLICTS_WITH", "PROMOTED_TO"}),
        )

    def test_intent_edges_not_in_computation_set(self):
        self.assertTrue(INTENT_EDGE_TYPES.isdisjoint(COMPUTATION_EDGE_TYPES))
        self.assertTrue(is_intent_edge("PURSUES"))
        self.assertTrue(is_computation_edge("AFFECTS"))
        self.assertFalse(is_computation_edge("PURSUES"))


if __name__ == "__main__":
    unittest.main()
