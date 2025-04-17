# Cauldron Infrastructure Helm Chart Guide

This guide provides a comprehensive overview of the Helm chart developed for deploying the core infrastructure dependencies of the Cauldron Sentient Enterprise Operating System (sEOS).

## Overview

The Cauldron Infrastructure Helm chart is designed to deploy the following core infrastructure components:

1. **PostgreSQL**: Main relational database for the Cauldron platform
2. **TimescaleDB**: Time-series database for metrics and monitoring
3. **Qdrant**: Vector database for the Lore module (knowledge management)
4. **RabbitMQ**: Message broker for event-driven architecture
5. **Redis**: Multiple Redis instances for caching, queuing, and Socket.IO communication

## Chart Structure

The Helm chart follows a standard structure with the following key files and directories:

```
cauldron-infra/
├── Chart.yaml                  # Chart metadata and dependencies
├── values.yaml                 # Default configuration values
├── values-dev.yaml             # Development environment values
├── values-staging.yaml         # Staging environment values
├── values-prod.yaml            # Production environment values
├── README.md                   # Chart documentation
├── INSTALLATION.md             # Installation guide
├── templates/                  # Kubernetes resource templates
│   ├── _helpers.tpl            # Template helpers
│   ├── configmap.yaml          # ConfigMap for PostgreSQL initialization scripts
│   ├── secret.yaml             # Secret for storing credentials
│   ├── postgres/               # PostgreSQL-specific templates
│   ├── timescaledb/            # TimescaleDB-specific templates
│   ├── qdrant/                 # Qdrant-specific templates
│   ├── rabbitmq/               # RabbitMQ-specific templates
│   └── redis/                  # Redis-specific templates
```

### Key Features

1. **Environment-Specific Configurations**: Separate values files for development, staging, and production environments
2. **Dependency Management**: Uses Bitnami's Helm charts for PostgreSQL, RabbitMQ, and Redis
3. **Resource Management**: Configurable resource requests and limits for all components
4. **Persistence**: Configurable persistent storage for all stateful components
5. **Health Checks**: Liveness and readiness probes for all components
6. **Metrics**: Optional metrics collection for monitoring

## Design Decisions

### 1. Using Bitnami Dependencies

The chart leverages Bitnami's well-maintained Helm charts for PostgreSQL, RabbitMQ, and Redis. This approach provides several benefits:

- **Reliability**: Bitnami charts are widely used and well-tested
- **Feature-Rich**: Includes features like high availability, metrics, and security
- **Maintenance**: Regular updates and security patches

### 2. Custom TimescaleDB and Qdrant Deployments

Since TimescaleDB and Qdrant don't have official Helm charts that meet our requirements, we've created custom deployments for these components:

- **TimescaleDB**: Based on the official TimescaleDB Docker image with PostgreSQL 15
- **Qdrant**: Based on the official Qdrant Docker image with configurable resources

### 3. Multiple Redis Instances

For Frappe/ERPNext integration, we deploy three separate Redis instances:

- **Redis Cache**: For caching frequently accessed data
- **Redis Queue**: For background job processing
- **Redis SocketIO**: For real-time communication

This separation follows Frappe/ERPNext's recommended architecture and allows for independent scaling and configuration of each Redis instance.

### 4. PostgreSQL Initialization

The chart includes a ConfigMap with initialization scripts for PostgreSQL:

- **Extensions**: Enables required PostgreSQL extensions (vector, timescaledb, uuid-ossp, etc.)
- **Schemas**: Creates the necessary schemas for different Cauldron modules
- **Databases**: Creates additional databases for services like AetherCore and SuperAGI

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
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-dev.yaml
```

For detailed installation instructions, refer to the `INSTALLATION.md` file.

### Configuration

The chart can be configured through the values files:

- **values.yaml**: Default configuration values
- **values-dev.yaml**: Development environment values (minimal resources)
- **values-staging.yaml**: Staging environment values (moderate resources)
- **values-prod.yaml**: Production environment values (high availability, more resources)

Key configuration parameters include:

- **Resource Allocation**: CPU and memory requests/limits for each component
- **Storage**: Persistent volume size for each component
- **Replication**: Number of replicas for high availability in production
- **Credentials**: Database and message broker credentials

### Customization

To customize the chart for your specific needs:

1. Create a custom values file based on one of the provided environment files
2. Override specific values as needed
3. Install or upgrade the chart with your custom values file

Example:

```bash
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f my-custom-values.yaml
```

## Integration with Cauldron Components

The infrastructure deployed by this Helm chart is designed to be used by other Cauldron components:

1. **Frappe/ERPNext**: Connects to PostgreSQL and the three Redis instances
2. **SuperAGI**: Connects to PostgreSQL and Qdrant
3. **AetherCore**: Connects to PostgreSQL and RabbitMQ
4. **Manifold UI**: Connects to the backend services

The connection details for each service are exposed through Kubernetes Services, making them accessible within the cluster.

## Scaling Considerations

### Development Environment

The development environment is configured with minimal resources and single instances of each component:

- **PostgreSQL**: Single instance with 256Mi memory
- **TimescaleDB**: Single instance with 256Mi memory
- **Qdrant**: Single instance with 256Mi memory
- **RabbitMQ**: Single instance with 256Mi memory
- **Redis**: Single instances with 32-64Mi memory each

### Production Environment

The production environment is configured for high availability and performance:

- **PostgreSQL**: Primary-replica architecture with 2Gi-4Gi memory per instance
- **TimescaleDB**: Single instance with 2Gi-4Gi memory (can be scaled manually)
- **Qdrant**: Multiple replicas with 2Gi-4Gi memory each
- **RabbitMQ**: Clustered deployment with 3 nodes and 2Gi-4Gi memory each
- **Redis**: Primary-replica architecture with 1Gi-2Gi memory per instance

## Monitoring and Maintenance

### Monitoring

The chart enables metrics for PostgreSQL, RabbitMQ, and Redis, which can be scraped by Prometheus. To view these metrics:

1. Install Prometheus and Grafana in your cluster
2. Configure Prometheus to scrape the metrics endpoints
3. Import the relevant Grafana dashboards for each component

### Backup and Restore

For backup and restore operations:

1. **PostgreSQL**: Use pg_dump and pg_restore
2. **TimescaleDB**: Use TimescaleDB-specific backup tools
3. **Qdrant**: Use Qdrant's backup API
4. **RabbitMQ**: Export and import definitions
5. **Redis**: Use Redis persistence (RDB/AOF)

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

The Cauldron Infrastructure Helm chart provides a solid foundation for deploying the core infrastructure dependencies of the Cauldron Sentient Enterprise Operating System. By leveraging well-established Helm charts and following best practices, it ensures reliability, scalability, and maintainability of the infrastructure components.

For detailed information on each component, refer to the `README.md` file and the official documentation of each component:

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Redis Documentation](https://redis.io/documentation)
