FROM node:18-alpine

# Build arguments
ARG N8N_VERSION=latest
ARG ENVIRONMENT=dev

# Set environment variables
ENV NODE_ENV=production \
    N8N_PORT=5678 \
    N8N_PROTOCOL=http \
    N8N_HOST=localhost \
    WEBHOOK_URL=http://localhost:5678/ \
    GENERIC_TIMEZONE=UTC \
    DB_TYPE=postgresdb \
    DB_POSTGRESDB_HOST=postgres \
    DB_POSTGRESDB_PORT=5432 \
    DB_POSTGRESDB_DATABASE=n8n \
    DB_POSTGRESDB_USER=postgres \
    ENVIRONMENT=${ENVIRONMENT}

# Install system dependencies
RUN apk add --no-cache \
    postgresql-client \
    tzdata \
    su-exec \
    bash \
    curl

# Create n8n user
RUN addgroup -S n8n && adduser -S n8n -G n8n

# Create directories and set permissions
RUN mkdir -p /home/node/.n8n /home/node/.n8n/custom
RUN chown -R n8n:n8n /home/node/.n8n

# Switch to n8n user
USER n8n
WORKDIR /home/node

# Install n8n
RUN if [ "$N8N_VERSION" = "latest" ]; then \
      npm install -g n8n; \
    else \
      npm install -g n8n@${N8N_VERSION}; \
    fi

# Copy entrypoint script
COPY --chown=n8n:n8n entrypoint.sh /home/node/entrypoint.sh
RUN chmod +x /home/node/entrypoint.sh

# Expose port
EXPOSE 5678

# Set entrypoint
ENTRYPOINT ["/home/node/entrypoint.sh"]
