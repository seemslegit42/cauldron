# Cauldron Manifold UI Installation Guide

This guide provides step-by-step instructions for installing the Cauldron Manifold UI Helm chart in different environments.

## Prerequisites

Before installing the Cauldron Manifold UI Helm chart, ensure you have the following:

- Kubernetes cluster (version 1.19+)
- Helm (version 3.2.0+)
- `kubectl` configured to communicate with your Kubernetes cluster
- Sufficient permissions to create resources in your Kubernetes cluster
- Cauldron Infrastructure Helm chart installed (for PostgreSQL, Redis, etc.)
- Cauldron AetherCore Helm chart installed (for API backend)

## Installation Steps

### Step 1: Add Required Helm Repositories

```bash
# Add Bitnami repository for common chart
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Step 2: Create a Namespace

```bash
kubectl create namespace cauldron
```

### Step 3: Install the Cauldron Infrastructure Chart

Before installing the Manifold UI chart, you need to install the Cauldron Infrastructure chart:

```bash
# For development environment
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-dev.yaml
```

### Step 4: Install the Cauldron AetherCore Chart

Before installing the Manifold UI chart, you need to install the Cauldron AetherCore chart:

```bash
# For development environment
helm install cauldron-aethercore ./cauldron-aethercore --namespace cauldron -f cauldron-aethercore/values-dev.yaml
```

### Step 5: Prepare Values File

Choose the appropriate values file based on your environment:

- Development: `values-dev.yaml`
- Staging: `values-staging.yaml`
- Production: `values-prod.yaml`

You may need to customize these files based on your specific requirements.

### Step 6: Install the Chart

```bash
# For development environment
helm install cauldron-manifold ./cauldron-manifold --namespace cauldron -f cauldron-manifold/values-dev.yaml

# For staging environment
helm install cauldron-manifold ./cauldron-manifold --namespace cauldron -f cauldron-manifold/values-staging.yaml

# For production environment
helm install cauldron-manifold ./cauldron-manifold --namespace cauldron -f cauldron-manifold/values-prod.yaml
```

### Step 7: Verify the Installation

```bash
# Check the status of the Helm release
helm status cauldron-manifold -n cauldron

# Check the deployed pods
kubectl get pods -n cauldron -l app.kubernetes.io/name=cauldron-manifold

# Check the deployed services
kubectl get services -n cauldron -l app.kubernetes.io/name=cauldron-manifold

# Check the deployed ingress
kubectl get ingress -n cauldron -l app.kubernetes.io/name=cauldron-manifold
```

### Step 8: Access the Manifold UI

Once the installation is complete, you can access the Manifold UI using the configured ingress:

- Development: http://cauldron.local
- Staging: https://staging.cauldron.ai
- Production: https://cauldron.ai

## Customizing the Installation

### Resource Allocation

To adjust resource allocation for Manifold UI, modify the `manifold.resources` section in your values file:

```yaml
manifold:
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "400m"
```

### Scaling

To adjust the number of replicas for Manifold UI, modify the `manifold.replicas` section in your values file:

```yaml
manifold:
  replicas: 3
```

Alternatively, you can enable autoscaling:

```yaml
manifold:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70
```

### API URL

To adjust the API URL for Manifold UI, modify the `manifold.api.url` section in your values file:

```yaml
manifold:
  api:
    url: "/api/v1"
```

## Upgrading the Chart

To upgrade the chart:

```bash
# For development environment
helm upgrade cauldron-manifold ./cauldron-manifold --namespace cauldron -f cauldron-manifold/values-dev.yaml

# For staging environment
helm upgrade cauldron-manifold ./cauldron-manifold --namespace cauldron -f cauldron-manifold/values-staging.yaml

# For production environment
helm upgrade cauldron-manifold ./cauldron-manifold --namespace cauldron -f cauldron-manifold/values-prod.yaml
```

## Uninstalling the Chart

To uninstall the chart:

```bash
helm uninstall cauldron-manifold --namespace cauldron
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**:
   - Check if there are enough resources in the cluster: `kubectl describe pod <pod-name> -n cauldron`

2. **API connection issues**:
   - Check if the AetherCore API is running: `kubectl get pods -n cauldron -l app=aethercore`
   - Check the Manifold UI logs: `kubectl logs -n cauldron <manifold-pod-name>`
   - Verify the API URL configuration: `kubectl get configmap -n cauldron <manifold-configmap-name> -o yaml`

3. **Ingress issues**:
   - Check if the ingress controller is running: `kubectl get pods -n <ingress-controller-namespace>`
   - Check the ingress configuration: `kubectl get ingress -n cauldron <manifold-ingress-name> -o yaml`
   - Verify the DNS resolution for the ingress host

### Getting Support

If you encounter any issues that you cannot resolve, please:

1. Check the [Cauldron documentation](https://github.com/seemslegit42/cauldron/docs)
2. Open an issue on the [Cauldron GitHub repository](https://github.com/seemslegit42/cauldron/issues)

## Next Steps

After installing the Cauldron Manifold UI chart, you can proceed to:

1. Configure the Manifold UI for your specific needs
2. Set up user authentication and authorization
3. Integrate with other Cauldron components
4. Develop custom dashboards and visualizations
