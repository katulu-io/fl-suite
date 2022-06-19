-include ../../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=localhost:5000
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

PIP_VERSION = $(shell echo "${MAKEVAR_VERSION}" | sed -e "s/-/+/" -e "s/-/./g")

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
	mkdir -p dist
	cp ../kubeflow-pipeline/python/dist/fl_suite-${PIP_VERSION}-py3-none-any.whl dist/
	sed -e "s/\\\$$\\\$$container-tag\\\$$\\\$$/${PIP_VERSION}/g" Dockerfile.tpl > dist/Dockerfile
	sed -e "s/\\\$$\\\$$container-tag\\\$$\\\$$/${PIP_VERSION}/g" requirements.tpl.txt > dist/requirements.txt
	docker build -t ${MAKEVAR_REGISTRY}/katulu-fl-jupyter-full:${CONTAINER_TAG} dist
.PHONY: dist

push:
	docker push ${MAKEVAR_REGISTRY}/katulu-fl-jupyter-full:${CONTAINER_TAG}
.PHONY: push

# Handy install target to iterate development over a single component
install:
	kustomize build kustomize/ | kubectl apply -f -
.PHONY: install

clean:
	@rm -rf dist
.PHONY: clean
