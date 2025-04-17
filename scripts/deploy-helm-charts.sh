#!/bin/bash
# deploy-helm-charts.sh - Script to deploy Cauldron Helm charts

set -e

# Default values
ENVIRONMENT="dev"
NAMESPACE="cauldron-dev"
VERSION="latest"
CHARTS=""
DRY_RUN=false
INFRA_ONLY=false
APPS_ONLY=false
SKIP_VALIDATION=false
TIMEOUT="10m"

# Available charts
INFRA_CHARTS="cauldron-infra"
APP_CHARTS="cauldron-frappe cauldron-superagi cauldron-n8n cauldron-nextcloud cauldron-manifold"
ALL_CHARTS="$INFRA_CHARTS $APP_CHARTS"

# Display help
function show_help {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to deploy to (dev, staging, prod) [default: dev]"
    echo "  -n, --namespace NS       Kubernetes namespace [default: cauldron-{environment}]"
    echo "  -v, --version VERSION    Version tag for deployment [default: latest]"
    echo "  -c, --charts CHARTS      Comma-separated list of charts to deploy [default: all]"
    echo "  --infra-only             Deploy only infrastructure charts"
    echo "  --apps-only              Deploy only application charts"
    echo "  --dry-run                Perform a dry run (no actual deployment)"
    echo "  --skip-validation        Skip Helm chart validation"
    echo "  --timeout DURATION       Timeout for Helm operations [default: 10m]"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Available charts:"
    echo "  Infrastructure: $INFRA_CHARTS"
    echo "  Applications:  $APP_CHARTS"
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
    -n|--namespace)
      NAMESPACE="$2"
      shift
      shift
      ;;
    -v|--version)
      VERSION="$2"
      shift
      shift
      ;;
    -c|--charts)
      CHARTS="$2"
      shift
      shift
      ;;
    --infra-only)
      INFRA_ONLY=true
      shift
      ;;
    --apps-only)
      APPS_ONLY=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-validation)
      SKIP_VALIDATION=true
      shift
      ;;
    --timeout)
      TIMEOUT="$2"
      shift
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

# Set namespace based on environment if not explicitly provided
if [ "$NAMESPACE" = "cauldron-dev" ] && [ "$ENVIRONMENT" != "dev" ]; then
  NAMESPACE="cauldron-$ENVIRONMENT"
fi

# Determine which charts to deploy
if [ "$INFRA_ONLY" = true ] && [ "$APPS_ONLY" = true ]; then
  echo "Error: Cannot specify both --infra-only and --apps-only"
  exit 1
elif [ "$INFRA_ONLY" = true ]; then
  DEPLOY_CHARTS="$INFRA_CHARTS"
elif [ "$APPS_ONLY" = true ]; then
  DEPLOY_CHARTS="$APP_CHARTS"
elif [ -n "$CHARTS" ]; then
  DEPLOY_CHARTS=$(echo "$CHARTS" | tr ',' ' ')
else
  DEPLOY_CHARTS="$ALL_CHARTS"
fi

echo "Deploying Cauldron Helm charts..."
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "Version: $VERSION"
echo "Charts to deploy: $DEPLOY_CHARTS"
echo "Dry run: $DRY_RUN"
echo ""

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
  echo "Error: Helm is not installed"
  exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
  echo "Error: kubectl is not installed"
  exit 1
fi

# Add Helm repositories
echo "Adding Helm repositories..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create namespace if it doesn't exist
echo "Creating namespace $NAMESPACE if it doesn't exist..."
kubectl get namespace $NAMESPACE > /dev/null 2>&1 || kubectl create namespace $NAMESPACE

# Validate Helm charts
if [ "$SKIP_VALIDATION" = false ]; then
  echo "Validating Helm charts..."
  for CHART in $DEPLOY_CHARTS; do
    if [ -d "$CHART" ]; then
      echo "Linting chart: $CHART"
      helm lint $CHART
      
      echo "Validating chart: $CHART"
      helm template $CHART --namespace $NAMESPACE > /tmp/rendered-$CHART.yaml
      if [ $? -ne 0 ]; then
        echo "Error: Helm template rendering failed for $CHART"
        exit 1
      fi
    else
      echo "Warning: Chart directory $CHART not found, skipping"
    fi
  done
  echo "Helm chart validation successful"
fi

# Deploy infrastructure charts first
if [[ "$DEPLOY_CHARTS" == *"cauldron-infra"* ]]; then
  echo "Deploying infrastructure chart..."
  VALUES_FILE="cauldron-infra/values-$ENVIRONMENT.yaml"
  
  if [ ! -f "$VALUES_FILE" ]; then
    echo "Warning: Values file $VALUES_FILE not found, using default values"
    VALUES_FILE="cauldron-infra/values.yaml"
  fi
  
  HELM_ARGS="--namespace $NAMESPACE -f $VALUES_FILE --set global.environment=$ENVIRONMENT --set global.version=$VERSION --timeout $TIMEOUT"
  
  if [ "$DRY_RUN" = true ]; then
    echo "Performing dry run for cauldron-infra..."
    helm upgrade --install cauldron-infra cauldron-infra $HELM_ARGS --debug --dry-run
  else
    echo "Deploying cauldron-infra..."
    helm upgrade --install cauldron-infra cauldron-infra $HELM_ARGS --wait
    
    echo "Waiting for infrastructure to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cauldron-infra -n $NAMESPACE --timeout=300s
  fi
  
  # Remove cauldron-infra from the list of charts to deploy
  DEPLOY_CHARTS=$(echo "$DEPLOY_CHARTS" | sed 's/cauldron-infra//')
fi

# Deploy application charts in the correct order
if [ -n "$DEPLOY_CHARTS" ]; then
  echo "Deploying application charts..."
  
  # Define the deployment order
  declare -A DEPLOY_ORDER
  DEPLOY_ORDER["cauldron-frappe"]=1
  DEPLOY_ORDER["cauldron-superagi"]=2
  DEPLOY_ORDER["cauldron-n8n"]=3
  DEPLOY_ORDER["cauldron-nextcloud"]=4
  DEPLOY_ORDER["cauldron-manifold"]=5
  
  # Create an array of charts to deploy
  CHART_ARRAY=($DEPLOY_CHARTS)
  
  # Sort charts by deployment order
  SORTED_CHARTS=()
  for CHART in "${CHART_ARRAY[@]}"; do
    if [ -d "$CHART" ]; then
      SORTED_CHARTS+=("$CHART:${DEPLOY_ORDER[$CHART]:-999}")
    fi
  done
  
  # Sort the array based on deployment order
  IFS=$'\n' SORTED_CHARTS=($(sort -t: -k2 -n <<<"${SORTED_CHARTS[*]}"))
  unset IFS
  
  # Deploy each chart
  for CHART_ENTRY in "${SORTED_CHARTS[@]}"; do
    CHART=$(echo $CHART_ENTRY | cut -d: -f1)
    RELEASE_NAME=$(basename $CHART)
    VALUES_FILE="$CHART/values-$ENVIRONMENT.yaml"
    
    if [ ! -f "$VALUES_FILE" ]; then
      echo "Warning: Values file $VALUES_FILE not found, using default values"
      VALUES_FILE="$CHART/values.yaml"
    fi
    
    echo "Deploying chart: $CHART as $RELEASE_NAME"
    
    HELM_ARGS="--namespace $NAMESPACE -f $VALUES_FILE --set global.environment=$ENVIRONMENT --set global.version=$VERSION --timeout $TIMEOUT"
    
    if [ "$DRY_RUN" = true ]; then
      echo "Performing dry run for $RELEASE_NAME..."
      helm upgrade --install $RELEASE_NAME $CHART $HELM_ARGS --debug --dry-run
    else
      echo "Deploying $RELEASE_NAME..."
      helm upgrade --install $RELEASE_NAME $CHART $HELM_ARGS --wait
      
      echo "Waiting for $RELEASE_NAME deployment to be ready..."
      kubectl rollout status deployment -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE --timeout=300s
    fi
  done
fi

if [ "$DRY_RUN" = false ]; then
  echo "Checking deployment status..."
  kubectl get all -n $NAMESPACE
  
  echo "Deployment completed successfully!"
else
  echo "Dry run completed successfully!"
fi
