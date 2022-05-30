MAKEVAR_REGISTRY ?= ghcr.io/katulu-io/fl-suite
DEV_CONTAINER_DIR = $(dir $(lastword $(MAKEFILE_LIST)))
DEV_CONTAINER_DOCKERFILE = $(DEV_CONTAINER_DIR)/Dockerfile
DEV_CONTAINER_TAG = $(shell (sha256sum $(DEV_CONTAINER_DOCKERFILE) || shasum -a 256 $(DEV_CONTAINER_DOCKERFILE)) | head -c 12)
DEV_CONTAINER_IMAGE_NAME = devcontainer
DEV_CONTAINER_MOUNT = $(abspath $(DEV_CONTAINER_DIR)../)
DEV_CONTAINER_WORKING_DIR = /workspace$(CURDIR:$(DEV_CONTAINER_MOUNT)%=%)

DOCKER_CONFIG_JSON = $(HOME)/.docker/config.json
DOCKER_LINUX_OPTS = -u $(shell id -u):$(shell id -g) --group-add=$(shell getent group docker | cut -d: -f3)
DOCKER_OTHER_OS_OPTS =

ifeq ($(shell uname), Linux)
	DOCKER_OS_OPTS = $(DOCKER_LINUX_OPTS)
else
	DOCKER_OS_OPTS = $(DOCKER_OTHER_OS_OPTS)
endif


--pull-devcontainer:
	@docker pull ${MAKEVAR_REGISTRY}/${DEV_CONTAINER_IMAGE_NAME}:${DEV_CONTAINER_TAG} || true
.PHONY: --pull-devcontainer

devcontainer: --pull-devcontainer
	@if [ -z "$(shell docker image ls -q ${MAKEVAR_REGISTRY}/${DEV_CONTAINER_IMAGE_NAME}:${DEV_CONTAINER_TAG})" ]; then \
		echo "Building devcontainer image..."; \
		DOCKER_BUILDKIT=1 docker build -t ${MAKEVAR_REGISTRY}/${DEV_CONTAINER_IMAGE_NAME}:${DEV_CONTAINER_TAG} \
		--build-arg BUILDKIT_INLINE_CACHE=1 \
		${DEV_CONTAINER_DIR};\
		docker push ${MAKEVAR_REGISTRY}/${DEV_CONTAINER_IMAGE_NAME}:${DEV_CONTAINER_TAG} || true; \
	fi
.PHONY: devcontainer

devcontainer-%: ENVFILE := $(shell mktemp)
devcontainer-%: devcontainer
	env | grep -e 'AWS_' -e 'ARM_' -e 'GITHUB_' -e 'MAKEVAR_' -e 'SKIP_' -e 'TF_' >> ${ENVFILE} || true
	echo MAKEVAR_DIND=true >> ${ENVFILE}
	docker run --rm $(DOCKER_OS_OPTS) \
		-v ~/.kube/config:$(DEV_CONTAINER_WORKING_DIR)/.kube/config \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(DEV_CONTAINER_MOUNT):/workspace \
		-v $(DOCKER_CONFIG_JSON):/root/.docker/config.json \
		-w $(DEV_CONTAINER_WORKING_DIR) \
		-e HOME=$(DEV_CONTAINER_WORKING_DIR) \
		-e GOPATH=$(DEV_CONTAINER_WORKING_DIR)/go \
		-e POETRY_VIRTUALENVS_PATH=$(DEV_CONTAINER_WORKING_DIR)/.venvs \
		-e SPIRE_AGENT_HOSTNAME=$(shell hostname)-katulu-fl-edge \
		-e DATASET_MOUNT_PATH=$(DEV_CONTAINER_MOUNT)/dataset \
		--env-file ${ENVFILE} \
		${MAKEVAR_REGISTRY}/${DEV_CONTAINER_IMAGE_NAME}:${DEV_CONTAINER_TAG} \
		make $(subst devcontainer-,,$@) $(MAKEVAR_ARGS) MAKEVAR_VERSION=$(MAKEVAR_VERSION);
.PHONY: devcontainer-%

+%:
	make $(subst +, devcontainer-,$@)
.PHONY: +%
