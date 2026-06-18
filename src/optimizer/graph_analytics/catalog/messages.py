from __future__ import annotations

from dataclasses import dataclass

from optimizer.graph_analytics.catalog.definitions import get_analytic_definition


@dataclass(frozen=True)
class ExecutiveMessages:
    discovery_text: str
    rationale_text: str


def get_executive_messages(analytic_id: str) -> ExecutiveMessages:
    definition = get_analytic_definition(analytic_id)
    return ExecutiveMessages(
        discovery_text=definition.discovery_text,
        rationale_text=definition.rationale_text,
    )
