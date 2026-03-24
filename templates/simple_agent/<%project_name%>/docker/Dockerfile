FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root
COPY . .
EXPOSE 8888
ENTRYPOINT ["sh", "-c", "gunicorn main:app --workers $(nproc) --worker-class uvicorn.workers.UvicornWorker --threads 3 --bind 0.0.0.0:8888"]
