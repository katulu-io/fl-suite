#!/usr/bin/env bash

set -e

CLUSTER_NAME=local.fl-suite
kind create cluster --config=kind-config.yaml --kubeconfig "$CLUSTER_NAME.kubeconfig.yaml" || true

# Export kind's internal kubeconfig to be used by devcontainer.
# This kubeconfig file is kept hidden because it is only used by the provision script
kind export kubeconfig --name "$CLUSTER_NAME" --internal --kubeconfig ".$CLUSTER_NAME-internal.kubeconfig.yaml"

KUBECONFIG="./$CLUSTER_NAME.kubeconfig.yaml"
# If this script is running inside docker then use the internal kubeconfig
if grep -q docker /proc/self/cgroup; then
  KUBECONFIG="./.$CLUSTER_NAME-internal.kubeconfig.yaml"
fi
export KUBECONFIG

while ! kustomize build kustomize | kubectl apply -f -; do
  echo "Retrying to apply resources"
  sleep 10
done
