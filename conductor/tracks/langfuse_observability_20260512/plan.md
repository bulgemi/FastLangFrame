# Implementation Plan: Langfuse Observability Integration via CallbackHandler

## Phase 1: Setup and Configuration
- [x] Task: Add `langfuse` and `langchain-openai` to project dependencies. (0c23ac6)
    - [x] Update `pyproject.toml` (and `requirements.txt` if needed) to include `langfuse` and `langchain-openai`.
    - [x] Update `.env.sample` with `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_HOST`.
- [x] Task: Implement Configuration Loading in Code. (60ab391)
    - [x] Write tests in `test/test_settings.py` to verify Langfuse settings are loaded correctly from environment variables.
    - [x] Update `src/common/configs/settings.py` to define and load Langfuse configurations.
    - [x] Ensure all tests pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Configuration' (Protocol in workflow.md)

## Phase 2: CallbackHandler Factory Implementation
- [ ] Task: Create Langfuse Callback Factory Utility.
    - [ ] Write tests for a new utility function (e.g., in `src/utils/observability.py`) that initializes the `CallbackHandler` with the appropriate User ID, Session ID, and Tags.
    - [ ] Implement the logic to instantiate the `CallbackHandler` securely, parsing metadata and gracefully handling missing configs.
    - [ ] Ensure all tests pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: CallbackHandler Factory Implementation' (Protocol in workflow.md)

## Phase 3: Core Engine Integration
- [ ] Task: Inject CallbackHandler into LangChain/LangGraph Core.
    - [ ] Write integration/unit tests simulating a graph run to ensure the callback handler is present in the execution config.
    - [ ] Modify `src/core/graph_builder.py` and `src/core/runtime/` to inject the Langfuse `CallbackHandler` dynamically.
    - [ ] Extract User ID from the authentication context (e.g., inside FastAPI dependencies) and pass it down to the Callback Factory.
    - [ ] Ensure all tests pass and existing agents run smoothly.
- [ ] Task: Update Agent Templates.
    - [ ] Apply the same injection logic to all generated project templates (`templates/*/`).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Core Engine Integration' (Protocol in workflow.md)