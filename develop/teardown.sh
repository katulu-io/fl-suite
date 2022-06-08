#!/usr/bin/env bash

set -e

CLUSTER_NAME=local.fl-suite

kind delete cluster --name "$CLUSTER_NAME"

rm -f "$CLUSTER_NAME.kubeconfig.yaml" ".$CLUSTER_NAME-internal.kubeconfig.yaml"
