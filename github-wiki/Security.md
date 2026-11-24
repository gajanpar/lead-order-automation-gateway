# Security Policy

## Project status

Order & Lead Automation Gateway is an early-stage development project. It is not yet intended to be exposed as a production service handling sensitive customer information without additional security work.

## Supported versions

There are no formal release versions or support commitments yet. Security fixes should be made against the current default branch.

## Reporting a vulnerability

Please do not publish credentials, customer data, or detailed exploit instructions in a public issue.

Use GitHub's private vulnerability reporting feature if it is enabled for this repository. Otherwise, contact the repository owner through a verified contact method listed on the GitHub profile.

## Security checklist before deployment

- Restrict CORS to trusted origins.
- Add authentication and authorization.
- Secure the n8n editor and webhook endpoints.
- Keep secrets out of source control.
- Use HTTPS.
- Pin container and dependency versions.
- Add rate limiting and request-size limits.
- Avoid unnecessary logging of personal information.
- Define data retention and deletion policies.
- Add monitoring, backups, and incident response procedures.
