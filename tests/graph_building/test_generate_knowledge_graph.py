"""
Regression tests for graph_building pipeline (post-migration).

Run from project root:
    python3 -m unittest discover -s tests -p "test_*.py" -v

Integration tests require OPENAI_API_KEY in .env (skipped otherwise).
"""

from __future__ import annotations

import asyncio
import importlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from pyvis.network import Network

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# optimizer is importable after: pip install -e . (see pyproject.toml)

# Load .env before integration skip checks (skipUnless runs at class definition time).
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")


def _sample_graph_documents():
    node_a = Node(id="Alice", type="Person")
    node_b = Node(id="Acme Corp", type="Organization")
    rel = Relationship(
        source=node_a,
        target=node_b,
        type="WORKS_AT",
    )
    return [
        GraphDocument(
            nodes=[node_a, node_b],
            relationships=[rel],
            source=Document(page_content="Alice works at Acme Corp."),
        )
    ]


def _load_modules_mocked():
    """Import optimizer modules with OpenAI/LLM construction mocked."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
        with patch(
            "optimizer.infrastructure.llm_client.graph_transformer.load_dotenv"
        ):
            with patch(
                "optimizer.infrastructure.llm_client.graph_transformer.ChatOpenAI",
                return_value=MagicMock(),
            ):
                mock_transformer = MagicMock()
                with patch(
                    "optimizer.infrastructure.llm_client.graph_transformer.LLMGraphTransformer",
                    return_value=mock_transformer,
                ):
                    import optimizer.application.run_pyvis_graph as run_pyvis_graph
                    import optimizer.graph_building.extraction as extraction
                    import optimizer.infrastructure.visualization.pyvis_graph as pyvis_graph

                    importlib.reload(extraction)
                    importlib.reload(pyvis_graph)
                    importlib.reload(run_pyvis_graph)

                    extraction.graph_transformer = mock_transformer
                    return extraction, pyvis_graph, run_pyvis_graph, mock_transformer


class _TempCwdTestCase(unittest.TestCase):
    """Run test body with cwd in a temporary directory."""

    def setUp(self):
        super().setUp()
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self._prev_cwd = os.getcwd()
        os.chdir(self._tmpdir.name)
        self.addCleanup(os.chdir, self._prev_cwd)


class TestVisualizeGraph(_TempCwdTestCase):
    def setUp(self):
        super().setUp()
        _, self.pyvis_graph, _, _ = _load_modules_mocked()

    def test_visualize_graph_builds_network(self):
        graph_documents = _sample_graph_documents()

        net = self.pyvis_graph.visualize_graph(graph_documents)

        self.assertIsInstance(net, Network)
        self.assertTrue(Path("knowledge_graph.html").is_file())


class TestGenerateKnowledgeGraphPipeline(_TempCwdTestCase):
    def setUp(self):
        super().setUp()
        _, _, self.run_pyvis_graph, _ = _load_modules_mocked()

    def test_generate_knowledge_graph_pipeline(self):
        fake_docs = _sample_graph_documents()

        with patch.object(self.run_pyvis_graph, "asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = fake_docs

            net = self.run_pyvis_graph.run_pyvis_graph("sample text")

        mock_asyncio.run.assert_called_once()
        self.assertIsInstance(net, Network)
        self.assertIsNotNone(net)


class TestExtractGraphData(unittest.TestCase):
    def setUp(self):
        self.extraction, _, _, self.mock_transformer = _load_modules_mocked()

    def test_extract_graph_data_calls_transformer(self):
        fake_docs = _sample_graph_documents()
        self.mock_transformer.aconvert_to_graph_documents = AsyncMock(
            return_value=fake_docs
        )
        self.extraction.graph_transformer = self.mock_transformer

        result = asyncio.run(self.extraction.extract_graph_data("sample text"))

        self.mock_transformer.aconvert_to_graph_documents.assert_awaited_once()
        self.assertEqual(result, fake_docs)


def _load_run_pyvis_for_integration():
    import optimizer.application.run_pyvis_graph as run_pyvis_graph
    import optimizer.graph_building.extraction as extraction
    import optimizer.infrastructure.llm_client.graph_transformer as gt_module

    importlib.reload(gt_module)
    importlib.reload(extraction)
    importlib.reload(run_pyvis_graph)
    return run_pyvis_graph


@unittest.skipUnless(
    os.getenv("OPENAI_API_KEY"),
    "OPENAI_API_KEY not set in .env",
)
class TestGenerateKnowledgeGraphIntegration(unittest.TestCase):
    """End-to-end: calls OpenAI (requires OPENAI_API_KEY in .env)."""

    def test_generate_knowledge_graph_e2e(self):
        run_pyvis_graph = _load_run_pyvis_for_integration()
        sample_text = (
            "Albert Einstein was a physicist. "
            "He developed the theory of relativity."
        )

        net = run_pyvis_graph.run_pyvis_graph(sample_text)

        self.assertIsNotNone(net)


if __name__ == "__main__":
    unittest.main()
