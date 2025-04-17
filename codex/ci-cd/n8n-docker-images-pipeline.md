# n8n Docker Images CI/CD Pipeline

This document describes the CI/CD pipeline for building n8n Docker images for the Cauldron project.

## Overview

The n8n Docker images CI/CD pipeline is responsible for building and publishing Docker images for the n8n workflow automation component of the Cauldron system. The pipeline builds a customized n8n image with Cauldron-specific configurations and integrations.

## Pipeline Workflow

The pipeline is implemented using GitHub Actions and is triggered by:

- Pushes to the `main` or `develop` branches that modify files in the `n8n/` directory
- Pull requests that modify files in the `n8n/` directory
- Manual triggers via the GitHub Actions UI

### Pipeline Stages

The pipeline consists of the following stages:

1. **Build n8n Image**: Builds the n8n Docker image with Cauldron-specific configurations
2. **Create Helm Chart**: Creates or updates the Helm chart for deploying n8n in Kubernetes

### Image Tagging Strategy

Images are tagged using the following strategy:

- For manual triggers: The version specified in the workflow dispatch input
- For pushes to `main`: `latest`
- For pushes to other branches: `sha-{git-sha}`
- For all builds: The branch name and git SHA are also added as tags

## Local Development

For local development, a script is provided to build the n8n Docker images locally:

```bash
./scripts/build-n8n-images.sh
```

### Script Options

The script supports the following options:

- `--version, -v VERSION`: Version tag for the images (default: latest)
- `--environment, -e ENV`: Environment to build for (dev, staging, prod) (default: dev)
- `--registry, -r URL`: Registry URL (default: localhost:5000)
- `--push, -p`: Push images to registry
- `--n8n-version VERSION`: n8n version to use (default: latest)
- `--help, -h`: Show help message

### Examples

Build the image for development:

```bash
./scripts/build-n8n-images.sh
```

Build and push production image to a custom registry:

```bash
./scripts/build-n8n-images.sh --environment prod --registry ghcr.io/myorg --push
```

Build with a specific n8n version:

```bash
./scripts/build-n8n-images.sh --n8n-version 0.214.0
```

## Image Structure

The n8n Docker image contains:

- Node.js 18
- n8n workflow automation platform
- PostgreSQL client for database connectivity
- Custom entrypoint script for initialization and configuration

## Environment-Specific Builds

The pipeline supports building images for different environments:

- **Development**: Minimal configuration, suitable for local development
- **Staging**: Similar to production but may include additional debugging
- **Production**: Optimized for performance and security

## Integration with Helm Charts

The pipeline automatically creates or updates the Helm chart for deploying n8n in Kubernetes. The Helm chart includes:

- Deployment configuration for n8n
- Service and ingress for accessing n8n
- Persistent volume claim for storing n8n data
- ConfigMap and Secret for configuration
- Environment-specific values files (dev, staging, prod)

## Security Considerations

- Images are built using Docker BuildKit for improved security and performance
- Sensitive information is stored in Kubernetes Secrets
- Network policies restrict communication between components
- Health checks ensure the application is functioning properly

## n8n Configuration

The n8n Docker image is configured with the following settings:

- PostgreSQL database for storing workflows and credentials
- Custom environment variables for Cauldron-specific configurations
- Timezone and locale settings
- Webhook URL configuration for external triggers

## Future Improvements

- Add automated testing of the built images
- Implement multi-architecture builds (amd64, arm64)
- Add support for custom n8n nodes and credentials
- Implement image signing for enhanced security
- Add integration with container vulnerability scanning tools
- Implement backup and restore mechanisms for n8n data
