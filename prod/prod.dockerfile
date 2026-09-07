ARG PYTHON_TAG=3.13-alpine

FROM python:${PYTHON_TAG}

ARG USER=notroot

ENV APPS_DIR=/apps
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV TZ=UTC
ENV WEB_PORT=5600
ENV USER_NAME=${USER}

EXPOSE ${WEB_PORT}

RUN <<EOF
sed -i 's/https/http/' /etc/apk/repositories
addgroup --system ${USER}
adduser --system ${USER}
EOF

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy

COPY pyproject.toml ${APPS_DIR}/football_pool/

RUN <<EOF
apk add --no-cache curl gcc g++ musl-dev postgresql-dev libpq-dev make shadow su-exec
uv pip install --system -r ${APPS_DIR}/football_pool/pyproject.toml
EOF

COPY ./apps/football_pool ${APPS_DIR}/football_pool/apps/football_pool
COPY ./migrations ${APPS_DIR}/football_pool/migrations
COPY ./alembic.ini ${APPS_DIR}/football_pool/alembic.ini
COPY ./prod/entrypoint.sh /entrypoint.sh

WORKDIR ${APPS_DIR}/football_pool

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "sh", "-c", "uvicorn apps.football_pool.main:app --host 0.0.0.0 --port ${WEB_PORT} --lifespan on" ]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:${WEB_PORT}/healthcheck || exit 1
