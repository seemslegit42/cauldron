# Helm Charts Deployment Pipeline

This document describes the CI/CD pipeline for deploying Helm charts for the Cauldron project.

## Overview

The Helm charts deployment pipeline is responsible for deploying the infrastructure and application components of the Cauldron system to Kubernetes clusters. The pipeline is designed to support multiple environments (development, staging, production) and provides a consistent deployment process across all environments.

## Pipeline Components

The deployment pipeline consists of two main workflows:

1. **Infrastructure Deployment**: Deploys the core infrastructure components (PostgreSQL, TimescaleDB, Qdrant, RabbitMQ, Redis)
2. **Application Deployment**: Deploys the application components (Frappe/ERPNext, SuperAGI, n8n, Nextcloud, Manifold UI)

## Deployment Workflow

The deployment process follows a specific order to ensure dependencies are properly satisfied:

1. **Infrastructure Deployment**:
   - Deploy PostgreSQL
   - Deploy TimescaleDB
   - Deploy Qdrant
   - Deploy RabbitMQ
   - Deploy Redis

2. **Application Deployment**:
   - Deploy Frappe/ERPNext
   - Deploy SuperAGI
   - Deploy n8n
   - Deploy Nextcloud
   - Deploy Manifold UI

## GitHub Actions Workflows

### Infrastructure Deployment Workflow

The infrastructure deployment workflow (`deploy-infra-helm-charts.yml`) is triggered by:

- Pushes to the `main` branch that modify files in the `cauldron-infra/` directory
- Manual triggers via the GitHub Actions UI

The workflow performs the following steps:

1. **Validate Helm Chart**: Lint and validate the infrastructure Helm chart
2. **Deploy to Environment**: Deploy the infrastructure components to the specified environment
3. **Notify Deployment Status**: Send notifications about the deployment status

### Application Deployment Workflow

The application deployment workflow (`deploy-app-helm-charts.yml`) is triggered by:

- Pushes to the `main` branch that modify files in the application Helm chart directories
- Manual triggers via the GitHub Actions UI

The workflow performs the following steps:

1. **Validate Helm Charts**: Lint and validate the application Helm charts
2. **Deploy to Environment**: Deploy the application components to the specified environment
3. **Notify Deployment Status**: Send notifications about the deployment status

## Local Deployment

For local or manual deployment, a script is provided to deploy Helm charts:

```bash
./scripts/deploy-helm-charts.sh
```

### Script Options

The script supports the following options:

- `-e, --environment ENV`: Environment to deploy to (dev, staging, prod) [default: dev]
- `-n, --namespace NS`: Kubernetes namespace [default: cauldron-{environment}]
- `-v, --version VERSION`: Version tag for deployment [default: latest]
- `-c, --charts CHARTS`: Comma-separated list of charts to deploy [default: all]
- `--infra-only`: Deploy only infrastructure charts
- `--apps-only`: Deploy only application charts
- `--dry-run`: Perform a dry run (no actual deployment)
- `--skip-validation`: Skip Helm chart validation
- `--timeout DURATION`: Timeout for Helm operations [default: 10m]
- `-h, --help`: Show help message

### Examples

Deploy all charts to the development environment:

```bash
./scripts/deploy-helm-charts.sh --environment dev
```

Deploy only infrastructure charts to the production environment:

```bash
./scripts/deploy-helm-charts.sh --environment prod --infra-only
```

Deploy specific charts to the staging environment:

```bash
./scripts/deploy-helm-charts.sh --environment staging --charts cauldron-frappe,cauldron-manifold
```

Perform a dry run for the production environment:

```bash
./scripts/deploy-helm-charts.sh --environment prod --dry-run
```

## Environment-Specific Configurations

The deployment pipeline supports different configurations for each environment:

- **Development**: Minimal resources, single replicas, local domain names
- **Staging**: Moderate resources, multiple replicas, staging domain names
- **Production**: High resources, high availability, production domain names

Each Helm chart includes environment-specific values files:

- `values-dev.yaml`: Development environment values
- `values-staging.yaml`: Staging environment values
- `values-prod.yaml`: Production environment values

## Secrets Management

Sensitive information (passwords, API keys, etc.) is stored in GitHub Secrets and injected into the Kubernetes cluster as Kubernetes Secrets during deployment. The following secrets are used:

- `DB_ROOT_PASSWORD`: PostgreSQL root password
- `RABBITMQ_PASSWORD`: RabbitMQ password
- `REDIS_PASSWORD`: Redis password
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `HUGGINGFACE_TOKEN`: Hugging Face token
- `SUPERAGI_API_KEY`: SuperAGI API key

## Deployment Verification

After deployment, the pipeline verifies that all components are running correctly by:

1. Waiting for all pods to be ready
2. Checking the deployment status
3. Sending notifications about the deployment status

## Rollback Procedure

In case of deployment failure, the pipeline automatically rolls back to the previous version. For manual rollback, use the following command:

```bash
helm rollback <release-name> <revision> -n <namespace>
```

For example:

```bash
helm rollback cauldron-infra 1 -n cauldron-prod
```

## Monitoring and Logging

The deployment pipeline integrates with monitoring and logging systems:

- **Slack Notifications**: Sends notifications about deployment status to a Slack channel
- **GitHub Deployment Status**: Updates the deployment status in GitHub
- **Kubernetes Logs**: Stores deployment logs in Kubernetes

## Security Considerations

The deployment pipeline includes several security features:

- **Secrets Management**: Sensitive information is stored in GitHub Secrets and Kubernetes Secrets
- **RBAC**: Role-Based Access Control for Kubernetes resources
- **Network Policies**: Restricts communication between components
- **TLS**: Enables TLS for all ingress resources in staging and production environments

## Future Improvements

- **Automated Testing**: Add automated testing of deployed components
- **Canary Deployments**: Implement canary deployments for production
- **Blue/Green Deployments**: Implement blue/green deployments for zero-downtime updates
- **ArgoCD Integration**: Integrate with ArgoCD for GitOps-based deployments
- **Helm Chart Versioning**: Implement versioning for Helm charts
