#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

trap "cd '${ORIG_DIR}'" EXIT

REPOSITORY=eoepca/demo
TAG=0.1

# eval $(minikube -p minikube docker-env)

docker build -f .docker/Dockerfile -t ${REPOSITORY}:${TAG} .
docker tag ${REPOSITORY}:${TAG} ${REPOSITORY}:latest

# eval $(minikube -p minikube docker-env -u)
