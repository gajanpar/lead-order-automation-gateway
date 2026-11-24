# API Reference

This page documents the currently exposed API routes.

## Base URL

For local development:

```text
http://localhost:8000
```

Interactive OpenAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## `GET /health`

Checks whether the FastAPI process is responding.

### Example

```bash
curl http://localhost:8000/health
```

The current response shape is:

```json
{
  "status": "ok",
  "service": "fastapi-gateway"
}
```

This is a process-level health check. It does not necessarily prove that n8n or downstream integrations are healthy.

## `POST /api/v1/orders`

Accepts an order or lead submission.

### Request fields

| Field | Type | Required | Validation / notes |
| --- | --- | --- | --- |
| `customer_name` | string | Yes | 2–100 characters |
| `customer_email` | email | Yes | Must be a valid email address |
| `customer_whatsapp` | string | Yes | 9–18 characters |
| `service_type` | string | Yes | `custom_software`, `workflow_automation`, or `consultation` |
| `budget_estimate_idr` | number | Yes | Must be greater than zero |
| `notes` | string or null | No | Maximum 500 characters |

### Example request

```json
{
  "customer_name": "Rian Kusuma",
  "customer_email": "rian.kusuma@example.com",
  "customer_whatsapp": "081234567890",
  "service_type": "workflow_automation",
  "budget_estimate_idr": 4500000,
  "notes": "Connect incoming orders to an internal workflow"
}
```

### Example cURL request

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Rian Kusuma",
    "customer_email": "rian.kusuma@example.com",
    "customer_whatsapp": "081234567890",
    "service_type": "workflow_automation",
    "budget_estimate_idr": 4500000,
    "notes": "Connect incoming orders to an internal workflow"
  }'
```

### Response fields

The response model includes:

| Field | Meaning |
| --- | --- |
| `status` | API-level result |
| `tracking_id` | Identifier generated for the request |
| `received_at` | Timestamp recorded by the API |
| `forwarded_to_n8n` | Whether forwarding to n8n was confirmed |

The exact response schema can be inspected in `/docs`.

### Status-code interpretation

A `201 Created` response indicates that the API accepted the request. It must not be interpreted as proof that an external workflow completed successfully. Check `forwarded_to_n8n` and n8n execution history.

## Validation errors

FastAPI returns a validation response when required fields are missing or values do not match the request schema. Use `/docs` to inspect the live OpenAPI schema and try requests interactively.
