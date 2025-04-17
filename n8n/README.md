# Cauldron n8n Docker

This directory contains the Docker setup for the n8n workflow automation component of the Cauldron system.

## Overview

The Cauldron n8n Docker setup provides:

- A customized n8n workflow automation platform
- Configuration for integration with other Cauldron components
- Environment-specific builds for development, staging, and production

## Docker Image

The n8n Docker image is built from this directory and includes:

- Node.js 18
- n8n workflow automation platform
- PostgreSQL client for database connectivity
- Custom entrypoint script for initialization and configuration

## Directory Structure

- `Dockerfile`: Dockerfile for the n8n image
- `entrypoint.sh`: Entrypoint script for the Docker container

## Building the Image

### Using GitHub Actions

The image is automatically built and published using GitHub Actions when changes are pushed to the repository. See the `.github/workflows/build-n8n-images.yml` file for details.

### Building Locally

To build the image locally, use the provided script:

```bash
./scripts/build-n8n-images.sh
```

For more options, run:

```bash
./scripts/build-n8n-images.sh --help
```

## Using the Image

### Docker Compose

The image can be used with Docker Compose. Here's an example:

```yaml
version: '3'

services:
  n8n:
    image: ghcr.io/seemslegit42/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - DB_ROOT_PASSWORD=postgres
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=postgres
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - n8n-data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  n8n-data:
  postgres-data:
```

### Kubernetes

For Kubernetes deployment, use the Helm chart provided in the `cauldron-n8n` directory.

## Environment Variables

The Docker image supports the following environment variables:

- `N8N_PORT`: Port on which n8n will listen (default: 5678)
- `N8N_PROTOCOL`: Protocol for n8n (http or https) (default: http)
- `N8N_HOST`: Host name for n8n (default: localhost)
- `WEBHOOK_URL`: URL for webhooks (default: http://localhost:5678/)
- `GENERIC_TIMEZONE`: Timezone for n8n (default: UTC)
- `DB_TYPE`: Database type (default: postgresdb)
- `DB_POSTGRESDB_HOST`: PostgreSQL host (default: postgres)
- `DB_POSTGRESDB_PORT`: PostgreSQL port (default: 5432)
- `DB_POSTGRESDB_DATABASE`: PostgreSQL database name (default: n8n)
- `DB_POSTGRESDB_USER`: PostgreSQL username (default: postgres)
- `DB_ROOT_PASSWORD`: PostgreSQL password

## Development

For development, it's recommended to use the Docker Compose setup provided in the root directory of the repository. This setup mounts the local directories into the containers, allowing for live code changes.

## Production

For production deployment, it's recommended to use the Kubernetes Helm chart provided in the `cauldron-n8n` directory. The Helm chart supports different environments (dev, staging, prod) with appropriate configurations for each.

## Troubleshooting

### Common Issues

1. **Database connection issues**:
   - Check if the PostgreSQL container is running
   - Verify the database credentials
   - Check if the database exists

2. **Webhook issues**:
   - Ensure the `WEBHOOK_URL` is correctly set
   - Check if the n8n container is accessible from the internet if using external webhooks

3. **Workflow execution issues**:
   - Check the n8n logs for errors
   - Verify that all required credentials are set up
   - Check if the n8n container has access to the required services

For more help, refer to the [n8n documentation](https://docs.n8n.io/) or open an issue in the Cauldron repository.
