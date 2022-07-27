-include ../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

PROTOC_VERSION=21.4
GOBIN = $(CURDIR)/bin

lint:
	go mod download
	golangci-lint run --allow-parallel-runners --timeout 5m
.PHONY: lint

test:
	go test -v -mod=readonly ./...
.PHONY: test

build:
	CGO_ENABLED=0 go build -o dist/fl-orchestrator ./cmd/main.go
.PHONY: build

dist:
	DOCKER_BUILDKIT=1 docker build -t ${MAKEVAR_REGISTRY}/fl-orchestrator:${CONTAINER_TAG} .
	cp kustomization.tpl.yaml kustomization.yaml
	kustomize edit set image fl-orchestrator=${MAKEVAR_REGISTRY}/fl-orchestrator:${CONTAINER_TAG}
.PHONY: dist

push:
	docker push ${MAKEVAR_REGISTRY}/fl-orchestrator:${CONTAINER_TAG}
.PHONY: push

# Handy install target to iterate development over a single component
install:
	kustomize build . | kubectl apply -f -
.PHONY: install

clean:
	rm -rf bin
	rm -rf dist
.PHONY: clean

bin/protoc:
	./scripts/download-protoc.sh $(PROTOC_VERSION)

bin/protoc-gen-go:
	GOBIN="$(GOBIN)" go install google.golang.org/protobuf/cmd/protoc-gen-go

bin/protoc-gen-go-grpc:
	GOBIN="$(GOBIN)" go install google.golang.org/grpc/cmd/protoc-gen-go-grpc

generate: bin/protoc bin/protoc-gen-go bin/protoc-gen-go-grpc
	PATH="$(GOBIN):$(PATH)" go generate ./pkg/...
.PHONY: generate
