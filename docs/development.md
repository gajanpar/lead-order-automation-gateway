# Local Development

This guide is for contributors who want to inspect or change the application.

## Prerequisites

- Git
- Python version compatible with the project dependencies (the current project targets Python 3.13)
- Docker and Docker Compose for the full local stack
- A code editor

## Run the full stack

From the repository root:

```bash
docker compose up -d --build
docker compose ps
```

Useful log commands:

```bash
docker compose logs -f api_gateway
docker compose logs -f n8n
```

Stop the services:

```bash
docker compose down
```

To also remove the named n8n data volume:

```bash
docker compose down -v
```

> Warning: `docker compose down -v` deletes persisted n8n data for this local Compose project.

## Run only the API

```bash
cd api
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API docs should be available at `http://localhost:8000/docs`.

## Workflow changes

The n8n workflow template is stored in `n8n/workflow_template.json`. When changing it:

1. Make the change in a local n8n workspace.
2. Export the workflow JSON.
3. Remove or replace any personal credentials and environment-specific values.
4. Review the diff before committing.
5. Update the architecture and README if behavior changes.

Never commit real API tokens, customer records, or personal credentials.

## Before opening a pull request

- Test the affected behavior.
- Update documentation for changed setup or API behavior.
- Check that no secrets or personal data are included.
- Describe what you tested in the pull request.
