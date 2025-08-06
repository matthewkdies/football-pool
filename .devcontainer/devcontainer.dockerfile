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
ENV FLASK_APP=apps.football_pool
ENV FLASK_DEBUG=1
ENV FLASK_ENV=development
ENV VIRTUAL_ENV=${PROJECT_DIR}/.venv
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}:${PROJECT_DIR}

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

RUN <<EOF
uv python install --default 3.13
uv venv "${VIRTUAL_ENV}"
uv tool install pre-commit
uv tool install ruff

# install tailwind + daisyui
npm install -D tailwindcss @tailwindcss/cli
npm install -D daisyui@latest
npm install -D @tailwindcss/typography
EOF

COPY ./pyproject.toml ${PROJECT_DIR}/pyproject.toml

RUN uv sync

CMD [ "sleep", "infinity" ]
