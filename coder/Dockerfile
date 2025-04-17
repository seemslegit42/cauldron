FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    CODER_VERSION=0.27.2 \
    CODER_DATA_DIR=/var/lib/coder \
    CODER_CONFIG_DIR=/etc/coder \
    CODER_CACHE_DIRECTORY=/var/cache/coder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    dumb-init \
    git \
    jq \
    openssh-client \
    sudo \
    tzdata \
    unzip \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://get.docker.com | sh

# Install Coder
RUN curl -fsSL https://coder.com/install.sh | sh

# Create Coder user
RUN useradd -ms /bin/bash coder \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/coder

# Create necessary directories
RUN mkdir -p ${CODER_DATA_DIR} ${CODER_CONFIG_DIR} ${CODER_CACHE_DIRECTORY} \
    && chown -R coder:coder ${CODER_DATA_DIR} ${CODER_CONFIG_DIR} ${CODER_CACHE_DIRECTORY}

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to coder user
USER coder
WORKDIR /home/coder

# Expose ports
EXPOSE 3000 8080

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
