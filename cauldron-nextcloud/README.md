# Cauldron Nextcloud Helm Chart

This Helm chart deploys Nextcloud as a document store and knowledge base for the Cauldron Sentient Enterprise Operating System (sEOS).

## Overview

The Cauldron Nextcloud Helm chart deploys the following components:

- **Nextcloud**: A self-hosted file sync and share server
- **Cron Job**: For scheduled tasks in Nextcloud

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (for persistent volumes)
- Cauldron Infrastructure Helm chart installed (for PostgreSQL, Redis, etc.)

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

# Install the chart with the release name "cauldron-nextcloud"
helm install cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron
```

For development environments:

```bash
helm install cauldron-nextcloud ./cauldron-nextcloud --namespace cauldron -f cauldron-nextcloud/values-dev.yaml
```

## Configuration

The following table lists the configurable parameters of the Cauldron Nextcloud chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name (dev, staging, prod) | `dev` |
| `global.storageClass` | Storage class for persistent volumes | `""` |
| `global.imagePullPolicy` | Image pull policy | `IfNotPresent` |
| `global.labels` | Common labels to apply to all resources | `{}` |

### Nextcloud Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `nextcloud.image.repository` | Nextcloud image repository | `nextcloud` |
| `nextcloud.image.tag` | Nextcloud image tag | `27.1.2-apache` |
| `nextcloud.image.pullPolicy` | Nextcloud image pull policy | `IfNotPresent` |
| `nextcloud.admin.username` | Nextcloud admin username | `admin` |
| `nextcloud.admin.password` | Nextcloud admin password | `admin` |
| `nextcloud.admin.existingSecret` | Existing secret with admin password | `""` |
| `nextcloud.admin.existingSecretPasswordKey` | Key in existing secret with admin password | `nextcloud-admin-password` |
| `nextcloud.db.type` | Database type | `pgsql` |
| `nextcloud.db.host` | Database host | `postgres` |
| `nextcloud.db.port` | Database port | `5432` |
| `nextcloud.db.name` | Database name | `nextcloud` |
| `nextcloud.db.user` | Database user | `postgres` |
| `nextcloud.db.passwordSecret` | Secret containing database password | `cauldron-secrets` |
| `nextcloud.db.passwordKey` | Key in secret containing database password | `db-root-password` |
| `nextcloud.db.createDatabase` | Create database if it doesn't exist | `true` |
| `nextcloud.redis.enabled` | Enable Redis for caching and locking | `true` |
| `nextcloud.redis.host` | Redis host | `redis` |
| `nextcloud.redis.port` | Redis port | `6379` |
| `nextcloud.trustedDomains` | Trusted domains for Nextcloud | See `values.yaml` |
| `nextcloud.resources` | Resource requests/limits for Nextcloud | See `values.yaml` |
| `nextcloud.persistence.enabled` | Enable persistence for Nextcloud | `true` |
| `nextcloud.persistence.size` | Nextcloud PVC size | `10Gi` |
| `nextcloud.persistence.accessMode` | Nextcloud PVC access mode | `ReadWriteOnce` |
| `nextcloud.replicas` | Number of Nextcloud replicas | `1` |
| `nextcloud.service.type` | Nextcloud service type | `ClusterIP` |
| `nextcloud.service.port` | Nextcloud service port | `80` |
| `nextcloud.ingress.enabled` | Enable ingress for Nextcloud | `true` |
| `nextcloud.ingress.className` | Ingress class name | `traefik` |
| `nextcloud.ingress.annotations` | Ingress annotations | See `values.yaml` |
| `nextcloud.ingress.hosts` | Ingress hosts | See `values.yaml` |
| `nextcloud.ingress.tls` | Ingress TLS configuration | `[]` |
| `nextcloud.livenessProbe` | Liveness probe configuration | See `values.yaml` |
| `nextcloud.readinessProbe` | Readiness probe configuration | See `values.yaml` |
| `nextcloud.initContainers` | Init container configuration | See `values.yaml` |
| `nextcloud.php` | PHP configuration | See `values.yaml` |
| `nextcloud.cron.enabled` | Enable cron job | `true` |
| `nextcloud.cron.schedule` | Cron job schedule | `*/15 * * * *` |
| `nextcloud.extraEnv` | Additional environment variables | `[]` |
| `nextcloud.config` | Additional configuration | See `values.yaml` |

## Persistence

The chart mounts a Persistent Volume for Nextcloud data. The volume is created using dynamic volume provisioning. If you want to disable this feature, you can change the values.yaml to disable persistence and use emptyDir instead.

## Upgrading

### To 1.0.0

This is the first release of the chart.

## Uninstalling the Chart

To uninstall/delete the `cauldron-nextcloud` deployment:

```bash
helm delete cauldron-nextcloud --namespace cauldron
```

This will delete all the Kubernetes resources associated with the chart and remove the release.

## Notes

- This chart is designed to be used with the Cauldron sEOS project.
- The chart assumes that PostgreSQL and Redis are already deployed and accessible.
- For production use, it is recommended to use a custom Nextcloud image with pre-installed apps.
- The default values are suitable for development environments. For production, adjust the resource requests/limits and persistence settings accordingly.
