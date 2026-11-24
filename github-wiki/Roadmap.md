# Roadmap

This roadmap describes proposed improvements. An unchecked item is not implemented and should not be advertised as a working feature.

## API foundation

- [ ] Replace the current tracking ID generation with UUID or ULID.
- [ ] Improve phone-number parsing and validation.
- [ ] Separate API acceptance from downstream delivery status more clearly.
- [ ] Add structured logs and request correlation IDs.
- [ ] Add automated API and normalization tests.

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

- [ ] Restrict CORS to trusted origins.
- [ ] Add API authentication and rate limiting.
- [ ] Pin tested Docker image versions.
- [ ] Add container health checks.
- [ ] Add CI checks for tests and linting.
- [ ] Document production deployment, backup, and recovery.

## Documentation and community

- [ ] Add screenshots and a short demo.
- [ ] Publish versioned releases.
- [ ] Maintain a changelog.
- [ ] Add a contribution guide and issue templates.
