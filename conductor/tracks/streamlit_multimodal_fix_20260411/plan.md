# Implementation Plan: Fix ModuleNotFoundError for 'st_chat_input_multimodal'

## Phase 1: Setup and Red Phase [checkpoint: f277e8f]
- [x] Task: Reproduce the error by generating a deep agent project and running `streamlit run chat_test/app.py` without `poetry run` to confirm the `ModuleNotFoundError` for `st_chat_input_multimodal`.
- [x] Task: Verify whether `st_chat_input_multimodal` is defined in the project's dependencies (`pyproject.toml`) and correctly installed in the root Poetry environment.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Red Phase' (Protocol in workflow.md)

## Phase 2: Implementation (Green Phase) [checkpoint: b7a4e94]
- [x] Task: If the dependency is missing, add `st_chat_input_multimodal` to the `pyproject.toml` used by the templates.
- [x] Task: Ensure that running the Streamlit app with `poetry run streamlit run chat_test/app.py` within the generated project's virtual environment resolves the issue.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation (Green Phase)' (Protocol in workflow.md)

## Phase 3: Refactoring and Documentation [checkpoint: 8a93612]
- [x] Task: Review the core `README.md` and any relevant guides to ensure that the instruction for starting the Streamlit app explicitly uses `poetry run streamlit run chat_test/app.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Refactoring and Documentation' (Protocol in workflow.md)