#!/usr/bin/env bash

set -e

SPIRE_AGENT_HOSTNAME=$(hostname)-local-edge

FLOWER_CLIENT_ENTRY_IDS=$(kubectl exec -n spire spire-server-0 -c spire-server -- /opt/spire/bin/spire-server entry show -parentID "spiffe://katulu.io/$SPIRE_AGENT_HOSTNAME" | grep "Entry ID" | awk '{ print $4 }')

for entry_id in $FLOWER_CLIENT_ENTRY_IDS; do
  kubectl exec -n spire spire-server-0 -c spire-server -- /opt/spire/bin/spire-server entry delete -entryID "$entry_id"
done

SPIRE_AGENT_ENTRY_ID=$(kubectl exec -n spire spire-server-0 -c spire-server -- /opt/spire/bin/spire-server entry show -spiffeID "spiffe://katulu.io/$SPIRE_AGENT_HOSTNAME" | grep "Entry ID" | awk '{ print $4 }')
kubectl exec -n spire spire-server-0 -c spire-server -- /opt/spire/bin/spire-server entry delete -entryID "$SPIRE_AGENT_ENTRY_ID"

kind delete cluster --name local-edge
