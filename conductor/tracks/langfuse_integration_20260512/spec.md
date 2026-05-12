# Specification: Langfuse Docker Compose Integration

## 1. Overview
Integrate a self-hosted Langfuse instance into the existing FastLangFrame `docker-compose.yml` to provide LLM observability and tracing. The setup will utilize the existing PostgreSQL container for storage and introduce a new Redis container for caching and background workers.

## 2. Functional Requirements
- **Langfuse Web/Server Container**:
  - Add the official Langfuse Docker image to `docker-compose.yml`.
  - Expose the Langfuse Web UI on host port `3000`.
  - Configure environment variables for Langfuse (Database connection, NextAuth secret, Salt, etc.).
- **Database Integration**:
  - Utilize the existing PostgreSQL container (`postgres`).
  - Configure an initialization script (e.g., in `/docker-entrypoint-initdb.d/`) or a pre-start command to create a dedicated logical database (e.g., `langfuse`) for Langfuse.
- **Redis Container**:
  - Add a Redis container to `docker-compose.yml` to support Langfuse caching and worker queues.
  - Configure Langfuse to connect to this Redis instance.

## 3. Non-Functional Requirements
- **Configuration Management**: Extract sensitive Langfuse configurations (secrets, salts) to `.env` / `.env.sample`.
- **Dependencies**: Ensure the Langfuse container depends on the `postgres` and `redis` containers starting successfully.

## 4. Acceptance Criteria
- [ ] Running `docker compose up -d` successfully starts Langfuse, Redis, and existing services without errors.
- [ ] The Langfuse Web UI is accessible at `http://localhost:3000`.
- [ ] Langfuse can successfully connect to the existing PostgreSQL instance and the new Redis instance.
- [ ] The `docker-compose.yml` and `.env.sample` files are updated with the necessary configurations.

## 5. Out of Scope
- Integration of Langfuse SDKs into specific agent codebases (this track focuses on infrastructure setup).
- Configuring advanced Langfuse features like SSO or custom domains beyond basic local hosting.