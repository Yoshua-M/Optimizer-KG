# knowledge-graph-llms (Optimizer)

## Intention

Build **Optimizer**: map client and internal interview material to an **organizational knowledge graph** linked to **client value**, so leaders can prioritize investment (see `docs/PRD.md`). This repo is the host codebase — Python package `optimizer` under `src/`, Streamlit UI at `app.py`, LangChain extraction + PyVis viewing today; full PRD pipeline (ingestion, hygiene, linkage, Neo4j) is staged.

Load only what your task declares — use the routing table below and the nearest `AGENTS.md` in the tree.

## Folder structure

```text
knowledge-graph-llms/
├── AGENTS.md              ← project identity + routing (this file)
├── app.py                 ← Streamlit entry
├── docs/                  ← PRD, architecture, structure references
├── src/optimizer/         ← application code + per-module AGENTS.md
├── tests/                 ← unittest mirrors src/
├── data/                  ← raw / interim / processed
└── configs/               ← scenario JSON (future)
```

Local-only (gitignored): `workflows/` (feature development pipeline), `workspace/` (example-run traces).

## Quick nav

| Task | Go to |
|------|--------|
| Code in a package module | `src/optimizer/AGENTS.md` → `<module>/AGENTS.md` |
| Product scope | `docs/PRD.md` |
| System map | `docs/architecture.md` |
| Run app | `streamlit run app.py` (venv: `graph_env/`, `pip install -e .`) |
| Run tests | `tests/AGENTS.md` |

## Task routing

| Task | Go to | Read | Refs |
|------|-------|------|------|
| Edit or extend package code | `src/optimizer/AGENTS.md` | Matching `<module>/AGENTS.md` | `docs/architecture.md` if boundaries unclear |
| Understand product goals | — | `docs/PRD.md` | — |
| System architecture | — | `docs/architecture.md` | — |
| Structure protocols (background) | — | `docs/code_filestructure_protocol.md`, `docs/directory_contract_info.md` | Module `AGENTS.md` wins for code |
| Run Streamlit app | Root | `README.md`; `app.py` | `.env` with `OPENAI_API_KEY` |
| Run unit tests | `tests/AGENTS.md` | `tests/<module>/` | `pip install -e .` |
| Add or store data files | `data/AGENTS.md` | — | — |
| Record an architecture decision | `docs/decisions/` | `docs/AGENTS.md` | ADR template in `docs/directory_contract_info.md` |
| Shipped work history (approved feature-dev) | `docs/CHANGELOG.md` | `docs/changelog_rules.md` | Updated at end of `04_implement` |
| Feature from a requirement file | `workflows/feature_dev/AGENTS.md` | `workflows/feature_dev/inputs/<req>.md`; stage `AGENTS.md` | `workflows/feature_dev/docs/`; artifacts in `workflows/feature_dev/stages/*/output/` |

## Cross-module flow (code)

```text
app.py → presentation → application → graph_building → infrastructure
                              ↘ ingestion, client_value, … (future)
```

**Default graph UI:** `app.py` → `presentation/` → `application/` → `graph_building/` + `infrastructure/`. Not through `experiments/`.

## Naming

- **Use cases:** `application/run_<capability>.py`
- **Tests:** `tests/<module>/test_*.py`
- **Feature-dev artifacts (local workflow):** under `workflows/feature_dev/stages/<stage>/output/` — `<req>_intake.md`, `<req>_change_spec.md`, `<req>_test_log.md`, `<req>_done.md`; requirement input in `workflows/feature_dev/inputs/<req>.md`
- **Draft docs (optional):** `description_status.md` (`draft` / `review` / `final`)

## File placement

| Kind | Where |
|------|--------|
| Importable Python | `src/optimizer/<module>/` |
| Streamlit shell | Root `app.py`; UI body `presentation/` |
| Product & architecture docs | `docs/` (incl. `CHANGELOG.md`) |
| Module boundaries & facades | `src/optimizer/<module>/AGENTS.md` |
| Data artifacts | `data/raw`, `data/interim`, `data/processed` |
| Feature-dev requirement | `workflows/feature_dev/inputs/<req>.md` |
| Feature-dev stage artifacts | `workflows/feature_dev/stages/<NN>_<stage>/output/<req>_*.md` |
| Secrets | `.env` (never commit) |

## Agent rules

- Load **only** paths named for your task; do not read the whole repo.
- **`AGENTS.md` (package):** routing + rules. **`AGENTS.md` (module):** responsibility, boundaries, files, facades.
- Update the **nearest** `AGENTS.md` when you move code, add public entrypoints, or change routing.
- Do not duplicate full PRD or long protocol docs inside module agent files.
