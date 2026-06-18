# Changelog

All notable **approved** development shipped through the Optimizer repo (primarily via `workflows/feature_dev/`).  
Format and update rules: [`changelog_rules.md`](changelog_rules.md).

---

## 2026-06-15 — Value stream Steiner discovery (`vs_steiner`)

**Requirement:** [VS_Selection_Protocol.md](VS_Selection_Protocol.md) — delivery-anchored grouping + Steiner trees (replaces per-metric linear path discovery).

**Summary:** Replaced per-metric `all_simple_paths` value stream discovery with **one Steiner tree per economic story** (delivery-anchored event group). The Grafo tab now lists historias by **accumulated normalized relevance**, supports optional **merge-by-crossing** (§1.2), and focuses streams by **delivery event** rather than metric. Backbone overlap drives node sizing in the global VS overlay; focus mode highlights all metrics touched by the tree.

**Shipped:**

- **Domain (`graph_analytics/`):** Rewrote `discover_value_streams` — `_group_by_delivery_anchor`, optional `_merge_crossing_groups`, multi-metric normalized edge costs, `steiner_tree` per group, union/overlap/backbone. Replaced `ValueStreamResult` with `ValueStreamTree` (`total_relevance`, `node_scores`); extended `ValueStreamDiscoveryResult` (`trees`, `initial_group_count`, `merge_crossing_applied`). `ValueStreamFocus` keyed by `delivery_event_id` with multi-metric AFFECTS/HAS_DRIVER highlights.
- **Application:** `GraphFilter.value_stream_focus_delivery_id` (breaking rename from `value_stream_focus_metric_id`), `value_stream_merge_crossing`; `ScenarioViewModel.event_label_by_id` and `value_stream_merge_crossing`; VS edge width from cumulative relevance; backbone `node_size_overrides` on overlay.
- **Infrastructure (`pyvis_graph.py`):** `VisualizeOptions.node_size_overrides`, `edge_width_overrides`.
- **Presentation:** Group-centric VS panel (relevancia acumulada, sorted list, backbone summary); **Fusionar historias por cruce de flujos** checkbox; focus dropdown by delivery event label. Grafo tab reordered so discovery respects merge flag before panel render.
- **Docs:** Superseded Part 1 banner in `VS_Analytics_Module.md`; ADR [0001-vs-steiner-selection.md](decisions/0001-vs-steiner-selection.md).
- **Tests:** Rewrote `test_value_streams`; extended `vs_graph_factory` (convergence, shared-backbone); updated `test_models`, `test_run_scenario_view`; **144** unittest cases green.

**Breaking:** `ValueStreamDiscoveryResult.streams` → `trees`; `GraphFilter.value_stream_focus_metric_id` → `value_stream_focus_delivery_id`.

**Refs:** [VS_Selection_Protocol.md](VS_Selection_Protocol.md) · [0001-vs-steiner-selection.md](decisions/0001-vs-steiner-selection.md)

**Notes:** Manual smoke: `streamlit run app_demo.py` → **energoil_mexico_v2** → Grafo → toggle merge crossing → **Enfocar value stream** by delivery event. Merge crossing defaults off; energoil may show 8 groups with or without fusion depending on 30% overlap threshold.

## 2026-06-12 — Value stream focus filter (`vs_filter`)

**Requirement:** [vs_filter.md](../workflows/feature_dev/inputs/vs_filter.md) — follow-up to analitics Grafo VS overlay.

**Summary:** Replaced whole-graph VS coloring with **per-metric focus** on the Grafo tab: pick one value stream, grey out non-focus nodes, and progressively add soporte or desperdicio layers. Stream view now reads as a flow — boundary events and value-chain nodes/edges use a dedicated palette; only stream PRECEDES, metric affectations, and (when enabled) support links stay visible; all other edges are dimmed.

**Shipped:**

- **Domain (`graph_analytics/value_streams.py`):** `ValueStreamFocus` payload with per-stream classification, demand/value **boundary events**, metric **driver** ids, and `highlight_edge_keys` (main-path PRECEDES, support PRECEDES when soporte layer is on, AFFECTS, HAS_DRIVER).
- **Application (`run_scenario_view.py`):** `GraphFilter.value_stream_focus_metric_id` + soporte/desperdicio flags; grey-out via `VisualizeOptions.highlight_node_ids`; node/edge color overrides for VS focus mode.
- **Infrastructure (`pyvis_graph.py`):** VS focus palette — boundary events (gold), main flow PRECEDES (orange), support PRECEDES (blue), metrics (green), metric drivers (dark green), AFFECTS/HAS_DRIVER (green); non-highlight edges dimmed when focus is active.
- **Presentation (`scenario_views.py`):** **Enfocar value stream** dropdown (by metric name), **Incluir actividades de soporte** / **Incluir actividades de desperdicio** checkboxes (Spanish).
- **Tests:** Extended `test_value_streams`, `test_run_scenario_view`, `test_pyvis_graph_scenario`; **141** unittest cases green.

**Refs:** [vs_filter_done.md](../workflows/feature_dev/stages/04_implement/output/vs_filter_done.md) · [vs_filter_change_spec.md](../workflows/feature_dev/stages/02_spec/output/vs_filter_change_spec.md)

**Notes:** Use demo scenario **`energoil_mexico_v2`** (v1 has no discovered streams). Manual smoke: `streamlit run app_demo.py` → Grafo → Enfocar value stream → toggle soporte/desperdicio.

## 2026-06-12 — Graph analytics & Porter catalog (`analitics`)

**Requirement:** [analitics.md](../workflows/feature_dev/inputs/analitics.md) — value streams, 36 Porter-area catalog analytics, demo UI integration.

**Summary:** Shipped waves **A–G** of the analytics feature: new `graph_analytics/` domain (VS discovery, 36 Porter catalog runners, registry facade), orchestration through `run_scenario_view` into `ScenarioViewModel`, and demo UI with **Analíticas** (Spanish findings + **Visualizar en grafo**) and **Grafo** VS color overlay plus analytic highlight session.

**Shipped:**

- **Domain (`graph_analytics/`):** models, `graph_bridge`, validation, Porter catalog definitions/messages, relevance/plots migration, `value_streams` discovery, nine runner modules (G/H/T/A/LI/O/LE/MV/PV), `registry` + `run_catalog` facade.
- **Application:** Extended `GraphFilter` (`value_stream_overlay`, `analytic_highlight_id`) and `ScenarioViewModel` (VS discovery, catalog findings, color overrides, active highlight); `run_scenario_view` runs VS discovery + full catalog on every scenario load.
- **Infrastructure:** `VS_CATEGORY_COLORS`, `VisualizeOptions.node_color_overrides` in PyVis adapter.
- **Presentation:** `analytics_views.py` (Porter Área/Sub-área menu, panel-only analytics excluded from Visualizar); `scenario_views` VS overlay toggle, analytic highlight session, `render_value_streams_panel` on Grafo tab; `streamlit_demo_app.py` tabs **Grafo | Analíticas | Valor**.
- **Tests:** `tests/graph_analytics/` mirror (49 cases) + ga-11/ga-12 orchestration/PyVis contracts; **128/128** unittest cases green in full discover run.

**Waves (condensed):**

| Wave | `change_id`s | Outcome |
|------|--------------|---------|
| A–C | ga-01…ga-03, ga-15 | Scaffold, bridge/validation, full 36-entry catalog, energoil preflight |
| D | ga-04…ga-09 | Relevance/plots, VS discovery, all nine runner modules |
| E | ga-10 | Registry map + `run_analytic` / `run_all_analytics` |
| F | ga-11, ga-12 | Scenario orchestration + PyVis VS category colors |
| G | ga-13, ga-14 | Analíticas tab + Grafo overlay/highlight wiring |

**Refs:** [analitics_done.md](../workflows/feature_dev/stages/04_implement/output/analitics_done.md) · [analitics_change_spec.md](../workflows/feature_dev/stages/02_spec/output/analitics_change_spec.md) · [analitics_test_log.md](../workflows/feature_dev/stages/03_tests/output/analitics_test_log.md)

**Notes:** Production `streamlit_app.py` unchanged (demo-only wiring per spec). Manual smoke on `streamlit run app_demo.py` (energoil_mexico): three tabs, Porter menus, Visualizar → Grafo banner (e.g. A-02), VS overlay checkbox, PyVis embed; panel-only ids (HR/H-04) omit Visualizar; backend script confirms 36 findings and highlight/overlay payloads. On energoil today VS discovery returns **0 primary streams** because fixture `PRECEDES` edges are Activity→Activity silos only (no event bridges) — overlay still classifies activities but shows little yellow until fixture spine is extended.

**Follow-ups:** Extend energoil `graph.json` with demand→value `PRECEDES` paths (see `scripts/build_energoil_demo_fixtures.py`); wire production app; VS edge thickness by relevance (post-MVP).

## 2026-06-11 — Scenario UI / demo separation (post-`UI_v2` refactor)

**Requirement:** Architectural cleanup — separate **product scenario UI** from **fixture demo** data path (follows [UI_v2.md](../workflows/feature_dev/inputs/UI_v2.md) shared-module intent; no new feature-dev requirement).

**Summary:** Clarified that the Grafo/Valor UI (`scenario_views`, `run_scenario_view`) is **source-agnostic** and not demo-specific. Moved presentation view types out of `demo_models.py` into `scenario_models.py` with neutral names; `demo_models.py` now holds only fixture bundle types (`DemoScenario`, `DemoBundle`). The demo app remains a thin edge: manifest + JSON load → same `ScenarioViewModel` path production will use.

**Shipped:**

- **Application:** `MatrixDisplayRow`, `ActivityScoreDisplay`, `ActivityDisplayItem`, `MATRIX_TOP_N` on `scenario_models`; tightened `ScenarioViewModel` field types; `run_demo_scenario` returns `ScenarioViewModel` (removed `DemoViewModel` alias).
- **Presentation:** `scenario_views` imports display types from `scenario_models`; default PyVis HTML output `scenario_knowledge_graph.html`.
- **Tests:** Renamed `test_pyvis_graph_demo.py` → `test_pyvis_graph_scenario.py`; updated demo adapter tests for `ScenarioViewModel`; **73** unittest cases green in full discover run.
- **Docs:** `application/`, `presentation/`, `tests/` `AGENTS.md` and `README.md` updated to reflect demo vs product UI boundary.

**Notes:** Demo edge unchanged: `app_demo.py`, `streamlit_demo_app.py`, `demo_loader`, `configs/demo_scenarios.json`, `data/processed/demo/`. Production `streamlit_app.py` wiring to `run_scenario_view` still deferred.

## 2026-06-10 — Demo UI v2 Wave 4 (`UI_v2` continued)

**Requirement:** [UI_v2.md](../workflows/feature_dev/inputs/UI_v2.md) — batch 2: explain relevance on graph, `"punto ciego"` pull edges, labels and tooltips.

**Summary:** Completed **UI_v2** with Wave 4: activity relevance is explained on the Grafo tab via grey-out highlighting (all scored metrics, full G/J/DV paths) while keeping the full graph visible; indirect metric links render as dashed **"punto ciego"** edges when relevance pull is on. Added dedicated **Explicar relevancia** and **Aislar subgrafo** menus, human-readable process/activity labels across the demo UI, and Spanish activity factor names in graph tooltips.

**Shipped:**

- **Application:** `RelevanceHighlight`, `build_relevance_explain_paths`, `explain_activity_relevance`, `merge_explain_highlight_into_documents`, `build_indirect_relevance_map`; `GraphFilter.explain_activity_id`; `format_process_label`, `format_activity_label`; `process_label_by_id` on `ScenarioViewModel`.
- **Infrastructure:** PyVis grey-out highlight, `CustomerJourneyStep` / `MetricDriver` colors, `"punto ciego"` synthetic edges; tooltips with ids and labeled factors (Posición, Causalidad, Frecuencia, Riesgo, Valor interno).
- **Presentation:** Explain-activity selectbox with metric summary banner; isolation menu shows process names; consistent `A-26 — …` / `P-05 — …` labels in menus, plots, and sidebar.
- **Tests:** 17 batch-2 contracts + merge test; **72** total unittest cases green in full discover run.

**Refs:** [UI_v2_done.md](../workflows/feature_dev/stages/04_implement/output/UI_v2_done.md) · [UI_v2_change_spec.md](../workflows/feature_dev/stages/02_spec/output/UI_v2_change_spec.md) · [UI_v2_test_log.md](../workflows/feature_dev/stages/03_tests/output/UI_v2_test_log.md)

**Notes:** Builds on the 2026-06-05 Wave 1–3 entry below. Production `streamlit_app.py` wiring still deferred. Grey-out `VisualizeOptions` seam reusable for future graph features.

## 2026-06-05 — Demo UI v2 (`UI_v2`)

**Requirement:** [UI_v2.md](../workflows/feature_dev/inputs/UI_v2.md) — analytics-first value tab, graph filters, shared scenario modules.

**Summary:** Enhanced the fixture demo app with Streamlit-side graph filtering (node/relationship types, subgraph isolation, relevance pull), Plotly scatter analytics on the Valor tab, and shared application/presentation modules reusable when production wiring lands. Text→graph via `app.py` remains unchanged.

**Shipped:**

- **Application:** `scenario_models`, `value_insights`, `graph_filter`, `run_scenario_view`; `run_demo_scenario` delegates via `bundle_to_value_input`.
- **Infrastructure:** PyVis `VisualizeOptions`, stable type colors, activity tooltips, relevance-pull edges; `bundle_to_value_input` in `demo_loader`.
- **Presentation:** `scenario_views` (filters, Plotly plots, top-3 lists, legacy expander); `streamlit_demo_app` passes `GraphFilter` to facade; `demo_views` re-exports.
- **Deps:** `plotly>=5.18.0` in `pyproject.toml` / `requirements.txt`.
- **Tests:** 56 unittest cases (value insights, graph filter, facade, PyVis, demo loader/regression).

**Refs:** [UI_v2_done.md](../workflows/feature_dev/stages/04_implement/output/UI_v2_done.md) · [UI_v2_change_spec.md](../workflows/feature_dev/stages/02_spec/output/UI_v2_change_spec.md) · [UI_v2_test_log.md](../workflows/feature_dev/stages/03_tests/output/UI_v2_test_log.md)

**Notes:** Presentation layout validated manually (`streamlit run app_demo.py`); no Streamlit unit tests. Production `streamlit_app.py` adoption deferred to follow-up.

## 2026-06-02 — Demo scenario app (`demo`)

**Requirement:** [demo.md](../workflows/feature_dev/inputs/demo.md) — fixture-based sales demo (Energoil México v1).

**Summary:** Shipped a separate Streamlit entry for pre-built scenario demos: interactive org/value graph and value views (metrics, relevance matrix, strategic B=0 list) without LLM or API key. Text→graph via `app.py` remains unchanged.

**Shipped:**

- **Application:** `run_demo_scenario`, `DemoViewModel` and related row types; matrix top-15 per metric; B=0 exclusion.
- **Infrastructure:** `demo_loader` (manifest + JSON fixtures, `graph.json` → `GraphDocument` adapter); PyVis label/group styling for demo nodes.
- **Presentation:** `streamlit_demo_app`, `demo_views` (graph + value tabs, activity sidebar).
- **Entry:** `app_demo.py` — `streamlit run app_demo.py`.
- **Data / config:** `configs/demo_scenarios.json`, `data/processed/demo/energoil_mexico/` bundle; `scripts/build_energoil_demo_fixtures.py`.
- **Tests:** 21 unittest cases (`tests/infrastructure/test_demo_loader.py`, `test_pyvis_graph_demo.py`, `tests/application/test_run_demo_scenario.py`); minimal fixture under `tests/fixtures/demo/minimal/`.

**Refs:** [demo_done.md](../workflows/feature_dev/stages/04_implement/output/demo_done.md) · [demo_change_spec.md](../workflows/feature_dev/stages/02_spec/output/demo_change_spec.md) · [demo_test_log.md](../workflows/feature_dev/stages/03_tests/output/demo_test_log.md)

**Notes:** Demo-04 UI has no automated Streamlit tests (stage 3 halt). PyVis click→Streamlit not wired; sidebar activity picker for v1.
