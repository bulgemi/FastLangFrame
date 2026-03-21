FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev
COPY . .
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "chat_test/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
