#!/usr/bin/bash

set -e

LOCAL_IMAGE="football-pool-local-build:latest"
REMOTE_IMAGE_NAME="matthewkdies/football-pool"
DATE_TAG=$(date +%d%b%g)

docker build --file "${GIT_REPOS_DIR}/football-pool/prod/prod.dockerfile" --tag "${LOCAL_IMAGE}" "${GIT_REPOS_DIR}/football-pool"
docker tag "${LOCAL_IMAGE}" "${REMOTE_IMAGE_NAME}:latest"
docker tag "${LOCAL_IMAGE}" "${REMOTE_IMAGE_NAME}:${DATE_TAG}"
docker push "${REMOTE_IMAGE_NAME}:latest"
docker push "${REMOTE_IMAGE_NAME}:${DATE_TAG}"
docker image rm "${LOCAL_IMAGE}"
docker image rm "${REMOTE_IMAGE_NAME}:latest"
docker image rm "${REMOTE_IMAGE_NAME}:${DATE_TAG}"
