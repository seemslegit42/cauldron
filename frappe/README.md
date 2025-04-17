# Cauldron Frappe Docker

This directory contains the Docker setup for the Frappe/ERPNext components of the Cauldron system.

## Overview

The Cauldron Frappe Docker setup provides:

- A base Frappe Bench environment
- Custom Cauldron apps built on Frappe/ERPNext
- Configuration for integration with other Cauldron components

## Docker Images

The following Docker images are built from this directory:

1. **frappe-base**: Base Frappe Bench environment without any apps
2. **frappe-{app_name}**: Individual images for each Cauldron app
3. **frappe-complete**: Complete image with all Cauldron apps

## Directory Structure

- `Dockerfile`: Dockerfile for the base Frappe Bench environment
- `entrypoint.sh`: Entrypoint script for the Docker containers
- `common_site_config.json`: Common site configuration for Frappe Bench

## Building Images

### Using GitHub Actions

The images are automatically built and published using GitHub Actions when changes are pushed to the repository. See the `.github/workflows/build-frappe-images.yml` file for details.

### Building Locally

To build the images locally, use the provided script:

```bash
./scripts/build-frappe-images.sh
```

For more options, run:

```bash
./scripts/build-frappe-images.sh --help
```

## Using the Images

### Docker Compose

The images can be used with Docker Compose. Here's an example:

```yaml
version: '3'

services:
  frappe:
    image: ghcr.io/seemslegit42/frappe-complete:latest
    ports:
      - "8000:8000"
      - "9000:9000"
    environment:
      - SITE_NAME=cauldron.local
      - ADMIN_PASSWORD=admin
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=frappe
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    volumes:
      - frappe-sites:/home/frappe/frappe-bench/sites
    depends_on:
      - postgres
      - redis-cache
      - redis-queue
      - redis-socketio

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis-cache:
    image: redis:7-alpine
    volumes:
      - redis-cache-data:/data

  redis-queue:
    image: redis:7-alpine
    volumes:
      - redis-queue-data:/data

  redis-socketio:
    image: redis:7-alpine
    volumes:
      - redis-socketio-data:/data

volumes:
  frappe-sites:
  postgres-data:
  redis-cache-data:
  redis-queue-data:
  redis-socketio-data:
```

### Kubernetes

For Kubernetes deployment, use the Helm chart provided in the `cauldron-frappe` directory.

## Environment Variables

The Docker images support the following environment variables:

- `SITE_NAME`: Name of the Frappe site (default: cauldron.local)
- `ADMIN_PASSWORD`: Admin password for the Frappe site
- `DB_HOST`: PostgreSQL host
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `STANDARD_APPS`: Comma-separated list of standard apps to install (format: app_name:branch)
- `CUSTOM_APPS`: Comma-separated list of custom apps to install (format: app_name:repo:branch)

## Custom Apps

The following custom Cauldron apps are included in the complete image:

- **cauldron_operations_core**: Core ERP extensions
- **cauldron_synapse**: Business intelligence and predictive analytics
- **cauldron_aegis_protocol**: Security monitoring and management
- **cauldron_lore**: Knowledge management and organizational memory
- **cauldron_command_cauldron**: DevOps and infrastructure management

## Development

For development, it's recommended to use the Docker Compose setup provided in the root directory of the repository. This setup mounts the local directories into the containers, allowing for live code changes.

## Production

For production deployment, it's recommended to use the Kubernetes Helm chart provided in the `cauldron-frappe` directory. The Helm chart supports different environments (dev, staging, prod) with appropriate configurations for each.

## Troubleshooting

### Common Issues

1. **Database connection issues**:
   - Check if the PostgreSQL container is running
   - Verify the database credentials
   - Check if the database exists

2. **Redis connection issues**:
   - Check if the Redis containers are running
   - Verify the Redis connection settings in `common_site_config.json`

3. **App installation issues**:
   - Check if the app repository is accessible
   - Verify the branch name
   - Check for any errors in the app installation logs

For more help, refer to the [Frappe Framework documentation](https://frappeframework.com/docs) or open an issue in the Cauldron repository.
