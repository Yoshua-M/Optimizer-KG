# Architecture

Human-facing map of **Optimizer** in this repo. Module boundaries and facades live in `src/optimizer/<module>/AGENTS.md`; this file stays brief.

## Goal

Turn client and internal interview material into an **organizational knowledge graph** linked to **client value**, so executives can see which activities and processes matter most for investment (see `PRD.md`).

**Current milestone:** LangChain extraction + **PyVis/Streamlit** to view the org graph from text. **Neo4j Aura** and full PRD pipeline are staged, not blocking the live UI path.

## Main domains

Package: `src/optimizer/` (`pip install -e .`).

| Layer | Module | Role |
|-------|--------|------|
| Entry | Root `app.py` | Thin Streamlit launcher only |
| UI | `presentation/` | All `st.*` UI and HTML embed |
| Use cases | `application/` | Orchestrate workflows; no UI or SDK wiring |
| Production KG | `graph_building/` | Extract, merge, org graph documents |
| Exploration | `experiments/` | Spikes; promote winners into `graph_building/` |
| Adapters | `infrastructure/` | LLM, PyVis, future Neo4j/config/files |
| Intake | `ingestion/` | Raw docs → normalized inputs |
| Client value | `client_value/` | Client interview → value metrics |
| Quality | `graph_hygiene/` | Dedup, prune, conflicts |
| Bridge | `value_linkage/` | Rank/link activities to metrics |
| Rules | `ontology/` | Allowed types/relations, validation |

**Support dirs:** `data/` (raw → interim → processed), `tests/` (mirrors modules, unittest), `docs/` (PRD, this file, ADRs).

## Main workflows

### Live today — view org graph from text

```text
streamlit run app.py
  → presentation.run_app()
  → application.run_pyvis_graph(text)
  → graph_building.extract_graph_data(text)
  → infrastructure (LLM transformer, PyVis network)
  → HTML embedded in Streamlit
```

Production path uses **`graph_building` only**, not `experiments/`.

### Target (PRD) — end-to-end Optimizer

```text
ingestion (client + internal sources)
  → client_value (client metrics)     graph_building (+ ontology)
  → graph_hygiene
  → value_linkage
  → infrastructure/graph_store (Neo4j Aura)
  → presentation (explainability + rankings)
```

## External inputs and outputs

| Input | Where | Output | Where |
|-------|--------|--------|--------|
| `.txt` upload or pasted text | UI (`presentation/`) | Interactive graph (PyVis HTML) | Browser embed; session file `knowledge_graph.html` at repo root today |
| Interview/docs (batch) | `data/raw/` → `ingestion/` (planned) | Graph documents, merged org graph | `graph_building/`; later `data/processed/` |
| OpenAI API | `.env` `OPENAI_API_KEY` | LLM graph extraction | `infrastructure/llm_client/` |
| Neo4j Aura (deferred) | Cloud | Persisted KG | `infrastructure/graph_store/` (planned) |

## Config strategy

- **Secrets:** `.env` at repo root (e.g. `OPENAI_API_KEY`); never committed.
- **Scenario params:** `configs/` (JSON examples; loader in `infrastructure/` planned).
- **Dependencies:** `pyproject.toml` (canonical); `requirements.txt` mirrors for simplicity.
- **Runtime:** single venv `graph_env/`; editable install `pip install -e .`.

## Reporting / audit needs

- **Explainability (PRD):** trace how entities, relationships, and scores were derived — future `presentation/` views over `application/` use cases.
- **Graph quality:** hygiene and conflict visibility before executives trust rankings — `graph_hygiene/` + explainability UI.
- **Decisions:** non-obvious structural choices → `docs/decisions/` (ADR format).
- **Generated artifacts:** prefer `data/processed/` or dedicated report dirs over mixing with source (see `data/AGENTS.md`).

## Dependency rules

```text
presentation  →  application  →  domains  →  infrastructure
                      ↓
              (never import presentation from application or domains)

experiments  →  infrastructure   (must not be required for production UI)
graph_building  ↛  experiments

domains do not import each other's internals — use facades documented in module AGENTS files.
```

**Tests** mirror modules under `tests/<module>/`. Regression bar: `python3 -m unittest discover -s tests -p "test_*.py" -v`.

## Assumptions

- One **organizational** knowledge graph in product terms; client value is a separate concern linked later via `value_linkage/`.
- Graph **documents** (LangChain in memory) are acceptable for viewing until quality supports Neo4j cutover.
- Module `AGENTS.md` files are kept in sync with code moves; agents load package router first (`src/optimizer/AGENTS.md`).
- Full PRD scope (Neo4j persistence, rankings, batch ingestion) ships incrementally; empty modules are intentional placeholders.

## Related docs

| Doc | Use |
|-----|-----|
| `PRD.md` | Product scope and success criteria |
| `src/optimizer/AGENTS.md` | Where to implement new code |
| `docs/AGENTS.md` | What belongs in this folder |
| `docs/decisions/` | Architecture decision records |
