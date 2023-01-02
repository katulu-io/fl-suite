-include ../../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=localhost:5000
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")
IMAGE_NAME = katulu-fl-jupyter-full
IMAGE_URL = ${MAKEVAR_REGISTRY}/${IMAGE_NAME}:${CONTAINER_TAG}

PIP_VERSION = $(shell echo "${MAKEVAR_VERSION}" | sed -e "s/-/+/" -e "s/-/./g")

lint test build:
	@echo "$@ not implemented"
.PHONY: lint test build

dist: manifests
	mkdir -p dist
	cp ../kubeflow-pipeline/python/dist/fl_suite-${PIP_VERSION}-py3-none-any.whl dist/
	sed -e "s/\\\$$\\\$$container-tag\\\$$\\\$$/${PIP_VERSION}/g" Dockerfile.tpl > dist/Dockerfile
	sed -e "s/\\\$$\\\$$container-tag\\\$$\\\$$/${PIP_VERSION}/g" requirements.tpl.txt > dist/requirements.txt
	DOCKER_BUILDKIT=1 docker build -t ${IMAGE_URL} dist
.PHONY: dist

manifests:
	cp kustomization.yaml.tpl kustomization.yaml
	kustomize edit set image ${IMAGE_NAME}=${IMAGE_URL}
.PHONY: manifests

push:
	docker push ${IMAGE_URL}
.PHONY: push

# Handy install target to iterate development over a single component
install:
	kustomize build . | kubectl apply -f -
.PHONY: install

uninstall:
	kustomize build . | kubectl delete -f -
.PHONY: uninstall

clean:
	-rm -rf dist
	-rm kustomization.yaml
.PHONY: clean
