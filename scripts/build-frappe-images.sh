#!/bin/bash
# Script to build Frappe Docker images locally

set -e

# Default values
VERSION="latest"
ENVIRONMENT="dev"
REGISTRY_URL="localhost:5000"
PUSH=false
BUILD_BASE=true
BUILD_APPS=true
BUILD_COMPLETE=true
FRAPPE_VERSION="v15"
ERPNEXT_VERSION="v15"

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
    --skip-base)
      BUILD_BASE=false
      shift
      ;;
    --skip-apps)
      BUILD_APPS=false
      shift
      ;;
    --skip-complete)
      BUILD_COMPLETE=false
      shift
      ;;
    --frappe-version)
      FRAPPE_VERSION="$2"
      shift
      shift
      ;;
    --erpnext-version)
      ERPNEXT_VERSION="$2"
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
      echo "  --skip-base                 Skip building the base image"
      echo "  --skip-apps                 Skip building the app-specific images"
      echo "  --skip-complete             Skip building the complete image"
      echo "  --frappe-version VERSION    Frappe version to use (default: v15)"
      echo "  --erpnext-version VERSION   ERPNext version to use (default: v15)"
      echo "  --help, -h                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Building Frappe Docker images with the following configuration:"
echo "  Version: $VERSION"
echo "  Environment: $ENVIRONMENT"
echo "  Registry URL: $REGISTRY_URL"
echo "  Push to registry: $PUSH"
echo "  Frappe Version: $FRAPPE_VERSION"
echo "  ERPNext Version: $ERPNEXT_VERSION"
echo ""

# Build base image
if [ "$BUILD_BASE" = true ]; then
  echo "Building Frappe base image..."
  docker build -t $REGISTRY_URL/frappe-base:$VERSION ./frappe
  
  if [ "$PUSH" = true ]; then
    echo "Pushing Frappe base image to registry..."
    docker push $REGISTRY_URL/frappe-base:$VERSION
  fi
fi

# Build app-specific images
if [ "$BUILD_APPS" = true ]; then
  # Define the apps to build
  APPS=(
    "cauldron_operations_core:https://github.com/seemslegit42/cauldron_operations_core.git:main"
    "cauldron_synapse:https://github.com/seemslegit42/cauldron_synapse.git:main"
    "cauldron_aegis_protocol:https://github.com/seemslegit42/cauldron_aegis_protocol.git:main"
    "cauldron_lore:https://github.com/seemslegit42/cauldron_lore.git:main"
    "cauldron_command_cauldron:https://github.com/seemslegit42/cauldron_command_cauldron.git:main"
  )
  
  for app_info in "${APPS[@]}"; do
    IFS=':' read -r app_name app_repo app_branch <<< "$app_info"
    
    echo "Building Frappe app image for $app_name..."
    
    # Create temporary Dockerfile for the app
    cat > Dockerfile.app << EOF
FROM $REGISTRY_URL/frappe-base:$VERSION

USER frappe
WORKDIR /home/frappe/frappe-bench

# Get Frappe and ERPNext
RUN bench get-app --branch $FRAPPE_VERSION frappe https://github.com/frappe/frappe.git && \
    bench get-app --branch $ERPNEXT_VERSION erpnext https://github.com/frappe/erpnext.git

# Get the custom app
RUN bench get-app --branch $app_branch $app_name $app_repo

# Set up the app for production if building for prod
RUN if [ "$ENVIRONMENT" = "prod" ]; then \
      bench --site all set-config developer_mode 0; \
      bench build --production; \
    fi

# Copy entrypoint script
COPY --chown=frappe:frappe entrypoint.sh /home/frappe/entrypoint.sh
RUN chmod +x /home/frappe/entrypoint.sh

ENTRYPOINT ["/home/frappe/entrypoint.sh"]
CMD ["bench", "start"]
EOF
    
    # Build the app image
    docker build -t $REGISTRY_URL/frappe-$app_name:$VERSION -f Dockerfile.app ./frappe
    
    if [ "$PUSH" = true ]; then
      echo "Pushing Frappe app image for $app_name to registry..."
      docker push $REGISTRY_URL/frappe-$app_name:$VERSION
    fi
    
    # Clean up
    rm Dockerfile.app
  done
fi

# Build complete image
if [ "$BUILD_COMPLETE" = true ]; then
  echo "Building complete Frappe image..."
  
  # Create temporary Dockerfile for the complete image
  cat > Dockerfile.complete << EOF
FROM $REGISTRY_URL/frappe-base:$VERSION

USER frappe
WORKDIR /home/frappe/frappe-bench

# Get Frappe and ERPNext
RUN bench get-app --branch $FRAPPE_VERSION frappe https://github.com/frappe/frappe.git && \
    bench get-app --branch $ERPNEXT_VERSION erpnext https://github.com/frappe/erpnext.git

# Get all custom apps
RUN bench get-app --branch main cauldron_operations_core https://github.com/seemslegit42/cauldron_operations_core.git && \
    bench get-app --branch main cauldron_synapse https://github.com/seemslegit42/cauldron_synapse.git && \
    bench get-app --branch main cauldron_aegis_protocol https://github.com/seemslegit42/cauldron_aegis_protocol.git && \
    bench get-app --branch main cauldron_lore https://github.com/seemslegit42/cauldron_lore.git && \
    bench get-app --branch main cauldron_command_cauldron https://github.com/seemslegit42/cauldron_command_cauldron.git

# Set up for production if building for prod
RUN if [ "$ENVIRONMENT" = "prod" ]; then \
      bench --site all set-config developer_mode 0; \
      bench build --production; \
    fi

# Copy entrypoint script
COPY --chown=frappe:frappe entrypoint.sh /home/frappe/entrypoint.sh
RUN chmod +x /home/frappe/entrypoint.sh

ENTRYPOINT ["/home/frappe/entrypoint.sh"]
CMD ["bench", "start"]
EOF
  
  # Build the complete image
  docker build -t $REGISTRY_URL/frappe-complete:$VERSION -f Dockerfile.complete ./frappe
  
  if [ "$PUSH" = true ]; then
    echo "Pushing complete Frappe image to registry..."
    docker push $REGISTRY_URL/frappe-complete:$VERSION
  fi
  
  # Clean up
  rm Dockerfile.complete
fi

echo "Frappe Docker image build process completed successfully!"
