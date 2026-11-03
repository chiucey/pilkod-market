#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SKILL_NAME="$(basename "$(cd "${SCRIPT_DIR}/.." && pwd)")"

cd "${ROOT_DIR}"

echo "Working directory: ${ROOT_DIR}"

if [[ ! -d "${SKILL_NAME}" ]]; then
  echo "Error: ${SKILL_NAME} directory not found under ${ROOT_DIR}"
  exit 1
fi

echo "Starting backup for ${SKILL_NAME} ..."

zip -r "${SKILL_NAME}.bak" "${SKILL_NAME}"

echo "Backup complete, removing original directory ..."

# Back up .authorization in the current script directory (if present) and restore it after update.
AUTH_BACKUP=""
if [[ -f "${SCRIPT_DIR}/.authorization" ]]; then
  AUTH_BACKUP="$(mktemp /tmp/authorization.XXXXXX)"
  cp "${SCRIPT_DIR}/.authorization" "${AUTH_BACKUP}"
  echo "Backed up .authorization to temporary file: ${AUTH_BACKUP}"
fi

rm -rf "${SKILL_NAME}"

# Use a generic temp-file pattern to avoid mktemp collisions.
TMP_ZIP="$(mktemp)"

echo "Downloading latest ${SKILL_NAME}.zip ..."

curl -L "https://gts-download.obs.myhuaweicloud.com/skills/${SKILL_NAME}.zip" -o "${TMP_ZIP}"

echo "Extracting to ${ROOT_DIR} ..."

unzip -o "${TMP_ZIP}"

# If .authorization was backed up, restore it to the new script directory.
if [[ -n "${AUTH_BACKUP}" && -f "${AUTH_BACKUP}" ]]; then
  cp "${AUTH_BACKUP}" "${SCRIPT_DIR}/.authorization"
  rm -f "${AUTH_BACKUP}"
  echo "Restored .authorization under SCRIPT_DIR"
fi

rm -f "${TMP_ZIP}"

echo "Update completed."

