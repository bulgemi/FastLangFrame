# Product Guide

## Initial Concept
FastLangFrame is a flexible and lightweight framework designed for the rapid creation, testing, and deployment of LLM (Large Language Model) Agents. It provides standard architectures and templates (Simple, RAG, Multi-Agent, MCP, Deep) based on LangChain and LangGraph.

## Target Audience
- AI/ML Engineers and Developers looking for a standardized way to build LLM agents.
- Teams needing a rapid prototyping environment with built-in UI (Streamlit) and API server (FastAPI).

## Key Features
- **Project Generation**: CLI tool (`lapm`) to generate boilerplate projects from predefined templates.
- **Built-in API Server**: Standard FastAPI server with Swagger UI for every agent project.
- **Integrated Security**: Standard OAuth2 Password and Bearer Token authentication with RBAC, supporting local JWT validation via Authelia.
- **Interactive UI**: Streamlit-based chat interface for real-time node trace and testing.
- **Integrated Observability**: Self-hosted Langfuse instance for LLM tracing and monitoring.
- **Extensibility**: Support for MCP, Skills, and integrated database support (PostgreSQL) with standardized CRUD capabilities and migration management (Alembic).
- **Deployment Ready**: Included Dockerfiles and Kubernetes deployment manifests.

## Core Value Proposition
To accelerate the development lifecycle of LLM agents by providing a structured, unopinionated core with plug-and-play templates, reducing boilerplate and focusing on business logic.