# Cauldron Nextcloud Helm Chart Guide

This guide provides a comprehensive overview of the Helm chart developed for deploying Nextcloud as a document store and knowledge base for the Cauldron Sentient Enterprise Operating System (sEOS).

## Overview

The Cauldron Nextcloud Helm chart is designed to deploy the following components:

1. **Nextcloud Server**: The main Nextcloud application for file storage, sharing, and collaboration
2. **Cron Job**: For scheduled tasks in Nextcloud

## Chart Structure

The Helm chart follows a standard structure with the following key files and directories:

```
cauldron-nextcloud/
├── Chart.yaml                  # Chart metadata and dependencies
├── values.yaml                 # Default configuration values
├── values-dev.yaml             # Development environment values
├── values-staging.yaml         # Staging environment values
├── values-prod.yaml            # Production environment values
├── README.md                   # Chart documentation
├── INSTALLATION.md             # Installation guide
├── templates/                  # Kubernetes resource templates
│   ├── _helpers.tpl            # Template helpers
│   ├── configmap.yaml          # ConfigMap for Nextcloud configuration
│   ├── secret.yaml             # Secret for storing credentials
│   ├── deployment.yaml         # Nextcloud deployment
│   ├── service.yaml            # Service for Nextcloud
│   ├── ingress.yaml            # Ingress for web access
│   ├── pvc.yaml                # Persistent volume claim
│   └── cronjob.yaml            # Cron job for scheduled tasks
```

### Key Features

1. **Environment-Specific Configurations**: Separate values files for development, staging, and production environments
2. **Dependency Management**: Uses Bitnami's common Helm chart for helpers
3. **Resource Management**: Configurable resource requests and limits
4. **Persistence**: Configurable persistent storage for Nextcloud data
5. **Health Checks**: Liveness and readiness probes
6. **Custom Configuration**: Support for custom PHP and Nextcloud configuration

## Design Decisions

### 1. Using Official Nextcloud Image

The chart uses the official Nextcloud Docker image, which provides a stable and well-maintained base for the deployment. This approach ensures compatibility with the latest Nextcloud releases and security updates.

### 2. Custom Entrypoint Script

The chart includes a custom entrypoint script that handles:

- Waiting for dependencies (PostgreSQL and Redis)
- Creating the database if it doesn't exist
- Installing Nextcloud if not already installed
- Configuring trusted domains
- Setting up Redis for caching and locking
- Configuring PHP settings
- Setting up other Nextcloud configuration options

This approach allows for a more flexible and customizable deployment compared to using the default entrypoint script.

### 3. PostgreSQL Integration

The chart is designed to work with the PostgreSQL database deployed by the Cauldron Infrastructure chart. It supports:

- Automatic database creation
- Configurable database connection settings
- Waiting for the database to be ready before starting Nextcloud

### 4. Redis Integration

The chart supports using Redis for caching and locking, which improves Nextcloud performance, especially in multi-pod deployments. It includes:

- Configurable Redis connection settings
- Automatic Redis configuration in Nextcloud
- Waiting for Redis to be ready before starting Nextcloud

### 5. Cron Job

The chart includes a Kubernetes CronJob for running Nextcloud's background tasks. This ensures that:

- Background tasks run regularly
- Tasks are executed even if the main Nextcloud pod is restarted
- Resource usage is optimized by running tasks on a schedule

## Usage

### Installation

To install the chart:

```bash
# Add required Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create namespace
kubectl create namespace cauldron

# Install the chart
helm install cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-dev.yaml
```

For detailed installation instructions, refer to the `INSTALLATION.md` file.

### Configuration

The chart can be configured through the values files:

- **values.yaml**: Default configuration values
- **values-dev.yaml**: Development environment values (minimal resources)
- **values-staging.yaml**: Staging environment values (moderate resources)
- **values-prod.yaml**: Production environment values (high availability, more resources)

Key configuration parameters include:

- **Image**: Nextcloud image repository and tag
- **Admin**: Admin username and password
- **Database**: Database connection details
- **Redis**: Redis connection details
- **Resources**: CPU and memory requests/limits
- **Persistence**: Persistent volume size and access mode
- **Ingress**: Ingress configuration for web access
- **PHP**: PHP configuration settings

### Customization

To customize the chart for your specific needs:

1. Create a custom values file based on one of the provided environment files
2. Override specific values as needed
3. Install or upgrade the chart with your custom values file

Example:

```bash
helm install cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f my-custom-values.yaml
```

## Integration with Cauldron Components

Nextcloud deployed by this Helm chart is designed to integrate with other Cauldron components:

1. **PostgreSQL**: Uses the PostgreSQL database deployed by the Cauldron Infrastructure chart
2. **Redis**: Uses the Redis instance deployed by the Cauldron Infrastructure chart
3. **Lore Module**: Integrates with the Lore module for knowledge management
4. **AetherCore**: Integrates with AetherCore for agent-based operations on documents

The integration is facilitated through Nextcloud's API and WebDAV interface, which allows other components to access and manipulate files stored in Nextcloud.

## Scaling Considerations

### Development Environment

The development environment is configured with minimal resources:

- **Nextcloud**: Single instance with 256Mi memory
- **Persistence**: 5Gi storage
- **PHP**: Minimal memory limits

### Production Environment

The production environment is configured for high availability and performance:

- **Nextcloud**: Multiple replicas with 2Gi-4Gi memory each
- **Persistence**: 50Gi storage
- **PHP**: Higher memory limits and execution times
- **TLS**: Enabled with proper certificates

## Monitoring and Maintenance

### Monitoring

To monitor the Nextcloud deployment:

1. Check the status of the pods: `kubectl get pods -n cauldron -l app.kubernetes.io/name=cauldron-nextcloud`
2. Check the logs of the pods: `kubectl logs -n cauldron <pod-name>`
3. Check the status of the services: `kubectl get services -n cauldron -l app.kubernetes.io/name=cauldron-nextcloud`
4. Check the status of the ingress: `kubectl get ingress -n cauldron -l app.kubernetes.io/name=cauldron-nextcloud`

### Backup and Restore

For backup and restore operations:

1. **Database**: Use PostgreSQL backup tools (pg_dump/pg_restore)
2. **Files**: Backup the persistent volume data
3. **Configuration**: Backup the Nextcloud configuration

Detailed backup and restore procedures should be documented in your organization's operational runbooks.

## Security Considerations

The chart implements several security measures:

1. **Secrets**: Credentials are stored in Kubernetes Secrets
2. **TLS**: Support for TLS encryption via Ingress
3. **Resource Limits**: Prevents resource exhaustion
4. **Health Checks**: Ensures the application is functioning properly

For production deployments, consider implementing additional security measures:

1. **Network Policies**: Restrict communication between components
2. **Pod Security Policies**: Enforce security best practices for pods
3. **Secure Ingress**: Use proper TLS certificates and security headers
4. **Regular Updates**: Keep Nextcloud and its dependencies up to date

## Conclusion

The Cauldron Nextcloud Helm chart provides a solid foundation for deploying Nextcloud as a document store and knowledge base for the Cauldron Sentient Enterprise Operating System. By leveraging Kubernetes and Helm, it ensures reliability, scalability, and maintainability of the Nextcloud deployment.

For detailed information on Nextcloud, refer to the [Nextcloud documentation](https://docs.nextcloud.com/).
