FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    mariadb-client \
    postgresql-client \
    build-essential \
    python3-dev \
    libffi-dev \
    liblcms2-dev \
    libldap2-dev \
    libmariadb-dev \
    libsasl2-dev \
    libtiff5-dev \
    libwebp-dev \
    redis-tools \
    wkhtmltopdf \
    xvfb \
    libfontconfig \
    fonts-cantarell \
    curl \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and Yarn
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn

# Create frappe user
RUN useradd -ms /bin/bash frappe
USER frappe
WORKDIR /home/frappe

# Install bench
RUN pip install --no-cache-dir frappe-bench

# Initialize bench (without site creation)
RUN bench init --skip-redis-config-generation --skip-assets --python $(which python3) frappe-bench

WORKDIR /home/frappe/frappe-bench

# Configure bench to use external services
COPY --chown=frappe:frappe common_site_config.json sites/common_site_config.json

# Expose ports
EXPOSE 8000 9000

# Set entrypoint
COPY --chown=frappe:frappe entrypoint.sh /home/frappe/entrypoint.sh
RUN chmod +x /home/frappe/entrypoint.sh

ENTRYPOINT ["/home/frappe/entrypoint.sh"]
CMD ["bench", "start"]
