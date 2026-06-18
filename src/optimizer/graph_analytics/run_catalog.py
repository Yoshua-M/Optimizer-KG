from __future__ import annotations

from optimizer.graph_analytics.catalog.definitions import list_analytic_ids
from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import error_finding
from optimizer.graph_analytics.runners.registry import get_runner


def run_analytic(context: GraphContext, analytic_id: str) -> AnalyticFinding:
    """Run a single catalog analytic; return structured finding or error."""
    runner = get_runner(analytic_id)
    try:
        return runner(context)
    except Exception as exc:
        return error_finding(analytic_id, str(exc))


def run_all_analytics(context: GraphContext) -> list[AnalyticFinding]:
    """Run every catalog analytic in definition order."""
    return [run_analytic(context, analytic_id) for analytic_id in list_analytic_ids()]
