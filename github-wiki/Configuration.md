# Configuration

This guide describes the environment configuration used by the local Docker Compose setup.

## Environment variables

| Variable | Service | Purpose |
| --- | --- | --- |
| `N8N_WEBHOOK_URL` | FastAPI | Webhook URL used to forward events |
| `N8N_TIMEOUT_SECONDS` | FastAPI | Timeout in seconds for forwarding events to n8n (default `4.0`) |
| `STRICT_WEBHOOK_DELIVERY` | FastAPI | Return `502 Bad Gateway` instead of `202 Accepted` when n8n delivery fails (default `false`) |
| `CORS_ORIGINS` | FastAPI | Comma-separated list of allowed CORS origins |
| `CORS_ALLOW_CREDENTIALS` | FastAPI | Enable CORS credentials when non-wildcard origins are set (default `false`) |
| `LOG_LEVEL` | FastAPI | Python logging level (default `INFO`) |
| `ENVIRONMENT` | FastAPI | Application environment label |
| `N8N_HOST` | n8n | Hostname configured for n8n |
| `N8N_PORT` | n8n | n8n port |
| `N8N_PROTOCOL` | n8n | Protocol configured for n8n |
| `GENERIC_TIMEZONE` | n8n | Timezone used by n8n |
| `TZ` | containers | Container timezone |

Refer to the committed `docker-compose.yml` for the actual defaults. Do not copy secrets into documentation or commit them to Git.

## Docker service-to-service URL

Inside the Compose network, the API should reach n8n through the service name:

```text
http://n8n:5678/webhook/lead-ingest
```

Container `localhost` is not the same as the host computer's `localhost` or another container.

## Local API development without Docker

If you want to run the API directly with Python:

```bash
cd api
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies and start the API:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Set `N8N_WEBHOOK_URL` to a webhook address reachable from the process before testing forwarding.

## Production considerations

- Use HTTPS behind a properly configured reverse proxy.
- Store credentials in environment secrets or a secret manager.
- Restrict CORS to known frontend origins.
- Pin tested container image versions.
- Secure the n8n editor and webhook endpoints.
- Configure backups for persistent n8n data.
- Add authentication, rate limiting, monitoring, and retry handling before public deployment.
