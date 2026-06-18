# experiments

## Responsibility

Own **non-production exploration** of graph extraction and generation: alternate LangChain chains, prompts, tools, and comparisons. Safe place to break things without affecting the default Streamlit → PyVis path. When an approach is stable, **promote** it into `graph_building/` (code + tests); do not let the app depend on this module.

## Boundaries

| In | Out |
|----|-----|
| Spike scripts, draft prompts, A/B helpers | Production `extract_graph_data` / merge → `graph_building/` |
| One-off runners and notebooks-style logic (in `.py` files) | Default UI workflow → `application/` must use `graph_building/` only |
| Reuse of `infrastructure/llm_client` | Permanent ontology rules → `ontology/` |
| | Streamlit pages → `presentation/` |

**Callers:** `application/run_experiment.py` (planned), manual/CLI runs. **Must not** be imported by `graph_building/` or `presentation/` for production.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker until experiment entrypoints exist. |

*(Empty — no spikes checked in yet.)*

## Facades (planned)

- Per-spike modules or `run_<experiment_name>(...)` — **not** part of the stable public API; document each spike file locally when added.

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `chains/` or `spikes/<name>.py` | Isolated alternative transformers/prompts. |
| `compare_runs.py` | Side-by-side metrics on sample texts (dev-only). |

**Promotion rule:** copy/adapt into `graph_building/`, delete or archive spike, extend `tests/graph_building/`. Never import `experiments` from production `graph_building` code.
