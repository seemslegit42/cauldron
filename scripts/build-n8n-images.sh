#!/bin/bash
# Script to build n8n Docker images locally

set -e

# Default values
VERSION="latest"
ENVIRONMENT="dev"
REGISTRY_URL="localhost:5000"
PUSH=false
N8N_VERSION="latest"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --version|-v)
      VERSION="$2"
      shift
      shift
      ;;
    --environment|-e)
      ENVIRONMENT="$2"
      shift
      shift
      ;;
    --registry|-r)
      REGISTRY_URL="$2"
      shift
      shift
      ;;
    --push|-p)
      PUSH=true
      shift
      ;;
    --n8n-version)
      N8N_VERSION="$2"
      shift
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --version, -v VERSION       Version tag for the images (default: latest)"
      echo "  --environment, -e ENV       Environment to build for (dev, staging, prod) (default: dev)"
      echo "  --registry, -r URL          Registry URL (default: localhost:5000)"
      echo "  --push, -p                  Push images to registry"
      echo "  --n8n-version VERSION       n8n version to use (default: latest)"
      echo "  --help, -h                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Building n8n Docker image with the following configuration:"
echo "  Version: $VERSION"
echo "  Environment: $ENVIRONMENT"
echo "  Registry URL: $REGISTRY_URL"
echo "  Push to registry: $PUSH"
echo "  n8n Version: $N8N_VERSION"
echo ""

# Build n8n image
echo "Building n8n image..."
docker build -t $REGISTRY_URL/n8n:$VERSION \
  --build-arg N8N_VERSION=$N8N_VERSION \
  --build-arg ENVIRONMENT=$ENVIRONMENT \
  ./n8n

if [ "$PUSH" = true ]; then
  echo "Pushing n8n image to registry..."
  docker push $REGISTRY_URL/n8n:$VERSION
fi

echo "n8n Docker image build process completed successfully!"
