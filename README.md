# Optimizer (knowledge-graph-llms)

Python codebase for **Optimizer**: map client and internal interview material to an **organizational knowledge graph** linked to **client value**, so leaders can see which activities and processes matter most for investment. Product scope is in [`docs/PRD.md`](docs/PRD.md); system design in [`docs/architecture.md`](docs/architecture.md).

**Today:** a Streamlit app that extracts entities and relationships from text with LangChain + OpenAI and renders an interactive graph with PyVis. **Staged next:** batch ingestion, graph hygiene, value linkage, and Neo4j persistence per the PRD.

![CleanShot 2025-05-28 at 13 11 46](https://github.com/user-attachments/assets/4fef9158-8dd8-432d-bb8a-b53953a82c6c)

## Features (current app)

- Text input via upload (`.txt`) or paste
- LLM-powered entity and relationship extraction (GPT-4o via LangChain)
- Interactive PyVis graph in the browser
- Modular package layout under `src/optimizer/` for ongoing PRD work

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

Use a virtual environment (e.g. `graph_env/` in the repo):

```bash
python -m venv graph_env
source graph_env/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```

`pip install -e .` installs the **`optimizer`** package from `src/` (see `pyproject.toml`). Dependencies are listed there; `requirements.txt` mirrors them for convenience.

Create a `.env` file at the project root:

```text
OPENAI_API_KEY=your_key_here
```

## Run the app

**Text → knowledge graph** (requires `OPENAI_API_KEY`):

```bash
source graph_env/bin/activate
streamlit run app.py
```

**Fixture sales demo** (no API key; pre-built scenario data via `configs/demo_scenarios.json`; uses the same scenario UI as production):

```bash
source graph_env/bin/activate
streamlit run app_demo.py
```

Opens in the browser (default http://localhost:8501). Session output may write `knowledge_graph.html` or `scenario_knowledge_graph.html` to the working directory (usually repo root).

## Tests

```bash
source graph_env/bin/activate
python -m unittest discover -s tests -p "test_*.py" -v
```

Unit tests mock the LLM. The integration test in `tests/graph_building/` runs against OpenAI when `OPENAI_API_KEY` is set in `.env`.

## Usage

1. Choose **Upload txt** or **Input text** in the sidebar
2. Provide text and click **Generate Knowledge Graph**
3. Explore the graph (drag nodes, zoom, filter)

## How it works

```text
app.py → presentation/ → application/run_pyvis_graph
       → graph_building/extract_graph_data → infrastructure/ (LLM + PyVis)
       → HTML embedded in Streamlit
```

LangChain's graph transformer turns text into graph documents; PyVis builds the interactive view.

## Project layout

| Path | Role |
|------|------|
| `app.py` | Streamlit entry — text → graph (`streamlit run app.py`) |
| `app_demo.py` | Streamlit entry — fixture demos (`streamlit run app_demo.py`) |
| `src/optimizer/` | Main Python package (`optimizer`) |
| `src/optimizer/presentation/` | Streamlit UI |
| `src/optimizer/application/` | Use-case orchestration (`run_pyvis_graph`, `run_demo_scenario`) |
| `src/optimizer/graph_building/` | Production org-graph extraction |
| `src/optimizer/infrastructure/` | LLM client, PyVis, future adapters |
| `src/optimizer/experiments/` | Exploration spikes (not used by default UI) |
| `src/optimizer/ingestion/`, `client_value/`, `graph_hygiene/`, `value_linkage/`, `ontology/` | PRD domains (scaffolded) |
| `tests/` | Unittest layout mirroring `src/optimizer/` |
| `data/raw`, `data/interim`, `data/processed` | Data pipeline placeholders |
| `docs/` | PRD, architecture, structure references |
| `configs/` | Runtime/scenario config (future) |

Each package module has an `AGENTS.md` with boundaries and entry points for contributors and agents working in that area.

## Documentation

| Doc | Contents |
|-----|----------|
| [`docs/PRD.md`](docs/PRD.md) | Product requirements |
| [`docs/architecture.md`](docs/architecture.md) | Domains, flows, dependencies |
| [`docs/AGENTS.md`](docs/AGENTS.md) | What lives in `docs/` |

## Origins

This repo began as a [knowledge graph from text tutorial](https://www.youtube.com/watch?v=O-T_6KOXML4); it is being extended into the Optimizer product described in the PRD.
