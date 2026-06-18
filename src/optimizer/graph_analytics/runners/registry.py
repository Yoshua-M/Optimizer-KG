from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from optimizer.graph_analytics.catalog.definitions import list_analytic_ids
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners import (
    external_logistics,
    governance,
    hr,
    internal_logistics,
    marketing,
    operations,
    postsale,
    procurement,
    tech,
)

if TYPE_CHECKING:
    from optimizer.graph_analytics.graph_bridge import GraphContext

RunnerFn = Callable[["GraphContext"], AnalyticFinding]

_REGISTRY: dict[str, RunnerFn] = {
    "G-01": governance.run_g01,
    "G-02": governance.run_g02,
    "G-03": governance.run_g03,
    "G-04": governance.run_g04,
    "H-01": hr.run_h01,
    "H-02": hr.run_h02,
    "H-03": hr.run_h03,
    "H-04": hr.run_h04,
    "T-01": tech.run_t01,
    "T-02": tech.run_t02,
    "T-03": tech.run_t03,
    "T-04": tech.run_t04,
    "A-01": procurement.run_a01,
    "A-02": procurement.run_a02,
    "A-03": procurement.run_a03,
    "A-04": procurement.run_a04,
    "LI-01": internal_logistics.run_li01,
    "LI-02": internal_logistics.run_li02,
    "LI-03": internal_logistics.run_li03,
    "O-01": operations.run_o01,
    "O-02": operations.run_o02,
    "O-03": operations.run_o03,
    "O-04": operations.run_o04,
    "LE-01": external_logistics.run_le01,
    "LE-02": external_logistics.run_le02,
    "LE-03": external_logistics.run_le03,
    "LE-04": external_logistics.run_le04,
    "MV-01": marketing.run_mv01,
    "MV-02": marketing.run_mv02,
    "MV-03": marketing.run_mv03,
    "MV-04": marketing.run_mv04,
    "PV-01": postsale.run_pv01,
    "PV-02": postsale.run_pv02,
    "PV-03": postsale.run_pv03,
    "PV-04": postsale.run_pv04,
    "PV-05": postsale.run_pv05,
}

_catalog_ids = set(list_analytic_ids())
_registry_ids = set(_REGISTRY)
if _catalog_ids != _registry_ids:
    missing = sorted(_catalog_ids - _registry_ids)
    extra = sorted(_registry_ids - _catalog_ids)
    raise RuntimeError(
        "Registry/catalog mismatch: "
        f"missing runners {missing or '—'}; extra runners {extra or '—'}"
    )


def list_registered_analytic_ids() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


def get_runner(analytic_id: str) -> RunnerFn:
    try:
        return _REGISTRY[analytic_id]
    except KeyError as exc:
        raise KeyError(f"Runner no registrado: {analytic_id}") from exc
