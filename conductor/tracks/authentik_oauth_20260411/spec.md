# Specification: Authentik OAuth Integration

## Overview
Integrate Authentik (an open-source Identity Provider) into the FastLangFrame project to provide OAuth2/OIDC authentication and authorization. The integration will encompass running Authentik via Docker Compose, securing the FastAPI backend, and enabling an OAuth login flow in the Streamlit UI. 

## Goals
- Provide a robust authentication and authorization mechanism using standard OAuth2.
- Secure the FastLangFrame API (FastAPI) and Frontend (Streamlit) using tokens issued by Authentik.
- Manage user roles and access control centrally in Authentik.

## Functional Requirements
1. **Dockerized Identity Provider:**
   - Add an Authentik container configuration to the project's main `docker-compose.yml`.
   - Configure default initial credentials (ID: `admin`, Password: `FastLangFrame1!`).
2. **FastAPI Backend Integration:**
   - Implement OAuth2/OIDC token validation using FastAPI's built-in `fastapi.security` modules.
   - Validate incoming JWT signatures locally using Authentik's public keys (JWKS).
   - Extract user roles/groups from the JWT and implement Role-Based Access Control (RBAC) on API endpoints.
3. **Streamlit UI Integration:**
   - Implement an OAuth2 login flow (redirect-based) in the Streamlit application.
   - Secure the main UI routes; redirect unauthenticated users to the Authentik login page.
   - Display user information (name, role) upon successful login.
4. **Configuration Management:**
   - Add necessary OAuth configuration variables (e.g., Client ID, Client Secret, Auth URL, Token URL, JWKS URL) to `.env.sample`.
   - Ensure the application loads these variables via the `settings.py` configuration.

## Non-Functional Requirements
- **Security:** Tokens should be securely handled and validated on every protected API request.
- **Performance:** JWT validation must be stateless and fast, relying on cached public keys where possible.

## Out of Scope
- Detailed management of Authentik user configurations beyond the initial admin setup and basic role definitions.
- Custom login page styling within Authentik.

## Acceptance Criteria
- [ ] Authentik container starts successfully via `docker-compose up` with the specified admin credentials.
- [ ] `.env.sample` includes all required Authentik connection variables.
- [ ] FastAPI backend successfully validates JWTs issued by Authentik and rejects invalid/expired tokens.
- [ ] FastAPI endpoints correctly enforce role-based access based on token claims.
- [ ] Streamlit UI successfully redirects users to Authentik for login and receives the authorization code/token upon return.
- [ ] The Streamlit UI displays authenticated user details and allows access to protected chat interfaces.