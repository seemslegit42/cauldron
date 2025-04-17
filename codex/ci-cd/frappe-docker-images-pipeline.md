# Frappe Docker Images CI/CD Pipeline

This document describes the CI/CD pipeline for building Frappe Docker images for the Cauldron project.

## Overview

The Frappe Docker images CI/CD pipeline is responsible for building and publishing Docker images for the Frappe/ERPNext components of the Cauldron system. The pipeline builds three types of images:

1. **Base Image**: Contains the Frappe Bench environment without any apps
2. **App-Specific Images**: Contains the base image plus a specific Cauldron app
3. **Complete Image**: Contains the base image plus all Cauldron apps

## Pipeline Workflow

The pipeline is implemented using GitHub Actions and is triggered by:

- Pushes to the `main` or `develop` branches that modify files in the `frappe/` directory
- Pull requests that modify files in the `frappe/` directory
- Manual triggers via the GitHub Actions UI

### Pipeline Stages

The pipeline consists of the following stages:

1. **Build Frappe Base Image**: Builds the base Frappe Bench environment
2. **Build Frappe App Images**: Builds individual images for each Cauldron app
3. **Build Complete Frappe Image**: Builds a complete image with all Cauldron apps
4. **Update Helm Chart Values**: Updates the Helm chart values with the new image tags

### Image Tagging Strategy

Images are tagged using the following strategy:

- For manual triggers: The version specified in the workflow dispatch input
- For pushes to `main`: `latest`
- For pushes to other branches: `sha-{git-sha}`
- For all builds: The branch name and git SHA are also added as tags

## Local Development

For local development, a script is provided to build the Frappe Docker images locally:

```bash
./scripts/build-frappe-images.sh
```

### Script Options

The script supports the following options:

- `--version, -v VERSION`: Version tag for the images (default: latest)
- `--environment, -e ENV`: Environment to build for (dev, staging, prod) (default: dev)
- `--registry, -r URL`: Registry URL (default: localhost:5000)
- `--push, -p`: Push images to registry
- `--skip-base`: Skip building the base image
- `--skip-apps`: Skip building the app-specific images
- `--skip-complete`: Skip building the complete image
- `--frappe-version VERSION`: Frappe version to use (default: v15)
- `--erpnext-version VERSION`: ERPNext version to use (default: v15)
- `--help, -h`: Show help message

### Examples

Build all images for development:

```bash
./scripts/build-frappe-images.sh
```

Build and push production images to a custom registry:

```bash
./scripts/build-frappe-images.sh --environment prod --registry ghcr.io/myorg --push
```

Build only the complete image:

```bash
./scripts/build-frappe-images.sh --skip-base --skip-apps
```

## Image Structure

### Base Image

The base image contains:

- Python 3.11
- Node.js 18
- Frappe Bench
- System dependencies required for Frappe/ERPNext

### App-Specific Images

Each app-specific image contains:

- The base image
- Frappe framework
- ERPNext
- A specific Cauldron app (e.g., cauldron_operations_core)

### Complete Image

The complete image contains:

- The base image
- Frappe framework
- ERPNext
- All Cauldron apps:
  - cauldron_operations_core
  - cauldron_synapse
  - cauldron_aegis_protocol
  - cauldron_lore
  - cauldron_command_cauldron

## Environment-Specific Builds

The pipeline supports building images for different environments:

- **Development**: Developer mode enabled, no production optimizations
- **Staging**: Similar to production but may include additional debugging
- **Production**: Developer mode disabled, assets built for production

## Integration with Helm Charts

The pipeline automatically updates the Helm chart values with the new image tags when triggered by a push to `main` or a manual workflow dispatch. This ensures that the Helm charts always reference the latest images.

## Security Considerations

- Images are built using Docker BuildKit for improved security and performance
- Images are scanned for vulnerabilities before being published
- Production images are built with minimal dependencies to reduce the attack surface

## Future Improvements

- Add automated testing of the built images
- Implement multi-architecture builds (amd64, arm64)
- Add support for custom app repositories and branches
- Implement image signing for enhanced security
- Add integration with container vulnerability scanning tools
