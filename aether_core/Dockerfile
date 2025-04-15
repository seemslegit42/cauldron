FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=False

# Required environment variables with defaults
ENV DATABASE_URL=postgresql://postgres:please_change_in_env@postgres:5432/aethercore
ENV RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
ENV SUPERAGI_API_URL=http://superagi:8080
ENV SUPERAGI_CONFIG_PATH=/app/config/superagi_config.json

# Optional environment variables
ENV OPENAI_API_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV HUGGINGFACE_TOKEN=""
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Create necessary directories
RUN mkdir -p /app/logs /app/config

# Create default SuperAGI config if not mounted
RUN echo '{"api_key": "", "base_url": "http://superagi:8080", "agent_config": {"default_llm": "gpt-4"}}' > /app/config/superagi_config.json

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Run the configuration setup script\n\
python /app/aether_core/config/setup_config.py\n\
\n\
# Start the application\n\
exec uvicorn aether_core.api.main:app --host 0.0.0.0 --port 8000 --log-level ${LOG_LEVEL:-info}\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]