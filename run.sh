#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

export PUSER="$(id -un)"
export PUID="$(id -u)"
export PGID="$(id -g)"

function onExit() {
  docker-compose -f docker-compose-dev.yml down
  rm kubeconfig
  cd "${ORIG_DIR}"
}

trap "onExit" EXIT

export DEPLOYMENT_GUIDE_ROOT="${DEPLOYMENT_GUIDE_ROOT:-${HOME}/deployments/deployment-guide}"

kubectl config view --flatten --minify >kubeconfig
chmod 600 kubeconfig

docker-compose -f docker-compose-dev.yml up --build
