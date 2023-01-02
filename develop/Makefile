DOCKER_NETWORK_NAME = kind

-include ../.devcontainer/targets.mk

clean dependencies lint test build dist push:
	@echo "$@ not implemented"
.PHONY: clean dependencies lint test build dist push

local-registry:
	docker network create kind || true
	docker run -d --name registry --restart=always -p 5000:5000 --net=kind registry:2
.PHONY: local-registry

provision:
	@./provision.sh
.PHONY: provision

teardown:
	@./teardown.sh
.PHONY: teardown
