# Specification: Authelia Integration

## Overview
Integrate Authelia as an OAuth2/OIDC identity provider for the FastLangFrame ecosystem. Authelia will be deployed via the existing `docker-compose.yml` to provide unified authentication. FastAPI will be configured to protect its API endpoints by requiring OAuth 2.0 Bearer tokens and validating them using Authelia's Token Introspection endpoint.

## Functional Requirements
1. **Docker Compose Integration**: Add Authelia and Redis (required for Authelia session/state) services to the existing `docker-compose.yml`.
2. **Authelia Configuration**:
   - Configure Authelia to use SQLite for database storage.
   - Configure Authelia to use a Local YAML file for user directory/management.
   - Configure Authelia as an OIDC provider, defining an OIDC client for the FastAPI backend.
3. **FastAPI Integration**:
   - Implement an authentication dependency in FastAPI that extracts the Bearer token from the `Authorization` header.
   - Integrate with Authelia's Token Introspection endpoint to validate the extracted token.
   - Protect relevant API routes using this new dependency.

## Non-Functional Requirements
- **Security**: Tokens must be handled securely. Secrets for Authelia (like JWT secret, session secret) must be managed via environment variables.
- **Performance**: Use efficient HTTP client settings (e.g., connection pooling via `httpx`) in FastAPI for introspection requests.

## Acceptance Criteria
- [ ] `docker-compose up` successfully starts the main application, Authelia, and Redis.
- [ ] Users can log in to Authelia using credentials defined in the local YAML file.
- [ ] FastAPI rejects requests to protected endpoints with `401 Unauthorized` when no token or an invalid token is provided.
- [ ] FastAPI allows requests to protected endpoints when a valid Bearer token is provided, successfully verifying it via Authelia's Introspection endpoint.

## Out of Scope
- LDAP/Active Directory integration (using Local YAML).
- PostgreSQL integration for Authelia (using SQLite).
- Stateless JWKS token validation (using Token Introspection).