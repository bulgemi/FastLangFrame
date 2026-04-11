# Specification: Fix ModuleNotFoundError for 'deepagents'

## Overview
When generating a new deep agent project using the `deep_agent` template and running its `main.py`, a `ModuleNotFoundError: No module named 'deepagents'` occurs. The goal of this track is to identify the root cause of the missing module and fix the template, dependencies, or instructions so that the generated agent runs out of the box.

## Functional Requirements
- Investigate the import statement `from deepagents import create_deep_agent` in `templates/deep_agent/<%project_name%>/graph/builder.py`.
- Determine whether the `deepagents` package is not correctly installed, not properly specified in the generated project's dependencies, or if there's a typo in the import name.
- Fix the issue by either updating the import in the template, ensuring `deepagents` is added to the generated dependencies, or updating the instructions on how to run the agent (e.g., using a specific virtual environment).

## Non-Functional Requirements
- The fix must maintain compatibility with the core FastLangFrame repository.
- Development workflows for other templates should not be affected.

## Acceptance Criteria
- Generating a new deep agent and starting its FastAPI server completes successfully without a `ModuleNotFoundError` for `deepagents`.
- The fix is verified by executing the generated agent's `main.py` in the appropriate environment.

## Out of Scope
- Architectural changes to the `deepagents` library.
- Fixes to other templates not related to this specific import issue.