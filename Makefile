MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite

include .devcontainer/targets.mk

MFILES = $(shell find . -maxdepth 5 -type f -name Makefile ! -path "*/node_modules/*" ! -path "*/vendor/*" ! -path "*/go/*" ! -path "*/demos/*")
SUBDIRS = $(filter-out ./,$(dir $(MFILES)))

node_modules: package.json
	@yarn install

dependencies: node_modules
.PHONY: dependencies

env: dependencies
	@rm -f .env
	@yarn workspace @katulu/release env > .env
.PHONY: env

commitlint:
	yarn commitlint --from ${MAKEVAR_COMMITS_FROM} --to ${MAKEVAR_COMMITS_TO}
.PHONY: commitlint

dockerlint:
	@find . -maxdepth 5 -type f -name Dockerfile | xargs -I {} hadolint {}
.PHONY: dockerlint

LINTTARGETS = $(SUBDIRS:%=lint--%)
lint: dependencies dockerlint $(LINTTARGETS)
$(LINTTARGETS):
	@$(MAKE) -C $(@:lint--%=%) lint
.PHONY: $(LINTTARGETS)
.PHONY: lint

TESTTARGETS = $(SUBDIRS:%=test--%)
test: dependencies $(TESTTARGETS)
$(TESTTARGETS):
	@$(MAKE) -C $(@:test--%=%) test
.PHONY: $(TESTTARGETS)
.PHONY: test

BUILDTARGETS = $(SUBDIRS:%=build--%)
build: dependencies $(BUILDTARGETS)
$(BUILDTARGETS):
	@$(MAKE) -C $(@:build--%=%) build
.PHONY: $(BUILDTARGETS)
.PHONY: build

DISTTARGETS = $(SUBDIRS:%=dist--%)
dist: dependencies $(DISTTARGETS)
$(DISTTARGETS):
	@$(MAKE) -C $(@:dist--%=%) dist
.PHONY: $(DISTTARGETS)
.PHONY: dist

PUSHTARGETS = $(SUBDIRS:%=push--%)
push: dependencies  $(PUSHTARGETS)
$(PUSHTARGETS):
	@$(MAKE) -C $(@:push--%=%) push
.PHONY: $(PUSHTARGETS)
.PHONY: push

release: dependencies
	@yarn workspace @katulu/release publish
.PHONY: release

CLEANTARGETS = $(SUBDIRS:%=clean--%)
clean: $(CLEANTARGETS)
$(CLEANTARGETS):
	@$(MAKE) -C $(@:clean--%=%) clean
.PHONY: $(CLEANTARGETS)
.PHONY: clean
