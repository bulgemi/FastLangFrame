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
- **Authelia**: Open-source identity provider for OAuth2/OIDC (Primary).
- **PyJWT**: For JWT token validation and RBAC.
- **FastAPI Security**: OAuth2 Password and Bearer Token flows with local JWT validation support for Authelia.

## Infrastructure & Deployment
- **Docker**: For containerizing agent projects.
- **Nginx**: Reverse proxy for HTTPS support and request routing.
- **Langfuse**: Self-hosted LLM observability and tracing platform.
- **Kubernetes (K8s)**: Target deployment platform.
- **Copier**: Template generation tool for bootstrapping new projects.

## Databases & Storage (Supported)
- **SQLModel (SQLAlchemy) & Alembic**: ORM and migration tool for relational databases (PostgreSQL, MySQL).
- **Redis**: For caching, temporary state storage, and service workers (shared by Authelia and Langfuse).
- **OpenSearch / VectorDB**: For RAG-based search and retrieval.