#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

trap "cd '${ORIG_DIR}'" EXIT

source ./container-info

VOLUME_MOUNT=
if test "$1" = "dev"; then VOLUME_MOUNT="-v $PWD/demoroot:/home/jovyan/work"; fi

./build.sh && docker run --rm --name jupyter -it -p 8888:8888 ${VOLUME_MOUNT} ${REPOSITORY}:${TAG}
