# Implementation Plan: Gemini API Key Not Valid in Streamlit Chat Test

## Phase 1: Investigation and Bug Fix
- [ ] Task: Locate the codebase where the Gemini provider (`provider=gemini`) is initialized and the API key is retrieved for the `research_agent`.
- [ ] Task: Write failing unit test(s) to simulate a missing or invalid `GOOGLE_API_KEY` for the Gemini provider, expecting a clear, fast failure rather than the Streamlit `RuntimeError` (Red Phase).
- [ ] Task: Implement the fix in the agent backend to correctly retrieve `GOOGLE_API_KEY` and fail fast if missing/invalid (Green Phase).
- [ ] Task: Run the test suite to confirm the new test passes and no other tests are broken.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Investigation and Bug Fix' (Protocol in workflow.md)

## Phase 2: System Validation
- [ ] Task: Run `streamlit run projects/research_agent/chat_test/app.py` with the `GOOGLE_API_KEY` correctly set in `.env` to verify the error is resolved.
- [ ] Task: Run the full test suite and verify test coverage meets the >80% requirement.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: System Validation' (Protocol in workflow.md)