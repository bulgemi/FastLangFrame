# Specification: Fix ModuleNotFoundError for langchain.schema in Streamlit Chat Test

## Overview
A bug was reported where running the Streamlit chat test locally using Poetry fails with `ModuleNotFoundError: No module named 'langchain.schema'`. This is caused by using newer versions of `langchain` where `langchain.schema` has been deprecated and moved to `langchain_core`. The fix involves updating the import statements to use `langchain_core`.

## Scope
- Update imports from `langchain.schema` to `langchain_core` in the relevant files used during the Streamlit chat test (specifically targeting the research agent).
- Ensure the chat test runs successfully locally via Poetry.

## Functional Requirements
- **FR-1**: The `streamlit` application for chat testing must start up without import errors.
- **FR-2**: All references to `langchain.schema` (such as `HumanMessage`, `SystemMessage`, `AIMessage`, etc.) should be replaced with their correct equivalents from `langchain_core.messages` or other relevant `langchain_core` modules.

## Acceptance Criteria
- [ ] Searching the codebase for `langchain.schema` yields 0 results.
- [ ] Running the Streamlit chat test locally for the research agent succeeds.
- [ ] Unit tests for the affected modules pass.

## Out of Scope
- Downgrading the `langchain` library to older versions.
- Modifying other agents not affected by this specific import error unless it's a shared library.
