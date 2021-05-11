#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

trap "cd '${ORIG_DIR}'" EXIT

AP_URL="${1}"
if test -z "${AP_URL}"; then
  echo "ERROR: Application Package URL must be supplied"
  exit 1
fi

sed -e "s|APPLICATION_PACKAGE_URL|${AP_URL}|" app-deploy-body-cwl-template.json > app-deploy-body-cwl.json
