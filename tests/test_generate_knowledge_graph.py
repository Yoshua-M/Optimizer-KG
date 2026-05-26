import asyncio
import importlib
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from pyvis.network import Network


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


@pytest.fixture
def gkg():
    """Reload generate_knowledge_graph with OpenAI/LLM construction mocked."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch("generate_knowledge_graph.load_dotenv"):
            with patch("generate_knowledge_graph.ChatOpenAI", return_value=MagicMock()):
                mock_transformer = MagicMock()
                with patch(
                    "generate_knowledge_graph.LLMGraphTransformer",
                    return_value=mock_transformer,
                ):
                    import generate_knowledge_graph

                    importlib.reload(generate_knowledge_graph)
                    generate_knowledge_graph.graph_transformer = mock_transformer
                    yield generate_knowledge_graph


def test_visualize_graph_builds_network(gkg, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    graph_documents = _sample_graph_documents()

    net = gkg.visualize_graph(graph_documents)

    assert isinstance(net, Network)
    assert (tmp_path / "knowledge_graph.html").is_file()


def test_generate_knowledge_graph_pipeline(gkg, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_docs = _sample_graph_documents()

    with patch.object(gkg, "extract_graph_data", new_callable=AsyncMock) as mock_extract:
        with patch.object(gkg, "asyncio") as mock_asyncio:
            mock_extract.return_value = fake_docs
            mock_asyncio.run.return_value = fake_docs

            net = gkg.generate_knowledge_graph("sample text")

    mock_asyncio.run.assert_called_once()
    assert isinstance(net, Network)
    assert net is not None


def test_extract_graph_data_calls_transformer(gkg):
    fake_docs = _sample_graph_documents()
    gkg.graph_transformer.aconvert_to_graph_documents = AsyncMock(
        return_value=fake_docs
    )

    result = asyncio.run(gkg.extract_graph_data("sample text"))

    gkg.graph_transformer.aconvert_to_graph_documents.assert_awaited_once()
    assert result == fake_docs


@pytest.mark.integration
def test_generate_knowledge_graph_e2e():
    """End-to-end: uses OPENAI_API_KEY from .env (loaded in conftest)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set in .env")

    import generate_knowledge_graph as gkg

    sample_text = (
        "Albert Einstein was a physicist. "
        "He developed the theory of relativity."
    )

    net = gkg.generate_knowledge_graph(sample_text)

    assert net is not None
