# Specification: Change FastAPI Authentication to OAuth2PasswordBearer

## 1. Overview
The goal of this track is to replace the existing Authentik OIDC (Authorization Code) flow with the OAuth2 `password` flow (`OAuth2PasswordBearer`) in the FastLangFrame ecosystem. This change will allow users and API clients to authenticate directly by providing a username and password to the FastAPI server.

## 2. Functional Requirements
*   **Token Endpoint:** Create a `/token` endpoint in the FastAPI server that accepts `username` and `password` via `OAuth2PasswordRequestForm`.
*   **Credential Verification:** The FastAPI server must verify the submitted credentials against the Authentik Identity Provider (IDP) (e.g., using a back-channel API call or by proxying the password grant).
*   **JWT Issuance:** Upon successful verification with Authentik, the FastAPI server will generate and issue its own Native JWT using PyJWT for subsequent API authorization.
*   **Dependency Update:** Update the FastAPI security dependency from the existing OIDC/JWKS implementation to use `OAuth2PasswordBearer(tokenUrl="token")`.
*   **Complete Replacement:** Completely remove the existing OIDC flow, redirect endpoints, and related session management logic from the codebase.
*   **Global Scope:**
    *   Apply the new authentication flow to the core FastAPI server (`src/core/server.py` and related auth middleware/dependencies).
    *   Apply the changes to the project templates (`templates/*/`).
    *   Update the Streamlit UI to present a standard login form (Username/Password fields) instead of an "OAuth Login" redirect button.

## 3. Non-Functional Requirements
*   **Security:** Ensure passwords are never logged or stored locally by the FastAPI server; they must only be transmitted to Authentik for verification over a secure channel.
*   **Consistency:** The generated JWTs must maintain compatibility with the existing Role-Based Access Control (RBAC) structures if applicable, mapping Authentik roles to the local JWT claims.

## 4. Acceptance Criteria
*   [ ] A client can send a POST request with `username` and `password` to the `/token` endpoint and receive a valid JWT in response.
*   [ ] Accessing protected API endpoints with the newly issued JWT succeeds (200 OK).
*   [ ] Accessing protected API endpoints without a token or with an invalid token fails with a 401 Unauthorized error.
*   [ ] The Streamlit UI displays a native login form and successfully authenticates users via the backend `/token` endpoint.
*   [ ] All previous OIDC-specific code, dependencies, and configuration variables are removed from the core project and templates.

## 5. Out of Scope
*   Implementing user registration or password reset flows (these will remain managed by Authentik).