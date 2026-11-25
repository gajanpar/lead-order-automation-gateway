# Roadmap

This roadmap describes proposed improvements. An unchecked item is not implemented and should not be advertised as a working feature.

## API foundation

- [x] Replace the current tracking ID generation with UUID or ULID (`ORD-<uuid4>`).
- [x] Improve phone-number parsing and validation.
- [x] Separate API acceptance (`202 Accepted`) from downstream delivery confirmation (`201 Created`).
- [x] Add structured application logging (`logging` with `tracking_id`, without raw PII).
- [x] Add automated API and normalization tests (`pytest`).

## Workflow reliability

- [ ] Add durable handling for events that fail to reach n8n.
- [ ] Add retry and timeout policies.
- [ ] Add delivery status tracking.
- [ ] Add idempotency protection to prevent duplicate processing.

## Business integrations

- [ ] Google Sheets destination.
- [ ] Airtable or CRM destination.
- [ ] Telegram notifications.
- [ ] WhatsApp Business API notifications.

## Security and operations

- [x] Restrict CORS to trusted origins (`CORS_ORIGINS`, credentials disabled for wildcard).
- [ ] Add API authentication and rate limiting.
- [x] Pin tested Docker image versions (`n8n:2.48.8`).
- [x] Add container health checks (`api_gateway` Compose health check).
- [x] Add CI checks for tests and linting (`pytest` in GitHub Actions).
- [ ] Document production deployment, backup, and recovery.

## Documentation and community

- [ ] Add screenshots and a short demo.
- [ ] Publish versioned releases.
- [ ] Maintain a changelog.
- [ ] Add a contribution guide and issue templates.
