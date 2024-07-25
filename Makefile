ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.DEFAULT_GOAL := all

SHELL:= /bin/bash
SHORT_COMMIT_SHA:=$(shell git rev-parse --short HEAD)
PULUMI_STATE_BUCKET:=vcmate-pulumi
export IMAGE:=us.gcr.io/${GOOGLE_CLOUD_PROJECT}/docker/synapse:${SHORT_COMMIT_SHA}

activate-service-account:
	@echo '${SERVICE_ACCOUNT}' > keyfile.txt
	gcloud auth activate-service-account --key-file keyfile.txt; rm keyfile.txt


build-app:
	@echo "Building app image ${IMAGE}"
	gcloud --project ${GOOGLE_CLOUD_PROJECT} builds submit . --region ${GOOGLE_CLOUD_REGION} --suppress-logs --tag ${IMAGE} || true

deploy-app:
	@echo "Deploying app image ${IMAGE}"
	gcloud --project ${GOOGLE_CLOUD_PROJECT} run deploy synapse image ${IMAGE} --region ${GOOGLE_CLOUD_REGION}
	gcloud --project ${GOOGLE_CLOUD_PROJECT} run services --region ${GOOGLE_CLOUD_REGION} add-iam-policy-binding synapse --member="allUsers" --role=roles/run.invoker

pulumi-configure:
	cd infrastructure && pulumi login gs://${PULUMI_STATE_BUCKET}
	cd infrastructure && pulumi stack select prod
	cd infrastructure && pulumi stack change-secrets-provider "gcpkms://projects/${GOOGLE_CLOUD_PROJECT}/locations/${GOOGLE_CLOUD_REGION}/keyRings/pulumi-secrets/cryptoKeys/pulumi-secrets-key"
	cd infrastructure && pulumi config set gcp:project ${GOOGLE_CLOUD_PROJECT}
	cd infrastructure && pulumi config set gcp:region ${GOOGLE_CLOUD_REGION}

pulumi-preview:
	cd infrastructure &&  pulumi preview

pulumi-up:
	cd infrastructure && pulumi up --yes

# Pulumi operations only
pulumi-deploy: pulumi-configure pulumi-preview pulumi-up
all: build-app deploy-app pulumi-configure pulumi-preview pulumi-up