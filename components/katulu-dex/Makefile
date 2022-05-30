MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite

-include ../../.devcontainer/targets.mk

# Drop Semver build metadata as tags may contain lowercase and uppercase letters, digits, underscores, periods and dashes.
CONTAINER_TAG ?= $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

dependencies:
	@echo "dependencies not implemented"
.PHONY: dependencies

lint:
	@echo "lint not implemented"
.PHONY: lint

test:
	@echo "test not implemented"
.PHONY: test

build:
	@echo "build not implemented"
.PHONY: build

dist:
	DOCKER_BUILDKIT=1 docker build -t ${MAKEVAR_REGISTRY}/dex:${CONTAINER_TAG} .
	cp kustomization.tpl.yaml kustomization.yaml
	kustomize edit set image katulu-dex=${MAKEVAR_REGISTRY}/dex:${CONTAINER_TAG}
.PHONY: dist

# Handy install target to iterate development over a single component
install:
	kustomize build . | kubectl apply -f -
.PHONY: install

push:
	docker push ${MAKEVAR_REGISTRY}/dex:${CONTAINER_TAG}
.PHONY: push
