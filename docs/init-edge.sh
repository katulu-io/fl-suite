#!/usr/bin/env bash

set -e

K8S_NODE_NAME=local-edge-control-plane
SPIRE_AGENT_HOSTNAME=$(hostname)-local-edge

# Create spire agent's join token
SPIRE_AGENT_JOIN_TOKEN=$(kubectl exec -n spire spire-server-0 -c spire-server -- \
  /opt/spire/bin/spire-server token generate -spiffeID "spiffe://katulu.io/$SPIRE_AGENT_HOSTNAME" -ttl 3600 | \
  awk '{print $2}')

# Allow the local-edge kind cluster's fl-clients to communicate with the fl-server
kubectl exec -n spire spire-server-0 -c spire-server -- /opt/spire/bin/spire-server entry create \
    -parentID "spiffe://katulu.io/$SPIRE_AGENT_HOSTNAME" \
    -spiffeID spiffe://katulu.io/flower-client \
    -selector "k8s:node-name:$K8S_NODE_NAME" \
    -selector "k8s:ns:katulu-fl" \
    -selector "k8s:pod-label:app:flower-client"
# Allow the local-edge kind cluster's fl-operator to communicate with the fl-orchestrator
kubectl exec -n spire spire-server-0 -c spire-server -- /opt/spire/bin/spire-server entry create \
    -parentID "spiffe://katulu.io/$SPIRE_AGENT_HOSTNAME" \
    -spiffeID spiffe://katulu.io/fl-operator \
    -selector "k8s:node-name:$K8S_NODE_NAME" \
    -selector "k8s:ns:katulu-fl" \
    -selector "k8s:pod-label:app:fl-operator-envoyproxy"

KUSTOMIZE_PARAMS_DIR=example/fl-edge/config

# Setup spire agent to communicate with the spire server
SPIRE_AGENT_SERVER_ADDRESS=$(kubectl -n spire get virtualservice spire-server -o jsonpath='{ .spec.hosts[0] }')
cat <<EOF > "$KUSTOMIZE_PARAMS_DIR/spire-server-creds.env"
spire_agent_join_token=$SPIRE_AGENT_JOIN_TOKEN
spire_agent_server_address=$SPIRE_AGENT_SERVER_ADDRESS
EOF

# Setup fl-operator to communicate with the fl-orchestrator
FL_ORCHESTRATOR_SNI=$(kubectl -n katulu-fl get virtualservice fl-orchestrator-envoyproxy -o jsonpath='{ .spec.hosts[0] }')
cat <<EOF > "$KUSTOMIZE_PARAMS_DIR/fl-operator-params.env"
fl_orchestrator_sni=$FL_ORCHESTRATOR_SNI
fl_orchestrator_port=8443
EOF

# Deploy kind cluster that uses fl-suite's container registry
CONTAINER_REGISTRY_FQDN=$(kubectl -n container-registry get virtualservice container-registry -o jsonpath='{ .spec.hosts[0] }')
export CONTAINER_REGISTRY_FQDN

kubectl -n katulu-fl get secret internal-registry-credentials -o jsonpath='{ .data.\.dockerconfigjson }' | base64 -d > "$KUSTOMIZE_PARAMS_DIR/internal-registry-credentials.json"
envsubst <<EOF | kind create cluster --kubeconfig local-edge-kubeconfig.yaml --config -
---
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: local-edge
nodes:
  - role: control-plane
    # Using the same kubernetes version as the cluster deployed in the example
    image: kindest/node:v1.21.10@sha256:84709f09756ba4f863769bdcabe5edafc2ada72d3c8c44d6515fc581b66b029c
    extraMounts:
      - hostPath: ./dataset
        containerPath: /dataset
        readOnly: true
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."$CONTAINER_REGISTRY_FQDN:8080"]
    endpoint = ["http://$CONTAINER_REGISTRY_FQDN:8080"]
EOF
