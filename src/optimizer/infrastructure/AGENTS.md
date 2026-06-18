# infrastructure

## Responsibility

Own **technical adapters**: configure and call external systems (LLM APIs, visualization libraries, databases, filesystem, env/config) and return neutral data structures. Translates between vendor APIs and the rest of the app; does not decide org-graph meaning, merge policy, or UI flow.

## Boundaries

| In | Out |
|----|-----|
| SDK/client construction (`ChatOpenAI`, `LLMGraphTransformer`, PyVis, Neo4j later) | Business rules on entities/relations → `graph_building/` |
| Env load, serialization (HTML, DB rows, bytes on disk) | Use-case ordering → `application/` |
| Reusable adapter modules per technology | Streamlit → `presentation/` |

**Callers:** `graph_building/`, `experiments/`, `application/`. **Must not import** domain modules.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker; no re-exports that shadow submodule filenames (breaks test mocks). |
| `llm_client/__init__.py` | Subpackage boundary for LLM-related adapters only. |
| `llm_client/graph_transformer.py` | One place to construct `ChatOpenAI` + `LLMGraphTransformer` and `load_dotenv`; domains import `graph_transformer` instead of duplicating API keys and model choice. |
| `visualization/__init__.py` | Subpackage boundary for render/export adapters. |
| `visualization/pyvis_graph.py` | Maps LangChain `GraphDocument` lists to a PyVis `Network` (layout, styling, invalid-edge filter); `VisualizeOptions` for colors, tooltips, relevance-pull edges, grey-out highlight, `"punto ciego"` synthetic edges, VS `node_color_overrides`, `node_size_overrides` (backbone), `edge_width_overrides` (VS focus); `VS_CATEGORY_COLORS` palette; no Streamlit, no extraction. |
| `demo_loader.py` | Manifest + JSON fixture load, validation, `graph.json` → `GraphDocument` adapter; repo-root path resolution. |

## Facades

- `graph_transformer` (`llm_client/graph_transformer.py`) — configured `LLMGraphTransformer` for `aconvert_to_graph_documents`.
- `visualize_graph(graph_documents, options=None) → Network` — PyVis network from graph documents; optional `VisualizeOptions` (highlight dimming, indirect `"punto ciego"` edges).
- `demo_loader` — `resolve_repo_root`, `load_manifest`, `load_demo_bundle`, `graph_json_to_graph_documents`, `bundle_to_value_input`; typed `Demo*Error` exceptions.

## Planned (same module)

| Path | Why it would live here |
|------|-------------------------|
| `graph_store/` | Neo4j driver/session; persist/query graph for chatbot era. |
| `config_loader.py` | Read `configs/` + env into typed settings. |
| `file_io.py` | Read/write artifacts (`knowledge_graph.html`, uploads) without UI. |

One external concern per subfolder or top-level adapter file; expose one obvious import per concern.
