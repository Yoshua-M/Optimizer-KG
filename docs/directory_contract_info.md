````markdown
# Directory Contracts

You are an AI coding agent. Use this file to understand what each major directory is for. This file defines responsibilities only. Do not implement logic from this file.

## Root

The project root contains project-level metadata, dependency files, documentation entrypoints, and top-level directories.

Required:

```text
README.md
requirements.txt
.gitignore
````

Required for Python:

```text
pyproject.toml
```

Do not place domain logic in the root.

## `README.md`

Purpose:

* Explain the project goal.
* Summarize the structure.
* Provide minimal install/run notes when known.

Allowed:

* brief project description
* directory overview
* known assumptions

Forbidden:

* detailed architecture contracts
* long implementation notes
* hidden business rules

## `requirements.txt`

Purpose:

* List Python dependencies required by the project.

Rules:

* This file is mandatory.
* Keep it explicit and simple.
* Use it even when `pyproject.toml` also exists.
* Leave a placeholder comment if dependencies are unknown.

Example:

```text
# Add runtime dependencies here.
```

## `pyproject.toml`

Purpose:

* Store Python project metadata and tool configuration.

Allowed:

* project name
* version
* Python version
* dependencies mirror or complementing `requirements.txt`
* pytest config
* formatter/linter config when needed

Forbidden:

* business logic
* environment-specific secrets

## `.gitignore`

Purpose:

* Prevent generated, local, secret, or heavy files from being committed.

Should usually ignore:

```text
__pycache__/
.venv/
.env
.ipynb_checkpoints/
.pytest_cache/
dist/
build/
*.egg-info/
```

Add data/report ignores only when the project requires it.

## `configs/`

Purpose:

* Store runtime configuration and scenario parameters.

Allowed:

```text
base.json
local.example.json
experiment_<name>.json
production.example.json
```

Owns:

* run parameters
* file paths
* scenario switches
* environment-specific examples

Forbidden:

* secrets
* algorithm implementations
* domain rules hidden as code

## `docs/`

Purpose:

* Store project-level design and architecture documentation.

Required:

```text
docs/architecture.md
docs/decisions/
```

Owns:

* architecture summary
* assumptions
* major workflows
* design rationale
* decision records

Forbidden:

* implementation source code
* generated reports
* raw data

## `docs/architecture.md`

Purpose:

* Give future agents and developers the project-level architectural map.

Must include:

```markdown
# Architecture

## Goal

## Main domains

## Main workflows

## External inputs and outputs

## Config strategy

## Reporting/audit needs

## Dependency rules

## Assumptions
```

Keep it brief and factual.

## `docs/decisions/`

Purpose:

* Store architecture decision records.

Use for non-obvious decisions such as:

* choosing an algorithm
* separating a domain module
* introducing an infrastructure adapter
* changing config strategy
* adding audit/reporting structure

Filename format:

```text
0001-short-title.md
```

Decision template:

```markdown
# Decision: <title>

Status: accepted

## Context

## Decision

## Consequences
```

## `src/`

Purpose:

* Contain importable source code only.

Rules:

* All project package code goes here.
* Do not place notebooks, raw data, reports, or ad hoc scripts here.

Expected:

```text
src/project_name/
```

## `src/project_name/`

Purpose:

* Main importable package.

Required:

```text
__init__.py
cli.py
application/
infrastructure/
```

Add domain modules only when justified.

Forbidden:

* large orchestration in `__init__.py`
* business logic in `cli.py`
* vague modules without README contracts

## `src/project_name/cli.py`

Purpose:

* Thin command-line entrypoint.

Allowed:

* parse arguments
* load config
* call `application/`

Forbidden:

* domain rules
* algorithm code
* data cleaning
* plotting
* file-format logic beyond basic delegation

## `src/project_name/application/`

Purpose:

* Own use-case orchestration.

Examples:

```text
prepare_inputs.py
run_assignment.py
evaluate_results.py
compare_scenarios.py
```

Owns:

* workflow order
* calling domain services
* coordinating infrastructure adapters
* high-level application use cases

Does not own:

* domain entities
* domain rules
* low-level file I/O
* plotting internals
* algorithm internals

## `src/project_name/infrastructure/`

Purpose:

* Own external technical adapters.

Examples:

```text
config_loader.py
file_io.py
database.py
api_client.py
report_writer.py
```

Owns:

* file-system access
* database access
* API clients
* config loading
* report exporting
* serialization/deserialization

Does not own:

* domain decisions
* business rules
* algorithm logic
* evaluation definitions

## Domain modules

Purpose:

* Own core problem concepts and rules.

Location:

```text
src/project_name/<domain_name>/
```

Examples:

```text
students/
schools/
assignment/
policies/
evaluation/
experiments/
```

Each domain module must contain:

```text
README.md
__init__.py
```

Owns:

* domain entities
* domain rules
* domain-specific validation
* domain-specific services
* public interface for that concept

Does not own:

* CLI parsing
* workflow orchestration
* external file/database/API access
* generated reports
* notebooks

## `tests/`

Purpose:

* Mirror source architecture for future testing.

Expected:

```text
tests/
  application/
  infrastructure/
  <domain_1>/
  <domain_2>/
```

Rules:

* Create directories only.
* Do not write tests unless another instruction file asks for implementation.
* Test directories should correspond to source boundaries.

## `data/`

Purpose:

* Store data artifacts when the project requires data.

Recommended:

```text
data/
  raw/
  interim/
  processed/
```

Owns:

* raw data
* intermediate data
* processed data

Forbidden:

* source code
* business logic
* secrets

Create only when the spec mentions data artifacts.

## `reports/`

Purpose:

* Store generated outputs.

Recommended:

```text
reports/
  figures/
  tables/
  summaries/
```

Owns:

* generated charts
* tables
* run summaries
* final exported artifacts

Forbidden:

* source code
* raw data
* config secrets

Create only when the spec mentions reporting, audit, evaluation, or deliverables.

## `notebooks/`

Purpose:

* Store exploratory notebooks.

Rules:

* Notebooks are for exploration only.
* Core logic must later move into `src/`.
* Do not make notebooks part of the main architecture.

Create only when exploration is explicitly needed.

## `scripts/`

Purpose:

* Store developer or maintenance scripts.

Allowed:

* setup helpers
* migration helpers
* one-off maintenance commands

Forbidden:

* core domain logic
* main application workflows
* hidden production behavior

Create only when the spec requires support scripts.

## `assets/`

Purpose:

* Store static non-code resources.

Allowed:

* images
* templates
* static files
* example documents

Forbidden:

* raw datasets
* source code
* secrets

Create only when static resources are required.

## Module `README.md`

Purpose:

* Act as a contract for future agents.

Required template:

```markdown
# Module: <module_name>

## Purpose

## Owns

## Does not own

## Public interface

## Allowed dependencies

## Forbidden dependencies

## Related tests
```

Keep it short. The README defines the boundary; it does not implement the module.

## Final rule

When in doubt, create less structure, but make every created directory explicit, named, justified, and documented.

```
```
