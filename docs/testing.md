# Testing

## Current status

The repository's initial implementation does not yet provide a complete automated test suite. Treat this page as the test plan and contributor guide, not as a claim that tests already pass.

## Recommended coverage

### API validation

- Valid order payload is accepted.
- Missing required fields are rejected.
- Invalid email is rejected.
- Unsupported service type is rejected.
- Non-positive budget is rejected.
- Notes longer than the allowed limit are rejected.

### Data normalization

- Indonesian phone numbers beginning with `0` are normalized as expected.
- Numbers beginning with `62` are handled correctly.
- Inputs containing spaces, plus signs, or separators are handled consistently.
- Invalid or ambiguous phone numbers are rejected rather than silently altered.

### n8n forwarding

- Successful webhook response sets `forwarded_to_n8n` appropriately.
- Connection errors are represented accurately.
- Timeout behavior is predictable.
- Failed forwarding is observable and does not get described as completed downstream processing.

## Suggested tools

- `pytest` for Python tests.
- FastAPI `TestClient` for endpoint tests.
- Mocking tools such as `unittest.mock` for outbound HTTP requests.
- GitHub Actions for running checks on pull requests.

Add the actual test commands here once the test suite and dependencies are committed.
