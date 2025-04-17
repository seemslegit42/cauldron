# Docker Compose Configuration for Cauldron

This directory contains Docker Compose configurations for the Cauldron project's infrastructure components.

## Services

The `docker-compose.yml` file defines the following services:

1. **PostgreSQL** - Primary relational database for ERPNext and microservices
   - Port: 5432
   - Default credentials: cauldron/cauldronpassword (configurable via environment variables)

2. **Qdrant** - Vector database for RAG capabilities in the Knowledge Management module
   - Ports: 6333 (REST API), 6334 (gRPC API)

3. **TimescaleDB** - Time-series database for DevOps monitoring and Security events
   - Port: 5433 (mapped to avoid conflict with PostgreSQL)
   - Default credentials: cauldron/cauldronpassword (configurable via environment variables)

4. **RabbitMQ** - Event-driven architecture for inter-service communication
   - Ports: 5672 (AMQP protocol), 15672 (Management UI)
   - Default credentials: cauldron/cauldronpassword (configurable via environment variables)

5. **Traefik** - API Gateway for managing external access to services
   - Ports: 80 (HTTP), 443 (HTTPS), 8080 (Dashboard - development only)

## Usage

### Environment Variables

Create a `.env` file in this directory with the following variables (or set them in your environment):

```
POSTGRES_USER=cauldron
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=cauldron

TIMESCALE_USER=cauldron
TIMESCALE_PASSWORD=your_secure_password
TIMESCALE_DB=cauldron_timeseries

RABBITMQ_USER=cauldron
RABBITMQ_PASSWORD=your_secure_password
```

### Starting Services

To start all services:

```bash
docker-compose up -d
```

To start specific services:

```bash
docker-compose up -d postgres rabbitmq
```

### Stopping Services

To stop all services:

```bash
docker-compose down
```

To stop and remove volumes (will delete all data):

```bash
docker-compose down -v
```

## Notes

- This configuration is intended for development and testing purposes.
- For production deployments, consider using Kubernetes (see the `../k8s` directory).
- Secure passwords should be used in production environments.
- The Traefik dashboard is enabled for development purposes only and should be disabled in production.