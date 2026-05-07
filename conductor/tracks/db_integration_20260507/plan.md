# Implementation Plan: FastAPI Database Integration

## Phase 1: Configuration and Connection Setup
- [x] Task: Update `config.yaml` (or sample) and `src/common/configs/settings.py` to support database connection strings (PostgreSQL). afea78c
    - [x] Write tests for settings loading DB configuration.
    - [x] Implement settings update.
- [x] Task: Implement database engine initialization in `src/utils/connectors/db/database.py`. afea78c
    - [x] Write unit tests for engine creation.
    - [x] Implement engine creation using `SQLModel`.
- [x] Task: Implement FastAPI dependency `get_session` as a yield generator in `src/utils/connectors/db/database.py`. afea78c
    - [x] Write unit tests for the dependency generator.
    - [x] Implement the `get_session` function.
- [x] Task: Integrate DB engine initialization into FastAPI app startup events (e.g., lifespan in `src/core/server.py`). afea78c
    - [x] Write integration test for app startup.
    - [x] Update app lifecycle to initialize DB.
- [~] Task: Conductor - User Manual Verification 'Configuration and Connection Setup' (Protocol in workflow.md)

## Phase 2: Alembic Integration and Initial Migration
- [ ] Task: Initialize Alembic in the project root.
    - [ ] Run `alembic init alembic`.
- [ ] Task: Configure Alembic to use the connection string from `settings.py`.
    - [ ] Update `alembic/env.py` to load config dynamically.
- [ ] Task: Define a baseline `SQLModel` for testing (e.g., a dummy `User` or `Item` model).
    - [ ] Create a models module with a simple model.
- [ ] Task: Configure Alembic `env.py` to discover `SQLModel` metadata.
    - [ ] Import models and set `target_metadata = SQLModel.metadata`.
- [ ] Task: Generate and apply the initial migration.
    - [ ] Generate migration: `alembic revision --autogenerate -m "initial"`.
    - [ ] Apply migration: `alembic upgrade head`.
- [ ] Task: Conductor - User Manual Verification 'Alembic Integration and Initial Migration' (Protocol in workflow.md)

## Phase 3: Agent/CRUD Verification
- [ ] Task: Create a simple CRUD operation test verifying the injected session.
    - [ ] Write a test that uses `get_session` to create, read, update, and delete the dummy model.
    - [ ] Ensure the test passes against a local PostgreSQL instance (or sqlite for testing if fallback is needed).
- [ ] Task: Conductor - User Manual Verification 'Agent/CRUD Verification' (Protocol in workflow.md)