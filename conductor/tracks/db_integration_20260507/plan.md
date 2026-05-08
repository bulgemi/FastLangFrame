# Implementation Plan: FastAPI Database Integration

## Phase 1: Configuration and Connection Setup [checkpoint: 1adf7cd]
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
- [x] Task: Conductor - User Manual Verification 'Configuration and Connection Setup' (Protocol in workflow.md)

## Phase 2: Alembic Integration and Initial Migration [checkpoint: 083988b]
- [x] Task: Initialize Alembic in the project root. afea78c
    - [x] Run `alembic init alembic`.
- [x] Task: Configure Alembic to use the connection string from `settings.py`. afea78c
    - [x] Update `alembic/env.py` to load config dynamically.
- [x] Task: Define a baseline `SQLModel` for testing (e.g., a dummy `User` or `Item` model). afea78c
    - [x] Create a models module with a simple model.
- [x] Task: Configure Alembic `env.py` to discover `SQLModel` metadata. afea78c
    - [x] Import models and set `target_metadata = SQLModel.metadata`.
- [x] Task: Generate and apply the initial migration. afea78c
    - [x] Generate migration: `alembic revision --autogenerate -m "initial"`.
    - [x] Apply migration: `alembic upgrade head`.
- [x] Task: Conductor - User Manual Verification 'Alembic Integration and Initial Migration' (Protocol in workflow.md)

## Phase 3: Agent/CRUD Verification [checkpoint: ecd01cb]
- [x] Task: Create a simple CRUD operation test verifying the injected session. afea78c
    - [x] Write a test that uses `get_session` to create, read, update, and delete the dummy model.
    - [x] Ensure the test passes against a local PostgreSQL instance (or sqlite for testing if fallback is needed).
- [x] Task: Conductor - User Manual Verification 'Agent/CRUD Verification' (Protocol in workflow.md)

## Phase 4: Template Updates and Distribution
- [x] Task: Add `config.yaml` to agent templates to ensure DB support in new projects. afea78c
    - [x] Update `templates/simple_agent` with `config.yaml`.
    - [x] Update other templates (rag, multi, mcp, deep, research).
    - [x] Verify a new project can be created and run with DB support using `lapm`.
- [~] Task: Conductor - User Manual Verification 'Template Updates' (Protocol in workflow.md)