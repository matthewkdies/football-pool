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
ENV REQ_TXT_PATH=${APPS_DIR}/football_pool/requirements.txt

COPY --chown=notroot:notroot ./requirements.txt ${REQ_TXT_PATH}

RUN <<EOF
addgroup -g 1000 ${USER}
adduser -S -h ${HOME} -u 1000 -G ${USER} ${USER}
apk update
apk add --no-cache gcc g++ musl-dev postgresql-dev libpq-dev make
pip --no-cache-dir install -r ${REQ_TXT_PATH}
EOF

COPY --chown=notroot:notroot ./apps/football_pool ${APPS_DIR}/football_pool

# we make sure to run the project as a regular user
USER ${USER}

WORKDIR ${APPS_DIR}

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5600", "football_pool:create_app()"]
