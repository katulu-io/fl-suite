-include ../../.devcontainer/targets.mk

MAKEVAR_REGISTRY?=ghcr.io/katulu-io/fl-suite
MAKEVAR_VERSION?=0.0.0-dev-$(shell git log -n 1 --pretty=format:%h)
CONTAINER_TAG = $(shell echo "${MAKEVAR_VERSION}" | sed "s/\+[0-9a-zA-Z-]*//")

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
	docker build -t ${MAKEVAR_REGISTRY}/fl-orchestrator:${CONTAINER_TAG} .
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
	rm -rf dist
.PHONY: clean

protobuf:
	protoc --go_out=. --go_opt=paths=source_relative \
		--go-grpc_out=. --go-grpc_opt=paths=source_relative \
		pkg/proto/fl_orchestrator.proto
.PHONY: protobuf
