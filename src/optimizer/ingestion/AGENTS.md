# ingestion

## Responsibility

Own **intake of source material**: load, decode, and normalize interviews and documents into structured inputs (text, paths, metadata) that downstream domains consume. Answers “where did this text come from and in what shape”; does not run LLM extraction or build the org knowledge graph.

## Boundaries

| In | Out |
|----|-----|
| File/folder readers, format decoding, batch listing under `data/raw/` | Entity/relationship extraction → `graph_building/` |
| Source metadata (client vs internal, interview id, timestamps) | Client value scoring → `client_value/` |
| Stable intake facades for `application/` to call | Upload widgets, spinners → `presentation/` |
| | LLM wiring → `infrastructure/llm_client/` |

**Callers (target):** `application/ingest_documents.py`. **Callees:** `infrastructure/file_io` when file access is non-trivial.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker until intake facades exist. |

*(No intake implementation yet — UI still reads bytes in `presentation/streamlit_app.py`; that should move here via application when intake is productized.)*

## Facades (planned)

- `load_interview_text(path) → str` — single file to UTF-8 text.
- `ingest_sources(paths | data/raw) → list[NormalizedSource]` — batch intake with metadata for downstream modules.

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `loaders.py` (or `sources.py`) | Format-specific readers (txt now; pdf/docx later) without mixing graph logic. |
| `models.py` | Small types: `NormalizedSource`, tags — intake shape only. |

Keep modules **I/O + normalization**; semantic interpretation starts in `graph_building/` or `client_value/`.
