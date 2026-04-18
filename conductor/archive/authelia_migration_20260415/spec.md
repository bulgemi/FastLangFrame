# Track Specification: Migrate from Authentik to Authelia

## Overview
Completely replace Authentik with Authelia as the primary identity provider for the FastLangFrame framework. Authelia will be deployed via Docker Compose and configured as an OIDC Provider. The FastAPI backend will maintain the current OAuth2 Password Grant flow, but it will authenticate against the new Authelia instance instead of Authentik.

## Functional Requirements
1.  **Docker Compose Update:** Remove Authentik services from `docker-compose.yml` and add Authelia services with the necessary configuration files.
2.  **Authelia Configuration:** Configure Authelia as an OpenID Connect (OIDC) provider that supports the Resource Owner Password Credentials Grant.
3.  **FastAPI Backend Update:** Update the `/token` endpoint and backend verification logic in `src/common/middleware/auth.py` and `src/core/server.py` to communicate with Authelia's OIDC token endpoint.
4.  **Cleanup:** Completely remove all Authentik-specific variables from `src/common/configs/settings.py`, `.env.sample`, template `.env` files, and any related documentation.
5.  **Documentation:** Provide updated setup instructions for deploying and testing with Authelia.

## Non-Functional Requirements
-   **Security:** Ensure secure handling of client secrets and tokens.
-   **Local Development:** The Docker Compose setup must work seamlessly for local development and testing.

## Acceptance Criteria
-   [ ] `docker-compose.yml` successfully spins up Authelia without errors.
-   [ ] A test user configured in Authelia can successfully authenticate via a POST request to the FastAPI `/token` endpoint.
-   [ ] A GET request to a protected FastAPI endpoint using the issued token succeeds.
-   [ ] No traces of Authentik (code, config, or docs) remain in the core project or templates.

## Out of Scope
-   Implementing Authelia's Forward Auth (Proxy) features for securing other services.
-   Complex multi-factor authentication (MFA) setups for the initial migration.