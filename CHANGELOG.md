# Changelog

Notable project changes are recorded here.

The project has not adopted a formal release process yet.

## Unreleased

- Replaced timestamp/hash tracking IDs with collision-resistant UUIDv4 identifiers (`ORD-<uuid4>`).
- Differentiated API acceptance (`202 accepted_unforwarded`) from confirmed n8n webhook delivery (`201 forwarded`) and added optional `STRICT_WEBHOOK_DELIVERY=true` (`502`).
- Hardened Indonesian and E.164 WhatsApp number validation and normalization (`api/validators.py`).
- Restricted CORS origins via `CORS_ORIGINS` and disabled wildcard credentials.
- Pinned `n8n` Docker image to `2.48.8` and added a container health check for `api_gateway`.
- Added `pytest` suite (`api/tests/test_orders.py`) and integrated it into GitHub Actions CI.
- Refined the public-facing README for beginner and developer audiences.
- Added architecture, API, configuration, development, testing, troubleshooting, and roadmap documentation.
- Added security and contribution guidance.
- Added GitHub issue and pull request templates.
- Added a starter CI workflow.
