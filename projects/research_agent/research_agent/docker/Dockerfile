FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
# 1. Install dependencies (using the project's pyproject.toml from the root context)
COPY projects/research_agent/research_agent/pyproject.toml /app/projects/research_agent/research_agent/pyproject.toml
WORKDIR /app/projects/research_agent/research_agent
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

# 2. Copy framework 'src' and project files
WORKDIR /app
COPY src ./src
COPY projects/research_agent/research_agent ./research_agent
# Copy .env from project root if it exists
COPY projects/research_agent/.env* ./research_agent/

# 3. Setup runtime environment
ENV PYTHONPATH=/app
WORKDIR /app/research_agent
EXPOSE 8888
ENTRYPOINT ["sh", "-c", "gunicorn main:app --workers $(nproc) --worker-class uvicorn.workers.UvicornWorker --threads 3 --bind 0.0.0.0:8888"]
