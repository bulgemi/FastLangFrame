# Implementation Plan: Replace OIDC with OAuth 2.0 Bearer Token Authentication

## Phase 1: Remove OIDC Flow and Update Auth Utilities [checkpoint: e3fe70f]
- [x] Task: Remove OIDC client (Authlib) configuration and login/callback endpoints from `src/core/server.py` and relevant auth modules. (249bbfa)
- [x] Task: Create/Update unit tests in `test/test_auth.py` to remove OIDC flow tests and prepare for JWT validation tests (Red Phase). (740e42a)
- [x] Task: Remove any OIDC-specific session management dependencies from FastAPI routes. (76c6034)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Remove OIDC Flow and Update Auth Utilities' (Protocol in workflow.md) (e3fe70f)

## Phase 2: Implement OAuth2 Bearer Token Validation
- [x] Task: Write failing unit tests in `test/test_auth.py` for decoding and validating JWT tokens using Authelia's public key (Red Phase). (90276a7)
- [x] Task: Implement `verify_token` utility in `src/common/middleware/auth.py` (consistent with existing) to perform local JWT validation using `PyJWT` (Green Phase). (c4f67a1)
- [x] Task: Write failing tests in `test/test_server.py` for API endpoints requiring Bearer tokens (Red Phase). (98fd110)
- [ ] Task: Update the `get_current_user` dependency in `src/core/server.py` (or equivalent) to use `fastapi.security.OAuth2AuthorizationCodeBearer` and the `verify_token` utility (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implement OAuth2 Bearer Token Validation' (Protocol in workflow.md)

## Phase 3: Configure Swagger UI OAuth2 Flow
- [ ] Task: Write a failing test in `test/test_openapi_schema.py` to assert the presence of the correct OAuth2 security scheme in the OpenAPI schema (Red Phase).
- [ ] Task: Configure the FastAPI app in `src/core/server.py` with `swagger_ui_init_oauth` and set up the OAuth2 scheme pointing to Authelia's `/api/oidc/authorization` and `/api/oidc/token` endpoints (Green Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Configure Swagger UI OAuth2 Flow' (Protocol in workflow.md)