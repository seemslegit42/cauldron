# Cauldron Frappe Installation Guide

This guide provides step-by-step instructions for installing the Cauldron Frappe Helm chart in different environments.

## Prerequisites

Before installing the Cauldron Frappe Helm chart, ensure you have the following:

- Kubernetes cluster (version 1.19+)
- Helm (version 3.2.0+)
- `kubectl` configured to communicate with your Kubernetes cluster
- Sufficient permissions to create resources in your Kubernetes cluster
- Cauldron Infrastructure Helm chart installed (for PostgreSQL, Redis, etc.)

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

Before installing the Frappe chart, you need to install the Cauldron Infrastructure chart:

```bash
# For development environment
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-dev.yaml
```

### Step 4: Prepare Values File

Choose the appropriate values file based on your environment:

- Development: `values-dev.yaml`
- Staging: `values-staging.yaml`
- Production: `values-prod.yaml`

You may need to customize these files based on your specific requirements.

### Step 5: Install the Chart

```bash
# For development environment
helm install cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-dev.yaml

# For staging environment
helm install cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-staging.yaml

# For production environment
helm install cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-prod.yaml
```

### Step 6: Verify the Installation

```bash
# Check the status of the Helm release
helm status cauldron-frappe -n cauldron

# Check the deployed pods
kubectl get pods -n cauldron -l app.kubernetes.io/name=cauldron-frappe

# Check the deployed services
kubectl get services -n cauldron -l app.kubernetes.io/name=cauldron-frappe

# Check the deployed ingress
kubectl get ingress -n cauldron -l app.kubernetes.io/name=cauldron-frappe
```

### Step 7: Access the Frappe Application

Once the installation is complete, you can access the Frappe application using the configured ingress:

- Development: http://cauldron.local
- Staging: https://staging.cauldron.ai
- Production: https://cauldron.ai

## Customizing the Installation

### Custom Apps

To add or modify custom Cauldron apps, edit the `frappe.customApps` section in your values file:

```yaml
frappe:
  customApps:
    - name: "cauldron_operations_core"
      repo: "https://github.com/seemslegit42/cauldron_operations_core.git"
      branch: "main"
    - name: "cauldron_synapse"
      repo: "https://github.com/seemslegit42/cauldron_synapse.git"
      branch: "main"
    # Add more custom apps as needed
```

### Resource Allocation

To adjust resource allocation for Frappe components, modify the `frappe.resources` section in your values file:

```yaml
frappe:
  resources:
    web:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
    # Adjust other components as needed
```

### Scaling

To scale the Frappe components, modify the `frappe.replicas` section in your values file:

```yaml
frappe:
  replicas:
    web: 3
    worker: 3
    scheduler: 1
    socketio: 3
```

## Upgrading the Chart

To upgrade the chart:

```bash
# For development environment
helm upgrade cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-dev.yaml

# For staging environment
helm upgrade cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-staging.yaml

# For production environment
helm upgrade cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-prod.yaml
```

## Uninstalling the Chart

To uninstall the chart:

```bash
helm uninstall cauldron-frappe --namespace cauldron
```

Note: This will not delete the persistent volume claims. To delete them:

```bash
kubectl delete pvc -n cauldron -l app.kubernetes.io/name=cauldron-frappe
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**:
   - Check if PVCs are being provisioned: `kubectl get pvc -n cauldron`
   - Check if there are enough resources in the cluster: `kubectl describe pod <pod-name> -n cauldron`

2. **Database connection issues**:
   - Check if the database pods are running: `kubectl get pods -n cauldron -l app=postgres`
   - Check the database logs: `kubectl logs -n cauldron <postgres-pod-name>`
   - Verify the database connection settings in the Frappe configmap: `kubectl get configmap -n cauldron cauldron-frappe-config -o yaml`

3. **Redis connection issues**:
   - Check if the Redis pods are running: `kubectl get pods -n cauldron -l app=redis-cache`
   - Check the Redis logs: `kubectl logs -n cauldron <redis-pod-name>`
   - Verify the Redis connection settings in the Frappe configmap: `kubectl get configmap -n cauldron cauldron-frappe-config -o yaml`

4. **Custom app installation issues**:
   - Check the Frappe web pod logs: `kubectl logs -n cauldron <frappe-web-pod-name>`
   - Verify the custom app repository and branch settings in the values file

### Getting Support

If you encounter any issues that you cannot resolve, please:

1. Check the [Cauldron documentation](https://github.com/seemslegit42/cauldron/docs)
2. Open an issue on the [Cauldron GitHub repository](https://github.com/seemslegit42/cauldron/issues)

## Next Steps

After installing the Cauldron Frappe chart, you can proceed to:

1. Configure the Frappe application for your specific needs
2. Set up integrations with other Cauldron components
3. Develop and deploy custom Cauldron apps
