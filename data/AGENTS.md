# data

## Responsibility

Store **project data artifacts** on disk in a fixed pipeline: untouched inputs → in-progress transforms → outputs ready for domains or reporting. Paths referenced by `ingestion/` and future batch jobs; not importable code.

## Boundaries

| In | Out |
|----|-----|
| Interview files, uploads copied for batch runs | Python modules → `src/optimizer/` |
| Intermediate extracts, normalized JSON/CSV | Secrets, API keys → `.env` only |
| Processed graphs or exports for reuse | Generated HTML from a session → repo root `knowledge_graph.html` today (move to `processed/` or `infrastructure/file_io` later) |
| | Test fixtures with logic → `tests/` |

**Writers (target):** `ingestion/`, `application/` batch use cases. **Readers:** same + `graph_building/` for batch replay.

## Subdirs — why here

| Path | Why it exists |
|------|----------------|
| `raw/` | Immutable or canonical copies of source material (txt, exports). Never overwrite in place. |
| `interim/` | Partial pipeline outputs (parsed text, draft graph docs) safe to delete and regenerate. |
| `processed/` | Stable outputs consumed by downstream steps or external tools (merged graph exports, reports). |

`.gitkeep` files keep empty stages in git; add real data paths to `.gitignore` when files are large or sensitive.

## Agent: keep current

Update this file if you add a new pipeline stage folder or change which module owns reads/writes for a stage. Do not commit large or client-confidential blobs without `.gitignore` rules.
