ARG IMAGE_NAME=ubuntu
ARG IMAGE_TAG=24.04

FROM ${IMAGE_NAME}:${IMAGE_TAG} AS devcontainer_build

SHELL [ "/bin/bash", "-e", "-c" ]

ENV USER=ubuntu
ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home/${USER}
ENV PROJECT_DIR=/workspace
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=development
ENV DEBUG=1
ENV VIRTUAL_ENV=${PROJECT_DIR}/.venv
ENV PATH=${VIRTUAL_ENV}/bin:${HOME}/.local/bin:${PATH}:${PROJECT_DIR}

WORKDIR ${PROJECT_DIR}

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    <<EOF
# install all OS dependencies
apt-get update
apt-get install -y \
build-essential \
curl \
git \
libpq-dev \
nodejs \
npm \
sudo \
vim

# add user to sudoers list
echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER}

# set permissions for various dirs for future usage
sudo mkdir --parents /workspace ${HOME}/.cache ${HOME}/.config
sudo chown --recursive ${USER} /workspace ${HOME}/.cache ${HOME}/.config
EOF

USER ${USER}

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_LINK_MODE=copy

RUN <<EOF
uv python install --default 3.13
uv venv "${VIRTUAL_ENV}"
uv tool install prek
uv tool install ruff

# install agy CLI
curl -fsSL https://antigravity.google/cli/install.sh | bash
EOF

COPY ./pyproject.toml ./uv.lock* ${PROJECT_DIR}/

ENV PYTHONPATH=/workspace/apps

RUN uv sync

LABEL com.centurylinklabs.watchtower.enable="false"

CMD [ "sleep", "infinity" ]
