#!/usr/bin/env bash

set -eux

BUILD_CONTEXT_PATH=$1
IMAGE_TAG=$2
OUTPUT_FILE=$3
# Lowercase first character, e.g True => true, False => false
VERIFY_TLS="${4,}"

# We assume that the mounted docker config contains a single entry
# This entry also indicates the registry to use
REGISTRY=$(jq -r '.auths | keys[0]' /.docker/config.json | sed -e 's/https:\/\///')
IMAGE_URL="${REGISTRY}/${IMAGE_TAG}"

buildah bud --tag "$IMAGE_URL" --file Dockerfile "${BUILD_CONTEXT_PATH}"

buildah push --authfile /.docker/config.json --tls-verify="$VERIFY_TLS" "$IMAGE_URL"

mkdir -p "$(dirname "$OUTPUT_FILE")"
echo "$IMAGE_URL" > "$OUTPUT_FILE"
