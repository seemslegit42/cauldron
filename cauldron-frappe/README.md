# Cauldron Frappe Helm Chart

This Helm chart deploys Frappe/ERPNext with custom Cauldron apps for the Cauldron Sentient Enterprise Operating System (sEOS).

## Overview

The Cauldron Frappe Helm chart deploys the following components:

- **Frappe Web Server**: The main web server for Frappe/ERPNext
- **Frappe Worker**: Background job processing for Frappe/ERPNext
- **Frappe Scheduler**: Scheduled tasks for Frappe/ERPNext
- **Frappe Socket.IO**: Real-time communication for Frappe/ERPNext
- **Custom Cauldron Apps**: Cauldron-specific applications built on Frappe

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

# Install the chart with the release name "cauldron-frappe"
helm install cauldron-frappe ./cauldron-frappe --namespace cauldron
```

For development environments:

```bash
helm install cauldron-frappe ./cauldron-frappe --namespace cauldron -f cauldron-frappe/values-dev.yaml
```

## Configuration

The following table lists the configurable parameters of the Cauldron Frappe chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name (dev, staging, prod) | `dev` |
| `global.storageClass` | Storage class for persistent volumes | `""` |
| `global.imagePullPolicy` | Image pull policy | `IfNotPresent` |
| `global.labels` | Common labels to apply to all resources | `{}` |

### Frappe Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frappe.image.repository` | Frappe image repository | `frappe/bench` |
| `frappe.image.tag` | Frappe image tag | `latest` |
| `frappe.image.pullPolicy` | Frappe image pull policy | `IfNotPresent` |
| `frappe.site.name` | Frappe site name | `cauldron.local` |
| `frappe.site.adminPassword` | Frappe admin password | `admin` |
| `frappe.db.host` | Database host | `postgres` |
| `frappe.db.port` | Database port | `5432` |
| `frappe.db.name` | Database name | `frappe` |
| `frappe.db.user` | Database user | `postgres` |
| `frappe.db.passwordSecret` | Secret containing database password | `cauldron-secrets` |
| `frappe.db.passwordKey` | Key in secret containing database password | `db-root-password` |
| `frappe.redis.cacheHost` | Redis cache host | `redis-cache` |
| `frappe.redis.queueHost` | Redis queue host | `redis-queue` |
| `frappe.redis.socketioHost` | Redis Socket.IO host | `redis-socketio` |
| `frappe.redis.port` | Redis port | `6379` |
| `frappe.resources` | Resource requests/limits for Frappe components | See `values.yaml` |
| `frappe.persistence.enabled` | Enable persistence for Frappe | `true` |
| `frappe.persistence.size` | Frappe PVC size | `10Gi` |
| `frappe.persistence.accessMode` | Frappe PVC access mode | `ReadWriteOnce` |
| `frappe.replicas` | Number of replicas for Frappe components | See `values.yaml` |
| `frappe.service.type` | Frappe service type | `ClusterIP` |
| `frappe.service.webPort` | Frappe web port | `8000` |
| `frappe.service.socketioPort` | Frappe Socket.IO port | `9000` |
| `frappe.ingress.enabled` | Enable ingress for Frappe | `true` |
| `frappe.ingress.className` | Ingress class name | `traefik` |
| `frappe.ingress.annotations` | Ingress annotations | See `values.yaml` |
| `frappe.ingress.hosts` | Ingress hosts | See `values.yaml` |
| `frappe.ingress.tls` | Ingress TLS configuration | `[]` |
| `frappe.apps` | Frappe/ERPNext apps to install | See `values.yaml` |
| `frappe.customApps` | Custom Cauldron apps to install | See `values.yaml` |
| `frappe.bench.developerMode` | Enable developer mode | `true` |
| `frappe.bench.serveDefaultSite` | Serve default site | `true` |
| `frappe.bench.autoUpdate` | Enable auto update | `false` |
| `frappe.bench.shallowClone` | Enable shallow clone | `true` |
| `frappe.livenessProbe` | Liveness probe configuration | See `values.yaml` |
| `frappe.readinessProbe` | Readiness probe configuration | See `values.yaml` |
| `frappe.worker.queues` | Worker queues | See `values.yaml` |
| `frappe.scheduler.enabled` | Enable scheduler | `true` |
| `frappe.socketio.enabled` | Enable Socket.IO | `true` |
| `frappe.initContainers` | Init container configuration | See `values.yaml` |

## Persistence

The chart mounts a Persistent Volume for Frappe sites. The volume is created using dynamic volume provisioning. If you want to disable this feature, you can change the values.yaml to disable persistence and use emptyDir instead.

## Upgrading

### To 1.0.0

This is the first release of the chart.

## Uninstalling the Chart

To uninstall/delete the `cauldron-frappe` deployment:

```bash
helm delete cauldron-frappe --namespace cauldron
```

This will delete all the Kubernetes resources associated with the chart and remove the release.

## Notes

- This chart is designed to be used with the Cauldron sEOS project.
- The chart assumes that PostgreSQL and Redis are already deployed and accessible.
- For production use, it is recommended to use a custom Frappe image with pre-installed apps.
- The default values are suitable for development environments. For production, adjust the resource requests/limits and persistence settings accordingly.
