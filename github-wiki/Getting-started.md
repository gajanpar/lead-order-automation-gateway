# Getting started

## Requirements
- Git
- Docker Desktop or Docker Engine with Docker Compose
- Local ports `8000` and `5678` available

## Start the project

```bash
git clone https://github.com/gajanpar/lead-order-automation-gateway.git
cd lead-order-automation-gateway
docker compose up -d --build
```

Open the API docs at http://localhost:8000/docs and n8n at http://localhost:5678.

Import `n8n/workflow_template.json` through the n8n editor if it is not already in the workspace. The file being mounted into the container does not automatically import it. The template is inactive (`active: false`), so activate it before testing the production webhook URL.
