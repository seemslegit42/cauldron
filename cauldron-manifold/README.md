# Cauldron Manifold UI Helm Chart

This Helm chart deploys the Manifold UI frontend application for the Cauldron Sentient Enterprise Operating System (sEOS).

## Overview

The Cauldron Manifold UI Helm chart deploys the following components:

- **Manifold UI**: The unified user interface for the Cauldron™ sEOS

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Cauldron Infrastructure Helm chart installed (for PostgreSQL, Redis, etc.)
- Cauldron AetherCore Helm chart installed (for API backend)

## Installing the Chart

### Add the Helm repository

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Install the chart

```bash
# Create a namespace for Cauldron (if not already created)
kubectl create namespace cauldron

# Install the chart with the release name "cauldron-manifold"
helm install cauldron-manifold ./cauldron-manifold --namespace cauldron
```

For development environments:

```bash
helm install cauldron-manifold ./cauldron-manifold --namespace cauldron -f cauldron-manifold/values-dev.yaml
```

## Configuration

The following table lists the configurable parameters of the Cauldron Manifold UI chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name (dev, staging, prod) | `dev` |
| `global.storageClass` | Storage class for persistent volumes | `""` |
| `global.imagePullPolicy` | Image pull policy | `IfNotPresent` |
| `global.labels` | Common labels to apply to all resources | `{}` |

### Manifold UI Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `manifold.image.repository` | Manifold UI image repository | `cauldron/manifold-ui` |
| `manifold.image.tag` | Manifold UI image tag | `latest` |
| `manifold.image.pullPolicy` | Manifold UI image pull policy | `IfNotPresent` |
| `manifold.resources` | Resource requests/limits for Manifold UI | See `values.yaml` |
| `manifold.replicas` | Number of Manifold UI replicas | `1` |
| `manifold.service.type` | Manifold UI service type | `ClusterIP` |
| `manifold.service.port` | Manifold UI service port | `80` |
| `manifold.service.targetPort` | Manifold UI container port | `80` |
| `manifold.ingress.enabled` | Enable ingress for Manifold UI | `true` |
| `manifold.ingress.className` | Ingress class name | `traefik` |
| `manifold.ingress.annotations` | Ingress annotations | See `values.yaml` |
| `manifold.ingress.hosts` | Ingress hosts | See `values.yaml` |
| `manifold.ingress.tls` | Ingress TLS configuration | `[]` |
| `manifold.api.url` | API URL for Manifold UI | `/api` |
| `manifold.livenessProbe` | Liveness probe configuration | See `values.yaml` |
| `manifold.readinessProbe` | Readiness probe configuration | See `values.yaml` |
| `manifold.autoscaling.enabled` | Enable autoscaling for Manifold UI | `false` |
| `manifold.autoscaling.minReplicas` | Minimum number of replicas | `1` |
| `manifold.autoscaling.maxReplicas` | Maximum number of replicas | `5` |
| `manifold.autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization percentage | `80` |
| `manifold.autoscaling.targetMemoryUtilizationPercentage` | Target memory utilization percentage | `80` |
| `manifold.networkPolicy.enabled` | Enable network policy for Manifold UI | `true` |
| `manifold.networkPolicy.ingressRules` | Network policy ingress rules | See `values.yaml` |
| `manifold.networkPolicy.egressRules` | Network policy egress rules | See `values.yaml` |
| `manifold.extraEnv` | Additional environment variables | `[]` |

## Upgrading

### To 1.0.0

This is the first release of the chart.

## Uninstalling the Chart

To uninstall/delete the `cauldron-manifold` deployment:

```bash
helm delete cauldron-manifold --namespace cauldron
```

This will delete all the Kubernetes resources associated with the chart and remove the release.

## Notes

- This chart is designed to be used with the Cauldron sEOS project.
- The chart assumes that AetherCore is already deployed and accessible.
- For production use, it is recommended to use a custom Manifold UI image with pre-built assets.
- The default values are suitable for development environments. For production, adjust the resource requests/limits and autoscaling settings accordingly.
