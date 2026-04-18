# Implementation Plan: Migrate from Authentik to Authelia

## Phase 1: Infrastructure and Setup [checkpoint: 4c0ca97]
- [x] Task: Update Docker Compose (71b6570)
    - [x] Remove all Authentik-related services (server, worker, redis, postgres) from `docker-compose.yml`.
    - [x] Add Authelia service to `docker-compose.yml`, including volume mounts for configuration.
- [x] Task: Configure Authelia (6d9b1df)
    - [x] Create initial `configuration.yml` for Authelia, configuring an OIDC provider.
    - [x] Create `users_database.yml` with a test user (`user01`/`user01`).
    - [x] Document the Authelia setup and testing process in a new file (e.g., `docs/authelia_setup.md`).
    - [x] Delete `docs/authentik_setup.md`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Infrastructure and Setup' (Protocol in workflow.md) (4c0ca97)

## Phase 2: FastAPI Backend Implementation (Red/Green/Refactor) [checkpoint: 3b685d6]
- [x] Task: Write Failing Tests (Red Phase) (8dcae2b)
    - [x] Update `test/test_authentik_auth.py` (rename it to `test_authelia_auth.py`) to test the `/token` endpoint expecting it to fail with Authelia.
- [x] Task: Implement Authentication Flow (Green Phase) (d00f972)
    - [x] Update `src/common/configs/settings.py` to remove `AUTHENTIK_*` variables and add `AUTHELIA_*` variables (e.g., `AUTHELIA_TOKEN_URL`, `AUTHELIA_CLIENT_ID`, `AUTHELIA_CLIENT_SECRET`).
    - [x] Update `src/common/middleware/auth.py` to replace `verify_credentials_with_authentik` with `verify_credentials_with_authelia`.
    - [x] Update `src/core/server.py`'s `/token` endpoint to use the new Authelia verification function.
    - [x] Update tests to mock Authelia responses and ensure they pass.
- [x] Task: Refactoring and Code Quality (26c88f2)
    - [x] Ensure no traces of Authentik remain in the core python files.
    - [x] Run the test suite and ensure all tests pass (>80% coverage).
- [x] Task: Conductor - User Manual Verification 'Phase 2: FastAPI Backend Implementation (Red/Green/Refactor)' (Protocol in workflow.md) (3b685d6)

## Phase 3: Template and Project Cleanup
- [ ] Task: Synchronize Templates
    - [ ] Update `.env.sample` in the project root to replace Authentik configuration with Authelia.
    - [ ] Update `.env` files in all templates (`templates/*/`) to use the new Authelia variables.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Template and Project Cleanup' (Protocol in workflow.md)