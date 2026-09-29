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
| `streamlit_demo_app.py` | Fixture demo shell (`run_demo_app`): scenario picker (defaults to `eneroil_real_v4_oficial`), `GraphFilter` widgets → `run_demo_scenario`, Grafo / Analíticas / Valor tabs. For `kind == "structural"` scenarios (no metrics) shows an info banner and swaps Valor for `render_structural_value_tab`. |
| `scenario_views.py` | Grafo + Valor UI: sidebar expanders, VS panel, PyVis embed, Plotly plots, **Flujo de la historia** (Cytoscape flow), legacy expander; `render_structural_value_tab` (metrics-less scenarios: explanation + VS flow only). |
| `value_stream_flow_view.py` | Embeds `static/value_stream_flow.html` (Cytoscape+dagre) via `components.html`. |
| `static/value_stream_flow.html` | Self-contained interactive VS flow template (vendored Cytoscape/dagre inlined at render). Activity **join** = white border; **shared across historias** = gold SVG badge (stream count) via `background-image` — see badge customization below. |
| `static/vendor/` | Vendored `cytoscape.min.js`, `dagre.min.js`, `cytoscape-dagre.js` (CDN paths were 404). |
| `analytics_views.py` | Spanish Analíticas tab: Porter area menu, catalog findings, Visualizar → session highlight (ga-13); `structural=True` warns and marks metric-dependent analytics as unavailable. |
| `demo_views.py` | Deprecated re-exports of `scenario_views` for backward compatibility. |

**Host (not in this folder):** `app.py` → `run_app()`; `app_demo.py` → `run_demo_app()`.

## Facade

- `run_app()` — entry invoked from root `app.py`; no graph logic inside.
- `run_demo_app()` — entry invoked from root `app_demo.py`; builds `GraphFilter`, calls `run_demo_scenario`.
- `scenario_views` — `build_graph_filter`, `render_graph_type_filters`, `render_graph_view_controls`, `render_value_streams_panel`, `render_graph_embed`, `render_value_tab`, `render_structural_value_tab`, `render_value_stream_flow_section`, activity sidebar/detail; relevance heatmap + VS focus.
- `analytics_views` — `render_analytics_tab` (Porter menu, findings, Visualizar; optional `structural` flag).

## Planned / moves

| Change | Why |
|--------|-----|
| Wire `streamlit_app.py` to `run_scenario_view` + `scenario_views` | Production scenario path (follow-up requirement). |
| Move file read/decode to `ingestion/` via `application/ingest_documents` | UI should pass text or source ids, not own intake rules long term. |
| Explainability panels (PRD) | New `presentation/` views calling `application/` only. |

Keep duplicate generate/embed paths DRY inside `streamlit_app.py` when refactoring.

### Flujos de valor — badge customization (for UI/design)

The shared-historias badge is built in `static/value_stream_flow.html` as `streamCountBadgeDataUri(count)` — an **inline SVG** converted to a `data:image/svg+xml` URL and applied with Cytoscape `background-image` on the activity node (top-right corner).

**What designers can change without new libraries:**

| Approach | Custom shape? | Notes |
|----------|---------------|--------|
| Edit SVG in `streamCountBadgeDataUri` | Yes | Circle → rounded rect, star path, emoji as `<text>😀</text>`, or banana clip-path in SVG |
| Swap to PNG/SVG asset URL | Yes | `background-image: url(...)` with hosted or data-URI asset |
| Change colors/size/position | Yes | `background-width`, `background-offset-x/y`, fill/stroke in SVG |

**If you need arbitrary HTML/CSS (full freedom — literal banana image, icons, animations):**

- Add **`cytoscape-node-html-label`** (or similar) — renders real DOM on top of nodes; designer can use any HTML/CSS/icon font.
- Or **compound nodes**: small child node for badge with its own shape/image.

Current MVP intentionally avoids extra deps: one function, one SVG template, number centered in the badge.
