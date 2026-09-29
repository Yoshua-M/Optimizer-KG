"""acg-03: run_coherence_audit on any scenario id or graph.json."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from optimizer.application.run_coherence_audit import run_coherence_audit
from optimizer.infrastructure.demo_loader import resolve_repo_root


class TestRunCoherenceAudit(unittest.TestCase):
    def test_scenario_id_loads_any_manifest_fixture(self):
        text = run_coherence_audit(
            scenario_id="eneroil_real_v4_oficial",
            repo_root=resolve_repo_root(),
        )
        # Coherence-repaired fixture: Check 1 (value reachability) is clean;
        # residual topology flags and Intent coverage still appear.
        self.assertIn("Check 5", text)
        self.assertIn("ACT-18", text)
        self.assertIn("C1", text)
        self.assertNotIn("no REALIZES path", text)

    def test_graph_json_path_and_output_file(self):
        payload = {
            "nodes": [
                {"id": "A", "type": "Activity", "properties": {}},
                {"id": "B", "type": "Activity", "properties": {}},
            ],
            "relationships": [
                {"source": "A", "target": "B", "type": "PRECEDES", "properties": {}},
                {"source": "B", "target": "A", "type": "PRECEDES", "properties": {}},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            graph_path = Path(tmp) / "graph.json"
            out_path = Path(tmp) / "coherence_report.md"
            graph_path.write_text(json.dumps(payload), encoding="utf-8")
            text = run_coherence_audit(graph_json=graph_path, output_path=out_path)
            self.assertIn("Check 2", text)
            self.assertEqual(out_path.read_text(encoding="utf-8"), text)

    def test_requires_exactly_one_source(self):
        with self.assertRaises(ValueError):
            run_coherence_audit()
        with self.assertRaises(ValueError):
            run_coherence_audit(scenario_id="x", graph_json=Path("y.json"))


if __name__ == "__main__":
    unittest.main()
