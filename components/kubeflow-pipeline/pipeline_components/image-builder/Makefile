-include ../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=localhost:5000
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

build lint test clean:
	@echo "$@ not implemented"
.PHONY: build lint test clean

dist:
	DOCKER_BUILDKIT=1 docker build -t ${MAKEVAR_REGISTRY}/image-builder:${CONTAINER_TAG} .
.PHONY: dist

push:
	docker push ${MAKEVAR_REGISTRY}/image-builder:${CONTAINER_TAG}
.PHONY: push
