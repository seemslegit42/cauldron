# Cauldron Infrastructure Installation Guide

This guide provides step-by-step instructions for installing the Cauldron Infrastructure Helm chart in different environments.

## Prerequisites

Before installing the Cauldron Infrastructure Helm chart, ensure you have the following:

- Kubernetes cluster (version 1.19+)
- Helm (version 3.2.0+)
- `kubectl` configured to communicate with your Kubernetes cluster
- Sufficient permissions to create resources in your Kubernetes cluster

## Installation Steps

### Step 1: Add Required Helm Repositories

```bash
# Add Bitnami repository for PostgreSQL, RabbitMQ, and Redis charts
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Step 2: Create a Namespace

```bash
kubectl create namespace cauldron
```

### Step 3: Prepare Values File

Choose the appropriate values file based on your environment:

- Development: `values-dev.yaml`
- Staging: `values-staging.yaml`
- Production: `values-prod.yaml`

You may need to customize these files based on your specific requirements.

### Step 4: Install the Chart

```bash
# For development environment
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-dev.yaml

# For staging environment
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-staging.yaml

# For production environment
helm install cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-prod.yaml
```

### Step 5: Verify the Installation

```bash
# Check the status of the Helm release
helm status cauldron-infra -n cauldron

# Check the deployed pods
kubectl get pods -n cauldron

# Check the deployed services
kubectl get services -n cauldron

# Check the deployed persistent volume claims
kubectl get pvc -n cauldron
```

## Accessing the Services

After installation, you can access the services using the following endpoints:

- PostgreSQL: `postgres.cauldron.svc.cluster.local:5432`
- TimescaleDB: `timescaledb.cauldron.svc.cluster.local:5432`
- Qdrant: `qdrant.cauldron.svc.cluster.local:6333` (HTTP), `qdrant.cauldron.svc.cluster.local:6334` (gRPC)
- RabbitMQ: `rabbitmq.cauldron.svc.cluster.local:5672` (AMQP), `rabbitmq.cauldron.svc.cluster.local:15672` (Management UI)
- Redis (main): `redis.cauldron.svc.cluster.local:6379`
- Redis Cache: `redis-cache.cauldron.svc.cluster.local:6379`
- Redis Queue: `redis-queue.cauldron.svc.cluster.local:6379`
- Redis SocketIO: `redis-socketio.cauldron.svc.cluster.local:6379`

## Upgrading the Chart

To upgrade the chart:

```bash
# For development environment
helm upgrade cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-dev.yaml

# For staging environment
helm upgrade cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-staging.yaml

# For production environment
helm upgrade cauldron-infra ./cauldron-infra --namespace cauldron -f cauldron-infra/values-prod.yaml
```

## Uninstalling the Chart

To uninstall the chart:

```bash
helm uninstall cauldron-infra --namespace cauldron
```

Note: This will not delete the persistent volume claims. To delete them:

```bash
kubectl delete pvc --all -n cauldron
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**:
   - Check if PVCs are being provisioned: `kubectl get pvc -n cauldron`
   - Check if there are enough resources in the cluster: `kubectl describe pod <pod-name> -n cauldron`

2. **Database connection issues**:
   - Check if the database pods are running: `kubectl get pods -n cauldron | grep postgres`
   - Check the database logs: `kubectl logs <postgres-pod-name> -n cauldron`

3. **RabbitMQ clustering issues**:
   - Check the RabbitMQ logs: `kubectl logs <rabbitmq-pod-name> -n cauldron`
   - Check the RabbitMQ cluster status: `kubectl exec -it <rabbitmq-pod-name> -n cauldron -- rabbitmqctl cluster_status`

### Getting Support

If you encounter any issues that you cannot resolve, please:

1. Check the [Cauldron documentation](https://github.com/seemslegit42/cauldron/docs)
2. Open an issue on the [Cauldron GitHub repository](https://github.com/seemslegit42/cauldron/issues)

## Next Steps

After installing the Cauldron Infrastructure, you can proceed to install the other components of the Cauldron Sentient Enterprise Operating System (sEOS):

1. Install the Frappe/ERPNext chart
2. Install the SuperAGI chart
3. Install the AetherCore chart
4. Install the Manifold UI chart
