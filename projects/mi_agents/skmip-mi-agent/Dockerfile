ARG PLATFORM_ARCH="linux/amd64"

# FROM --platform=${PLATFORM_ARCH} python:3.11-bookworm
FROM skpc-registry.skpc.cloudzcp.net/amdp-public/amdp-oss/python-uv:3.13-slim



ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 
ENV PYTHONUNBUFFERED=1

# RUN apt-get update && \
#     apt-get install -y vim curl yq jq

RUN addgroup -gid 1000 usergroup && \
    adduser user \
    --disabled-password \
    -u 1000 --gecos "" \
    --ingroup 0 \
    --ingroup usergroup && \
    mkdir -p /workdir && \
    chown -R user:usergroup /workdir

WORKDIR /workdir

ENV PATH="${HOME}/.local/bin:${PATH}"

USER user

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


# RUN python -m pip install   adxp-sdk
# RUN python -m pip install   adxp-cli

# RUN python -m pip install --trusted-host pypi.org  adxp-sdk
# RUN python -m pip install --trusted-host pypi.org  adxp-cli

# RUN python -m pip install  --trusted-host pypi.org  -r ./requirements.txt

# RUN cat ./SK_SSL.crt >> $(python -m certifi)

RUN echo 'import os' > /workdir/server.py && \
    echo 'from adxp_sdk.serves.server import get_server' >> /workdir/server.py && \
    echo '' >> /workdir/server.py && \
    echo 'app = get_server("./apps/agents/mi_agent/graph_builder.py:runnable_graph", ".env")' >> /workdir/server.py

ENV APP_MODULE="server:app"
EXPOSE 18080
CMD python -m gunicorn \
    -k "${WORKER_CLASS}" \
    -b "${APP__HOST}:${APP__PORT}" \
    --log-level "${LOG_LEVEL}" \
    --graceful-timeout "${GRACEFUL_TIMEOUT}" \
    --timeout "${TIMEOUT}" \
    --keep-alive "${KEEP_ALIVE}" \
    --preload "${APP_MODULE}"
