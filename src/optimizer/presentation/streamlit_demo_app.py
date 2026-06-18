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
    render_value_streams_panel,
    render_vs_merge_crossing_control,
    render_value_tab,
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
    choice = st.sidebar.selectbox("Escenario", list(labels.keys()))
    scenario_id = labels[choice]

    try:
        with st.spinner("Cargando escenario…"):
            base_view_model = run_demo_scenario(scenario_id, repo_root=repo_root)
    except DemoLoadError as exc:
        st.error(str(exc))
        return

    st.markdown(base_view_model.scenario.description or "")

    activity = render_activity_sidebar(base_view_model)
    if activity is not None:
        render_activity_detail(
            activity,
            metric_label_by_id=base_view_model.metric_label_by_id,
        )

    if "analytic_highlight_id" not in st.session_state:
        st.session_state["analytic_highlight_id"] = None

    graph_tab, analytics_tab, value_tab = st.tabs(["Grafo", "Analíticas", "Valor"])
    with graph_tab:
        merge_crossing = render_vs_merge_crossing_control()
        discovery_prefilter = GraphFilter(
            node_types=None,
            relationship_types=None,
            isolation_seed_id=None,
            relevance_pull_enabled=False,
            value_stream_merge_crossing=merge_crossing,
        )
        discovery_view_model = run_demo_scenario(
            scenario_id,
            repo_root=repo_root,
            graph_filter=discovery_prefilter,
        )
        render_value_streams_panel(discovery_view_model)
        graph_filter = build_graph_filter(
            discovery_view_model,
            merge_crossing=merge_crossing,
        )
        if graph_filter.node_types is not None and len(graph_filter.node_types) == 0:
            st.info("Selecciona al menos un tipo de nodo para ver el grafo.")
        else:
            graph_view_model = run_demo_scenario(
                scenario_id,
                repo_root=repo_root,
                graph_filter=graph_filter,
            )
            st.caption("El grafo se regenera al cambiar filtros.")
            render_graph_embed(graph_view_model)
    with analytics_tab:
        render_analytics_tab(base_view_model)
    with value_tab:
        render_value_tab(base_view_model)
