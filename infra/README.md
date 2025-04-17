# Cauldron Infrastructure

This directory contains infrastructure as code (IaC) configurations, deployment scripts, and related resources for the Cauldron project.

## Directory Structure

- `aws/` - AWS-specific infrastructure configurations using Terraform
- `docker/` - Docker Compose configurations for local development and testing
- `k8s/` - Kubernetes manifests for container orchestration
- `terraform/` - Terraform modules and configurations for cloud infrastructure
- `modules/` - Reusable infrastructure modules

## Infrastructure Components

The Cauldron infrastructure includes:

- **Databases**:
  - PostgreSQL for relational data
  - TimescaleDB for time-series data
  - Qdrant for vector embeddings
  
- **Messaging and Event Streaming**:
  - RabbitMQ for event-driven architecture
  
- **API Gateway**:
  - Traefik for routing and load balancing
  
- **Compute**:
  - Kubernetes for container orchestration
  - Docker for containerization

## Deployment Environments

- **Development**: Local development environment using Docker Compose
- **Staging**: Kubernetes-based environment for testing
- **Production**: Highly available, scalable Kubernetes deployment

## Getting Started

### Local Development

```bash
# Start local development environment
cd docker
docker-compose up -d
```

### Cloud Deployment

```bash
# Deploy to AWS using Terraform
cd terraform
terraform init
terraform apply -var-file=environments/dev.tfvars
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
cd k8s
kubectl apply -k overlays/dev
```

## Security Considerations

- Secrets management using Kubernetes Secrets or HashiCorp Vault
- Network policies for secure communication between services
- Zero Trust security model implementation
- Regular security audits and updates

## Monitoring and Observability

Infrastructure monitoring is implemented using:

- Prometheus for metrics collection
- Grafana for visualization
- Loki for log aggregation
- Jaeger for distributed tracing