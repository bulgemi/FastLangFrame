# Implementation Plan: Change FastAPI Authentication to OAuth2PasswordBearer

## Phase 1: Core FastAPI Server Authentication Update
- [ ] Task: Update Dependencies and Configuration (Red Phase)
    - [ ] Write failing tests in `test/test_auth.py` that expect a Native JWT signed by the FastAPI server, and verify removal of OIDC specific config.
    - [ ] Write failing test for the new `/token` endpoint expecting `username` and `password`.
- [ ] Task: Implement Native JWT and `/token` endpoint (Green Phase)
    - [ ] Update `src/common/configs/settings.py` to remove Authentik OIDC specific variables and add variables for PyJWT (secret key, algorithm).
    - [ ] Create the `/token` endpoint in `src/core/server.py` using `OAuth2PasswordRequestForm`.
    - [ ] Implement logic to verify credentials against Authentik IDP (e.g., via a back-channel request to Authentik).
    - [ ] Implement logic to issue a Native JWT using PyJWT upon successful verification.
    - [ ] Ensure tests pass.
- [ ] Task: Update Security Dependencies (Green Phase)
    - [ ] Replace existing OIDC dependency with `OAuth2PasswordBearer(tokenUrl="token")` in `src/common/middleware/auth.py`.
    - [ ] Update JWT decoding logic to verify the Native JWT instead of the Authentik JWKS.
    - [ ] Ensure all protected endpoints correctly authorize using the new token.
    - [ ] Ensure tests pass.
- [ ] Task: Remove Old OIDC Code (Refactoring)
    - [ ] Delete any remaining OIDC login/callback endpoints and related session state logic from the backend.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core FastAPI Server Authentication Update' (Protocol in workflow.md)

## Phase 2: Template Updates
- [ ] Task: Apply backend changes to templates (Red Phase)
    - [ ] Write failing tests (or define manual checks) for the template generation to ensure templates lack the old OIDC code.
- [ ] Task: Update template files (Green Phase)
    - [ ] Replicate the changes made in Phase 1 to all project templates in `templates/*/`.
    - [ ] Ensure the generated code uses `OAuth2PasswordBearer` and Native JWTs.
    - [ ] Ensure tests pass for the generated projects.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Template Updates' (Protocol in workflow.md)

## Phase 3: Streamlit UI Updates
- [ ] Task: Update Streamlit Authentication UI (Red Phase)
    - [ ] Define tests or a clear manual verification process for the new Streamlit login flow.
- [ ] Task: Implement Standard Login Form (Green Phase)
    - [ ] Remove the "Login with Authentik" redirect logic in `src/utils/auth_streamlit.py`.
    - [ ] Create a Streamlit form with `st.text_input` for Username and Password.
    - [ ] Implement the submit action to make a POST request to the backend `/token` endpoint.
    - [ ] Store the received Native JWT in Streamlit's session state securely.
    - [ ] Ensure the app correctly identifies the authenticated user from the Native JWT.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Streamlit UI Updates' (Protocol in workflow.md)