#!/bin/sh

set -e

# validate PUID and PGID vars
if [ -z "${PUID}" ] || [ -z "${PGID}" ]; then
    echo "ERROR: The 'PUID' and 'PGID' variables must be set."
    exit 1
fi

# change UID and GID as needed
OLD_UID=$(id -u "${USER_NAME}")
OLD_GID=$(id -g "${USER_NAME}")
if [[ "${OLD_UID}" != "${PUID}" || "${OLD_GID}" != "${PGID}" ]]; then
    echo "INFO: Changing IDs of user from ${OLD_UID}:${OLD_GID} to ${PUID}:${PGID}."
    groupmod --gid "${PGID}" "${USER_NAME}"
    usermod --uid "${PUID}" "${USER_NAME}"
    find / -user "${OLD_UID}" -exec chown "${PUID}" {} + 2>/dev/null
    find / -group "${OLD_GID}" -exec chown "${PGID}" {} + 2>/dev/null
fi

# migrate the database if needed
echo "INFO: Beginning database migrations..."
flask db upgrade
flask db stamp head
echo "INFO: Completed database migrations!"

# start the app
echo "Setup complete!"
echo "Executing the following command '$@' as ${USER_NAME} (${PUID}:${PGID})."
exec su-exec "${USER_NAME}" "$@"
