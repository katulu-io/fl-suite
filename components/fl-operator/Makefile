-include ../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

GOBIN = $(shell pwd)/bin

# Image URL to use all building/pushing image targets
IMG ?= ${MAKEVAR_REGISTRY}/fl-operator:${CONTAINER_TAG}

# Setting SHELL to bash allows bash commands to be executed by recipes.
# This is a requirement for 'setup-envtest.sh' in the test target.
# Options are set to exit when a recipe line exits non-zero or a piped command fails.
SHELL = /usr/bin/env bash -o pipefail
.SHELLFLAGS = -ec

ENVTEST_K8S_VERSION = 1.23

.PHONY: all
all: build

##@ General

# The help target prints out all targets with their descriptions organized
# beneath their categories. The categories are represented by '##@' and the
# target descriptions by '##'. The awk commands is responsible for reading the
# entire set of makefiles included in this invocation, looking for lines of the
# file as xyz: ## something, and then pretty-format the target and help. Then,
# if there's a line with ##@ something, that gets pretty-printed as a category.
# More info on the usage of ANSI control characters for terminal formatting:
# https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
# More info on the awk command:
# http://linuxcommand.org/lc3_adv_awk.php

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

bin/controller-gen:
	GOBIN="$(GOBIN)" go install sigs.k8s.io/controller-tools/cmd/controller-gen

bin/setup-envtest:
	GOBIN="$(GOBIN)" go install sigs.k8s.io/controller-runtime/tools/setup-envtest

.PHONY: manifests
manifests: bin/controller-gen ## Generate WebhookConfiguration, ClusterRole and CustomResourceDefinition objects.
	PATH="$(GOBIN):$(PATH)" controller-gen rbac:roleName=manager-role crd webhook paths="./..." \
		output:crd:artifacts:config=config/crd/bases \
		output:rbac:artifacts:config=config/rbac

.PHONY: generate
generate: bin/controller-gen ## Generate code containing DeepCopy, DeepCopyInto, and DeepCopyObject method implementations.
	PATH="$(GOBIN):$(PATH)" controller-gen object:headerFile="hack/boilerplate.go.txt" paths="./..."

.PHONY: test
test: manifests generate bin/setup-envtest  ## Run tests.
	KUBEBUILDER_ASSETS="$(shell $(GOBIN)/setup-envtest use $(ENVTEST_K8S_VERSION) -p path)" go test -v ./... -coverprofile cover.out

##@ Build

.PHONY: build
build: generate ## Build manager binary.
	CGO_ENABLED=0 go build -o bin/manager main.go

.PHONY: run
run:
	go run ./cmd/manager

.PHONY: dist
dist: manifests # test ## Build docker image with the manager.
	DOCKER_BUILDKIT=1 docker build -t ${IMG} .
	cp kustomization.yaml.tpl kustomization.yaml
	kustomize edit set image controller=${IMG}

.PHONY: push
push: ## Push docker image with the manager.
	docker push ${IMG}

# Handy install target to iterate development over a single component
install:
	kustomize build . | kubectl apply -f -
.PHONY: install

lint:
	go mod download
	golangci-lint run --allow-parallel-runners --timeout 5m
.PHONY: lint

clean:
	rm -rf bin/
.PHONY: clean
