#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

export PUSER="$(id -un)"
export PUID="$(id -u)"
export PGID="$(id -g)"

function onExit() {
  docker-compose -f docker-compose-dev.yml down
  rm -f kubeconfig
  cd "${ORIG_DIR}"
}
trap "onExit" EXIT

if ! hash docker 2>/dev/null; then
  echo "ERROR - docker is required" 1>&2
  exit 1
fi
if ! hash docker-compose 2>/dev/null; then
  echo "ERROR - docker-compose is required" 1>&2
  exit 1
fi

touch kubeconfig
if hash kubectl 2>/dev/null; then
  if kubectl config view --flatten --minify 2>/dev/null >kubeconfig; then
    chmod 600 kubeconfig
  fi
fi

docker-compose -f docker-compose-dev.yml up --build
