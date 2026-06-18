from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_community.graphs.graph_document import GraphDocument


@dataclass(frozen=True)
class DemoScenario:
    id: str
    title: str
    description: str
    paths: dict[str, str]


@dataclass(frozen=True)
class DemoBundle:
    scenario: DemoScenario
    graph: dict[str, Any]
    metrics: dict[str, Any]
    relevance: dict[str, Any]
    graph_documents: list[GraphDocument]
