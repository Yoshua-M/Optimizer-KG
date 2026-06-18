# presentation

## Responsibility

Own **all user-facing UI** for Optimizer phase 1: Streamlit layout, input controls, progress feedback, and embedding visualization output (e.g. PyVis HTML). Collects user actions and text, calls `application/` for capabilities, renders results. Does not implement graph extraction, merge logic, or LLM/PyVis construction.

## Boundaries

| In | Out |
|----|-----|
| `st.*` widgets, sidebar, `components.html` embed | Graph extraction/merge → `graph_building/` |
| Calling `application` facades on button/submit | Use-case step order → `application/` |
| Saving/displaying HTML produced for the session | Building PyVis network → `infrastructure/visualization/` |
| | `st.set_page_config` at host entry → root `app.py` (thin launcher only) |

**Callers:** root `app.py` (text graph), root `app_demo.py` (fixture demos). **Callees:** `application/` (`run_pyvis_graph`, `run_demo_scenario`, `run_scenario_view` via demo adapter).

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker. |
| `streamlit_app.py` | Full Streamlit UI (`run_app`): input method, generate button, spinner, save `knowledge_graph.html`, embed — delegates graph work to `run_pyvis_graph`. |
| `streamlit_demo_app.py` | Fixture demo shell (`run_demo_app`): scenario picker, `GraphFilter` widgets → `run_demo_scenario`, Grafo / Analíticas / Valor tabs. |
| `scenario_views.py` | Grafo + Valor UI: filter controls (VS focus by delivery event + soporte/desperdicio layers, analytic highlight session), group-centric VS panel (historias, backbone), PyVis embed, Plotly plots, top-3 lists, legacy expander. |
| `analytics_views.py` | Spanish Analíticas tab: Porter area menu, catalog findings, Visualizar → session highlight (ga-13). |
| `demo_views.py` | Deprecated re-exports of `scenario_views` for backward compatibility. |

**Host (not in this folder):** `app.py` → `run_app()`; `app_demo.py` → `run_demo_app()`.

## Facade

- `run_app()` — entry invoked from root `app.py`; no graph logic inside.
- `run_demo_app()` — entry invoked from root `app_demo.py`; builds `GraphFilter`, calls `run_demo_scenario`.
- `scenario_views` — `build_graph_filter`, `render_value_streams_panel`, `render_graph_embed`, `render_value_tab`, activity sidebar/detail; explain-relevance + VS overlay on Grafo tab.
- `analytics_views` — `render_analytics_tab` (Porter menu, findings, Visualizar).

## Planned / moves

| Change | Why |
|--------|-----|
| Wire `streamlit_app.py` to `run_scenario_view` + `scenario_views` | Production scenario path (follow-up requirement). |
| Move file read/decode to `ingestion/` via `application/ingest_documents` | UI should pass text or source ids, not own intake rules long term. |
| Explainability panels (PRD) | New `presentation/` views calling `application/` only. |

Keep duplicate generate/embed paths DRY inside `streamlit_app.py` when refactoring.
