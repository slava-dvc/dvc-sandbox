ifneq (,$(wildcard ./.env))
    include .env
    export
endif

SHELL := /bin/bash
SHORT_COMMIT_SHA := $(shell git rev-parse --short HEAD)
export DOCKER_REPOSITORY_ROOT := us-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/docker
export IMAGE := ${DOCKER_REPOSITORY_ROOT}/synapse:${SHORT_COMMIT_SHA}
export IMAGE_LATEST := ${DOCKER_REPOSITORY_ROOT}/synapse:latest
export PATH := ~/.pulumi/bin:$(PATH)

# Authentication
activate-service-account:
	@echo '${SERVICE_ACCOUNT}' > keyfile.txt
	gcloud auth activate-service-account --key-file keyfile.txt; rm keyfile.txt

# Testing targets
.PHONY: test
test:
	python -m pytest tests

.PHONY: test-backend-dry-run
test-backend-dry-run:
	python -m app.backend --dry-run

.PHONY: test-job-dry-run
test-job-dry-run:
	python -m app.job --dry-run

.PHONY: test-public-dry-run
test-public-dry-run:
	python -m app.public --dry-run

.PHONY: ci
ci: test test-backend-dry-run test-job-dry-run test-public-dry-run

# Docker targets
.PHONY: docker-build
docker-build:
	@echo "Building image ${IMAGE}"
	docker pull ${IMAGE_LATEST} || true
	docker build --network=host -t ${IMAGE} -t ${IMAGE_LATEST} --cache-from ${IMAGE_LATEST} .

.PHONY: docker-push
docker-push: docker-build
	@echo "Pushing image ${IMAGE}"
	docker push ${IMAGE}
	docker push ${IMAGE_LATEST}

# Infrastructure targets
.PHONY: infra-setup
infra-setup:
	@if ! command -v pulumi >/dev/null 2>&1; then \
		echo "Installing infrastructure tool (Pulumi)"; \
		curl -fsSL https://get.pulumi.com | sh; \
	else \
		echo "Infrastructure tool (Pulumi) is already installed."; \
	fi
	cd infrastructure && pulumi login gs://${PULUMI_STATE_BUCKET}
	cd infrastructure && pulumi stack select prod || (pulumi stack init prod --secrets-provider=passphrase && pulumi stack select prod)
	cd infrastructure && pulumi install
	cd infrastructure && pulumi config set gcp:project ${GOOGLE_CLOUD_PROJECT}
	cd infrastructure && pulumi config set gcp:region ${GOOGLE_CLOUD_REGION}

.PHONY: infra-diff
infra-diff:
	cd infrastructure && pulumi preview && pulumi preview --diff --non-interactive 2>&1 > preview.txt

.PHONY: infra-apply
infra-apply:
	cd infrastructure && pulumi up --yes --skip-preview

.PHONY: infra-refresh
infra-refresh:
	cd infrastructure && pulumi refresh

# Composite targets
.PHONY: docker
docker: docker-build docker-push

.PHONY: infra-deploy
infra-deploy: docker-push
	$(MAKE) infra-setup
	$(MAKE) infra-apply

.PHONY: cd
cd: docker infra-deploy

.PHONY: all
all: ci cd