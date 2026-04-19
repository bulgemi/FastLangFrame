# Tech Stack

## Programming Language
- **Python 3.12**: Core language for the framework and agent projects.
- **Poetry**: Dependency management and packaging.

## Backend Frameworks
- **FastAPI**: Used for building the standard API server for agent projects.
- **LangChain & LangGraph**: Core libraries for LLM orchestration and state management.
- **DeepAgents**: Additional LLM orchestration layer.
- **Uvicorn / Gunicorn**: ASGI/WSGI servers for deployment.

## Frontend & Testing
- **Streamlit**: Provides the interactive chat UI for testing agents.
- **Pytest**: Primary testing framework.

## Security & Identity
- **Zitadel**: Open-source identity provider for OAuth2/OIDC.
- **PyJWT**: For JWT token validation and RBAC.
- **FastAPI Security**: OAuth2PasswordBearer flow for direct authentication and native JWT issuance.

## Infrastructure & Deployment
- **Docker**: For containerizing agent projects.
- **Kubernetes (K8s)**: Target deployment platform.
- **Copier**: Template generation tool for bootstrapping new projects.

## Databases & Storage (Supported)
- **SQLAlchemy & Alembic**: ORM and migration tool for relational databases (PostgreSQL, MySQL).
- **Redis**: For caching and temporary state storage.
- **OpenSearch / VectorDB**: For RAG-based search and retrieval.