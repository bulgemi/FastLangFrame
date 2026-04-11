# Specification: Fix ModuleNotFoundError for 'st_chat_input_multimodal'

## Overview
When running the Streamlit chat test in a newly generated deep agent project using `streamlit run auth_test/chat_test/app.py`, a `ModuleNotFoundError: No module named 'st_chat_input_multimodal'` occurs. This track will investigate whether this is an environment execution issue (e.g., not using `poetry run`) or a missing dependency in the generated project's `pyproject.toml`.

## Functional Requirements
- Investigate the usage of `st_chat_input_multimodal` in the `chat_test/app.py` template.
- Confirm whether `st_chat_input_multimodal` is included in the project's dependencies (`pyproject.toml`).
- Ensure the instructions for running the Streamlit app clearly specify the correct environment execution method (e.g., `poetry run streamlit run ...`) and verify that dependencies are correctly installed upon project creation.

## Non-Functional Requirements
- The fix must maintain compatibility with the core FastLangFrame repository.
- Development workflows for other templates should be consistent.

## Acceptance Criteria
- Generating a new deep agent and starting its Streamlit chat test UI completes successfully without a `ModuleNotFoundError` for `st_chat_input_multimodal`.
- Documentation (e.g., README.md or setup guides) accurately reflects the correct commands to run the Streamlit app.

## Out of Scope
- Architectural changes to the Streamlit UI itself.
- Changes to the underlying `st-chat-input-multimodal` library.