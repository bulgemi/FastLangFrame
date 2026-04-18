# Implementation Plan: Migrate from Authelia to Zitadel

## Phase 1: Infrastructure and Setup
- [ ] Task: Update Docker Compose
    - [ ] Remove the Authelia service and its volume from `docker-compose.yml`.
    - [ ] Add a Zitadel PostgreSQL service to `docker-compose.yml`.
    - [ ] Add the Zitadel server service (and init container if required) to `docker-compose.yml`.
- [ ] Task: Configure Zitadel
    - [ ] Create initial configuration for Zitadel (e.g., machine keys, basic settings).
    - [ ] Document the Zitadel setup, initialization, and configuration process in a new file (`docs/zitadel_setup.md`).
    - [ ] Delete `docs/authelia_setup.md` and the `authelia/` directory.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Infrastructure and Setup' (Protocol in workflow.md)

## Phase 2: FastAPI Backend Implementation (Red/Green/Refactor)
- [ ] Task: Write Failing Tests (Red Phase)
    - [ ] Rename `test/test_authelia_auth.py` to `test_zitadel_auth.py`.
    - [ ] Update tests to expect a `verify_credentials_with_zitadel` function and ensure they fail (Red phase).
- [ ] Task: Implement Authentication Flow (Green Phase)
    - [ ] Update `src/common/configs/settings.py` to remove `AUTHELIA_*` variables and add `ZITADEL_*` variables (e.g., `ZITADEL_TOKEN_URL`, `ZITADEL_CLIENT_ID`, `ZITADEL_CLIENT_SECRET`).
    - [ ] Update `src/common/middleware/auth.py` to replace `verify_credentials_with_authelia` with `verify_credentials_with_zitadel`.
    - [ ] Update `src/core/server.py`'s `/token` endpoint to use the new Zitadel verification function.
    - [ ] Update tests to mock Zitadel responses and ensure they pass.
- [ ] Task: Refactoring and Code Quality
    - [ ] Ensure no traces of Authelia remain in the core python files (`src/`).
    - [ ] Run the test suite and ensure all tests pass (>80% coverage).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: FastAPI Backend Implementation (Red/Green/Refactor)' (Protocol in workflow.md)

## Phase 3: Template and Project Cleanup
- [ ] Task: Synchronize Templates
    - [ ] Update `.env.sample` in the project root to replace Authelia configuration with Zitadel.
    - [ ] Update `.env` files in all templates (`templates/*/`) to use the new Zitadel variables.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Template and Project Cleanup' (Protocol in workflow.md)