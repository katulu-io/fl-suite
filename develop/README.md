# Local kubernetes cluster

## Requirements

* [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl).
* [kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/).
* [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).

> 🌻 Add `devcontainer-` to any of the make targets to use a container image with the requirements already pre-installed

## Deploy

To deploy a local kubernetes cluster we will use kind (Kubernetes In Docker).

### 1. Setup a local container registry

The kind cluster uses a local registry to host the fl-suite container images. To deploy this run:

```shell
make local-registry
```

### 2. Push the fl-suite images to the local container registry

Build, dist and push the fl-suite's container images. This needs to be done at the root of the project:

On Linux (with all the tools to build all the components of the fl-suite):

```
cd /path/to/katulu-io/fl-suite/

export MAKEVAR_REGISTRY=localhost:5000
make build dist push
```

On any other platform:

```
cd /path/to/katulu-io/fl-suite/

export MAKEVAR_REGISTRY=localhost:5000
make devcontainer-build devcontainer-dist push
```

### 3. Provision the kind cluster

```shell
make provision
```

That step will show some errors like:

```
Error from server (NotFound): error when creating "STDIN": namespaces "katulu-fl" not found
```

This and other CRD related errors are expected. The namespace "katulu-fl" gets created once a Kubeflow Profile is reconciled in kubernetes which might take some time. The other CRD errors (e.g cert-manager's Certificates CRDs) have the same cause. The `provision` target will take care to retry this as many times as it needs and normally this takes around ~20 mins but depends on the local resources like CPU, Network, etc.

> 🌻 The same make-target can be used to update the cluster with the latest kustomize changes

A kubeconfig file is generated which can be used to configure `kubectl` and access the kind cluster:

```shell
kubectl get nodes
NAME                            STATUS   ROLES                  AGE     VERSION
local.fl-suite-control-plane   Ready    control-plane,master   5m00s   v1.21.10
```

### 4. Wait for all the pods to be ready

```shell
kubectl get pods -n cert-manager
kubectl get pods -n istio-system
kubectl get pods -n auth
kubectl get pods -n knative-eventing
kubectl get pods -n knative-serving
kubectl get pods -n kubeflow
kubectl get pods -n katulu-fl
kubectl get pods -n spire
kubectl get pods -n container-registry
```

### 5. Login to the fl-suite central dashboard

Once all pods are ready, you can access the fl-suite via:

On Linux: http://localhost
On MacOS: http://docker.for.mac.localhost

The credentials are:

```
Username: user@example.com
Password: 12341234
```

## Teardown

```shell
make teardown
```
