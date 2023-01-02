MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite

-include ../../.devcontainer/targets.mk

# Drop Semver build metadata as tags may contain lowercase and uppercase letters, digits, underscores, periods and dashes.
CONTAINER_TAG ?= $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

node_modules: package.json
	@yarn install

dependencies: node_modules

lint: dependencies
	@yarn ng lint
.PHONY: lint

test: dependencies
	@yarn ng test --browsers=Headless --watch=false
.PHONY: test

build: dependencies
	@yarn ng build
.PHONY: build

dist:
	DOCKER_BUILDKIT=1 docker build -t ${MAKEVAR_REGISTRY}/centraldashboard:${CONTAINER_TAG} .
	cp kustomization.tpl.yaml kustomization.yaml
	kustomize edit set image centraldashboard=$(MAKEVAR_REGISTRY)/centraldashboard:$(CONTAINER_TAG)
.PHONY: dist

push:
	docker push ${MAKEVAR_REGISTRY}/centraldashboard:${CONTAINER_TAG}
.PHONY: push

# Handy install target to iterate development over a single component
install:
	kustomize build . | kubectl apply -f -
.PHONY: install

dev:
	@yarn start
.PHONY: dev

clean:
	-rm -r dist
	-rm kustomization.yaml
.PHONY: clean

clean-dev:
	@echo "clean-dev not implemented"
.PHONY: clean-dev
