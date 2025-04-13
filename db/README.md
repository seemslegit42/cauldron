# Cauldron sEOS Database Schema

This directory contains the SQL scripts to set up the Cauldron sEOS database schema, incorporating PostgreSQL as the foundation, with extensions for vector database capabilities (PGVector), time-series functionality (TimescaleDB), and Supabase integration.

## Overview

The Cauldron sEOS database is designed as a comprehensive foundation for the Sentient Enterprise Operating System, featuring:

- **PostgreSQL Core**: Robust relational database capabilities
- **Vector Database (PGVector)**: For semantic search and knowledge management
- **Time-Series Database (TimescaleDB)**: For efficient storage and querying of metrics
- **Supabase Integration**: For authentication, storage, and real-time capabilities

## Directory Structure

- `00_init/`: Initial setup scripts (extensions, schemas)
- `01_core/`: Core tables (users, roles, permissions)
- `02_lore/`: Lore module with vector database integration
- `03_timeseries/`: Time-series data tables
- `04_superagi/`: SuperAGI integration schema
- `05_supabase/`: Supabase-specific configurations
- `06_integration/`: Integration points and data flow
- `07_performance/`: Performance optimizations
- `migrations/`: Database migration scripts

## Key Files

- `database_schema.sql`: Complete database schema in a single file
- `DATABASE_SCHEMA.md`: Detailed documentation of the schema design
- `SCHEMA_DIAGRAM.md`: Visual representation of the database schema
- `setup_database.sh`: Script to automate database setup

## Setup Instructions

### Option 1: Using the Setup Script

Run the setup script to create and configure the database:

```bash
chmod +x setup_database.sh
./setup_database.sh -n cauldron_seos -u postgres -h localhost -p 5432
```

### Option 2: Manual Setup

1. Create a PostgreSQL database:
   ```
   createdb cauldron_seos
   ```

2. Apply the complete schema:
   ```
   psql -d cauldron_seos -f database_schema.sql
   ```

3. Alternatively, apply individual scripts:
   ```
   psql -d cauldron_seos -f 00_init/00_extensions.sql
   psql -d cauldron_seos -f 00_init/01_schemas.sql
   psql -d cauldron_seos -f 01_core/01_users.sql
   # ... and so on
   ```

## Schema Components

1. **Core User Management**
   - User accounts and profiles
   - Role-based access control
   - Organizations and teams

2. **Vector Database (Lore Module)**
   - Document storage and chunking
   - Vector embeddings for semantic search
   - Knowledge graph with entities and relationships

3. **Time-Series Database**
   - System metrics collection
   - User activity tracking
   - Business KPIs and metrics

4. **Supabase Integration**
   - Authentication and user management
   - File storage and management
   - Real-time subscriptions and notifications

5. **Agent System**
   - AI agents and their configurations
   - Agent executions and history
   - Tools and workflows

## Requirements

- PostgreSQL 15+
- Extensions:
  - TimescaleDB (for time-series data)
  - PGVector (for vector embeddings)
  - uuid-ossp (for UUID generation)
  - pg_trgm (for full-text search)
  - pgcrypto (for cryptographic functions)

## Supabase Integration

For Supabase integration:

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Configure the connection in your application
3. Use the schema in `05_supabase/` for custom tables and functions

## Documentation

For more detailed information about the database schema, refer to:

- `DATABASE_SCHEMA.md`: Comprehensive documentation
- `SCHEMA_DIAGRAM.md`: Visual schema diagrams
