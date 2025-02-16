ARG IMAGE_NAME=ubuntu
ARG IMAGE_TAG=24.04

FROM ${IMAGE_NAME}:${IMAGE_TAG} AS devcontainer_build

ENV USER=ubuntu
ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home/${USER}
ENV PROJECT_DIR=/workspace
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=apps.football_pool
ENV FLASK_DEBUG=1
ENV FLASK_ENV=development
ENV FLASK_CONFIG_DEFAULT=Dev
ENV VIRTUAL_ENV=${HOME}/venv
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}:${PROJECT_DIR}

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
pipx \
python3.12 \
python3.12-dev \
python3.12-venv \
sudo \
vim

# add user to sudoers list
echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER}

# create virtual environment
python3.12 -m venv ${VIRTUAL_ENV}
EOF

USER ${USER}

COPY ./requirements.txt ${PROJECT_DIR}/requirements.txt

WORKDIR ${PROJECT_DIR}

RUN --mount=type=cache,target=${HOME}/.cache/pip,uid=1000,gid=1000 \
<<EOF
# set permissions for workdir and venv
sudo chown --recursive 1000 /workspace
sudo chown --recursive 1000 ${VIRTUAL_ENV}

# install requirements.txt
${VIRTUAL_ENV}/bin/python -m pip install --cache-dir ${HOME}/.cache/pip -r ${PROJECT_DIR}/requirements.txt
pipx install ruff  # TODO: not working currently, pipx probably not properly installed

# add usability aliases
alias python='python3.12'
alias python3='python3.12'

# install tailwind + daisyui
npm install -D tailwindcss @tailwindcss/cli
npm install -D daisyui@latest
npm install -D @tailwindcss/typography
EOF

CMD [ "sleep", "infinity" ]
