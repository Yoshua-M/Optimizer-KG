import json
import unittest
from pathlib import Path

from optimizer.graph_analytics.enhanced_scoring import (
    compose_enhanced_value_input,
    compose_v,
    cross_validate_p_vs_proximity,
    normalize_corroboration,
    overall_evaluation_confidence,
    parse_enhanced_activities,
)
from optimizer.infrastructure.demo_loader import graph_json_to_graph_documents, load_demo_bundle


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestEnhancedScoring(unittest.TestCase):
    def test_compose_v_reweights_null_dimensions(self) -> None:
        # P=0.5 only → V=0.5
        self.assertAlmostEqual(compose_v(0.5, None, None, None), 0.5)
        # P=0.2, C=0.8 → (0.3*0.2 + 0.4*0.8) / 0.7
        self.assertAlmostEqual(compose_v(0.2, 0.8, None, None), (0.06 + 0.32) / 0.7, places=4)

    def test_compose_v_all_null_returns_none(self) -> None:
        self.assertIsNone(compose_v(None, None, None, None))

    def test_normalize_corroboration_saturates_at_three(self) -> None:
        self.assertAlmostEqual(normalize_corroboration(1), 1 / 3)
        self.assertAlmostEqual(normalize_corroboration(3), 1.0)
        self.assertAlmostEqual(normalize_corroboration(5), 1.0)

    def test_cross_validation_flags_divergence(self) -> None:
        activities = parse_enhanced_activities(
            {
                "activities": [
                    {
                        "activity_id": "ACT-01",
                        "activity_name": "Test",
                        "process_id": "PRO-01",
                        "p": 0.9,
                        "p_confidence": 0.75,
                    }
                ]
            }
        )
        findings = cross_validate_p_vs_proximity(activities, {"ACT-01": 0.1}, threshold=0.25)
        self.assertEqual(len(findings), 1)
        self.assertIn("ACT-01", findings[0].activity_id)

    def test_overall_evaluation_confidence(self) -> None:
        activities = parse_enhanced_activities(
            {
                "activities": [
                    {
                        "activity_id": "ACT-01",
                        "activity_name": "A",
                        "process_id": "P",
                        "p": 0.5,
                        "p_confidence": 0.8,
                        "c": 0.5,
                        "c_confidence": 0.6,
                    }
                ]
            }
        )
        score = overall_evaluation_confidence(activities)
        self.assertIsNotNone(score)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestEneroilV2Fixture(unittest.TestCase):
    def test_fixture_loads_and_composes_scores(self) -> None:
        bundle = load_demo_bundle("eneroil_real_v2", repo_root=REPO_ROOT)
        self.assertEqual(bundle.scenario.kind, "ai_enhanced")

        graph_path = REPO_ROOT / bundle.scenario.paths["graph"]
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        generated_nodes = [
            node["id"] for node in graph["nodes"] if node.get("properties", {}).get("generated")
        ]
        self.assertIn("ACT-24", generated_nodes)
        self.assertIn("MET-01", generated_nodes)

        metric_ids = {node["id"] for node in graph["nodes"] if node["type"] == "Metric"}
        self.assertEqual(metric_ids, {"MET-01", "MET-02", "MET-03"})

        result = compose_enhanced_value_input(
            bundle.graph,
            bundle.metrics,
            bundle.relevance,
            bundle.graph_documents,
        )
        self.assertGreater(len(result.value_input.activities), 0)
        self.assertIsNotNone(result.evaluation_confidence)
        self.assertTrue(any(act.v > 0 for act in result.value_input.activities))

        docs = graph_json_to_graph_documents(graph)
        self.assertGreater(len(docs[0].relationships), 100)


class TestEneroilV3Fixture(unittest.TestCase):
    def test_fixture_loads_with_paso7_feeders(self) -> None:
        bundle = load_demo_bundle("eneroil_real_v3", repo_root=REPO_ROOT)
        self.assertEqual(bundle.scenario.kind, "ai_enhanced")

        graph_path = REPO_ROOT / bundle.scenario.paths["graph"]
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        by_id = {node["id"]: node for node in graph["nodes"]}

        for aid in ("ACT-26", "ACT-27", "ACT-28", "ACT-29", "ACT-30", "ACT-31"):
            self.assertIn(aid, by_id)
            props = by_id[aid]["properties"]
            self.assertTrue(props.get("generated"))
            self.assertIn(props.get("fill_flag"), {"contested_external", "tier_bajo"})

        self.assertEqual(by_id["ACT-26"]["properties"].get("fill_flag"), "contested_external")
        self.assertEqual(by_id["ACT-30"]["properties"].get("fill_flag"), "tier_bajo")

        precedes = {
            (rel["source"], rel["target"])
            for rel in graph["relationships"]
            if rel["type"] == "PRECEDES"
        }
        self.assertIn(("ACT-28", "ACT-05"), precedes)
        self.assertIn(("ACT-30", "ACT-24"), precedes)
        self.assertIn(("ACT-22", "ACT-06"), precedes)

        performs_targets = {
            rel["target"]
            for rel in graph["relationships"]
            if rel["type"] == "PERFORMS"
        }
        self.assertNotIn("ACT-26", performs_targets)

        scored = {row["activity_id"]: row for row in bundle.relevance.get("activities", [])}
        for aid in ("ACT-24", "ACT-26", "ACT-27", "ACT-28", "ACT-29", "ACT-30", "ACT-31"):
            self.assertIn(aid, scored)
        self.assertEqual(scored["ACT-26"].get("score_flag"), "void_on_collapse")
        self.assertEqual(scored["ACT-26"].get("c_basis"), "simulated")
        self.assertEqual(scored["ACT-30"].get("score_flag"), "tier_bajo")
        self.assertNotIn("score_flag", scored["ACT-24"])

        result = compose_enhanced_value_input(
            bundle.graph,
            bundle.metrics,
            bundle.relevance,
            bundle.graph_documents,
        )
        scored_ids = {act.activity_id for act in result.value_input.activities}
        self.assertTrue({"ACT-24", "ACT-26", "ACT-31"}.issubset(scored_ids))
        self.assertGreater(len(result.value_input.activities), 0)
        self.assertIsNotNone(result.evaluation_confidence)


class TestEneroilV4ExperimentFixture(unittest.TestCase):
    def test_walkthrough_promotes_feeders_and_rewires_billing(self) -> None:
        bundle = load_demo_bundle("eneroil_real_v4_experiment", repo_root=REPO_ROOT)
        self.assertEqual(bundle.scenario.kind, "ai_enhanced")

        graph_path = REPO_ROOT / bundle.scenario.paths["graph"]
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        by_id = {node["id"]: node for node in graph["nodes"]}

        for aid in ("ACT-24", "ACT-25", "ACT-26", "ACT-27", "ACT-28", "ACT-29"):
            self.assertIn(aid, by_id)
            self.assertFalse(by_id[aid]["properties"].get("generated"))

        self.assertTrue(by_id["ACT-30"]["properties"].get("generated"))
        self.assertEqual(by_id["ACT-30"]["properties"].get("fill_flag"), "tier_bajo")
        self.assertTrue(by_id["TEA-04"]["properties"].get("external"))
        self.assertIn("TEA-10", by_id)
        self.assertIn("SYS-06", by_id)
        self.assertIn("ACT-35", by_id)
        self.assertIn("MDR-07", by_id)

        precedes = {
            (rel["source"], rel["target"])
            for rel in graph["relationships"]
            if rel["type"] == "PRECEDES"
        }
        self.assertIn(("ACT-08", "ACT-10"), precedes)
        self.assertNotIn(("ACT-25", "ACT-10"), precedes)
        self.assertIn(("ACT-24", "ACT-33"), precedes)

        performs = {
            (rel["source"], rel["target"])
            for rel in graph["relationships"]
            if rel["type"] == "PERFORMS"
        }
        self.assertIn(("TEA-10", "ACT-27"), performs)
        self.assertIn(("TEA-04", "ACT-25"), performs)

        drives = {
            (rel["source"], rel["target"])
            for rel in graph["relationships"]
            if rel["type"] == "DRIVES"
        }
        self.assertIn(("MDR-07", "MET-01"), drives)

        result = compose_enhanced_value_input(
            bundle.graph,
            bundle.metrics,
            bundle.relevance,
            bundle.graph_documents,
        )
        scored_ids = {act.activity_id for act in result.value_input.activities}
        self.assertTrue({"ACT-08", "ACT-24", "ACT-35"}.issubset(scored_ids))
        self.assertIsNotNone(result.evaluation_confidence)


class TestEneroilV4OficialFixture(unittest.TestCase):
    def test_f2_retires_external_delivery_and_extracts_bol_path(self) -> None:
        bundle = load_demo_bundle("eneroil_real_v4_oficial", repo_root=REPO_ROOT)
        self.assertEqual(bundle.scenario.kind, "ai_enhanced")

        graph_path = REPO_ROOT / bundle.scenario.paths["graph"]
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        by_id = {node["id"]: node for node in graph["nodes"]}

        self.assertNotIn("ACT-25", by_id)
        self.assertNotIn("ACT-29", by_id)
        self.assertNotIn("TEA-04", by_id)
        self.assertFalse(by_id["ACT-32"]["properties"].get("generated"))
        self.assertFalse(by_id["ACT-33"]["properties"].get("generated"))
        self.assertTrue(by_id["ACT-24"]["properties"].get("generated"))
        self.assertEqual(
            by_id["ACT-28"]["properties"].get("fill_flag"), "informal_no_documentado"
        )

        precedes = {
            (rel["source"], rel["target"])
            for rel in graph["relationships"]
            if rel["type"] == "PRECEDES"
        }
        self.assertIn(("ACT-33", "ACT-10"), precedes)
        self.assertNotIn(("ACT-25", "ACT-10"), precedes)
        self.assertIn(("ACT-24", "ACT-32"), precedes)

        performs_targets = {
            rel["target"]
            for rel in graph["relationships"]
            if rel["type"] == "PERFORMS"
        }
        self.assertNotIn("ACT-05", performs_targets)
        self.assertNotIn("ACT-32", performs_targets)
        self.assertNotIn("ACT-33", performs_targets)

        touches_targets = {
            rel["target"]
            for rel in graph["relationships"]
            if rel["type"] == "TOUCHES"
        }
        self.assertNotIn("CJS-04", touches_targets)
        rel_types = {rel["type"] for rel in graph["relationships"]}
        self.assertIn("DRIVES", rel_types)
        self.assertNotIn("HAS_DRIVER", rel_types)

        result = compose_enhanced_value_input(
            bundle.graph,
            bundle.metrics,
            bundle.relevance,
            bundle.graph_documents,
        )
        scored_ids = {act.activity_id for act in result.value_input.activities}
        self.assertTrue({"ACT-24", "ACT-28", "ACT-33"}.issubset(scored_ids))
        self.assertIsNotNone(result.evaluation_confidence)


if __name__ == "__main__":
    unittest.main()
