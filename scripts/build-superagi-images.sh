#!/bin/bash
# Script to build SuperAGI Docker images locally

set -e

# Default values
VERSION="latest"
ENVIRONMENT="dev"
REGISTRY_URL="localhost:5000"
PUSH=false
SUPERAGI_VERSION="main"
BUILD_BASE=true
BUILD_CUSTOM=true

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
    --superagi-version)
      SUPERAGI_VERSION="$2"
      shift
      shift
      ;;
    --skip-base)
      BUILD_BASE=false
      shift
      ;;
    --skip-custom)
      BUILD_CUSTOM=false
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --version, -v VERSION       Version tag for the images (default: latest)"
      echo "  --environment, -e ENV       Environment to build for (dev, staging, prod) (default: dev)"
      echo "  --registry, -r URL          Registry URL (default: localhost:5000)"
      echo "  --push, -p                  Push images to registry"
      echo "  --superagi-version VERSION  SuperAGI version/branch to use (default: main)"
      echo "  --skip-base                 Skip building the base image"
      echo "  --skip-custom               Skip building the custom image"
      echo "  --help, -h                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Building SuperAGI Docker images with the following configuration:"
echo "  Version: $VERSION"
echo "  Environment: $ENVIRONMENT"
echo "  Registry URL: $REGISTRY_URL"
echo "  Push to registry: $PUSH"
echo "  SuperAGI Version: $SUPERAGI_VERSION"
echo ""

# Build base image
if [ "$BUILD_BASE" = true ]; then
  echo "Building SuperAGI base image..."
  docker build -t $REGISTRY_URL/superagi-base:$VERSION \
    --build-arg SUPERAGI_VERSION=$SUPERAGI_VERSION \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    ./superagi
  
  if [ "$PUSH" = true ]; then
    echo "Pushing SuperAGI base image to registry..."
    docker push $REGISTRY_URL/superagi-base:$VERSION
  fi
fi

# Build custom image
if [ "$BUILD_CUSTOM" = true ]; then
  echo "Building SuperAGI custom image..."
  
  # Create temporary Dockerfile for the custom image
  cat > Dockerfile.custom << EOF
FROM $REGISTRY_URL/superagi-base:$VERSION

# Copy custom configurations and extensions
COPY ./superagi/custom/ /app/custom/

# Install additional dependencies if needed
RUN if [ -f /app/custom/requirements.txt ]; then \\
      pip install --no-cache-dir -r /app/custom/requirements.txt; \\
    fi

# Copy custom entrypoint script
COPY ./superagi/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set environment variables for Cauldron integration
ENV CAULDRON_INTEGRATION=true

# Expose port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
EOF
  
  # Build the custom image
  docker build -t $REGISTRY_URL/superagi:$VERSION -f Dockerfile.custom .
  
  if [ "$PUSH" = true ]; then
    echo "Pushing SuperAGI custom image to registry..."
    docker push $REGISTRY_URL/superagi:$VERSION
  fi
  
  # Clean up
  rm Dockerfile.custom
fi

echo "SuperAGI Docker image build process completed successfully!"
