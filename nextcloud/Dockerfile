FROM php:8.2-apache

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libapache2-mod-php \
    libxml2-dev \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libzip-dev \
    libgmp-dev \
    libldap2-dev \
    libpq-dev \
    libmagickwand-dev \
    libsmbclient-dev \
    libssh2-1-dev \
    libffi-dev \
    libicu-dev \
    ffmpeg \
    smbclient \
    openssl \
    unzip \
    bzip2 \
    supervisor \
    redis-tools \
    sudo \
    cron \
    rsync \
    vim \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure PHP extensions
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-configure ldap --with-libdir=lib/x86_64-linux-gnu/ \
    && docker-php-ext-install -j$(nproc) \
    bcmath \
    exif \
    gd \
    gmp \
    intl \
    ldap \
    opcache \
    pcntl \
    pdo_mysql \
    pdo_pgsql \
    pgsql \
    zip

# Install PECL extensions
RUN pecl install apcu redis imagick \
    && docker-php-ext-enable apcu redis imagick

# Configure Apache
RUN a2enmod rewrite headers env dir mime setenvif ssl

# Set recommended PHP.ini settings
RUN { \
    echo 'opcache.enable=1'; \
    echo 'opcache.interned_strings_buffer=32'; \
    echo 'opcache.max_accelerated_files=10000'; \
    echo 'opcache.memory_consumption=128'; \
    echo 'opcache.save_comments=1'; \
    echo 'opcache.revalidate_freq=1'; \
    } > /usr/local/etc/php/conf.d/opcache-recommended.ini; \
    { \
    echo 'memory_limit=512M'; \
    echo 'upload_max_filesize=1G'; \
    echo 'post_max_size=1G'; \
    echo 'max_execution_time=300'; \
    echo 'max_input_time=300'; \
    } > /usr/local/etc/php/conf.d/nextcloud.ini

# Download and extract Nextcloud
ENV NEXTCLOUD_VERSION 27.1.2
RUN curl -fsSL -o nextcloud.tar.bz2 \
    "https://download.nextcloud.com/server/releases/nextcloud-${NEXTCLOUD_VERSION}.tar.bz2" \
    && tar -xjf nextcloud.tar.bz2 -C /var/www/ \
    && rm nextcloud.tar.bz2 \
    && chown -R www-data:www-data /var/www/nextcloud

# Copy Apache configuration
RUN { \
    echo '<VirtualHost *:80>'; \
    echo '  DocumentRoot /var/www/nextcloud/'; \
    echo '  <Directory /var/www/nextcloud/>'; \
    echo '    Options Indexes FollowSymLinks'; \
    echo '    AllowOverride All'; \
    echo '    Require all granted'; \
    echo '    SetEnv HOME /var/www/nextcloud'; \
    echo '    SetEnv HTTP_HOME /var/www/nextcloud'; \
    echo '  </Directory>'; \
    echo '</VirtualHost>'; \
    } > /etc/apache2/sites-available/000-default.conf

# Create entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set working directory
WORKDIR /var/www/nextcloud

# Expose ports
EXPOSE 80

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
