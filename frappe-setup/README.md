# Frappe Framework Installation

This directory contains scripts and configuration files to install the base Frappe framework within its container environment.

## Prerequisites

- Docker
- Docker Compose

## Installation Steps

### 1. Start the Docker containers

```bash
cd frappe-setup
docker-compose up -d
```

This will start the following containers:

- PostgreSQL database
- Redis for cache, queue, and socketio
- Frappe web server

### 2. Configure PostgreSQL connection

```bash
chmod +x configure-postgres.sh
./configure-postgres.sh
```

This will configure Frappe to connect to the PostgreSQL database with the correct settings. The script will:

1. Update the common_site_config.json file with the database settings
2. Update the site_config.json file with the database credentials
3. Test the database connection to ensure it's working properly

You can customize the database connection settings using command-line options:

```bash
./configure-postgres.sh --db-host custom-postgres --db-port 5433 --db-name mydb --db-user myuser --db-password mypassword
```

### 3. Run the setup script

```bash
chmod +x setup-frappe.sh
./setup-frappe.sh
```

This will:

1. Install the Frappe framework
2. Create a new site
3. Install ERPNext (optional)
4. Configure the site
5. Build assets

### 4. Start the Frappe server

```bash
chmod +x start-frappe.sh
./start-frappe.sh
```

Alternatively, you can start the server directly:

```bash
docker exec -it frappe-web bash -c 'cd /home/frappe/frappe-bench && bench start'
```

### 5. Access the Frappe site

Open your browser and navigate to: [http://localhost:8000](http://localhost:8000)

Login with:

- Username: Administrator
- Password: admin (or the password you specified)

## Additional Scripts

### Create a new custom app

```bash
chmod +x create-app.sh
./create-app.sh --app-name my_custom_app
```

This will create a new Frappe app and install it on your site.

### Install Invoice DocType

```bash
chmod +x install-invoice-doctype.sh
./install-invoice-doctype.sh
```

This will install the Invoice DocType and related DocTypes in your Frappe application. The script will:

1. Create a new app if it doesn't exist (default: cauldron_operations_core)
2. Create a new module if it doesn't exist (default: Accounts)
3. Install the Invoice and Invoice Item DocTypes
4. Migrate the site to update the database

You can customize the installation with command-line options:

```bash
./install-invoice-doctype.sh --app-name my_custom_app --module-name Billing
```

### Install Purchase Order DocType

```bash
chmod +x install-purchase-order-doctype.sh
./install-purchase-order-doctype.sh
```

This will install the Purchase Order DocType and related DocTypes in your Frappe application. The script will:

1. Create a new app if it doesn't exist (default: cauldron_operations_core)
2. Create a new module if it doesn't exist (default: Buying)
3. Install the Purchase Order and Purchase Order Item DocTypes
4. Migrate the site to update the database

You can customize the installation with command-line options:

```bash
./install-purchase-order-doctype.sh --app-name my_custom_app --module-name Procurement
```

### Install Server Scripts

```bash
chmod +x install-server-script.sh
./install-server-script.sh
```

This will install server scripts in your Frappe application. The script will:

1. Copy the server script to the appropriate location in your app
2. Update the app's hooks.py file to attach the script to the specified DocType
3. Configure the script to run on various document events (validate, submit, cancel, etc.)

By default, the script installs the Invoice server script, but you can customize it with command-line options:

```bash
./install-server-script.sh --app-name my_custom_app --module-name Billing --script-name purchase_order_server_script --doctype "Purchase Order"
```

### Configure API Authentication

```bash
chmod +x configure-api-auth.sh
./configure-api-auth.sh
```

This will configure REST API authentication in your Frappe application. The script will:

1. Enable API Key authentication in System Settings
2. Enable JWT authentication in System Settings
3. Configure CORS settings for cross-origin requests
4. Create an API Key for the specified user
5. Generate sample API authentication scripts
6. Create API documentation

You can customize the configuration with command-line options:

```bash
./configure-api-auth.sh --user "ApiUser" --api-key-expiry 90 --allowed-origins "https://example.com,https://app.example.com"
```

For detailed information about API authentication, see the [API_AUTHENTICATION.md](API_AUTHENTICATION.md) file.

### Setup RBAC Roles

```bash
chmod +x setup-rbac-roles.sh
./setup-rbac-roles.sh
```

This will set up Role-Based Access Control (RBAC) roles in your Frappe application. The script will:

1. Create core roles (Admin, Finance User, Dev User, etc.)
2. Set up permissions for each role on relevant DocTypes
3. Create role profiles for common user types

The following roles will be created:

- **Cauldron Admin**: Full administrative access
- **Cauldron Finance User**: Access to financial modules
- **Cauldron Dev User**: Access to development tools
- **Cauldron Operator**: Day-to-day operational access
- **Cauldron Agent**: Limited API access for automated agents
- **Cauldron Read Only**: Read-only access to view data
- **Cauldron Customer**: Limited access for external customers
- **Cauldron Supplier**: Limited access for suppliers

For detailed information about RBAC roles, see the [RBAC_ROLES.md](RBAC_ROLES.md) file.

### Setup Core Permissions

```bash
# On Linux/Mac:
chmod +x setup-core-permissions.sh
./setup-core-permissions.sh

# On Windows:
./setup-core-permissions.sh
# or
bash setup-core-permissions.sh
```

This will set up permissions for core Frappe DocTypes for the initial roles. The script will:

1. Assign appropriate permissions to core Frappe DocTypes for each role
2. Follow the principle of least privilege for each role
3. Ensure that each role has only the permissions necessary for its function

The script assigns permissions to essential Frappe DocTypes such as:

- User, Role, DocType, DocField, Custom Field
- Workflow, Workflow State, Workflow Action
- File, Report, Page, Module Def
- System Settings, Print Format, Email Template, Notification
- And many more core DocTypes

For detailed information about core permissions, see the [CORE_PERMISSIONS.md](CORE_PERMISSIONS.md) file.

## Customization Options

### Setup Script Options

You can customize the installation by passing options to the setup script:

```bash
./setup-frappe.sh --frappe-version version-14 --skip-erpnext
```

Available options:

- `--container NAME`: Container name (default: frappe-web)
- `--frappe-version VER`: Frappe version/branch (default: version-15)
- `--erpnext-version VER`: ERPNext version/branch (default: version-15)
- `--site-name NAME`: Site name (default: cauldron.local)
- `--admin-password PASS`: Admin password (default: admin)
- `--skip-erpnext`: Skip ERPNext installation
- `--install-custom-apps`: Install custom Cauldron apps
- `--help`: Show help message

### Update Config Script Options

```bash
./update-config.sh --container my-container
```

Available options:

- `--container NAME`: Container name (default: frappe-web)
- `--help`: Show help message

### Start Frappe Script Options

```bash
./start-frappe.sh --site-name my-site.local
```

Available options:

- `--container NAME`: Container name (default: frappe-web)
- `--site-name NAME`: Site name (default: cauldron.local)
- `--help`: Show help message

### Create App Script Options

```bash
./create-app.sh --app-name my_custom_app
```

Available options:

- `--container NAME`: Container name (default: frappe-web)
- `--site-name NAME`: Site name (default: cauldron.local)
- `--app-name NAME`: App name (required)
- `--help`: Show help message

## Environment Variables

You can customize the environment by editing the `.env` file:

- `DB_ROOT_PASSWORD`: PostgreSQL root password
- `DB_NAME`: Database name
- `SITE_NAME`: Frappe site name
- `ADMIN_PASSWORD`: Admin password

## Troubleshooting

### Database connection issues

If you encounter database connection issues, check if the PostgreSQL container is running:

```bash
docker ps | grep frappe-postgres
```

You can check the PostgreSQL logs:

```bash
docker logs frappe-postgres
```

### Redis connection issues

Check if the Redis containers are running:

```bash
docker ps | grep frappe-redis
```

### Frappe installation issues

Check the Frappe container logs:

```bash
docker logs frappe-web
```

You can also access the Frappe container shell:

```bash
docker exec -it frappe-web bash
```

## Cleaning Up

To stop and remove the containers:

```bash
docker-compose down
```

To stop and remove the containers along with volumes (this will delete all data):

```bash
docker-compose down -v
```
