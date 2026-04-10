# Specification: Fix ModuleNotFoundError for langchain_mcp_adapters in Streamlit Chat Test

## Overview
A bug was reported where running the Streamlit chat test for the research agent fails with `ModuleNotFoundError: No module named 'langchain_mcp_adapters'`. This is caused by the missing dependency `langchain-mcp-adapters` required for MCP (Model Context Protocol) integration in the templates. The fix involves adding this package to the project's dependencies using Poetry.

## Scope
- Add `langchain-mcp-adapters` to the project's `pyproject.toml` dependencies.
- Ensure the chat test runs successfully locally without this import error.

## Functional Requirements
- **FR-1**: The `streamlit` application for chat testing must start up without import errors for `langchain_mcp_adapters`.
- **FR-2**: The `pyproject.toml` must include `langchain-mcp-adapters` as a dependency and `poetry.lock` must be updated.

## Acceptance Criteria
- [ ] `langchain-mcp-adapters` is listed in `pyproject.toml`.
- [ ] `poetry run python -c "import langchain_mcp_adapters"` executes successfully.
- [ ] Running the Streamlit chat test locally for the research agent succeeds.

## Out of Scope
- Refactoring the MCP implementation or other unrelated dependencies.
