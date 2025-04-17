# Cauldron Frappe Helm Chart Guide

This guide provides a comprehensive overview of the Helm chart developed for deploying the Frappe/ERPNext application with custom Cauldron apps for the Cauldron Sentient Enterprise Operating System (sEOS).

## Overview

The Cauldron Frappe Helm chart is designed to deploy the following components:

1. **Frappe Web Server**: The main web server for Frappe/ERPNext
2. **Frappe Worker**: Background job processing for Frappe/ERPNext
3. **Frappe Scheduler**: Scheduled tasks for Frappe/ERPNext
4. **Frappe Socket.IO**: Real-time communication for Frappe/ERPNext
5. **Custom Cauldron Apps**: Cauldron-specific applications built on Frappe

## Chart Structure

The Helm chart follows a standard structure with the following key files and directories:

```
cauldron-frappe/
├── Chart.yaml                  # Chart metadata and dependencies
├── values.yaml                 # Default configuration values
├── values-dev.yaml             # Development environment values
├── values-staging.yaml         # Staging environment values
├── values-prod.yaml            # Production environment values
├── README.md                   # Chart documentation
├── INSTALLATION.md             # Installation guide
├── templates/                  # Kubernetes resource templates
│   ├── _helpers.tpl            # Template helpers
│   ├── configmap.yaml          # ConfigMap for Frappe configuration
│   ├── secret.yaml             # Secret for storing credentials
│   ├── deployment.yaml         # Web server deployment
│   ├── worker-deployment.yaml  # Worker deployment
│   ├── scheduler-deployment.yaml # Scheduler deployment
│   ├── socketio-deployment.yaml # Socket.IO deployment
│   ├── service.yaml            # Services for web and socketio
│   ├── ingress.yaml            # Ingress for web access
│   └── pvc.yaml                # Persistent volume claim
```

### Key Features

1. **Environment-Specific Configurations**: Separate values files for development, staging, and production environments
2. **Dependency Management**: Uses Bitnami's common Helm chart for helpers
3. **Resource Management**: Configurable resource requests and limits for all components
4. **Persistence**: Configurable persistent storage for Frappe sites
5. **Health Checks**: Liveness and readiness probes for all components
6. **Custom Apps**: Support for installing custom Cauldron apps

## Design Decisions

### 1. Microservices Architecture

The chart deploys Frappe as a set of microservices, with separate deployments for:

- **Web Server**: Handles HTTP requests
- **Worker**: Processes background jobs
- **Scheduler**: Runs scheduled tasks
- **Socket.IO**: Handles real-time communication

This approach allows for independent scaling and management of each component based on workload requirements.

### 2. Shared Persistence

All Frappe components share a single persistent volume for the sites directory. This ensures that all components have access to the same site files, which is required for Frappe to function correctly.

### 3. ConfigMap for Configuration

The chart uses a ConfigMap to store the Frappe configuration, including:

- **common_site_config.json**: Shared configuration for all sites
- **entrypoint.sh**: Script for initializing and starting the web server
- **worker-entrypoint.sh**: Script for starting the worker
- **scheduler-entrypoint.sh**: Script for starting the scheduler
- **socketio-entrypoint.sh**: Script for starting the Socket.IO server

This approach allows for easy configuration management and updates without rebuilding the container images.

### 4. Custom App Installation

The chart supports installing custom Cauldron apps from Git repositories. The apps are defined in the values file and installed during the site initialization process.

### 5. Init Containers for Dependencies

The chart uses init containers to ensure that the required dependencies (PostgreSQL and Redis) are available before starting the Frappe components. This prevents startup failures due to missing dependencies.

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
helm install cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-dev.yaml
```

For detailed installation instructions, refer to the `INSTALLATION.md` file.

### Configuration

The chart can be configured through the values files:

- **values.yaml**: Default configuration values
- **values-dev.yaml**: Development environment values (minimal resources)
- **values-staging.yaml**: Staging environment values (moderate resources)
- **values-prod.yaml**: Production environment values (high availability, more resources)

Key configuration parameters include:

- **Image**: Frappe image repository and tag
- **Site**: Site name and admin password
- **Database**: Database connection details
- **Redis**: Redis connection details
- **Resources**: CPU and memory requests/limits for each component
- **Persistence**: Persistent volume size and access mode
- **Replicas**: Number of replicas for each component
- **Ingress**: Ingress configuration for web access
- **Apps**: Standard and custom apps to install

### Customization

To customize the chart for your specific needs:

1. Create a custom values file based on one of the provided environment files
2. Override specific values as needed
3. Install or upgrade the chart with your custom values file

Example:

```bash
helm install cauldron-frappe ./cauldron-frappe --namespace cauldron -f my-custom-values.yaml
```

## Integration with Cauldron Components

The Frappe application deployed by this Helm chart is designed to integrate with other Cauldron components:

1. **PostgreSQL**: Uses the PostgreSQL database deployed by the Cauldron Infrastructure chart
2. **Redis**: Uses the Redis instances deployed by the Cauldron Infrastructure chart
3. **AetherCore**: Integrates with AetherCore through the custom Cauldron apps
4. **SuperAGI**: Integrates with SuperAGI through the custom Cauldron apps

The integration is configured through the custom Cauldron apps, which provide the necessary connectors and APIs.

## Scaling Considerations

### Development Environment

The development environment is configured with minimal resources and single instances of each component:

- **Web Server**: Single instance with 256Mi memory
- **Worker**: Single instance with 256Mi memory
- **Scheduler**: Single instance with 128Mi memory
- **Socket.IO**: Single instance with 128Mi memory

### Production Environment

The production environment is configured for high availability and performance:

- **Web Server**: Multiple replicas with 2Gi-4Gi memory each
- **Worker**: Multiple replicas with 2Gi-4Gi memory each
- **Scheduler**: Single instance with 1Gi-2Gi memory
- **Socket.IO**: Multiple replicas with 1Gi-2Gi memory each

## Monitoring and Maintenance

### Monitoring

To monitor the Frappe application:

1. Check the status of the pods: `kubectl get pods -n cauldron -l app.kubernetes.io/name=cauldron-frappe`
2. Check the logs of the pods: `kubectl logs -n cauldron <pod-name>`
3. Check the status of the services: `kubectl get services -n cauldron -l app.kubernetes.io/name=cauldron-frappe`
4. Check the status of the ingress: `kubectl get ingress -n cauldron -l app.kubernetes.io/name=cauldron-frappe`

### Backup and Restore

For backup and restore operations:

1. **Database**: Use PostgreSQL backup tools (pg_dump/pg_restore)
2. **Files**: Backup the persistent volume data
3. **Configuration**: Backup the ConfigMap and Secret

Detailed backup and restore procedures should be documented in your organization's operational runbooks.

## Security Considerations

The chart implements several security measures:

1. **Secrets**: Credentials are stored in Kubernetes Secrets
2. **Network Policies**: Can be added to restrict communication between components
3. **Resource Limits**: Prevents resource exhaustion
4. **Health Checks**: Ensures components are functioning properly

For production deployments, consider implementing additional security measures:

1. **TLS**: Enable TLS for all communications
2. **Authentication**: Configure strong authentication for all components
3. **Authorization**: Implement fine-grained access control
4. **Audit Logging**: Enable audit logging for all components

## Conclusion

The Cauldron Frappe Helm chart provides a solid foundation for deploying the Frappe/ERPNext application with custom Cauldron apps for the Cauldron Sentient Enterprise Operating System. By leveraging Kubernetes and Helm, it ensures reliability, scalability, and maintainability of the Frappe application.

For detailed information on the Frappe application and custom Cauldron apps, refer to the respective documentation:

- [Frappe Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com/)
- [Cauldron Documentation](https://github.com/seemslegit42/cauldron/docs)
