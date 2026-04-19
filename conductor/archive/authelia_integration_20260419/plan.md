# Implementation Plan

## Phase 1: Docker & Authelia Infrastructure Setup
- [x] Task: Setup Authelia Directory and Configuration Files (422e9f5, 8dba419)
    - [x] Create `authelia/config/configuration.yml` for Authelia settings (SQLite, local YAML backend, OIDC client for FastAPI).
    - [x] Create `authelia/config/users_database.yml` for local user definitions.
    - [x] Fix Authelia 4.38.10 configuration errors (secure scheme, cookies, encryption_key).
- [x] Task: Update `docker-compose.yml` (08d00a6, 8dba419)
    - [x] Add `redis` service (required for Authelia session state).
    - [x] Add `authelia` service mapping to `authelia/config` and exposing necessary ports.
    - [x] Pin Authelia version to 4.38.10 for stability.
- [ ] Task: Conductor - User Manual Verification 'Docker & Authelia Infrastructure Setup' (Protocol in workflow.md)

## Phase 2: FastAPI Authentication Integration (Test-Driven)
- [x] Task: Setup FastAPI Authentication Dependencies (04a2c7b)
    - [x] Ensure `httpx` dependency is available via Poetry (for introspection requests).
    - [x] Update `src/common/configs/` to include settings for Authelia Introspection URL, Client ID, and Client Secret.
- [x] Task: Implement Token Introspection Logic (ce42b4c)
    - [x] Write failing test for Authelia introspection token validation logic.
    - [x] Implement the authentication dependency to call Authelia's introspection endpoint (`/api/oidc/introspection`).
    - [x] Ensure tests pass.
- [x] Task: Protect API Endpoints (414ca78)
    - [x] Write failing tests to verify that protected endpoints return 401 Unauthorized without a valid token.
    - [x] Apply the new Authelia authentication dependency to relevant API routes.
    - [x] Ensure tests pass.
- [ ] Task: Conductor - User Manual Verification 'FastAPI Authentication Integration (Test-Driven)' (Protocol in workflow.md)

## Phase: Review Fixes
- [x] Task: Apply review suggestions (dfb4ef4)