# Implementation Plan: Langfuse Docker Compose Integration

## Phase 1: Configuration & Redis Setup [checkpoint: 186d404]
- [x] Task: Add Langfuse configuration variables (`NEXTAUTH_SECRET`, `SALT`, `NEXTAUTH_URL`, `TELEMETRY_ENABLED`) to `.env.sample`. 1e4c6f9
- [x] Task: Add Redis service definition to `docker-compose.yml`. 7d0e011
- [x] Task: Conductor - User Manual Verification 'Configuration & Redis Setup' (Protocol in workflow.md) 186d404

## Phase 2: PostgreSQL Database Initialization [checkpoint: 7c8a08f]
- [x] Task: Create a PostgreSQL initialization script (e.g., `postgres-init/init-langfuse-db.sql`) to automatically create the `langfuse` logical database on startup. f475770
- [x] Task: Update the `postgres` service in `docker-compose.yml` to mount the initialization script to `/docker-entrypoint-initdb.d/`. 08500ad
- [x] Task: Conductor - User Manual Verification 'PostgreSQL Database Initialization' (Protocol in workflow.md) 7c8a08f

## Phase 3: Langfuse Container Integration
- [ ] Task: Add the `langfuse` service definition to `docker-compose.yml`.
    - [ ] Expose host port `3000` to container port `3000`.
    - [ ] Configure environment variables to connect to `postgres` and `redis`.
    - [ ] Set `depends_on` for `postgres` and `redis`.
- [ ] Task: Conductor - User Manual Verification 'Langfuse Container Integration' (Protocol in workflow.md)