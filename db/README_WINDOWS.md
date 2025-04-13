# Cauldron sEOS Database Setup for Windows

This guide will help you set up the PostgreSQL database for Cauldron sEOS on Windows.

## Prerequisites

- Windows 10 or 11
- PowerShell
- Administrator privileges

## Installation Steps

### 1. Install PostgreSQL

If you don't have PostgreSQL installed:

1. Download PostgreSQL 15 from [the official website](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the installation wizard
3. Set the password for the postgres user to `password` (or choose your own and update the scripts)
4. Make sure to install the contrib packages when prompted
5. Complete the installation

### 2. Install Required Extensions

For full functionality, you'll need these extensions:

- pgvector: For vector database capabilities
- TimescaleDB: For time-series data

#### Installing pgvector

1. Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Clone the pgvector repository:
   ```
   git clone https://github.com/pgvector/pgvector.git
   ```
3. Build and install:
   ```
   cd pgvector
   make
   make install
   ```

#### Installing TimescaleDB

Follow the instructions at [TimescaleDB Windows Installation](https://docs.timescale.com/install/latest/self-hosted/installation-windows/)

### 3. Run the Setup Script

1. Open PowerShell as Administrator
2. Navigate to the `db` directory:
   ```
   cd c:\Users\B42\cauldron-seos\db
   ```
3. Run the setup script:
   ```
   .\setup_all.ps1
   ```
4. Follow the prompts to complete the setup

## Verifying the Installation

After running the setup script, you can verify the installation by connecting to the database:

```
psql -h localhost -p 5432 -U postgres -d cauldron_seos
```

Then run:

```sql
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');
```

You should see all the schemas created for Cauldron sEOS.

## Troubleshooting

### PostgreSQL Service Not Running

If the PostgreSQL service is not running:

1. Open Services (services.msc)
2. Find the PostgreSQL service (usually named "postgresql-x64-15")
3. Right-click and select "Start"

### Extension Installation Issues

If you encounter issues with extensions:

1. Make sure you have the required build tools installed
2. Check the PostgreSQL log files for specific error messages
3. For pgvector, you may need to set the PATH environment variable to include the PostgreSQL bin directory

### Database Connection Issues

If you can't connect to the database:

1. Check if the PostgreSQL service is running
2. Verify the password for the postgres user
3. Make sure the firewall is not blocking connections to port 5432