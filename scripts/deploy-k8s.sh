#!/bin/bash
# deploy-k8s.sh - Script to deploy Cauldron to Kubernetes

set -e

# Default values
ENVIRONMENT="dev"
REGISTRY_URL="your-registry-url"
VERSION="latest"
SKIP_BUILD=false
SKIP_PUSH=false

# Display help
function show_help {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to deploy to (dev, staging, prod) [default: dev]"
    echo "  -r, --registry URL       Container registry URL [default: your-registry-url]"
    echo "  -v, --version VERSION    Version tag for images [default: latest]"
    echo "  --skip-build             Skip building images"
    echo "  --skip-push              Skip pushing images to registry"
    echo "  -h, --help               Show this help message"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -e|--environment)
            ENVIRONMENT="$2"
            shift
            shift
            ;;
        -r|--registry)
            REGISTRY_URL="$2"
            shift
            shift
            ;;
        -v|--version)
            VERSION="$2"
            shift
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-push)
            SKIP_PUSH=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "prod" ]]; then
    echo "Error: Environment must be one of: dev, staging, prod"
    exit 1
fi

# Set namespace based on environment
NAMESPACE="cauldron-$ENVIRONMENT"

echo "Deploying Cauldron to Kubernetes..."
echo "Environment: $ENVIRONMENT"
echo "Registry: $REGISTRY_URL"
echo "Version: $VERSION"
echo "Namespace: $NAMESPACE"

# Build Docker images if not skipped
if [ "$SKIP_BUILD" = false ]; then
    echo "Building Docker images..."
    
    echo "Building AetherCore image..."
    docker build -t $REGISTRY_URL/aethercore:$VERSION ./aether_core
    
    echo "Building Manifold UI image..."
    docker build -t $REGISTRY_URL/manifold-ui:$VERSION ./manifold
    
    echo "Images built successfully."
fi

# Push Docker images to registry if not skipped
if [ "$SKIP_PUSH" = false ]; then
    echo "Pushing Docker images to registry..."
    
    docker push $REGISTRY_URL/aethercore:$VERSION
    docker push $REGISTRY_URL/manifold-ui:$VERSION
    
    echo "Images pushed successfully."
fi

# Create namespace if it doesn't exist
kubectl get namespace $NAMESPACE > /dev/null 2>&1 || kubectl create namespace $NAMESPACE

# Set image versions in kustomization
echo "Configuring Kustomize with image versions..."
cd infra/k8s/overlays/$ENVIRONMENT

# Create a temporary kustomization file with image replacements
cat > kustomization-temp.yaml << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namespace: $NAMESPACE

commonLabels:
  environment: $ENVIRONMENT

patches:
  - path: patches/ingress-patch.yaml
EOF

# Add replicas patch if it exists
if [ -f "patches/replicas-patch.yaml" ]; then
    echo "  - path: patches/replicas-patch.yaml" >> kustomization-temp.yaml
fi

# Add resources patch if it exists
if [ -f "patches/resources-patch.yaml" ]; then
    echo "  - path: patches/resources-patch.yaml" >> kustomization-temp.yaml
fi

# Add HPA patch if it exists
if [ -f "patches/hpa-patch.yaml" ]; then
    echo "  - path: patches/hpa-patch.yaml" >> kustomization-temp.yaml
fi

# Add config map generator
cat >> kustomization-temp.yaml << EOF

configMapGenerator:
  - name: cauldron-$ENVIRONMENT-config
    literals:
      - ENVIRONMENT=$ENVIRONMENT

secretGenerator:
  - name: cauldron-secrets
    behavior: replace
    envs:
      - secrets.env

images:
  - name: \${REGISTRY_URL}/aethercore:\${VERSION}
    newName: $REGISTRY_URL/aethercore
    newTag: $VERSION
  - name: \${REGISTRY_URL}/manifold-ui:\${VERSION}
    newName: $REGISTRY_URL/manifold-ui
    newTag: $VERSION
EOF

# Replace the original kustomization file
mv kustomization-temp.yaml kustomization.yaml

# Apply the Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -k .

echo "Deployment completed successfully!"
echo "To check the status of your deployment, run:"
echo "  kubectl get all -n $NAMESPACE"

cd - > /dev/null
