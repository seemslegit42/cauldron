# Cauldron SuperAGI Docker

This directory contains the Docker setup for the SuperAGI agent framework component of the Cauldron system.

## Overview

The Cauldron SuperAGI Docker setup provides:

- A customized SuperAGI agent framework
- Cauldron-specific extensions and configurations
- Integration with other Cauldron components
- Environment-specific builds for development, staging, and production

## Docker Images

The following Docker images are built from this directory:

1. **superagi-base**: Standard SuperAGI installation
2. **superagi**: Cauldron-specific SuperAGI image with customizations

## Directory Structure

- `Dockerfile`: Dockerfile for the SuperAGI base image
- `entrypoint.sh`: Entrypoint script for the Docker containers
- `custom/`: Directory for Cauldron-specific customizations
  - `requirements.txt`: Additional Python dependencies
  - `config.json`: Custom configuration for SuperAGI
  - `extensions/`: Custom extensions for SuperAGI (if any)

## Building Images

### Using GitHub Actions

The images are automatically built and published using GitHub Actions when changes are pushed to the repository. See the `.github/workflows/build-superagi-images.yml` file for details.

### Building Locally

To build the images locally, use the provided script:

```bash
./scripts/build-superagi-images.sh
```

For more options, run:

```bash
./scripts/build-superagi-images.sh --help
```

## Using the Images

### Docker Compose

The images can be used with Docker Compose. Here's an example:

```yaml
version: '3'

services:
  superagi:
    image: ghcr.io/seemslegit42/superagi:latest
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN}
      - DATABASE_URL=postgresql://postgres:${DB_ROOT_PASSWORD}@postgres:5432/superagi
      - VECTOR_DB_URL=http://qdrant:6333
      - DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
      - DB_HOST=postgres
    volumes:
      - superagi-data:/app/data
    depends_on:
      - postgres
      - qdrant

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=${DB_ROOT_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant-data:/qdrant/storage

volumes:
  superagi-data:
  postgres-data:
  qdrant-data:
```

### Kubernetes

For Kubernetes deployment, use the Helm chart provided in the `cauldron-superagi` directory.

## Environment Variables

The Docker images support the following environment variables:

- `OPENAI_API_KEY`: OpenAI API key for LLM access
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude access
- `HUGGINGFACE_TOKEN`: Hugging Face token for model access
- `DATABASE_URL`: PostgreSQL connection URL
- `VECTOR_DB_URL`: Qdrant connection URL
- `DB_ROOT_PASSWORD`: PostgreSQL root password
- `DB_HOST`: PostgreSQL host
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `DEBUG`: Enable debug mode (True/False)
- `ENVIRONMENT`: Environment (dev, staging, prod)

## Cauldron-Specific Customizations

The SuperAGI images include several Cauldron-specific customizations:

1. **Agent Templates**: Pre-configured agent templates for different roles in the Cauldron system
2. **Integration with Frappe/ERPNext**: Tools and configurations for interacting with the Frappe/ERPNext backend
3. **Integration with RabbitMQ**: Support for event-driven architecture using RabbitMQ
4. **Integration with Qdrant**: Configuration for using Qdrant as the vector store
5. **Monitoring and Observability**: Integration with Prometheus and OpenTelemetry for monitoring

## Development

For development, it's recommended to use the Docker Compose setup provided in the root directory of the repository. This setup mounts the local directories into the containers, allowing for live code changes.

## Production

For production deployment, it's recommended to use the Kubernetes Helm chart provided in the `cauldron-superagi` directory. The Helm chart supports different environments (dev, staging, prod) with appropriate configurations for each.

## Troubleshooting

### Common Issues

1. **Database connection issues**:
   - Check if the PostgreSQL container is running
   - Verify the database credentials
   - Check if the database exists

2. **Vector database issues**:
   - Check if the Qdrant container is running
   - Verify the Qdrant connection URL
   - Check if the Qdrant collections exist

3. **LLM API issues**:
   - Verify the API keys are correctly set
   - Check if the LLM provider is accessible
   - Check the SuperAGI logs for API errors

For more help, refer to the [SuperAGI documentation](https://superagi.com/docs/) or open an issue in the Cauldron repository.
