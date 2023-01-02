-include ../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=localhost:5000

MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")
IMAGE_NAME = edge-identity
IMAGE_URL = ${MAKEVAR_REGISTRY}/${IMAGE_NAME}:${CONTAINER_TAG}
# We're changing the version a bit to make it work with pip, as PEP 440 isn't semver compatible.
PIP_VERSION = $(shell echo "${MAKEVAR_VERSION}" | sed -e "s/-/+/" -e "s/-/./g")
POETRY_STAMP := .poetry.stamp

# Build is not needed because the dist target builds the application via docker multi-stage
clean lint test build:
	@echo "$@ not implemented"
.PHONY: lint test build

${POETRY_STAMP}: backend/poetry.lock
	@cd backend/ && \
		poetry install
	touch ${POETRY_STAMP}

dependencies: ${POETRY_STAMP}

backend/edge-identity.db: ${POETRY_STAMP} backend/apps/default/schema.sql
	@cd backend/ && FLASK_APP=apps.default poetry run flask init-db

dist: manifests
	@cd backend/ && \
		poetry version ${PIP_VERSION}

	# Using ../ as docker context to be able to retrieve the components/vendor/kubeflow for the common backend/frontend code
	DOCKER_BUILDKIT=1 docker build -t ${IMAGE_URL} -f Dockerfile ..
.PHONY: dist

manifests:
	@cd kustomize/base/ && \
		cp kustomization.tpl.yaml kustomization.yaml && \
		kustomize edit set image ${IMAGE_NAME}=${IMAGE_URL}
.PHONY: manifests


run: ${POETRY_STAMP} backend/edge-identity.db
	@cd backend/ && \
		poetry run gunicorn -w 3 --bind 0.0.0.0:8080 --access-logfile - entrypoint:app
run: export BACKEND_MODE = dev
run: export APP_SECURE_COOKIES = False
run: export APP_PREFIX = /
run: export UI_FLAVOR = default
.PHONY: run

spire-sdk:
	@cd backend/ && \
		poetry run python -m grpc_tools.protoc \
			--python_out=. --grpc_python_out=. \
			-I ../../vendor/spire-api-sdk/proto/ \
			../../vendor/spire-api-sdk/proto/spire/api/server/agent/v1/agent.proto \
			../../vendor/spire-api-sdk/proto/spire/api/server/entry/v1/entry.proto \
			../../vendor/spire-api-sdk/proto/spire/api/types/*.proto
.PHONY: spire-sdk

push:
	docker push ${IMAGE_URL}
.PHONY: push

install:
	kustomize build kustomize/overlays/istio | kubectl apply -f -
.PHONY: install

uninstall:
	kustomize build kustomize/overlays/istio | kubectl delete -f -
.PHONY: uninstall

maintainer-clean:
	rm -fr ../vendor/kubeflow/components/crud-web-apps/common/frontend/kubeflow-common-lib/dist/kubeflow frontend/node_modules frontend/dist/
.PHONY: maintainer-clean
