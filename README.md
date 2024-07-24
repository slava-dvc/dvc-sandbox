# vcmate-synapse

## Description
VcMate Backend is a FastAPI-based service that processes PDF files with LLM to extract structured data. It serves as the backend for the VcMate project, providing PDF processing, CRM integrations, workspace management, and user management functionalities and everything else. 

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone git@github.com:vctuna/vcmate-synapse.git
   cd vcmate-synapse
   ```

2. Make venv and Install dependencies:
   ```bash
   python3 -m venv .venv  
   source .venv/bin/activate.[fish, csh, bash]
   pip install -Ur requirements.txt
   ```

3. Configure google cloud auth
    Install if you didn't already [google cloud cli](https://cloud.google.com/sdk/docs/install-sdk ) then obtain credentials:
    ```bash
    gcloud init
    ```

4. Run the FastAPI server:
    As in production 
    ```bash
    python3 -m app.backend --port 8000
    ```
    For development 
    ```bash
    fastapi run app/backend.py --port 8000
    ```

The server will start on `http://localhost:8000`.

## How to Test

Currently, there are no unit tests implemented. Use and add sample requests from the http/ folder

## How to Deploy

To deploy the project, we use Pulumi for infrastructure management and Docker for containerization. Use the following command:

```
make deploy
```

This command will build the Docker image, push it to the container registry, and deploy the application to Google Cloud Run using Pulumi.

## Project Structure

```
vcmate-backend/
├── app/                  # Application code
│   ├── deals/            # Deal processing module
│   ├── integrations/     # CRM and other integrations
│   ├── workspaces/       # Workspace management
│   ├── users/            # User management
│   ├── foundation/       # Shared utilities and configurations
│   ├── backend.py        # Entry point for the backend application
│   └── other_service.py  # Entry point for the other services 
├── infrastructure/       # Pulumi deployment code
├── tests/                # Test directory
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── Makefile              # Make commands for common tasks
└── README.md             # This file
```

- `app/`: Contains all the application code, organized by domain with common code in foundation folder 
- `infrastructure/`: Houses the Pulumi code for deploying to Google Cloud.
- `Dockerfile`: Defines the Docker image for the application.
- `Makefile`: Provides shortcuts for common development and deployment tasks.
```