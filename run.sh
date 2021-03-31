#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

trap "cd '${ORIG_DIR}'" EXIT

source ./container-info

./build.sh && docker run --rm --name jupyter -it -p 8888:8888 ${REPOSITORY}:${TAG}
# ./build.sh && docker run --rm --name jupyter -it -p 8888:8888 -v $PWD/demoroot:/home/jovyan/work ${REPOSITORY}:${TAG}
