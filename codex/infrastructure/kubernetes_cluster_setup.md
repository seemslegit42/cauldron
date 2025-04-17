# Cauldron™ Kubernetes Cluster Setup Guide

## Overview

This guide provides detailed instructions for setting up and managing the Kubernetes cluster environment for the Cauldron™ Sentient Enterprise Operating System (sEOS). The Kubernetes infrastructure is designed to be scalable, maintainable, and environment-aware through the use of Kustomize for configuration management.

## Architecture

The Cauldron™ Kubernetes architecture follows a microservices approach, with each component deployed as a separate service. The architecture includes:

1. **Database Layer**
   - PostgreSQL: Primary relational database
   - Qdrant: Vector database for the Lore module
   - TimescaleDB: Time-series database for metrics and monitoring

2. **Messaging Layer**
   - RabbitMQ: Message broker for event-driven architecture

3. **Application Layer**
   - SuperAGI: AI agent framework
   - AetherCore: Agent orchestration service
   - Manifold UI: Frontend user interface

4. **Networking Layer**
   - Traefik: Ingress controller for routing external traffic

## Directory Structure

The Kubernetes configuration is organized as follows:

```
infra/k8s/
├── base/                 # Base configurations shared across environments
│   ├── aethercore.yaml
│   ├── kustomization.yaml
│   ├── manifold-ui.yaml
│   ├── namespace.yaml
│   ├── postgres.yaml
│   ├── qdrant.yaml
│   ├── rabbitmq.yaml
│   ├── secrets.yaml
│   ├── superagi.yaml
│   ├── timescaledb.yaml
│   └── traefik.yaml
├── overlays/             # Environment-specific configurations
│   ├── dev/              # Development environment
│   │   ├── kustomization.yaml
│   │   ├── patches/
│   │   │   ├── ingress-patch.yaml
│   │   │   └── replicas-patch.yaml
│   │   └── secrets.env.example
│   ├── staging/          # Staging environment
│   │   ├── kustomization.yaml
│   │   ├── patches/
│   │   │   ├── ingress-patch.yaml
│   │   │   ├── replicas-patch.yaml
│   │   │   └── resources-patch.yaml
│   │   └── secrets.env.example
│   └── prod/             # Production environment
│       ├── kustomization.yaml
│       ├── patches/
│       │   ├── hpa-patch.yaml
│       │   ├── ingress-patch.yaml
│       │   ├── replicas-patch.yaml
│       │   └── resources-patch.yaml
│       └── secrets.env.example
└── README.md             # Documentation for Kubernetes setup
```

## Prerequisites

Before setting up the Kubernetes cluster, ensure you have the following:

1. A Kubernetes cluster (v1.22+)
2. kubectl (v1.22+) configured to access your cluster
3. kustomize (v4.0+)
4. Docker registry for storing container images
5. Domain names for each environment (dev, staging, prod)
6. SSL certificates for production (can be managed via cert-manager)

## Setup Instructions

### 1. Prepare Environment Secrets

For each environment, create a secrets file from the provided template:

```bash
# For development environment
cp infra/k8s/overlays/dev/secrets.env.example infra/k8s/overlays/dev/secrets.env
# Edit the file with your secret values

# For staging environment
cp infra/k8s/overlays/staging/secrets.env.example infra/k8s/overlays/staging/secrets.env
# Edit the file with your secret values

# For production environment
cp infra/k8s/overlays/prod/secrets.env.example infra/k8s/overlays/prod/secrets.env
# Edit the file with your secret values
```

### 2. Update Domain Names

Update the ingress host values in each environment's `patches/ingress-patch.yaml` file to match your actual domain names.

### 3. Build and Push Docker Images

Build and push the Docker images for AetherCore and Manifold UI:

```bash
# Build AetherCore image
docker build -t your-registry/aethercore:version ./aether_core

# Build Manifold UI image
docker build -t your-registry/manifold-ui:version ./manifold

# Push images to registry
docker push your-registry/aethercore:version
docker push your-registry/manifold-ui:version
```

Alternatively, use the provided deployment script:

```bash
./scripts/deploy-k8s.sh --registry your-registry --version 1.0.0 --environment dev
```

### 4. Deploy to Kubernetes

Deploy to the desired environment using kustomize:

```bash
# For development environment
kubectl apply -k infra/k8s/overlays/dev

# For staging environment
kubectl apply -k infra/k8s/overlays/staging

# For production environment
kubectl apply -k infra/k8s/overlays/prod
```

### 5. Verify Deployment

Check the status of the deployed resources:

```bash
kubectl get all -n cauldron-dev    # For development
kubectl get all -n cauldron-staging  # For staging
kubectl get all -n cauldron-prod     # For production
```

## Environment-Specific Configurations

### Development Environment

- Single replica for each service
- Minimal resource requests and limits
- No horizontal pod autoscaling
- Simplified ingress configuration

### Staging Environment

- Multiple replicas for critical services
- Moderate resource requests and limits
- No horizontal pod autoscaling
- Similar to production configuration for testing

### Production Environment

- Multiple replicas for all services
- Higher resource requests and limits
- Horizontal pod autoscaling for key services
- TLS encryption for ingress
- More robust health checks

## Maintenance Tasks

### Updating Images

To update the image version for a specific component:

```bash
./scripts/deploy-k8s.sh --registry your-registry --version new-version --environment env --skip-build --skip-push
```

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

### Backup and Restore

For database backups:

```bash
# Backup PostgreSQL
kubectl exec -n <namespace> <postgres-pod> -- pg_dump -U postgres <database> > backup.sql

# Restore PostgreSQL
kubectl exec -n <namespace> <postgres-pod> -- psql -U postgres <database> < backup.sql
```

## Security Considerations

1. **Secrets Management**: Use Kubernetes secrets for sensitive information. Consider using a secrets management solution like HashiCorp Vault for production.

2. **Network Policies**: Implement Kubernetes network policies to restrict communication between pods.

3. **RBAC**: Configure Role-Based Access Control to limit permissions for service accounts.

4. **Pod Security Policies**: Enforce pod security standards to prevent privilege escalation.

5. **Image Scanning**: Scan container images for vulnerabilities before deployment.

## Troubleshooting

### Common Issues

1. **Pod Startup Failures**:
   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   kubectl logs <pod-name> -n <namespace>
   ```

2. **Service Connectivity Issues**:
   ```bash
   kubectl exec -it <pod-name> -n <namespace> -- curl <service-name>:<port>
   ```

3. **Resource Constraints**:
   ```bash
   kubectl top pods -n <namespace>
   kubectl top nodes
   ```

4. **Ingress Issues**:
   ```bash
   kubectl get ingress -n <namespace>
   kubectl describe ingress <ingress-name> -n <namespace>
   ```

## Conclusion

This Kubernetes setup provides a scalable and maintainable infrastructure for the Cauldron™ sEOS platform. By using Kustomize for configuration management, we can easily maintain different environments while sharing common configurations.

For additional assistance or to report issues, please contact the Cauldron™ DevOps team.
