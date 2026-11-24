# Troubleshooting

## API documentation does not open

1. Run `docker compose ps`.
2. Check API logs:

   ```bash
   docker compose logs api_gateway
   ```

3. Confirm port `8000` is not already in use.

## n8n editor does not open

1. Check whether the n8n container is running.
2. Read its logs:

   ```bash
   docker compose logs n8n
   ```

3. Confirm port `5678` is available.

## `forwarded_to_n8n` is `false`

This means the API did not confirm successful forwarding to the configured n8n webhook.

1. Confirm that the n8n container is running.
2. Check `N8N_WEBHOOK_URL`.
3. From the API container, use the Compose service hostname, for example `http://n8n:5678`.
4. Confirm the workflow has been imported and activated.
5. Inspect the n8n execution history and API logs.

## The workflow is not visible in n8n

A file mounted into a container is not necessarily imported into the n8n workspace. Import `n8n/workflow_template.json` through the n8n editor.

The committed workflow is inactive (`active: false`). Activate it in n8n before testing the production webhook URL.

## Reset local services

Stop containers:

```bash
docker compose down
```

Stop containers and remove the named data volume:

```bash
docker compose down -v
```

**Warning:** the second command deletes persisted n8n data for this Compose project. Do not run it if you need to keep your local workflows or credentials.
