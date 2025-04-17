# Cauldron Kubernetes Cluster Setup

This directory contains Kubernetes manifests for deploying the Cauldron sEOS platform using Kustomize for environment-specific configurations.

## Directory Structure

- `base/`: Contains the base Kubernetes manifests that are common across all environments
- `overlays/`: Contains environment-specific configurations
  - `dev/`: Development environment configuration
  - `staging/`: Staging environment configuration
  - `prod/`: Production environment configuration

## Prerequisites

- Kubernetes cluster (v1.22+)
- kubectl (v1.22+)
- kustomize (v4.0+)

## Setup Instructions

### 1. Prepare Environment Secrets

For each environment, copy the `secrets.env.example` file to `secrets.env` and fill in the appropriate values:

```bash
# For development environment
cp overlays/dev/secrets.env.example overlays/dev/secrets.env
# Edit the file with your secret values

# For staging environment
cp overlays/staging/secrets.env.example overlays/staging/secrets.env
# Edit the file with your secret values

# For production environment
cp overlays/prod/secrets.env.example overlays/prod/secrets.env
# Edit the file with your secret values
```

### 2. Update Domain Names

Update the ingress host values in each environment's `patches/ingress-patch.yaml` file to match your actual domain names.

### 3. Deploy to Kubernetes

Deploy to the desired environment using kustomize:

```bash
# For development environment
kubectl apply -k overlays/dev

# For staging environment
kubectl apply -k overlays/staging

# For production environment
kubectl apply -k overlays/prod
```

### 4. Verify Deployment

Check the status of the deployed resources:

```bash
kubectl get all -n cauldron-dev    # For development
kubectl get all -n cauldron-staging  # For staging
kubectl get all -n cauldron-prod     # For production
```

## Components

The Cauldron Kubernetes deployment includes the following components:

- **PostgreSQL**: Main relational database
- **Qdrant**: Vector database for Lore module
- **TimescaleDB**: Time-series database for metrics and monitoring
- **RabbitMQ**: Message broker for event-driven architecture
- **SuperAGI**: AI agent framework
- **AetherCore**: Agent orchestration service
- **Manifold UI**: Frontend user interface
- **Traefik**: Ingress controller for routing external traffic

## Configuration

Each environment can be configured by modifying the corresponding overlay files:

- **Replicas**: Adjust the number of replicas in `replicas-patch.yaml`
- **Resources**: Adjust CPU and memory allocations in `resources-patch.yaml`
- **Autoscaling**: Configure horizontal pod autoscalers in `hpa-patch.yaml` (production only)
- **Ingress**: Configure domain names and TLS in `ingress-patch.yaml`

## Maintenance

### Updating Images

To update the image version for a specific component, modify the corresponding deployment file in the base directory or create a patch in the overlay.

### Scaling

For manual scaling:

```bash
kubectl scale deployment <deployment-name> --replicas=<count> -n <namespace>
```

For production, horizontal pod autoscalers will automatically adjust the number of replicas based on CPU utilization.

### Monitoring

Monitor the health of your deployments:

```bash
kubectl get pods -n <namespace>
kubectl logs <pod-name> -n <namespace>
kubectl describe pod <pod-name> -n <namespace>
```
