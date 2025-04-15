# AetherCore Configuration

This directory contains configuration files for the AetherCore service, which is responsible for agent orchestration in the Cauldron system.

## Configuration Files

- `superagi_config.json`: Configuration for SuperAGI integration
- `setup_config.py`: Script to replace environment variable placeholders in configuration files

## Environment Variables

The following environment variables are used by AetherCore:

### Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://postgres:password@postgres:5432/aethercore`)
- `RABBITMQ_URL`: RabbitMQ connection string (e.g., `amqp://guest:guest@rabbitmq:5672/`)
- `SUPERAGI_API_URL`: URL of the SuperAGI service (e.g., `http://superagi:8080`)
- `SUPERAGI_CONFIG_PATH`: Path to the SuperAGI configuration file (default: `/app/config/superagi_config.json`)

### Optional Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM access
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude access
- `HUGGINGFACE_TOKEN`: Hugging Face token for model access
- `DEBUG`: Enable debug mode (default: `False`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `HOST`: Host to bind the API server to (default: `0.0.0.0`)
- `PORT`: Port to bind the API server to (default: `8000`)
- `SUPERAGI_API_KEY`: API key for authenticating with SuperAGI

## Configuration Setup

The `setup_config.py` script replaces environment variable placeholders in configuration files with their actual values from the environment. This allows for dynamic configuration based on environment variables.

Example usage:

```bash
python setup_config.py
```

This script is automatically run when the container starts.