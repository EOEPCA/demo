#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

function onExit() {
  docker-compose -f docker-compose-dev.yml down
  cd "${ORIG_DIR}"
}

trap "onExit" EXIT

docker-compose -f docker-compose-dev.yml up
