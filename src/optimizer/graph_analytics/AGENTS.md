# graph_analytics

## Responsibility

Own **graph-native analytics** for Optimizer: value stream discovery, Porter-area catalog runners, NetworkX (and companion library) integrations, and migrated relevance/plot calculations. Produces domain findings and highlight payloads for orchestration and UI; does not render Streamlit or PyVis.

## Boundaries

| In | Out |
|----|-----|
| Catalog metadata and Spanish executive copy | Streamlit layout → `presentation/` |
| `GraphContext` adapter from `GraphDocument` + scores | Scenario orchestration → `application/` |
| Value stream discovery, activity classification, analytic runners | PyVis rendering → `infrastructure/visualization/` |
| Preflight warnings and runner error messages | LLM extraction → `graph_building/` |

**Callers:** `application/run_scenario_view.py` (planned), `application/value_insights.py` (migration target). **Callees:** `application/scenario_models` types for score input only — no import of `presentation/` or Streamlit.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Public facade exports for domain types and `build_graph_context`. |
| `models.py` | Frozen domain types: `AnalyticFinding`, `HighlightPayload`, VS results, enums. |
| `graph_bridge.py` | Adapter: LangChain graph + `ValueScenarioInput` → NetworkX `GraphContext`. |
| `validation.py` | Preflight warnings; Spanish `analytic_error_message` helper. |
| `catalog/definitions.py` | 36 Porter analytic definitions (generated from product doc). |
| `catalog/messages.py` | `get_executive_messages` for UI copy. |
| `relevance.py` | Edge/indirect relevance maps, explain paths, `top_n_by_distance` (ga-04). |
| `plots.py` | Plot series, labels, top contributions (ga-04). |
| `value_streams.py` | VS Steiner discovery (`discover_value_streams`) + four-way activity classification (ga-05); per-group focus payload (`build_value_stream_focus`, vs_filter). See `docs/VS_Selection_Protocol.md`. |
| `runners/_common.py` | Shared runner helpers (paths, scores, findings). |
| `runners/governance.py` | G-01…G-04 runners (ga-06). |
| `runners/hr.py` | H-01…H-04 runners (ga-06). |
| `runners/tech.py` | T-01…T-04 runners (ga-07). |
| `runners/procurement.py` | A-01…A-04 runners (ga-07). |
| `runners/internal_logistics.py` | LI-01…LI-03 runners (ga-08). |
| `runners/operations.py` | O-01…O-04 runners (ga-08). |
| `runners/external_logistics.py` | LE-01…LE-04 runners (ga-09). |
| `runners/marketing.py` | MV-01…MV-04 runners (ga-09). |
| `runners/postsale.py` | PV-01…PV-05 runners (ga-09). |
| `runners/registry.py` | Map analytic id → runner callable (ga-10). |
| `run_catalog.py` | Run one / all catalog analytics (ga-10). |

## Facades

- `build_graph_context(documents, value_input) → GraphContext`
- `preflight_graph(context) → PreflightResult`
- `get_analytic_definition(analytic_id) → AnalyticDefinition`
- `list_analytic_ids() → tuple[str, …]`
- `get_executive_messages(analytic_id) → ExecutiveMessages`
- `relevance.build_edge_relevance_map`, `build_indirect_relevance_map`, `build_relevance_explain_paths`
- `plots.build_plot_series`, `build_top_contributions`, `format_*_label`
- `discover_value_streams(context, …) → ValueStreamDiscoveryResult` (delivery-anchored groups, Steiner trees, backbone/overlap)
- `build_value_stream_focus(context, discovery, delivery_event_id, …) → ValueStreamFocus | None`
- `runners.registry.get_runner`, `list_registered_analytic_ids`
- `run_catalog.run_analytic`, `run_all_analytics`

Update this file when adding runners or public entrypoints.
