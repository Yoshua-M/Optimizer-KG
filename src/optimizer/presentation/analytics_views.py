from __future__ import annotations

from collections import defaultdict

import streamlit as st

from optimizer.application.scenario_models import ScenarioViewModel
from optimizer.graph_analytics.catalog.definitions import ALL_ANALYTIC_DEFINITIONS, AnalyticDefinition
from optimizer.graph_analytics.models import AnalyticFinding, AnalyticStatus

_SESSION_HIGHLIGHT_KEY = "analytic_highlight_id"


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


def _render_score_summary(finding: AnalyticFinding) -> None:
    if not finding.scores:
        return
    st.markdown("**Puntuaciones destacadas**")
    ranked = sorted(finding.scores.items(), key=lambda item: item[1], reverse=True)
    for node_id, score in ranked[:5]:
        st.markdown(f"- `{node_id}`: {score:.2f}")
    if len(ranked) > 5:
        st.caption(f"+ {len(ranked) - 5} nodos adicionales")


def render_analytics_tab(view_model: ScenarioViewModel) -> None:
    """Spanish Analíticas tab: Porter area menu, findings, Visualizar for highlightable ids."""
    st.subheader("Analíticas Porter")

    if not view_model.catalog_findings:
        st.info("No hay hallazgos de catálogo para este escenario.")
        return

    findings_by_id = {finding.analytic_id: finding for finding in view_model.catalog_findings}
    catalog = _catalog_by_area()
    areas = sorted(catalog.keys())

    col_area, col_sub = st.columns(2)
    with col_area:
        selected_area = st.selectbox("Área de la empresa", areas, key="analytics_porter_area")
    sub_areas = sorted(catalog[selected_area].keys())
    with col_sub:
        selected_sub_area = st.selectbox("Sub-área", sub_areas, key="analytics_porter_sub_area")

    definitions = catalog[selected_area][selected_sub_area]
    st.caption(
        f"{len(definitions)} analíticas en **{selected_sub_area}** "
        f"({selected_area})."
    )

    for definition in definitions:
        finding = _finding_for(findings_by_id, definition.analytic_id)
        if finding is None:
            continue
        label = f"{finding.analytic_id} — {finding.title}"
        with st.expander(label, expanded=False):
            st.markdown(finding.summary)
            if finding.detail:
                st.caption(finding.detail)
            if finding.status == AnalyticStatus.ERROR and finding.error_message:
                st.warning(finding.error_message)
            elif finding.status == AnalyticStatus.OK:
                st.success("Analítica ejecutada correctamente.")
            _render_score_summary(finding)
            if definition.highlightable:
                if st.button(
                    "Visualizar en grafo",
                    key=f"analytics_visualize_{finding.analytic_id}",
                ):
                    st.session_state[_SESSION_HIGHLIGHT_KEY] = finding.analytic_id
                    st.rerun()
                active_id = st.session_state.get(_SESSION_HIGHLIGHT_KEY)
                if active_id == finding.analytic_id:
                    st.info(
                        "Resaltado activo. Abre la pestaña **Grafo** para ver el subconjunto."
                    )
