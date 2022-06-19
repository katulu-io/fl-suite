-include ../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=localhost:5000
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
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
	docker build -t ${MAKEVAR_REGISTRY}/image-builder:${CONTAINER_TAG} .
.PHONY: dist

push:
	docker push ${MAKEVAR_REGISTRY}/image-builder:${CONTAINER_TAG}
.PHONY: push

clean:
	@echo "clean not implemented"
.PHONY: clean
