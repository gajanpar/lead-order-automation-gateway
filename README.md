# Order & Lead Automation Gateway

**A simple starting point for turning incoming orders and customer inquiries into structured, trackable workflow events.**

Order & Lead Automation Gateway is a small automation project built with **FastAPI** and **n8n**. It receives order or lead information through an API, checks that the data is valid, tidies up selected fields, creates a tracking ID, and sends the event to an n8n webhook.

The goal is straightforward: reduce repetitive copy-and-paste work and give incoming requests a more consistent path through your business process.

> **Project status:** Early-stage showcase / development project. The API-to-n8n handoff and basic data formatting are implemented. External destinations such as Google Sheets, Airtable, Telegram, and WhatsApp Business API are not yet connected in the current workflow template.

## What can it do today?

- Accept an order or lead through `POST /api/v1/orders`.
- Validate required fields using Pydantic.
- Normalize common Indonesian WhatsApp number formats.
- Generate a tracking ID and timestamp.
- Forward the event to an n8n webhook when the workflow service is reachable.
- Format the incoming data and an IDR budget value in n8n.
- Provide an API health endpoint and interactive API docs.

## How it works

```text
Your form / app / API client
          |
          | POST JSON
          v
     FastAPI Gateway
     - validate input
     - normalize WhatsApp number
     - create tracking ID
          |
          | HTTP webhook
          v
       n8n workflow
       - receive event
       - format data and message
          |
          v
   Future integrations
   (Sheets / CRM / messaging)
```

FastAPI handles the API-facing work. n8n handles the visual workflow orchestration. Keeping those responsibilities separate makes it easier to change the workflow without rewriting the API.

## Quick start

### Requirements

- Docker Desktop or Docker Engine with the Compose plugin
- A terminal
- A free local port `8000` and `5678`

### 1. Get the project

```bash
git clone https://github.com/gajanpar/lead-order-automation-gateway.git
cd lead-order-automation-gateway
```

### 2. Start the services

```bash
docker compose up -d --build
```

Check the running containers:

```bash
docker compose ps
```

### 3. Open the local tools

| Service | Address | What it is for |
| --- | --- | --- |
| FastAPI docs | http://localhost:8000/docs | Try the API from your browser |
| API health | http://localhost:8000/health | Check whether the API is responding |
| n8n | http://localhost:5678 | View and configure the workflow |

The current Compose file binds both services to `127.0.0.1`, so they are intended for local access from the same machine.

### 4. Import the n8n workflow

The Compose file makes `n8n/workflow_template.json` available inside the n8n container. If it is not already present in your n8n workspace, import it from the n8n editor:

1. Open `http://localhost:5678`.
2. Use the workflow import option.
3. Select `n8n/workflow_template.json` from your project folder.
4. Review the nodes and credentials.
5. Activate the workflow in n8n before sending requests to the production webhook URL used by the API.

The committed workflow template has `active: false`, so importing it does not automatically make the production webhook ready. The template currently contains a webhook trigger and a formatting Code node. It does not yet write to Google Sheets or send messages.

## Try the API

Open `http://localhost:8000/docs`, expand `POST /api/v1/orders`, and use this example:

```json
{
  "customer_name": "Rian Kusuma",
  "customer_email": "rian.kusuma@example.com",
  "customer_whatsapp": "081234567890",
  "service_type": "workflow_automation",
  "budget_estimate_idr": 4500000,
  "notes": "Connect incoming orders to a business workflow"
}
```

You can also send the same request with cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Rian Kusuma",
    "customer_email": "rian.kusuma@example.com",
    "customer_whatsapp": "081234567890",
    "service_type": "workflow_automation",
    "budget_estimate_idr": 4500000,
    "notes": "Connect incoming orders to a business workflow"
  }'
```

A successful API response includes a tracking ID and a `forwarded_to_n8n` value. **A successful API response does not guarantee that a downstream workflow or external integration completed successfully.** Check `forwarded_to_n8n` and the n8n execution history.

## API at a glance

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check API availability |
| `POST` | `/api/v1/orders` | Validate and submit an order or lead |

For the full request and response details, see [API Reference](docs/api-reference.md).

## Project structure

```text
.
├── api/                       # FastAPI application
├── n8n/                       # n8n workflow template
├── docs/                      # Project documentation
├── docker-compose.yml         # Local services
└── README.md
```

## Configuration

The API reads `N8N_WEBHOOK_URL` from its environment. In Docker Compose, it points to the n8n service using the internal Docker network:

```text
http://n8n:5678/webhook/lead-ingest
```

See [Configuration](docs/configuration.md) before changing ports, webhook addresses, or deployment settings.

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Security Notes](docs/security.md)
- [Roadmap](docs/roadmap.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Current limitations

This project is still being developed. Before using it for real customer data, keep these points in mind:

- The current n8n template formats the event but does not connect to external storage or messaging providers.
- The API can return HTTP `201` even when forwarding to n8n fails; inspect `forwarded_to_n8n`.
- The current tracking ID implementation should be replaced with a collision-resistant identifier before production use.
- CORS currently allows all origins and should be restricted to trusted frontend origins.
- The n8n Docker image currently uses the `latest` tag. Pin a tested version for repeatable deployments.
- Add authentication, secrets management, tests, logging, retry handling, and monitoring before exposing the service publicly.

## Contributing

Ideas, bug reports, and improvements are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request.

## License

No license has been confirmed for this repository yet. Until the owner adds a license file, the code should not be assumed to be available for unrestricted reuse.
