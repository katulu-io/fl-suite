#!/usr/bin/env bash

set -eux

BUILD_CONTEXT_PATH=$1
IMAGE_NAME=$2
IMAGE_TAG=$3
OUTPUT_FILE=$4
# Lowercase first character, e.g True => true, False => false
VERIFY_TLS="${5,}"
DOCKER_CONFIG_FILE="/.docker/config.json"

# We assume that the mounted docker config contains a single entry
# This entry also indicates the registry to use
REGISTRY=$(jq -r '.auths | keys[0]' "$DOCKER_CONFIG_FILE" | sed -e 's/https:\/\///')
IMAGE_URL="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

buildah bud --tag "$IMAGE_URL" --file Dockerfile "${BUILD_CONTEXT_PATH}"

buildah push --authfile "$DOCKER_CONFIG_FILE" --tls-verify="$VERIFY_TLS" "$IMAGE_URL"

mkdir -p "$(dirname "$OUTPUT_FILE")"
echo "$IMAGE_URL" > "$OUTPUT_FILE"
