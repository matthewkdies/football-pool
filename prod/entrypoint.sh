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
NEW_USERNAME="${NEW_USERNAME:-new_user}"
NEW_GROUPNAME="${NEW_GROUPNAME:-new_group}"
if [[ "${OLD_UID}" != "${PUID}" || "${OLD_GID}" != "${PGID}" ]]; then
    echo "INFO: Creating group, if it doesn't exist already."
    getent group "${NEW_GROUPNAME}" &>/dev/null || groupadd --gid "${PGID}" "${NEW_GROUPNAME}"

    echo "INFO: Creating user, if it doesn't exist already."
    id -u "${NEW_USERNAME}" &>/dev/null || useradd --uid "${PUID}" --gid "${PGID}" "${NEW_USERNAME}"

    echo "INFO: Changing IDs of user to (${OLD_UID}:${OLD_GID}) to ${PUID}:${PGID}."
    groupmod --gid "${PGID}" "${NEW_GROUPNAME}"
    usermod --uid "${PUID}" "${NEW_USERNAME}"
    find / -user "${OLD_UID}" -exec echo chown "${PUID}" '{}' \; 2>/dev/null
    find / -user "${OLD_UID}" -exec chown "${PUID}:${PGID}" {} + 2>/dev/null
    find / -group "${OLD_GID}" -exec chown "${PUID}:${PGID}" {} + 2>/dev/null
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
