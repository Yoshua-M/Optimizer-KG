"""Smoke tests for Valor-tab flow HTML embed."""

from __future__ import annotations

import unittest
from pathlib import Path

from optimizer.presentation.value_stream_flow_view import (
    _STATIC_DIR,
    _VENDOR_FILES,
    _html_template,
    _vendor_script_tags,
)


class TestValueStreamFlowView(unittest.TestCase):
    def test_vendor_scripts_present(self):
        for filename in _VENDOR_FILES:
            path = _STATIC_DIR / "vendor" / filename
            self.assertTrue(path.is_file(), msg=str(path))

    def test_vendor_script_tags_non_empty(self):
        tags = _vendor_script_tags()
        self.assertIn("<script>", tags)
        self.assertIn("cytoscape", tags.lower())

    def test_template_inlines_vendor_and_keeps_payload_placeholder(self):
        template = _html_template()
        self.assertNotIn("__VENDOR_SCRIPTS__", template)
        self.assertIn("__FLOW_PAYLOAD_JSON__", template)
        self.assertIn("cytoscape.use(cytoscapeDagre)", template)


if __name__ == "__main__":
    unittest.main()
