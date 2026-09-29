# Generation-Time Signals (Doc 2)

**Loaded on every code-generation pass.** Keep it short — it competes for context with the actual work.

**What this does.** Watches for a small set of architectural red flags while code is being written, commits each logical change, and appends a log entry **only when a flag fires**. Silence is the normal outcome. Most passes produce a commit and no log.

**What this does not do.** No predictions. No scoring. No recommendations. No record of what shipped. No report when nothing fires. Decisions belong to Doc 3.

**Dependencies.** Module contracts (MWP `.md` files) and git. Nothing else. This doc works from the first commit of a greenfield codebase.

---

## 1. Before writing code

Read the contract for the module you are about to change.

From it, extract the **declared scope**:

- **Owns** — files, paths, or responsibilities this module is responsible for
- **May depend on** — modules it is permitted to reach
- **Data owned** — tables, schemas, keys, or state it may write
- **Side effects allowed** — I/O, network, filesystem, events it may emit
- **Config scope** — configuration keys it is entitled to read

If no contract exists for this module, log `NO_CONTRACT` and proceed. A module being edited without a contract is itself a finding.

---

## 2. Commit

Commit **before** evaluating flags, so every signal carries the SHA of the change it describes. That SHA is what lets Doc 3 open the diff later.

### When to commit

The test is logical completeness, not size or elapsed time:

> Can you describe what changed in one sentence, without using "and"?

If the sentence needs an "and", there are two commits in the working tree.

Commit when all three hold:

- The change does one thing
- Tests pass, or at least nothing newly fails
- Nothing in the working tree belongs to a different concern

**Never begin a second logical change on top of an uncommitted first one.** Commit before switching concerns. This rule prevents mixed commits more reliably than any of the others, because the failure happens at the *start* of the next change, not the end of the last one.

Also commit before any risky or large operation, so there is a rollback point, and at each MWP stage boundary regardless.

Commit **autonomously** — it is local, reversible, and changes no code. Do not ask. Pushing stays manual; batching pushes is fine, since git preserves the individual commits either way.

### Before committing

Check `src/` and `scripts/` for untracked files. Include them, gitignore them explicitly, or flag. Untracked code is invisible to every downstream lens.

### Message format

```
<type>(<module>): <one line, imperative>

<why, if a boundary was crossed>

req_id: <requirement id, if in-pipeline>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`.

The type matters more than it looks. Mechanical work — reformats, renames, dependency bumps, generated code — goes in its own commit typed `chore` or `style`, never mixed with semantic change. That lets the evolutionary pass exclude noise **by intent** rather than by commit size, which is a blunt filter that can exclude the very commits that matter.

**One logical change per commit.** A rename bundled with logic makes every renamed file appear coupled to every changed file.

The body explains **why**, not what — the file list already says what. If the change crossed a module boundary, the body says what forced it. Same standard as the `note` field below, and for the same reason: it is the causal link Doc 3 needs when it opens the commit.

**Do not squash-merge.** Squash collapses granular commits back into one feature-sized commit and destroys the grain everything here depends on. Turn squash merge off at the repository level.

---

## 3. After committing — check for flags

Compare what you actually did against the declared scope. Log only what fires.

### Boundary flags

| Flag | Fires when |
|---|---|
| `SCOPE_EXCEEDED` | Touched a file outside the module's declared **owns** |
| `UNDECLARED_DEPENDENCY` | Imported or called a module not in **may depend on** |
| `FOREIGN_DATA_WRITE` | Wrote to a table, schema, cache key, or store not in **data owned** |
| `UNDECLARED_SIDE_EFFECT` | Performed I/O, emitted an event, or hit the network beyond **side effects allowed** |
| `AMBIENT_CONFIG` | Read config from a global or shared store rather than a value passed in, or read a key outside **config scope** |

`SCOPE_EXCEEDED` is the blast-radius signal. Log the **delta** — the specific files touched beyond declared scope — not the full touched set.

### Friction flags

| Flag | Fires when |
|---|---|
| `RETRY_LOOP` | More than **3** attempts or test-failure cycles before the change landed |
| `WIDE_FAN_OUT` | A single-concern task touched more than **5** files, or files in more than **1** module |
| `CONTEXT_PULL` | Needed to read more than **3** other modules to make a change in this one |

### Duplication flags

| Flag | Fires when |
|---|---|
| `KNOWN_DUPLICATE` | Found existing equivalent logic during search, and wrote new code anyway. **Log the reason.** |
| `COPY_WITHOUT_ABSTRACTION` | Wrote a block substantially identical to one written earlier in this session |

Before writing any non-trivial logic, search for an existing implementation. If one exists and you do not reuse it, that is `KNOWN_DUPLICATE` — record why (incompatible signature, different lifecycle, deliberate divergence, or none).

### Recurrence flag

| Flag | Fires when |
|---|---|
| `RETURN_TO_LOCATION` | Editing a file or module changed within the last **3** working sessions |

Fires in both contexts — a feature edit returning to recent territory, and a bug fix landing where something was recently fixed. Set `detail.context` to `"development"` or `"bugfix"` so Doc 3 can separate them without a second flag.

Repeated fires on the same location, in either context, mean the earlier change did not settle. That is the signal, regardless of what prompted the return.

### Bug flags — narrow scope only

Log a bug **only** if it meets one of these. Ordinary self-contained bugs go to the normal tracker and never here.

| Flag | Fires when |
|---|---|
| `CROSS_MODULE_BUG` | The fix required touching files outside the module where the bug appeared |
| `FIX_BROKE_ELSEWHERE` | The fix caused a failure in a module it did not intend to touch |

A bug landing in a recently-fixed location fires `RETURN_TO_LOCATION` with `context: "bugfix"`, not a separate flag.

`FIX_BROKE_ELSEWHERE` is the strongest single signal in this document. It is confirmed coupling cost, not suspected.

### Capture flag

| Flag | Fires when |
|---|---|
| `UNCOMMITTED_WORK` | The pass ends with changes still uncommitted in source directories |

Log it with `commit: null`. This makes the capture gap visible as data instead of silently degrading every git-based lens downstream.

---

## 4. Thresholds

Read `.signals/thresholds.json` at load. If it is absent or unreadable, use the inline defaults above — they work on day one without calibration.

Doc 3 owns the authoritative values and writes that file. An architectural audit (Doc 1) may propose refinements from this codebase's actual distributions; those flow through Doc 3, never directly into this file.

Do not tune thresholds mid-session. A noisy flag is Doc 3's problem to resolve, not a reason to silence it.

---

## 5. Log format

Append to `.signals/log.jsonl`. One line per flag. No entry when nothing fires.

```json
{
  "ts": "2026-09-29T14:22:10Z",
  "flag": "SCOPE_EXCEEDED",
  "module": "billing",
  "task": "add proration to invoice generation",
  "commit": "a3f9c21",
  "req_id": "proration",
  "detail": {
    "declared_scope": ["src/billing/**"],
    "delta": ["src/notifications/templates.py", "src/core/tax.py"]
  },
  "note": "Proration changed the invoice line-item shape, so the email template that renders line items had to change with it. Tax rounding lives in core/tax.py and the proration math needed it."
}
```

Required fields: `ts`, `flag`, `module`, `task`, `commit`. Put flag-specific evidence in `detail`.

`commit` is the SHA of the change this flag describes, or `null` when the work was not committed (which is `UNCOMMITTED_WORK` firing). It is the join to the diff: with it, Doc 3 can open the actual change; without it, a flag is an assertion with no evidence behind it.

`req_id` joins the signal to its changelog entry and done log. Null for changes outside the feature pipeline — those join by SHA alone.

Do not list the full set of touched files. `git show` gives that from the SHA; duplicating it here only creates something that can drift.

Keep `detail` factual and machine-readable — Doc 3 aggregates these fields to detect trends.

### The `note` field

Optional. One to three sentences of plain narrative: what you were doing when the flag fired, and what forced it.

Write it whenever the structured fields alone would not make the entry legible to someone reading it weeks later with no memory of the task. Skip it when the flag is self-explanatory.

**Write:** what happened, and what the immediate cause was.
**Do not write:** whether the flag was justified, whether the coupling is acceptable, or what should be done about it.

The distinction matters because Doc 3 reads these to judge whether coupling is real. A note that says *"the email template renders invoice line items, so changing the line-item shape forced a change there"* gives Doc 3 the causal link it needs. A note that says *"this is fine, they're obviously related"* pre-empts the judgment and destroys the signal.

For `KNOWN_DUPLICATE`, the note is effectively required — the reason you did not reuse existing logic is the entire content of that flag.

---

## 6. Rules

1. **Log only on flag.** No entry means no flag fired. That is the expected case.
2. **Never suppress a flag** because it seems justified. Explain the circumstance in `note`; the flag still fires.
3. **One entry per flag**, not one per file. Multiple flags in one task means multiple entries.
4. **No interpretation.** Do not rank, score, or recommend. Doc 3 does that.
5. **Never narrate what shipped.** This log is exception-based. No summaries, no "added X" entries, nothing written for a large successful feature that flagged nothing. What shipped belongs in the changelog; what went wrong architecturally belongs here.
6. **Contracts are not optional abstractions.** If a minimalism or anti-abstraction directive is also loaded, contracts and seams introduced by the review protocol are exempt from it. Do not skip writing a declared interface on YAGNI grounds.
7. **A recurring flag on the same module may mean the contract is wrong**, not the code. Log it identically either way — Doc 3 makes that call.
