# application

## Responsibility

Own **product use cases**: define the ordered steps for a user-visible capability and invoke domain + infrastructure through their facades. Decides *when* things run and *what* is passed between steps; does not implement extraction rules, UI, or vendor SDKs.

## Boundaries

| In | Out |
|----|-----|
| Orchestration of one capability per file | `streamlit` / layout → `presentation/` |
| Async/sync glue between domain calls | LangChain/OpenAI setup → `infrastructure/llm_client/` |
| Return values for UI/CLI (e.g. PyVis `Network`) | PyVis node/edge logic → `infrastructure/visualization/` |
| | Entity/relationship extraction → `graph_building/` |

**Callers:** `presentation/`, future `cli.py`. **Callees:** `graph_building/`, `infrastructure/`, `graph_hygiene/`, later `ingestion/`, `experiments/`, etc.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker; keep empty of logic. |
| `run_pyvis_graph.py` | Single use case “text → viewable org graph”: runs extraction then visualization in sequence without knowing LLM or PyVis internals. |
| `demo_models.py` | Fixture bundle types only (`DemoScenario`, `DemoBundle`). |
| `scenario_models.py` | Shared scenario types: `ValueScenarioInput`, display rows (`MatrixDisplayRow`, `ActivityDisplayItem`, …), `GraphFilter`, `ScenarioViewModel`; analytics fields (`value_stream_discovery`, `catalog_findings`, `vs_color_overrides`, `active_analytic_highlight`); VS focus filter fields (`value_stream_focus_delivery_id`, layer flags); `relevance_heatmap_enabled`; `event_label_by_id`. |
| `value_insights.py` | Re-export shim to `graph_analytics.relevance` / `plots` (ga-04); callers unchanged. |
| `graph_filter.py` | `GraphDocument` type filters, subgraph isolation, `explain_activity_relevance`. |
| `run_scenario_view.py` | Unified scenario facade: VS discovery + catalog run → filter → PyVis → insights → `ScenarioViewModel`. |
| `value_stream_flow.py` | `build_flow_graph_for_selection(view_model, delivery_event_ids)` for Valor-tab Cytoscape flow. |
| `run_demo_scenario.py` | Fixture load → `ValueScenarioInput` → delegate `run_scenario_view`; no LLM. |
| `run_coherence_audit.py` | Load any demo scenario id or `graph.json` → optional label sanitize → `audit_coherence` → markdown (stdout or `-o`). Read-only aside from sanitize. |
| `run_coherence_protocol.py` | CoherenceCheckProtocol cycle: C1–C14 + R1/R2/R6 (+ R3 if `--authorize-ontology`) + Salidas report; optional `--repaired-graph`. |

## Facade

- `run_pyvis_graph(text) → Network` — production path for the Streamlit app; only public orchestration entry for graph viewing today.
- `run_scenario_view(graph_documents, value_input, graph_filter=None, …) → ScenarioViewModel` — shared orchestration for demo + production UIs.
- `run_demo_scenario(scenario_id, *, repo_root=None, graph_filter=None) → ScenarioViewModel` — thin fixture adapter over `run_scenario_view`.
- `run_coherence_audit(scenario_id=… | graph_json=…, output_path=None, sanitize_labels=True) → str` — fixture-agnostic coherence report; strips evidence notes from labels by default.
- `run_coherence_protocol(scenario_id=… | graph_json=…, output_path=None, repaired_graph_path=None, authorize_ontology=False) → str` — full CoherenceCheckProtocol cycle (topology auto; ontology gated).
- `value_stream_flow.build_flow_graph_for_selection` — Valor-tab flow payload from `FlowStoryOption`.
- `value_stream_flow.list_flow_story_options` — fused stories first, then per-delivery options.
- `value_insights` — `build_plot_series`, `build_top_contributions`, `format_metric_label`, `format_process_label`, `format_activity_label`, `build_edge_relevance_map`, `build_indirect_relevance_map`, `build_relevance_explain_paths`, `top_n_by_distance` on `ValueScenarioInput`.
- `graph_filter` — `filter_graph_document`, `isolate_subgraph`, `explain_activity_relevance`, `merge_explain_highlight_into_documents`, `list_node_types`, `list_relationship_types`.

## Planned files (same module, same rules)

| File | Why it would live here |
|------|-------------------------|
| `run_experiment.py` | Orchestrate an experiments spike + optional preview, not production graph policy. |
| `ingest_documents.py` | Orchestrate intake then hand off to domains (calls `ingestion/` then downstream). |
| `run_client_value_analysis.py` | Orchestrate client-value domain after intake. |
| `run_hygiene_pass.py` | Orchestrate hygiene on an existing graph document. |
| `run_value_linkage.py` | Orchestrate linkage/ranking use case. |

New capability → new `run_<capability>.py`; keep each file one story, thin delegates.
