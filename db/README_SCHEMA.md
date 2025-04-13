# Cauldron sEOS Database Schema

This document provides a comprehensive overview of the Cauldron sEOS database schema, which incorporates PostgreSQL as the foundation with integrations for Supabase, vector database capabilities (PGVector), and time-series functionality (TimescaleDB).

## Architecture Overview

The database architecture consists of the following key components:

1. **PostgreSQL Core**: The foundation of the database system, providing robust relational database capabilities.
2. **Vector Database (PGVector)**: Integrated for semantic search and knowledge management.
3. **Time-Series Database (TimescaleDB)**: For efficient storage and querying of time-series metrics and events.
4. **Supabase Integration**: For authentication, storage, and real-time capabilities.

## Schema Organization

The database is organized into multiple schemas to logically separate different functional areas:

### Core Schemas

- **public**: Core tables for users, roles, permissions, organizations, and system settings
- **erp**: ERPNext core tables
- **hr**: HR module tables
- **crm**: CRM module tables

### Cauldron sEOS Module Schemas

- **command_cauldron**: Command & Cauldron module for AI Software Development & Autonomous DevOps
- **synapse**: Synapse module for Predictive & Prescriptive Business Intelligence
- **aegis**: Aegis Protocol module for Proactive & Autonomous Cybersecurity
- **lore**: Lore module for Collective Intelligence & Knowledge Synthesis

### Technical Schemas

- **vector**: Vector embeddings using PGVector
- **timeseries**: Time-series data using TimescaleDB
- **audit**: Audit and logging tables
- **admin**: Administrative functions and procedures
- **supabase**: Supabase integration tables and functions
- **realtime**: Supabase Realtime functionality
- **storage**: Supabase Storage functionality
- **auth**: Supabase Auth functionality
- **analytics**: Analytics and reporting
- **integration**: External system integrations

## Key Components

### 1. Core User Management

The core user management system includes:

- User accounts and profiles
- Role-based access control
- Organizations and teams
- API tokens and sessions
- System and user settings

Key tables:
- `public.users`: Core user accounts
- `public.user_profiles`: Extended user profile information
- `public.roles`: User roles for access control
- `public.permissions`: Available permissions in the system
- `public.organizations`: Organizations using the platform
- `public.teams`: Teams within organizations

### 2. Vector Database (PGVector)

The vector database capabilities are implemented across two schemas:

#### Lore Schema (Domain-Specific)

- `lore.documents`: Knowledge documents
- `lore.document_chunks`: Chunked documents with vector embeddings
- `lore.entities`: Knowledge graph entities
- `lore.relationships`: Relationships between entities

Key features:
- Document chunking and embedding
- Knowledge graph with entities and relationships
- HNSW indexes for fast similarity search

#### Vector Schema (Generic)

- `vector.embeddings`: Generic vector embeddings for various entities
- `vector.embedding_models`: Available embedding models
- `vector.collections`: Collections of related embeddings
- `vector.search_queries`: Log of vector similarity search queries

Key features:
- Generic embedding storage and retrieval
- Model management
- Search history and analytics

### 3. Time-Series Database (TimescaleDB)

Time-series functionality is implemented in the `timeseries` schema:

- `timeseries.system_metrics`: System-level metrics
- `timeseries.user_activity`: User activity tracking
- `timeseries.business_metrics`: Business KPIs and metrics
- `timeseries.agent_metrics`: AI agent performance metrics
- `timeseries.events`: System-wide event log
- `timeseries.alerts`: System alerts and notifications
- `timeseries.anomalies`: Detected anomalies
- `timeseries.forecasts`: Time-series forecast predictions

Key features:
- Automatic partitioning by time (hypertables)
- Continuous aggregates for efficient querying
- Retention policies for data lifecycle management
- Anomaly detection and forecasting

### 4. Supabase Integration

Supabase integration is implemented across multiple schemas:

- **auth**: User authentication and management
  - `auth.users`: Supabase Auth users
  - `auth.sessions`: Supabase Auth sessions
  - `auth.user_mappings`: Mapping between Supabase and application users

- **storage**: File storage and management
  - `storage.buckets`: Supabase Storage buckets
  - `storage.objects`: Supabase Storage objects
  - `storage.file_metadata`: Application-specific metadata for storage objects

Key features:
- Seamless integration with Supabase Auth
- Managed file storage with metadata
- Access control for files and buckets

## Performance Optimizations

The schema includes several performance optimizations:

1. **Indexes**: Comprehensive indexing strategy for all tables
2. **Vector Indexes**: HNSW indexes for efficient similarity search
3. **Partitioning**: Time-based partitioning for large tables (hypertables)
4. **Continuous Aggregates**: Pre-computed aggregates for time-series data
5. **Full-Text Search**: GIN indexes for text search capabilities

## Security Features

Security is implemented at multiple levels:

1. **Role-Based Access Control**: Fine-grained permissions system
2. **Row-Level Security**: For multi-tenant data isolation
3. **Audit Logging**: Comprehensive audit trail of all actions
4. **Encryption**: Support for encrypted data storage

## Directory Structure

The database schema is organized into the following directories:

- `00_init/`: Initial setup scripts (extensions, schemas)
- `01_core/`: Core tables (users, roles, permissions)
- `02_lore/`: Lore module with vector database integration
- `03_timeseries/`: Time-series data tables
- `04_vector/`: Generic vector database functionality
- `05_supabase/`: Supabase integration tables

## Setup Instructions

### Prerequisites

- PostgreSQL 15+
- Extensions:
  - TimescaleDB (for time-series data)
  - PGVector (for vector embeddings)
  - uuid-ossp (for UUID generation)
  - pg_trgm (for full-text search)
  - pgcrypto (for cryptographic functions)

### Installation

1. Run the setup script:
   ```bash
   chmod +x setup_database.sh
   ./setup_database.sh -n cauldron_seos -u postgres -h localhost -p 5432
   ```

2. Alternatively, apply the schema manually:
   ```bash
   createdb cauldron_seos
   psql -d cauldron_seos -f database_schema.sql
   ```

## Usage Examples

### Vector Similarity Search

```sql
-- Search for similar documents
SELECT * FROM vector.similarity_search(
    'What is the Cauldron sEOS platform?',
    NULL,  -- Use default model
    NULL,  -- No specific collection
    'document',  -- Entity type
    '{}',  -- No filters
    10,    -- Top 10 results
    0.7,   -- Similarity threshold
    FALSE  -- No hybrid search
);
```

### Time-Series Analytics

```sql
-- Get system metrics trend
SELECT * FROM timeseries.get_metric_trend(
    'cpu_usage',
    NOW() - INTERVAL '24 hours',
    NOW(),
    '5 minutes'::INTERVAL
);

-- Detect anomalies
SELECT * FROM timeseries.detect_anomalies(
    'active_users',
    NOW() - INTERVAL '7 days',
    NOW(),
    3.0  -- Threshold (3 standard deviations)
);
```

### User Management

```sql
-- Create a new user
INSERT INTO public.users (
    username, email, full_name, hashed_password, salt
) VALUES (
    'johndoe',
    'john.doe@example.com',
    'John Doe',
    -- In a real application, these would be properly hashed
    encode(digest('password123' || 'random_salt', 'sha256'), 'hex'),
    'random_salt'
);

-- Assign a role to a user
INSERT INTO public.user_roles (user_id, role_id)
VALUES (
    (SELECT id FROM public.users WHERE username = 'johndoe'),
    (SELECT id FROM public.roles WHERE name = 'analyst')
);
```

## Maintenance

### Backup and Restore

```bash
# Backup
pg_dump -h localhost -U postgres -d cauldron_seos -F c -f cauldron_backup.dump

# Restore
pg_restore -h localhost -U postgres -d cauldron_seos -c cauldron_backup.dump
```

### Monitoring

```sql
-- Check table sizes
SELECT
    schema_name,
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Check index usage
SELECT
    indexrelname AS index_name,
    relname AS table_name,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Conclusion

This database schema provides a comprehensive foundation for the Cauldron sEOS platform, combining the strengths of PostgreSQL, vector databases, time-series databases, and Supabase to create a powerful and flexible data layer for enterprise operations.