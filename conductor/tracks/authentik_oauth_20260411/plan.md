# Implementation Plan: Authentik OAuth Integration

## Phase 1: Environment & Infrastructure Setup [checkpoint: 04b7449]
- [x] Task: Update Configuration Models [63f9a10]
    - [x] Update `.env.sample` with Authentik OAuth connection variables (Client ID, Secret, URLs).
    - [x] Write failing test in `test_settings.py` to ensure OAuth settings are loaded correctly.
    - [x] Update `src/common/configs/settings.py` to parse and validate OAuth configuration.
    - [x] Ensure `test_settings.py` passes.
- [x] Task: Configure Authentik in Docker Compose [5c37e68]
    - [x] Add Authentik services (server, worker, redis, postgres) to main project's `docker-compose.yml` with default credentials (`admin`/`FastLangFrame1!`).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment & Infrastructure Setup' (Protocol in workflow.md) [04b7449]

## Phase 2: FastAPI Backend Security [checkpoint: 1caebdf]
- [x] Task: Implement JWT Validation Dependency [dced5d2]
    - [x] Write failing test for JWT signature validation and token decoding (mocking JWKS) in a new test file `test_auth.py`.
    - [x] Implement authentication dependency using `fastapi.security` to fetch JWKS and validate tokens.
    - [x] Ensure JWT validation tests pass.
- [x] Task: Implement Role-Based Access Control (RBAC) [dced5d2]
    - [x] Write failing test for role extraction and authorization logic in `test_auth.py`.
    - [x] Implement RBAC dependency to check for roles mapped from the Authentik token.
    - [x] Ensure RBAC tests pass.
    - [x] Update standard API endpoints to use the new auth dependencies.
- [x] Task: Conductor - User Manual Verification 'Phase 2: FastAPI Backend Security' (Protocol in workflow.md) [1caebdf]

## Phase 3: Streamlit UI Integration [checkpoint: b0b4c07]
- [x] Task: Implement OAuth Redirect Flow in Streamlit [dced5d2]
    - [x] Create UI components and logic for "Login with Authentik" button.
    - [x] Implement redirect to Authentik authorization URL.
    - [x] Implement callback logic to handle the authorization code exchange for tokens.
- [x] Task: Session Management in Streamlit [dced5d2]
    - [x] Store access tokens securely in Streamlit session state.
    - [x] Display authenticated user details (name, role) per sidebar logic.
    - [x] Restrict access to main application logic unless authenticated.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Streamlit UI Integration' (Protocol in workflow.md) [b0b4c07]