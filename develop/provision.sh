#!/usr/bin/env bash

set -e

# CLUSTER_NAME=local.fl-suite

kind create cluster --config=kind-config.yaml || true

# # If this script is running inside docker (most probably devcontainer) then use a "internal" kubeconfig
# if grep -q docker /proc/self/cgroup; then
#   # This kubeconfig file is kept "hidden" because it is only used by the provision script
#   kind export kubeconfig --name "$CLUSTER_NAME" --internal --kubeconfig ".$CLUSTER_NAME-internal.kubeconfig.yaml"
#   KUBECONFIG="./.$CLUSTER_NAME-internal.kubeconfig.yaml"
#   export KUBECONFIG
# fi

# while ! kustomize build kustomize | kubectl apply -f -; do
#   echo "Retrying to apply resources"
#   sleep 10
# done

kubectl create ns argo || true
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml

kustomize build kustomize-argo | kubectl apply -f -
