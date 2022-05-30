-include ../../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=localhost:5000
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

# We're changing the version a bit to make it work with pip, as PEP 440 isn't semver compatible.
PIP_VERSION = $(shell echo "${MAKEVAR_VERSION}" | sed -e "s/-/+/" -e "s/-/./g")

fl_suite/_version.py:
	sed -e "s/\\\$$\\\$$version\\\$$\\\$$/${CONTAINER_TAG}/g" fl_suite/_version.tpl > fl_suite/_version.py

lint: fl_suite/_version.py
	poetry install
	poetry run flake8p
	poetry run pylint fl_suite tests
.PHONY: lint

test: fl_suite/_version.py
	poetry install
	poetry run pytest
.PHONY: test

build: fl_suite/_version.py
	poetry version ${PIP_VERSION}
	poetry build
.PHONY: build

dist:
	@echo "dist not implemented"
.PHONY: dist

push:
	@echo "push not implemented"
.PHONY: push

clean:
	@rm -rf dist
.PHONY: clean
