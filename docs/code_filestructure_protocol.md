Structure Creation Protocol

You are an AI coding agent. Your task is to create the project file structure only. Do not implement logic, write business code, or populate documentation. Create directories and empty files only.

Architecture standard: use a lightweight DDD-style modular monolith.

This means: create one single codebase organized mainly by domain/problem concepts, with separate folders for workflow orchestration and external technical adapters.

In practice:

Domain folders represent core problem areas.

application/ coordinates workflows and use cases.

infrastructure/ handles files, databases, APIs, config loading, serialization, and other external systems.

cli.py is only the command entrypoint.

Documentation files are created empty; another protocol will populate them.

Required input

Read the project spec provided by the user and extract only what is needed to create the structure:

Project name.

Language/runtime.

Main domain concepts.

Main workflows/use cases.

External inputs and outputs.

External systems.

Experiment or scenario needs.

Reporting or audit needs.

Data artifact needs.

If information is missing, infer conservatively.

Mandatory root structure

Always create:

project/

project/.gitignore

project/README.md

project/requirements.txt

project/configs/

project/docs/

project/docs/architecture.md

project/docs/decisions/

project/docs/decisions/README.md

project/tests/

project/src/

For Python projects, also create:

project/pyproject.toml

requirements.txt is mandatory, even when pyproject.toml exists.

All files created by this protocol must be empty unless another instruction explicitly says otherwise.

Python source package

For Python projects, create:

project/src/project_name/

project/src/project_name/__init__.py

project/src/project_name/cli.py

project/src/project_name/application/

project/src/project_name/application/__init__.py

project/src/project_name/application/README.md

project/src/project_name/infrastructure/

project/src/project_name/infrastructure/__init__.py

project/src/project_name/infrastructure/README.md

Normalize the package name:

School Matching becomes school_matching.

Use lowercase and snake_case.

Required core directories

Create these by default:

configs/: runtime configuration and scenario files.

docs/: architecture and project documentation.

docs/decisions/: architecture decision records.

tests/: test structure mirroring source boundaries.

src/: importable source package.

application/: orchestration and use-case workflows.

infrastructure/: external adapters and technical I/O boundaries.

Optional root directories

Create these only when justified by the project spec:

data/: data artifacts.

reports/: generated figures, tables, summaries, or audit outputs.

notebooks/: exploration only.

scripts/: developer or maintenance scripts.

assets/: static resources.

Do not create optional directories by habit.

Domain module discovery

Create domain modules under:

project/src/project_name/<domain_name>/

A domain module is justified when at least three of these are true:

It has its own vocabulary.

It has its own rules.

It changes for a different reason than other modules.

It contains objects or entities reused across workflows.

It should be testable independently.

A non-programmer stakeholder would recognize it.

Examples of domain modules:

students/

schools/

assignment/

policies/

evaluation/

experiments/

Avoid vague modules:

utils/

helpers/

misc/

common/

core/

Create vague modules only if explicitly required by the spec.

Domain module structure

For every domain module, create:

project/src/project_name/<domain_name>/

project/src/project_name/<domain_name>/__init__.py

project/src/project_name/<domain_name>/README.md

Both files must be empty.

Test structure

Mirror source boundaries under tests/.

For example, if source contains:

project/src/project_name/application/

project/src/project_name/infrastructure/

project/src/project_name/assignment/

project/src/project_name/evaluation/

Then create:

project/tests/application/

project/tests/infrastructure/

project/tests/assignment/

project/tests/evaluation/

Create directories only. Do not write tests.

Dependency direction to preserve in structure

Design the structure so future code should follow this dependency direction:

cli.py → application/ → domain modules

application/ → infrastructure/

Domain modules should not be structured around direct dependency on:

cli.py

application/

notebooks/

reports/

scripts/

Config structure

Always create:

project/configs/

Do not create config files unless the spec explicitly names them.

Documentation structure

Always create:

project/docs/

project/docs/architecture.md

project/docs/decisions/

project/docs/decisions/README.md

These files must be empty.

Root file rules

Always create empty:

project/README.md

project/requirements.txt

project/.gitignore

For Python projects, create empty:

project/pyproject.toml

Do not populate these files in this protocol.

Naming rules

Use lowercase directory names.

Use snake_case for Python packages.

Use clear domain names.

Do not use spaces.

Do not use ambiguous abbreviations.

Use singular or plural naming consistently.

Creation procedure

First, read the project spec.

Second, identify project name and runtime.

Third, normalize the package name.

Fourth, create mandatory root files and directories.

Fifth, create Python-specific files if applicable.

Sixth, identify justified domain modules.

Seventh, create domain directories under src/project_name/.

Eighth, create empty README.md and __init__.py inside every source module.

Ninth, create matching test directories.

Tenth, add optional root directories only when justified.

Finally, stop.

Final self-check

Before finishing, verify that:

requirements.txt exists.

Root README.md exists.

.gitignore exists.

Source code lives under src/project_name/.

application/ exists.

infrastructure/ exists.

Domain modules are justified.

Every source module has empty README.md and __init__.py.

Tests mirror source boundaries.

Docs structure exists.

No business logic was implemented.

No documentation content was populated.