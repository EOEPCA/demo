#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

trap "cd '${ORIG_DIR}'" EXIT

source ./container-info

# eval $(minikube -p minikube docker-env)

docker-compose build
docker tag ${REPOSITORY}:latest ${REPOSITORY}:${TAG}

# eval $(minikube -p minikube docker-env -u)

echo -e "\nCreated docker image: ${REPOSITORY}:latest => ${REPOSITORY}:${TAG}\n"

echo "Pushing images..."
docker push ${REPOSITORY}:latest
docker push ${REPOSITORY}:${TAG}
