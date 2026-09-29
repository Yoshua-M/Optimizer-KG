# tests

## Responsibility

Hold **automated regression tests** that mirror `src/optimizer/` module boundaries. Each test file proves behavior of the matching package module’s public facades; tests do not implement product logic.

## Boundaries

| In | Out |
|----|-----|
| `unittest` modules named `test_*.py` | Application/domain implementation → `src/optimizer/` |
| Mocks of LLM, filesystem, Streamlit where needed | Long fixtures of real client data → `data/` (reference paths only) |
| One test package folder per source module | pytest-only layout (legacy `pytest.ini` deprecated for this repo) |

**Layout rule:** `tests/<module>/` corresponds to `src/optimizer/<module>/`. New code in a module → add or extend tests in the matching folder.

**Before editing tests or the code they cover,** read `docs/Protocols/GENERATION-SIGNALS (1).md` (also required from root `AGENTS.md`).

## Subdirs — why here

| Path | Why it exists |
|------|----------------|
| `graph_building/` | Production extract/visualize path. |
| `graph_analytics/` | TDD tests for `analitics` requirement; blocked until domain module ships. |
| `infrastructure/` | Demo loader + PyVis scenario rendering tests (`test_demo_loader.py`, `test_pyvis_graph_scenario.py`). |
| `application/` | Demo facade tests (`test_run_demo_scenario.py`). |
| `presentation/` | Reserved mirror for UI wiring tests. |
| `fixtures/demo/minimal/` | Tiny scenario bundle for loader tests (graph, metrics, relevance JSON). |
| `graph_hygiene/` | Coherence audit tests (`test_coherence.py`). |
| `ingestion/`, `client_value/`, `experiments/`, `value_linkage/`, `ontology/` | Empty mirrors until those modules gain behavior. |
| `__init__.py` (root and packages) | Makes discovery packages importable under `tests/`. |

## Files (live)

| File | Why it lives here |
|------|-------------------|
| `graph_building/test_generate_knowledge_graph.py` | Locks post-migration behavior: mocked extraction, PyVis output, optional live OpenAI integration (`OPENAI_API_KEY` in `.env`; `load_dotenv` before skip checks). |
| `infrastructure/test_demo_loader.py` | Demo manifest load, bundle validation, `graph.json` → `GraphDocument` adapter (FR-7, FR-8). |
| `infrastructure/test_pyvis_graph_scenario.py` | Scenario PyVis labels, UI_v2 colors/tooltips/relevance pull, grey-out + punto ciego; **analitics** VS color overrides (ga-12). |
| `graph_hygiene/test_coherence.py` | Checks 1–7 on tiny graphs + Eneroil Check 1 AC. |
| `graph_hygiene/test_sanitize_labels.py` | Evidence notes stripped from labels into `evidence_pointer`. |
| `graph_hygiene/test_intent_checks.py` | Protocol C1–C4 Intent coverage / ladder / alignment. |
| `graph_hygiene/test_protocol_cycle.py` | R1/R2 cycle assigns Intent + SERVES. |
| `ontology/test_schema.py` | Ontology v2.2 Intent vocabulary + isolation. |
| `application/test_run_coherence_audit.py` | Runner on scenario id and raw `graph.json`. |
| `application/test_run_demo_scenario.py` | `run_demo_scenario` → `ScenarioViewModel` via fixture adapter (AC-1, FR-1–FR-6). |
| `application/test_value_insights.py` | UI_v2 shared plot analytics on `ValueScenarioInput` (ui2-01); explain paths + indirect relevance map (ui2-07, ui2-08). |
| `application/test_graph_filter.py` | UI_v2 graph type filter + isolation (ui2-02); explain highlight sets (ui2-07). |
| `application/test_run_scenario_view.py` | UI_v2 `run_scenario_view` facade + demo delegation (ui2-04); explain mode (ui2-07); **analitics** VS + catalog orchestration (ga-11). |
| `graph_analytics/test_models.py` | ga-01 domain types (blocked). |
| `graph_analytics/test_graph_bridge.py` | ga-02 adapter + preflight (blocked). |
| `graph_analytics/test_catalog_definitions.py` | ga-03 full catalog metadata (blocked). |
| `graph_analytics/test_relevance_migration.py` | ga-04 relevance/plot migration. |
| `graph_analytics/test_value_streams.py` | ga-05 VS discovery + classification. |
| `graph_analytics/test_runners_*.py` | ga-06…ga-09 runner contracts. |
| `graph_analytics/test_catalog_registry.py` | ga-10 registry + run_catalog. |
| `graph_analytics/test_fixture_validation.py` | ga-15 energoil event_type + preflight (blocked). |
| `fixtures/scenario/` | Value/graph factories for UI_v2 tests (no `demo_loader`); `relevance_explain_factory.py` for batch 2 A-26 explain + punto ciego. |
| `fixtures/graph_analytics/` | VS/governance graph fixtures for `graph_analytics` TDD (`vs_graph_factory.py`). |
| `graph_analytics/` | TDD tests for `analitics` requirement (ga-01…ga-15); **blocked** until `src/optimizer/graph_analytics/` lands in `04_implement`. |

**Run (project root, venv active, `pip install -e .`):**

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Agent: keep current

When you add a public facade or change cross-module wiring, add or update tests in the **mirrored** folder. Integration tests that hit OpenAI stay optional/skipped without API key. Update this file if you add the first test in a previously empty mirror folder.
