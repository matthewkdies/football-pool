ARG PYTHON_TAG=3-alpine

FROM python:${PYTHON_TAG}

EXPOSE 5600

ARG USER=notroot

ENV HOME /home/${USER}
ENV APPS_DIR=${HOME}/apps \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=football_pool \
    FLASK_DEBUG=0 \
    FLASK_ENV=production

COPY --chown=notroot:notroot requirements.txt package.json package-lock.json ${APPS_DIR}/football_pool/

RUN <<EOF
addgroup -g 1000 ${USER}
adduser -S -h ${HOME} -u 1000 -G ${USER} ${USER}
apk update
apk add --no-cache gcc g++ musl-dev postgresql-dev libpq-dev make nodejs npm
npm --prefix ${APPS_DIR}/football_pool install
pip --no-cache-dir install -r ${APPS_DIR}/football_pool/requirements.txt
EOF

COPY --chown=notroot:notroot ./apps/tailwind.config.js ${APPS_DIR}
COPY --chown=notroot:notroot ./apps/football_pool ${APPS_DIR}/football_pool

# we make sure to run the project as a regular user
USER ${USER}

WORKDIR ${APPS_DIR}

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5600", "football_pool:create_app()"]
