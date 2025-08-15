ARG PYTHON_TAG=3.12-alpine

FROM python:${PYTHON_TAG}

ARG USER=notroot

ENV APPS_DIR=/apps
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=football_pool
ENV FLASK_DEBUG=0
ENV FLASK_ENV=production
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

COPY pyproject.toml package.json package-lock.json ${APPS_DIR}/football_pool/

RUN <<EOF
apk add --no-cache curl gcc g++ musl-dev postgresql-dev libpq-dev make nodejs npm shadow su-exec
npm --prefix ${APPS_DIR}/football_pool install
uv pip install --system -r ${APPS_DIR}/football_pool/pyproject.toml
EOF

COPY ./tailwind.config.js ${APPS_DIR}
COPY ./apps/football_pool ${APPS_DIR}/football_pool
COPY ./migrations ${APPS_DIR}/migrations
COPY ./prod/entrypoint.sh /entrypoint.sh

WORKDIR ${APPS_DIR}

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "sh", "-c", "gunicorn --workers 4 --bind 0.0.0.0:${WEB_PORT} --config ${APPS_DIR}/football_pool/gunicorn_config.py 'football_pool:create_app()'" ]

# HEALTHCHECK [ ]  # TODO
