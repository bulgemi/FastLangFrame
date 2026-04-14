# Track Specification: FastAPI OAuth2 Authentication via Local Authentik

## Overview
Implement an OAuth2 Password Flow authentication mechanism in the FastAPI server. This flow will authenticate users against a local instance of Authentik running at `http://localhost:9000/`. The implementation will specifically verify a manually created test user (`ID: user01`, `Password: user01`) and protect relevant API endpoints. The track also includes the necessary configuration steps within Authentik to set up the OAuth2 provider.

## Functional Requirements
1.  **FastAPI Authentication Endpoint:** Implement a `/token` endpoint in FastAPI that accepts OAuth2 password request form data (username, password).
2.  **Authentik Integration:** The `/token` endpoint must validate the provided credentials against the local Authentik instance (using an appropriate back-channel request or direct OIDC token exchange for the password grant type).
3.  **API Protection:** Implement a dependency injection in FastAPI (`OAuth2PasswordBearer`) to protect specific endpoints. This dependency should validate the token returned upon successful login.
4.  **Authentik Configuration Documentation/Steps:** Provide clear, reproducible steps to configure Authentik, including setting up an Application, a Provider (OAuth2/OIDC with Password flow enabled), and ensuring the test user can authenticate.

## Non-Functional Requirements
-   **Security:** Passwords must not be logged or exposed. Tokens must be handled securely according to OAuth2 best practices.
-   **Local Development:** The solution must work out-of-the-box with a default Authentik deployment on `localhost:9000`.

## Acceptance Criteria
-   [ ] A test user (`user01`/`user01`) is manually created in the local Authentik instance.
-   [ ] Authentik is configured with an OAuth2 provider supporting the password grant flow.
-   [ ] A POST request to FastAPI's `/token` endpoint with valid credentials (`user01`/`user01`) returns a valid access token.
-   [ ] A GET request to a protected FastAPI endpoint without a token returns a `401 Unauthorized`.
-   [ ] A GET request to a protected FastAPI endpoint with a valid access token succeeds.
-   [ ] A POST request to the `/token` endpoint with invalid credentials returns an appropriate error.

## Out of Scope
-   Automated provisioning of the `user01` account within Authentik.
-   Streamlit UI integration for the login flow (this track focuses solely on the FastAPI backend).
-   Role-Based Access Control (RBAC) mapping from Authentik groups to FastAPI roles.