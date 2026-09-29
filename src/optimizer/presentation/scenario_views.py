from __future__ import annotations

import json
from typing import Literal

import streamlit as st
import streamlit.components.v1 as components
from plotly import graph_objects as go

from optimizer.application.scenario_models import (
    ActivityDisplayItem,
    GraphFilter,
    PlotPoint,
    ScenarioViewModel,
)
from optimizer.application.value_insights import format_activity_label
from optimizer.graph_analytics.models import ActivityCategory
from optimizer.infrastructure.visualization.colors import (
    relevance_gradient_color,
    value_gradient_color,
)
from optimizer.presentation.value_stream_flow_view import render_value_stream_flow_html

_SESSION_ANALYTIC_HIGHLIGHT_KEY = "analytic_highlight_id"
_SESSION_GRAPH_FINGERPRINT_KEY = "demo_graph_generated_fingerprint"
_SESSION_LAST_SCENARIO_KEY = "demo_last_scenario_id"
_VALUE_STREAM_MERGE_CROSSING = True

_VS_CATEGORY_LABELS: dict[ActivityCategory, str] = {
    ActivityCategory.VALUE_STREAM: "Value stream (amarillo)",
    ActivityCategory.STRUCTURAL_SUPPORT: "Soporte estructural (azul)",
    ActivityCategory.SEMANTIC_SUPPORT: "Soporte semántico (azul claro)",
    ActivityCategory.WASTE: "Desperdicio (rojo)",
}


def _process_label(view_model: ScenarioViewModel, process_id: str) -> str:
    return view_model.process_label_by_id.get(process_id, process_id)


def _activity_label(activity: ActivityDisplayItem) -> str:
    return format_activity_label(activity.activity_id, activity.activity_name)


def _activity_label_by_id(view_model: ScenarioViewModel) -> dict[str, str]:
    return {
        activity.activity_id: _activity_label(activity)
        for activity in view_model.activities
    }


def graph_filter_fingerprint(scenario_id: str, graph_filter: GraphFilter) -> str:
    """Stable key for graph-affecting sidebar controls."""

    def _sorted_frozen(values: frozenset[str] | None) -> list[str] | None:
        if values is None:
            return None
        return sorted(values)

    payload = {
        "scenario_id": scenario_id,
        "node_types": _sorted_frozen(graph_filter.node_types),
        "relationship_types": _sorted_frozen(graph_filter.relationship_types),
        "isolation_seed_id": graph_filter.isolation_seed_id,
        "relevance_pull_enabled": graph_filter.relevance_pull_enabled,
        "explain_activity_id": graph_filter.explain_activity_id,
        "value_stream_focus_delivery_id": graph_filter.value_stream_focus_delivery_id,
        "value_stream_focus_is_fused": graph_filter.value_stream_focus_is_fused,
        "value_stream_include_support": graph_filter.value_stream_include_support,
        "value_stream_include_waste": graph_filter.value_stream_include_waste,
        "value_stream_merge_crossing": graph_filter.value_stream_merge_crossing,
        "analytic_highlight_id": graph_filter.analytic_highlight_id,
        "relevance_heatmap_enabled": graph_filter.relevance_heatmap_enabled,
        "confidence_heatmap_enabled": graph_filter.confidence_heatmap_enabled,
        "generated_highlight_enabled": graph_filter.generated_highlight_enabled,
        "generated_opacity": graph_filter.generated_opacity,
    }
    return json.dumps(payload, sort_keys=True)


def reset_scenario_session_state(scenario_id: str) -> None:
    """Clear graph + VS focus state when the selected scenario changes."""
    if st.session_state.get(_SESSION_LAST_SCENARIO_KEY) == scenario_id:
        return
    st.session_state[_SESSION_LAST_SCENARIO_KEY] = scenario_id
    st.session_state.pop(_SESSION_GRAPH_FINGERPRINT_KEY, None)
    st.session_state.pop("filter_vs_focus_story", None)


def render_graph_generate_button(
    scenario_id: str,
    graph_filter: GraphFilter,
) -> bool:
    """Render generate control; return True when the current filter graph should display."""
    current_fingerprint = graph_filter_fingerprint(scenario_id, graph_filter)
    generated_fingerprint = st.session_state.get(_SESSION_GRAPH_FINGERPRINT_KEY)
    graph_is_current = generated_fingerprint == current_fingerprint

    if st.button(
        "Generar grafo",
        type="primary",
        disabled=graph_is_current,
        key="demo_generate_graph",
    ):
        st.session_state[_SESSION_GRAPH_FINGERPRINT_KEY] = current_fingerprint
        st.rerun()

    if graph_is_current and generated_fingerprint is not None:
        return True

    if generated_fingerprint is not None:
        st.caption("Los controles cambiaron. Pulsa «Generar grafo» para actualizar.")
    else:
        st.caption("Pulsa «Generar grafo» para visualizar el escenario.")
    return False


def render_graph_type_filters(
    view_model: ScenarioViewModel,
) -> tuple[frozenset[str] | None, frozenset[str] | None]:
    """Sidebar multiselects for node and relationship types."""
    node_type_options = list(view_model.available_node_types)
    rel_type_options = list(view_model.available_relationship_types)

    selected_node_types = st.multiselect(
        "Tipos de nodo",
        node_type_options,
        default=node_type_options,
        key="filter_node_types_multiselect",
    )
    selected_rel_types = st.multiselect(
        "Tipos de relación",
        rel_type_options,
        default=rel_type_options,
        key="filter_rel_types_multiselect",
    )
    return (
        _selection_to_frozenset(selected_node_types, view_model.available_node_types),
        _selection_to_frozenset(selected_rel_types, view_model.available_relationship_types),
    )


def render_graph_view_controls(
    view_model: ScenarioViewModel,
) -> dict[str, object]:
    """Sidebar view-mode controls (VS focus, heatmap, explain, isolate)."""
    analytic_highlight_id = st.session_state.get(_SESSION_ANALYTIC_HIGHLIGHT_KEY)
    if analytic_highlight_id:
        st.caption(f"Resaltado analítico: `{analytic_highlight_id}`")
        if st.button("Quitar resaltado", key="clear_analytic_highlight"):
            st.session_state[_SESSION_ANALYTIC_HIGHLIGHT_KEY] = None
            st.rerun()

    highlight_blocks_modes = analytic_highlight_id is not None

    value_stream_focus_delivery_id = None
    value_stream_focus_is_fused = False
    value_stream_include_support = False
    value_stream_include_waste = False

    from optimizer.application.value_stream_flow import list_flow_story_options

    flow_options = list_flow_story_options(view_model)
    if flow_options and not highlight_blocks_modes:
        focus_options = ["(ninguno)"]
        focus_map: dict[str, tuple[str | None, bool]] = {"(ninguno)": (None, False)}
        for option in flow_options:
            focus_options.append(option.label)
            delivery_id = next(iter(option.delivery_event_ids))
            focus_map[option.label] = (delivery_id, option.is_fused)

        chosen_focus = st.selectbox(
            "Enfocar value stream",
            focus_options,
            key="filter_vs_focus_story",
        )
        value_stream_focus_delivery_id, value_stream_focus_is_fused = focus_map[
            chosen_focus
        ]
        focus_enabled = value_stream_focus_delivery_id is not None

        col_support, col_waste = st.columns(2)
        with col_support:
            value_stream_include_support = st.checkbox(
                "+ Soporte",
                value=False,
                disabled=not focus_enabled,
                key="filter_vs_include_support",
            )
        with col_waste:
            value_stream_include_waste = st.checkbox(
                "+ Desperdicio",
                value=False,
                disabled=not focus_enabled,
                key="filter_vs_include_waste",
            )
    elif highlight_blocks_modes:
        st.selectbox(
            "Enfocar value stream",
            ["(no disponible con resaltado analítico)"],
            disabled=True,
            key="filter_vs_focus_disabled",
        )
        focus_enabled = False
    else:
        focus_enabled = False

    relevance_heatmap_enabled = st.checkbox(
        "Mapa de calor de relevancia",
        value=False,
        disabled=highlight_blocks_modes or focus_enabled,
        key="filter_relevance_heatmap",
        help=(
            "Actividades coloreadas marrón (baja) → naranja (alta) por relevancia acumulada "
            "normalizada; demás nodos y aristas atenuados."
        ),
    )

    is_ai_enhanced = getattr(view_model.scenario, "kind", "value") == "ai_enhanced"
    confidence_heatmap_enabled = False
    generated_highlight_enabled = False
    generated_opacity = 0.2
    if is_ai_enhanced:
        gen_node_count = len(view_model.generated_node_ids)
        gen_edge_count = len(view_model.generated_edge_keys)
        st.caption(
            f"**{gen_node_count}** nodos generados · **{gen_edge_count}** aristas generadas. "
            f"Nodos: borde **magenta**; aristas: **naranja punteado**."
        )
        if view_model.generated_node_ids:
            labels = []
            for node_id in sorted(view_model.generated_node_ids):
                label = view_model.metric_label_by_id.get(node_id, node_id)
                if node_id.startswith("ACT-"):
                    for act in view_model.activities:
                        if act.activity_id == node_id:
                            label = f"{node_id} — {act.activity_name[:40]}"
                            break
                elif node_id in view_model.event_label_by_id:
                    label = view_model.event_label_by_id[node_id]
                elif node_id in view_model.metric_label_by_id:
                    label = f"{node_id} — {view_model.metric_label_by_id[node_id][:40]}"
                labels.append(label)
            st.markdown("**Nodos generados:** " + " · ".join(f"`{n.split(' — ')[0]}`" for n in labels))
            for line in labels:
                st.caption(line)
        if view_model.evaluation_confidence is not None:
            st.metric(
                "Confianza global de evaluación",
                f"{view_model.evaluation_confidence:.0%}",
                help=(
                    "Promedio ponderado de confianza en dimensiones P/C/F/R "
                    "de actividades puntuadas — no incluye abducciones de métricas."
                ),
            )
        confidence_heatmap_enabled = st.checkbox(
            "Mapa de confianza (rojo → azul)",
            value=False,
            disabled=highlight_blocks_modes or focus_enabled or relevance_heatmap_enabled,
            key="filter_confidence_heatmap",
            help="Colorea nodos por confianza de existencia; rojo=baja, azul=alta.",
        )
        generated_highlight_enabled = st.checkbox(
            "Opacidad completa en generados",
            value=False,
            disabled=confidence_heatmap_enabled,
            key="filter_generated_highlight",
            help="Ignora el control deslizante y muestra generados al 100%.",
        )
        generated_opacity = st.slider(
            "Opacidad de elementos generados",
            min_value=0.05,
            max_value=1.0,
            value=0.2,
            step=0.05,
            disabled=generated_highlight_enabled or confidence_heatmap_enabled,
            key="filter_generated_opacity",
            help=(
                "Baja = generados más tenues vs extraídos. "
                "Afecta nodos y aristas generados; pulsa «Generar grafo» para aplicar."
            ),
        )
        if view_model.cross_validation_findings:
            st.caption(
                f"Validación cruzada P vs proximidad "
                f"({len(view_model.cross_validation_findings)} hallazgos)"
            )
            for finding in view_model.cross_validation_findings:
                st.caption(f"• **{finding.activity_id}** — {finding.message}")

    if confidence_heatmap_enabled:
        relevance_heatmap_enabled = False

    relevance_pull = st.checkbox(
        "Relevance pull",
        value=False,
        key="filter_relevance_pull",
    )

    explain_options = ["(sin explicar)"]
    explain_ids: dict[str, str | None] = {"(sin explicar)": None}
    explain_metric_count: dict[str, int] = {}
    for activity in view_model.activities:
        scored = [
            score
            for score in activity.scores
            if (score.relevance or 0.0) > 0
        ]
        if not scored:
            continue
        label = _activity_label(activity)
        explain_options.append(label)
        explain_ids[label] = activity.activity_id
        explain_metric_count[label] = len(scored)

    isolation_options = ["(sin aislamiento)"]
    isolation_ids: dict[str, str | None] = {"(sin aislamiento)": None}
    process_ids = sorted({item.process_id for item in view_model.activities if item.process_id})
    for process_id in process_ids:
        label = f"Proceso: {_process_label(view_model, process_id)}"
        isolation_options.append(label)
        isolation_ids[label] = process_id
    for activity in view_model.activities:
        label = f"Actividad: {_activity_label(activity)}"
        isolation_options.append(label)
        isolation_ids[label] = activity.activity_id

    explain_blocked = highlight_blocks_modes or relevance_heatmap_enabled
    if explain_blocked:
        st.selectbox(
            "Explicar relevancia",
            ["(no disponible)"],
            disabled=True,
            key="filter_explain_disabled",
        )
        explain_activity_id = None
        chosen_explain = "(sin explicar)"
    else:
        chosen_explain = st.selectbox(
            "Explicar relevancia",
            explain_options,
            key="filter_explain_activity",
        )
        explain_activity_id = explain_ids[chosen_explain]

    if highlight_blocks_modes or explain_activity_id is not None or relevance_heatmap_enabled:
        st.selectbox(
            "Aislar subgrafo",
            ["(no disponible)"],
            disabled=True,
            key="filter_isolation_disabled",
        )
        isolation_seed = None
    else:
        chosen_isolate = st.selectbox(
            "Aislar subgrafo",
            isolation_options,
            key="filter_isolation",
        )
        isolation_seed = isolation_ids[chosen_isolate]

    if explain_activity_id is not None and st.session_state.get(
        _SESSION_ANALYTIC_HIGHLIGHT_KEY
    ):
        st.session_state[_SESSION_ANALYTIC_HIGHLIGHT_KEY] = None
        analytic_highlight_id = None

    if explain_activity_id is not None:
        metric_labels = [
            view_model.metric_label_by_id.get(score.metric_id, score.metric_id)
            for activity in view_model.activities
            if activity.activity_id == explain_activity_id
            for score in activity.scores
            if (score.relevance or 0.0) > 0
        ]
        activity_name = next(
            (
                _activity_label(activity)
                for activity in view_model.activities
                if activity.activity_id == explain_activity_id
            ),
            explain_activity_id,
        )
        st.caption(
            f"Explicando: {activity_name} · "
            f"{explain_metric_count[chosen_explain]} métricas: "
            + ", ".join(metric_labels)
        )

    if relevance_heatmap_enabled:
        value_stream_focus_delivery_id = None
        value_stream_focus_is_fused = False
        value_stream_include_support = False
        value_stream_include_waste = False
        confidence_heatmap_enabled = False
    elif confidence_heatmap_enabled:
        value_stream_focus_delivery_id = None
        value_stream_focus_is_fused = False
        value_stream_include_support = False
        value_stream_include_waste = False
        relevance_heatmap_enabled = False
    elif value_stream_focus_delivery_id:
        relevance_heatmap_enabled = False
        confidence_heatmap_enabled = False

    if relevance_heatmap_enabled and explain_activity_id:
        relevance_heatmap_enabled = False

    if relevance_heatmap_enabled and explain_activity_id:
        relevance_heatmap_enabled = False

    return {
        "isolation_seed_id": isolation_seed,
        "relevance_pull_enabled": relevance_pull,
        "explain_activity_id": explain_activity_id,
        "value_stream_focus_delivery_id": value_stream_focus_delivery_id,
        "value_stream_focus_is_fused": value_stream_focus_is_fused,
        "value_stream_include_support": value_stream_include_support,
        "value_stream_include_waste": value_stream_include_waste,
        "value_stream_merge_crossing": _VALUE_STREAM_MERGE_CROSSING,
        "analytic_highlight_id": analytic_highlight_id,
        "relevance_heatmap_enabled": relevance_heatmap_enabled,
        "confidence_heatmap_enabled": confidence_heatmap_enabled,
        "generated_highlight_enabled": generated_highlight_enabled,
        "generated_opacity": 1.0 if generated_highlight_enabled else generated_opacity,
    }


def build_graph_filter(
    view_model: ScenarioViewModel,
    *,
    node_types: frozenset[str] | None = None,
    relationship_types: frozenset[str] | None = None,
    view_controls: dict[str, object] | None = None,
) -> GraphFilter:
    """Compose type filters + view controls into a ``GraphFilter``."""
    if view_controls is None:
        if node_types is None and relationship_types is None:
            node_types, relationship_types = render_graph_type_filters(view_model)
        view_controls = render_graph_view_controls(view_model)
    return GraphFilter(
        node_types=node_types,
        relationship_types=relationship_types,
        **view_controls,
    )


def render_value_streams_panel(view_model: ScenarioViewModel) -> None:
    """Summarize VS discovery in sibling collapsed expanders (Streamlit disallows nesting)."""
    discovery = view_model.value_stream_discovery
    if discovery is None:
        return

    st.caption(
        "Value streams: expande las secciones abajo. Enfoca una historia o activa el "
        "**mapa de calor** en la barra lateral (Controles del grafo)."
    )

    if not discovery.trees:
        with st.expander("Value streams — aviso", expanded=False):
            st.warning(
                "No se descubrieron historias de valor conectadas entre eventos de demanda "
                "y entrega de valor en este escenario."
            )
    elif (
        discovery.merge_crossing_applied
        and discovery.initial_group_count > 0
        and discovery.initial_group_count == discovery.group_count
    ):
        with st.expander("Value streams — fusión", expanded=False):
            st.warning(
                "La fusión de historias (§1.2) está activa, pero ningún grupo compartió "
                "suficiente solape de actividades ancestras (umbral 30%) para fusionarse. "
                "Solo están disponibles las historias por entrega."
            )
    if discovery.trees:
        activity_labels = _activity_label_by_id(view_model)
        event_labels = view_model.event_label_by_id

        with st.expander("Value streams — Resumen", expanded=False):
            st.markdown(
                f"**{discovery.group_count}** historias · "
                f"**{len(discovery.vs_union)}** actividades en el VS · "
                f"**{len(discovery.backbone)}** nodos backbone"
            )
            if discovery.initial_group_count > discovery.group_count:
                st.caption(
                    f"Fusión §1.2: **{discovery.initial_group_count}** grupos "
                    f"iniciales → **{discovery.group_count}** tras fusionar."
                )
            else:
                st.caption(
                    f"Fusión §1.2 activa · **{discovery.group_count}** grupo(s) "
                    "(sin fusiones con el umbral actual)."
                )
            if discovery.group_count:
                st.caption(
                    f"Tamaño promedio de grupo: **{discovery.avg_group_size:.1f}** eventos "
                    "por entrega (demanda/precondición + entrega)."
                )

        trees_ranked = sorted(
            discovery.trees,
            key=lambda tree: (tree.total_relevance, len(tree.activity_ids)),
            reverse=True,
        )
        with st.expander("Value streams — Historias de valor", expanded=False):
            st.caption(
                "Ordenadas por relevancia acumulada (suma normalizada multi-métrica)."
            )
            for tree in trees_ranked:
                delivery_label = event_labels.get(
                    tree.delivery_event_id,
                    tree.delivery_event_id,
                )
                anchors = ", ".join(
                    event_labels.get(event_id, event_id)
                    for event_id in sorted(tree.anchor_event_ids)
                )
                activity_count = len(tree.activity_ids)
                st.markdown(
                    f"- **{delivery_label}** — relevancia acum. "
                    f"**{tree.total_relevance:.2f}** · {activity_count} actividades"
                )
                if anchors:
                    st.markdown(f"  - Anclas: {anchors}")

        backbone_activities = [
            (activity_id, discovery.node_overlap.get(activity_id, 0))
            for activity_id in sorted(discovery.backbone)
            if activity_id in activity_labels
        ]
        if backbone_activities:
            with st.expander("Value streams — Backbone", expanded=False):
                for activity_id, overlap in sorted(
                    backbone_activities,
                    key=lambda item: item[1],
                    reverse=True,
                ):
                    label = activity_labels.get(activity_id, activity_id)
                    st.markdown(f"- {label} — en **{overlap}** historias")

    counts = {category: 0 for category in ActivityCategory}
    for category in discovery.classifications.values():
        counts[category] += 1
    summary = " · ".join(
        f"{_VS_CATEGORY_LABELS[category]}: {counts[category]}"
        for category in ActivityCategory
    )
    with st.expander("Value streams — Clasificación de actividades", expanded=False):
        st.markdown(summary)


def _selection_to_frozenset(
    selected: list[str],
    available: tuple[str, ...],
) -> frozenset[str] | None:
    if not available:
        return None
    if len(selected) == len(available):
        return None
    return frozenset(selected)


def render_graph_tab(
    view_model: ScenarioViewModel,
    *,
    html_path: str = "scenario_knowledge_graph.html",
) -> None:
    """Graph filters, optional empty state, and PyVis embed (legacy single-call API)."""
    graph_filter = build_graph_filter(view_model)
    if graph_filter.node_types is not None and len(graph_filter.node_types) == 0:
        st.info("Selecciona al menos un tipo de nodo para ver el grafo.")
        return
    st.caption("El grafo se regenera al cambiar filtros (Streamlit → facade → PyVis).")
    render_graph_embed(view_model, html_path=html_path)


def render_graph_embed(
    view_model: ScenarioViewModel,
    *,
    html_path: str = "scenario_knowledge_graph.html",
) -> None:
    """Embed the PyVis graph for the loaded scenario."""
    if view_model.graph_network is None:
        st.warning("No hay grafo para mostrar.")
        return
    view_model.graph_network.save_graph(html_path)
    with open(html_path, "r", encoding="utf-8") as html_file:
        components.html(html_file.read(), height=900, scrolling=True)


def render_value_tab(view_model: ScenarioViewModel) -> None:
    """Plotly analytics primary; VS flow diagram; legacy tables in a collapsed expander."""
    plot_series = view_model.plot_series
    if plot_series is None:
        st.info("No hay series analíticas para este escenario.")
    else:
        _render_plot_row(
            plot_series.relevance_scatter,
            plot_series.top_relevance,
            title="Relevancia agregada",
            x_label="Relevancia máxima",
            y_label="Métricas afectadas",
            gradient="relevance",
            color_source="cumulative_relevance",
            view_model=view_model,
        )
        _render_plot_row(
            plot_series.v_scatter,
            plot_series.top_v,
            title="Valor interno (V)",
            x_label="V",
            y_label="Procesos afectados",
            gradient="value",
            color_source="x",
        )
        _render_plot_row(
            plot_series.v_relevance_scatter,
            plot_series.top_v_relevance,
            title="V × Relevancia",
            x_label="V",
            y_label="Relevancia máxima",
            gradient="relevance",
            color_source="cumulative_relevance",
            view_model=view_model,
        )
        _render_plot_row(
            plot_series.process_scatter,
            plot_series.top_process,
            title="Procesos (rollups)",
            x_label="Suma de relevancia",
            y_label="Métricas con rollup",
            gradient="relevance",
            color_source="x",
        )

    render_value_stream_flow_section(view_model)

    contributions = _top_process_contributions(view_model)
    if contributions:
        st.subheader("Top contribuciones por proceso")
        for process_label, metric_label, pct in contributions:
            st.markdown(f"- **{process_label}** · {metric_label}: {pct:.1%}")

    with st.expander("Datos tabulares (depuración)", expanded=False):
        _render_legacy_tables(view_model)


def render_structural_value_tab(view_model: ScenarioViewModel) -> None:
    """Valor tab for structural (no-metrics) scenarios: explanation + VS flow only."""
    st.subheader("Valor — no disponible en este escenario")
    st.markdown(
        "Este escenario es **estructural**: proviene de una extracción real sin "
        "métricas de valor cliente definidas, por lo que no existen puntajes "
        "P/C/F/R/V(A) ni relevancia B×V que graficar. Puntuar antes de definir "
        "las métricas produciría artefactos, no hallazgos."
    )
    st.markdown(
        "Cuando la investigación de cliente (JTBD) confirme las métricas de valor, "
        "este escenario podrá cuantificarse igual que los escenarios simulados."
    )
    render_value_stream_flow_section(view_model)


def render_value_stream_flow_section(view_model: ScenarioViewModel) -> None:
    """Interactive demand→delivery flow for selected value stream story."""
    from optimizer.application.value_stream_flow import (
        build_flow_graph_for_selection,
        default_flow_story_index,
        list_flow_story_options,
    )

    options = list_flow_story_options(view_model)
    if not options:
        return

    st.subheader("Flujos de valor")
    st.caption(
        "Demanda abajo, entrega arriba. **Borde blanco** = conjunción (varias entradas). "
        "**Insignia dorada con número** = actividad compartida por ese número de historias "
        "(ambos pueden aparecer a la vez). Clic en un nodo para relevancia y métricas."
    )

    labels = [option.label for option in options]
    default_index = default_flow_story_index(options)
    chosen_label = st.selectbox(
        "Flujo",
        labels,
        index=default_index,
        key="valor_vs_flow_story",
    )
    chosen = next(option for option in options if option.label == chosen_label)

    if chosen.is_fused:
        st.info(
            "Vista de historia fusionada: muestra el tronco compartido entre entregas "
            "y las conjunciones donde convergen varias rutas."
        )

    flow_graph = build_flow_graph_for_selection(view_model, chosen)
    if flow_graph is None:
        st.warning("No se pudo construir el diagrama de flujo para la selección.")
        return

    flow_opacity = 1.0
    if getattr(view_model.scenario, "kind", "value") == "ai_enhanced":
        if st.session_state.get("filter_generated_highlight"):
            flow_opacity = 1.0
        else:
            flow_opacity = float(st.session_state.get("filter_generated_opacity", 0.2))

    render_value_stream_flow_html(flow_graph, generated_opacity=flow_opacity)


def _marker_colors_for_points(
    points: tuple[PlotPoint, ...],
    *,
    gradient: Literal["relevance", "value"],
    color_source: Literal["cumulative_relevance", "x"],
    view_model: ScenarioViewModel | None = None,
) -> list[str]:
    if not points:
        return []
    if color_source == "cumulative_relevance":
        scores = (view_model.cumulative_relevance_by_activity_id if view_model else {}) or {}
        values = [float(scores.get(point.entity_id, 0.0)) for point in points]
    else:
        values = [float(point.x) for point in points]
    max_value = max(values) if values else 1.0
    max_value = max_value or 1.0
    color_fn = relevance_gradient_color if gradient == "relevance" else value_gradient_color
    return [color_fn(value / max_value) for value in values]


def _render_plot_row(
    points: tuple[PlotPoint, ...],
    top_points: tuple[PlotPoint, ...],
    *,
    title: str,
    x_label: str,
    y_label: str,
    gradient: Literal["relevance", "value"],
    color_source: Literal["cumulative_relevance", "x"],
    view_model: ScenarioViewModel | None = None,
) -> None:
    st.subheader(title)
    chart_col, top_col = st.columns([3, 1])
    marker_colors = _marker_colors_for_points(
        points,
        gradient=gradient,
        color_source=color_source,
        view_model=view_model,
    )
    with chart_col:
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=[point.x for point in points],
                    y=[point.y for point in points],
                    text=[point.entity_name for point in points],
                    mode="markers",
                    marker={"size": 10, "color": marker_colors},
                    hovertemplate="%{text}<br>%{xaxis.title.text}=%{x}<br>%{yaxis.title.text}=%{y}<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=360,
            margin={"l": 40, "r": 20, "t": 30, "b": 40},
        )
        st.plotly_chart(fig, use_container_width=True)
    with top_col:
        st.markdown("**Top 3**")
        if not top_points:
            st.caption("Sin puntos alejados del origen.")
        for point in top_points:
            st.markdown(
                f"- {point.entity_name}  \n  ({point.x:.2f}, {point.y:.2f})"
            )


def _top_process_contributions(
    view_model: ScenarioViewModel,
) -> list[tuple[str, str, float]]:
    rollups = list(view_model.process_rollups)
    if not rollups:
        return []
    ranked = sorted(
        rollups,
        key=lambda row: float(row.get("pct_contribution") or 0.0),
        reverse=True,
    )
    results: list[tuple[str, str, float]] = []
    for row in ranked[:3]:
        metric_id = str(row.get("metric_id", ""))
        metric_label = view_model.metric_label_by_id.get(metric_id, metric_id)
        results.append(
            (
                view_model.process_label_by_id.get(
                    str(row.get("process_id", "")),
                    str(row.get("process_id", "")),
                ),
                metric_label,
                float(row.get("pct_contribution") or 0.0),
            )
        )
    return results


def _render_legacy_tables(view_model: ScenarioViewModel) -> None:
    st.subheader("Métricas de valor")
    for metric in view_model.metrics:
        st.markdown(f"**{metric.name}**")
        st.markdown(f"- Definición: {metric.definition}")
        st.markdown(f"- Necesidad del cliente: {metric.client_need}")

    st.subheader("Matriz de relevancia (actividades × métricas)")
    if not view_model.matrix_rows:
        st.info("No hay datos de matriz para este escenario.")
    else:
        table = [
            {
                "Actividad": format_activity_label(row.activity_id, row.activity_name),
                "Métrica": view_model.metric_label_by_id.get(row.metric_id, row.metric_id),
                "Relevancia": row.relevance,
            }
            for row in view_model.matrix_rows
        ]
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.caption("Máximo 15 actividades por métrica; actividades B=0 estratégico excluidas.")

    if view_model.strategic_b_zero:
        st.subheader("Sin trazabilidad a valor (B=0 estratégico)")
        for entry in view_model.strategic_b_zero:
            st.markdown(f"**{format_activity_label(entry.activity_id, entry.activity_name)}**")
            st.caption(entry.b_zero_reason or "—")

    if view_model.process_rollups:
        st.subheader("Rollups por proceso (JSON)")
        st.json(list(view_model.process_rollups))


def render_activity_sidebar(view_model: ScenarioViewModel) -> ActivityDisplayItem | None:
    """Sidebar activity picker; returns the selected activity."""
    if not view_model.activities:
        return None

    labels = [_activity_label(item) for item in view_model.activities]
    choice = st.sidebar.selectbox("Actividad", labels, index=0)
    selected_id = choice.split(" — ", 1)[0]
    return next(
        (item for item in view_model.activities if item.activity_id == selected_id),
        None,
    )


def render_activity_detail(
    activity: ActivityDisplayItem,
    *,
    metric_label_by_id: dict[str, str] | None = None,
) -> None:
    """Per-metric scores for the selected activity (G/J/DV in expander)."""
    labels = metric_label_by_id or {}
    st.sidebar.markdown("### Detalle de actividad")
    st.sidebar.markdown(f"**{_activity_label(activity)}**")
    factors = (
        ("Posición", activity.p),
        ("Causalidad", activity.c),
        ("Frecuencia", activity.f),
        ("Riesgo", activity.r),
        ("Valor interno", activity.v),
    )
    if any(value is not None for _, value in factors):
        st.sidebar.caption(
            " · ".join(f"{name}: {value}" for name, value in factors if value is not None)
        )
    if activity.strategic_b_zero:
        st.sidebar.warning(
            activity.b_zero_reason or "Actividad marcada como B=0 estratégico."
        )
    if not activity.scores:
        st.sidebar.caption("Sin puntuaciones por métrica en el fixture.")
        return

    for score in activity.scores:
        metric_label = labels.get(score.metric_id, score.metric_id)
        with st.sidebar.expander(metric_label, expanded=False):
            st.write(f"Relevancia: {score.relevance}")
            st.write(f"% contribución: {score.pct_contribution}")
            st.write(f"G: {score.g} · J: {score.j} · DV: {score.dv} · B: {score.b}")
