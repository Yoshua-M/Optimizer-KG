from __future__ import annotations

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

_SESSION_ANALYTIC_HIGHLIGHT_KEY = "analytic_highlight_id"

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


def render_vs_merge_crossing_control() -> bool:
    """Optional §1.2 merge pass; must be read before VS discovery on the Grafo tab."""
    return st.checkbox(
        "Fusionar historias por cruce de flujos (§1.2)",
        value=False,
        key="filter_vs_merge_crossing",
        help=(
            "Segunda pasada opcional: une grupos cuyas actividades ancestras se solapan "
            "≥30%. Puede reducir el número de historias en grafos muy conectados."
        ),
    )


def render_value_streams_panel(view_model: ScenarioViewModel) -> None:
    """Summarize VS discovery and how to see it on the graph overlay."""
    discovery = view_model.value_stream_discovery
    if discovery is None:
        return

    st.markdown("### Value streams")
    st.caption(
        "Elige una historia de valor abajo (**Enfocar value stream**) para resaltar solo "
        "ese árbol y atenuar el resto del grafo. Activa capas de soporte o desperdicio según necesites."
    )

    if not discovery.trees:
        st.warning(
            "No se descubrieron historias de valor conectadas entre eventos de demanda "
            "y entrega de valor en este escenario. El overlay mostrará la clasificación "
            "por actividad, pero probablemente sin nodos amarillos (value stream)."
        )
    else:
        activity_labels = _activity_label_by_id(view_model)
        event_labels = view_model.event_label_by_id
        st.markdown(
            f"**{discovery.group_count}** historias · "
            f"**{len(discovery.vs_union)}** actividades en el VS · "
            f"**{len(discovery.backbone)}** nodos backbone"
        )
        if discovery.merge_crossing_applied:
            if discovery.initial_group_count > discovery.group_count:
                st.caption(
                    f"Fusión por cruce activa: **{discovery.initial_group_count}** grupos "
                    f"iniciales → **{discovery.group_count}** tras fusionar."
                )
            else:
                st.caption("Fusión por cruce activa (ningún grupo fusionado con umbral 30%).")
        if discovery.group_count:
            st.caption(
                f"Tamaño promedio de grupo: **{discovery.avg_group_size:.1f}** eventos por entrega "
                "(demanda/precondición + entrega). A mayor conectividad del grafo, cada grupo "
                "suele incluir más anclas sin cambiar el algoritmo."
            )
        trees_ranked = sorted(
            discovery.trees,
            key=lambda tree: (tree.total_relevance, len(tree.activity_ids)),
            reverse=True,
        )
        st.caption("Ordenadas por relevancia acumulada (suma normalizada multi-métrica).")
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
                f"- **{delivery_label}** — relevancia acum. **{tree.total_relevance:.2f}** · "
                f"{activity_count} actividades"
            )
            if anchors:
                st.markdown(f"  - Anclas: {anchors}")

        backbone_activities = [
            (activity_id, discovery.node_overlap.get(activity_id, 0))
            for activity_id in sorted(discovery.backbone)
            if activity_id in activity_labels
        ]
        if backbone_activities:
            st.markdown("**Backbone (infraestructura compartida):**")
            for activity_id, overlap in sorted(
                backbone_activities,
                key=lambda item: item[1],
                reverse=True,
            )[:5]:
                label = activity_labels.get(activity_id, activity_id)
                st.markdown(f"- {label} — en **{overlap}** historias")

    counts = {category: 0 for category in ActivityCategory}
    for category in discovery.classifications.values():
        counts[category] += 1
    summary = " · ".join(
        f"{_VS_CATEGORY_LABELS[category]}: {counts[category]}"
        for category in ActivityCategory
    )
    st.markdown(f"**Clasificación de actividades:** {summary}")


def build_graph_filter(
    view_model: ScenarioViewModel,
    *,
    merge_crossing: bool = False,
) -> GraphFilter:
    """Read graph-tab widgets and return a ``GraphFilter`` for the facade."""
    st.subheader("Filtros del grafo")

    analytic_highlight_id = st.session_state.get(_SESSION_ANALYTIC_HIGHLIGHT_KEY)
    if analytic_highlight_id:
        st.info(
            f"**Resaltado analítico activo:** `{analytic_highlight_id}`. "
            "Explicar relevancia, aislamiento y enfoque VS están deshabilitados."
        )
        if st.button("Quitar resaltado analítico", key="clear_analytic_highlight"):
            st.session_state[_SESSION_ANALYTIC_HIGHLIGHT_KEY] = None
            st.rerun()

    value_stream_focus_delivery_id = None
    value_stream_include_support = False
    value_stream_include_waste = False
    highlight_blocks_vs_focus = analytic_highlight_id is not None

    discovery = view_model.value_stream_discovery
    if discovery and discovery.trees and not highlight_blocks_vs_focus:
        focus_options = ["(ninguno)"]
        focus_ids: dict[str, str | None] = {"(ninguno)": None}
        for tree in discovery.trees:
            delivery_label = view_model.event_label_by_id.get(
                tree.delivery_event_id,
                tree.delivery_event_id,
            )
            focus_options.append(delivery_label)
            focus_ids[delivery_label] = tree.delivery_event_id

        trees_by_delivery = {t.delivery_event_id: t for t in discovery.trees}
        ranked_labels = sorted(
            focus_options[1:],
            key=lambda label: (
                trees_by_delivery[focus_ids[label]].total_relevance,
                len(trees_by_delivery[focus_ids[label]].activity_ids),
            ),
            reverse=True,
        )
        focus_options = ["(ninguno)"] + ranked_labels

        chosen_focus = st.selectbox(
            "Enfocar value stream",
            focus_options,
            key="filter_vs_focus_delivery",
        )
        value_stream_focus_delivery_id = focus_ids[chosen_focus]
        focus_enabled = value_stream_focus_delivery_id is not None

        col_support, col_waste = st.columns(2)
        with col_support:
            value_stream_include_support = st.checkbox(
                "Incluir actividades de soporte",
                value=False,
                disabled=not focus_enabled,
                key="filter_vs_include_support",
            )
        with col_waste:
            value_stream_include_waste = st.checkbox(
                "Incluir actividades de desperdicio",
                value=False,
                disabled=not focus_enabled,
                key="filter_vs_include_waste",
            )

        if focus_enabled:
            st.caption(
                "Solo el árbol de la historia seleccionada está resaltado. Marca soporte "
                "o desperdicio para ampliar el conjunto visible."
            )
    elif highlight_blocks_vs_focus:
        st.selectbox(
            "Enfocar value stream",
            ["(no disponible con resaltado analítico)"],
            disabled=True,
            key="filter_vs_focus_disabled_analytic",
        )

    selected_node_types: list[str] = []
    selected_rel_types: list[str] = []

    col_nodes, col_rels = st.columns(2)
    with col_nodes:
        st.markdown("**Tipos de nodo**")
        for node_type in view_model.available_node_types:
            if st.checkbox(node_type, value=True, key=f"filter_node_{node_type}"):
                selected_node_types.append(node_type)
    with col_rels:
        st.markdown("**Tipos de relación**")
        for rel_type in view_model.available_relationship_types:
            if st.checkbox(rel_type, value=True, key=f"filter_rel_{rel_type}"):
                selected_rel_types.append(rel_type)

    relevance_pull = st.checkbox(
        "Relevance pull (acercar actividades a métricas)",
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

    highlight_blocks_modes = analytic_highlight_id is not None

    col_explain, col_isolate = st.columns(2)
    with col_explain:
        if highlight_blocks_modes:
            st.selectbox(
                "Explicar relevancia",
                ["(no disponible con resaltado analítico)"],
                disabled=True,
                key="filter_explain_disabled_analytic",
            )
            explain_activity_id = None
        else:
            chosen_explain = st.selectbox(
                "Explicar relevancia",
                explain_options,
                key="filter_explain_activity",
            )
            explain_activity_id = explain_ids[chosen_explain]

    with col_isolate:
        if highlight_blocks_modes or explain_activity_id is not None:
            disabled_label = (
                "(no disponible con resaltado analítico)"
                if highlight_blocks_modes
                else "(no disponible con explicar activo)"
            )
            st.selectbox(
                "Aislar subgrafo",
                [disabled_label],
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
        st.info(
            f"**Explicando relevancia:** {activity_name}. "
            f"Resaltadas **{explain_metric_count[chosen_explain]} métricas** con relevancia > 0: "
            + ", ".join(metric_labels)
        )

    node_types = _selection_to_frozenset(selected_node_types, view_model.available_node_types)
    relationship_types = _selection_to_frozenset(
        selected_rel_types, view_model.available_relationship_types
    )

    return GraphFilter(
        node_types=node_types,
        relationship_types=relationship_types,
        isolation_seed_id=isolation_seed,
        relevance_pull_enabled=relevance_pull,
        explain_activity_id=explain_activity_id,
        value_stream_focus_delivery_id=value_stream_focus_delivery_id,
        value_stream_include_support=value_stream_include_support,
        value_stream_include_waste=value_stream_include_waste,
        value_stream_merge_crossing=merge_crossing,
        analytic_highlight_id=analytic_highlight_id,
    )


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
    """Plotly analytics primary; legacy tables in a collapsed expander."""
    plot_series = view_model.plot_series
    if plot_series is None:
        st.info("No hay series analíticas para este escenario.")
        _render_legacy_tables(view_model)
        return

    _render_plot_row(
        plot_series.relevance_scatter,
        plot_series.top_relevance,
        title="Relevancia agregada",
        x_label="Relevancia máxima",
        y_label="Métricas afectadas",
    )
    _render_plot_row(
        plot_series.v_scatter,
        plot_series.top_v,
        title="Valor interno (V)",
        x_label="V",
        y_label="Procesos afectados",
    )
    _render_plot_row(
        plot_series.v_relevance_scatter,
        plot_series.top_v_relevance,
        title="V × Relevancia",
        x_label="V",
        y_label="Relevancia máxima",
    )
    _render_plot_row(
        plot_series.process_scatter,
        plot_series.top_process,
        title="Procesos (rollups)",
        x_label="Suma de relevancia",
        y_label="Métricas con rollup",
    )

    contributions = _top_process_contributions(view_model)
    if contributions:
        st.subheader("Top contribuciones por proceso")
        for process_label, metric_label, pct in contributions:
            st.markdown(f"- **{process_label}** · {metric_label}: {pct:.1%}")

    with st.expander("Datos tabulares (depuración)", expanded=False):
        _render_legacy_tables(view_model)


def _render_plot_row(
    points: tuple[PlotPoint, ...],
    top_points: tuple[PlotPoint, ...],
    *,
    title: str,
    x_label: str,
    y_label: str,
) -> None:
    st.subheader(title)
    chart_col, top_col = st.columns([3, 1])
    with chart_col:
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=[point.x for point in points],
                    y=[point.y for point in points],
                    text=[point.entity_name for point in points],
                    mode="markers",
                    marker={"size": 10},
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
