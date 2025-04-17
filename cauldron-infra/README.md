# Cauldron Infrastructure Helm Chart

This Helm chart deploys the core infrastructure dependencies for the Cauldron Sentient Enterprise Operating System (sEOS).

## Overview

The Cauldron Infrastructure Helm chart deploys the following components:

- **PostgreSQL**: Main relational database
- **TimescaleDB**: Time-series database for metrics and monitoring
- **Qdrant**: Vector database for the Lore module
- **RabbitMQ**: Message broker for event-driven architecture
- **Redis**: Multiple Redis instances for caching, queuing, and Socket.IO

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (for persistent volumes)

## Installing the Chart

### Add the Helm repository

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Install the chart

```bash
# Create a namespace for Cauldron
kubectl create namespace cauldron

# Install the chart with the release name "cauldron-infra"
helm install cauldron-infra ./cauldron-infra --namespace cauldron
```

For development environments:

```bash
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-dev.yaml
```

## Configuration

The following table lists the configurable parameters of the Cauldron Infrastructure chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name (dev, staging, prod) | `dev` |
| `global.storageClass` | Storage class for persistent volumes | `""` |
| `global.imagePullPolicy` | Image pull policy | `IfNotPresent` |
| `global.labels` | Common labels to apply to all resources | `{}` |

### PostgreSQL Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable PostgreSQL | `true` |
| `postgresql.auth.username` | PostgreSQL username | `postgres` |
| `postgresql.auth.password` | PostgreSQL password | `please_change_in_env` |
| `postgresql.auth.database` | PostgreSQL database name | `postgres` |
| `postgresql.primary.persistence.size` | PostgreSQL PVC size | `10Gi` |
| `postgresql.primary.resources` | PostgreSQL resource requests/limits | See `values.yaml` |

### TimescaleDB Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `timescaledb.enabled` | Enable TimescaleDB | `true` |
| `timescaledb.image.repository` | TimescaleDB image repository | `timescale/timescaledb` |
| `timescaledb.image.tag` | TimescaleDB image tag | `latest-pg15` |
| `timescaledb.auth.username` | TimescaleDB username | `postgres` |
| `timescaledb.auth.password` | TimescaleDB password | `please_change_in_env` |
| `timescaledb.auth.database` | TimescaleDB database name | `timeseries` |
| `timescaledb.persistence.enabled` | Enable persistence for TimescaleDB | `true` |
| `timescaledb.persistence.size` | TimescaleDB PVC size | `10Gi` |
| `timescaledb.resources` | TimescaleDB resource requests/limits | See `values.yaml` |

### Qdrant Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `qdrant.enabled` | Enable Qdrant | `true` |
| `qdrant.image.repository` | Qdrant image repository | `qdrant/qdrant` |
| `qdrant.image.tag` | Qdrant image tag | `latest` |
| `qdrant.persistence.enabled` | Enable persistence for Qdrant | `true` |
| `qdrant.persistence.size` | Qdrant PVC size | `5Gi` |
| `qdrant.resources` | Qdrant resource requests/limits | See `values.yaml` |
| `qdrant.service.type` | Qdrant service type | `ClusterIP` |
| `qdrant.service.ports.http` | Qdrant HTTP port | `6333` |
| `qdrant.service.ports.grpc` | Qdrant gRPC port | `6334` |

### RabbitMQ Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `rabbitmq.enabled` | Enable RabbitMQ | `true` |
| `rabbitmq.auth.username` | RabbitMQ username | `guest` |
| `rabbitmq.auth.password` | RabbitMQ password | `guest` |
| `rabbitmq.persistence.enabled` | Enable persistence for RabbitMQ | `true` |
| `rabbitmq.persistence.size` | RabbitMQ PVC size | `5Gi` |
| `rabbitmq.resources` | RabbitMQ resource requests/limits | See `values.yaml` |

### Redis Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable Redis | `true` |
| `redis.architecture` | Redis architecture | `standalone` |
| `redis.auth.enabled` | Enable Redis authentication | `false` |
| `redis.master.persistence.enabled` | Enable persistence for Redis | `false` |
| `redis.master.resources` | Redis resource requests/limits | See `values.yaml` |

### Redis Instances Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redisInstances.enabled` | Enable Redis instances for Frappe/ERPNext | `true` |
| `redisInstances.image.repository` | Redis image repository | `redis` |
| `redisInstances.image.tag` | Redis image tag | `7-alpine` |
| `redisInstances.cache.enabled` | Enable Redis Cache instance | `true` |
| `redisInstances.cache.command` | Redis Cache command | See `values.yaml` |
| `redisInstances.cache.resources` | Redis Cache resource requests/limits | See `values.yaml` |
| `redisInstances.queue.enabled` | Enable Redis Queue instance | `true` |
| `redisInstances.queue.command` | Redis Queue command | See `values.yaml` |
| `redisInstances.queue.resources` | Redis Queue resource requests/limits | See `values.yaml` |
| `redisInstances.socketio.enabled` | Enable Redis SocketIO instance | `true` |
| `redisInstances.socketio.command` | Redis SocketIO command | See `values.yaml` |
| `redisInstances.socketio.resources` | Redis SocketIO resource requests/limits | See `values.yaml` |

## Persistence

The chart mounts persistent volumes for PostgreSQL, TimescaleDB, Qdrant, and RabbitMQ. The volumes are created using dynamic volume provisioning. If you want to disable this feature, you can change the values.yaml to disable persistence and use emptyDir instead.

## Upgrading

### To 1.0.0

This is the first release of the chart.

## Uninstalling the Chart

To uninstall/delete the `cauldron-infra` deployment:

```bash
helm delete cauldron-infra --namespace cauldron
```

This will delete all the Kubernetes resources associated with the chart and remove the release.

## Notes

- This chart is designed to be used with the Cauldron sEOS project.
- For production use, it is recommended to use external managed services for databases and message brokers.
- The default values are suitable for development environments. For production, adjust the resource requests/limits and persistence settings accordingly.
