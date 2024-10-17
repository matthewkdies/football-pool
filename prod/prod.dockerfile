ARG PYTHON_TAG=3.12-alpine

FROM --platform=linux/amd64 python:${PYTHON_TAG}

EXPOSE 5600

ARG USER=notroot

ENV HOME /home/${USER}
ENV APPS_DIR=${HOME}/apps \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=football_pool \
    FLASK_DEBUG=0 \
    FLASK_ENV=production \
    TZ=UTC

RUN sed -i 's/https/http/' /etc/apk/repositories && \
    addgroup -g 1000 ${USER} && \
    adduser -S -h ${HOME} -u 1000 -G ${USER} ${USER}

COPY --chown=notroot:notroot requirements.txt package.json package-lock.json ${APPS_DIR}/football_pool/

RUN apk add --no-cache curl gcc g++ musl-dev postgresql-dev libpq-dev make nodejs npm && \
    npm --prefix ${APPS_DIR}/football_pool install && \
    pip --no-cache-dir install -r ${APPS_DIR}/football_pool/requirements.txt && \
    mkdir ${APPS_DIR}/migrations && \
    chown 1000:1000 ${APPS_DIR}/migrations

COPY --chown=notroot:notroot ./tailwind.config.js ${APPS_DIR}
COPY --chown=notroot:notroot ./apps/football_pool ${APPS_DIR}/football_pool

# we make sure to run the project as a regular user
USER ${USER}

WORKDIR ${APPS_DIR}

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5600", "football_pool:create_app()"]
