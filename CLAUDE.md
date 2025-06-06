# DVC Synapse - Dev Guide

## Build & Run Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -Ur requirements.txt`
- Run locally: `python3 -m app.backend --port 8000`
- Run tests: `pytest tests/`
- Run single test: `pytest tests/test_file.py::test_function -v`
- Deploy: `make app-deploy` (builds+deploys app) or `make all` (runs tests + infra+app)


## Testing

- After made any change check that server can be started as `bash -c 'source .venv/bin/activate && source .env &&  python3 -m app.backend --dry-run'`


## Project Structure
Synapse is a FastAPI-powered microservice designed to process PDF files using Large Language Models (LLMs) and extract structured data, with the following structure:

- `app/`: Application code organized by domain
  - `deals/`: Deal processing module
  - `integrations/`: CRM and other integrations
  - `workspaces/`: Workspace management
  - `users/`: User management
  - `foundation/`: Shared utilities and configurations
  - `backend.py`: Entry point for the backend application
  - `job.py`: Entry point for backend jobs
- `infrastructure/`: Pulumi deployment code
  - `services/`: Cloud Run service definitions
  - `topics/`: Pub/Sub topics configuration
- `tests/`: Test directory
- `Dockerfile`: Docker configuration
- `Makefile`: Single source of truth for all operations
- `cloudbuild.yaml`: Cloud Build configuration
- `.github/workflows/`: CI/CD workflows
