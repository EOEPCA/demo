#!/usr/bin/env bash

ORIG_DIR="$(pwd)"
cd "$(dirname "$0")"
BIN_DIR="$(pwd)"

trap "cd '${ORIG_DIR}'" EXIT

source ./container-info

VOLUME_MOUNT=
# dev mode - use a mount for access to local files
if test "$1" = "dev"; then
  VOLUME_MOUNT="-v $PWD/demoroot:/home/jovyan/work"
# otherwise - make a build to embed the content
else
  ./build.sh
fi

docker run --rm --name jupyter -it -p 8888:8888 ${VOLUME_MOUNT} ${REPOSITORY}:${TAG}
