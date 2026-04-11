# Implementation Plan: Gemini API Key Not Valid in Streamlit Chat Test

## Phase 1: Investigation and Bug Fix [checkpoint: 6bbee66]
- [x] Task: Locate the codebase where the Gemini provider (`provider=gemini`) is initialized and the API key is retrieved for the `research_agent`. 5a8c6d4
- [x] Task: Write failing unit test(s) to simulate a missing or invalid `GOOGLE_API_KEY` for the Gemini provider, expecting a clear, fast failure rather than the Streamlit `RuntimeError` (Red Phase). 5b840d2
- [x] Task: Implement the fix in the agent backend to correctly retrieve `GOOGLE_API_KEY` and fail fast if missing/invalid (Green Phase). 27724c9
- [x] Task: Run the test suite to confirm the new test passes and no other tests are broken. 27724c9
- [x] Task: Conductor - User Manual Verification 'Phase 1: Investigation and Bug Fix' (Protocol in workflow.md) 6bbee66

## Phase 2: System Validation
- [ ] Task: Run `streamlit run projects/research_agent/chat_test/app.py` with the `GOOGLE_API_KEY` correctly set in `.env` to verify the error is resolved.
- [ ] Task: Run the full test suite and verify test coverage meets the >80% requirement.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: System Validation' (Protocol in workflow.md)