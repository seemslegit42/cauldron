FROM python:3.10-slim

# Build arguments
ARG SUPERAGI_VERSION=main
ARG ENVIRONMENT=dev

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone SuperAGI repository with specific version/branch
RUN git clone -b ${SUPERAGI_VERSION} https://github.com/TransformerOptimus/SuperAGI.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8080
ENV DEBUG=False
ENV DATABASE_URL=postgresql://postgres:please_change_in_env@postgres:5432/superagi
ENV VECTOR_DB_URL=http://qdrant:6333
ENV ENVIRONMENT=${ENVIRONMENT}

# Optional environment variables
ENV OPENAI_API_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV HUGGINGFACE_TOKEN=""
ENV LOG_LEVEL=INFO

# Set environment-specific configurations
RUN if [ "$ENVIRONMENT" = "prod" ]; then \
      echo "Setting production configurations"; \
      echo "DEBUG=False" >> /app/.env; \
      echo "LOG_LEVEL=INFO" >> /app/.env; \
    elif [ "$ENVIRONMENT" = "staging" ]; then \
      echo "Setting staging configurations"; \
      echo "DEBUG=False" >> /app/.env; \
      echo "LOG_LEVEL=INFO" >> /app/.env; \
    else \
      echo "Setting development configurations"; \
      echo "DEBUG=True" >> /app/.env; \
      echo "LOG_LEVEL=DEBUG" >> /app/.env; \
    fi

# Expose port
EXPOSE 8080

# Create necessary directories
RUN mkdir -p /app/config /app/data

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Wait for PostgreSQL to be ready\n\
until PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_HOST:-postgres} -U postgres -c "\\q"; do\n\
    echo "PostgreSQL is unavailable - sleeping"\n\
    sleep 1\n\
done\n\
echo "PostgreSQL is up - continuing"\n\
\n\
# Wait for Qdrant to be ready\n\
until curl -s -f ${VECTOR_DB_URL:-http://qdrant:6333}/health > /dev/null; do\n\
    echo "Qdrant is unavailable - sleeping"\n\
    sleep 1\n\
done\n\
echo "Qdrant is up - continuing"\n\
\n\
# Check if database exists, if not create it\n\
if ! PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_HOST:-postgres} -U postgres -lqt | cut -d \\| -f 1 | grep -qw "superagi"; then\n\
    echo "Creating database: superagi"\n\
    PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_HOST:-postgres} -U postgres -c "CREATE DATABASE superagi;"\n\
    echo "Database created."\n\
fi\n\
\n\
# Run database migrations\n\
alembic upgrade head\n\
\n\
# Start the application\n\
exec uvicorn main:app --host 0.0.0.0 --port 8080 --log-level ${LOG_LEVEL:-info}\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]
