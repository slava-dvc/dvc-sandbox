ifneq (,$(wildcard ./.env))
    include .env
    export
endif

SHELL:= /bin/bash
SHORT_COMMIT_SHA:=$(shell git rev-parse --short HEAD)
export IMAGE:=us.gcr.io/${GOOGLE_CLOUD_PROJECT}/docker/synapse:${SHORT_COMMIT_SHA}
export PATH:= ~/.pulumi/bin:$(PATH)

activate-service-account:
	@echo '${SERVICE_ACCOUNT}' > keyfile.txt
	gcloud auth activate-service-account --key-file keyfile.txt; rm keyfile.txt


build-app:
	@echo "Building image ${IMAGE}"
	gcloud --project ${GOOGLE_CLOUD_PROJECT} builds submit . --region ${GOOGLE_CLOUD_REGION} --suppress-logs --tag ${IMAGE} || true

deploy-app:
	@echo "Deploying image ${IMAGE}"
	gcloud --project ${GOOGLE_CLOUD_PROJECT} run deploy portfolio --image ${IMAGE} --region ${GOOGLE_CLOUD_REGION}
	gcloud --project ${GOOGLE_CLOUD_PROJECT} run deploy synapse --image ${IMAGE} --region ${GOOGLE_CLOUD_REGION}
	gcloud --project ${GOOGLE_CLOUD_PROJECT} run services --region ${GOOGLE_CLOUD_REGION} add-iam-policy-binding synapse --member="allUsers" --role=roles/run.invoker

install-infra-tool:
	@if command -v pulumi >/dev/null 2>&1; then \
        echo "Infrastructure tool (Pulumi) is already installed."; \
    else \
        echo "Installing infrastructure tool (Pulumi)"; \
        curl -fsSL https://get.pulumi.com | sh; \
    fi

configure-infra-tool:
	cd infrastructure && pulumi login gs://${PULUMI_STATE_BUCKET}
	cd infrastructure && pulumi stack select prod || (pulumi stack init prod --secrets-provider=passphrase && pulumi stack select prod)
	cd infrastructure && pulumi install
	cd infrastructure && pulumi config set gcp:project ${GOOGLE_CLOUD_PROJECT}
	cd infrastructure && pulumi config set gcp:region ${GOOGLE_CLOUD_REGION}

infra-diff:
	cd infrastructure && pulumi preview && pulumi preview --diff --non-interactive 2>&1 > preview.txt

infra-apply:
	cd infrastructure && pulumi up --yes --skip-preview

infra-refresh:
	cd infrastructure && pulumi refresh

# Pulumi operations only
infra-deploy: install-infra-tool configure-infra-tool infra-diff infra-apply
app-deploy: build-app deploy-app
all: infra-deploy app-deploy
