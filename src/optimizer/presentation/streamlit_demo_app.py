import streamlit as st

from optimizer.application.scenario_models import GraphFilter
from optimizer.application.run_demo_scenario import run_demo_scenario
from optimizer.infrastructure.demo_loader import (
    DemoLoadError,
    load_manifest,
    resolve_repo_root,
)
from optimizer.presentation.analytics_views import render_analytics_tab
from optimizer.presentation.scenario_views import (
    build_graph_filter,
    render_activity_detail,
    render_activity_sidebar,
    render_graph_embed,
    render_graph_generate_button,
    render_graph_type_filters,
    render_graph_view_controls,
    render_structural_value_tab,
    render_value_streams_panel,
    render_value_tab,
    reset_scenario_session_state,
)


def run_demo_app() -> None:
    """Fixture-based sales demo: scenario picker, graph + value tabs."""
    st.title("Optimizer — Demo de escenarios")

    try:
        repo_root = resolve_repo_root()
        scenarios = load_manifest(repo_root=repo_root)
    except DemoLoadError as exc:
        st.error(str(exc))
        st.info(
            "Registra escenarios en `configs/demo_scenarios.json` y coloca los JSON "
            "en `data/processed/demo/<id>/`."
        )
        return

    if not scenarios:
        st.warning("No hay escenarios registrados en el manifiesto.")
        return

    labels = {f"{s.title} ({s.id})": s.id for s in scenarios}
    label_list = list(labels.keys())
    default_id = "eneroil_real_v4_oficial"
    default_index = next(
        (i for i, lab in enumerate(label_list) if labels[lab] == default_id),
        len(label_list) - 1,
    )
    choice = st.sidebar.selectbox(
        "Escenario",
        label_list,
        index=default_index,
    )
    scenario_id = labels[choice]
    reset_scenario_session_state(scenario_id)

    try:
        with st.spinner("Cargando escenario…"):
            base_view_model = run_demo_scenario(scenario_id, repo_root=repo_root)
    except DemoLoadError as exc:
        st.error(str(exc))
        return

    if "analytic_highlight_id" not in st.session_state:
        st.session_state["analytic_highlight_id"] = None

    with st.sidebar.expander("Controles del grafo", expanded=False):
        discovery_prefilter = GraphFilter(
            node_types=None,
            relationship_types=None,
            isolation_seed_id=None,
            relevance_pull_enabled=False,
            value_stream_merge_crossing=True,
        )
        discovery_view_model = run_demo_scenario(
            scenario_id,
            repo_root=repo_root,
            graph_filter=discovery_prefilter,
        )
        view_controls = render_graph_view_controls(discovery_view_model)

    with st.sidebar.expander("Tipos en el grafo", expanded=False):
        node_types, relationship_types = render_graph_type_filters(discovery_view_model)

    graph_filter = build_graph_filter(
        discovery_view_model,
        node_types=node_types,
        relationship_types=relationship_types,
        view_controls=view_controls,
    )

    st.markdown(base_view_model.scenario.description or "")

    is_structural = getattr(base_view_model.scenario, "kind", "value") == "structural"
    is_ai_enhanced = getattr(base_view_model.scenario, "kind", "value") == "ai_enhanced"
    if is_structural:
        st.info(
            "**Escenario estructural (experimental).** Datos reales sin métricas de "
            "valor cliente definidas: no hay nodos Metric ni puntajes P/C/F/R/V. "
            "Las funciones de relevancia y valor quedan deshabilitadas hasta "
            "definir las métricas (investigación JTBD pendiente)."
        )
    elif is_ai_enhanced:
        st.warning(
            "**Escenario AI enhanced (experimental).** Incluye nodos/aristas **generados** "
            "para cerrar brechas ontológicas (opacidad reducida por defecto). "
            "Métricas MET-01..03 son abducciones pendientes de validación JTBD. "
            "V(A) y analíticas Fase-2 se computan al cargar — revise confianza en "
            "Controles del grafo."
        )

    activity = render_activity_sidebar(base_view_model)
    if activity is not None:
        render_activity_detail(
            activity,
            metric_label_by_id=base_view_model.metric_label_by_id,
        )

    graph_tab, analytics_tab, value_tab = st.tabs(["Grafo", "Analíticas", "Valor"])
    with graph_tab:
        render_value_streams_panel(discovery_view_model)
        if graph_filter.node_types is not None and len(graph_filter.node_types) == 0:
            st.info("Selecciona al menos un tipo de nodo para ver el grafo.")
        elif render_graph_generate_button(scenario_id, graph_filter):
            graph_view_model = run_demo_scenario(
                scenario_id,
                repo_root=repo_root,
                graph_filter=graph_filter,
            )
            render_graph_embed(graph_view_model)
    with analytics_tab:
        render_analytics_tab(base_view_model, structural=is_structural)
    with value_tab:
        if is_structural:
            render_structural_value_tab(base_view_model)
        else:
            render_value_tab(base_view_model)
