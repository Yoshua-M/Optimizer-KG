# MODEL WORKSPACE PROTOCOL (MWP) — CONTEXT

## PURPOSE
MWP is a filesystem-based protocol to run multi-step AI workflows using:
- one model
- staged execution inside workspaces
- structured, per-task context loaded on demand

Goal:
Convert complex projects into sequential transformations over files,
organized into **workspaces** (mental modes) and **stages** (transformation steps).

---

## CORE IDEA
Instead of:
- one giant prompt, OR
- many agents + code orchestration

Use:
- root = identity + routing
- workspaces = mental modes (one per type of work)
- stages = transformation steps inside a workspace
- files = context + state
- one agent reads only the context it needs per task

---

## PROJECT = ROOT + WORKSPACES

A project root contains:
- L0: `CLAUDE.md` (identity)
- L1: `CONTEXT.md` (routing)
- L3: `docs/` (reference material; optional)
- one folder per workspace

A **workspace** = a subfolder for one type of work / mental mode.
Each workspace contains:
- its own `CONTEXT.md` (workspace contract)
- `stages/` if the workspace runs as a multi-step pipeline
- workspace-local L3 references if needed
- `output/` working artifacts (L4)

Rules:
- One workspace = one mental mode. If you shift how you think between two tasks, those are two workspaces.
- Start with 2–3 workspaces; add more only when a type of work proves it needs its own context.
- Never bleed context between workspaces.

---

## LAYERS (CONTEXT MODEL)

### L0 — Identity
File: root `CLAUDE.md`
Contains:
- project intention (2–3 sentences)
- folder structure
- quick nav (tasks → workspaces)
- cross-workspace flow
- naming conventions
- file placement rules

Answers: "Where am I? What does this project do?"

Rule of thumb: must fit in **one screen**. If longer, extract content into workspace `CONTEXT.md` files.

---

### L1 — Routing
File: root `CONTEXT.md`
Contains:
- task routing table (task → workspace → files to read → skills/refs)
- workspace summaries
- cross-workspace flow

Answers: "Where do I go?"

Purpose: frees the user from referencing files manually in chat.

Routing table format:
```
| Task | Go to | Read | Skills/refs |
|------|-------|------|-------------|
```

Without this table the agent either reads everything (wasting tokens) or guesses (failing unpredictably).

---

### L2 — Workspace / Stage Contract
Files:
- `<workspace>/CONTEXT.md` (workspace contract)
- `<workspace>/stages/<NN_name>/CONTEXT.md` (per-stage contract, if multi-stage)

Contract structure:
- **Inputs** — which files / resources to load for this task
- **Process** — what to do, OR a pointer to a workflow file (rules for artifacts)
- **Outputs** — what to write and where (dir structure)

Answers: "What do I do here?"

#### L2-sub — multi-stage workflows
If a workspace needs many stages, add a workflow description file inside the workspace's `specs/` (or equivalent) describing the stage sequence. Each stage folder still carries its own L2 `CONTEXT.md`.

---

### L3 — Reference (STATIC)
Folder: **`<workspace>/docs/`** — L3 is **per-workflow** (per workspace).
There is no global root `docs/`. Each workspace owns its own L3.

Content:
- templates
- rules
- style guides
- conventions
- **skills** (packaged how-to instructions plugged into the workspace)
- research outputs that landed here via the Research workflow (see below)

Use:
- constraints (DO NOT transform)
- the only place skills and reference material may live for that workspace

---

### L4 — Working Artifacts (DYNAMIC)
Folder: `<workspace>/output/` (or `<workspace>/stages/<NN>/output/` for multi-stage).

Content:
- current run data
- stage outputs
- drafts

Use:
- input/output (TRANSFORM)
- **editable control surface** — humans review and edit here between stages

---

## KEY DISTINCTIONS

| Pair | Difference |
|------|------------|
| L3 vs L4 | L3 = stable rules; L4 = per-run data. Never mix. |
| Workspace vs Stage | Workspace = mental mode (e.g. writing vs coding); Stage = transformation step inside a workspace (research → spec → plan). |
| L0 vs L1 | L0 = what this project is; L1 = where to go for a given task. |

---

## STAGES

A stage = one transformation step inside a workspace.

Rules:
- one job only
- read declared inputs
- write declared output
- no hidden state

Execution order = folder numbering. Example: `01_research → 02_spec → 03_plan`.

---

## STAGE CONTRACT (REQUIRED)

Each stage MUST define in its `CONTEXT.md`:

```
## Inputs
- L4: ../01_research/output/
- L3: ../../docs/template.md

## Process
- transform research into spec

## Outputs
- spec.md → output/
```

---

## EXECUTION LOOP

For each stage:

1. Load:
   - L0 + L1 (always)
   - workspace `CONTEXT.md` (L2)
   - stage `CONTEXT.md` (L2-sub) if multi-stage
   - declared L3 references
   - declared L4 inputs

2. Execute the stage process.

3. Write output → `output/`.

4. STOP — human may edit.

5. User signals the next stage **either** by editing the stage output **or** via chat.

6. Next stage reads the (possibly edited) output.

---

## HUMAN LOOP

Between stages:
- review output
- edit directly OR signal via chat
- rerun stage if needed

Principle:
Stage outputs are editable control surfaces.

---

## DESIGN PRINCIPLES

1. One stage = one job
2. One workspace = one mental mode
3. Plain text = interface
4. Load only relevant context
5. Every output is editable
6. Configure once (L3), reuse many times
7. `CLAUDE.md` ≤ one screen
8. Start small (2–3 workspaces); grow only when proven

---

## SKILLS

Skills = packaged how-to instructions (a workflow, a tool-usage pattern, a method).
- Stored under that workspace's L3 (`<workspace>/docs/`).
- Plugged into the workspace via the L1 routing table (a column lists applicable skills).
- Workspaces only "see" the skills they declare.

Rule of thumb: any process you re-explain to the agent in every chat should become a skill.

---

## RESEARCH WORKFLOW (terminates in L3)

When a stage detects that a critical decision lacks evidence:

1. The stage records a `Research recommendations` block in its `output/` and halts (or finishes with the block visible) instead of guessing a default.
2. The user (or a separate research workflow) acquires the missing material.
3. The result is written into the **requesting workflow's L3** (`<workspace>/docs/`) as either:
   - a new **skill** (if it codifies a how-to), or
   - a new **reference document** (if it codifies facts/standards/best practices).
4. The originating stage is rerun; it now finds the new L3 entry via the L1 routing table.

Principle:
Research never lingers as floating text — it always lands as a durable L3 artifact in the workflow that needed it.

---

## NAMING CONVENTIONS

Defined in L0 (`CLAUDE.md`) so the agent can find/create files without a lookup.

Pattern: `description_status.extension`

Examples:
- draft:        `api-auth-guide_draft.md`
- final:        `api-auth-guide_final.md`
- versioned:    `demo-script_v2.md`
- date-stamped: `2026-03-14_launch-week-newsletter.md`
- client-keyed: `alpha_proposal_v3.md`

Pick one and stay consistent.

---

## WORKFLOW TYPE

Best for:
- sequential workflows
- human-reviewed pipelines
- repeatable, stage-based work

Not for:
- real-time multi-agent loops
- high concurrency
- complex auto-branching

---

## ARTIFACT FLOW (example)

PRD → Spec → Plan → Tasks → Implementation → Verification

Each = an L4 artifact, produced by one stage in some workspace.

---

## FILE ROLES

- root `CLAUDE.md`                          → L0 identity
- root `CONTEXT.md`                         → L1 routing
- `<workspace>/CONTEXT.md`                  → workspace contract (L2)
- `<workspace>/stages/<NN>/CONTEXT.md`      → stage contract (L2-sub)
- `<workspace>/docs/`                       → L3 references / templates / skills (per-workflow)
- `<workspace>/output/` or `<workspace>/stages/<NN>/output/` → L4 working artifacts

---

## RULES FOR AGENT

- NEVER load the entire project.
- ONLY load declared inputs.
- ALWAYS write to the declared output path.
- NEVER overwrite previous stage data silently.
- FOLLOW L3 rules strictly.
- TRANSFORM only L4 data.

---

## COMMON MISTAKES

1. `CLAUDE.md` too long → split into workspace `CONTEXT.md` files.
2. No routing table → agent guesses; add it to L1.
3. Too many workspaces → start with 2–3.
4. Context files describe the agent instead of the work → 80% project/standards, ≤20% behavior.
5. Stale context files → treat them as living documents.
6. Flat folders (>8–10 files at one level) → introduce subfolders.
7. Building everything before using it → first version should take ~15 minutes.

---

## MENTAL MODEL

MWP = a compiler pipeline organized by mental mode.

- Workspaces = compilation units.
- Stages = passes.
- Artifacts (L4) = intermediate representations.

Each stage:
`input → transform → output`

---

## MINIMAL PROJECT

```
project/
├── CLAUDE.md                  ← L0 identity, naming, file placement, quick nav
├── CONTEXT.md                 ← L1 routing table
└── <workspace>/
    ├── CONTEXT.md             ← L2 workspace contract
    ├── docs/                  ← L3 references / skills (per-workflow)
    ├── stages/                ← only if multi-stage
    │   ├── 01_x/
    │   │   ├── CONTEXT.md
    │   │   └── output/
    │   └── 02_y/
    │       ├── CONTEXT.md
    │       └── output/
    └── output/                ← L4 (if single-stage workspace)
```

---

## END
