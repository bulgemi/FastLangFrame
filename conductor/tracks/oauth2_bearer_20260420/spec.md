# Specification: Replace OIDC with OAuth 2.0 Bearer Token Authentication

## Overview
This track replaces the existing Authelia OIDC interactive login flow in the FastAPI server with standard OAuth 2.0 Bearer Token authentication. The FastAPI server will transition into a pure resource server, validating tokens via local JWT signature verification using Authelia's public keys. The Swagger UI will be configured to support the full OAuth 2.0 flow, allowing developers to authenticate directly through the Swagger interface.

## Functional Requirements
1. **Remove OIDC Interactive Flow:**
   - Remove existing OIDC client implementations (e.g., Authlib) and login/callback endpoints from the FastAPI server.
2. **Implement OAuth 2.0 Bearer Token Validation:**
   - Configure FastAPI to accept `Authorization: Bearer <token>` headers.
   - Implement local JWT validation using `PyJWT` and the Authelia public key.
   - Validate token claims (e.g., `iss`, `aud`, `exp`).
3. **Swagger UI OAuth2 Configuration:**
   - Configure FastAPI's OpenAPI schema to define an `OAuth2` security scheme (Authorization Code flow).
   - Set up the authorization URL and token URL in the Swagger configuration to point to Authelia's respective endpoints.
   - Ensure Swagger UI correctly initiates the OAuth2 flow to obtain the bearer token.
4. **Update Authentication Middleware/Dependencies:**
   - Update `get_current_user` dependencies to rely on the decoded JWT payload instead of session state.

## Non-Functional Requirements
- **Performance:** Local JWT validation must be fast and not introduce network latency.
- **Security:** Ensure robust signature verification and claim validation.

## Out of Scope
- Modifications to the Streamlit frontend's authentication mechanism.
- Deployment infrastructure changes.

## Acceptance Criteria
- [ ] FastAPI endpoints no longer redirect to Authelia for login.
- [ ] FastAPI endpoints successfully authenticate requests bearing a valid Authelia OAuth 2.0 token.
- [ ] Requests with invalid, expired, or missing tokens receive a `401 Unauthorized` response.
- [ ] Swagger UI displays the "Authorize" button, successfully executes the OAuth 2.0 flow against Authelia, and automatically attaches the token to API requests.