# Cauldron Nextcloud Installation Guide

This guide provides step-by-step instructions for installing the Cauldron Nextcloud Helm chart in different environments.

## Prerequisites

Before installing the Cauldron Nextcloud Helm chart, ensure you have the following:

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

Before installing the Nextcloud chart, you need to install the Cauldron Infrastructure chart:

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
helm install cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-dev.yaml

# For staging environment
helm install cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-staging.yaml

# For production environment
helm install cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-prod.yaml
```

### Step 6: Verify the Installation

```bash
# Check the status of the Helm release
helm status cauldron-nextcloud -n cauldron

# Check the deployed pods
kubectl get pods -n cauldron -l app.kubernetes.io/name=cauldron-nextcloud

# Check the deployed services
kubectl get services -n cauldron -l app.kubernetes.io/name=cauldron-nextcloud

# Check the deployed ingress
kubectl get ingress -n cauldron -l app.kubernetes.io/name=cauldron-nextcloud
```

### Step 7: Access the Nextcloud Application

Once the installation is complete, you can access the Nextcloud application using the configured ingress:

- Development: http://nextcloud.cauldron.local
- Staging: https://nextcloud-staging.cauldron.ai
- Production: https://nextcloud.cauldron.ai

## Customizing the Installation

### Resource Allocation

To adjust resource allocation for Nextcloud, modify the `nextcloud.resources` section in your values file:

```yaml
nextcloud:
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"
```

### PHP Configuration

To adjust PHP configuration for Nextcloud, modify the `nextcloud.php` section in your values file:

```yaml
nextcloud:
  php:
    memoryLimit: "512M"
    uploadMaxFilesize: "1G"
    postMaxSize: "1G"
    maxExecutionTime: "300"
    maxInputTime: "300"
```

### Trusted Domains

To configure trusted domains for Nextcloud, modify the `nextcloud.trustedDomains` section in your values file:

```yaml
nextcloud:
  trustedDomains:
    - "nextcloud.cauldron.local"
    - "localhost"
    - "nextcloud.example.com"
```

## Upgrading the Chart

To upgrade the chart:

```bash
# For development environment
helm upgrade cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-dev.yaml

# For staging environment
helm upgrade cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-staging.yaml

# For production environment
helm upgrade cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-prod.yaml
```

## Uninstalling the Chart

To uninstall the chart:

```bash
helm uninstall cauldron-nextcloud --namespace cauldron
```

Note: This will not delete the persistent volume claims. To delete them:

```bash
kubectl delete pvc -n cauldron -l app.kubernetes.io/name=cauldron-nextcloud
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**:
   - Check if PVCs are being provisioned: `kubectl get pvc -n cauldron`
   - Check if there are enough resources in the cluster: `kubectl describe pod <pod-name> -n cauldron`

2. **Database connection issues**:
   - Check if the database pods are running: `kubectl get pods -n cauldron -l app=postgres`
   - Check the database logs: `kubectl logs -n cauldron <postgres-pod-name>`
   - Verify the database connection settings in the Nextcloud pod: `kubectl exec -it -n cauldron <nextcloud-pod-name> -- cat /var/www/html/config/config.php`

3. **Redis connection issues**:
   - Check if the Redis pods are running: `kubectl get pods -n cauldron -l app=redis`
   - Check the Redis logs: `kubectl logs -n cauldron <redis-pod-name>`
   - Verify the Redis connection settings in the Nextcloud pod: `kubectl exec -it -n cauldron <nextcloud-pod-name> -- cat /var/www/html/config/config.php`

4. **Ingress issues**:
   - Check if the ingress is properly configured: `kubectl get ingress -n cauldron`
   - Check if the ingress controller is running: `kubectl get pods -n <ingress-controller-namespace>`
   - Verify the ingress rules: `kubectl describe ingress -n cauldron <ingress-name>`

### Getting Support

If you encounter any issues that you cannot resolve, please:

1. Check the [Cauldron documentation](https://github.com/seemslegit42/cauldron/docs)
2. Open an issue on the [Cauldron GitHub repository](https://github.com/seemslegit42/cauldron/issues)

## Next Steps

After installing the Cauldron Nextcloud chart, you can proceed to:

1. Configure Nextcloud for your specific needs
2. Install additional Nextcloud apps
3. Set up user accounts and groups
4. Configure external storage providers
5. Set up integration with other Cauldron components
