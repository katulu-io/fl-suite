-include ../../../../.devcontainer/targets.mk

MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

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
	docker build -t ${MAKEVAR_REGISTRY}/fl-server:${CONTAINER_TAG} .
.PHONY: dist

push:
	docker push ${MAKEVAR_REGISTRY}/fl-server:${CONTAINER_TAG}
.PHONY: push

clean:
.PHONY: clean
