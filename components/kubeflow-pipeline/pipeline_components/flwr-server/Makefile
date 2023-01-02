-include ../../../../.devcontainer/targets.mk

MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")
POETRY_STAMP := .poetry.stamp

${POETRY_STAMP}: poetry.lock
	poetry install --no-root
	touch ${POETRY_STAMP}

lint: ${POETRY_STAMP}
	poetry run python -m isort --check-only flwr_server/
	poetry run python -m black --check flwr_server/
	poetry run python -m mypy flwr_server/
.PHONY: lint

build test clean:
	@echo "$@ not implemented"
.PHONY: build test clean

dist:
	poetry export -o requirements.txt
	DOCKER_BUILDKIT=1 docker build -t ${MAKEVAR_REGISTRY}/fl-server:${CONTAINER_TAG} .
.PHONY: dist

push:
	docker push ${MAKEVAR_REGISTRY}/fl-server:${CONTAINER_TAG}
.PHONY: push
