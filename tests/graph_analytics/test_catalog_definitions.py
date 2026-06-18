"""
Tests for ga-03-catalog-definitions: full Porter catalog metadata + Spanish copy.

Run: python3 -m unittest tests.graph_analytics.test_catalog_definitions -v
"""

from __future__ import annotations

import unittest

from tests.graph_analytics.test_models import (
    EXPECTED_ANALYTIC_IDS,
    PANEL_ONLY_ANALYTIC_IDS,
)


class TestCatalogDefinitions(unittest.TestCase):
    """ga-03: static catalog mirrors docs/Optimizer_Analiticas_por_Area_Porter.md."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.catalog.definitions import (
            ALL_ANALYTIC_DEFINITIONS,
            get_analytic_definition,
            list_analytic_ids,
        )
        from optimizer.graph_analytics.catalog.messages import get_executive_messages

        cls.ALL_ANALYTIC_DEFINITIONS = ALL_ANALYTIC_DEFINITIONS
        cls.get_analytic_definition = staticmethod(get_analytic_definition)
        cls.list_analytic_ids = staticmethod(list_analytic_ids)
        cls.get_executive_messages = staticmethod(get_executive_messages)

    def test_lists_all_thirty_six_analytic_ids(self):
        ids = self.list_analytic_ids()
        self.assertEqual(len(ids), 36)
        self.assertEqual(tuple(sorted(ids)), tuple(sorted(EXPECTED_ANALYTIC_IDS)))

    def test_each_definition_has_area_subarea_and_library(self):
        for analytic_id in EXPECTED_ANALYTIC_IDS:
            definition = self.get_analytic_definition(analytic_id)
            self.assertEqual(definition.analytic_id, analytic_id)
            self.assertTrue(definition.porter_area)
            self.assertTrue(definition.sub_area)
            self.assertTrue(definition.library)

    def test_panel_only_analytics_not_highlightable(self):
        for analytic_id in PANEL_ONLY_ANALYTIC_IDS:
            definition = self.get_analytic_definition(analytic_id)
            self.assertFalse(
                definition.highlightable,
                f"{analytic_id} should be panel-only per D12",
            )

    def test_highlightable_analytics_majority(self):
        highlightable = [
            d.analytic_id
            for d in self.ALL_ANALYTIC_DEFINITIONS
            if d.highlightable
        ]
        self.assertGreaterEqual(len(highlightable), 30)

    def test_executive_messages_in_spanish_non_empty(self):
        for analytic_id in EXPECTED_ANALYTIC_IDS:
            messages = self.get_executive_messages(analytic_id)
            self.assertTrue(messages.discovery_text)
            self.assertTrue(messages.rationale_text)
            combined = messages.discovery_text + messages.rationale_text
            self.assertRegex(
                combined,
                r"[áéíóúñÁÉÍÓÚÑ]|Qué descubrimos|Por qué funciona",
                msg=f"{analytic_id} should use Spanish executive copy",
            )


if __name__ == "__main__":
    unittest.main()
