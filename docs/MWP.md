# Model Workspace Protocol (MWP) — Project Reference

> Project-level reference. The full protocol every workspace in this project (and every workspace it emits) operates under. Loaded on demand by any agent that needs the full picture; CLAUDE.md (L0) carries the brief.

A filesystem protocol for running multi-step AI workflows with one model, staged execution inside workspaces, and per-task context loaded on demand.

## Core idea

Replace one giant prompt (or many agents + orchestration code) with:

- root = identity + routing
- workspaces = mental modes (one per type of work)
- stages = transformation steps inside a workspace
- files = context + state
- one agent reads only what each task names

Scaling principle: a new mental mode = copy a workspace folder, write its `CONTEXT.md`, add one row to the L1 routing table.

## Layers

| Layer | File                                     | Purpose                                       |
|-------|------------------------------------------|-----------------------------------------------|
| L0    | root `CLAUDE.md`                         | identity (always loaded)                      |
| L1    | root `CONTEXT.md`                        | routing                                       |
| L2    | `<workspace>/CONTEXT.md`                 | workspace contract                            |
| L2-sub| `<workspace>/stages/CONTEXT.md` (root) and `<workspace>/stages/<NN>/CONTEXT.md` (per stage) | stage sequence + per-stage contracts |
| L3    | `<workspace>/docs/`                      | static reference: templates / rules / domain references |
| L4    | `<workspace>/output/` or `<workspace>/stages/<NN>/output/` | dynamic working artifacts |

L0 and L1 are **separate files**. L3 is **per-workspace**. There is no global root `docs/`. Each workspace owns its own L3.

> Convention note: the L2-sub *root* lives at `stages/CONTEXT.md`, not in a `specs/` subdirectory. Single-stage workspaces have no `stages/` at all and use `<workspace>/output/` directly.

## L0 — root `CLAUDE.md` (identity)

Auto-loaded into every conversation; pure tax. Contents:

- project intention (2–3 sentences)
- folder structure
- quick nav (task → workspace)
- cross-workspace flow
- naming conventions (project-wide rules live here)
- file placement rules
- brief explainer of any framework the project teaches its agents (e.g. MWP itself when relevant)

Rule of thumb: must fit in **one screen** by default. Generator-style projects that teach a framework to their own agents may exceed this; budget guidance below applies as soft targets.

## L1 — root `CONTEXT.md` (routing)

Frees the user from referencing files manually in chat. Contents:

- task routing table
- workspace summary
- cross-workspace flow

Routing table format:

```
| Task | Go to | Read | Skills/refs |
```

Without this table the agent reads everything (wasting tokens) or guesses (failing unpredictably). The "Skills/refs" column wires L3 entries (or external skills) into the workspace at the point of use.

## L2 — workspace `CONTEXT.md` (contract)

Workspace-routing surface. Shape branches on stage count.

**Multi-stage workflows** — required section set, in this order (matches `examples/L2_multistage_wf.md`):

- `## What This Workspace Is` — 1–2 sentences of purpose; cross-workspace flow if any
- `## Where to Go` — task → file routing inside the workspace
- `## Folder Structure` — the workspace's tree
- `## What to Load` — task-level load hints (small; per-stage loads live in each stage's CONTEXT)
- `## Skills & Tools for This Workspace` — external skills/tools wired in (slash-commands, MCPs, etc.); paired with the stage that uses each. **Not** per-stage how-to docs.
- `## Hard Rules` — workspace-specific invariants

The `Inputs / Process / Outputs` triple does **not** appear at multi-stage L2 — it's the L2-sub (stage) shape (see below).

**Single-stage workflows** — the workspace IS the one stage; no L2-sub exists. L2 carries the stage contract directly:

```
# <Workflow Name>

<1–2 sentence purpose>

## Inputs   — files / resources to load
## Process  — what to do
## Outputs  — what to write and where
## Hard Rules  — optional
```

Each workspace either has `output/` (single-stage) **xor** a `stages/` tree with per-stage `output/` (multi-stage), never both.

## L2-sub — multi-stage workflows only

If a workspace has many stages: write `<workspace>/stages/CONTEXT.md` describing the stage sequence, and one `<workspace>/stages/<NN>/CONTEXT.md` per stage. Each stage `CONTEXT.md` uses exactly:

```
## Inputs   — files / resources to load for the task
## Process  — what to do (inline; this is where the stage's procedure lives)
## Outputs  — what to write and where
```

This triple is the **stage** contract; do not promote it to a multi-stage workspace L2.

The stage's `## Process` block is the single home for the stage's procedure. Procedures are **not** extracted into separate `skill_*.md` files in L3 — see "Rules for L3" below.

## L3 — `<workspace>/docs/` (reference, static)

Contents that belong in L3:

- **Templates** — output skeletons / "what good output looks like" docs that stages consume.
- **Reference docs** — domain facts, schemas, constraints, decision heuristics narrow to *this* workspace's job.
- **External-skill wrappers** (rare) — `skill_*.md` reserved for genuinely reusable methodology (a tool wrapper, a research method, a workflow shared across multiple stages or workspaces). Per-stage how-tos do not qualify.

Contents that do **not** belong in L3:

- A per-stage procedure. That goes in the stage's own `CONTEXT.md` `## Process`.
- Project-wide identity, conventions, or constraints. Those live above L2 (in `CLAUDE.md` (L0) or in a project-level reference such as this `MWP.md`).

L3 is constraint, not transformation: the agent loads it, follows it, but does not modify it inside a stage run.

## L4 — `<workspace>/output/` (working artifacts, dynamic)

Per-run data, stage outputs, drafts. The **editable control surface**: humans review and edit here between stages.

## Stage contract & execution loop

Each stage `CONTEXT.md` declares Inputs / Process / Outputs (see L2-sub shape). Execution per stage:

1. Load: L0 + L1 (always) → workspace `CONTEXT.md` (L2) → stage `CONTEXT.md` (L2-sub) if multi-stage → declared L3 references → declared L4 inputs.
2. Execute the stage's process.
3. Write output to `output/`. STOP.
4. Human reviews. May edit the output OR signal advancement in chat.
5. Next stage reads the (possibly edited) output. No caching.

Order = folder numbering (`01_… → 02_… → 03_…`). One stage = one job. No hidden state.

## Skills

Two distinct concepts share the word; keep them separate:

1. **External skills / tools** — slash-commands (`/frontend-design`), MCPs (Context7, Web Search), Playwright wrappers, etc. These are wired into a workspace via the L2's `## Skills & Tools` table and via the L1 `Skills/refs` column.
2. **Reusable methodologies** packaged as `skill_*.md` in an L3 — only when the methodology is genuinely shared across multiple stages or workspaces. A procedure used by exactly one stage is not a skill; it is the stage's process and lives in the stage's `CONTEXT.md`.

Rule of thumb: any process you re-explain to the agent in every chat *and* that applies to multiple consumers should become a skill. A process specific to one stage is not a skill.

## Research workflow (terminates in L3)

When a stage detects a critical decision lacking evidence:

1. The stage writes a `Research recommendations` block in its `output/` and halts (or finishes with the block visible) instead of guessing.
2. The user (or a research pass) acquires the missing material.
3. The result is written into the **requesting workflow's L3** as either:
   - a new **reference doc** (facts / standards / heuristics / templates), or
   - a new **skill** (only if it codifies a reusable methodology shared across stages/workspaces — see above).
4. The originating stage is rerun; it now finds the new entry via the L1 routing table.

Research never lingers as floating text — it always lands as a durable L3 artifact in the workflow that needed it.

## Rules for the agent

- NEVER load the entire project.
- ONLY load declared inputs.
- ALWAYS write to the declared output path.
- NEVER overwrite previous stage data silently.
- FOLLOW L3 rules strictly.
- TRANSFORM only L4 data.

## Rules for L3 (what goes in `<workspace>/docs/`)

1. **Reference material the stages consume, not procedures the stages execute.** A stage's `## Process` is the right home for procedure.
2. **`skill_*.md` is reserved for reusable methodology** that applies across multiple stages or workspaces, or for an external-tool/integration wrapper. Per-stage how-tos are not skills.
3. **L3 is per-workspace and contains only workspace-specific material.** Project-wide identity (the protocol itself), project-wide conventions (file/dir naming), and project-wide constraints (context budgets) live above L2 — in `CLAUDE.md` (L0) or a project-level reference such as this `MWP.md` — not duplicated into each workspace's `docs/`.
4. **Templates are L3.** Output skeletons, schemas, and "what good output looks like" docs are reference material a stage consumes — they are valid L3 entries.
5. **L3-worthiness test, applied per file:**
   - Loaded by exactly one stage AND content is procedural → fold into the stage's `CONTEXT.md`.
   - Loaded by multiple stages of this workspace, or by every stage of this workspace as background → reference doc in this workspace's `docs/`.
   - Loaded by multiple workspaces of the project → project-level, above L2.

## Context budget

| Layer / file                     | Soft target     | Why                                          |
|----------------------------------|-----------------|----------------------------------------------|
| Root `CLAUDE.md` (L0)            | one screen (~80 lines) by default; framework-teaching projects may exceed | auto-loaded into every conversation; pure tax |
| Root `CONTEXT.md` (L1)           | ~60 lines       | routing only; no instructions                |
| Workspace `CONTEXT.md` (L2)      | ~150 lines      | workspace contract + load-table              |
| `stages/CONTEXT.md` (L2-sub root)| ~80 lines       | stage sequence + per-stage one-liner         |
| Stage `CONTEXT.md` (L2-sub)      | soft target ~50–100 lines; relax for complex stages whose `## Process` is intentionally inline | inputs / process / outputs |
| L3 file (template / reference)   | ~150 lines      | one focused concern per file                 |

Per-stage **execution context** target (everything the stage loads): `15–30 %` of the model's context window. Default model assumption: 200k tokens (CN-001); ~30k–60k tokens per stage.

### Budget rules

1. If a file exceeds its target *and* the excess content can be split without losing cohesion, split it. Preferred split: by section → new L3 file referenced from the parent.
2. The agent must load **only** what the routing table or the stage contract names. No "load the whole workspace" reflex.
3. L0 + L1 are always loaded. Everything else is on-demand.
4. These are **soft targets**, not hard caps. A stage whose `## Process` is intentionally inlined for clarity may exceed the L2-sub target. Prefer comprehension over arbitrary trimming.

### Failure modes to avoid

- L0 slowly grows past one screen for no good reason → split content into workspace `CONTEXT.md` files or into a project-level reference (this file).
- Stage CONTEXT.md describes the agent instead of the work → keep behavioral guidance ≤ 20 % of the file.
- Multiple skills loaded "just in case" → cuts directly into the per-stage budget.

## Common mistakes

| Mistake                                     | Fix                                                |
|---------------------------------------------|----------------------------------------------------|
| `CLAUDE.md` too long                        | Split into workspace `CONTEXT.md` files or a project-level reference. |
| No routing table                            | Add it to L1.                                      |
| Too many workspaces                         | Start with 2–3. Add more only when proven.         |
| Context describes the agent, not the work   | Keep behavioral guidance ≤ 20 % of the file.       |
| Stale context files                         | Treat them as living documents.                    |
| Flat folders (>8–10 files at one level)     | Introduce subfolders.                              |
| Building everything before using it         | First version should run in ~15 minutes.           |
| Per-stage skills cluttering L3              | Fold the procedure back into the stage's `## Process`. |
| Project-wide constraints duplicated per workspace L3 | Promote to L0 / project-level reference and reference by path. |

## Best for / not for

Best for sequential workflows, human-reviewed pipelines, repeatable stage-based work. Not for real-time multi-agent loops, high concurrency, or auto-branching pipelines.

## Mental model

MWP = a compiler pipeline organized by mental mode. Workspaces = compilation units. Stages = passes. L4 artifacts = intermediate representations. Each stage: `input → transform → output`.

---

## Appendix A — Naming conventions (project-wide)

### File names

Pattern: `description_status.extension`

Examples:
- draft   → `prd_draft.md`
- final   → `prd_final.md`
- versioned → `plan_v2.md`
- dated   → `2026-05-01_extraction.md`

Pick one convention per project and keep it. Status values: `draft` → `review` → `final`.

### Workspace dir names

- `lower_snake_case`.
- Name describes the **mental mode**, not the artifact. Good: `workspace_blueprint`. Bad: `tree_files`.
- One workspace per mental mode. Two tasks that share a mental mode share a workspace.

### Stage dir names

Pattern: `NN_short_verb_or_noun` (e.g. `01_prd`, `04_plan_review`, `06_l0_l1_emit`).

Rules:
- `NN` is a two-digit zero-padded order index. Order = folder numbering.
- Renumbering is allowed but rare; downstream stages must still find prior outputs by name.

### Reserved files

- `CLAUDE.md` — L0 identity (root only).
- `CONTEXT.md` — L1 routing (root) / L2 workspace contract / L2-sub stage contract / L2-sub root in `stages/`.
- `MWP.md` — project-level MWP reference (this file; root only).
- Workspace-specific reserved names (e.g. `workflows_to_implement.md` in this generator) are declared in that workspace's L2.
