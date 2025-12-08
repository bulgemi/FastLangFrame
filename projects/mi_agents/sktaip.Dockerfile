ARG PLATFORM_ARCH="linux/amd64"

FROM --platform=${PLATFORM_ARCH} python:3.12-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 
ENV PYTHONUNBUFFERED=1
#ENV UV_SYSTEM_PYTHON=1

RUN apt-get update && \
    apt-get install -y vim curl yq jq
RUN addgroup -gid 1000 usergroup && \
    adduser user \
    --disabled-password \
    -u 1000 --gecos "" \
    --ingroup 0 \
    --ingroup usergroup && \
    mkdir -p /workdir && \
    chown -R user:usergroup /workdir

WORKDIR /workdir

USER user
ENV HOME=/home/user
ENV PATH="/workdir/.venv/bin:${HOME}/.local/bin:${PATH}"



ENV WORKER_CLASS="uvicorn.workers.UvicornWorker"

ENV APP__HOST=0.0.0.0
ENV APP__PORT=18080
ENV LOG_LEVEL=info
ENV GRACEFUL_TIMEOUT=600
ENV TIMEOUT=600
ENV KEEP_ALIVE=600

# For distinguishing between deployed app and agent-backend
ENV IS_DEPLOYED_APP=true

ADD . /workdir/.

USER root
RUN chown -R user:usergroup /workdir
RUN chown -R user:usergroup /home/user
USER user

RUN uv sync

RUN echo 'import os' > /workdir/server.py && \
    echo 'from adxp_sdk.serves.server import get_server' >> /workdir/server.py && \
    echo '' >> /workdir/server.py && \
    echo 'app = get_server("./mari_agent/graph_builder.py:mari_graph", ".env" )' >> /workdir/server.py

ENV APP_MODULE="server:app"
EXPOSE 18080
SHELL ["/bin/bash", "-c"]
CMD python -m gunicorn \
    -k "${WORKER_CLASS}" \
    -b "${APP__HOST}:${APP__PORT}" \
    --log-level "${LOG_LEVEL}" \
    --graceful-timeout "${GRACEFUL_TIMEOUT}" \
    --timeout "${TIMEOUT}" \
    --keep-alive "${KEEP_ALIVE}" \
    --preload "${APP_MODULE}"
