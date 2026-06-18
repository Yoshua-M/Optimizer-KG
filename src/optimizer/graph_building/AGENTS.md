# graph_building

## Responsibility

Own the **organizational knowledge graph** in production: turn normalized text (interviews, internal material) into graph documents, merge multiple sources into **one** org graph, and expose a stable domain API for downstream hygiene and linkage. Owns *what* entities and relationships mean in the org model and *how* they are assembled; not UI, not LLM client setup, not persistence drivers.

## Boundaries

| In | Out |
|----|-----|
| Extraction/generation prompts and graph-document assembly | Streamlit, HTML embed → `presentation/` |
| Merge policy across interviews/scenarios | PyVis rendering → `infrastructure/visualization/` |
| In-memory graph model / `GraphDocument` handling | `ChatOpenAI` / transformer construction → `infrastructure/llm_client/` |
| Calling `ontology/` for validation when it exists | Client value metrics → `client_value/` |
| | Raw file intake → `ingestion/` |
| | Use-case sequencing → `application/` |
| | Ad-hoc prompt spikes → `experiments/` (promote here when stable) |

**Callers:** `application/` (production), later `graph_hygiene/`, `value_linkage/`. **Callees:** `infrastructure/llm_client`, future `ontology/`.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker; optional re-export of domain facades only (avoid shadowing submodules). |
| `extraction.py` | Production path text → `GraphDocument` list: wraps LangChain `Document` + `graph_transformer.aconvert_to_graph_documents` without importing UI or PyVis. |

## Facade

- `extract_graph_data(text) → list[GraphDocument]` (async) — production extraction entry used by `application/run_pyvis_graph`.

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `merge.py` | Combine multiple graph documents / interviews into one org graph (single product graph). |
| `graph_model.py` | Internal types/helpers for nodes, edges, merge state — domain shape, not vendor SDKs. |
| `prompts.py` | Production prompt templates and chain config (not experiment forks). |

Promotion from `experiments/`: move proven prompt/chain code here and add tests under `tests/graph_building/`.
