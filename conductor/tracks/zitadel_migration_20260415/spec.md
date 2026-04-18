# Track Specification: Migrate from Authelia to Zitadel

## Overview
Completely replace Authelia with a self-hosted instance of Zitadel as the primary identity provider for the FastLangFrame framework. Zitadel will be deployed via Docker Compose using a PostgreSQL database backend. The FastAPI backend will maintain the current OAuth2 Password Grant flow, but it will authenticate against the new Zitadel instance instead of Authelia.

## Functional Requirements
1.  **Docker Compose Update:** Remove Authelia services and configurations from `docker-compose.yml` and add Zitadel services (including a PostgreSQL database instance dedicated to Zitadel) with the necessary configuration files.
2.  **Zitadel Configuration:** Configure the self-hosted Zitadel instance with an initial setup, an organization, a project, an application supporting the password grant flow, and a test user (`user01`/`user01`).
3.  **FastAPI Backend Update:** Update the `/token` endpoint and backend verification logic in `src/common/middleware/auth.py` and `src/core/server.py` to communicate with Zitadel's token endpoint.
4.  **Cleanup:** Completely remove all Authelia-specific variables from `src/common/configs/settings.py`, `.env.sample`, template `.env` files, and delete the `authelia/` configuration directory and related documentation.
5.  **Documentation:** Provide updated setup instructions for deploying and testing with Zitadel (e.g., `docs/zitadel_setup.md`).

## Non-Functional Requirements
-   **Security:** Ensure secure handling of client secrets, tokens, and database credentials.
-   **Local Development:** The Docker Compose setup must work seamlessly for local development and testing.

## Acceptance Criteria
-   [ ] `docker-compose.yml` successfully spins up Zitadel and its PostgreSQL database without errors.
-   [ ] A test user configured in Zitadel can successfully authenticate via a POST request to the FastAPI `/token` endpoint.
-   [ ] A GET request to a protected FastAPI endpoint using the issued token succeeds.
-   [ ] No traces of Authelia (code, config, or docs) remain in the core project or templates.

## Out of Scope
-   Complex multi-factor authentication (MFA) setups for the initial migration.
-   Federated login via external providers (Google, GitHub, etc.).