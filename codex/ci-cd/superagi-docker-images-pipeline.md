# SuperAGI Docker Images CI/CD Pipeline

This document describes the CI/CD pipeline for building SuperAGI Docker images for the Cauldron project.

## Overview

The SuperAGI Docker images CI/CD pipeline is responsible for building and publishing Docker images for the SuperAGI agent framework component of the Cauldron system. The pipeline builds two types of images:

1. **Base Image**: Contains the standard SuperAGI installation
2. **Custom Image**: Contains the base image plus Cauldron-specific customizations and extensions

## Pipeline Workflow

The pipeline is implemented using GitHub Actions and is triggered by:

- Pushes to the `main` or `develop` branches that modify files in the `superagi/` directory
- Pull requests that modify files in the `superagi/` directory
- Manual triggers via the GitHub Actions UI

### Pipeline Stages

The pipeline consists of the following stages:

1. **Build SuperAGI Base Image**: Builds the standard SuperAGI installation
2. **Build SuperAGI Custom Image**: Builds the Cauldron-specific SuperAGI image with customizations
3. **Update Helm Chart Values**: Updates the Helm chart values with the new image tags

### Image Tagging Strategy

Images are tagged using the following strategy:

- For manual triggers: The version specified in the workflow dispatch input
- For pushes to `main`: `latest`
- For pushes to other branches: `sha-{git-sha}`
- For all builds: The branch name and git SHA are also added as tags

## Local Development

For local development, a script is provided to build the SuperAGI Docker images locally:

```bash
./scripts/build-superagi-images.sh
```

### Script Options

The script supports the following options:

- `--version, -v VERSION`: Version tag for the images (default: latest)
- `--environment, -e ENV`: Environment to build for (dev, staging, prod) (default: dev)
- `--registry, -r URL`: Registry URL (default: localhost:5000)
- `--push, -p`: Push images to registry
- `--superagi-version VERSION`: SuperAGI version/branch to use (default: main)
- `--skip-base`: Skip building the base image
- `--skip-custom`: Skip building the custom image
- `--help, -h`: Show help message

### Examples

Build all images for development:

```bash
./scripts/build-superagi-images.sh
```

Build and push production images to a custom registry:

```bash
./scripts/build-superagi-images.sh --environment prod --registry ghcr.io/myorg --push
```

Build with a specific SuperAGI version:

```bash
./scripts/build-superagi-images.sh --superagi-version v0.1.2
```

## Image Structure

### Base Image

The base image contains:

- Python 3.10
- SuperAGI framework
- System dependencies required for SuperAGI
- Environment-specific configurations

### Custom Image

The custom image contains:

- The base image
- Cauldron-specific extensions and configurations
- Additional dependencies for integration with other Cauldron components
- Custom entrypoint script for initialization and configuration

## Environment-Specific Builds

The pipeline supports building images for different environments:

- **Development**: Debug mode enabled, verbose logging
- **Staging**: Similar to production but may include additional debugging
- **Production**: Debug mode disabled, optimized for performance and security

## Integration with Helm Charts

The pipeline automatically updates the Helm chart values with the new image tags when triggered by a push to `main` or a manual workflow dispatch. This ensures that the Helm charts always reference the latest images.

## Cauldron-Specific Customizations

The SuperAGI images include several Cauldron-specific customizations:

1. **Agent Templates**: Pre-configured agent templates for different roles in the Cauldron system
2. **Integration with Frappe/ERPNext**: Tools and configurations for interacting with the Frappe/ERPNext backend
3. **Integration with RabbitMQ**: Support for event-driven architecture using RabbitMQ
4. **Integration with Qdrant**: Configuration for using Qdrant as the vector store
5. **Monitoring and Observability**: Integration with Prometheus and OpenTelemetry for monitoring

## Security Considerations

- Images are built using Docker BuildKit for improved security and performance
- Sensitive information is stored in environment variables or Kubernetes Secrets
- Environment-specific builds to minimize attack surface in production
- Proper permissions are set for GitHub Actions workflows

## Future Improvements

- Add automated testing of the built images
- Implement multi-architecture builds (amd64, arm64)
- Add support for custom SuperAGI plugins
- Implement image signing for enhanced security
- Add integration with container vulnerability scanning tools
