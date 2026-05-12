# Implementation Plan: Langfuse Docker Compose Integration

## Phase 1: Configuration & Redis Setup
- [x] Task: Add Langfuse configuration variables (`NEXTAUTH_SECRET`, `SALT`, `NEXTAUTH_URL`, `TELEMETRY_ENABLED`) to `.env.sample`. 1e4c6f9
- [x] Task: Add Redis service definition to `docker-compose.yml`. 7d0e011
- [ ] Task: Conductor - User Manual Verification 'Configuration & Redis Setup' (Protocol in workflow.md)

## Phase 2: PostgreSQL Database Initialization
- [ ] Task: Create a PostgreSQL initialization script (e.g., `postgres-init/init-langfuse-db.sql`) to automatically create the `langfuse` logical database on startup.
- [ ] Task: Update the `postgres` service in `docker-compose.yml` to mount the initialization script to `/docker-entrypoint-initdb.d/`.
- [ ] Task: Conductor - User Manual Verification 'PostgreSQL Database Initialization' (Protocol in workflow.md)

## Phase 3: Langfuse Container Integration
- [ ] Task: Add the `langfuse` service definition to `docker-compose.yml`.
    - [ ] Expose host port `3000` to container port `3000`.
    - [ ] Configure environment variables to connect to `postgres` and `redis`.
    - [ ] Set `depends_on` for `postgres` and `redis`.
- [ ] Task: Conductor - User Manual Verification 'Langfuse Container Integration' (Protocol in workflow.md)