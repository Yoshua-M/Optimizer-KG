from __future__ import annotations

from collections import defaultdict

import streamlit as st

from optimizer.application.scenario_models import ScenarioViewModel
from optimizer.graph_analytics.catalog.definitions import ALL_ANALYTIC_DEFINITIONS, AnalyticDefinition
from optimizer.graph_analytics.models import AnalyticFinding, AnalyticStatus

_SESSION_HIGHLIGHT_KEY = "analytic_highlight_id"
_GRID_COLUMNS = 2


def _catalog_by_area() -> dict[str, dict[str, list[AnalyticDefinition]]]:
    grouped: dict[str, dict[str, list[AnalyticDefinition]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for definition in ALL_ANALYTIC_DEFINITIONS:
        grouped[definition.porter_area][definition.sub_area].append(definition)
    return {
        area: {sub_area: definitions for sub_area, definitions in sub_areas.items()}
        for area, sub_areas in grouped.items()
    }


def _finding_for(
    findings_by_id: dict[str, AnalyticFinding],
    analytic_id: str,
) -> AnalyticFinding | None:
    return findings_by_id.get(analytic_id)


def _availability_notice(
    finding: AnalyticFinding | None,
    *,
    structural: bool = False,
) -> str | None:
    if finding is not None and finding.status == AnalyticStatus.ERROR:
        if structural:
            return "no disponible sin métricas de valor"
        return "currently not available"
    if structural and finding is not None and not finding.scores and not finding.summary:
        return "no disponible sin métricas de valor"
    return None


def _chunked(items: list[AnalyticDefinition], size: int) -> list[list[AnalyticDefinition]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def _render_score_summary(finding: AnalyticFinding) -> None:
    if not finding.scores:
        return
    st.markdown("**Puntuaciones destacadas**")
    ranked = sorted(finding.scores.items(), key=lambda item: item[1], reverse=True)
    for node_id, score in ranked[:5]:
        st.markdown(f"- `{node_id}`: {score:.2f}")
    if len(ranked) > 5:
        st.caption(f"+ {len(ranked) - 5} nodos adicionales")


def _render_analytic_detail(
    definition: AnalyticDefinition,
    finding: AnalyticFinding | None,
) -> None:
    st.markdown("**Qué descubre**")
    st.markdown(definition.discovery_text)
    st.markdown("**Cómo lo calculamos**")
    st.markdown(definition.rationale_text)
    st.caption(f"Biblioteca: `{definition.library}`")

    if finding is None:
        st.info("No hay resultado de ejecución para este escenario.")
        return

    st.markdown("**Resultado en este escenario**")
    st.markdown(finding.summary)
    if finding.detail:
        st.caption(finding.detail)
    if finding.status == AnalyticStatus.ERROR and finding.error_message:
        st.warning(finding.error_message)
    _render_score_summary(finding)

    if definition.highlightable:
        if st.button(
            "Visualizar en grafo",
            key=f"analytics_visualize_{definition.analytic_id}",
        ):
            st.session_state[_SESSION_HIGHLIGHT_KEY] = definition.analytic_id
            st.rerun()
        active_id = st.session_state.get(_SESSION_HIGHLIGHT_KEY)
        if active_id == definition.analytic_id:
            st.info(
                "Resaltado activo. Abre la pestaña **Grafo** para ver el subconjunto."
            )


def _render_analytic_tile(
    definition: AnalyticDefinition,
    finding: AnalyticFinding | None,
    *,
    structural: bool = False,
) -> None:
    """One catalog analytic in the grid; popover holds methodology and findings."""
    st.markdown(f"### {definition.title}")
    st.caption(definition.analytic_id)
    notice = _availability_notice(finding, structural=structural)
    if notice:
        st.markdown(f"*{notice}*")
    elif finding is not None and finding.summary:
        st.markdown(finding.summary)
    with st.popover("Metodología y resultado"):
        _render_analytic_detail(definition, finding)


def _render_analytic_grid(
    definitions: list[AnalyticDefinition],
    findings_by_id: dict[str, AnalyticFinding],
    *,
    structural: bool = False,
) -> None:
    for row in _chunked(definitions, _GRID_COLUMNS):
        columns = st.columns(_GRID_COLUMNS)
        for column, definition in zip(columns, row):
            with column:
                _render_analytic_tile(
                    definition,
                    _finding_for(findings_by_id, definition.analytic_id),
                    structural=structural,
                )
        if len(row) < _GRID_COLUMNS:
            columns[len(row)].empty()


def render_analytics_tab(
    view_model: ScenarioViewModel,
    *,
    structural: bool = False,
) -> None:
    """Spanish Analíticas tab: Porter areas in a grid with expandable catalog copy."""
    st.subheader("Analíticas Porter")
    st.caption(
        "Catálogo completo por área de la empresa. Cada tarjeta muestra el hallazgo; "
        "abre **Metodología y resultado** para la explicación y el detalle."
    )
    if structural:
        st.warning(
            "Escenario estructural sin métricas de valor: solo las analíticas "
            "puramente topológicas arrojan resultados; las que dependen de métricas "
            "o relevancia aparecen como no disponibles o con datos insuficientes."
        )

    if not view_model.catalog_findings:
        st.info("No hay hallazgos de catálogo para este escenario.")
        return

    findings_by_id = {finding.analytic_id: finding for finding in view_model.catalog_findings}
    catalog = _catalog_by_area()
    areas = sorted(catalog.keys())

    for area in areas:
        sub_areas = catalog[area]
        area_count = sum(len(definitions) for definitions in sub_areas.values())
        st.markdown(f"## {area}")
        with st.expander(f"{area_count} analíticas", expanded=True):
            for sub_area in sorted(sub_areas.keys()):
                definitions = sorted(
                    sub_areas[sub_area],
                    key=lambda item: item.analytic_id,
                )
                st.markdown(f"### {sub_area}")
                st.caption(f"{len(definitions)} analíticas en esta sub-área.")
                _render_analytic_grid(definitions, findings_by_id, structural=structural)
                st.divider()
