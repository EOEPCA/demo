#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

trap "cd '${ORIG_DIR}'" EXIT

INPUT_DATA_URL="${1}"
if test -z "${INPUT_DATA_URL}"; then
  echo "ERROR: Input Data URL must be supplied"
  exit 1
fi

sed -e "s|INPUT_DATA_URL|${INPUT_DATA_URL}|" app-execute-body-template.json > app-execute-body.json
